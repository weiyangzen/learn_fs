# subset-b-000900 Research

Grouped research for VMX/KVM files under `sources/distributed-fs/ceph-client/arch/x86/kvm/vmx`. Each section preserves the source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/pmu_intel.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/pmu_intel.c

## Purpose
Implements Intel-specific KVM PMU operations for VMX vCPUs. It translates guest RDPMC/MSR accesses to KVM PMU counters, refreshes virtual PMU capabilities from CPUID and host perf capabilities, manages fixed/general counters, supports guest Last Branch Record virtualization through perf, and wires Intel behavior into `struct kvm_pmu_ops intel_pmu_ops`.

## Important APIs, Types, And Functions
The exported/externally consumed objects are `intel_pmu_ops`, `intel_pmu_lbr_is_enabled()`, `intel_pmu_create_guest_lbr_event()`, `vmx_passthrough_lbr_msrs()`, and `intel_pmu_cross_mapped_check()`. Core helpers include `intel_rdpmc_ecx_to_pmc()`, `intel_is_valid_msr()`, `intel_pmu_get_msr()`, `intel_pmu_set_msr()`, `intel_pmu_refresh()`, `intel_pmu_init()`, `intel_pmu_reset()`, `intel_pmu_deliver_pmi()`, `intel_mediated_pmu_load()`, and `intel_mediated_pmu_put()`. `vcpu_to_lbr_desc()` and `vcpu_to_lbr_records()` deliberately return `NULL` for TDX vCPUs, preventing LBR virtualization on protected guests.

## Control Flow
Guest RDPMC calls flow through `intel_rdpmc_ecx_to_pmc()`, which decodes architectural ECX type/index fields, rejects non-architectural PMUs, selects fixed or GP counter arrays, and returns a masked `kvm_pmc`. Guest PMU MSR reads/writes flow through `intel_pmu_get_msr()` and `intel_pmu_set_msr()`, which handle fixed counter control, PEBS, DS area, counter values, event selectors, and LBR MSRs. PMU refresh parses CPUID leaf 0xa, clamps virtual counter counts and widths to host `kvm_pmu_cap`, enables TSX event bits when exposed, builds reserved masks, and configures LBR/PEBS support based on `IA32_PERF_CAPABILITIES`. LBR passthrough is enabled only in the VM-entry path after the backing perf event is active; otherwise KVM reinstalls MSR intercepts and returns zeros for inaccessible LBR reads.

## State And Persistence
Persistent vCPU PMU state lives in `struct kvm_pmu`: counter arrays, `fixed_ctr_ctrl`, `global_ctrl_rsvd`, PEBS fields, masks, and event accounting. VMX-specific LBR state lives in `struct lbr_desc` attached to `vcpu_vmx`: the LBR record layout, perf event pointer, and `msr_passthrough` flag. The code marks counters in `pmu->pmc_in_use`, requests counter reprogramming, and stores/clears host hardware PMU MSRs across mediated PMU load/put. LBR perf events are released on reset or cleanup when guest debugctl no longer enables LBR.

## Dependencies And Integration Points
The file depends on KVM PMU core helpers from `pmu.h`, VMX MSR bitmap manipulation, perf event APIs, CPUID helpers, VMX capabilities, nested VMX, TDX detection, and VMCS accessors. `intel_pmu_ops` is the main integration point with the x86 PMU core. The LBR path integrates with host perf scheduling and VM-entry MSR interception. Mediated PMU support integrates with VMCS `GUEST_IA32_PERF_GLOBAL_CTRL` and host MSRs.

## Risks
High-risk areas are LBR passthrough and mediated PMU save/restore. Host perf can reclaim LBR resources asynchronously, so incorrect state checks could leak host LBR values or expose stale guest values. Reserved-bit validation for PEBS/eventsel/full-width counter writes must match CPU model semantics. TDX bypasses VMX LBR state; any accidental `to_vmx()` use for TD vCPUs would be unsafe, hence the local `#pragma GCC poison to_vmx`. Cross-mapped host counters can make guest PMU behavior differ from architectural expectations.

## Test Signals
Useful signals include KVM unit tests for RDPMC, PMU MSR reserved bits, fixed counters, PEBS exposure, LBR enable/disable, nested CPUID model changes, and TDX guests with PMU operations disabled. Kernel logs with `fail to passthrough LBR`, perf event creation failures, WARNs on non-architectural PMU use, and counter reprogramming behavior under host perf contention are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/pmu_intel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/pmu_intel.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/pmu_intel.h

## Purpose
Declares the VMX Intel PMU interface shared by the PMU implementation and other VMX code. It exposes helpers for guest `IA32_PERF_CAPABILITIES`, full-width counter writes, guest LBR state, and the LBR capability record.

## Important APIs, Types, And Functions
`vcpu_get_perf_capabilities()` returns zero unless guest CPUID exposes PDCM, otherwise it returns `vcpu->arch.perf_capabilities`. `fw_writes_is_enabled()` checks `PERF_CAP_FW_WRITES`. `struct lbr_desc` contains `struct x86_pmu_lbr records`, a backing `struct perf_event *event`, and `bool msr_passthrough`. The header declares `intel_pmu_lbr_is_enabled()`, `intel_pmu_create_guest_lbr_event()`, and `extern struct x86_pmu_lbr vmx_lbr_caps`.

