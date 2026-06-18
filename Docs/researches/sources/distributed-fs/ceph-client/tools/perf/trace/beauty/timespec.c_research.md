# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/timespec.c

Purpose: Formats `struct timespec *` syscall arguments when augmented user memory is available.

Important APIs/types/functions: `syscall_arg__scnprintf_timespec` prints either a structured `{ .tv_sec, .tv_nsec }` value or the raw pointer. `syscall_arg__scnprintf_augmented_timespec` does the structured rendering.

Control flow: The wrapper tests `arg->augmented.args`; present augmented data is cast to `struct timespec`, absent data falls back to hex pointer formatting.

State and persistence: Reads only captured syscall memory; no persistent state.

Dependencies and integration points: Depends on syscall augmentation, `struct timespec`, and `PRIu64` formatting.

Risks: The code assumes captured bytes are large enough for `struct timespec` and prints fields as unsigned 64-bit values. ABI time-size differences may need care on 32-bit builds.

Test signals: Trace syscalls with timespec pointers with augmentation on/off; test NULL and invalid pointers.
