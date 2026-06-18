<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkuboot.sh -->
# sources/distributed-fs/ceph-client/scripts/mkuboot.sh

## Purpose

`mkuboot.sh` invokes U-Boot `mkimage` when the tool is available. It is a thin availability/check wrapper used by architecture image rules that already assemble the correct `mkimage` arguments.

## Important APIs, Types, and Functions

The script has no internal functions. It chooses `${CROSS_COMPILE}mkimage` first, then falls back to host `mkimage`, and forwards all original arguments with `"$@"`.

## Control Flow

It searches `PATH` with `type -path`. If no tool is found it prints a warning-style error and exits non-zero; otherwise it executes the selected `mkimage` with the caller-provided argument vector.

## State and Persistence Behavior

The only persistent effect is whatever output file the forwarded `mkimage` invocation creates.

## Dependencies and Integration Points

It depends on U-Boot `mkimage`, optional `CROSS_COMPILE`, and Kbuild-provided command arguments. It integrates with architecture boot-image targets.

## Risks and Edge Cases

Wrong load/entry addresses, compression labels, architecture strings, or stale input images produce boot failures that the wrapper cannot detect because it only forwards arguments. Missing `mkimage` causes the image target to fail.

## Test Signals

Build a known image, inspect it with `mkimage -l`, and boot it under the target firmware or emulator. Negative tests should cover missing host and cross `mkimage`, missing input, and invalid forwarded parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mkuboot.sh -->