## Control Flow
The header is mostly inline policy. PMU code calls the capability helpers before accepting full-width counter MSR aliases or PEBS/LBR features. VM-entry code and PMU code use `lbr_desc` to decide whether guest LBR MSRs are intercepted or passed through.

## State And Persistence
`struct lbr_desc` is persistent per VMX vCPU. `records` describes architectural LBR MSR ranges, `event` pins the host perf LBR resource for guest use, and `msr_passthrough` tracks whether the MSR bitmap currently allows direct guest access. The helper functions do not persist state themselves but gate access to vCPU PMU state.

## Dependencies And Integration Points
Includes `linux/kvm_host.h` and local `cpuid.h`. It depends on x86 feature definitions such as `X86_FEATURE_PDCM` and perf capability bits. The header is used by PMU code and VMX entry/intercept code that needs LBR status without including the full PMU implementation.

## Risks
Incorrectly reporting `PERF_CAP_FW_WRITES` changes guest-visible MSR alias behavior and can let userspace or the guest write unsupported counter widths. `lbr_desc::msr_passthrough` must stay synchronized with VMX MSR bitmap changes; stale passthrough state could expose host LBRs.

## Test Signals
Compile coverage for both PMU and VMX users, PMU capability tests with and without PDCM, full-width counter write tests, and LBR passthrough tests all exercise this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/pmu_intel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.c

## Purpose
Implements VMX posted interrupt lifecycle support, including per-vCPU PI descriptor updates on vCPU load/put, wakeup handling for blocked vCPUs, APICv state restore cleanup, pending interrupt checks, and VT-d interrupt remapping integration.

## Important APIs, Types, And Functions
Public functions are `vmx_vcpu_pi_load()`, `vmx_vcpu_pi_put()`, `pi_wakeup_handler()`, `pi_init_cpu()`, `pi_apicv_pre_state_restore()`, `pi_has_pending_interrupt()`, `vmx_pi_start_bypass()`, and `vmx_pi_update_irte()`. Key internal helpers are `vcpu_to_pi_desc()`, `pi_try_set_control()`, `vmx_can_use_vtd_pi()`, `pi_enable_wakeup_handler()`, and `vmx_needs_pi_wakeup()`. Per-CPU state consists of `wakeup_vcpus_on_cpu` and `wakeup_vcpus_on_cpu_lock`.

## Control Flow
On vCPU load, `vmx_vcpu_pi_load()` refreshes the PI descriptor destination APIC ID, clears suppress-notification, restores the normal posted interrupt vector, removes the vCPU from the previous CPU wake list if it was blocking, and sets ON if PIR is nonempty. On vCPU put, `vmx_vcpu_pi_put()` either installs the wakeup vector and queues the vCPU on a per-CPU wake list when the vCPU is blocking with interrupts allowed, or suppresses notifications to avoid spurious host IRQs. The wakeup interrupt runs `pi_wakeup_handler()`, which scans the local wake list and wakes vCPUs whose PI descriptor ON bit is set. VT-d irqfd updates call `irq_set_vcpu_affinity()` with PI descriptor physical address and vector.

## State And Persistence
The PI descriptor in `vcpu_vt` stores PIR bits, ON/SN flags, notification vector, and destination. `vcpu_vt::pi_wakeup_list` links a blocked vCPU into exactly one per-CPU wake list. Descriptor control updates are atomic via `try_cmpxchg64()` because hardware or other vCPUs can set ON concurrently. The per-CPU wake lists persist for CPU lifetime and are initialized by `pi_init_cpu()`.

## Dependencies And Integration Points
Depends on APICv capability state, local APIC in-kernel mode, VMX/VT common vCPU structures, TDX interrupt allowance checks, irq bypass, irq remapping, and KVM request/wakeup APIs. It integrates with scheduler load/put hooks, posted interrupt vectors, VT-d interrupt remapping, and TDX posted-interrupt delivery, while excluding TDX from IPIV wakeup use.

## Risks
The main risks are CPU migration races, lock ordering between scheduler locks and wakeup locks, lost posted interrupts when switching vectors, and stale PI destination fields after hotplug or migration. The code disables IRQs around per-CPU lock operations to avoid deadlocks with the wakeup interrupt. Incorrect SN/ON ordering could either lose wakeups or cause interrupt storms.

## Test Signals
Relevant signals include APICv and posted-interrupt KVM tests, irqfd passthrough tests, vCPU block/wakeup under migration, CPU hotplug while TD/VMX vCPUs are loaded, and stress with dynamic APICv inhibition. WARNs for SN set before blocking and failures in irq affinity update are important diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.h

## Purpose
Declares the posted interrupt API for VMX and provides a small bitmap helper for selecting the highest pending posted interrupt vector.

## Important APIs, Types, And Functions
The header declares load/put hooks, the wakeup handler, CPU initialization, APICv restore cleanup, pending interrupt query, VT-d IRTE update, and bypass-start notification. `pi_find_highest_vector()` uses `find_last_bit()` over the 256-bit PIR bitmap and returns `-1` when no vector is pending.

