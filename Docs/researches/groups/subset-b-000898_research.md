# subset-b-000898

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/tss.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/tss.h

## Purpose
`tss.h` declares the in-memory layouts KVM's x86 instruction emulator uses when emulating task-state-segment based task switches. It models the architectural 32-bit and 16-bit TSS formats closely enough for the emulator to read and write guest TSS memory while preserving field offsets mandated by the x86 architecture.

## Important APIs, Types, And Functions
The file exports only two structure definitions: `struct tss_segment_32` and `struct tss_segment_16`. The 32-bit layout contains the previous-task link, three privilege stack pairs, `cr3`, saved instruction pointer and flags, general-purpose registers, segment selectors, LDT selector, debug-trap bit, and I/O bitmap offset. The 16-bit layout contains the corresponding 16-bit task link, privilege stacks, saved IP/FLAGS, general registers, segment selectors, and LDT selector. There are no functions, macros, or inline helpers in this header.

## Control Flow
There is no local executable control flow. Runtime behavior is driven by consumers in `arch/x86/kvm/emulate.c`, which allocate these structs on the stack, fetch guest TSS bytes into them, update task-switch state, and write the modified task image back to guest memory. `offsetof(struct tss_segment_32, eip)` and `offsetof(struct tss_segment_32, ldt_selector)` are used by emulator logic, so member order is a hard ABI with the guest architectural format.

## State And Persistence
The structs represent persisted guest architectural state, not host-owned persistent state. KVM copies guest memory into these layouts during emulation and may write modified state back to guest memory. Any padding introduced by the compiler would be risky; the current field sequence uses naturally aligned 32-bit or 16-bit members and relies on the standard C layout matching the architecture.

## Dependencies And Integration Points
The header depends on Linux integer typedefs (`u16`, `u32`) being available through includers. Its main integration point is the x86 emulator task-switch path, including helpers that read/write 16-bit and 32-bit TSS images and validate segment/TSS descriptors.

## Risks And Edge Cases
The largest risk is silent layout drift: changing field type, order, or implicit packing assumptions can corrupt guest task switches. The 32-bit TSS includes an `io_map` offset, while the 16-bit TSS does not; consumers must select the right structure based on descriptor type. Emulation paths also need robust bounds checks when guest memory provides an incomplete TSS or malicious descriptor limit.

## Test Signals
Useful signals are KVM emulator tests for far `JMP`/`CALL`/`IRET` task switches, nested task return, 16-bit protected-mode task switches, privilege-stack loading, LDT selector propagation, debug-trap handling, and failure injection for too-small TSS limits or unreadable guest TSS memory. Build-time offset checks would be valuable if not already covered elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/tss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/capabilities.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/capabilities.h

## Purpose
`vmx/capabilities.h` centralizes Intel VMX capability state and inline feature predicates for the VMX backend. It turns raw VMX MSR-derived configuration (`vmcs_config`) and EPT/VPID capability bits (`vmx_capability`) into readable gates used across VMX setup, nested VMX, VMCS access, APIC virtualization, tracing, memory management, and feature exposure.

## Important APIs, Types, And Functions
`struct nested_vmx_msrs` stores the "true" nested VMX control MSR masks, fixed CR0/CR4 masks, VMCS enum data, VMFUNC controls, EPT caps, VPID caps, basic/misc data, and related fields exposed to L1 guests. `struct vmcs_config` stores host-selected VM execution, entry, exit, and misc controls plus nested capability MSRs. `struct vmx_capability` stores EPT and VPID capability words. The file declares `vmcs_config` and `vmx_capability` as `__ro_after_init`, alongside module-tunable booleans such as `enable_vpid`, `enable_ept`, `enable_unrestricted_guest`, `enable_ept_ad_bits`, `enable_cet`, `enable_pml`, and `pt_mode`.

