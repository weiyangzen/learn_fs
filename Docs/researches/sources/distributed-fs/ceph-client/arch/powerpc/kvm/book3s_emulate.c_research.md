# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_emulate.c

## Purpose

`book3s_emulate.c` implements instruction and SPR emulation for Book3S PR KVM guests. It decodes privileged Book3S instructions that trap to the host, updates the vCPU register/MMU model, synthesizes architected exceptions, and handles special facilities such as transactional memory and paired-single emulation. It is the PR-mode counterpart to the HV code paths, and it is used when hardware execution cannot directly perform a guest operation.

## Important APIs, Types, And Functions

The file defines opcode constants for `rfid`, `rfi`, MSR access, segment register access, SLB operations, TLB invalidation, `dcbz`, Book3S hypercall trapping, transactional memory operations, floating-point load/store alignment handling, and Gekko/Broadway paired-single registers. `enum priv_level` and `spr_allowed()` enforce access restrictions for problem, supervisor, and hypervisor SPRs; PAPR guests are prevented from using hypervisor-only SPRs and problem-state guests are limited to problem-visible state.

When `CONFIG_PPC_TRANSACTIONAL_MEM` is enabled, `kvmppc_copyto_vcpu_tm()`, `kvmppc_copyfrom_vcpu_tm()`, `kvmppc_emulate_treclaim()`, `kvmppc_emulate_trchkpt()`, and exported `kvmppc_emulate_tabort()` move checkpointed register state between live vCPU state and TM save areas, manipulate TEXASR/TFIAR/TFHAR, and enforce ISA transaction-state transitions.

`kvmppc_core_emulate_op_pr()` is the main instruction emulator. It handles reversed little-endian legacy syscall traps, return-from-interrupt instructions, MSR reads/writes, segment register reads/writes, TLB invalidation, PAPR `sc 1` hypercall exits, SLB management, `dcbz`, and TM soft emulation. It falls back to `kvmppc_emulate_paired_single()` when normal decoding fails.

`kvmppc_set_bat()` and `kvmppc_find_bat()` maintain the PR guest's instruction/data BAT model. `kvmppc_core_emulate_mtspr_pr()` and `kvmppc_core_emulate_mfspr_pr()` implement SPR write/read behavior for SDR1, DSISR, DAR, HIOR, BATs, HID registers, GQRs, FSCR, EBB registers, TM SPRs, PMU/debug-related SPRs, and unimplemented SPR exception behavior. `kvmppc_alignment_dsisr()` and `kvmppc_alignment_dar()` provide alignment-fault metadata.

## Control Flow

Instruction emulation begins with opcode extraction (`get_op`, `get_xop`, register field helpers) and a switch over primary opcode. `rfi`/`rfid` copies SRR0/SRR1 into PC/MSR and suppresses normal PC advance. MSR writes either update RI/EE only for the special `mtmsrd` form or replace the guest MSR through `kvmppc_set_msr()`. Segment, SLB, and TLB operations delegate into the vCPU MMU function table if the active Book3S MMU implementation supports the operation.

For PAPR `sc 1`, the emulator validates that the guest is not in problem state and that PAPR is enabled. It first tries in-kernel PR hcall handling; if not handled, it fills `run->papr_hcall`, sets `KVM_EXIT_PAPR_HCALL`, marks `hcall_needed`, and returns to userspace.

`dcbz` computes the effective 32-byte-aligned address, stores a zero cache block through `kvmppc_st()`, and on translation or permission failure records DAR/DSISR fields and queues a data-storage interrupt without advancing the PC.

The TM cases perform facility-unavailable checks first. Privileged-only TM operations queue program interrupts for problem-state or illegal transaction-state combinations. Otherwise they temporarily enable host TM, move state through the vCPU save areas, update TEXASR/TFIAR/TFHAR, and adjust guest MSR transaction bits.

SPR emulation is a separate switch keyed by SPR number. BAT writes update parsed BAT fields and flush PR MMU PTE and segment caches. Invalid SPR access logs a rate-limited message and queues privileged-instruction or illegal-instruction program interrupts depending on SPR encoding and guest privilege.

## State And Persistence Behavior

All state is runtime vCPU state. The file mutates `vcpu->arch.regs`, `vcpu->arch.shregs`, PR Book3S extension state (`to_book3s(vcpu)`), MMU shadow state, BAT caches, HID/GQR arrays, TM checkpoint arrays, and fault fields. It does not persist data outside the VM. Some operations intentionally flush guest MMU caches after control-register changes. TM paths temporarily affect per-CPU hardware TM registers and use preemption disabling so host thread state and vCPU state do not migrate mid-operation.

## Dependencies And Integration Points

The code depends on PowerPC instruction decoding helpers, Book3S KVM vCPU structures, the PR MMU callback table, TM helper routines, paired-single emulation, KVM exit ABI fields, and Book3S interrupt queuing helpers. It integrates with userspace through `KVM_EXIT_PAPR_HCALL` and with the generic KVM run loop through `EMULATE_DONE`, `EMULATE_FAIL`, `EMULATE_AGAIN`, and `EMULATE_EXIT_USER` return codes.

## Risks

Privilege filtering is security-sensitive; allowing a PAPR or problem-state guest to access hypervisor-level SPRs would expose state that should be virtualized or unavailable. The TM code is fragile because it mixes host TM enablement, vCPU save areas, preemption control, and ISA-specific failure-summary semantics. BAT writes require broad MMU flushes; missing a flush can leave stale translations. `dcbz` fault synthesis must keep DAR, DSISR, and PC advancement consistent or guest recovery paths will see incorrect storage exceptions. Unsupported SPR behavior is intentionally permissive for several legacy registers, so changes need compatibility testing.

## Test Signals

Useful signals include PR Book3S guests booting through MSR, segment, SLB, and BAT setup; PAPR hypercalls either handled in kernel or surfaced to userspace with correct arguments; problem-state invalid SPR accesses producing program interrupts; `dcbz` faults matching guest expectations; paired-single workloads on Gekko/Broadway-like PVRs; and transactional-memory guests exercising `tbegin`, `tabort`, `treclaim`, and `trecheckpoint` without host TM state leakage or incorrect MSR TS transitions.
