<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_smt.h -->
# sources/distributed-fs/ceph-client/include/linux/cpu_smt.h

## Purpose

`cpu_smt.h` declares the CPU hotplug control surface for simultaneous multithreading. It tracks whether SMT is enabled, disabled, force-disabled, unsupported, or not implemented. The source was read as a complete 33-line file.

## Important APIs, Types, and Functions

`enum cpuhp_smt_control` defines `CPU_SMT_ENABLED`, `CPU_SMT_DISABLED`, `CPU_SMT_FORCE_DISABLED`, `CPU_SMT_NOT_SUPPORTED`, and `CPU_SMT_NOT_IMPLEMENTED`. With `CONFIG_SMP` and `CONFIG_HOTPLUG_SMT`, it exposes `cpu_smt_control`, `cpu_smt_num_threads`, `cpu_smt_disable()`, `cpu_smt_set_num_threads()`, `cpu_smt_possible()`, `cpuhp_smt_enable()`, and `cpuhp_smt_disable()`. Other builds define inert constants and stubs.

## Control Flow

Boot or mitigation code sets SMT policy, then hotplug code enables or disables sibling threads accordingly. Thread-count configuration restricts how many SMT siblings may stay online.

## State and Persistence Behavior

Global SMT state persists in kernel variables for the boot lifetime. It can be influenced by boot parameters, architecture support, and security mitigation policy, but the header owns no storage.

## Dependencies and Integration Points

It integrates with CPU hotplug, SMP topology, sysfs SMT controls, and CPU mitigation code in `cpu.h`. It intentionally has no includes beyond the guard and relies on consumers having basic type definitions.

## Risks and Edge Cases

Force-disabled SMT should not be re-enabled through ordinary paths. Disabled-config stubs can make callers think a transition succeeded without hardware effect. Thread-count limits must match topology or sibling CPUs may be wrongly offlined or exposed.

## Test Signals

Signals include SMT sysfs enable/disable tests, boot-parameter mitigation tests, hotplug of sibling threads, force-disabled re-enable rejection, topology variations with different thread counts, and !HOTPLUG_SMT builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpu_smt.h -->