## Control Flow
VMX vCPU scheduling and interrupt code call these prototypes without depending on the implementation internals. `pi_find_highest_vector()` is synchronous and only interprets the current PIR bitmap; it does not clear bits or update descriptor control.

## State And Persistence
This header owns no storage. It describes operations over `struct pi_desc`, `struct kvm_vcpu`, `struct kvm`, and irqfd state managed by the implementation and by architecture code.

## Dependencies And Integration Points
Includes Linux bitmap/find/KVM host headers and `asm/posted_intr.h`. The declarations are consumed by VMX vCPU lifecycle, APICv, interrupt injection, irq bypass, and TDX code.

## Risks
The helper assumes a 256-vector PIR layout. Callers must handle synchronization around PIR mutation and descriptor ON/SN state; this header intentionally does not impose locking.

## Test Signals
Build coverage, APICv delivery tests, highest-vector selection checks, and irqfd posted-interrupt passthrough cover the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/posted_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/run_flags.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/run_flags.h

## Purpose
Defines bit flags passed to the low-level VMX run assembly path.

## Important APIs, Types, And Functions
`VMX_RUN_VMRESUME` selects VMRESUME instead of VMLAUNCH. `VMX_RUN_SAVE_SPEC_CTRL` documents/specifies a run flag for saving guest SPEC_CTRL state. `VMX_RUN_CLEAR_CPU_BUFFERS_FOR_MMIO` requests CPU buffer clearing when the vCPU can access host MMIO.

## Control Flow
`vmenter.S` tests `VMX_RUN_VMRESUME` before executing VMRESUME or VMLAUNCH and tests `VMX_RUN_CLEAR_CPU_BUFFERS_FOR_MMIO` in the VERW mitigation path when the CPU uses conditional MMIO buffer clearing. C code constructing run flags controls these mitigations and entry mode.

## State And Persistence
No persistent state. The flags are transient inputs to a single guest entry attempt and are consumed from the assembly stack frame.

## Dependencies And Integration Points
Depends on `BIT()` from included kernel context. Integrated directly with `__vmx_vcpu_run()` and VMX C code that decides launch/resume and mitigation requirements.

## Risks
Flag bit reuse or mismatch with assembly offsets can select the wrong VM-entry instruction or skip required CPU vulnerability mitigations. Since the assembly reads flags by stack offset, calling convention changes must keep this contract intact.

## Test Signals
VMX launch/resume tests, nested VMX tests, and CPU mitigation selftests or tracing around VERW behavior are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/run_flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.c

## Purpose
Implements KVM virtualization of Intel SGX ENCLS exits for VMX. It emulates or forwards key ENCLS leaves, validates guest SGX capabilities and BIOS enablement, safely translates guest operands for ECREATE/EINIT, virtualizes SGX launch-enclave public-key hash MSRs, and programs the VMCS ENCLS exiting bitmap.

## Important APIs, Types, And Functions
External functions are `handle_encls()`, `setup_default_sgx_lepubkeyhash()`, `vcpu_setup_sgx_lepubkeyhash()`, and `vmx_write_encls_bitmap()`. Core helpers include `sgx_get_encls_gva()`, `sgx_gva_to_gpa()`, `sgx_gpa_to_hva()`, `sgx_inject_fault()`, `handle_encls_ecreate()`, `__handle_encls_ecreate()`, `handle_encls_einit()`, `encls_leaf_enabled_in_guest()`, `sgx_enabled_in_guest_bios()`, and `sgx_intercept_encls_ecreate()`. The module parameter `enable_sgx` gates support.

## Control Flow
An ENCLS VM-exit reaches `handle_encls()`. It injects #UD if SGX/SGX1 is unavailable, #GP if the leaf is not guest-enabled, BIOS enablement is missing, or paging is off, then dispatches ECREATE and EINIT. ECREATE translates PAGEINFO, SECINFO, source, and SECS operands through GVA, GPA, and HVA stages, deep-copies SECS contents to avoid TOCTOU, enforces CPUID masks, provisioning-key policy, XFRM constraints, and max enclave size, then calls `sgx_virt_ecreate()`. EINIT translates SIGSTRUCT, SECS, and TOKEN operands, calls `sgx_virt_einit()` with vCPU launch-control hashes, updates flags and RAX, and skips the instruction. Bitmap programming starts from intercept-all, clears allowed SGX1/SGX2 ranges, forces ECREATE/EINIT exits when KVM must enforce policy, and ORs nested VMX ENCLS exits when needed.

## State And Persistence
Global `sgx_pubkey_hash[4]` stores default launch-control hash values after setup. Each VMX vCPU stores virtual `msr_ia32_sgxlepubkeyhash` values copied from that global. SGX provisioning policy is stored in `kvm->arch.sgx_provisioning_allowed`. The ENCLS bitmap is VMCS state and may incorporate nested `vmcs12->encls_exiting_bitmap`.

