# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-log-ops.c

## Purpose
`glusterd-log-ops.c` implements the CLI-facing and operation-state-machine pieces of volume log rotation. It decodes log-rotate requests, validates target volume/brick state, and performs local brick logfile rename plus `SIGHUP` to trigger log reopening.

## Important APIs, Types, And Functions
`glusterd_handle_log_rotate()` wraps `__glusterd_handle_log_rotate()` in the GlusterD big lock. `glusterd_op_stage_log_rotate()` validates the operation during the op-sm stage phase. `glusterd_op_log_rotate()` performs the commit work on local bricks. The operation uses dict keys `volname`, optional `brick`, and internally added `rotate-key`.

## Control Flow
The request handler decodes `gf_cli_req`, unserializes the dict, extracts `volname`, logs the request, writes `rotate-key` with the current time, and starts the transaction through `glusterd_op_begin_synctask(req, GD_OP_LOG_ROTATE, dict)`. On early failure it sends a CLI response with an explanatory message.

The stage function requires `volname`, verifies the volume exists, rejects stopped volumes, and optionally validates a specific `brick` against the volume. Absence of a brick is treated as "all bricks" and is not an error.

The commit function retrieves the volume and rotate key, optionally parses a specific brick into temporary brickinfo, iterates local bricks for the volume, skips remote bricks, filters to the requested brick if present, reads the brick pidfile, renames the current logfile to `<logfile>.<rotate-key>`, and sends `SIGHUP` to the brick process. If the request named one brick, it stops after that brick. If no local matching brick exists, it treats the operation as successful for this node.

## State And Persistence Behavior
The handler mutates the operation dict by adding a timestamp rotate key so every node uses the same suffix. The commit path changes filesystem state by renaming brick logfiles and signals running brick processes. It does not update persistent GlusterD store metadata. Temporary brickinfo allocated for requested brick parsing is deleted before return.

## Dependencies And Integration Points
The file integrates with CLI XDR, GlusterD op-sm/synctask execution, volume and brick lookup utilities, pidfile path macros, syscall wrappers, and process signaling. It relies on brick processes honoring `SIGHUP` by reopening logs after the old file has been renamed.

## Risks
The implementation reads pidfiles and sends signals directly; stale pidfiles can signal the wrong process if process reuse is possible. Rename failure is logged as a warning but does not immediately abort before `SIGHUP`, which may still rotate from the brick process's perspective depending on logger behavior. Missing pidfiles or unreadable pidfiles fail the operation for local matching bricks. Requested brick parsing must match hostname/path formatting exactly.

## Test Signals
Tests should cover request decode/unserialize failures, missing `volname`, stopped volume rejection, unknown brick rejection, all-bricks rotation across only local bricks, single-brick filtering, missing local brick success, pidfile open/read failures, logfile rename failure logging, `SIGHUP` failure, and use of a consistent `rotate-key` across staged/commit execution.
