# Research Report: subset-b-000783

This grouped report covers the PowerPC Book3S KVM files assigned to `subset-b-000783`. Each file section is bounded by the required reconciliation markers and is intended to be split into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_emulate.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_emulate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_exports.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_exports.c

## Purpose

`book3s_exports.c` is a small symbol-export file for Book3S KVM entry trampolines. It makes the low-level guest-entry trampoline symbols visible to loadable KVM variants when the corresponding PR or HV Book3S implementation can be built as a module or used across compilation units.

## Important APIs, Types, And Functions

The file exports `kvmppc_hv_entry_trampoline` when `CONFIG_KVM_BOOK3S_HV_POSSIBLE` is enabled and exports `kvmppc_entry_trampoline` when `CONFIG_KVM_BOOK3S_PR_POSSIBLE` is enabled. Both are exported with `EXPORT_SYMBOL_GPL`, so consumers must be GPL-compatible modules.

## Control Flow

There is no runtime control flow beyond module symbol registration. The preprocessor selects which exports exist based on the configured Book3S KVM modes.

## State And Persistence Behavior

The file has no mutable runtime state and no persistent storage behavior. Its only effect is on the kernel module symbol table.

## Dependencies And Integration Points

It includes the KVM PowerPC and Book3S headers that declare the trampoline symbols. It integrates with architecture assembly entry code and the Linux module loader. HV and PR code that branches through these trampolines relies on these exports when linked modularly.

## Risks

The main risk is configuration or declaration drift: exporting a trampoline only when the corresponding implementation is possible must match the build system and symbol definitions. Removing or renaming these exports can break module loading even though the file has no direct runtime behavior.

## Test Signals

Build signals are the key checks: Book3S PR-only, HV-only, and combined configurations should link without unresolved trampoline symbols. Runtime module-load tests should confirm the KVM module loads and guest entry reaches the assembly trampoline rather than failing during relocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv.c

## Purpose

`book3s_hv.c` is the main KVM-HV implementation for 64-bit PowerPC Book3S processors, especially POWER7 and later. It owns HV-mode VM/vCPU lifecycle, virtual core scheduling, PAPR hypercall dispatch, guest entry and exit handling, MMU mode setup, LPID/partition-table management, VPA/DTL bookkeeping, nested virtualization hooks, interrupt and timer handling, dirty logging, passthrough interrupt mapping, secure guest transitions, module initialization, and the `kvmppc_ops` backend registered for Book3S HV KVM.

## Important APIs, Types, And Functions

Module parameters include `dynamic_mt_modes`, `target_smt_mode`, `one_vm_per_core`, `nested`, and XICS-specific `kvm_irq_bypass` and `h_ipi_redirect`. `default_enabled_hcalls` is initialized from `default_hcall_list[]` and copied into each VM.

Scheduling and wakeup helpers include `next_runnable_thread()`, `for_each_runnable_thread`, `kvmppc_ipi_thread()`, `kvmppc_fast_vcpu_kick_hv()`, stolen-time helpers, `kvmppc_run_vcpu()` for pre-POWER9 virtual-core execution, and `kvmhv_run_single_vcpu()` for POWER9-and-later one-vCPU-per-vcore execution. `kvmppc_run_core()` is the core POWER7/POWER8 runner that grabs sibling hardware threads, optionally enters split-core mode, starts guest threads through `__kvmppc_vcore_entry`, waits for secondary threads, unsplits, and post-processes exits.

VPA and dispatch state is handled by `do_h_register_vpa()`, `set_vpa()`, `kvmppc_update_vpa()`, `kvmppc_update_vpas()`, `__kvmppc_create_dtl_entry()`, `kvmppc_update_vpa_dispatch()`, `kvmppc_update_vpa_dispatch_p9()`, and `vcpu_vpa_increment_dispatch()`. These functions pin guest pages, update lppaca fields, maintain dispatch trace log entries, track dirty pinned pages, and support nestedv2 VPA synchronization.

