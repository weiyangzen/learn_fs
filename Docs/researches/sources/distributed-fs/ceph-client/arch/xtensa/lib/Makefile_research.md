# sources/distributed-fs/ceph-client/arch/xtensa/lib/Makefile

Purpose: Selects Xtensa architecture library objects for kernel linking.

Important APIs, types, and functions: `lib-y` includes memory, checksum, compiler helper, usercopy, and string-user routines; `lib-$(CONFIG_ARCH_HAS_STRNCPY_FROM_USER)` adds `strncpy_user.o`; `lib-$(CONFIG_PCI)` adds `pci-auto.o`.

Control flow: Kbuild compiles the listed objects into the architecture library. Optional objects are selected by config symbols so PCI autoconfiguration and `strncpy_from_user` support are only linked when needed.

State and persistence: No runtime state; it controls link-time availability of exported symbols like `memcpy`, `memset`, arithmetic helpers, cache/user copy helpers, and PCI scan helpers.

Dependencies and integration: Integrated by arch kbuild into the kernel image and module symbol namespace; assembly files depend on Xtensa core feature macros.

Risks: Missing helper objects can lead to unresolved compiler-generated symbols; optional string-user coverage must match `asm/uaccess.h` expectations; architecture feature variants must compile across cores with and without hardware multiply/divide/loops.

Test signals: All Xtensa defconfig builds, module link checks for exported helpers, PCI-enabled build, and `CONFIG_ARCH_HAS_STRNCPY_FROM_USER` toggles.