## Dependencies And Integration Points
Depends on SGX kernel helpers `sgx_virt_ecreate()` and `sgx_virt_einit()`, KVM MMU translation, VMX segment helpers, CPUID leaf 0x12, feature-control MSR state, nested VMX, VMCS writes, and guest capability state. It integrates with `vmx.c` exit handling and vCPU setup paths.

## Risks
SGX operand translation is sensitive to segmentation, canonicality, alignment, and page faults. Bad HVA handling exits to userspace as emulation failure. Provisioning-key and CPUID enforcement must happen on copied data to prevent guest TOCTOU. The code comments identify a limitation: non-EPCM #PF detection lacks PFEC.SGX plumbing. ENCLS bitmap errors can expose unsupported leaves or incorrectly trap leaves that should run natively.

## Test Signals
SGX KVM tests should cover disabled SGX, SGX1/SGX2 leaf gating, ECREATE CPUID mask enforcement, provisioning-key denial, EINIT launch-control hash behavior, nested ENCLS bitmap merging, invalid operands, bad userspace HVA exits, and SGX2 EPCM fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.h

## Purpose
Declares the VMX SGX hooks and provides no-op or intercept-all fallbacks when `CONFIG_X86_SGX_KVM` is disabled.

## Important APIs, Types, And Functions
When SGX KVM support is enabled, it declares `enable_sgx`, `handle_encls()`, `setup_default_sgx_lepubkeyhash()`, `vcpu_setup_sgx_lepubkeyhash()`, and `vmx_write_encls_bitmap()`. Without SGX KVM, `enable_sgx` is a constant zero, setup functions are no-ops, and `vmx_write_encls_bitmap()` writes `-1ull` to `ENCLS_EXITING_BITMAP` when hardware supports ENCLS exits.

## Control Flow
VMX initialization/setup uses the setup helpers for launch-control MSR defaults. VM-exit handling calls `handle_encls()` only in SGX-enabled builds. VMCS setup calls `vmx_write_encls_bitmap()` regardless of build, allowing the disabled build to force all ENCLS leaves to exit.

## State And Persistence
The header owns no state. It exposes global SGX enablement and vCPU launch-control setup when enabled. In disabled builds, state is intentionally absent and ENCLS remains intercepted.

## Dependencies And Integration Points
Includes KVM host definitions, VMX capabilities, and VMCS operation helpers. It links SGX support to VMX exit handling, VMCS setup, and vCPU initialization.

## Risks
The fallback must preserve correct guest behavior when host hardware supports ENCLS exits but the kernel lacks SGX KVM support. If the bitmap is not set to intercept all leaves, unsupported ENCLS execution could reach hardware unexpectedly.

## Test Signals
Builds with and without `CONFIG_X86_SGX_KVM`, VMCS bitmap inspection, and guest SGX-disabled ENCLS #UD/#GP behavior validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/sgx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx.c

## Purpose
Implements Intel TDX support for KVM/VMX. It manages TDX hardware enablement, TD VM and TD vCPU lifecycle, HKID allocation/release, TD control-page allocation and reclamation, TDVMCALL exit handling, protected interrupt delivery, private/shared GPA mapping, Secure EPT integration, guest memory population and measurement, TDX ioctls, emulated MSRs, CPUID metadata, and TD entry/exit.

## Important APIs, Types, And Functions
Important public hooks include `tdx_hardware_setup()`, `tdx_hardware_unsetup()`, `tdx_disable_virtualization_cpu()`, `tdx_vm_init()`, `tdx_vm_destroy()`, `tdx_mmu_release_hkid()`, `tdx_vcpu_create()`, `tdx_vcpu_load()`, `tdx_vcpu_put()`, `tdx_vcpu_free()`, `tdx_vcpu_pre_run()`, `tdx_vcpu_run()`, `tdx_handle_exit()`, `tdx_deliver_interrupt()`, `tdx_inject_nmi()`, `tdx_get_exit_info()`, `tdx_get_msr()`, `tdx_set_msr()`, `tdx_vm_ioctl()`, `tdx_vcpu_ioctl()`, `tdx_vcpu_unlocked_ioctl()`, `tdx_flush_tlb_current()`, `tdx_flush_tlb_all()`, `tdx_load_mmu_pgd()`, and `tdx_gmem_max_mapping_level()`. Internal control paths include TD creation/finalization, VP creation/init, TDVMCALL dispatch, SEPT page add/augment/link/remove, and CPUID metadata reads.

## Control Flow
Hardware setup initializes per-CPU TD vCPU lists, verifies EPT/TDP MMU/MMIO caching/EPT A-D/APICv/OSXSAVE/TDX platform support, obtains TDX sysinfo, validates capabilities, sets misc cgroup capacity, and installs Secure EPT hooks. VM init marks the VM as protected/private-memory backed and sets TDX-specific MMIO SPTE behavior. `KVM_TDX_INIT_VM` validates user TD params and CPUID, allocates HKID/TDR/TDCS pages, creates the TD, configures keys on one CPU per package, adds TDCS pages, initializes TD metadata, reads TSC parameters, and transitions to `TD_STATE_INITIALIZED`. `KVM_TDX_INIT_VCPU` allocates TDVPR/TDCX pages, creates/adds/initializes VP state, programs posted interrupt TD VMCS fields, and transitions to `VCPU_TD_STATE_INITIALIZED`. `KVM_TDX_INIT_MEM_REGION` populates guest_memfd private pages through KVM MMU mapping and optionally extends measurement in 256-byte chunks. Finalization calls `TDH_MR_FINALIZE`, transitions to runnable, and enables pre-faulting.