The many `cpu_has_*()` helpers gate individual VMX features: pin controls such as virtual NMIs, preemption timer, and posted interrupts; primary/secondary/tertiary execution controls such as MSR bitmaps, EPT, VPID, RDTSCP, APIC virtualization, PLE, VMFUNC, shadow VMCS, SGX ENCLS exiting, XSAVES, waitpkg, TSC scaling, bus-lock detection, IPI virtualization, and notify VM exits; VM-entry/exit controls for EFER, perf global control, CET, BNDCFGS; and EPT/VPID invalidation extents and page-size support. `cpu_need_tpr_shadow()` adds the vCPU-local dependency that in-kernel LAPIC must be active. `ept_caps_to_lpage_level()` converts EPT large-page caps to KVM page levels. `vmx_pebs_supported()` combines CPU PEBS support, PMU EPT capability, and mediated PMU exclusion.

## Control Flow
The header is all inline predicate logic. Most helpers directly test one bit in initialized global capability state, while compound helpers enforce multi-bit contracts, for example APICv requires APIC-register virtualization, virtual-interrupt delivery, and posted interrupts. Feature setup code in `vmx.c` fills `vmcs_config` and then later uses these helpers to enable or disable KVM capabilities, operation hooks, CPUID exposure, and nested VMX MSR masks.

## State And Persistence
Persistent state is the post-initialization global VMX capability snapshot. The globals are read-mostly or `__ro_after_init`, so runtime code assumes they are stable after hardware setup. `pt_mode` remains the selected Intel Processor Trace mode. No per-vCPU state is stored here except through helper parameters such as `cpu_need_tpr_shadow(vcpu)`.

## Dependencies And Integration Points
The header depends on `<asm/vmx.h>` control bit definitions and KVM x86 headers for LAPIC, CPUID, PMU, paging levels, and CPU feature tests. It is widely consumed by `vmx.c`, `nested.c`, `vmcs12.c`, SGX handling, TDX setup, VMX ops helpers, and VMX-on-Hyper-V sanitization. Nested VMX support depends on `nested_vmx_msrs` to present a coherent virtual VMX capability set to L1.

## Risks And Edge Cases
Incorrect predicates can expose unsupported hardware behavior to guests or disable valid acceleration paths. Compound helpers must stay aligned with Intel SDM requirements; e.g. APICv and shadow-VMCS support depend on multiple controls, not one raw bit. `vmx_umip_emulated()` deliberately treats lack of hardware UMIP plus descriptor-table exiting as an emulated capability. `vmx_pebs_supported()` must not enable PEBS when mediated PMU is active. Any initialization path that mutates `vmcs_config` after consumers cache decisions would be risky.

## Test Signals
Signals include module initialization on CPUs with varied VMX MSR capabilities, nested VMX selftests that read VMX MSRs and attempt controls, APICv/posted interrupt tests, EPT and VPID invalidation tests, Intel PT and PEBS capability exposure tests, SGX/ENCLS exiting tests, TSC scaling and bus-lock detection tests, and negative tests where module parameters disable EPT, VPID, unrestricted guest, PML, or CET.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/capabilities.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/common.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/common.h

## Purpose
`vmx/common.h` contains small pieces shared by Intel VMX and TDX-backed execution paths: VM-exit reason decoding, the common `vcpu_vt` state embedded in both VMX and TDX vCPU structs, TDX type predicates, EPT-violation translation, and posted-interrupt delivery helpers.

## Important APIs, Types, And Functions
`union vmx_exit_reason` exposes the raw 32-bit VM-exit reason and named bits including `basic`, bus-lock detection, enclave mode, SMI indicators, and failed VM-entry. `struct vcpu_vt` stores the posted-interrupt descriptor, PI wakeup list node, last exit reason, qualification, interrupt info, guest-state-loaded flag, emulation-required flag, and host kernel GS base on x86-64. With `CONFIG_KVM_INTEL_TDX`, `is_td()` and `is_td_vcpu()` classify TD VMs; otherwise they compile to false.

