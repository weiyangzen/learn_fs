# Research Report: subset-b-000785

This grouped report covers the requested PowerPC Book3S KVM files from `sources/distributed-fs/ceph-client/arch/powerpc/kvm/`. Each section is source-tree aligned and wrapped for reconciliation into the mapped per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm_builtin.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm_builtin.c

Purpose: this file handles a narrow POWER9 HV KVM transactional-memory path where the guest is in real suspend state and selected instructions can be emulated early without dooming the transaction. It also provides a rollback helper for returning to a guest in transactional state by restoring checkpointed architectural state.

Important APIs: `kvmhv_p9_tm_emulation_early()` decodes `vcpu->arch.emul_inst` and handles `rfid`, `rfebb`, `mtmsrd`, and `tsr.` forms that can transition from suspended to transactional state. `kvmhv_emulate_tm_rollback()` clears `MSR_TS`, sets NIP from `tfhar`, restores checkpointed GPR/FPR/TM state via `copy_from_checkpoint()`, and marks CR0 with the rollback result.

Control flow: the early emulator masks the opcode, validates that the requested transition is the expected suspend-to-transactional transition, updates shadow MSR/NIP/CFAR or BESCR state, and returns `1` only when it fully handled the instruction. Unsupported privilege/facility combinations return `0`, leaving the caller to continue normal handling. The `tsr.` case intentionally ignores bit 31 because POWER9 treats both forms as softpatchable TM-related invalid forms.

State and persistence: all state is per-vCPU architectural state: `shregs.msr`, `shregs.srr0/srr1`, `regs.nip`, `regs.ccr`, `cfar`, `tfhar`, and TM checkpointed registers. No heap allocation or persistent global state is introduced.

Dependencies and integration: this depends on Book3S KVM MSR helpers, `sanitize_msr()`, TM predicates, SPR accessors for BESCR/EBBRR/FSCR, HFSCR facility bits, and checkpoint copy helpers. It integrates with the HV softpatch/emulation path before the normal transaction would be aborted.

Risks: correctness is tightly coupled to ISA TM transition rules. Missing privilege checks are called out by comments for `rfid` and `mtmsrd`. Incorrect MSR sanitization or facility gating can either let a guest enter an invalid TM state or wrongly doom a transaction.

Test signals: exercise POWER9 transactional guests around `rfid`, `rfebb`, `mtmsrd`, `tsr.`, suspended transactions, disabled HFSCR facilities, PR-mode combinations, and rollback paths. Useful failures show up as bad guest NIP/MSR/CR0, unexpected transaction aborts, or softpatch exits that should have resumed the guest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_tm_builtin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_uvmem.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_uvmem.c

Purpose: this file implements secure-memory page tracking and migration for pseries secure guests on Ultravisor-enabled POWER platforms. It represents secure guest pages with private ZONE_DEVICE memory, migrates pages between normal HV memory and UV secure memory, and tracks VM/GFN state across `H_SVM_INIT_START`, page-in/page-out/share, abort, done, and termination-style transitions.

Important APIs and types: global device-private backing is represented by `kvmppc_uvmem_pgmap`, `kvmppc_uvmem_bitmap`, and `kvmppc_uvmem_bitmap_lock`. Per-memslot GFN state is held in `struct kvmppc_uvmem_slot` with a `pfns[]` flag array. Per-device-page metadata is `struct kvmppc_uvmem_page_pvt`, carrying `kvm`, `gpa`, `skip_page_out`, and `remove_gfn`. Public entry points include `kvmppc_uvmem_available()`, `kvmppc_h_svm_init_start()`, `kvmppc_h_svm_init_done()`, `kvmppc_h_svm_init_abort()`, `kvmppc_h_svm_page_in()`, `kvmppc_h_svm_page_out()`, `kvmppc_send_page_to_uv()`, memslot create/delete hooks, and module init/free helpers.

