<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cpu.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/cpu.h

## Purpose

`linux/cpu.h` stubs CPU hotplug registration for userspace tests.

## Important APIs, Types, and Functions

It defines `cpuhp_setup_state_nocalls(a, b, c, d)` to return `0`.

## Control Flow and State

There is no real CPU hotplug state. Callers see successful registration without side effects.

## Dependencies and Integration Points

It is used when imported kernel data-structure code references CPU hotplug APIs that are irrelevant in userspace.

## Risks and Test Signals

The risk is hiding bugs that depend on hotplug callback execution. For data-structure unit tests, successful build and absence of hotplug-dependent behavior are expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/cpu.h -->
