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
