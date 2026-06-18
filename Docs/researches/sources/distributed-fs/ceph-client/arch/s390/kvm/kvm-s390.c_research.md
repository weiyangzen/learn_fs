# sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.c

## Purpose

`kvm-s390.c` is the main s390 architecture implementation for KVM. It wires the IBM Z/SIE execution engine into the generic KVM framework, exposes s390-specific VM and vCPU ioctls, initializes CPU models and facilities, manages VM/vCPU creation and destruction, implements protected virtualization command dispatch, controls memory-slot/gmap behavior, synchronizes guest-visible registers, and runs the SIE enter/exit loop.

The file owns the architecture-wide lifecycle: module init registers debug facilities, the FLIC device, PCI/GIB support, and the KVM core; VM init allocates SCA/SIE/GISA/gmap/crypto state; vCPU init allocates SIE pages and configures SIE control bits; `KVM_RUN` synchronizes userspace state, enters SIE, handles intercepts/faults, and stores state back.

## Important APIs, Types, and Functions

Module and feature setup:

- Module parameters: `nested`, `hpage`, `halt_poll_max_steal`, `use_gisa`, `diag9c_forwarding_hz`, and `async_destroy`.
- Stats descriptors `kvm_vm_stats_desc` and `kvm_vcpu_stats_desc` define VM/vCPU counters used by KVM stats ABI.
- `kvm_s390_cpu_feat_init()` detects host CPU subfunctions/facilities for PLO, PTFF, CPACF/MSA, SORTL, DFLTCC, PFCR, nested SIE-related features, and stores available CPU features in `kvm_s390_available_cpu_feat` and `kvm_s390_available_subfunc`.
- `__kvm_s390_init()` registers debug views, FLIC ops, optional PCI state, GIB alert support, and the TOD epoch notifier.
- `kvm_s390_init()` checks SIE availability, augments base facility masks with non-hypervisor-managed facilities, calls architecture init, and registers with generic `kvm_init()`.

Capability and VM attribute APIs:

- `kvm_vm_ioctl_check_extension()` reports s390 capabilities and capability values, including IRQCHIP, memory operations, CPU model/topology, protected virtualization, protected dump, zPCI, vector/RI/GS/BPB facilities, hpage support, and max vCPU IDs.
- `kvm_vm_ioctl_enable_cap()` enables VM-level capabilities such as IRQCHIP, user SIGP/STSI/instr0/operexc, vector registers, RI, AIS, GS, huge pages, CPU topology, and VSIE ESA mode.
- `kvm_s390_vm_set_attr()`, `kvm_s390_vm_get_attr()`, and `kvm_s390_vm_has_attr()` dispatch KVM device-attribute groups for memory control, TOD, CPU model, crypto, migration, and CPU topology.
- CPU model helpers set/get processor IDs, IBC, facility masks/lists, CPU feature bitmaps, subfunction blocks, and UV guest feature exposure.
- TOD helpers set/get guest epoch and epoch index, while `kvm_clock_sync()` tracks host TOD adjustments across all VMs/vCPUs.

Memory, keys, migration, and protected virtualization:

- `kvm_s390_get_skeys()`/`kvm_s390_set_skeys()` get/set storage keys through DAT/gmap helpers.
- `kvm_s390_get_cmma_bits()`/`kvm_s390_set_cmma_bits()` expose CMMA state for migration and use dirty-page accounting.
- `kvm_s390_vm_start_migration()` and `kvm_s390_vm_stop_migration()` switch CMMA migration mode and broadcast vCPU requests.
- `kvm_s390_handle_pv()` dispatches VM-level protected virtualization commands such as enable, disable, async cleanup prepare/perform, set secure parameters, unpack, verify, prepare reset, unshare all, info, and dump.
- `kvm_s390_cpus_to_pv()` and `kvm_s390_cpus_from_pv()` convert vCPUs into or out of protected mode and coordinate GISA use depending on UV AIV support.
- `kvm_s390_pv_dmp()` and `kvm_s390_handle_pv_vcpu_dump()` implement protected VM/CPU dump subcommands.
- `kvm_s390_vm_mem_op_abs()`, `kvm_s390_vm_mem_op_cmpxchg()`, `kvm_s390_vcpu_mem_op()`, and `kvm_s390_vcpu_sida_op()` implement VM and vCPU memory operation ABI variants.

VM/vCPU lifecycle:

