# sources/distributed-fs/ceph-client/drivers/virt/coco/pkvm-guest/Makefile

## Purpose
Builds the arm64 pKVM guest helper.

## APIs, Types, and Functions
Maps `CONFIG_ARM_PKVM_GUEST` to `arm-pkvm-guest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Included by the parent CoCo Makefile.

## Risks and Test Signals
Build with `ARM_PKVM_GUEST=y`; it is bool-only, so module unload paths do not apply.