Hypercall handling is centered on `kvmppc_pseries_do_hcall()`, `kvmppc_hcall_impl_hv()`, `kvmppc_h_set_mode()`, `kvmppc_h_page_init()`, `kvmppc_h_rpt_invalidate()`, and `kvmppc_nested_h_rpt_invalidate()`. Implemented in-kernel services include HPT operations, VPA registration, cede/prod/confer, RTAS, cache-inhibited logical loads/stores, XICS/XIVE-compatible calls, TCE calls when configured, random numbers, radix invalidation, nested virtualization calls, page initialization, and secure-VM page calls.

Exit handling is split between `kvmppc_handle_exit_hv()` for ordinary guests and `kvmppc_handle_nested_exit()` for L2/nested exits. They classify hypervisor decrementer, external, doorbell, HMI, PMI, system reset, machine check, program, syscall, storage fault, emulation assist, facility unavailable, softpatch, and passthrough exits into guest resume, userspace exit, page-fault handling, or real-mode completion.

Register ABI support is provided by `kvm_arch_vcpu_ioctl_get_sregs_hv()`, `kvm_arch_vcpu_ioctl_set_sregs_hv()`, `kvmppc_get_one_reg_hv()`, and `kvmppc_set_one_reg_hv()`. These cover PVR, SLB, LPCR, DABR/DAWR, PMU, DSCR, AMR/UAMOR/IAMR, PURR/SPURR, DPDES, VTB, CIABR, PID, PSSCR, VPA addresses, timebase offset, DEC expiry, online state, PTCR, FSCR, transactional-memory state, and newer POWER10/POWER11-related registers through helper accessors.

MMU and VM setup functions include `kvmhv_setup_mmu()`, `kvmppc_hv_setup_htab_rma()`, `kvmppc_switch_mmu_to_hpt()`, `kvmppc_switch_mmu_to_radix()`, `kvmppc_update_lpcr()`, `kvmppc_setup_partition_table()`, `kvmhv_configure_mmu()`, `kvmppc_core_init_vm_hv()`, and `kvmppc_core_destroy_vm_hv()`. The `kvm_ops_hv` table wires this implementation into generic KVM.

## Control Flow

VM creation initializes locks, allocates or receives an LPID/guest ID, allocates real-mode host operations when needed, initializes nested state, copies default hcall enablement, configures LPCR defaults, selects radix when the host uses radix, computes TLB set counts, tracks HV VM activation on pre-POWER9, and initializes strict or emulated SMT mode. vCPU creation initializes shared register state, nestedv2 I/O buffers when applicable, PMU defaults, MSR/HFSCR defaults, MMU state, wait queues, vcore assignment, per-vCPU locks, and thread placement metadata.

`kvmppc_vcpu_run_hv()` is the top-level run callback. It validates vCPU sanity, signal state, and host transactional-memory constraints; forces old userspace vCPUs online; prepares pending exceptions; records that a vCPU is running; enables host facilities needed to save guest state; saves user registers and SPRs; then loops through either the POWER9 single-vCPU runner or the pre-POWER9 vcore runner. Loop exits for in-kernel hcalls, page faults, and passthrough completions are handled immediately and can re-enter the guest until a non-resume result is produced.

On POWER7/POWER8, `kvmppc_run_vcpu()` puts the vCPU into its vcore's runnable set, updates VPA mappings, coordinates with other vCPU tasks, handles ceded virtual cores with polling/sleep, and lets a runner call `kvmppc_run_core()`. `kvmppc_run_core()` validates primary-thread ownership, collects piggyback vcores if dynamic micro-threading allows, hard-disables interrupts, optionally switches POWER8 split-core mode, populates PACA `kvm_hstate`, enters guest assembly via `__kvmppc_vcore_entry`, restores host core state, releases sibling threads, then calls `post_guest_process()` to classify each runnable vCPU's trap.

