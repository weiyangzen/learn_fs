# sources/distributed-fs/ceph-client/arch/csky/kernel/probes/simulate-insn.h

Purpose: probe simulation table macros and simulator declarations.

Important APIs/types/functions: macros: `__CSKY_KERNEL_PROBES_SIMULATE_INSN_H`, `__CSKY_INSN_FUNCS(name,`, `CSKY_INSN_SET_SIMULATE(name,`

Control flow: There is no standalone runtime flow; consumers include the header and expand its constants, inline helpers, types, and prototypes at compile time.

State and persistence: No runtime persistence in this file; it contributes compile-time symbols, declarations, constants, or object selection.

Dependencies and integration: Depends on architecture-local and generic Linux kernel declarations. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: ABI, bitfield, or inline-helper mistakes propagate to many translation units and can break boot, userspace ABI, locking, or memory management.

Test signals: C-SKY cross-build; ftrace, kprobes, uprobes, and jump-label selftests.