- `kvm_arch_init_vm()` allocates SCA, per-VM debug state, `sie_page2`, facility masks, crypto block, floating-interrupt lists, gmap, optional ucontrol fake memslot, VSIE state, GISA, and protected-VM cleanup lists.
- `kvm_arch_destroy_vm()` destroys vCPUs, SCA, GISA, protected VM state, mmu notifier, debug state, adapters, floating IRQs, VSIE state, and gmap.
- `kvm_arch_vcpu_create()` allocates an MMU cache and SIE page, initializes low-level SIE fields, KVM sync-reg masks, optional ucontrol child gmap, then calls `kvm_s390_vcpu_setup()`.
- `kvm_s390_vcpu_setup()` sets initial CPUSTAT bits, guest model fields, SIE control bits for host/guest facilities, prefix-notification and interrupt behavior, CMMA, timers, crypto, zPCI, and PV CPU creation.
- `kvm_arch_vcpu_destroy()` clears local IRQs and async-pf queues, removes the vCPU from SCA/gmap, destroys PV CPU state, frees CMMA/SIE/MMU-cache state, and reports topology changes.
- SCA helpers `sca_add_vcpu()`, `sca_del_vcpu()`, and `sca_can_add_vcpu()` manage ESCA/SCA references and max vCPU ID limits.

Run loop and register synchronization:

- `kvm_arch_vcpu_ioctl_run()` implements `KVM_RUN`: validates sync fields, loads the vCPU, activates signal masks, starts the vCPU if KVM controls CPU state, syncs userspace registers into SIE state, enables CPU-timer accounting, runs `__vcpu_run()`, handles signals/debug/userspace exits, stores registers back, and unloads the vCPU.
- `__vcpu_run()` loops with SRCU held outside guest execution, calls `vcpu_pre_run()`, prepares guest-mode entry, disables CPU timer accounting while the guest runs, enters SIE via `kvm_s390_enter_exit_sie()`, reenables accounting, then calls `vcpu_post_run()`.
- `vcpu_pre_run()` checks async page completions, refreshes GPR14/GPR15, delivers pending interrupts, handles KVM requests, patches PER debug state, clears GISA kicked state, and emits SIE enter traces.
- `vcpu_post_run()` restores debug PER state, handles machine-check SIE returns, dispatches SIE intercepts via `kvm_handle_sie_intercept()`, or handles DAT/protected-storage faults.
- `sync_regs()`, `sync_regs_fmt2()`, `store_regs()`, and `store_regs_fmt2()` transfer PSW, prefix, control/access/general/floating/vector registers, CPU timer, clock comparator, pfault controls, runtime instrumentation, guarded storage, branch prediction control, etoken, and diag318 state between `struct kvm_run` and the SIE block.

vCPU control and ioctl APIs:

- `kvm_s390_vcpu_start()`/`kvm_s390_vcpu_stop()` transition STOPPED/OPERATING state with start-stop serialization, UV state changes for protected CPUs, IBS enable/disable policy, TLB flush requests, and stop IRQ clearing.
- Reset helpers implement normal, initial, and clear resets, including PV reset UVC calls.
- `kvm_arch_vcpu_ioctl()` handles store-status, initial PSW, resets, one-reg access, ucontrol mapping/faulting, vCPU capability enable, vCPU mem/SIDA ops, local IRQ state get/set, and protected CPU dump commands.
- `kvm_arch_vcpu_unlocked_ioctl()` handles unlocked injection ioctls and clears a pending single-step debug exit when userspace injects an interrupt after emulation.

Memory-slot integration:

- `kvm_arch_prepare_memory_region()` rejects invalid ucontrol slots, protected-VM slot changes, unaligned/out-of-limit memory, and stops CMMA migration mode if dirty logging assumptions are invalidated.
- `kvm_arch_commit_memory_region()` creates/deletes/moves DAT slot mappings under the MMU write lock.
- `kvm_test_age_gfn()`, `kvm_age_gfn()`, and `kvm_unmap_gfn_range()` delegate age/unmap operations to DAT/gmap helpers.

## Control Flow

### Module and VM Creation

`kvm_s390_init()` refuses to load without SIE facility support, adjusts base facility masks for non-hypervisor-managed facilities, initializes s390-specific global state, then registers KVM. Global init sets up debug buffers, detects feature/subfunction availability, registers the FLIC device, initializes optional zPCI state, initializes GIB alert support, and registers a TOD epoch notifier.

VM creation in `kvm_arch_init_vm()` validates VM type and privileges, allocates SCA and `sie_page2`, initializes the guest CPU model from host facilities and KVM policy, sets default emulated facilities, initializes crypto state, optional PCI interpretation, floating interrupt state, gmap, ucontrol fake memory when requested, memory feature flags, start/stop lock, VSIE state, optional GISA, and protected-VM cleanup lists. Error paths free partially initialized SIE/debug/SCA resources.