On POWER9 and later, `kvmhv_run_single_vcpu()` prepares radix migration flushes, sets PACA state for the current CPU, injects or advertises external interrupts through LPCR, updates dispatch accounting, enters `kvmhv_p9_guest_entry()`, and handles cede blocking directly on the vCPU wait object. `kvmhv_p9_guest_entry()` chooses between pseries nestedv1, pseries nestedv2, nested bare-metal, or normal bare-metal entry. It handles time limits, XIVE push/pull, in-entry `H_CEDE`, `H_ENTER_NESTED`, and XICS hcalls that must be processed before interrupt context is pulled.

MMU setup is lazy. The first run path calls `kvmhv_setup_mmu()` when `mmu_ready` is false. HPT guests allocate/reset an HPT, inspect guest memory at GPA 0 to choose a VRMA page size, create VRMA HPTEs, and update LPCR. Radix guests allocate partition-scoped page tables and install partition table entries. MMU reconfiguration clears `mmu_ready`, waits for no running vCPUs, switches HPT/radix state, updates the partition table and LPCR, then re-enables execution.

## State And Persistence Behavior

The file maintains only kernel runtime state, but much of it is guest-visible and long-lived for the VM lifetime. VM state includes LPID, LPCR, radix/HPT configuration, HPT or radix page tables, process table, enabled hcall bitmap, `need_tlb_flush` masks, vcore array, passthrough IRQ map, secure guest flags, uvmem lists, and nested state. vCPU state includes VPA/DTL/SLB shadow pins, dispatch counters, stolen time, ceded/prodded flags, doorbell requests, decrementer timers, PMU and debug SPRs, HFSCR, LPCR dirty state for nestedv2, TM state, and online count.

Pinned VPA/DTL pages are marked dirty when KVM writes to them and are harvested into dirty logs. Dirty logging also merges HPT/radix dirty bits with host-side memslot dirty bitmaps. Secure guest shutdown explicitly drops ultravisor memory, unregisters secure memslots, terminates UV state, unpins VPA pages, and resets partition tables.

## Dependencies And Integration Points

This file integrates with generic KVM through `struct kvmppc_ops`, KVM run ioctls, one-reg/sregs ABI, memslot hooks, irqfd/irq-bypass, SRCU, wait queues, hrtimers, debugfs, and dirty logging. Architecture dependencies include PACA `kvm_hstate`, Book3S exception numbers, LPCR/LPID/HFSCR/MMU registers, XICS/XIVE interrupt controllers, OPAL, radix and HPT MMU helpers, pseries nested hcalls, ultravisor secure-VM services, hardware breakpoints, transactional memory helpers, PMU save/restore, and assembly guest-entry functions.

## Risks

This file is concurrency and hardware-ordering sensitive. PACA state, `cpu`/`thread_cpu`, pending exceptions, doorbells, and wait queues rely on explicit barriers. Pre-POWER9 split-core execution depends on grabbing secondary hardware threads and restoring HID0 split mode correctly; failure can hang sibling threads or leave the host in the wrong threading mode. MMU mode changes must synchronize `mmu_ready` with `vcpus_running` or a vCPU can enter with torn HPT/radix state. VPA pin/unpin paths must not hold locks across GUP and must dirty pages correctly. Nested virtualization and secure guest paths have multiple host/L0/L1/L2 ownership transitions. Interrupt paths differ for XICS, XIVE, OPAL, pseries, bare metal, and passthrough, so regressions can appear only on specific platform combinations.

## Test Signals

Important signals include booting POWER8 HPT guests with multiple vCPUs per vcore, POWER9/POWER10 radix guests with one vCPU per vcore, HPT allocation and resize ioctls, MMU v3 radix/HPT configuration, PAPR hcall coverage, VPA/DTL registration and dirty logging, guest cede/prod/confer behavior, decrementer delivery, XICS and XIVE interrupt injection, passthrough IRQ bypass, nested HV L2 entry/exit, secure guest enable/off flows, live migration register get/set coverage, debugfs timing output when configured, and module init/exit on valid and invalid host feature combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv.h