Control flow: init discovers secure memory from device tree, reserves a physical region, registers it with `memremap_pages()`, and allocates a bitmap. `H_SVM_INIT_START` validates radix and SVM enablement, registers all memslots with UV, disables KSM merging, and allocates GFN state arrays. `H_SVM_INIT_DONE` walks memslots, finds GFNs not yet marked secure/shared, and migrates them to device-private pages without UV page-in copying. Page-in allocates a free uvmem PFN, optionally calls `uv_page_in()`, and replaces the userspace PTE through `migrate_vma`. Page-out allocates a normal page, optionally calls `uv_page_out()`, migrates back to RAM, and releases the device PFN through `dev_pagemap_ops`. Sharing uses `uv_page_in()` while marking the GFN shared. Dropping pages forces faults/migrations to remove device mappings.

State and persistence: GFN state uses high-bit flags `KVMPPC_GFN_UVMEM_PFN`, `KVMPPC_GFN_MEM_PFN`, and `KVMPPC_GFN_SHARED`; secure PFNs store the device PFN in the low bits. VM state is carried in `kvm->arch.secure_guest`; per-guest coordination uses `kvm->arch.uvmem_lock`; memslot lifetime is tied to `kvm->arch.uvmem_pfns`.

Dependencies and integration: the file depends on Linux migration APIs, device-private memory, KVM memslots/SRCU, mmap locking, KSM, Open Firmware device-tree parsing, and Ultravisor calls such as `uv_register_mem_slot()`, `uv_page_in()`, `uv_page_out()`, and `uv_svm_terminate()`. It integrates with KVM memory-region hooks and page-fault migration through `dev_pagemap_ops.migrate_to_ram`.

Risks: the design assumes `PAGE_SHIFT` granularity and one `kvmppc_uvmem_slot` per KVM memslot. Lock ordering is explicit and fragile: SRCU, `mmap_lock`, then `uvmem_lock`. Error paths can leave a transient VM in an erroneous state until userspace terminates it. `kvmppc_h_svm_init_abort()` returns `H_PARAMETER` after terminating, which should be validated against callers. Bitmap allocation/release and `zone_device_data` ownership are critical for avoiding PFN leaks or stale GFN flags.

Test signals: secure guest boot on PEF/UV hosts, non-UV fallback, page-in/out at 64K only, sharing/unsharing virtio or VPA pages, memslot add/delete during secure mode, KSM merge toggling, migration fault paths, abort before done, and low secure-memory capacity. Watch for `SIGBUS` on HV faults, leaked device pages, inconsistent `secure_guest` bits, and UV return-code propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_uvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_interrupts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_interrupts.S

Purpose: this assembly file is the high-memory PR KVM vCPU run loop for Book3S. It saves host state, loads guest nonvolatile state, copies volatile state into the shadow vCPU, enters the low-level trampoline, then returns from guest exits into C exit handling.

Important entry points: `__kvmppc_vcpu_run` is the exported run routine called by PR KVM C code. Internal labels `kvm_start_entry`, `kvm_start_lightweight`, `kvm_exit_loop`, `kvm_loop_heavyweight`, and `kvm_loop_lightweight` structure first entry, re-entry with nonvolatile reload, and lightweight re-entry.

Control flow: the entry path builds a switch frame, saves host LR/CR/nonvolatile GPRs, stores the vCPU pointer, and loads guest r14-r31. The lightweight path calls `kvmppc_copy_to_svcpu()`, restores the vCPU pointer, sets 64-bit host flags such as dcbz32 restore and guest SPRG3, then branches to `kvmppc_entry_trampoline()`. After lowmem/segment code exits the guest, the high-memory path stores the trap number, calls `kvmppc_copy_from_svcpu()`, restores host SPRG3, saves guest nonvolatile GPRs, and calls `kvmppc_handle_exit_pr()`. Return codes decide whether to exit to host, resume lightweight, or reload nonvolatile state before re-entry.

State and persistence: state is split between the stack frame, `struct kvm_vcpu`, PACA/shadow vCPU fields, SPRG3, and nonvolatile guest GPR slots. The file does not allocate memory; it preserves ABI state across guest execution.