`vt_is_tdx_private_gpa()` interprets a GPA as private for TDX using KVM's direct/shared address mask. `__vmx_handle_ept_violation()` converts EPT violation qualification bits into KVM page-fault error flags, including read/write/fetch, present/protection, guest page versus final translation, and private access, then calls `kvm_mmu_page_fault()`. `kvm_vcpu_trigger_posted_interrupt()` chooses between sending a posted-interrupt notification IPI to an in-guest vCPU or waking a non-running/blocking vCPU. `__vmx_deliver_posted_interrupt()` sets the PIR bit, sets PID.ON if needed, and triggers notification.

## Control Flow
EPT violation handling is a straight qualification-to-error-code translation followed by MMU fault dispatch. Posted interrupt delivery is more stateful: first set the target vector in PIR; if it was already pending, return. Then set PID.ON; if another notification is already in flight, return. Otherwise, if the vCPU is in guest mode and not the current running vCPU, send the posted-interrupt IPI; if it is not in guest mode, wake it so normal vCPU entry can sync PIR into vIRR.

## State And Persistence
`vcpu_vt` persists per-vCPU posted-interrupt state and the latest VM-exit metadata. Posted interrupts modify the `pi_desc` bitmap and ON bit, which are consumed by APIC/vCPU entry paths. `guest_state_loaded` tracks whether hardware currently contains guest or host state. EPT handling does not persist local state but may update MMU state through `kvm_mmu_page_fault()`.

## Dependencies And Integration Points
The file depends on KVM host definitions, posted interrupt primitives, and VMX MMU constants. It integrates with VMX/TDX vCPU structs via common offset requirements, APIC posted-interrupt code, vCPU wake/block logic, EPT MMU fault handling, and NMI handling through the external `vmx_handle_nmi()` declaration.

## Risks And Edge Cases
Posted-interrupt ordering is concurrency-sensitive. The barrier implied by `pi_test_and_set_on()` must pair with mode transitions in `vcpu_enter_guest()` so a missed IPI still leaves a visible pending interrupt. Sending an IPI to the currently running vCPU is intentionally avoided because the fastpath will sync PIR before reentry. For TDX, classifying private GPAs incorrectly would produce wrong MMU error codes and could confuse shared/private memory handling. EPT qualification bit mapping must remain aligned with KVM page-fault semantics.

## Test Signals
Coverage should include EPT violation tests for read, write, execute, permission, translated-GVA, and private/shared GPA cases; APICv posted-interrupt delivery to running, non-running, blocking, and current vCPU cases; SMP and !SMP builds; TDX private memory fault tests; and stress tests for interrupt races around vCPU mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.c

## Purpose
`vmx/hyperv.c` implements VMX-specific Hyper-V enlightened VMCS support for nested virtualization. It reads the guest Hyper-V VP assist page's current eVMCS pointer, reports supported eVMCS versions, filters virtual VMX control MSRs to the subset representable by eVMCS v1, validates nested VMCS controls under eVMCS, enables eVMCS per vCPU, and supports Hyper-V direct TLB-flush enlightenment for L2.

## Important APIs, Types, And Functions
`nested_get_evmptr()` returns the current nested eVMCS GPA from `hv_vcpu->vp_assist_page.current_nested_vmcs`, but only after ensuring the assist page can be read and enlightened VM-entry is enabled. `nested_get_evmcs_version()` returns a min/max version range encoded in a 16-bit value, currently versions 1 through `KVM_EVMCS_VERSION`, when VMX is available and the vCPU has eVMCS enabled if a vCPU is supplied.

