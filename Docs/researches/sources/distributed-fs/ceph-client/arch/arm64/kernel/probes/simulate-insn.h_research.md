# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/simulate-insn.h

Purpose: this private header declares the ARM64 probe instruction simulator entry points used by the decoder and probe handlers.

Important APIs: it declares one function per simulated instruction family: ADR/ADRP, B/BL, conditional branch, BR/BLR, RET, CBZ/CBNZ, TBZ/TBNZ, LDR literal, LDRSW literal, and NOP. Each takes `u32 opcode`, original instruction address as `long addr`, and mutable `struct pt_regs *regs`.

Control flow and state: no local state. The common signature lets `arch_probe_insn.handler` point at any simulator function and lets kprobe/uprobe code invoke the handler uniformly.

Dependencies and integration: included by `decode-insn.c` to assign handlers and by `simulate-insn.c` for declarations. Callers must provide pt_regs from the active exception context.

Risks: adding a simulator in C without declaring it here prevents the decoder from assigning it cleanly. Changing the signature breaks the handler callback ABI embedded in architecture probe structs.

Test signals: all simulator functions should be referenced by decode paths and covered by probe registration/execution tests for their instruction families.
