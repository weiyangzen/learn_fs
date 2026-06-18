<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-smp.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-smp.c

## Purpose
`hyp-smp.c` provides nVHE-local CPU topology and per-CPU base helpers. It mirrors the host CPU logical map and per-CPU base array into hyp-readable storage for code that cannot trust or directly use host data after pKVM finalization.

## Important APIs, Types, and Functions
`hyp_cpu_logical_map[NR_CPUS]` stores MPIDR hardware ids, initialized to `INVALID_HWID`. `cpu_logical_map()` returns the hyp copy for a logical CPU and asserts bounds. `kvm_arm_hyp_percpu_base[NR_CPUS]` stores host-provided per-CPU base addresses. `__hyp_per_cpu_offset()` converts a CPU’s kernel VA base to a hyp VA offset relative to `__per_cpu_start`.

## Control Flow, State, and Persistence
Both arrays are `__ro_after_init`, so they are populated by setup before becoming immutable. The file has no complex control flow: callers query a CPU index and get either an MPIDR or per-CPU offset. Bounds errors are fatal via `BUG_ON`.

## Dependencies and Integration Points
It integrates with PSCI CPU selection (`psci-relay.c`), per-CPU macros, `kvm_init_params` setup, and nVHE per-CPU storage in the linker script. It depends on `kern_hyp_va()` address translation and hyp section symbols.

## Risks and Test Signals
Risks include stale CPU maps if CPUs come online after KVM initialization, bounds BUGs from corrupted CPU ids, and mismatched per-CPU bases causing silent state corruption. Test signals are CPU hotplug restrictions, PSCI CPU_ON only for initialized CPUs, per-CPU variable access on all initialized CPUs, and boot on systems with sparse MPIDRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-smp.c -->
