# sources/distributed-fs/ceph-client/tools/testing/selftests/net/lib/ksft.h

## Purpose
This small C header provides readiness and wait synchronization helpers for compiled networking selftest helpers run under the Python `bkg`/kselftest environment.

## Important APIs and Functions
`ksft_ready()` writes `ready\n` to the file descriptor named by `KSFT_READY_FD`, or stdout when the variable is absent. `ksft_wait()` reads one byte from `KSFT_WAIT_FD`, or stdin when the variable is absent. Both close non-stdio descriptors after use and report invalid fd values or I/O errors to stderr.

## Control Flow and State
There is no persistent state. The helpers bridge environment variables into file-descriptor handshakes: child programs call `ksft_ready()` after binding/listening and `ksft_wait()` before exit when the parent owns shutdown timing.

## Dependencies and Integration
It depends only on libc `getenv`, `atoi`, `write`, `read`, `close`, and stdio. It integrates with `lib/py/utils.py` command helpers, especially background commands using `ksft_ready` and `ksft_wait`, and is used by `gro.c` and `xdp_helper.c`.

## Risks and Test Signals
Fd `0` is treated as invalid for environment-provided descriptors, while missing variables deliberately fall back to stdio. A blocked `ksft_wait()` can hang if the parent never writes the byte. The readiness signal is the exact `ready\n` payload expected by the Python helper.
