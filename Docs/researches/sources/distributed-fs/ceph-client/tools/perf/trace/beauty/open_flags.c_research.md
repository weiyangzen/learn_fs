# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/open_flags.c

Purpose: Formats `open/openat/openat2` style file flags and hides the mode argument when it is ignored.

Important APIs/types/functions: `open__scnprintf_flags` is a reusable formatter; `syscall_arg__scnprintf_open_flags` wraps it for syscall arguments and sets `arg->mask` for the following mode parameter when `O_CREAT` is absent.

Control flow: The formatter handles access mode first, emitting `O_RDONLY` for zero. It then walks known `O_*` bits, handles platform `O_NONBLOCK` versus `O_NDELAY`, detects `O_SYNC` versus `O_DSYNC`, clears printed bits, and appends unknown leftovers.

State and persistence: It only mutates per-syscall display mask state.

Dependencies and integration points: Depends on `<fcntl.h>` and local fallbacks for flags missing on older libc headers. Used by perf trace syscall tables.

Risks: `O_TMPFILE` and access-mode combinations are subtle because some flags are masks rather than independent bits. Mode hiding only keys on `O_CREAT`, while some APIs may also require mode for `O_TMPFILE`.

Test signals: Trace `openat` with read-only, create, tmpfile, sync, nonblock, and unknown bits. Verify mode visibility follows expected kernel semantics.
