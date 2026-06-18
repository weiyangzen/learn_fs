## sources/distributed-fs/ceph-client/arch/mips/kvm/entry.c

Purpose: Dynamically generates the low-level MIPS guest entry, exception, TLB-refill, exit, re-entry, and host-return code used by the KVM MIPS backend.

Important APIs, types, and functions: Public builders include `kvm_mips_entry_setup()`, `kvm_mips_build_vcpu_run()`, `kvm_mips_build_tlb_refill_exception()`, `kvm_mips_build_exception()`, and `kvm_mips_build_exit()`. Internal builders are `kvm_mips_build_enter_guest()`, `kvm_mips_build_ret_from_exit()`, `kvm_mips_build_ret_to_guest()`, `kvm_mips_build_ret_to_host()`, plus scratch/EBase helpers.

Control flow: Setup picks CP0 scratch registers, preferring KScratch registers not already used by the PGD register. The generated run function saves host callee-saved state/status/scratch registers, stores host stack and GP in the VCPU arch, switches status and EBase for guest exception vectors, then enters guest mode. Entry loads guest EPC, saves host PGD, installs the KVM GPA PGD, sets GuestCtl0.GM, configures GuestID or root ASID, disables RDHWR, restores guest GPRs and HI/LO, and executes `eret`. Generated exception vectors save guest K0/K1 and branch to the common exit handler. Exit saves guest GPRs, PC, BadVAddr, Cause, optional BadInstr/BadInstrP, restores host EBase/status/PGD/ASID/RDHWR/stack/GP, calls `kvm_mips_handle_exit()`, then either re-enters guest or unwinds to host.

State and persistence: The generated code reads/writes `struct kvm_vcpu_arch` fields for host stack/GP/PGD/EntryHi, guest EBase, guest GPRs, PC, HI/LO, FPU/MSA status registers, and saved exception CP0 fields. The emitted code resides in per-VCPU memory allocated by `mips.c` and flushed into the instruction cache.

Dependencies and integration points: Uses `uasm` emission helpers, MIPS CP0 definitions, Linux TLB refill builder helpers, `tlbmiss_handler_setup_pgd()`, VZ GuestCtl registers, KScratch/PGD conventions, FPU/MSA CSR save handling, and the C exit dispatcher `kvm_mips_handle_exit()`.

Risks: Emitted code relies on exact `struct kvm_vcpu_arch` offsets and architecture hazard ordering. Scratch register selection must avoid collision with host PGD usage. GuestID/root ASID and HTW/PGD transitions are highly ordering-sensitive. The code has comments noting assumptions about stack size and branch labels. FPU/MSA CSR clearing is intentionally tied to die-notifier recovery, so instruction offset changes in assembly helpers can break exception stepping.

Test signals: Boot/run VCPU on CPUs with/without KScratch, GuestID, HTW, VEIC/VINT, 64-bit KX, Loongson64 TLB refill, FPU, and MSA. Validate generated code dumping, guest exits for TLB/refill/general exceptions, host return codes, ASID/GuestID isolation, and FPU/MSA exception recovery.
