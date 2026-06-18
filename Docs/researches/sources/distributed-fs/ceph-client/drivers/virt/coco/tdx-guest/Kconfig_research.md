# sources/distributed-fs/ceph-client/drivers/virt/coco/tdx-guest/Kconfig

## Purpose
Declares Intel TDX guest userspace driver support.

## APIs, Types, and Functions
`TDX_GUEST_DRIVER` is a tristate depending on `INTEL_TDX_GUEST` and selecting `TSM_REPORTS` and `TSM_MEASUREMENTS`.

## Control Flow and State
Build-time only. Runtime exposes a misc device, TSM report provider, and measurement sysfs group.

## Dependencies and Integration
Requires architecture TDX guest support plus shared TSM report and measurement helpers.

## Risks and Test Signals
Build-test with `INTEL_TDX_GUEST` enabled. Confirm parent Makefile descends into this directory under the architecture symbol and that `TDX_GUEST_DRIVER` controls object compilation inside it.
