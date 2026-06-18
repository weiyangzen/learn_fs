# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/common.bpf.h

Purpose: central BPF-side sched_ext support header. It imports `vmlinux.h`, declares sched_ext and BPF kfuncs, provides struct_ops section macros, safe verifier-friendly pointer helpers, kptr/list/rbtree/cpumask/task/cgroup declarations, CPU iterators, time helpers, READ/WRITE_ONCE, math helpers, task-weight scaling, random helper, and scheduler clock accessors.

Important APIs/macros: `BPF_STRUCT_OPS()` and `BPF_STRUCT_OPS_SLEEPABLE()` define struct_ops program sections. `scx_bpf_exit()`, `scx_bpf_error()`, and `scx_bpf_dump()` wrap bstr kfuncs with variadic formatting. `RESIZABLE_ARRAY()`, `MEMBER_VPTR()`, and `ARRAY_ELEM_PTR()` are used heavily by sched_ext examples to satisfy verifier bounds requirements. It declares kfuncs such as `scx_bpf_create_dsq()`, `scx_bpf_select_cpu_dfl()`, `scx_bpf_dispatch_nr_slots()`, `scx_bpf_kick_cpu()`, DSQ iterators, cpuperf kfuncs, cpumask kfuncs, task/cgroup kfuncs, and BPF object/list/rbtree helpers.

Control flow: mostly inline helpers and macros. CPU iterator definitions wrap `bpf_iter_bits`. Time comparison helpers use signed subtraction. `is_migration_disabled()` handles the ambiguity introduced by BPF execution disabling migration. Clock helpers use CO-RE shadow structs for `rq` and optional IRQ/paravirt accounting fields.

State and persistence: no persistent data of its own, but it declares extern kernel symbols such as `runqueues`, weak `cpu_irqtime`, and kconfig variables. It gives BPF programs access to mutable kernel scheduler state through kfuncs and CO-RE reads.

Dependencies and integration: requires bpftool-generated `vmlinux.h`, libbpf BPF helper headers, `user_exit_info.bpf.h`, generated enum definitions, and finally includes `compat.bpf.h` plus `enums.bpf.h`. It is the foundational include for all sched_ext BPF examples in this subset.

Risks: many helpers depend on kernel version and weak kfunc availability. Verifier-friendly macros return `NULL` on failed bounds proof and require immediate checks. Clock accessors require correct callback context and rq locking assumptions. The bstr wrappers rely on format checking but still pass raw values to kernel kfuncs.

Test signals: BPF compile and verifier load across kernel versions, especially with changed sched_ext kfunc signatures, missing optional fields, old clang/pahole enum handling, and examples using resizable arrays and rbtree/list helpers.