Local enums define an eVMCS revision (`EVMCSv1_LEGACY`) and control classes (`EVMCS_EXIT_CTRLS`, `EVMCS_ENTRY_CTRLS`, `EVMCS_EXEC_CTRL`, secondary, tertiary, pin, and VMFUNC). `evmcs_supported_ctrls` maps those classes to the masks from `hyperv_evmcs.h`; secondary controls deliberately clear `SECONDARY_EXEC_TSC_SCALING` for exposed nested eVMCS controls. `nested_evmcs_filter_control_msr()` masks VMX MSR low/high words so Hyper-V guests do not try to use VMCS fields absent from eVMCS. It also hides perf global control unless the Hyper-V nested CPUID bit `HV_X64_NESTED_EVMCS1_PERF_GLOBAL_CTRL` is present. `nested_evmcs_check_controls()` rejects unsupported nested VMCS controls with `-EINVAL` and KVM nested consistency-check annotations. `nested_enable_evmcs()` sets `vmx->nested.enlightened_vmcs_enabled` and optionally returns the supported version range. `nested_evmcs_l2_tlb_flush_enabled()` checks the mapped eVMCS enlightenment bit and the VP assist page's direct-hypercall feature. `vmx_hv_inject_synthetic_vmexit_post_tlb_flush()` causes a synthetic nested VM exit after flush.

## Control Flow
The eVMCS activation flow starts in KVM's Hyper-V enable path, which calls `nested_enable_evmcs()`. CPUID/MSR paths call `nested_get_evmcs_version()` and `nested_evmcs_filter_control_msr()` to advertise only valid controls. During nested VM-entry, `nested.c` maps the GPA from `nested_get_evmptr()`, copies eVMCS content into `vmcs12`, and invokes `nested_evmcs_check_controls()`. On L2 TLB flush paths, nested VMX checks `nested_evmcs_l2_tlb_flush_enabled()` and may inject the synthetic post-flush VM exit.

## State And Persistence
This file mutates only `vcpu_vmx.nested.enlightened_vmcs_enabled`; the eVMCS pointer, mapped page, and VP assist state are stored elsewhere in `vcpu_vmx.nested` and `kvm_vcpu_hv`. The static supported-control table is immutable. The VP assist page content is guest/Hyper-V shared state and can change across entries or after migration, so callers must revalidate mapping and version.

## Dependencies And Integration Points
The implementation depends on KVM Hyper-V helpers, CPUID cache state, nested VMX, VMCS definitions, eVMCS masks from `hyperv_evmcs.h`, and trace/consistency-check infrastructure. Integration points include `x86.c`'s Hyper-V eVMCS enable ioctl/MSR path, `arch/x86/kvm/hyperv.c` CPUID generation, `vmx.c` feature MSR reads, and `nested.c` eVMCS mapping, control checks, direct flush handling, and synthetic VM exits.

## Risks And Edge Cases
The filter must match the actual eVMCS field map; advertising unsupported controls can make Hyper-V write fields KVM cannot translate. Hiding perf global control without the companion CPUID bit is a Windows compatibility quirk and should not be removed casually. `nested_get_evmptr()` returns invalid when the assist page cannot be read or enlightened entry is disabled, which disables eVMCS rather than failing all nested VMX. Version encoding is min/max in one word, so consumers must not treat it as a single revision. TLB-flush enlightenment depends on both eVMCS control and VP assist direct-hypercall state, including after migration.

## Test Signals
Useful tests include Hyper-V CPUID eVMCS version exposure, enabling eVMCS through KVM nested ops, reading VMX control MSRs with and without eVMCS and perf-global-control CPUID bit, nested VM-entry rejection of unsupported eVMCS controls, valid L2 launch through eVMCS, migration with remapped eVMCS, direct TLB-flush enlightenment and synthetic VM-exit delivery, and cases where the VP assist page is missing or `enlighten_vmentry` is clear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.h

## Purpose
`vmx/hyperv.h` declares VMX Hyper-V enlightened VMCS interfaces and provides inline helpers for eVMCS pointer state. It is the compile-time boundary between common nested VMX code and optional `CONFIG_KVM_HYPERV` support.