Dependencies and integration: it depends on generated asm offsets, PPC ABI mode, `book3s_segment.S` via the trampoline target, and C helpers `kvmppc_copy_to_svcpu()`, `kvmppc_copy_from_svcpu()`, and `kvmppc_handle_exit_pr()`. It is invoked from `kvmppc_vcpu_run_pr()` in `book3s_pr.c`.

Risks: this code is register- and ABI-sensitive. A wrong offset or missed save/restore can corrupt host state or guest state. Endianness conversion for shared SPRG3 must match the shared page mode. The lightweight/heavyweight distinction matters because `RESUME_GUEST_NV` requires nonvolatile guest GPRs to be reloaded.

Test signals: run PR guests through repeated exits, PAPR hcalls, SPRG3 shared-page updates, both endian modes, dcbz32 host flag cases, and paths returning `RESUME_GUEST` versus `RESUME_GUEST_NV`. Failures usually appear as corrupted nonvolatile registers, bad trap numbers, or host instability after guest exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_interrupts.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_mmu_hpte.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_mmu_hpte.c

Purpose: this file implements the PR Book3S shadow HPTE cache. It indexes translated guest mappings by effective address, virtual page, and physical range so KVM can invalidate shadow mappings efficiently when the guest or host memory state changes.

Important APIs: `kvmppc_mmu_hpte_cache_map()` inserts a `struct hpte_cache` into several RCU hlist hash tables. `kvmppc_mmu_pte_flush()`, `kvmppc_mmu_pte_vflush()`, and `kvmppc_mmu_pte_pflush()` invalidate by effective address mask, virtual page mask, or physical address range. `kvmppc_mmu_hpte_cache_next()` allocates cache entries and flushes everything when the per-vCPU cache reaches `HPTEG_CACHE_NUM`. `kvmppc_mmu_hpte_init()`, `destroy()`, `sysinit()`, and `sysexit()` initialize per-vCPU hash heads and the slab cache.

Control flow: mappings are hashed into short and long EA lists, short and long virtual-page lists, and on 64-bit builds a 64K VPTE list. Flush helpers compute the matching hash bucket, scan under RCU, and call `invalidate_pte()`. `invalidate_pte()` invokes the architecture MMU invalidation callback, removes every list node under `mmu_lock`, decrements `hpte_cache_count`, and releases the cache object through `kfree_rcu()`.

State and persistence: persistent state is per-vCPU in `struct kvmppc_vcpu_book3s`: hlist arrays, `mmu_lock`, and `hpte_cache_count`. Global state is the `hpte_cache` slab. The cached entries mirror active shadow mappings and are not guest-persistent state.

Dependencies and integration: it depends on Linux RCU lists, spinlocks, the Book3S MMU callback table, hash helpers, and tracepoints from `trace_pr.h`. It is used by PR fault handling, MMU notifier invalidation, dirty-log flushing, and HPT/TLB invalidation paths.

Risks: invalidation is RCU plus spinlock based; double invalidation is handled by checking `hlist_unhashed()`, but callback ordering must remain correct. Unsupported masks trigger `WARN_ON(1)`. Complete flush iterates the long VPTE hash and invalidates while traversing under RCU, so list deletion assumptions matter.

Test signals: guest TLB invalidation instructions, memslot unmap, dirty logging, physical range invalidation, 64K page guests, cache saturation, and concurrent vCPU faults should be exercised. Watch for stale translations, missing MMIO exits, RCU misuse warnings, and incorrect `hpte_cache_count`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_mmu_hpte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_paired_singles.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_paired_singles.c

Purpose: this file emulates paired-single and selected floating-point instructions for Book3S guests where paired-single behavior is required but not executed natively. It supports Gekko/Broadway-style paired-single load/store and arithmetic using FPR plus QPR state.

