# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm_builtin.c

Purpose: this file handles a narrow POWER9 HV KVM transactional-memory path where the guest is in real suspend state and selected instructions can be emulated early without dooming the transaction. It also provides a rollback helper for returning to a guest in transactional state by restoring checkpointed architectural state.

Important APIs: `kvmhv_p9_tm_emulation_early()` decodes `vcpu->arch.emul_inst` and handles `rfid`, `rfebb`, `mtmsrd`, and `tsr.` forms that can transition from suspended to transactional state. `kvmhv_emulate_tm_rollback()` clears `MSR_TS`, sets NIP from `tfhar`, restores checkpointed GPR/FPR/TM state via `copy_from_checkpoint()`, and marks CR0 with the rollback result.

Control flow: the early emulator masks the opcode, validates that the requested transition is the expected suspend-to-transactional transition, updates shadow MSR/NIP/CFAR or BESCR state, and returns `1` only when it fully handled the instruction. Unsupported privilege/facility combinations return `0`, leaving the caller to continue normal handling. The `tsr.` case intentionally ignores bit 31 because POWER9 treats both forms as softpatchable TM-related invalid forms.

State and persistence: all state is per-vCPU architectural state: `shregs.msr`, `shregs.srr0/srr1`, `regs.nip`, `regs.ccr`, `cfar`, `tfhar`, and TM checkpointed registers. No heap allocation or persistent global state is introduced.

Dependencies and integration: this depends on Book3S KVM MSR helpers, `sanitize_msr()`, TM predicates, SPR accessors for BESCR/EBBRR/FSCR, HFSCR facility bits, and checkpoint copy helpers. It integrates with the HV softpatch/emulation path before the normal transaction would be aborted.

Risks: correctness is tightly coupled to ISA TM transition rules. Missing privilege checks are called out by comments for `rfid` and `mtmsrd`. Incorrect MSR sanitization or facility gating can either let a guest enter an invalid TM state or wrongly doom a transaction.

Test signals: exercise POWER9 transactional guests around `rfid`, `rfebb`, `mtmsrd`, `tsr.`, suspended transactions, disabled HFSCR facilities, PR-mode combinations, and rollback paths. Useful failures show up as bad guest NIP/MSR/CR0, unexpected transaction aborts, or softpatch exits that should have resumed the guest.
