# sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Makefile

## Purpose
Builds the Intel TDX guest driver.

## APIs, Types, and Functions
Maps `CONFIG_TDX_GUEST_DRIVER` to `tdx-guest.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Included from the CoCo parent directory when TDX guest support is selected.

## Risks and Test Signals
Build `TDX_GUEST_DRIVER=m/y`, especially with the parent directory selected by `CONFIG_INTEL_TDX_GUEST`.
