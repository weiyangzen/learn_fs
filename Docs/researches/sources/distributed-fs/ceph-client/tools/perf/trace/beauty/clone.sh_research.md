# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/clone.sh

## Purpose
This generator reads UAPI `linux/sched.h` and emits a C string array mapping clone flag bit positions to suffix names for `clone.c`.

## Important APIs, Types, And Functions
It is a shell script taking an optional beauty UAPI linux directory. It uses grep, sed, and xargs to emit `static const char *clone_flags[]`.

## Control Flow
The script selects `tools/perf/trace/beauty/include/uapi/linux/` by default, sets `linux_sched`, prints an array opener, greps `#define CLONE_* 0x...` lines, rewrites each to `<hex> <name_without_CLONE_>`, and formats entries as `[ilog2(value) + 1] = "NAME"`.

## State, Dependencies, And Integration
No persistent state is written directly; the Makefile redirects stdout to a generated include. It depends on bitmask values being powers of two because the generated index uses `ilog2(value) + 1`.

## Risks And Test Signals
The regex only captures hex constants and may miss expression-defined or non-power-of-two flags. Generated output should compile and `perf trace` should decode representative clone flags correctly.