The run path checks state, blocks entry while SEPT zap retry is active, handles pending posted interrupts, enters via `TDH.VP.ENTER`, maps TDX module return state to VMX exit reasons, restores host debug/xsave state, and either fast-reenters or calls `tdx_handle_exit()`. Exit handling supports triple fault, exception/NMI, external interrupt, CPUID, HLT, TDVMCALLs, hypercalls, I/O, MSR read/write, MMIO via EPT misconfig, EPT violation, and SMI. TDVMCALLs implement MAP_GPA chunking to userspace hypercall exits, fatal-error system events, TD VM call info, quote requests, and event-notify interrupt setup.

## State And Persistence
Persistent TD state lives in `struct kvm_tdx`: misc cgroup charge, HKID, TD state, attributes, XFAM, TSC offset/multiplier, TDR/TDCS control pages, transient `page_add_src`, and `wait_for_sept_zap`. Persistent vCPU state lives in `struct vcpu_tdx`: embedded common VT state, TDX module VP structure, CPU association list node, VP.ENTER args/return, extended exit qualification, exit GPA, vCPU state, and MAP_GPA progress. Per-CPU `associated_tdvcpus` tracks TD vCPUs associated with each CPU and is updated with IRQs disabled. TDX module state persists outside KVM and is manipulated through SEAMCALLs.

## Dependencies And Integration Points
Depends on TDX host platform APIs, SEAMCALL wrappers, KVM MMU/TDP MMU, guest_memfd, misc cgroup TDX resource accounting, VMX capabilities, posted interrupts, KVM x86 ops, local APIC, tracepoints, CPUID, and user ABI structs for `KVM_TDX_*`. It installs external SPT hooks into `vt_x86_ops` and relies on KVM core locking (`kvm->lock`, vCPU mutexes, `slots_lock`, `mmu_lock`) for state transitions and memory operations.

## Risks
The highest-risk paths are resource teardown and SEAMCALL concurrency. HKID release requires VP flush, cache writeback across packages, key free, and control-page reclamation in the right order; failures intentionally leak pages/HKIDs rather than reusing unsafe memory. SEPT removal and page add/augment can return operand-busy due to running vCPUs or zero-step mitigation; retry and `wait_for_sept_zap` ordering are critical. TD initialization requires all packages to have an online CPU for key programming. Private/shared GPA validation must prevent MMIO or MAP_GPA from crossing the shared-bit boundary. Protected guests limit host visibility, so unsupported exits and MSRs must be rejected or surfaced to userspace carefully.

## Test Signals
Coverage should include TDX disabled setup paths, capability ioctl sizing, TD init invalid CPUID/attributes/XFAM/GPAW, package-online failure, vCPU init before/after TD init, memory population and measurement, finalize then pre-fault, MAP_GPA chunking and retry, MMIO/PIO exits, emulated MSRs, CPUID metadata reads, private EPT faults, SEPT zap under vCPU load, CPU hotplug/TD vCPU disassociation, HKID release failure injection, and guest fatal-error reporting. Logs from `TDX_BUG_ON`, non-recoverable VP.ENTER returns, and VM dead requests are key diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx.h

## Purpose
Defines the public TDX data model and inline accessors used by VMX/KVM code. It wraps TDX support in `CONFIG_KVM_INTEL_TDX`, defines TD and vCPU state structs, declares hardware/runtime hooks, and generates typed TDVPS read/write helpers.

## Important APIs, Types, And Functions
`enum kvm_tdx_state` models TD module state: uninitialized, initialized, runnable. `struct kvm_tdx` embeds `struct kvm` and stores misc cgroup, HKID, TD state, attributes, XFAM, TSC data, `struct tdx_td`, `page_add_src`, and `wait_for_sept_zap`. `enum vcpu_tdx_state` and `struct vcpu_tdx` hold TD vCPU state, common VT state, exit metadata, `struct tdx_vp`, per-CPU list node, VP.ENTER return, and MAP_GPA progress. Inline helpers include `td_tdcs_exec_read64()` and macro-generated `td_vmcs_read/write/setbit/clearbit*`, `td_management_*`, and `td_state_non_arch_*`.

## Control Flow
The header exposes TDX lifecycle hooks to `x86_ops.h` and VMX code. Generated accessors build TDX field IDs from VMCS, management, or non-architectural state classes and call `tdh_vp_rd()` or `tdh_vp_wr()`. Compile-time checks prevent unsupported TD VMCS high-field and width mismatches.

## State And Persistence
This header defines the persistent allocation shape for TDX VMs and vCPUs. It also records the transient synchronization field `wait_for_sept_zap`, used to keep vCPUs out of TD entry while Secure EPT zapping retries. In disabled builds, stub `struct kvm_tdx` and `struct vcpu_tdx` preserve container expectations without enabling functionality.

