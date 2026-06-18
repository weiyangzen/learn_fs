# sources/distributed-fs/ceph-client/kernel/sched/ext_idle.h

Purpose: provides the private sched_ext idle-tracking interface shared between `ext.c` and `ext_idle.c`. It declares BTF kfunc ID sets used by sched_ext verifier filtering, idle-mask initialization, topology updates, default CPU selection, enable/disable hooks, and late BPF kfunc registration.

Important APIs and types: forward-declares `struct sched_ext_ops` so callers can pass scheduler operation tables without including the full internal header through this file. Exports `scx_kfunc_ids_idle` and `scx_kfunc_ids_select_cpu` for context filtering in `ext.c`. Declares `scx_idle_update_selcpu_topology()`, `scx_idle_init_masks()`, `scx_select_cpu_dfl()`, `scx_idle_enable()`, `scx_idle_disable()`, and `scx_idle_init()`.

Control flow: `init_sched_ext_class()` calls `scx_idle_init_masks()` during scheduler class initialization. `scx_init()` calls `scx_idle_init()` after enough BPF/BTF infrastructure exists to register kfunc sets. Root scheduler enable calls `scx_idle_enable()` before `ops.init()` and updates topology after hotplug validation; root disable calls `scx_idle_disable()`. The scheduler wakeup path in `ext.c` calls `scx_select_cpu_dfl()` when the BPF scheduler lacks `ops.select_cpu()` or when bypassing requires the built-in path.

State and persistence: the header contains no storage beyond extern declarations. All state is owned by `ext_idle.c` static keys and cpumasks, or by `ext.c` scheduler instances and BTF registration tables.

Dependencies and integration points: couples the sched_ext implementation file with the idle helper implementation. The `btf_id_set8` externs are used by `scx_kfunc_context_filter()` logic in `ext.c` to distinguish idle kfuncs from select-cpu kfuncs, and the function declarations let `ext.c` manage idle tracking without exposing implementation internals to the rest of the scheduler.

Risks: this header is small but ABI-sensitive inside the sched_ext subsystem. Prototype drift between `ext_idle.c`, `ext.c`, and BPF kfunc registration would break builds or verifier filtering. The select-cpu declaration includes an optional `cpus_allowed` mask and flags; mismatched semantics would directly affect wakeup CPU placement and BPF kfunc behavior.

Test signals: build sched_ext with BTF and BPF struct_ops enabled, verify kfunc registration succeeds, load BPF schedulers that use both idle and select-cpu helper sets, and exercise enable/disable plus CPU hotplug so all declared entry points are called.
