# sources/distributed-fs/ceph-client/include/linux/mlx5/rsc_dump.h

## Purpose
This header declares the mlx5 resource dump interface. It lets callers describe a firmware resource or resource range and iteratively retrieve dump segments into pages for diagnostics.

## Important APIs, Types, And Data
- `enum mlx5_sgmt_type` lists supported dump segment/resource types: hardware CQ/SQ/RQ contexts, full SRQ/CQ/EQ/QP contexts, send/receive/SRQ/CQ/EQ buffers, SX/RX slices, RDB, PRM query QP/CQ/MKEY, menu, terminate, and a count sentinel.
- `struct mlx5_rsc_key` identifies the resource to dump: segment type, two indexes, two object counts, and expected size.
- `struct mlx5_rsc_dump_cmd` is opaque to callers.
- `mlx5_rsc_dump_cmd_create()` allocates/prepares a dump command for a device and key.
- `mlx5_rsc_dump_next()` streams the next chunk into a caller-supplied `struct page` and returns its size.
- `mlx5_rsc_dump_cmd_destroy()` tears down command state.

## Control Flow
Diagnostic code creates a dump command from a key, repeatedly calls `mlx5_rsc_dump_next()` until firmware indicates completion or error, then destroys the command. The menu and terminate segment types allow discovery and stream termination semantics.

## State And Persistence
The opaque command object holds iteration state for an in-progress dump. Dumped resource data is a snapshot or firmware stream; this header does not persist it beyond pages supplied by callers. Firmware resources being dumped continue to live independently.

## Dependencies And Integration Points
It includes `linux/mlx5/driver.h` for device definitions and uses `struct page` for output buffers. It integrates with mlx5 diagnostics, devlink health reporters, debugfs, or crash-analysis paths that need firmware-visible resource state.

## Risks
Callers must destroy commands on all error paths. Segment indexes/counts/sizes must match firmware expectations or the dump may fail or return misleading data. Output pages must be valid and sized for the reported segment payload. Dumping live resources can race with resource teardown unless the implementation pins or validates objects.

## Test Signals
Tests should create and destroy commands for menu queries and representative QP/CQ/MKEY resources, iterate until completion, validate nonzero sizes, exercise invalid keys, and run dumps while resources are being created and destroyed to check cleanup and race handling.