## Purpose

`book3s_hv.h` is the private header for Book3S HV KVM C and assembly support. It defines host SPR save state for POWER9-style entry paths, declares guest-state load/store and PMU switching helpers, provides timing macros, and generates nestedv2-aware vCPU register accessors that keep local cached state synchronized with the guest-state-buffer dirty/reload mechanism.

## Important APIs, Types, And Functions

`struct p9_host_os_sprs` holds host privileged non-hypervisor SPRs that must be saved across guest entry: IAMR, AMR, PMCs, MMCRs, MMCRA, SIAR, SIERs, and SDAR. `nesting_enabled()` returns true only when the VM requested nested virtualization and is using radix MMU.

The header declares `load_vcpu_state()`, `store_vcpu_state()`, `save_p9_host_os_sprs()`, `restore_p9_host_os_sprs()`, `switch_pmu_to_guest()`, and `switch_pmu_to_host()`, which are implemented elsewhere and used by the POWER9/nested entry paths.

When `CONFIG_KVM_BOOK3S_HV_P9_TIMING` is enabled, `accumulate_time()`, `start_timing()`, and `end_timing()` update timebase accumulators. Otherwise the macros compile to no-ops.

`__kvmppc_set_msr_hv()` and `__kvmppc_get_msr_hv()` directly access the shadow MSR and integrate with nestedv2 dirty/reload tracking. The `KVMPPC_BOOK3S_HV_VCPU_ACCESSOR*` macros generate typed get/set helpers for scalar and array vCPU fields, including MMCRA, HFSCR, FSCR, DSCR, PURR, SPURR, AMR, UAMOR, SIAR, SDAR, IAMR, DAWR/DAWRX, DEXCR, hash key registers, CIABR, WORT, PPR, CTRL, MMCR arrays, SIER arrays, PMC arrays, and PSPB.

## Control Flow

Callers use the generated setters when guest state changes locally; each setter stores the new value and marks the corresponding nestedv2 guest-state ID dirty. Generated getters request a cached reload for the guest-state ID before returning the local field; several use `WARN_ON()` if reload fails. This creates a uniform path for normal HV state access and nestedv2 state synchronization.

## State And Persistence Behavior

The header does not define persistent storage. It defines access patterns for runtime vCPU architectural state and host SPR save areas. Its main state effect is ensuring that state modified in the in-kernel cache is marked dirty for nestedv2 and that reads reload from nestedv2 buffers when needed.

## Dependencies And Integration Points

The file depends on `asm/guest-state-buffer.h` for `KVMPPC_GSID_*` identifiers and nestedv2 dirty/reload helpers. It is included by `book3s_hv.c`, `book3s_hv_builtin.c`, and related HV support code that needs consistent access to guest SPRs and timing helpers.

## Risks

Accessor macro mistakes can silently desynchronize nestedv2 guest state. A wrong GSID mapping, missing dirty mark, or missing reload can make L0/L1 see stale or incorrect registers. The accessors are inline and widely used, so changes have a broad blast radius. Host SPR save structure layout must stay consistent with assembly/C save and restore routines.

## Test Signals

Signals include nestedv2 guests preserving MSR, LPCR, PMU, debug, and facility state across entries; one-reg get/set behavior matching guest execution; no `WARN_ON()` reload failures; PMU counters switching cleanly between host and guest; and timing debugfs output compiling both with and without P9 timing enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_builtin.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_builtin.c

## Purpose

`book3s_hv_builtin.c` contains Book3S HV support that must be built into the kernel or callable from real-mode/low-level contexts. It handles CMA reservation for hash page tables, real-mode hypercall helpers, HV VM activity tracking, real-mode IPI and exit coordination, XICS passthrough interrupt triage, interrupt injection support, guest MSR sanitization, and per-CPU TLB flush checks.

