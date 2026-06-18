<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/tee/tstee/Kconfig

## Purpose

`tstee/Kconfig` adds the build-time option for the Arm Trusted Services TEE driver. It exposes Trusted Services Secure Partitions over the generic Linux TEE userspace interface when FF-A transport is available.

## Important APIs, Types, and Functions

The config symbol is `ARM_TSTEE`, a tristate labeled "Arm Trusted Services TEE driver". It depends on `ARM_FFA_TRANSPORT` and defaults to `n`. The help text describes Trusted Services as a framework for Root of Trust services in FF-A Secure Partitions and states that this driver provides the userspace interface missing from the FF-A driver itself.

## Control Flow

When enabled as built-in or module, the Makefile builds `arm-tstee.o`, whose FF-A driver probes Secure Partitions advertising the Trusted Services RPC protocol UUID. If the symbol is disabled, no tstee TEE device is registered.

## State and Persistence Behavior

The Kconfig file has no runtime state. It controls whether driver code is compiled and therefore whether runtime TEE devices can appear for Trusted Services partitions.

## Dependencies and Integration Points

The dependency on `ARM_FFA_TRANSPORT` ensures the FF-A bus and messaging/memory-share operations used by `core.c` are present. The symbol integrates with the TEE core by selecting compilation of the tstee driver but does not itself select `TEE`; the build context must satisfy broader subsystem dependencies.

## Risks and Edge Cases

Because the option defaults off, platforms expecting Trusted Services userspace access must enable it explicitly. The dependency is narrow; any missing implicit dependency on TEE core symbols or architecture support would show up as build failures in unusual configs. The help text is descriptive but does not mention the module name.

## Test Signals

Config tests should build `ARM_TSTEE=y` and `m` with `ARM_FFA_TRANSPORT`, verify it is hidden or rejected without FF-A transport, and run compile tests for module load/unload plus FF-A probe matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/tee/tstee/Kconfig -->
