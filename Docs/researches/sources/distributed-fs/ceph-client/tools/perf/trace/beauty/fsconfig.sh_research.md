# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsconfig.sh

## Purpose
This generator emits a command-name array for the `fsconfig` syscall's `FSCONFIG_*` command enum.

## Important APIs, Types, And Functions
It takes an optional UAPI linux header directory, reads `mount.h`, and emits `static const char *fsconfig_cmds[]`.

## Control Flow
The script prints the array opener, then uses `sed -nr` to match enum-style lines of the form `FSCONFIG_NAME = NUMBER,` and emits array entries indexed by that number.

## State, Dependencies, And Integration
Output is consumed by `builtin-trace.c`, which defines `strarray__fsconfig_cmds` and uses it for syscall argument formatting. The script depends on mount.h using enum syntax rather than preprocessor defines.

## Risks And Test Signals
If upstream changes formatting or assigns expressions instead of decimal literals, entries may be missed. Tests should check that known commands such as set-string, set-binary, set-path, and command create/reconfigure print symbolically.