## Important APIs, Types, And Functions
`EVMPTR_INVALID` marks no valid eVMCS pointer and `EVMPTR_MAP_PENDING` marks a restored or deferred state where the GPA is known to require remapping before use. `enum nested_evmptrld_status` reports whether eVMCS loading is disabled, succeeded, failed architecturally, or failed due to a host mapping error.

With `CONFIG_KVM_HYPERV`, `evmptr_is_valid()` rejects invalid and map-pending sentinels, while `evmptr_is_set()` rejects only invalid. `nested_vmx_is_evmptr12_valid()` and `nested_vmx_is_evmptr12_set()` apply those tests to `vmx->nested.hv_evmcs_vmptr`. `nested_vmx_evmcs()` returns the mapped `struct hv_enlightened_vmcs *`. `guest_cpu_cap_has_evmcs()` exposes eVMCS to a vCPU only when Hyper-V CPUID is enabled and userspace explicitly enabled enlightened VMCS. The header declares `nested_get_evmptr()`, `nested_get_evmcs_version()`, `nested_enable_evmcs()`, `nested_evmcs_filter_control_msr()`, `nested_evmcs_check_controls()`, `nested_evmcs_l2_tlb_flush_enabled()`, and `vmx_hv_inject_synthetic_vmexit_post_tlb_flush()`.

When Hyper-V support is not compiled, the inline helpers compile to false or NULL and no function declarations are provided for the implementation-only operations.

## Control Flow
This header does not run complex control flow; it controls feature reachability. Nested VMX paths first check whether guest eVMCS capability is enabled, then use pointer-state helpers to decide whether an existing mapping can be used, needs mapping, or should be treated as absent. The non-Hyper-V stubs allow the same broader VMX code to compile out eVMCS paths.

## State And Persistence
The state represented here lives in `struct vcpu_vmx.nested`: the eVMCS GPA sentinel/value, host map, mapped pointer, and `enlightened_vmcs_enabled`. `EVMPTR_MAP_PENDING` is important for persistence across migration or state restore because it distinguishes "feature enabled but mapping not restored yet" from "no eVMCS".

## Dependencies And Integration Points
The header depends on KVM host types, `vmcs12.h`, and `vmx.h` for `struct vcpu_vmx`. It is included by nested VMX, VMX MSR handling, and Hyper-V eVMCS implementation code. It integrates with `arch/x86/kvm/hyperv.c` for CPUID/version exposure and with `nested.c` for `EVMPTRLD`-like mapping and release.

## Risks And Edge Cases
Confusing "set" and "valid" pointer semantics can break migration and lazy mapping: `EVMPTR_MAP_PENDING` is set but not valid. `guest_cpu_cap_has_evmcs()` requires both Hyper-V enabled in CPUID and userspace opt-in; bypassing either check would expose eVMCS unexpectedly. The !`CONFIG_KVM_HYPERV` stubs intentionally return false, so code that expects declarations must remain compiled under the same config guard.

## Test Signals
Test signals include builds with and without `CONFIG_KVM_HYPERV`, eVMCS enable/disable through userspace, nested VMX migration that restores `EVMPTR_MAP_PENDING`, nested VMCLEAR/VM-entry paths for valid and invalid eVMCS pointers, and CPUID combinations where Hyper-V is disabled even though VMX exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.c

## Purpose
`vmx/hyperv_evmcs.c` defines the translation table from architectural VMCS field encodings to offsets in Hyper-V's `struct hv_enlightened_vmcs` v1 layout. The table is shared by KVM running on Hyper-V, where VMCS reads/writes are redirected into an enlightened VMCS, and by nested VMX code translating an L1 Hyper-V guest's eVMCS into KVM's `vmcs12`.

## Important APIs, Types, And Functions
The file defines two macros: `EVMCS1_OFFSET(x)` wraps `offsetof(struct hv_enlightened_vmcs, x)`, and `EVMCS1_FIELD(number, name, clean_field)` installs an `evmcs_field` entry indexed by `ENC_TO_VMCS12_IDX(number)`. The exported `vmcs_field_to_evmcs_1[]` array maps many 64-bit, 32-bit, and 16-bit VMCS fields to eVMCS offsets and Hyper-V clean-field masks. `nr_evmcs_1_fields` exports the array size for bounds checking in `evmcs_field_offset()`.

