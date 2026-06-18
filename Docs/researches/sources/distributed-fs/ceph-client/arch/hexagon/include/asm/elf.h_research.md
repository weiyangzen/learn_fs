# sources/distributed-fs/ceph-client/arch/hexagon/include/asm/elf.h

Purpose: Hexagon ELF machine constants, relocations, and executable/core-dump ABI.

Important APIs/types/functions: types: `elf32_hdr`, `linux_binprm`; macros: `__ASM_ELF_H`, `R_HEXAGON_NONE`, `R_HEXAGON_B22_PCREL`, `R_HEXAGON_B15_PCREL`, `R_HEXAGON_B7_PCREL`, `R_HEXAGON_LO16`, `R_HEXAGON_HI16`, `R_HEXAGON_32`, `R_HEXAGON_16`, `R_HEXAGON_8`, `R_HEXAGON_GPREL16_0`, `R_HEXAGON_GPREL16_1`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/ptrace.h`, `asm/user.h`, `linux/elf-em.h`. It integrates with the Hexagon architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: Hexagon cross-build; ptrace, signal, seccomp, audit, and core-dump ABI tests.
