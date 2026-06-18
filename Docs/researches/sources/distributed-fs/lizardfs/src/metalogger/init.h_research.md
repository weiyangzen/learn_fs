# sources/distributed-fs/lizardfs/src/metalogger/init.h

## Purpose

`metalogger/init.h` defines the metalogger module initialization tables used by the common application startup framework. The source was read as a complete 42-line header.

## Important APIs, Types, and Functions

It defines `runfn`, `run_tab`, and three arrays: `RunTab` containing `masterconn_init` named "connection with master", and empty sentinel-only `LateRunTab` and `EarlyRunTab`.

## Control Flow

At application startup, the common runner walks these tables and calls `masterconn_init` as the metalogger's primary initialization step. Sentinel entries with null function and `"****"` terminate each table.

## State and Persistence Behavior

The header owns no persistent state. Initialization connects the metalogger process to the master through `masterconn_init`.

## Dependencies and Integration Points

It includes `master/masterconn.h` even though it lives under metalogger, reflecting shared connection code. It is tied to the common main/init table convention.

## Risks and Edge Cases

Because the arrays are defined in a header, include discipline matters to avoid multiple-definition problems; the project likely includes this as a generated/app-specific init header in one translation unit. No early or late init hooks are registered here.

## Test Signals

Build/link success for `mfsmetalogger`, startup smoke tests verifying `masterconn_init` runs, and failure-path tests for master connection initialization.