Mapped fields include guest/host RIP/RSP/RFLAGS, host and guest PAT/EFER/perf global controls, CR0/CR3/CR4/DR7, SYSENTER fields, IO/MSR bitmaps, segment bases/limits/access rights/selectors, descriptor table bases/limits, TSC offset/multiplier, APIC page, VMCS link pointer, PDPTRs, guest pending debug exceptions, EPT pointer, XSS and ENCLS bitmaps, exit qualification and physical/linear addresses, VM-exit and VM-entry event fields, VM instruction error, exit reason, instruction length, pin/primary/secondary controls, TPR threshold, page-fault masks, CR3 target/MSR load-store counts, host selectors, guest selectors, and VPID. Several newer CET/LBR fields are listed as not used by KVM.

## Control Flow
There is no dynamic control flow beyond static initialization. At runtime, readers call `evmcs_field_offset()` from `hyperv_evmcs.h`, which indexes this table by encoded VMCS field. KVM-on-Hyper-V accessors use the returned offset to load/store the current eVMCS and clear the appropriate clean-field bit. Nested VMX code uses the same mapping to read arbitrary eVMCS fields or copy clean groups.

## State And Persistence
The table is immutable kernel data. The clean-field mask associated with each entry determines how writes invalidate Hyper-V's clean-state cache in the live eVMCS page. Entries using `HV_VMX_ENLIGHTENED_CLEAN_FIELD_ALL` represent fields without a spec-defined specific clean mask and force broad invalidation. Offset zero is reserved by lookup code to mean "hole" because `revision_id` has no VMCS encoding and lives at offset zero.

## Dependencies And Integration Points
The implementation depends on `hyperv_evmcs.h`, which brings in Hyper-V HVDK eVMCS definitions, VMCS field encodings, and `struct evmcs_field`. It integrates with `vmx_onhyperv.h` eVMCS read/write paths, `nested.c` eVMCS copy paths, and any code that needs to translate standard VMCS encodings to enlightened layout.

## Risks And Edge Cases
The translation table is a correctness-critical ABI map. A wrong offset can corrupt eVMCS state; a wrong clean mask can make Hyper-V or KVM reuse stale fields. Unsupported VMCS fields must remain holes so lookup returns `-ENOENT`; accidentally mapping a field absent from eVMCS v1 would falsely expose support. The table includes `TSC_MULTIPLIER` even though nested eVMCS control filtering clears TSC scaling for guest controls, so consumers must distinguish field layout from feature exposure. The offset-zero hole convention means no encoded VMCS field can validly map to offset zero.

## Test Signals
Useful signals are compile-time layout checks against `struct hv_enlightened_vmcs`, VMCS read/write tests while KVM runs on Hyper-V, nested Hyper-V eVMCS launch tests, clean-field invalidation tests for each major group, unsupported-field lookup tests, migration tests preserving eVMCS data, and comparison tests between VMCS12 copy behavior and expected eVMCS field values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.h

## Purpose
`vmx/hyperv_evmcs.h` defines the shared contract for Hyper-V Enlightened VMCS v1 support. It declares eVMCS versioning, enumerates which VMX controls are representable by eVMCS v1, exposes the VMCS-field-to-eVMCS translation table, and provides inline helpers for offset lookup and typed field reading.

## Important APIs, Types, And Functions
`KVM_EVMCS_VERSION` is currently `1`. The `EVMCS1_SUPPORTED_*` masks define the VMX pin, primary execution, secondary execution, tertiary execution, VM-exit, VM-entry, and VMFUNC controls usable with eVMCS v1. Comments list VMCS fields not supported by eVMCS v1, such as posted-interrupt descriptor fields, APIC access address, EOI bitmaps, PML fields, VMFUNC/EPTP list fields, VMREAD/VMWRITE bitmaps, preemption timer, PLE fields, and some tracing fields.