## Dependencies And Integration Points
Includes TDX architectural constants and errno values. Enabled builds include `common.h` and depend on SEAMCALL types from architecture headers. The structs are used as larger VM/vCPU allocations selected during TDX hardware setup.

## Risks
Struct layout affects allocation size and container casts. Accessor macros BUG the VM on unexpected TDH_VP_RD/WR failures, so field IDs and widths must be exact. Stub behavior must remain consistent enough for non-TDX builds to compile while preventing accidental TDX operation.

## Test Signals
Builds with and without `CONFIG_KVM_INTEL_TDX`, compile-time VMCS width checks, TDVPS access to posted interrupt and NMI fields, and KVM sanity checks for `kvm_tdx` allocation size validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_arch.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_arch.h

## Purpose
Defines architectural TDX field encodings, TD parameter layout, CPUID value layout, TSC conversion helpers, Secure EPT state decoding, and metadata IDs used by KVM's TDX implementation.

## Important APIs, Types, And Functions
Field encoding macros include `BUILD_TDX_FIELD()`, `BUILD_TDX_FIELD_NON_ARCH()`, `TDCS_EXEC()`, `TDVPS_VMCS()`, `TDVPS_STATE()`, `TDVPS_STATE_NON_ARCH()`, and `TDVPS_MANAGEMENT()`. Key structs are `struct tdx_cpuid_value` and the 1024-byte aligned/packed `struct td_params`. Helpers include `tdx_vcpu_state_details_intr_pending()`, `tdx_get_sept_level()`, and `tdx_get_sept_state()`.

## Control Flow
`tdx.c` uses these constants to build TDH_MNG_INIT input, read TDCS execution controls, read/write TDVPS fields, inject pending NMI, detect pending interrupt state, extend measurement in fixed chunks, interpret extended exit qualification, and construct metadata reads for TD CPUID values.

## State And Persistence
The file defines persistent ABI layout for `struct td_params`, including attributes, XFAM, max vCPUs, EPTP controls, config flags, TSC frequency, measurement IDs, owner fields, and CPUID values. It does not allocate state itself.

## Dependencies And Integration Points
Depends only on Linux types and bit helpers. It integrates with SEAMCALL wrappers, TDX module metadata, KVM userspace ABI conversion, and Secure EPT handling.

## Risks
Packed layout and field IDs must match the TDX module ABI exactly. TSC frequency conversion truncates to 25 MHz units, so callers must ensure the default TSC kHz is valid. Secure EPT state decoding must match module-provided level/state bit positions.

## Test Signals
Static size/build assertions in `tdx.c`, TD init success/failure against the TDX module, CPUID metadata reads, measurement extension, and Secure EPT fault handling validate these definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_errno.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_errno.h

## Purpose
Defines architectural TDX SEAMCALL status values and operand IDs consumed by the TDX implementation.

## Important APIs, Types, And Functions
`TDX_SEAMCALL_STATUS_MASK` extracts the high status field from RAX. Status constants include non-recoverable vCPU/TD failures, resumable interruption, invalid operand, operand busy, previous TLB epoch busy, incorrect page metadata, vCPU not associated, key errors, cache writeback completion, flush-vp-not-done, EPT walk failure, EPT entry state errors, and unreadable metadata fields. Operand IDs identify RCX, TDR, SEPT, and TD epoch.

## Control Flow
`tdx.c` masks SEAMCALL returns to detect operand-busy retry paths, invalid user operands, non-recoverable TD states, interrupted cache writeback, missing HKID cache work, and VP association races. The low 32-bit operand IDs are returned to userspace in selected hardware error cases.

## State And Persistence
No state is stored. The constants are stable ABI glue between TDX module returns and KVM error handling.

## Dependencies And Integration Points
Included by `tdx.h` and used throughout `tdx.c` in `TDX_BUG_ON` checks, retry decisions, teardown, and ioctl `hw_error` reporting.

## Risks
Incorrect status constants would route fatal module errors into retry paths or user errors into KVM BUG paths. Masking only high status bits means low operand details must be preserved when reporting `hw_error`.

## Test Signals
Fault-injection or mocked SEAMCALL tests for operand-busy, invalid operand, non-recoverable returns, cache writeback statuses, and metadata read failures validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs.h

## Purpose
Defines VMCS support types and helpers shared across VMX code, including VMCS12 field index compression, loaded-VMCS tracking, host-state caching, control-shadow caching, interrupt-info predicates, and VMCS field metadata helpers.

## Important APIs, Types, And Functions
Macros `ROL16()`, `VMCS12_IDX_TO_ENC()`, and `ENC_TO_VMCS12_IDX()` map VMCS encodings to compact array indices. `struct vmcs_host_state` caches host fields loaded on VM-exit. `struct vmcs_controls_shadow` caches execution/entry/exit controls. `struct loaded_vmcs` tracks current VMCS, shadow VMCS, CPU, launch state, virtual NMI state, hv timer state, MSR bitmap, loaded-list linkage, host state, and control shadows. Helper predicates identify interrupt types and exception vectors. `vmcs_field_width()`, `vmcs_field_readonly()`, and `vmcs_field_index()` decode VMCS field encodings.

