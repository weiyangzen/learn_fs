<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.cc -->
# sources/distributed-fs/eos/mgm/proc/IProcCommand.cc

Source read size: 633 lines, 21528 bytes.

## Purpose

Implements the asynchronous protobuf-based proc command base class for MGM commands. It manages command execution slots, thread-pool dispatch, streaming responses, temporary output files, JSON formatting, path/id resolution, routing redirects, and comment logging.

## Important APIs, Types, and Functions

Key methods are `open`, `read`, `LaunchJob`, `KillJob`, `OpenTemporaryOutputFiles`, `CloseTemporaryOutputFiles`, `ConvertOutputToJsonFormat`, `ResponseToJsonString`, `GetPathFromFid`, `GetPathFromCid`, `IsOperationForbidden`, `ShouldRoute`, `HasSlot`, and `ResolveIdentifierToPath`. Static state includes `uuid`, `mMapCmdsMutex`, and `mCmdsExecuting`.

## Control Flow

`open` launches `ProcessRequest` once a per-command slot is available, either via `ProcInterface::sProcThreads` or synchronously through a ready promise. It waits up to five seconds; not-ready jobs stall the client, slot exhaustion stalls for a shorter delay, and ready jobs are converted to redirect/stall, file-backed streams, or an in-memory `mgm.proc.*` response. It logs privileged comments with the protobuf request serialized to JSON. `read` drains stdout, stderr, and return-code streams in order for file-backed output, or slices `mTmpResp` by offset. JSON conversion parses key/value lines into nested JSON with compatibility rewrites for known flat status keys. Identifier helpers resolve fid/fxid/cid/cxid to namespace paths.

## State and Persistence Behavior

Each command object owns future state, request identity, routing info, temp filenames/streams, and result buffers. Static command counters enforce up to 50 queued/running commands per command type and are decremented in the destructor. Temporary files are created under `/var/tmp/eos/mgm/` and unlinked by close/destruction. Comments can persist through `gOFS->mCommentLog`.

## Dependencies and Integration Points

Depends on protobuf request/reply types, `ProcInterface` thread pool, XRootD SFS interfaces, MGM redirect/stall, namespace services, JSONCPP, protobuf JSON conversion, `ProcBounce*` validation, and `CommentLog`.

## Risks and Edge Cases

The slot counter relies on destructor cleanup; leaked command objects leak capacity. Async jobs capture `this`, so object lifetime must be controlled by `KillJob` and caller ownership. `ConvertOutputToJsonFormat` advances `jep` twice per token level, which deserves scrutiny. File output uses fixed `/var/tmp/eos/mgm/` rather than `TmpStorePath`. Identifier resolution does not take an explicit namespace view lock in `ResolveIdentifierToPath`.

## Test Signals

Test async ready/stall/slot-exhaustion paths, redirect and route-stall replies, file-backed and memory-backed reads with offsets, comment logging authorization, JSON conversion of nested and conflicting keys, fid/fxid/cid/cxid resolution success/failure, forbidden path checks, destructor cleanup, and command counter decrementing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.cc -->