`struct evmcs_field` stores an eVMCS byte offset and a Hyper-V clean-field mask. `vmcs_field_to_evmcs_1[]` and `nr_evmcs_1_fields` are defined in `hyperv_evmcs.c`. `evmcs_field_offset()` converts an encoded VMCS field to an array index with `ENC_TO_VMCS12_IDX()`, rejects out-of-range or hole entries, optionally returns the clean-field mask, and returns the eVMCS offset. `evmcs_read_any()` reuses `vmcs12_read_any()` against an eVMCS pointer because it accepts an explicit offset and field encoding.

## Control Flow
Feature filtering code uses the supported-control masks to hide VMX features that Hyper-V eVMCS cannot carry. VMCS access code calls `evmcs_field_offset()` before every redirected field access. If lookup fails, the caller treats the field as unsupported for eVMCS. Successful writes use the returned clean-field mask to invalidate Hyper-V clean groups; reads use the offset directly. `evmcs_read_any()` is used by nested VMX when an arbitrary field encoding needs to be read from the mapped eVMCS page.

## State And Persistence
The header itself stores no mutable state. It defines the static ABI between KVM and `struct hv_enlightened_vmcs`. Runtime state lives in the eVMCS page, especially `hv_clean_fields`, which tracks which groups Hyper-V may treat as unchanged. The control masks also define persistent guest-visible nested VMX capability behavior once exposed through CPUID/MSRs.

## Dependencies And Integration Points
The file depends on Hyper-V HVDK definitions (`<hyperv/hvhdk.h>`), `capabilities.h`, and `vmcs12.h`. It is consumed by `hyperv.c`, `hyperv_evmcs.c`, `vmx_onhyperv.h`, nested VMX copy/validation code, and VMX-on-Hyper-V setup that sanitizes VMCS controls to the eVMCS-supported subset.

## Risks And Edge Cases
The supported-control masks must agree with the field map and Hyper-V behavior. Exposing a control without a corresponding eVMCS field can break nested Hyper-V guests. Some fields are present in the structure but not used by KVM; future feature work must add both table entries and control validation deliberately. `evmcs_field_offset()` relies on offset zero as a hole marker because `revision_id` is not VMCS-encoded. Callers must handle `-ENOENT` and must not access eVMCS memory after failed lookup.

## Test Signals
Signals include VMX control MSR filtering tests, eVMCS field lookup tests for supported and unsupported encodings, KVM-on-Hyper-V boot and nested virtualization tests, clean-field update tests, CPUID eVMCS version tests, and nested Hyper-V L1 tests that attempt unsupported controls such as posted interrupts, PML, VMFUNC controls, and preemption timer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/main.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/main.c

## Purpose
`vmx/main.c` is the Intel KVM backend module entry point and operation table definition. When TDX is enabled, it provides a VT dispatch layer that routes each KVM x86 operation to either classic VMX or TDX based on VM/vCPU type. When TDX is not compiled, the same table aliases directly to VMX functions.

## Important APIs, Types, And Functions
Under `CONFIG_KVM_INTEL_TDX`, the file defines many `vt_*` wrappers. VM and vCPU lifecycle wrappers include `vt_hardware_setup()`, `vt_hardware_unsetup()`, `vt_disable_virtualization_cpu()`, `vt_vm_init()`, `vt_vm_pre_destroy()`, `vt_vm_destroy()`, `vt_vcpu_precreate()`, `vt_vcpu_create()`, `vt_vcpu_free()`, `vt_vcpu_reset()`, `vt_vcpu_load()`, `vt_vcpu_put()`, `vt_vcpu_pre_run()`, and `vt_vcpu_run()`. Runtime wrappers cover exit handling, MSR access, intercept recalculation, instruction emulation checks, APIC and interrupt operations, segment/control/debug register access, descriptor tables, TLB flushes, NMI/IRQ/exception injection, MMU root loading, Hyper-V timer, machine-check setup, TSS and identity-map addresses, TSC offset/multiplier, memory-encryption ioctls, and guest-memory mapping level.

