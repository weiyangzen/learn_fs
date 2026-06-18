# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/compat.bpf.h

Purpose: BPF-side compatibility layer for sched_ext kernel API evolution.

Important APIs/macros: `__COMPAT_ENUM_OR_ZERO()` checks enum value existence. It wraps renamed or changed kfuncs including task cgroup lookup, DSQ move/consume/dispatch variants, cpumask populate, DSQ peek fallback, sub-dispatch, enqueue CPU-selected detection, `scx_bpf_now()`, event counters, NUMA-aware idle CPU helpers, current-task lookup, packed-argument variants of `scx_bpf_select_cpu_and()` and `scx_bpf_dsq_insert_vtime()`, boolean-returning `scx_bpf_dsq_insert()`, task slice/vtime setters, local reenqueue, generic DSQ reenqueue, and `SCX_OPS_DEFINE()`.

Control flow: wrappers use `bpf_ksym_exists()`, `bpf_core_type_exists()`, and `bpf_core_enum_value_exists()` to choose the best available implementation at load/runtime. Some fallbacks directly read or write task fields when newer authority-checking kfuncs are absent.

State and persistence: no persistent state. It changes generated BPF call paths based on kernel features.

Dependencies and integration: included at the tail of `common.bpf.h`, so every sched_ext BPF example gets these wrappers. It depends on weak kfunc declarations, CO-RE type/enum detection, and generated `HAVE_*` macros.

Risks: compatibility branches can hide behavior changes across kernel versions. Some fallbacks return success after void older kfunc calls, which differs from newer boolean semantics. Generic reenq fallback intentionally errors if an unsupported DSQ reenqueue is requested.

Test signals: load the same BPF examples on kernels before and after sched_ext renames/signature changes, especially v6.13, v6.15, v6.19, v6.20, and v7.1-related paths noted in comments.
