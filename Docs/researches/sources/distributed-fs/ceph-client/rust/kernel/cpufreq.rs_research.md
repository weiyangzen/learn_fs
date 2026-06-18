<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpufreq.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/cpufreq.rs

## Purpose
This file implements Rust abstractions for the Linux cpufreq subsystem, including frequency tables, policies, driver callback traits, and registration.

## Important APIs, Types, and Functions
It defines driver flags, `DEFAULT_TRANSITION_LATENCY_NS`, `Relation`, `PolicyData`, `TableIndex`, `Table`, `TableBox`, `TableBuilder`, `Policy`, internal `PolicyCpu`, trait `Driver`, and `Registration<T>`. `TableBuilder` builds pinned C frequency tables terminated by a sentinel. `Policy` wraps `struct cpufreq_policy` and exposes CPU, min/max/current/suspend frequencies, generic helpers, cpumask, optional common-clock attachment, DVFS/fast-switch flags, transition/cpuinfo fields, frequency table getter/setter, and private driver data get/set/clear. `Driver` mirrors many cpufreq callbacks. `Registration<T>` builds a mutable C `cpufreq_driver` vtable and registers/unregisters it.

## Control Flow and State
`Relation::new` decodes C relation flags and efficient-bit markers. `TableBuilder::to_table` appends a sentinel entry with `c_ulong::MAX` before pinning entries. `Registration::new` copies the static vtable into `KBox<UnsafeCell<_>>` because cpufreq mutates driver fields, then calls `cpufreq_register_driver`. Mandatory callbacks include `init` and `verify`; optional callbacks are installed based on vtable macro `HAS_*` constants. `init_callback` wraps the policy, calls `T::init`, and stores returned `PData` as foreign-owned driver data. `exit_callback` clears that data and passes ownership to `T::exit`. Other callbacks map C pointers/integers into `Policy`, `PolicyData`, `Relation`, `TableIndex`, or `PolicyCpu` and convert Rust `Result` back into C integers.

## State and Persistence Behavior
Registered driver state persists in a heap-owned `cpufreq_driver` until `Registration::drop`, which unregisters. Per-policy private data is stored in `policy.driver_data` as a `ForeignOwnable` pointer and must be cleared exactly once on exit. `TableBox` pins frequency-table memory so raw C pointers remain stable while the table is installed. `PolicyCpu` acquires policy references with `cpufreq_cpu_get` and releases with `cpufreq_cpu_put`.

## Dependencies and Integration Points
The module depends on `Hertz`, `CpuId`, `Cpumask`, `Device`, `devres`, kernel errors, `ForeignOwnable`, `Opaque`, optional `Clk`, `KVec`, and cpufreq C bindings. It integrates with platform/device drivers through `Registration::new_foreign_owned`.

## Risks
Lifetime hazards dominate: `Policy::set_freq_table` and `set_clk` store raw pointers and rely on callers to keep `TableBox`/`Clk` alive. Callback pointer validity is guaranteed only by cpufreq C infrastructure. Frequency conversion uses kHz fields and can truncate or overflow when casting. `copy_name` relies on compile-time `build_assert!` for name length. `init_callback` can fail with `EBUSY` if driver data was already set. Callback default methods deliberately build-error if installed unexpectedly.

## Test Signals
No local tests. Doc examples cover table construction, policy mutation, and registration from a platform driver. Runtime test signals should include registering/unregistering a sample driver, policy init/exit data ownership, verify/target callbacks, frequency-table lifetime, and suspend/get generic helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/cpufreq.rs -->
