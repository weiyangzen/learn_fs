# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.h

Purpose: public helper contract for the openat2 selftests, including fallback syscall numbers, openat2 ABI structures, resolver flags, assertions, and wrapper declarations.

Important APIs/types: defines `struct open_how` with 64-bit `flags`, `mode`, and `resolve`; `OPEN_HOW_SIZE_VER0`; fallback `__NR_openat2`; fallback `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_BENEATH`, and `RESOLVE_IN_ROOT`; `ARRAY_LEN()` and `BUILD_BUG_ON()`. The `E_func` family wraps libc/syscall helpers and aborts through kselftest on unexpected failure.

Control flow/integration: C test files include this header to share ABI definitions independent of userspace headers. The `extern bool openat2_supported` flag is initialized in `helpers.c` and consumed by tests to report skip rather than fail when the kernel lacks openat2.

State and dependencies: no runtime state beyond the extern flag declaration. It depends on Linux integer types, errno, kselftest, and GNU extensions.

Risks: fallback syscall number `437` is architecture-sensitive in general, but the kernel selftest environment expects the correct arch headers or this fallback. Fallback flag definitions must remain synchronized with kernel UAPI or tests could check the wrong bits.

Test signals: indirectly controls hard failures via `E_*` macros and compile-time checks via `BUILD_BUG_ON()`.