Important APIs: `kvmppc_emulate_paired_single()` is the exported emulator. Helpers include `kvmppc_inst_is_paired_single()` for opcode recognition, `kvmppc_emulate_fpr_load/store()` for ordinary FPR memory operations, `kvmppc_emulate_psq_load/store()` for paired-single quantized load/store forms, and `kvmppc_ps_one_in()`, `kvmppc_ps_two_in()`, `kvmppc_ps_three_in()` for applying scalar/simd floating helpers to PS0/PS1 halves.

Control flow: the emulator fetches `last_inst`, decodes register fields, verifies paired-single support and FP enablement, gives up host FP ownership, enables kernel FP, dispatches on primary opcode and extended fields, and returns an emulation result. Memory operations use `kvmppc_ld()`/`kvmppc_st()` and either inject data-storage faults or route MMIO through KVM load/store helpers. Arithmetic delegates to `fps_*` and `fpd_*` helpers while maintaining `vcpu->arch.qpr[]` as the second single component. Update forms write back RA after successful memory emulation.

State and persistence: state lives in guest FPRs, `vcpu->arch.qpr[]`, `vcpu->arch.fp.fpscr`, GPR RA writeback, CR for record forms, `paddr_accessed`, DAR/DSISR on injected faults, and queued Book3S interrupts. No global state is maintained.

Dependencies and integration: this file depends on KVM instruction fetch, Book3S interrupt queuing, KVM MMIO emulation, FP conversion helpers, and kernel FP enable/disable primitives. It is reached from PR exit handling when paired-single guests trap through FP unavailable/program paths.

Risks: implementation is incomplete for several comparison/FPSCR forms marked `XXX` or returning `EMULATE_FAIL`. Quantization type and scale fields are decoded but not fully applied, which matters for exact paired-single semantics. CR update code for comparisons appears suspect because it computes `tmp_cr` but folds from `cr` rather than `tmp_cr`. Kernel FP preemption boundaries must stay correct.

Test signals: run paired-single instruction suites for PSQ load/store update/indexed forms, arithmetic scalar variants, FPR load/store MMIO paths, disabled MSR[FP], page faults, and record forms. Compare against native hardware where possible, especially FPSCR/CR and quantized memory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_paired_singles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr.c

Purpose: this is the main implementation for Book3S PR KVM, where guests run without hypervisor mode, generally in problem state. It wires vCPU lifecycle, guest entry/exit, shadow MSR handling, MMU fault handling, facility/FPU ownership, PAPR/OSI/PV hcalls, one-reg state, memory invalidation, dirty logging, and module registration.

Important APIs: key entry points include `kvmppc_vcpu_run_pr()`, `kvmppc_handle_exit_pr()`, `kvmppc_copy_to_svcpu()`, `kvmppc_copy_from_svcpu()`, `kvmppc_set_msr_pr()`, `kvmppc_set_pvr_pr()`, `kvmppc_handle_pagefault()`, `kvmppc_giveup_ext()`, `kvmppc_giveup_fac()`, `kvmppc_set_fscr()`, vCPU create/free/load/put helpers, one-reg get/set handlers, VM init/destroy, and the `kvm_ops_pr` registration table.

Control flow: `kvmppc_vcpu_run_pr()` validates vCPU sanity, prepares interrupt entry, gives up host math state, optionally preloads FP, fixes EE state, and calls the assembly `__kvmppc_vcpu_run()`. Guest exits arrive at `kvmppc_handle_exit_pr()`, which decodes the Book3S interrupt number. Storage exits call `kvmppc_handle_pagefault()` to translate guest addresses, map shadow PTEs, inject guest faults, or route MMIO. Syscall exits dispatch in-kernel PAPR hcalls where possible or exit to userspace. Program/facility/math exits either emulate instructions, enable guest-owned facilities, or inject guest interrupts. Before re-entry it calls `kvmppc_prepare_to_enter()` and repairs lost external state.

State and persistence: per-vCPU state includes shadow vCPU content, shadow MSR, guest-owned FP/VMX/VSX bits, FSCR/TAR, SLB shadows, BAT/SR state, TM state, PVR-derived feature flags, split-real hack flags, timing counters, and shared page. Per-VM state includes `hpt_mutex`, enabled hcall bitmap, RTAS token list, and global relocation-on-exception user count for firmware set-mode platforms.

