# sources/distributed-fs/eos/mgm/proc/admin/SchedCmd.cc

## Purpose
`SchedCmd.cc` implements the protobuf-backed scheduler administration command for configuring and inspecting filesystem placement scheduler state.

## Important APIs, Types, And Functions
`SchedCmd::ProcessRequest()` dispatches `SchedProto` cases. `ConfigureSubcmd()` dispatches nested configure options to `SchedulerTypeSubcmd()`, `WeightSubCmd()`, `ShowSubCmd()`, and `RefreshSubCmd()`. `LsSubcmd()` emits scheduler state. The implementation calls `gOFS->mFsScheduler` methods such as `setPlacementStrategy()`, `getPlacementStrategy()`, `setDiskWeight()`, `getStateStr()`, and `updateClusterData()`, and formats strategy names through `placement::strategy_to_str()`.

## Control Flow
Top-level dispatch supports `config` and `ls`; unsupported top-level cases return `EINVAL`. Configure dispatch supports type, weight, show, and refresh. Type changes set the default scheduler strategy. Weight changes update a specific fsid weight in a space and fail on scheduler rejection. Listing maps enum options to `bucket`, `disk`, or `all` before requesting a scheduler state string. Show currently handles scheduler type display, optionally for a named space. Refresh forces cluster data refresh.

## State, Persistence, And Dependencies
The command mutates in-memory scheduler state through `mFsScheduler`; any persistence depends on scheduler internals or other config paths, not this file. It depends on the global MGM object, placement strategy definitions, and generated scheduler protobufs. There is no explicit authorization check or lock in this implementation.

## Integration Points
This command is the console protobuf entry point for scheduler inspection and limited configuration. It overlaps with `SpaceCmd`'s `space config ... scheduler.type` path, which sets per-space scheduler strategy and persists it as space config.

## Risks
The absence of local root/admin gating means safety depends on outer command authorization. `ShowSubCmd()` returns a default reply if the requested option is not `TYPE`, which can look successful with empty output. Scheduler state changes are made without explicit synchronization in this file. Formatting has minor spacing issues in success strings but no behavioral impact.

## Test Signals
Cover unsupported top-level and configure cases, default and per-space scheduler type changes, invalid disk weight updates, list modes for bucket/disk/all, refresh behavior, and authorization through the surrounding command dispatcher. Tests should also verify `ShowSubCmd()` behavior for non-`TYPE` options.