## Control Flow
Nested VMX uses the encoding/index helpers to map arbitrary VMREAD/VMWRITE field encodings to `struct vmcs12` offsets. VMX entry/load paths use `loaded_vmcs` to track whether a VMCS is loaded on a CPU and whether it has launched. Exit handling uses interrupt predicates to classify VM-exit interruption information.

## State And Persistence
`DECLARE_PER_CPU(struct vmcs *, current_vmcs)` tracks the loaded VMCS pointer per CPU. `loaded_vmcs` instances persist for vCPU or nested-VMX lifetime and link into per-CPU loaded VMCS lists so CPU-down paths can clear them. Host-state and control-shadow fields are write-through caches of VMCS fields.

## Dependencies And Integration Points
Depends on Linux time/list/nospec, x86 KVM/VMX architectural constants, and VMX capability definitions. Used by VMX core, nested VMX, VMCS operation wrappers, TDX VMCS access checks, and VM-entry code.

## Risks
VMCS field encoding helpers must match Intel VMCS encoding layout. `loaded_vmcs` CPU tracking is sensitive to migration and CPU hotplug. Interrupt-info helpers rely on valid VMCS interruption information masks; misuse can misclassify NMIs, exceptions, or external interrupts.

## Test Signals
Nested VMX VMREAD/VMWRITE tests, CPU hotplug with loaded VMCSs, virtual NMI tests, VMCS shadow tests, and exception-injection/exit-classification tests exercise this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.c

## Purpose
Builds the runtime lookup table that maps VMCS field encodings to offsets in KVM's packed `struct vmcs12`, filtered by the actual VMX capabilities available on the host.

## Important APIs, Types, And Functions
`kvm_supported_vmcs12_field_offsets[]` is the static offset table populated with `FIELD()` and `FIELD64()` macros. `vmcs12_field_offsets[]` and `nr_vmcs12_fields` are runtime, read-mostly outputs. `cpu_has_vmcs12_field()` checks whether a field should be exposed based on VMX features. `nested_vmx_setup_vmcs12_fields()` copies supported entries into the runtime table at init.

## Control Flow
At initialization, `nested_vmx_setup_vmcs12_fields()` iterates the static array. Empty entries and capability-disabled fields are skipped. Supported fields get their `struct vmcs12` offset copied into `vmcs12_field_offsets`, and `nr_vmcs12_fields` advances to the highest present index plus one. Nested VMX VMREAD/VMWRITE later use `get_vmcs12_field_offset()` from the header against this table.

## State And Persistence
`vmcs12_field_offsets[]` and `nr_vmcs12_fields` are initialized once and marked `__ro_after_init`. They define the persistent nested-VMX field surface for the running module. The static table is `__initconst`.

## Dependencies And Integration Points
Depends on `vmcs12.h`, VMCS encodings, and capability helpers such as VPID, posted interrupts, TSC scaling, TPR shadow, APIC access virtualization, VMFUNC, EPT, XSAVES, ENCLS VM-exit, perf global ctrl load, secondary controls, and CET controls. It is central to nested VMX emulation and live migration compatibility.

## Risks
Forgetting to gate a field by its CPU capability could expose unusable nested VMX features. Omitting a supported field breaks L1 hypervisors. Incorrect offsets corrupt VMCS12 state. Because the struct layout is migration ABI, offset changes are especially dangerous.

## Test Signals
Nested VMX selftests for VMREAD/VMWRITE of optional fields, feature-masked CPU models, migration of nested state, and host capability combinations cover this file. Build-time offset checks in `vmcs12.h` also protect the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.h

## Purpose
Defines KVM's emulated VMCS layout for nested VMX (`struct vmcs12`), migration-compatible offsets, revision/size constants, offset validation, and generic typed read/write helpers for VMCS12 fields.

## Important APIs, Types, And Functions
`struct vmcs12` is packed and contains the VMCS header, abort state, launch state, 64-bit controls/pointers, natural-width fields, 32-bit fields, and 16-bit selectors/status fields. `VMCS12_REVISION` and `VMCS12_SIZE` define nested VMX ABI. `vmx_check_vmcs12_offsets()` asserts fixed offsets. `get_vmcs12_field_offset()` validates and translates VMCS field encodings. `vmcs12_read_any()` and `vmcs12_write_any()` access fields according to VMCS width.

## Control Flow
L1 accesses VMCS12 through VMX instructions emulated by KVM. The nested VMX emulator decodes the VMCS field, calls `get_vmcs12_field_offset()`, and then reads or writes via the generic helpers. During nested run, VMCS12 is used to synthesize VMCS02 hardware state for L2. Offset checks protect build-time layout stability.

## State And Persistence
VMCS12 contents are guest-owned nested virtualization state stored in guest memory selected by VMPTRLD. The packed layout is explicitly migration ABI; existing field locations must not change. `launch_state` persists VMLAUNCH/VMCLEAR state. Padding areas are reserved for compatible expansion.