Dependencies and integration: it integrates with `book3s_interrupts.S` and `book3s_segment.S`, PR MMU implementations, `book3s_pr_papr.c`, RTAS, XICS, paired-single emulation, Linux FPU/Altivec/VSX context management, KVM MMU notifiers, and KVM core ops. Module init sets `kvmppc_pr_ops` and initializes the HPTE cache.

Risks: this file is the central correctness boundary for PR KVM. Risks include stale shadow translations, split-real address fixup mistakes, host math-state leakage, incorrect TM save/restore, facility masking errors, PVR feature misclassification, bad return-code choice between `RESUME_GUEST` and `RESUME_GUEST_NV`, and guest-visible behavior diverging from PAPR.

Test signals: boot 32-bit and 64-bit Book3S guests, PAPR guests, radix-host rejection, HPT mode on POWER9, dirty logging, MMIO, single-step debug, FPU/VMX/VSX/TAR/TM facilities, paired-single guests, split real mode, magic page transitions, and all major exit classes. Watch for bad registers after re-entry, missing guest interrupts, stale mappings, and host state corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr_papr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr_papr.c

Purpose: this file implements PAPR hypercall handling for PR KVM Book3S guests, especially HPT manipulation hcalls that operate on the guest/userspace hash page table.

Important APIs: `kvmppc_h_pr()` dispatches hcalls. `kvmppc_hcall_impl_pr()` reports implemented hcalls, and `kvmppc_pr_init_default_hcalls()` enables the historical default set. HPT helpers include `kvmppc_h_pr_enter()`, `remove()`, `bulk_remove()`, and `protect()`. Other handlers wrap logical CI load/store, `H_SET_MODE`, TCE calls when configured, XICS hcalls, `H_CEDE`, and `H_RTAS`.

Control flow: HPT hcalls compute the target PTEG address from SDR1, lock `kvm->arch.hpt_mutex`, copy HPTEs from userspace HPT memory, validate flags/AVPN/slot state, update or clear entries with `copy_to_user()`, and call the vCPU MMU `tlbie()` hook when mappings change. `kvmppc_h_pr()` first checks the enabled-hcall bitmap, then handles in-kernel operations or falls back to `EMULATE_FAIL` so userspace can process unsupported calls.

State and persistence: persistent state includes the userspace HPT contents, SDR1, enabled hcall bits, vCPU GPR return values, and guest-visible HPTE referenced/change bits returned by removal operations. The file does not own the HPT memory; it synchronizes access with `hpt_mutex`.

Dependencies and integration: it depends on user accessors, PAPR hcall constants, `compute_tlbie_rb()`, PR MMU callbacks, optional SPAPR TCE IOMMU helpers, XICS, and RTAS. It is invoked from syscall exit handling in `book3s_pr.c` for `sc 1` PAPR hypercalls.

Risks: user memory copies can fail and return `H_FUNCTION`. HPT locking must cover read-modify-write plus TLB invalidation. Bulk remove encodes per-request status in guest registers and must not mix incompatible flags. The default hcall enable list intentionally excludes `H_RTAS`; changing that affects userspace ABI.

Test signals: PAPR guests under PR KVM, H_ENTER exact and non-exact insertion, remove/protect/bulk-remove with AVPN and ANDCOND flags, user HPT fault injection, TCE enabled/disabled builds, XICS hcalls, RTAS token presence/absence, and `H_CEDE` halt/wakeup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_pr_papr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_rmhandlers.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_rmhandlers.S

Purpose: this assembly file provides real-mode low-physical-memory handlers and the entry bridge into the segment trampoline for Book3S PR KVM. On 32-bit builds it also defines interrupt trampolines that distinguish KVM guest faults from normal Linux faults.

