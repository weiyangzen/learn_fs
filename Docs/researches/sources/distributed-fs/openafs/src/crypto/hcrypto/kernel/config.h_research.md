# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/config.h

This kernel hcrypto config shim makes userspace Heimdal hcrypto sources build inside OpenAFS kernel code. It includes OpenAFS config, standard, sysinclude, afs include, and prototype headers; maps `assert` to `osi_Assert`; removes conflicting kernel macros like `current` and `u`; normalizes `inline`; and remaps libc allocation/string/random/process APIs to kernel-safe substitutes.

Important APIs are macro remaps for `calloc`, `malloc`, `free`, `strdup`, `realloc`, `strcasecmp`, `getpid`, `abort`, `open`, `read`, `close`, `rk_cloexec`, and optionally `gettimeofday`. It declares `osi_readRandom`, provides `_afscrypto_getpid` returning 1, `_afscrypto_abort` panicking, and stubs unsupported file operations. For Solaris and arm64 Linux kernel builds, it remaps `double` to `void *` to avoid floating-point ABI use.

There is no persistence except through functions it redirects to. Integration is every kernel hcrypto source compiled with this config. Risks are broad macro side effects, disabled entropy sources, stubbed file I/O, artificial PID entropy, and replacing `double` in function signatures. Test signals are kernel module builds on Linux, Solaris, AIX, HPUX, SGI, and runtime crypto/RNG tests.
