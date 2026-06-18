# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm.c

## Purpose

`book3s_hv_tm.c` emulates selected transactional memory instructions for POWER9 DD2.2 softpatch interrupts. It handles cases where hardware TM behavior requires KVM to synthesize state transitions, facility-unavailable exceptions, illegal-instruction exceptions, transaction failure state, checkpoint copying, and rollback-like effects in vcpu state.

## Important APIs, Types, And Functions

The exported function is `kvmhv_p9_tm_emulation()`. The local helper `emulate_tx_failure()` synthesizes TEXASR and TFIAR failure state. The function uses instruction opcode constants for `rfid`, `rfebb`, `mtmsrd`, `tsr`, `treclaim`, and `trechkpt`, plus helpers such as `sanitize_msr()`, `kvmppc_get_gpr()`, `kvmppc_core_queue_program()`, `kvmppc_book3s_queue_irqprio()`, `copy_from_checkpoint()`, and `copy_to_checkpoint()`.

## Control Flow

`kvmhv_p9_tm_emulation()` receives the faulting instruction in `vcpu->arch.emul_inst`. Because the softpatch interrupt advances NIP past the instruction, it first subtracts four to reconstruct normal synchronous-interrupt semantics. It masks instructions with `PO_XOP_OPCODE_MASK`, intentionally ignoring bit 31 for TM instructions whose invalid forms can also produce the softpatch.

For `rfid` and `mtmsrd`, it checks for suspended-to-transactional transitions, sanitizes the target MSR, updates guest MSR and NIP/CFAR as appropriate, and resumes the guest. For `rfebb`, it enforces PR/PCR and EBB facility availability, queues illegal or facility-unavailable interrupts when needed, updates BESCR[GE], transitions TM state from suspended to transactional, and branches to EBBRR.

For `tsr`, it checks privilege/architecture and TM facility availability, records previous transactional state in CR0, and performs suspend or resume depending on the L bit. For `treclaim`, it verifies TM availability and active transaction state, optionally synthesizes failure state from RA, copies checkpointed state back into active state, records prior state in CR0, clears MSR TS bits, and advances NIP. For `trechkpt`, it requires TM enabled, no active transaction, and TEXASR[FS] set, copies active state to checkpoint, records CR0 state, sets suspended state, and advances NIP. Unknown instructions queue a program illegal interrupt and emit a rate-limited warning.

## State And Persistence Behavior

The function updates `vcpu->arch.shregs.msr`, `vcpu->arch.regs.nip`, `vcpu->arch.cfar`, `vcpu->arch.regs.ccr`, `vcpu->arch.texasr`, `vcpu->arch.tfiar`, `vcpu->arch.tfhar` indirectly through checkpoint helpers, `vcpu->arch.fscr`, `vcpu->arch.hfscr`, and `vcpu->arch.trap`. It preserves TEXASR ROT/TL bits when synthesizing failure state. It returns either `RESUME_GUEST` for fully handled emulation or `-1` to rerun host interrupt handling for hypervisor facility unavailable cases.

## Dependencies And Integration Points

This file is called from the POWER9 entry/exit handling in `book3s_hv_p9_entry.c` and virtual-mode exit handling in `book3s_hv.c`. It complements the TM save/restore assembly in `book3s_hv_rmhandlers.S` and the early TM softpatch handling in `book3s_hv_tm_builtin.c`. It depends on Book3S interrupt queuing, MSR sanitization, TM checkpoint copy helpers, and HFSCR/FSCR facility cause encodings.

## Risks

TM state transitions are subtle. Incorrect NIP rewind/advance can re-execute or skip an instruction. Wrong MSR TS transitions can produce TM bad-thing behavior or fail to emulate hardware. Facility checks must distinguish hypervisor facility unavailable from guest facility unavailable. `treclaim` and `trechkpt` must copy checkpoint state in the correct direction and preserve CR0/TEXASR semantics. The bit-31 masking behavior is intentional and should not be simplified without hardware validation.

## Test Signals

Signals include POWER9 DD2.2 TM softpatch tests for `rfid`, `rfebb`, `mtmsrd`, `tsr`, `treclaim`, and `trechkpt`; PR and HV privilege combinations; HFSCR/FSCR TM and EBB disabled cases; active, suspended, and non-transactional MSR states; TEXASR[FS] set and clear; RA failure-cause generation; and unknown TM-related instruction warning paths.
