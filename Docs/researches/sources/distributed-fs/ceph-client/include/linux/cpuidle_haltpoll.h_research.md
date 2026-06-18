<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle_haltpoll.h -->
# sources/distributed-fs/ceph-client/include/linux/cpuidle_haltpoll.h

## Purpose

`cpuidle_haltpoll.h` provides architecture hooks for enabling and disabling haltpoll cpuidle behavior on a CPU. The source was read as a complete 16-line file.

## Important APIs, Types, and Functions

With `CONFIG_ARCH_CPUIDLE_HALTPOLL`, it includes `asm/cpuidle_haltpoll.h`. Otherwise it defines no-op `arch_haltpoll_enable(unsigned int cpu)` and `arch_haltpoll_disable(unsigned int cpu)`.

## Control Flow

Haltpoll cpuidle code calls the architecture enable/disable hooks when CPUs or drivers activate haltpoll behavior. Architectures that need model-specific setup provide the implementation in asm headers.

## State and Persistence Behavior

The header owns no state. Architecture code may maintain per-CPU haltpoll controls, but unsupported builds do nothing.

## Dependencies and Integration Points

It integrates with cpuidle haltpoll drivers and architecture idle/halt controls.

## Risks and Edge Cases

Callers must tolerate no-op behavior on architectures without haltpoll support. Architecture implementations must be CPU-hotplug safe because hooks take a CPU number.

## Test Signals

Signals include build coverage with and without `CONFIG_ARCH_CPUIDLE_HALTPOLL`, haltpoll driver enable/disable on CPU hotplug, and architecture-specific idle behavior validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cpuidle_haltpoll.h -->
