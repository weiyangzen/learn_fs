# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_segment.S

Purpose: this assembly include contains the real-mode guest entry and exit trampoline that switches between host and guest segment/MMU state for PR Book3S. It is included by `book3s_rmhandlers.S`.

Important entry points: `kvmppc_handler_trampoline_enter` enters the guest. `kvmppc_interrupt_pr` normalizes 64-bit interrupt entry state. `kvmppc_handler_trampoline_exit` saves guest state and returns to the high-memory C/assembly handler. Subarchitecture-specific segment operations come from `book3s_64_slb.S` or `book3s_32_sr.S` through `LOAD_GUEST_SEGMENTS` and `LOAD_HOST_SEGMENTS`.

Control flow: entry obtains the shadow vCPU, saves host handler/MSR/R1/R2, marks guest mode active, loads guest segment state, adjusts FSCR and optional HID5 dcbz32 state, restores guest CTR/LR/CR/XER and volatile GPRs, sets SRR0/SRR1 from guest PC/shadow MSR, and RFI's to the guest. Exit saves volatile registers, restores host R1/R2, captures SRR/HSRR PC and MSR, restores scratch GPRs/CR, saves XER/DAR/DSISR/CTR/LR, optionally fetches the last guest instruction by temporarily enabling data relocation, clears guest mode, restores host segments, restores FSCR/HID5, and RFI's or vectors through host interrupt handlers before reaching the high-memory handler.

State and persistence: transient state is stored in `SVCPU_*` and `HSTATE_*` fields, PACA, SRR/HSRR, FSCR, HID5, guest mode byte, and last-instruction slot. It preserves guest volatile state for `kvmppc_copy_from_svcpu()`.

Dependencies and integration: depends on asm offsets, CPU feature fixups, exception constants, TM MSR handling, and the entry contract from `book3s_interrupts.S`/`book3s_rmhandlers.S`. Its saved trap number becomes the `exit_nr` handled by `kvmppc_handle_exit_pr()`.

Risks: wrong guest-mode marking can route host faults into KVM or guest faults into Linux. Last-instruction fetch intentionally uses skip mode to tolerate faults; prefixed instructions are noted as disabled. TM bits must be preserved carefully on return to host to avoid invalid TS transitions.

Test signals: instruction/data/program/syscall/alignment/facility exits, last-instruction fetch success and failure, 32-bit SR and 64-bit SLB guests, dcbz32 toggling, FSCR save/restore, host external/decrementer/perf/doorbell interrupts during guest exit, and transactional-memory guest states.
