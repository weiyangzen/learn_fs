<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_emulate.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_emulate.c

Purpose: Emulates generic BookE privileged instructions and special-purpose register accesses that cannot execute directly in the guest context.

Important APIs/types/functions: Implements `kvmppc_booke_emulate_op()`, `kvmppc_booke_emulate_mtspr()`, and `kvmppc_booke_emulate_mfspr()`. Internal helpers emulate `rfi`, `rfci`, and `rfdi`. It decodes op 19 return instructions and op 31 MSR operations (`mfmsr`, `mtmsr`, `wrtee`, `wrteei`) plus a large set of BookE SPRs including DEAR/ESR, CSRR/DSRR, debug registers, TSR/TCR/DECAR, SPRG4-7, IVPR/IVORs, MCSR, and EPCR.

Control flow: Instruction emulation first switches on primary opcode and extended opcode, updates vCPU architectural state, sets exit accounting type, and controls whether the PC advances. SPR writes update vCPU state, optionally mask unsupported debug bits, synchronize debug hardware when guest-owned debug registers change, preserve TCR WRC semantics, and defer to failure when an unknown SPR is seen. SPR reads return the virtualized backing state and expose `DBCR0_EDM` when userspace owns debugging.

State and persistence: Persists guest return state in SRR/CSRR/DSRR, exception metadata in DEAR/ESR/MCSR, timer state in TSR/TCR/DECAR, IVPR/IVOR exception vector offsets, debug address/control/status registers, EPCR, SPRG values, and guest-visible MSR. Writes often have side effects such as clearing TSR/DBSR bits, dequeuing debug exceptions, or updating shadow MSR through `kvmppc_set_msr()`.

Dependencies and integration points: Depends on `asm/disassemble.h` decoders, `booke.h` setters and queue helpers, PowerPC SPR constants, debug register switching, and e500 fallback dispatch from `e500_emulate.c`.

Risks: SPR behavior is architecture-visible and migration-visible. Incorrect DBCR/DBSR ownership can leak host debug resources or hide guest debug events. `wrtee/wrteei` update only MSR[EE], so callers must not use them as full MSR synchronization. The BookE-HV note warns that some registers are real hardware-backed in GS mode and these helpers can be wrong outside the intended trap context.

Test signals: Privileged instruction emulation tests, guest return-from-interrupt paths, timer SPR read/write tests, guest debug register tests with and without userspace debug, EPCR/IVOR migration round trips, and e500 fallback SPR tests are relevant.

Source read size: 511 lines, 11297 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke_emulate.c -->
