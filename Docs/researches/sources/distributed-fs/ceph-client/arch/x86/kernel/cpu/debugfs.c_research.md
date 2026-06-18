# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/debugfs.c

## Purpose
`debugfs.c` exposes x86 CPU topology internals through debugfs. It creates `arch_debugfs_dir/topo/domains` for system topology domain sizes/shifts and `arch_debugfs_dir/topo/cpus/<cpu>` for per-CPU topology and cache IDs.

## Important APIs, Types, and Functions
`cpu_debug_show()` prints online state and, if initialized, APIC IDs, package/die/core topology fields, CPU type, logical topology IDs, LLC/L2 cache IDs, AMD node data, and package/core/thread count globals. `dom_debug_show()` prints domain names, shifts, domain sizes, and cumulative max thread counts from `x86_topo_system`.

`cpu_debug_open()` and `dom_debug_open()` wrap the show functions with `single_open()`. `dfs_cpu_ops` and `dfs_dom_ops` provide read-only seq_file operations. `cpu_init_debugfs()` creates the directory tree at `late_initcall`.

## Control Flow
At late init, `cpu_init_debugfs()` creates `topo`, then `domains`, then a `cpus` directory with one file per possible CPU. Reading a CPU file uses the CPU number stored in `inode->i_private`, gets `per_cpu(cpu_info, cpu)`, and prints nothing beyond online state if that CPU has not completed initialization. Reading `domains` iterates `TOPO_MAX_DOMAIN`.

## State and Persistence
The file has no independent persistent state. Debugfs dentries persist while mounted and reflect live kernel state from `cpu_info`, topology globals, and CPU online state at read time.

## Dependencies and Integration Points
It depends on debugfs, seq_file, `arch_debugfs_dir`, APIC/topology structures, `cpu_info` from `common.c`, and topology helpers such as `get_topology_cpu_type_name()` and `topology_amd_nodes_per_pkg()`.

## Risks
Debugfs is diagnostic and optional, but formatting changes can affect scripts used by developers. The per-CPU files are created for possible CPUs, so reads must tolerate offline or not-yet-initialized CPUs. There is no explicit error handling for debugfs creation failures, matching common debugfs practice.

## Test Signals
With debugfs mounted, inspect `/sys/kernel/debug/x86/topo/domains` and `/sys/kernel/debug/x86/topo/cpus/*` on SMT, multi-core, multi-die, AMD-node, and hybrid CPU systems. Hotplug CPUs and confirm online/initialized behavior remains coherent.