## Important APIs, Types, And Functions

`early_parse_kvm_cma_resv()` parses the `kvm_cma_resv_ratio=` boot parameter. `kvm_cma_reserve()` reserves a contiguous CMA area for KVM HPT allocation when the host is in HV mode. `kvm_alloc_hpt_cma()` and `kvm_free_hpt_cma()` allocate and release HPT pages from that CMA area and are GPL-exported.

`kvmppc_rm_h_confer()` implements the real-mode part of `H_CONFER` by watching vcore running, ceded, and conferring bitmaps for a short timebase window and returning `H_TOO_HARD` when the virtual-mode scheduler should yield.

`hv_vm_count`, `kvm_hv_vm_activated()`, `kvm_hv_vm_deactivated()`, and `kvm_hv_mode_active()` track whether HV VMs exist, using CPU hotplug read locking around count changes. `kvmppc_hcall_impl_hv_realmode()` checks the real-mode hcall table. `kvmppc_hwrng_present()` and `kvmppc_rm_h_random()` expose platform random seed support to real-mode hcalls.

`kvmhv_rm_send_ipi()`, `kvmhv_interrupt_vcore()`, and `kvmhv_commence_exit()` send doorbells/IPIs and coordinate all threads in a vcore or split-core group to leave the guest. `kvmppc_read_intr()` and `kvmppc_read_one_intr()` read XICS/OPAL interrupt state in real mode, distinguish host IPIs, guest wakeup IPIs, passthrough interrupts, and host-handled interrupts, and save XIRR state in PACA.

`get_irqmap()` and `kvmppc_check_passthru()` support lockless lookup of mapped passthrough IRQs when `CONFIG_KVM_XICS` is enabled. `kvmppc_set_msr_hv()`, `inject_interrupt()`, `kvmppc_inject_interrupt_hv()`, and `kvmppc_guest_entry_inject_int()` sanitize guest MSR, synthesize interrupt entry state, and inject pending external/decrementer/doorbell events. `flush_guest_tlb()` and `kvmppc_check_need_tlb_flush()` perform per-CPU guest TLB flushes requested by shared masks.

## Control Flow

Early boot calls `kvm_cma_reserve()` after memblock setup. If HV mode is unavailable it returns; otherwise it computes a percentage of physical memory, aligns to HPT requirements, and declares the `kvm_cma` area. Later HPT allocation uses `cma_alloc()` with HPT alignment and releases with `cma_release()`.

Real-mode exit coordination begins when one guest thread calls `kvmhv_commence_exit()`. It atomically sets that thread's exit-request bit in `entry_exit_map`; the first exiting thread interrupts other active vcore threads, and if split-core mode is active it also marks other subcores for exit and interrupts them.

Interrupt polling reads host IPI state first, then XICS/OPAL XIRR when XIVE is not active. XICS IPIs are cleared and EOIed; if a host IPI raced in, it is resent and the host handles it. Otherwise guest wakeup IPIs are consumed in real mode. Non-IPI interrupts are checked against passthrough mappings; mapped interrupts can be delivered directly to the target virtual interrupt controller, while unmapped or failed delivery returns control to host interrupt handling.

Interrupt injection writes SRR0/SRR1, PC, and MSR according to Book3S rules, including transactional suspend conversion and LPCR AIL=3 alternate interrupt location when legal. `kvmppc_set_msr_hv()` forces ME on, HV off, rejects illegal TS=11, updates the shadow MSR, and clears cede state.

## State And Persistence Behavior

Persistent-in-kernel state includes the CMA reservation pointer, the boot-time reservation ratio, `hv_vm_count`, and exported `kvmppc_host_rm_ops_hv`. Runtime per-vCPU/vcore state includes `conferring_threads`, `entry_exit_map`, PACA `kvm_hstate` fields, saved XIRR, cede/timer flags, doorbell state, and per-VM `need_tlb_flush` masks. No filesystem persistence is used.

