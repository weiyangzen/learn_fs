# sources/distributed-fs/ceph-client/drivers/power/sequencing/core.c

## Purpose
`core.c` implements the Linux power-sequencing framework. It creates a `pwrseq` bus, lets providers register sequencers exposing named targets made from dependency-ordered units, and lets consumers acquire descriptors and call `pwrseq_power_on()`/`pwrseq_power_off()` with shared reference counting.

## Important APIs, Types, and Functions
Important types are private `struct pwrseq_unit`, `pwrseq_unit_dep`, `pwrseq_target`, `pwrseq_device`, and `pwrseq_desc`. Exported APIs are `pwrseq_device_register()`, `pwrseq_device_unregister()`, `devm_pwrseq_device_register()`, `pwrseq_device_get_drvdata()`, `pwrseq_get()`, `devm_pwrseq_get()`, `pwrseq_put()`, `pwrseq_power_on()`, and `pwrseq_power_off()`. Debugfs support exposes target/unit state.

## Control Flow
Provider registration validates config, allocates an ID/device, checks each target dependency graph for cycles with a radix tree, builds unique unit objects and dependency references, and adds the sequencer to the pwrseq bus under `pwrseq_sem`. Consumer lookup scans the bus, invokes provider `.match()`, finds the requested target name, pins the provider module, and returns a descriptor. Power-on locks the provider, recursively enables dependencies before the target, increments enable counts, then runs post-enable outside the state lock. Power-off disables the target and dependencies in reverse when the last user releases them, with rollback on dependency disable failure.

## State and Persistence Behavior
Persistent state includes the global IDA, bus registration, global `pwrseq_sem`, provider devices, unit dependency lists, enable counts, descriptors' `powered_on` flags, and optional debugfs dentry. Provider removal is guarded by device and rwsem references and warns on active users.

## Dependencies and Integration Points
It depends on the driver core bus/device model, krefs, IDA, list/radix-tree helpers, rwsems/mutexes, module owner pinning, cleanup guards, debugfs/seq_file, and public pwrseq consumer/provider headers. Providers in this tree register through the provider API; consumers use the descriptor API.

## Risks and Edge Cases
Reference counting and lock ordering are central risks: provider unregister, consumer lookup, and power transitions must not race. Post-enable failure rolls back after the state lock is reacquired. Dependency-cycle checking uses unit-data pointer identity, so provider static data must be stable. `pwrseq_get()` returns `-EPROBE_DEFER` when no provider matches, which can hide permanent DT mismatches. Removal only warns about active users; misuse can leave hardware on.

## Test Signals
Test provider registration/unregistration, invalid configs, cyclic dependencies, shared dependencies with multiple targets, concurrent consumers, post-enable failure rollback, disable failure rollback, module unload while descriptors exist, debugfs output, and probe-defer behavior when providers appear late.
