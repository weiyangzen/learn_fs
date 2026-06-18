# sources/distributed-fs/ceph-client/arch/powerpc/kernel/sysfs.c

## Purpose
Creates and manages PowerPC CPU sysfs files for topology, physical IDs, CPU hotplug registration, PMU and SPR access, DSCR defaults, pseries idle counters, SVM status, and selected e500 power-management controls.

## Important APIs, Types, and Functions
- `DEFINE_PER_CPU(struct cpu, cpu_devices)` backs CPU device registration.
- SPR/PMC macros generate `read_*`, `write_*`, `show_*`, and `store_*` functions that run on the target CPU via `smp_call_function_single()`.
- DSCR support: `dscr_default`, `show/store_dscr`, `show/store_dscr_default`, `sysfs_create_dscr_default()`.
- e500 controls: PW20 and AltiVec idle state/wait-time attributes manipulate `SPRN_PWRMGTCR0`.
- `ppc_enable_pmcs()` enables PMCs once per CPU and marks PMU in use.
- `register_cpu_online()` creates per-CPU attributes according to CPU features and `cur_cpu_spec->pmc_type`; `unregister_cpu_online()` removes them.
- Exported helpers `cpu_add_dev_attr[_group]()` and `cpu_remove_dev_attr[_group]()` add/remove attributes across possible CPUs.
- `topology_init()` registers CPU devices, physical ID files, CPUHP callbacks, DSCR default, and SVM file.

## Control Flow and State
At `subsys_initcall`, the code registers present/hotpluggable CPU devices and installs a CPU hotplug state. On CPU online, it obtains the OF CPU node, creates SMT snooze, PMU, PURR/SPURR/PIR/TSCR, DSCR, pseries idle, and e500 idle files depending on config and feature bits, then calls cacheinfo online. Offline removes the same files, cacheinfo state, and OF node reference.

## State and Persistence Behavior
Persistent kernel state includes per-CPU device objects, sysfs files, `dscr_default`, per-PACA DSCR defaults, per-CPU `pmcs_enabled`, e500 idle wait globals, and OF node references. Sysfs writes can directly modify hardware SPRs on target CPUs.

## Dependencies and Integration Points
Integrates with CPU subsystem, CPU hotplug, OF CPU nodes, cacheinfo, PMU/PMC definitions, PACA/LPPACA, firmware features, pseries idle accounting, secure virtual machine status, and platform CPU probe/release hooks.

## Risks
Sysfs SPR writes are privileged but dangerous: wrong values can affect performance counters, power management, or CPU behavior. Attribute add/remove must mirror exactly across hotplug to avoid stale sysfs files. `smp_call_function_single()` assumes target CPUs are online and responsive. DSCR updates across all CPUs must respect task inheritance semantics.

## Test Signals
CPU online/offline loops with sysfs scanning, read/write DSCR and PMU attributes, pseries idle PURR/SPURR exposure, e6500 PW20/AltiVec idle controls, secure guest `svm` file, NUMA node symlinks, and dynamic `cpu_add_dev_attr_group()` users.
