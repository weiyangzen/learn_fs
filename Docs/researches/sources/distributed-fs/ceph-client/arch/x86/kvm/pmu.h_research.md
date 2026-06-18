# sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.h

## Purpose
Defines common PMU helpers, vendor operation table, counter indexing conventions, inline counter read/enabled logic, and public common PMU APIs for KVM x86.

## Important APIs, Types, and Functions
- `struct kvm_pmu_ops` abstracts vendor differences for PMC lookup, MSR handling, refresh/init/reset, PMI delivery, mediated PMU hooks, and register layout constants.
- Index helpers map vCPU/PMU/PMC relationships and fixed counter fields.
- `kvm_pmu_has_perf_global_ctrl()` determines v2+ global-control exposure.
- `kvm_vcpu_has_mediated_pmu()` gates mediated PMU usage.
- `kvm_pmc_idx_to_pmc()` and `kvm_for_each_pmc()` iterate common GP/fixed counter bitmaps.
- `pmc_read_counter()`, `pmc_bitmask()`, `pmc_is_gp()`, `pmc_is_fixed()`, `pmc_is_locally_enabled()`, `pmc_is_globally_enabled()`, and `kvm_pmu_is_fastpath_emulation_allowed()` provide shared inline state checks.
- Declares common PMU lifecycle, MSR, RDPMC, filtering, emulated event, mediated PMU, and intercept-decision functions.

## Control Flow
Backend modules provide a `kvm_pmu_ops` table, common code updates static calls, and generic PMU paths use inline helpers to select counters, test local/global enablement, request reprogramming, and decide if hardware intercepts can be disabled. `pmc_read_counter()` reads from mediated state directly or combines stored offset, emulated count, and perf event count for perf-backed PMUs.

## State and Persistence
The header defines interpretation of persistent per-vCPU `struct kvm_pmu` and `struct kvm_pmc` state: bitmaps use indices 0-31 for GP counters and 32+ for fixed counters, counters are masked by type bit width, reprogram requests persist in bitmaps, and mediated PMU state is distinguished from perf-backed emulation.

## Dependencies and Integration Points
Includes `linux/nospec.h` for speculation-safe array indexing and `asm/kvm_host.h` for PMU structs. Integrated by Intel/AMD PMU backends, common PMU code, MSR dispatch, RDPMC intercept policy, emulator instruction accounting, perf-backed counters, and mediated PMU vendor code.

## Risks
Counter-index conventions are subtle: internal fixed counters use index 32+, while guest RDPMC uses bit 30 encoding. Misusing `kvm_pmc_idx_to_pmc()` for raw guest ECX would be wrong. Fastpath emulation decisions must account for mediated PMU hardware counting to avoid double-counting. Vendor ops are required for most paths; missing static-call functions trigger WARNs.

## Test Signals
Build tests for Intel and AMD ops, fixed/GP counter mapping, RDPMC guest index conversion in backends, global-control gating by PMU version, mediated PMU enablement, fastpath emulation disablement when hardware counts instructions, and speculation-safe PMC MSR lookup.
