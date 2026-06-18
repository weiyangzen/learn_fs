# File Research: sources/block-storage/util-linux/sys-utils/setarch.c

This file implements `setarch(8)` and its architecture-name wrapper aliases. It changes the process personality architecture and optional personality flags before executing a command or shell. It also lists supported architecture names and shows current or target process personality values.

Architecture support is encoded in `init_arch_domains()`, which builds a static transition table conditioned on compile-time architecture macros and adds the running machine as a trivial transition when appropriate. It maps names such as `linux32`, `linux64`, `i386`, `x86_64`, `arm`, `aarch64`, `ppc`, `s390`, `sparc`, `mips`, `riscv`, and others to `PER_*` values and expected `uname` results. `verify_arch_domain()` checks that the kernel accepted the requested architecture.

Personality flags include address limit flags, no-randomize, read-implies-exec, mmap-page-zero, sticky-timeouts, uname-2.6, FDPIC function pointers, and compatibility options. `--show` decodes the personality and option bits into symbolic names, optionally using `/proc/<pid>/personality`. After calling `personality()`, the command execs the provided program or a login-style `/bin/sh`.