Important entry points: `kvmppc_trampoline_<intno>` labels are generated by `INTERRUPT_TRAMPOLINE` for several Book3S interrupt vectors on 32-bit. `kvmppc_handler_skip_ins` skips a faulting guest instruction when guest mode requests it. `_GLOBAL_TOC(kvmppc_entry_trampoline)` clears relocation bits and enters `kvmppc_handler_trampoline_enter` in real mode. The file includes `book3s_segment.S`, which contains most entry/exit segment switching.

Control flow: a 32-bit interrupt trampoline saves scratch registers, locates the thread shadow vCPU, checks `HSTATE_IN_GUEST`, and either branches back to the normal Linux handler or records the interrupt number and exits through the KVM trampoline. Skip mode advances SRR0 by 4, restores scratch state, and returns. The common entry trampoline loads the real address of `kvmppc_handler_trampoline_enter`, clears IR/DR in SRR1, preserves a host MSR with EE set for later C handling, and uses RFI to enter real mode trampoline code.

State and persistence: state is held in SPRG scratch registers, `HSTATE_SCRATCH*`, `HSTATE_IN_GUEST`, SRR0/SRR1, and the shadow vCPU/PACA. No persistent allocation exists.

Dependencies and integration: it depends on asm offsets, Book3S interrupt constants, real/physical address macros, and `book3s_segment.S`. It is called from `book3s_interrupts.S` after the high-memory run loop has copied vCPU state to the shadow vCPU.

Risks: this code executes with relocation disabled and minimal state, so register clobbering or wrong physical address conversion can break host exception handling. Skip mode assumes prefixed instructions are disabled for PR KVM and advances by exactly 4 bytes.

Test signals: 32-bit Book3S PR guest interrupt exits, skip-instruction paths on failed last-instruction fetch, normal host interrupt handling while no guest is active, and guest entry with IR/DR transitions. Failures show up as lost host interrupts, wrong exit numbers, or guest PC corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_rmhandlers.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_rtas.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_rtas.c

Purpose: this file implements in-kernel RTAS token definition and selected RTAS calls for Book3S KVM guests, currently focused on interrupt-controller operations such as XIVE/XICS set/get and interrupt masking.

Important APIs and types: `struct rtas_handler` maps RTAS names to handlers. `struct rtas_token_definition` stores per-VM token-to-handler bindings. `kvm_vm_ioctl_rtas_define_token()` lets userspace define or undefine supported RTAS tokens. `kvmppc_rtas_hcall()` executes a guest RTAS call. `kvmppc_rtas_tokens_free()` releases per-VM token definitions. Handler functions include `kvm_rtas_set_xive()`, `get_xive()`, `int_off()`, and `int_on()`.

Control flow: userspace defines a token by name; the code rejects duplicate token numbers and unsupported names under `rtas_token_lock`. At runtime, `kvmppc_rtas_hcall()` reads the guest `rtas_args` from guest physical memory in r4, validates argument array bounds, redirects `args.rets` into the copied args array, finds a matching token, calls its handler, restores the original return pointer, and writes the modified args back to guest memory.

State and persistence: token definitions persist on `kvm->arch.rtas_tokens` until undefinition or VM teardown. Handler results are written into guest RTAS return slots using big-endian RTAS format. No global mutable state is used.

Dependencies and integration: the interrupt RTAS handlers dispatch to XIVE if `xics_on_xive()` is true, otherwise XICS. The hcall path is invoked from PR PAPR handling when `H_RTAS` is requested and tokens exist. It uses KVM guest memory access under vCPU SRCU.

Risks: malformed guest RTAS pointers or excessive nargs fail out to userspace rather than returning an RTAS error because the return area cannot be trusted. Name matching uses fixed-size token argument names. Token definitions are only for known in-kernel handlers; userspace remains responsible for other RTAS services.

Test signals: define/undefine tokens, duplicate tokens, unsupported names, malformed guest args GPA, bad nargs/nret counts, set/get XIVE and int on/off on XICS and XIVE-backed systems, and VM teardown with live token lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_rtas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_segment.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_segment.S

