# sources/distributed-fs/ceph-client/arch/x86/lib/msr-reg-export.c

Purpose: exports safe MSR register-array access helpers implemented in assembly.

Important APIs/functions: exports `rdmsr_safe_regs` and `wrmsr_safe_regs`.

Control flow: none locally; this file only emits export records for the assembly symbols.

State and persistence behavior: no state. Runtime behavior is in `msr-reg.S`.

Dependencies/integration points: depends on `<asm/msr.h>` declarations and the linked `msr-reg.o` symbols. Modules or subsystems needing safe MSR operations with full register arrays rely on these exports.

Risks: if exports are missing or mismatched, modular MSR users fail to link. Symbol names must match assembly exactly.

Test signals: module link tests for MSR helpers and build coverage across 32-bit/64-bit configs.
