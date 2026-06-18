# sources/distributed-fs/ceph-client/drivers/of/cpu.c

## Purpose
`cpu.c` maps devicetree CPU nodes to logical Linux CPU IDs, extracts hardware thread IDs, and resolves CPU idle-state nodes. It provides generic weak matching hooks that architectures can override when firmware CPU numbering does not match Linux logical numbering.

## Important APIs, types, and functions
The key exported APIs are `of_get_cpu_hwid()`, `of_get_cpu_node()`, `of_cpu_device_node_get()`, `of_cpu_node_to_id()`, and `of_get_cpu_state_node()`. Weak hooks `arch_match_cpu_phys_id()` and `arch_find_n_match_cpu_physical_id()` provide default physical-ID matching. `__of_find_n_match_cpu_property()` reads either `reg` or PowerPC's `ibm,ppc-interrupt-server#s`.

## Control flow and state
`of_get_cpu_hwid()` reads the CPU node's `reg` property using the parent address-cell count and returns the requested thread slot. `of_get_cpu_node()` iterates all CPU nodes and applies the architecture matching hook, returning a referenced node. `of_cpu_device_node_get()` first tries the registered CPU device's `of_node` and falls back to scanning firmware. `of_cpu_node_to_id()` inverts the mapping by scanning possible CPUs. `of_get_cpu_state_node()` prefers hierarchical `power-domains` plus `domain-idle-states`, then falls back to flat `cpu-idle-states`.

## Dependencies and integration
This file depends on core OF traversal and phandle parsing from `base.c`, CPU device registration from the driver core, and architecture-provided matching overrides. CPU idle and power-management code consume these helpers.

## Risks and test signals
Malformed `reg` lengths, absent address-cell metadata, or architecture-specific physical IDs can make CPU lookup fail. Callers must release returned nodes. Idle-state resolution may be sensitive to mixed old and new bindings. Test signals are boot-time CPU topology correctness, CPU hotplug device association, and cpuidle binding tests.
