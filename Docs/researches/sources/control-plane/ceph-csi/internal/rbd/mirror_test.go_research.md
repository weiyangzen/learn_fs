# sources/control-plane/ceph-csi/internal/rbd/mirror_test.go

## Purpose
Tests parsing of librbd mirror status description strings into `SyncInfo`.

## Important APIs, Types, And Functions
`TestValidateLastSyncInfo` exercises `newSyncInfo` through valid JSON, empty descriptions, missing optional fields, missing required local snapshot timestamp, zero duration, invalid JSON, and no-JSON descriptions.

## Control Flow
The table-driven parallel test calls `newSyncInfo`, checks whether returned errors contain expected substrings, and when a struct is returned compares last sync time, duration, and byte count through the `types.SyncInfo` interface.

## State And Persistence
No persistent state is used. Inputs are static status-description strings that model librbd output.

## Dependencies And Integration Points
Depends on RBD error sentinel `ErrLastSyncTimeNotFound` and `types.SyncInfo`. It protects the parser used by mirror status and resync flows.

## Risks And Test Signals
The test gives strong coverage for current description formats, including optional byte/duration fields. It cannot detect changes in live librbd status formatting beyond the included samples, and it does not cover mirror promote/demote/resync operations.
