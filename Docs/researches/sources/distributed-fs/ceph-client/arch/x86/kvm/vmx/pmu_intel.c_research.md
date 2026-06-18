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