Purpose: this assembly include contains the real-mode guest entry and exit trampoline that switches between host and guest segment/MMU state for PR Book3S. It is included by `book3s_rmhandlers.S`.

Important entry points: `kvmppc_handler_trampoline_enter` enters the guest. `kvmppc_interrupt_pr` normalizes 64-bit interrupt entry state. `kvmppc_handler_trampoline_exit` saves guest state and returns to the high-memory C/assembly handler. Subarchitecture-specific segment operations come from `book3s_64_slb.S` or `book3s_32_sr.S` through `LOAD_GUEST_SEGMENTS` and `LOAD_HOST_SEGMENTS`.

Control flow: entry obtains the shadow vCPU, saves host handler/MSR/R1/R2, marks guest mode active, loads guest segment state, adjusts FSCR and optional HID5 dcbz32 state, restores guest CTR/LR/CR/XER and volatile GPRs, sets SRR0/SRR1 from guest PC/shadow MSR, and RFI's to the guest. Exit saves volatile registers, restores host R1/R2, captures SRR/HSRR PC and MSR, restores scratch GPRs/CR, saves XER/DAR/DSISR/CTR/LR, optionally fetches the last guest instruction by temporarily enabling data relocation, clears guest mode, restores host segments, restores FSCR/HID5, and RFI's or vectors through host interrupt handlers before reaching the high-memory handler.

State and persistence: transient state is stored in `SVCPU_*` and `HSTATE_*` fields, PACA, SRR/HSRR, FSCR, HID5, guest mode byte, and last-instruction slot. It preserves guest volatile state for `kvmppc_copy_from_svcpu()`.

Dependencies and integration: depends on asm offsets, CPU feature fixups, exception constants, TM MSR handling, and the entry contract from `book3s_interrupts.S`/`book3s_rmhandlers.S`. Its saved trap number becomes the `exit_nr` handled by `kvmppc_handle_exit_pr()`.

Risks: wrong guest-mode marking can route host faults into KVM or guest faults into Linux. Last-instruction fetch intentionally uses skip mode to tolerate faults; prefixed instructions are noted as disabled. TM bits must be preserved carefully on return to host to avoid invalid TS transitions.

Test signals: instruction/data/program/syscall/alignment/facility exits, last-instruction fetch success and failure, 32-bit SR and 64-bit SLB guests, dcbz32 toggling, FSCR save/restore, host external/decrementer/perf/doorbell interrupts during guest exit, and transactional-memory guest states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_segment.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.c

Purpose: this file implements the emulated XICS interrupt controller for Book3S KVM. It models interrupt source controllers (ICS), interrupt presentation controllers (ICP), PAPR XICS hcalls, KVM device attributes, debugfs state, and passthrough IRQ mapping metadata.

Important APIs: source control functions include `kvmppc_xics_set_xive()`, `get_xive()`, `int_on()`, `int_off()`, and `kvmppc_xics_set_irq()`. ICP/hcall handlers include `kvmppc_xics_hcall()`, `kvmppc_xics_rm_complete()`, `kvmppc_h_xirr()`, `h_ipi()`, `h_cppr()`, `h_eoi()`, and `h_ipoll()`. Device/lifecycle functions include `kvm_xics_ops`, `kvmppc_xics_connect_vcpu()`, `kvmppc_xics_free_icp()`, `kvmppc_xics_get_icp()`, `kvmppc_xics_set_icp()`, and mapped IRQ setters.

Control flow: `ics_deliver_irq()` updates per-source P/Q state, handles MSI versus LSI behavior, and calls `icp_deliver_irq()` when an interrupt should be presented. `icp_deliver_irq()` locks the source, resolves the target server, handles masked-pending and resend state, and attempts an atomic ICP delivery. ICP state transitions use `icp_try_update()` with a 64-bit compare/exchange on `union kvmppc_icp_state`; successful output queues `BOOK3S_INTERRUPT_EXTERNAL` and may kick the target vCPU. Hcalls manipulate XIRR, CPPR, MFRR, EOI, and resend checks according to PAPR-like state transitions. Device attrs serialize/restore source state for migration.