## Dependencies And Integration Points

The file depends on memblock/CMA, CPU hotplug locks, OPAL interrupt services, XICS/XIVE interfaces, PACA `kvm_hstate`, Book3S interrupt constants, hcall real-mode tables, platform random seed hooks, and the HV private header. It exports functions used by KVM-HV modules, real-mode assembly handlers, and host interrupt paths.

## Risks

Real-mode code has strict constraints: it cannot rely on normal sleeping locks and must carefully order MMIO, OPAL, and shared-memory updates. The passthrough IRQ map uses lockless readers, so writer store ordering and the reader `smp_rmb()` are correctness-critical. Exit coordination uses bitmaps shared with assembly; incorrect bit placement can leave sibling threads running. Interrupt injection must preserve Book3S MSR/SRR semantics, especially around TM and AIL. CMA reservation sizing can fail HPT allocation if the ratio or alignment is wrong.

## Test Signals

Signals include successful HPT allocation from CMA, correct `kvm_cma_resv_ratio` parsing, CPU hotplug blocked while pre-POWER9 HV VMs exist, `H_CONFER` yield behavior, real-mode `H_RANDOM`, guest exits pulling all vcore/split-core threads out, XICS guest wakeup IPIs not leaking to the host, passthrough IRQs delivered or completed correctly, decrementer/external/doorbell injection, and per-CPU TLB flush masks clearing after guest TLB invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_builtin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_hmi.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_hmi.c

## Purpose

`book3s_hv_hmi.c` provides small synchronization helpers used by Hypervisor Maintenance Interrupt handling when KVM-HV guests may be running on POWER8 subcores. It waits for guest subcores to leave guest mode and waits for timebase resynchronization to complete before host HMI handling proceeds.

## Important APIs, Types, And Functions

`wait_for_subcore_guest_exit()` loops over `MAX_SUBCORE_PER_CORE` entries in the local PACA's `sibling_subcore_state->in_guest[]` array and waits until no sibling subcore is marked in guest mode. `wait_for_tb_resync()` waits until `CORE_TB_RESYNC_REQ_BIT` is clear in the sibling subcore state flags.

## Control Flow

Both functions first check `local_paca->sibling_subcore_state`. A NULL pointer means KVM has not initialized subcore tracking, no relevant guests are running, or the CPU is POWER9 or newer where this synchronization is not needed. In that case they return immediately. Otherwise they spin with `cpu_relax()` until the relevant guest-exit or timebase-resync condition clears.

## State And Persistence Behavior

The file does not own state. It observes per-core `sibling_subcore_state` installed in PACA by KVM-HV initialization and shared with HMI/timebase code. It does not persist data.

## Dependencies And Integration Points

It depends on PACA, HMI definitions, processor relaxation primitives, `MAX_SUBCORE_PER_CORE`, and the bit layout of `sibling_subcore_state`. It integrates with HMI paths that need all subcores in host context before OPAL or host code modifies timebase-related state.

## Risks

These are busy-wait loops in a high-priority maintenance path. If `in_guest[]` or the resync flag is not cleared because a guest thread is stuck or state ownership is broken, HMI handling can spin indefinitely. Conversely, returning too early can allow host timebase changes while a guest subcore still observes old state. The NULL-pointer fast path must stay aligned with POWER9+ and unloaded-KVM assumptions.

## Test Signals

Signals include HMI recovery on POWER8 with KVM guests in split-core mode, no hangs waiting for `in_guest[]`, successful timebase resync completion, and no unnecessary waiting on POWER9 or systems where KVM-HV subcore tracking was never initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_hmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_interrupts.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_interrupts.S

## Purpose

