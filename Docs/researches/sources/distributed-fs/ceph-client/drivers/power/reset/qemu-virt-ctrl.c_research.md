# sources/distributed-fs/ceph-client/drivers/power/reset/qemu-virt-ctrl.c

## Purpose
QEMU virt machine system-controller reset/poweroff driver.

## Important APIs, Types, and Functions
MMIO register definitions, sys-off poweroff/restart handlers, and platform probe.

## Control Flow
probe maps the virt-control resource and registers restart/poweroff; callbacks write command values to QEMU-provided MMIO registers and delay/log on failure.

## State and Persistence Behavior
MMIO base is device-managed; command writes are consumed by the emulator and do not persist past VM exit/reset.

## Dependencies and Integration Points
HAS_IOMEM, platform/OF, sys-off API, QEMU virt hardware model.

## Risks and Edge Cases
only works when QEMU exposes the controller; writes on nonmatching hardware would be meaningless; no completion except VM action.

## Test Signals
QEMU virt DT probe, guest poweroff/reboot, unmapped resource failure, and command-value tracing.
