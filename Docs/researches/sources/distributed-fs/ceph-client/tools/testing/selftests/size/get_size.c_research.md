# sources/distributed-fs/ceph-client/tools/testing/selftests/size/get_size.c

## Purpose
Minimal TAP-emitting program that reports runtime system memory use while avoiding libc startup and heavy dependencies.

## Important APIs, types, and functions
Implements raw-print helpers `print()`, `num_to_str()`, `print_num()`, and `print_k_value()`. Entry point is `_start()`, which uses only `syscall(SYS_sysinfo)`, `syscall(SYS_write)`, and `syscall(SYS_exit)`.

## Control flow
`_start()` prints TAP header, calls `sysinfo()`, reports failure as `not ok 1` if unavailable, otherwise computes used memory as `totalram - freeram - bufferram`, prints total/free/buffer/in-use values in KiB, prints `1..1`, and exits.

## State and persistence
No persistent state. Uses stack/local buffers and the kernel-provided `struct sysinfo`.

## Dependencies and integration points
Depends on syscall numbers provided by libc headers but not libc runtime initialization. Integrated as a kselftest generated program.

## Risks
The file warns that syscall failures may crash on some libc implementations because `errno` TLS is not initialized without startup files. Memory accounting intentionally ignores cache complexities.

## Test signals
Pass is `ok 1 get runtime memory use` followed by diagnostic memory report. Failure is `not ok 1` with reason `could not get sysinfo`.
