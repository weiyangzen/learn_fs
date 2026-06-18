# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fs_at_flags.sh

## Purpose
This generator emits a bit-indexed `AT_*` flag name array for filesystem-at syscall beautifiers.

## Important APIs, Types, And Functions
It accepts an optional UAPI linux header directory, reads `fcntl.h`, and emits `static const char *fs_at_flags[]`. It uses grep, sed, and xargs with `ilog2(value) + 1` indexing.

## Control Flow
The script filters `#define AT_* 0x...` lines, explicitly excludes context-specific aliases such as `AT_EACCESS`, `AT_STATX_SYNC_TYPE`, handle flags, and `AT_RENAME_NOREPLACE`, then strips the `AT_` prefix and formats entries.

## State, Dependencies, And Integration
The generated table is included by `fs_at_flags.c`. It depends on bitmask values being powers of two and on header defines being hex literals.

## Risks And Test Signals
The intentional exclusions must stay aligned with C-side special cases and syscall-specific formatters. Tests should verify generated entries do not include aliases that would make generic output misleading.
