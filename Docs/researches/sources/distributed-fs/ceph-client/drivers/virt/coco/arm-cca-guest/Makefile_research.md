# sources/distributed-fs/ceph-client/drivers/virt/coco/arm-cca-guest/Makefile

## Purpose
Builds the Arm CCA guest TSM provider.

## APIs, Types, and Functions
Maps `CONFIG_ARM_CCA_GUEST` to `arm-cca-guest.o`.

## Control Flow and State
No runtime state; it is a single-object module rule.

## Dependencies and Integration
Consumed by the parent CoCo Makefile and Kconfig.

## Risks and Test Signals
Build with `ARM_CCA_GUEST=m` and built-in on arm64 to verify module naming and TSM symbol linkage.