`VMX_REQUIRED_APICV_INHIBITS` enumerates APICv inhibit reasons required by VMX: disabled, absent, Hyper-V, blocked IRQ, physical ID aliasing, APIC ID modified, and APIC base modified. `vt_x86_ops` fills `struct kvm_x86_ops` with VMX/TDX dispatch functions and feature hooks. `vt_init_ops` fills `struct kvm_x86_init_ops` with hardware setup, PMU ops, and the runtime ops table. `vt_init()` calls `vmx_init()`, sizes the vCPU cache for the larger of VMX and TDX structs when needed, marks TDX VM type support, then calls `kvm_init()`. `vt_exit()` calls `kvm_exit()` and `vmx_exit()`.

## Control Flow
Module initialization starts in `vt_init()`: initialize VMX, adjust vCPU allocation metadata for TDX, expose TDX VM type if enabled, and register KVM only after hardware/backend setup is ready because `/dev/kvm` becomes visible. Hardware setup later calls either `vmx_hardware_setup()` alone or VMX followed by TDX hardware setup. Runtime KVM calls enter `vt_x86_ops`; each wrapper checks `is_td()` or `is_td_vcpu()` and selects TDX behavior, VMX behavior, a harmless no-op, or an error where the operation is invalid for TDs. On module exit, common KVM teardown precedes VMX teardown.

## State And Persistence
This file owns static operation table state in `vt_x86_ops` and `vt_init_ops`, both `__initdata`, and mutates global KVM capability state by setting `kvm_caps.supported_vm_types` when TDX is enabled. It does not own per-vCPU state; wrappers delegate to VMX or TDX implementations. For TD guests, many architectural reads return zero or operations become no-ops because guest state is protected or managed by the TDX module rather than directly visible to KVM.

## Dependencies And Integration Points
The file includes VMX, MMU, nested VMX, PMU, posted interrupt, and TDX headers. It is integrated with core KVM through `kvm_x86_ops` and `kvm_x86_init_ops`, module init/exit, Intel PMU ops, nested VMX ops, posted interrupt hooks, Hyper-V timer hooks, SMM hooks under `CONFIG_KVM_SMM`, and TDX memory-encryption ioctls. `tdx.c` can further patch `vt_x86_ops` for TDX-specific private-memory operations during TDX setup.

## Risks And Edge Cases
Dispatch correctness is the primary risk. Operations that are impossible or unsafe for TD guests must not fall through to VMX, because TD guest state and memory are protected. Conversely, returning zero/no-op for TDs must match core KVM expectations; a wrong default can hide bugs or cause guest-visible state loss. Initialization order is sensitive: `kvm_init()` must remain last because it exposes `/dev/kvm`. vCPU cache sizing must cover both `struct vcpu_vmx` and `struct vcpu_tdx`. APICv inhibit masks must stay synchronized with VMX APIC virtualization requirements. Several wrappers use `KVM_BUG_ON`/`WARN_ON_ONCE` for paths that should never target TDs, which are good test signals but also indicate invariants relied on by core KVM.

## Test Signals
Useful tests include VMX module load/unload, TDX-enabled and TDX-disabled builds, creation of normal VMX VMs and TD VMs, vCPU lifecycle and run loops for both types, MSR get/set dispatch tests, interrupt/NMI/APIC behavior for TD and non-TD VMs, SMM tests confirming TD paths are blocked, TLB flush and MMU root load tests, Hyper-V timer rejection for TDs, memory-encryption ioctl routing, `/dev/kvm` exposure after successful init only, and regression tests for vCPU allocation size/alignment when TDX support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/main.c -->
