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
