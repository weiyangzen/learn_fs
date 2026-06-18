# sources/distributed-fs/juicefs/pkg/meta/status.go

## Purpose

`status.go` implements high-level filesystem status collection for any `Meta` backend. It loads sanitized format settings, active sessions, filesystem capacity/inode statistics, and optional trash/pending-deletion object statistics into a `Sections` result.

## Important APIs, Types, And Functions

`Statistic` is the status data model. It includes used/available space and inodes, plus optional JSON-omitted counters and sizes for trash files, pending deleted files, trash slices, and pending deleted slices. `Sections` groups the sanitized `Format`, session list, and computed `Statistic`. `Status` is the main API.

## Control Flow

`Status` first calls `m.Load(true)` to read the format and then calls `RemoveSecret` to redact credentials/tokens. It calls `m.ListSessions()` for active sessions. It initializes `Statistic`, calls `m.StatFS` on `RootInode`, and computes used space as `totalSpace - AvailableSpace`.

When the `trash` flag is true, it creates a progress instance with four double spinners and calls `m.ScanDeletedObject`. The supplied callbacks accumulate slice sizes, pending slice sizes, trash file counts/sizes, and pending deleted file sizes. After scanning, the spinners are finalized and their counts are copied into the `Statistic`. If a `Sections` pointer is provided, the function stores format, sessions, and statistics before returning.

## State And Persistence Behavior

`Status` is read-oriented and does not directly persist metadata. It may trigger backend scans through `ScanDeletedObject`, which can be expensive and may interact with backend cleanup scan logic, but the callbacks here only count and always return `false` for cleanup.

## Dependencies And Integration Points

The function depends on the `Meta` interface methods `Load`, `ListSessions`, `StatFS`, and `ScanDeletedObject`; `Background` and `WrapContext` context helpers; `utils.NewProgress`; and filesystem constants such as `RootInode`. It is backend-independent and consumes the SQL backend through the same interface as Redis, TiKV, or other metadata engines.

## Risks And Edge Cases

`UsedSpace = totalSpace - AvailableSpace` assumes the backend returns a consistent pair and can underflow if a backend reports invalid values. Trash scans can be expensive on large metadata stores and add progress UI side effects even though this is a status function. Errors are wrapped by phase (`load setting`, `list sessions`, `stat fs`, `statistic`) but partial results are not returned unless all requested work succeeds.

## Test Signals

The listed SQL tests do not directly target `Status`. It should be covered by backend-agnostic status or CLI tests that verify secret redaction, session listing, StatFS integration, and trash scan counters.
