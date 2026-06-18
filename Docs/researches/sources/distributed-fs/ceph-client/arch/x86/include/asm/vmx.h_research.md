# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmx.h

Purpose: Central x86 Intel VMX hardware definition header. It provides VMCS layouts, control-bit masks, VMX capability decoders, VMCS field encodings, exit qualification masks, EPT/VPID constants, error numbers, mitigation state, and #VE information structures used primarily by KVM and nested virtualization code.

Important APIs/types/functions: `struct vmcs_hdr` and `struct vmcs` model VMCS memory. `VMCS_CONTROL_BIT()` maps `VMX_FEATURE_*` numbers to control masks. Control constants cover primary, secondary, tertiary, pin-based, VM-exit, VM-entry, and VMFUNC controls. Inline decoders parse `IA32_VMX_BASIC` and `IA32_VMX_MISC` values: `vmx_basic_vmcs_revision_id()`, `vmx_basic_vmcs_size()`, `vmx_basic_vmcs_mem_type()`, `vmx_basic_encode_vmcs_info()`, `vmx_misc_preemption_timer_rate()`, `vmx_misc_cr3_count()`, `vmx_misc_max_msr()`, and `vmx_misc_mseg_revid()`. `enum vmcs_field` is the VMREAD/VMWRITE encoding list for guest/host state, controls, bitmaps, EPT, posted interrupts, CET fields, and more. EPT helpers include `vmx_eptp_page_walk_level()` and `EPT_VIOLATION_RWX_TO_PROT()`. `struct vmx_msr_entry`, `enum vm_entry_failure_code`, `enum vm_instruction_error_number`, `VMX_VMENTER_INSTRUCTION_ERRORS`, `enum vmx_l1d_flush_state`, `l1tf_vmx_mitigation`, and `struct vmx_ve_information` define supporting data.

Control flow: This header supplies constants used by VMX setup and VM-exit handling. KVM reads VMX MSRs, builds allowed control masks, writes VMCS fields by enum value, decodes exit qualification using masks, validates EPTP page-walk level, reports VM-instruction errors, and applies L1TF mitigation state during vmentry.

State and persistence: VMCS memory persists per VM/vCPU. MSR entry arrays persist for VM-entry/exit load-store lists. The external `l1tf_vmx_mitigation` records the global L1D flush policy. Most definitions are stateless hardware encodings.

Dependencies and integration points: Depends on bitops, bug checks, types, UAPI VMX definitions, trap numbers, and `vmxfeatures.h`. Integrated with KVM VMX, nested VMX, EPT MMU code, APIC virtualization, posted interrupts, Intel PT, CET, SGX exits, and mitigation code.

Risks: Constants are hardware ABI. Incorrect control bits or VMCS encodings can cause VM-entry failure, guest corruption, or host instability. `vmx_eptp_page_walk_level()` assumes prevalidated EPTP and only warns on unexpected values. EPT violation bit translations are guarded by `static_assert`, which is an important compile-time safety signal.

Test signals: KVM unit tests, VMX capability selftests, nested-VMX tests, EPT violation/MMIO tests, vmentry failure trace coverage, APICv/posted interrupt tests, and boot/runtime tests across Intel CPUs with different VMX feature sets.
