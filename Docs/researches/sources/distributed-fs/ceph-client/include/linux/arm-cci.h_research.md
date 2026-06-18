# sources/distributed-fs/ceph-client/include/linux/arm-cci.h

## Purpose
Declares Linux interfaces for ARM CCI cache-coherent interconnect probing and port control.

## Important APIs, Types, And Functions
`cci_probed()` reports whether CCI is available. With `CONFIG_ARM_CCI400_PORT_CTRL`, callers can get ACE ports from device tree nodes, disable a port by CPU MPIDR, or enable/disable ports by device node or index through `__cci_control_port_by_device()` and `__cci_control_port_by_index()`. Convenience macros map enable/disable names to the internal control functions. Stubs return `-ENODEV` when port control is disabled. `cci_enable_port_for_self()` is always declared.

## Control Flow, State, And Persistence
The header does not hold state. Implementations coordinate CCI port enable/disable around CPU/device coherency transitions. Stub control flow makes unsupported port control explicit to callers.

## Dependencies And Integration Points
Depends on `linux/errno.h`, `linux/types.h`, and `asm/arm-cci.h`. Integrated by ARM platform boot, CPU hotplug, power management, and device-tree based coherent-interconnect setup.

## Risks And Test Signals
Incorrect port control can break cache coherency. Tests should cover probe detection, device-tree ACE port lookup, CPU power transitions, unsupported-config error handling, and SMP coherency stress on CCI platforms.