State and persistence: `struct kvmppc_xics` owns an array of up to 1024 ICS pointers and per-device flags. Each `struct kvmppc_ics` has a spinlock and 1024 `ics_irq_state` entries. Each vCPU can own one `struct kvmppc_icp` with atomic CPPR/MFRR/pending/XISR state and resend bitmap. Source state contains priority, saved priority, server, P/Q bits, resend, masked pending, LSI/MSI mode, host IRQ, and interrupt CPU.

Dependencies and integration: integrates with Book3S interrupt queuing, KVM device framework, KVM IRQ routing, migration attrs, RTAS/PAPR hcalls, optional real-mode HV completion, debugfs, and passthrough IRQ acknowledgement via `kvm_notify_acked_irq()`.

Risks: the code intentionally mixes spinlocked ICS state with lockless atomic ICP updates; memory barriers around resend maps are critical. Server lookup is linear across vCPUs. Restoring ICP/ICS state from userspace must be internally consistent or interrupts can be lost/replayed. Real-mode completion uses deferred action bits and must be cleared exactly once.

Test signals: MSI and LSI injection, mask/unmask with pending interrupts, XIRR/CPPR/EOI/IPI/IPOLL hcalls, migration get/set of ICP and source attrs, passthrough IRQ acknowledgement, vCPU connect/free, real-mode too-hard completion, and debugfs inspection. Watch for stuck external interrupts, lost resends, invalid priority ordering, and migration state rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.h

Purpose: this header defines the private XICS data model shared by Book3S KVM XICS implementation and real-mode helpers. It gives the interrupt source hierarchy, atomic ICP state layout, per-vCPU presenter object, per-ICS source table, and top-level XICS device structure.

Important APIs and types: `struct ics_irq_state` represents one interrupt source. `union kvmppc_icp_state` packs output, resend, CPPR, MFRR, pending priority, and XISR into one machine word for atomic compare/exchange. `struct kvmppc_icp` is the per-vCPU interrupt presenter, including resend bitmap and real-mode deferred-action fields. `struct kvmppc_ics` is one source block with 1024 IRQ states. `struct kvmppc_xics` is the VM-level device. Inline helpers `kvmppc_xics_find_server()` and `kvmppc_xics_find_ics()` resolve vCPU presenters and source blocks.

Control flow contribution: the header itself has no runtime loop, but its layout enables `book3s_xics.c` to perform atomic ICP updates and locked ICS source updates. IRQ numbers are split by `KVMPPC_XICS_ICS_SHIFT`; the high bits choose the ICS and the low bits choose the source index.

State and persistence: constants define the source space, reserved IRQ floor, `MASKED` priority, P/Q bits, and resend-map size. Real-mode action bits (`XICS_RM_KICK_VCPU`, `XICS_RM_CHECK_RESEND`, `XICS_RM_NOTIFY_EOI`) persist until virtual-mode completion.

Dependencies and integration: declarations for `xics_rm_h_xirr()`, `xics_rm_h_xirr_x()`, `xics_rm_h_ipi()`, `xics_rm_h_cppr()`, and `xics_rm_h_eoi()` connect C XICS code with optional real-mode assembly/C implementations. The header is compiled only under `CONFIG_KVM_XICS`.

Risks: bitfield packing in `union kvmppc_icp_state` is assumed to fit in `unsigned long` and to be safe for `cmpxchg64()` usage in the C file. Changing constants affects migration ABI and device-attribute validation. `kvmppc_xics_find_server()` is simple but O(vCPU count).

Test signals: compile both XICS-enabled and disabled configs, migration state get/set, high IRQ numbers near `KVMPPC_XICS_MAX_ICS_ID`, reserved IRQ rejection below `KVMPPC_XICS_FIRST_IRQ`, real-mode completion paths, and atomic ICP state packing on supported PPC word sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_xics.h -->
