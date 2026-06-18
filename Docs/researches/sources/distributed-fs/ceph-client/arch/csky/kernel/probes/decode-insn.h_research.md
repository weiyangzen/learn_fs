# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/decode-insn.h

Purpose: probe decoder declarations and C-SKY instruction-width helpers.

Important APIs/types/functions: types: `probe_insn`; macros: `__CSKY_KERNEL_KPROBES_DECODE_INSN_H`, `is_insn32(insn)`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on `asm/sections.h`, `asm/kprobes.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: C-SKY cross-build.