vCPU creation allocates a SIE page and MMU cache, initializes SIE block addresses and memory-size limits, sets sync-register validity based on available facilities, optionally creates a ucontrol child gmap, and configures SIE execution controls in `kvm_s390_vcpu_setup()`. Post-create synchronizes TOD epoch, attaches the vCPU to the VM gmap/SCA, and enables operation-exception interception if needed.

### VM Configuration and Migration

Most VM configuration flows are userspace ioctls routed through `kvm_arch_vm_ioctl()` or generic device attributes. Capability enables generally take `kvm->lock`, reject changes after vCPU creation when the ABI requires a stable CPU model, and update facility masks/lists or VM behavior flags. Memory-control attributes manage CMMA, memory limits, and dirty CMMA reset. CPU-model attributes allow userspace to select guest-visible CPU/facility/subfunction/UV-feature state before vCPU creation.

Migration mode requires memslots and, when CMMA is active, dirty bitmaps for all slots. Starting migration marks all CMMA pages dirty and disables direct CMMA virtualization on vCPUs via requests. Stopping migration reenables CMMA virtualization when possible. Memory-slot changes that invalidate dirty logging assumptions force migration mode off.

### Protected Virtualization

Protected virtualization command handling is centralized in `kvm_s390_handle_pv()`. `KVM_PV_ENABLE` disables THP creation, sets export-on-unmap, disables COW sharing, initializes the protected VM through UV, converts all vCPUs to protected mode, and masks service interrupts. Disable and async cleanup convert CPUs back from PV, deinitialize or set aside protected VM state, and clear service-interrupt masking. PV page faults in the run loop distinguish secure/non-secure storage exceptions, destroy stale secure pages after async teardown, or import pages into the protected guest.

Protected guests change several normal flows: many ioctls such as one-reg and memory operations are rejected, run-loop GPRs are copied through `sie_page->pv_grregs`, interrupts may be fenced in the internal PSW after certain PV intercepts, and reset/state changes use UV commands.

### KVM_RUN and SIE

`kvm_arch_vcpu_ioctl_run()` is the userspace-facing entry point. It rejects running while a protected dump is active, validates sync-reg masks, loads the vCPU, starts it if KVM owns CPU state, syncs userspace registers, enables CPU timer accounting, and calls `__vcpu_run()`.

`__vcpu_run()` repeatedly:

- Holds SRCU while preparing and post-processing host-side state.
- Calls `vcpu_pre_run()` to process async-pf completions, deliver pending interrupts, handle requests, patch guest debug PER state, and prepare trace state.
- Drops SRCU, prepares guest mode, disables CPU timer accounting because hardware/SIE accounts the running guest, enters SIE through `sie64a()`, reenables timer accounting, and reacquires SRCU.
- Copies PV GPRs back if needed and calls `vcpu_post_run()` to handle machine checks, SIE intercepts, or DAT/protected-storage faults.

Userspace exits are represented by `-EREMOTE` internally after `kvm_run` has been prepared; `kvm_arch_vcpu_ioctl_run()` converts that to a successful ioctl return. Signals become `KVM_EXIT_INTR` and `-EINTR`. Debug exits are prepared after interrupt delivery or SIE exits when single-step/PER requires userspace notification.

### Requests, Faults, and Async Page Faults

`kvm_s390_handle_requests()` drains architecture requests by clearing the SIE request bit, refreshing prefix notification pages, flushing TLBs via `ihcpu`, toggling IBS, enabling operation-exception interception, switching CMMA virtualization for migration, and consuming VSIE restart requests. Prefix refresh can return errors and requeue itself.

Fault handling after SIE uses `current->thread.gmap_int_code` and TEID. Translation/protection faults call `vcpu_dat_fault_handler()`, which can translate ucontrol addresses and fault in the relevant gfn. Secure-storage faults are PV-specific and either destroy stale secure pages or import pages into the protected VM. Async page faults inject pfault-init and pfault-done interrupts through the interrupt file rather than using a separate completion queue semantics.

## State and Persistence Behavior

Important per-VM state includes:

- `kvm->arch.sca`, `sie_page2`, `gmap`, `mem_limit`, facility model, CPU feature bitmaps, subfunction blocks, CPUID/IBC, TOD epoch/epoch-index, crypto CRYCB state, floating interrupt state, adapter list, GISA state, VSIE state, PV state, migration flags, CMMA dirty count, topology change bit, and debug buffer.
- `kvm->arch.model.fac_mask` and `fac_list` are userspace-visible CPU model state and are copied into vCPU SIE setup.
- `kvm->arch.pv` tracks protected VM handles, dumping state, cleanup lists, import locks, and notifier state.

Important per-vCPU state includes:

- `vcpu->arch.sie_block`, `gmap`, MMU cache, local interrupt state, CPU timer seqcount/start/enabled fields, pfault token/select/compare, debug/PER state, guarded-storage host backup, host access registers, local hrtimer, diag318 state, and PV CPU handle/state.
- `vcpu->run->s.regs` is the userspace synchronization area. `kvm_valid_regs` advertises which fields are supported and `kvm_dirty_regs` controls inbound synchronization.

State persists across userspace exits via explicit sync in `store_regs()`, VM/vCPU ioctls, migration APIs, and KVM device attributes. Runtime-only state such as host ACRS/FPU/GS controls is lazily loaded and restored around `KVM_RUN`. CPU timer accounting uses a seqcount plus preemption disabling to coordinate host TOD changes, vCPU load/put, and cross-vCPU reads.

## Dependencies and Integration Points

The file integrates with:

- Generic KVM core: module registration, VM/vCPU lifecycle hooks, ioctls, dirty logging, memslots, requests, SRCU, stats, halt polling, signal masks, and guest-mode entry helpers.
- s390 SIE assembly (`sie64a`) and SIE block format, including CPUSTAT/prog20 request bits, SCA/ESCA, facility controls, and interception fields.
- s390 memory translation (`gmap`, DAT helpers, storage keys, CMMA, prefix notification, ucontrol child gmappings).
- s390 protected virtualization (`uv.h` and KVM PV helpers) for VM/CPU create/destroy, secure page import/export, dump, reset, and UV feature reporting.
- Interrupt handling in `interrupt.c` for FLIC registration, IRQ injection/delivery, local/floating IRQ state, GISA/GIB, async page fault interrupt injection, and stop IRQ clearing.
- Optional zPCI and AP crypto integration through `pci.h`, AP instruction availability, CRYCB masks, and exported crypto mask functions.
- Debug/perf/trace infrastructure through debug feature buffers, `trace-s390.h`, and KVM event macros.

## Risks and Edge Cases

- The run loop depends on precise ordering of SRCU, guest-mode entry work, interrupt delivery, request handling, CPU timer accounting, FPU/ACR/GS state, and local IRQ state. Reordering can produce host state leaks, lost requests, or invalid guest timing.
- Protected virtualization introduces split behavior for memory slots, register access, interrupt injection, PV faults, dumping, and reset. Normal code paths must be fenced when a PV handle exists.
- VM configuration APIs often require no vCPUs to exist. Missing `kvm->lock` checks or allowing late CPU model changes can break migration ABI and SIE setup consistency.
- TOD/epoch changes are synchronized with preemption disabled and vCPU blocking. Races with vCPU load/put or CPU timer accounting can corrupt guest timer state.
- Memory operations intentionally reject protected VMs only heuristically in VM-level paths; concurrent PV transitions are considered userspace misuse but still must fail safely at access time.
- CMMA migration depends on dirty logging being active for every slot. Slot changes can silently force migration mode off via warning path.
- SCA/ESCA limits differ depending on SCA entry support, affecting max vCPU ID and external-call interpretation behavior.
- ucontrol mode uses fake memslots and child gmappings; normal VM assumptions about memory slots and address translation do not always apply.
- `exit_sie()` busy-waits until SIE leaves `PROG_IN_SIE`; misuse in contexts where the vCPU cannot make progress would deadlock.

## Test Signals

Useful validation signals include:

- KVM s390 selftests for capability probing, CPU model get/set, subfunction filtering, VM attributes, TOD set/get, topology change reporting, memory limits, and huge-page/CMMA incompatibilities.
- QEMU boot, reset, hotplug, migration, and protected-virtualization scenarios that exercise VM/vCPU creation, SCA/ESCA limits, IRQCHIP, FLIC, GISA, and CPU model ABI.
- `KVM_RUN` tests covering stopped/runnable state, signal exits, userspace SIE intercept exits, single-step/debug exits, operation-exception interception, and register sync masks.
- Storage key, CMMA, MEM_OP, CMPXCHG, SIDA, and ucontrol fault tests with boundary sizes, invalid flags, protected-VM rejection, and injected exception behavior.
- Protected virtualization tests for enable/disable, async cleanup, secure parameter import, unpack, verify, reset, unshare, dump init/config/cpu/complete, and secure/non-secure storage fault handling.
- Timer tests for CPU timer seqcount correctness, host TOD delta notifier handling, halt polling with steal-time cap, and migration of timer-related registers.
- Memory-slot tests that create/delete/move slots under normal, migration, ucontrol, and protected-VM states.
- Trace/stat counters from `kvm_vm_stats_desc`, `kvm_vcpu_stats_desc`, `trace_kvm_s390_sie_enter/exit`, vCPU start/stop traces, PV event logs, and debug feature buffers.