`book3s_hv_interrupts.S` contains the module-memory assembly entry point for Book3S HV virtual-core execution and a local helper for saving host PMU state. It bridges C scheduling code and the lower-level HV partition-switch trampoline by saving host nonvolatile state, preparing hypervisor decrementer/LPCR state, calling `kvmppc_hv_entry_trampoline`, and restoring the host frame after a guest exit that must return to virtual mode.

## Important APIs, Types, And Labels

`__kvmppc_vcore_entry` is the global entry label called from `kvmppc_run_core()` on pre-POWER9 paths. It uses PACA (`r13`) `HSTATE_*` offsets, vcore/KVM offsets, switch-frame offsets, and feature-fixup sections. `kvmhv_save_host_pmu` is a local function that freezes counters and saves host PMU registers into PACA host-state fields when the host has PMU state in use.

The assembly uses `SAVE_NVGPRS`, `REST_NVGPRS`, `PPC_MSGSND`-related register conventions indirectly through included headers, `SPRN_DSCR`, `SPRN_DABR`, `SPRN_LPCR`, `SPRN_DEC`, `SPRN_HDEC`, `SPRN_MMCR*`, `SPRN_MMCRA`, `SPRN_SIAR`, `SPRN_SDAR`, `SPRN_SIER`, and PMC SPRs.

## Control Flow

`__kvmppc_vcore_entry` saves LR into the caller stack frame, creates a switch frame, saves nonvolatile GPRs and CR, stores host DSCR in PACA, conditionally saves DABR on CPUs before ISA 2.07S, and calls `kvmhv_save_host_pmu()`. It then loads the current vcore and KVM, reads the host LPCR, sets LPCR[HDICE], copies the current DEC value into HDEC, records the resulting decrementer expiry in PACA, and branches to `kvmppc_hv_entry_trampoline`.

When the trampoline returns in virtual mode after a guest exit that cannot be handled in real mode, the code assumes hard interrupts remain disabled and that registers carry the trap number and handler ID conventions documented in comments. It restores nonvolatile GPRs and CR, tears down the switch frame, restores LR, and returns to C.

`kvmhv_save_host_pmu` freezes counters first. On POWER8-class CPUs it applies the MMCR2 freeze-all workaround, then freezes MMCR0 and clears MMCRA to stop SDAR updates. If `PACA_PMCINUSE` is clear, it returns after freezing. Otherwise it saves MMCR0/MMCR1/MMCRA, SIAR, SDAR, optional MMCR2/SIER, and PMC1 through PMC6 into PACA host-state slots.

## State And Persistence Behavior

The file saves transient host CPU state into the current PACA so guest entry can use PMU, decrementer, LPCR, DABR, and DSCR resources. It does not persist data beyond the guest-entry/exit interval. The saved HDEC expiry and PMU register state are later consumed by HV return/restoration paths outside this file.

## Dependencies And Integration Points

It is tightly coupled to `book3s_hv.c`'s call into `__kvmppc_vcore_entry`, the external `kvmppc_hv_entry_trampoline`, PACA layout generated in `asm-offsets.h`, `struct kvmppc_vcore` and KVM offset definitions, CPU feature fixup sections, PMU ownership tracking, and the real-mode HV handlers that return to this virtual-mode epilogue.

## Risks

Offset drift between C structures and assembly constants can corrupt host or guest state. PMU save ordering is delicate: counters must be frozen before reading event registers, and POWER8 errata require MMCR2 handling. LPCR[HDICE] must be set before writing HDEC on affected hardware. The entry/exit register convention must match the trampoline and C post-processing paths. Because the code runs with hard interrupts disabled, any missed restore can destabilize the host.

## Test Signals

Signals include pre-POWER9 KVM-HV guests entering and exiting reliably through `__kvmppc_vcore_entry`, host nonvolatile registers and CR preserved across guest runs, decrementer exits firing through HDEC, host PMU counts preserved when `PACA_PMCINUSE` is set, correct behavior on POWER8 errata-sensitive PMU paths, and no crashes from PACA offset mismatches under guest exit stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_interrupts.S -->
