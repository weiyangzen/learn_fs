## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/getcpu.c

Purpose: Implements the s390 vDSO `getcpu` fast path.

Important API: `__s390_vdso_getcpu(unsigned *cpu, unsigned *node, void *unused)`.

Control flow: Stores the extended TOD clock into a local `union tod_clock`, reads the programmable field as the current CPU number, writes it to `*cpu` when provided, writes NUMA node zero when `node` is provided, and returns success.

State and persistence: Reads hardware TOD programmable field maintained by kernel CPU initialization. It owns no persistent state.

Dependencies and integration: Depends on `store_tod_clock_ext()`, `vdso_getcpu_init()` in `vdso.c`, and s390 convention that NUMA node is always zero for this vDSO API.

Risks and test signals: Risk is stale programmable field after CPU migration or hotplug if CPU init does not update it. Test signals include vDSO `getcpu()` compared with syscall/getcpu, CPU migration stress, and null pointer arguments.
