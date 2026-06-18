# sources/distributed-fs/ceph-client/arch/mips/kernel/pm-cps.c

## Purpose
Implements power-management entry for MIPS CPS systems that can run cores non-coherently, clock-gate, or power-gate. It generates low-level entry/exit assembly at runtime so cache, CM, and CPC operations happen without compiler-inserted memory accesses in unsafe non-coherent windows.

## Important APIs, Types, and Functions
- `cps_nc_entry_fn` is the generated function signature used to enter a CPS PM state.
- `nc_asm_enter`, `ready_count`, `online_coupled`, `pm_barrier`, and `cps_cpu_state` are per-CPU/per-core state used for generated entry stubs and sibling VPE coordination.
- `cps_pm_support_state()` exposes state availability.
- `cps_pm_enter_state()` coordinates online coupled VPEs, prepares CPS boot config for power-gated restore, maps `ready_count` noncoherently, calls generated code, and restores coherent CPU tracking.
- `cps_gen_entry_code()` emits the state-specific assembly sequence using uasm.
- `cps_gen_cache_routine()`, `cps_gen_flush_fsb()`, and `cps_gen_set_top_bit()` emit cache loops, fill/store-buffer workaround code, and LL/SC synchronization snippets.
- `cps_pm_online_cpu()` generates per-core entry functions during CPU hotplug online.
- `cps_pm_power_notifier()` blocks suspend when a JTAG probe would make CPC power gating unsafe.
- `cps_pm_init()` detects CM/CPC capabilities and registers hotplug and PM notifiers.

## Control Flow
`arch_initcall(cps_pm_init)` checks for a CM, verifies that the idle wait function is safe with IRQs off for noncoherent wait, detects CPC clock-gate support, enables power-gating support only when CPS SMP is active, registers a suspend notifier, and installs a CPUHP online callback. On CPU online, `cps_pm_online_cpu()` generates missing entry routines per supported state and shares them with sibling VPEs, then allocates one core `ready_count`. Runtime entry via `cps_pm_enter_state()` calculates the online sibling set, optionally writes restart PC/GP/SP for power-gated restore, clears the CPU from `cpu_coherent_mask`, maps `ready_count` through `kmap_noncoherent()`, synchronizes coupled VPEs, calls the generated function, unmaps, restores `cpu_coherent_mask`, and for noncoherent wait may IPI siblings that remained in `wait`.

## State and Persistence
All state is runtime-only. Generated code buffers are allocated with `kcalloc()` and stored in per-CPU arrays for the life of the boot. `state_support` records available states. Per-core `ready_count` and `pm_barrier` coordinate sibling VPE state transitions. `cps_cpu_state` preserves CPU state for power gating. CM/CPC hardware registers carry the actual coherency and power commands.

## Dependencies and Integration Points
Depends on MIPS CPS/CM/CPC register helpers, CPU topology (`cpu_sibling_map`, `cpu_core`, `cpu_cluster`, `cpu_vpe_id`), cpuhotplug, suspend notifiers, uasm, cache descriptors, `mips_cps_pm_save/restore`, and `cpu_coherent_mask`. It integrates with cpuidle-like state entry even though it cannot use the generic coupled cpuidle barrier directly.

## Risks
This code is highly timing and ordering sensitive. Incorrect barriers or LL/SC loops can let a VPE touch L1 while another disables coherence. Generated code size/label arrays are fixed. The FSB flush workaround temporarily uses perf counters and can perturb counts. Power gating depends on valid CPS SMP boot config and correct restore entry addresses. Noncoherent mappings of `ready_count` must be initialized and unmapped exactly once. JTAG suspend blocking is essential to avoid NoC hangs.

## Test Signals
Boot logs should advertise available/unavailable PM states with warnings for missing CM/CPC or unsafe wait functions. CPU hotplug online should generate entry functions without `"Failed to generate"` errors. Repeated cpuidle/suspend cycles should not corrupt data or hang sibling VPEs. Suspend with EJTAG probe should abort. Cache coherency stress across idle transitions is the primary behavioral signal.
