# sources/distributed-fs/ceph-client/arch/powerpc/boot/crtsavres.S

## Purpose
32-bit PowerPC boot-wrapper runtime support routines for compiler-generated GPR save/restore calls, derived from GCC rs6000 support. PPC64 intentionally uses linker-provided routines instead.

## Important APIs, Types, And Control Flow
The file defines `_savegpr_14` through `_savegpr_31` and `_save32gpr_*` aliases, storing r14-r31 at fixed negative offsets from r11. It defines `_restgpr_14` through `_restgpr_31` and `_rest32gpr_*` aliases, loading the same offsets. The `_restgpr_*_x` variants restore registers, load LR from `4(r11)`, move r11 back to r1, and return for epilogue-with-exit sequences.

## State, Dependencies, Risks, And Tests
State is the caller stack save area addressed by r11 and, for `_x` variants, LR and SP. Dependencies include the PowerPC EABI/SVR4 ABI, GCC code generation, and boot-wrapper linking when not using `CONFIG_PPC64_BOOT_WRAPPER`. Risks are offset/ABI mismatch, accidental ppc64 inclusion, and missing symbols under compiler options that emit save/restore calls. Test by compiling wrapper C with register pressure, linking without unresolved `_savegpr`/`_restgpr` symbols, and booting paths that exercise non-leaf functions.
