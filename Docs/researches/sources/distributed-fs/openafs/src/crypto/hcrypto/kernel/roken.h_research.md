# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/roken.h

This kernel-only roken stub exposes just enough of Heimdal's roken API for kernel hcrypto. It requires `KERNEL`, strips roken export annotations, defines `HAVE_STRLCPY`/`HAVE_STRLCAT` defaults with platform exceptions, aliases missing functions to `rk_strlcpy`/`rk_strlcat`, and declares `ct_memcmp`.

There is no runtime state in the header. Dependencies are kernel platform macros and any compiled roken replacement functions. Integration is hcrypto and RFC3961 kernel code using roken string and constant-time comparison helpers. Risks are mismatch between userspace autoconf availability and kernel availability, especially Linux without `strlcpy` and AIX without both functions. Test signals are kernel builds on exception platforms and crypto checksum tests that rely on `ct_memcmp`.