## Dependencies And Integration Points
Depends on `vmcs.h` for field width decoding and encoding-index mapping. Externs `vmcs12_field_offsets` and `nr_vmcs12_fields` are populated by `vmcs12.c`. Used broadly by nested VMX instruction emulation, state save/restore, and VMCS shadow support.

## Risks
Layout changes break save/restore and migration. Generic read/write helpers cast directly into packed storage, so offsets and widths must be correct. `get_vmcs12_field_offset()` uses nospec indexing to reduce speculative out-of-bounds risk; callers must still handle `-ENOENT`.

## Test Signals
Nested VMX state migration tests, VMCS12 offset build assertions, VMREAD/VMWRITE width tests, VMLAUNCH/VMCLEAR state tests, and L1/L2 nested boot tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs_shadow_fields.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs_shadow_fields.h

## Purpose
Defines the VMCS fields eligible for VMCS shadowing by invoking caller-provided `SHADOW_FIELD_RO` and `SHADOW_FIELD_RW` macros. It is an include-time table rather than a standalone header API.

## Important APIs, Types, And Functions
The file requires at least one of `SHADOW_FIELD_RO` or `SHADOW_FIELD_RW` to be defined and provides empty defaults for the other. It lists shadowed fields grouped by width: selected 16-bit fields, read-only VM-exit info, read/write execution and entry controls, natural-width guest/control fields, host FS/GS fields, and read-only guest physical address fields.

## Control Flow
Callers include this file with macros that generate enums, arrays, or handling code. Fields modified when L0 emulates VMX instructions are intentionally not shadowed because such changes would require extra shadow synchronization. The comments require shadowed fields to be synced by `prepare_vmcs02`, not only rare preparation paths.

## State And Persistence
The file itself has no storage. It defines the shadowed subset of VMCS12/VMCS fields that can be cached in hardware shadow VMCS state for nested VMX performance.

## Dependencies And Integration Points
Depends on VMCS field encoding symbols and `struct vmcs12` field names. Integrated by nested VMX shadow-VMCS code and VMCS12 generic read/write helpers.

## Risks
Adding a field that changes during L0 VMX instruction emulation can create stale shadow state. Removing a field can hurt nested VMX performance or alter VMREAD/VMWRITE interception. Field ordering by size is used for branch prediction expectations in generic accessors.

## Test Signals
Nested VMCS shadow tests, L1 VMREAD/VMWRITE behavior, VMX instruction failure paths, and L2 run preparation tests validate this table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs_shadow_fields.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmenter.S -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmenter.S

## Purpose
Provides the low-level assembly path for VMX guest entry and exit, plus IRQ-off event trampolines and a VMREAD error trampoline for compiler configurations without asm-goto output.

## Important APIs, Types, And Functions
Main symbols are `__vmx_vcpu_run`, global inner label `vmx_vmexit`, `vmx_do_nmi_irqoff`, optional `vmread_error_trampoline`, and optional `vmx_do_interrupt_irqoff`. `VMX_DO_EVENT_IRQOFF` builds synthetic IRQ/NMI frames. Register offset macros map KVM vCPU register indices to array offsets. The run path consumes flags from `run_flags.h`.

## Control Flow
`__vmx_vcpu_run(vmx, regs, flags)` saves callee-saved host registers, saves arguments on the stack, calls `vmx_update_host_rsp()`, optionally writes guest SPEC_CTRL before any unsafe return/indirect branch, loads guest GPRs from `regs`, executes required VERW buffer clearing based on CPU alternatives and flags, and chooses VMLAUNCH or VMRESUME. Successful VM-entry resumes at `vmx_vmexit` via VMCS HOST_RIP. The exit path saves guest GPRs back to `regs`, sets return value 0, clears guest GPR values from host registers, fills the RSB, restores host SPEC_CTRL, clears branch history, restores host registers, and returns. VM-fail/fixup paths set return value 1, except reboot fixups can tolerate instruction failure.

## State And Persistence
Guest register state is persisted through the caller-provided `regs` array. Host state is protected on the stack and through `vmx_update_host_rsp()` and `vmx_spec_ctrl_restore_host()`. SPEC_CTRL and branch-history/RSB mitigation state are transient but security-critical. RSP is intentionally omitted from software GPR save/restore because hardware switches it.

## Dependencies And Integration Points
Depends on generated KVM assembly offsets, x86 alternatives, speculation mitigation macros, VMX instructions, run flags, and external C helpers. `vmx_do_nmi_irqoff` and `vmx_do_interrupt_irqoff` integrate with IRQ/NMI handling paths that must run with interrupts disabled.

## Risks
This is a high-risk security and correctness path. Stack layout must match argument/flag offsets. There must be no return or indirect branch between SPEC_CTRL handling and VM-entry. Guest registers must be cleared after exit to avoid speculative use. Mitigation alternatives must match CPU vulnerability requirements. Objtool unwind hints and synthetic interrupt frames must remain correct across 32-bit/64-bit and FRED/non-FRED configurations.

## Test Signals
VMX smoke tests, nested VMX launch/resume tests, VM-fail injection, objtool validation, noinstr validation, speculation mitigation selftests, NMI/IRQ exit stress, reboot/kexec paths, and register-corruption tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmenter.S -->
