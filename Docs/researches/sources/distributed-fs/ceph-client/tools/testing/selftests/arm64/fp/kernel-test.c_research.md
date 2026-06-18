<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/kernel-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/kernel-test.c

Purpose: stress test for kernel-mode FP/SIMD use by repeatedly running AF_ALG hash operations backed by known arm64 crypto drivers and checking digest stability under signals.

Important APIs and functions: `create_socket` scans `/proc/crypto`, opens `AF_ALG` hash socket, binds to a matching driver, accepts an operation socket, creates a zero-copy pipe, and allocates digest buffers. `compute_digest` sends data using `vmsplice` and `splice`, then `recv`s the digest. Signal handlers count SIGUSR1/SIGUSR2 and report on SIGTERM.

Control flow: install signal handlers, allocate a zeroed 64 KiB buffer, discover a kernel crypto hash driver using FP/NEON/CE, or fall back to `./fpsimd-test` if unsupported. Compute a reference digest, then loop computing and comparing digests forever.

State and persistence: global sockets, pipe FDs, algorithm name, digest buffers, signal count, and iteration count. No persistent files; reads `/proc/crypto`.

Dependencies and integration: called by `fp-stress` as a child named `KERNEL-*`. Depends on AF_ALG, kernel crypto drivers, and splice/vmsplice support.

Risks: driver list is static and can miss newer implementations. The `recv` retry compares `errno` to `-EAGAIN`, which is unusual because `errno` is positive. Fallback typo in the error message says `fspimd-test`.

Test signals: startup prints selected algorithm. Any digest mismatch, socket failure, or allocation failure exits nonzero; SIGTERM reports iterations and signal count with exit 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/kernel-test.c -->
