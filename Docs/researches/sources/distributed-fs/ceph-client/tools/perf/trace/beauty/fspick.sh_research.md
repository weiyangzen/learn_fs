# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fspick.sh

## Purpose
This generator emits a bit-indexed array for `FSPICK_*` mount API flags.

## Important APIs, Types, And Functions
It accepts an optional UAPI linux directory, reads `mount.h`, and emits `static const char *fspick_flags[]` using grep, sed, and xargs.

## Control Flow
The script filters hex `#define FSPICK_*` lines, rewrites each into `<value> <suffix>`, and formats entries as `[ilog2(value) + 1] = "SUFFIX"`.

## State, Dependencies, And Integration
No direct state is persisted; Makefile generation captures stdout. The output is included by `fspick.c`.

## Risks And Test Signals
It assumes flags are hex powers of two. Header formatting drift or compound masks would be missed. Tests should ensure generated arrays include all current `FSPICK_*` flags.
