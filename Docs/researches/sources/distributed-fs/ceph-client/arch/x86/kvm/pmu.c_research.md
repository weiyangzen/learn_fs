# sources/distributed-fs/ceph-client/arch/x86/kvm/pmu.c

## Purpose
Implements common x86 virtual PMU support for KVM across Intel and AMD backends. It manages host/KVM PMU capabilities, perf-backed virtual counters, mediated PMU pass-through, PMIs, event filtering, RDPMC, global control/status MSRs, emulated instruction/branch events, cleanup, and guest PMU load/put.

## Important APIs, Types, and Functions
- Global capability state: `kvm_host_pmu`, exported `kvm_pmu_cap`, and emulated event selectors.
- `kvm_pmu_ops_update()` wires vendor PMU ops into static calls.
- `kvm_init_pmu_capability()` derives KVM-exposed PMU caps from host perf caps and module policy.
- Perf event lifecycle: `pmc_reprogram_counter()`, `pmc_pause_counter()`, `pmc_resume_counter()`, `pmc_release_perf_event()`, `pmc_stop_counter()`, and `pmc_write_counter()`.
- Event filtering: filter validation/conversion/sorting, `pmc_is_event_allowed()`, and `kvm_vm_ioctl_set_pmu_event_filter()`.
- Runtime handling: `kvm_pmu_handle_event()`, `kvm_pmu_rdpmc()`, `kvm_pmu_get_msr()`, `kvm_pmu_set_msr()`, `kvm_pmu_refresh()`, `kvm_pmu_init()`, `kvm_pmu_cleanup()`, `kvm_pmu_destroy()`.
- Emulated events: `kvm_pmu_instruction_retired()` and `kvm_pmu_branch_retired()`.
- Mediated PMU: `kvm_handle_guest_mediated_pmi()`, `kvm_mediated_pmu_load()`, and `kvm_mediated_pmu_put()`.

## Control Flow
Initialization reads perf PMU capabilities unless PMU is disabled or the host is hybrid, clamps capability exposure, records raw event encodings, and disables mediated PMU if unsupported. Guest writes to PMU MSRs update common state or delegate to vendor ops, then request counter reprogramming. `kvm_pmu_handle_event()` consumes the reprogram bitmap, reprograms or resumes perf events, performs cleanup, and refreshes emulation bitmaps. Perf overflows set PMU global status and request PMI/PMU handling. RDPMC validates PMU presence, VMware pseudo-PMCs, backend PMC lookup, CR4.PCE/CPL permissions, then reads the virtual counter. Event filters are copied from userspace, validated, converted to masked filters if needed, sorted into include/exclude ranges, installed with RCU, and all vCPUs are forced to reprogram.

## State and Persistence
Per-vCPU PMU state includes GP/fixed PMCs, counters, `eventsel`, `eventsel_hw`, `fixed_ctr_ctrl`, `global_ctrl`, `global_status`, reserved masks, PEBS masks, reprogram bitmaps, in-use bitmaps, emulated event bitmaps, and perf-event pointers. VM-wide filter state persists in `kvm->arch.pmu_event_filter` under RCU/SRCU. Mediated PMU state is loaded into hardware on vCPU entry and read back on exit.

## Dependencies and Integration Points
Depends on Linux perf events, bsearch/sort, CPU model matching, LAPIC delivery, KVM static-call vendor ops, CPUID/feature state, module params such as `enable_pmu`, `enable_mediated_pmu`, and `enable_vmware_backdoor`, and userspace ioctls for PMU filtering. Integrates with KVM requests (`KVM_REQ_PMU`, `KVM_REQ_PMI`), APIC LVTPC, perf guest context APIs, MSR dispatch, emulator instruction accounting, and vendor Intel/AMD PMU implementations.

## Risks
Counter and overflow handling is race-prone: asynchronous perf overflow can race reprogramming, and emulated counts must not be lost when guests write counters. Event filters use RCU and must reprogram all vCPUs to avoid stale allow/deny decisions. Mediated PMU directly touches hardware PMCs and global control; load/put ordering with perf guest context and LAPIC state is critical. Hybrid PMUs are disabled because capability reporting is insufficient. PEBS precise levels are CPU-model sensitive.

## Test Signals
Tests should cover capability initialization on Intel/AMD/no-PMU/hybrid hosts, RDPMC privilege and VMware backdoor paths, guest MSR read/write semantics, perf event creation failure recovery, PMI delivery, PEBS overflow status, event filter allow/deny/masked/exclude behavior, reprogram bitmap races, vCPU cleanup of unused counters, emulated instruction/branch counting, mediated PMU load/put, and migration of PMU state.
