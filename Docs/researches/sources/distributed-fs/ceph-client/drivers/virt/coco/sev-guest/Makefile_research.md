# sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Makefile

## Purpose
Builds the AMD SEV guest driver.

## APIs, Types, and Functions
Maps `CONFIG_SEV_GUEST` to `sev-guest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Included by the parent CoCo Makefile.

## Risks and Test Signals
Build as `m` and `y`, especially with `TSM_REPORTS=m/y` compatibility.
