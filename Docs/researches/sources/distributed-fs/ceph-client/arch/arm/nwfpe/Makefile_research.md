# sources/distributed-fs/ceph-client/arch/arm/nwfpe/Makefile

## Purpose
Builds the NetWinder Floating Point Emulator object when `CONFIG_FPE_NWFPE` is enabled and adds optional extended-precision support.

## Important APIs, Types, And Functions
Defines `obj-$(CONFIG_FPE_NWFPE) += nwfpe.o`, the `nwfpe-y` object list, and `nwfpe-$(CONFIG_FPE_NWFPE_XP) += extended_cpdo.o`. Adds a Clang-specific flag for `softfloat.o` to avoid generating `__aeabi_uldivmod()` from `float64_rem()`.

## Control Flow
Kbuild links emulator core files into `nwfpe.o`; extended precision is conditionally linked. Compiler flags are conditionally applied for Clang.

## State, Dependencies, And Integration
No runtime state. Dependencies are Kconfig, Kbuild, compiler identity, and all listed NWFPE/SoftFloat sources. Integration is with ARM undefined-instruction handling and module init.

## Risks And Test Signals
Risks are missing object files, extended-precision link failures, and compiler optimization generating unavailable helper calls. Test signals are GCC and Clang ARM builds with and without `CONFIG_FPE_NWFPE_XP`, plus boot/module load of NWFPE.
