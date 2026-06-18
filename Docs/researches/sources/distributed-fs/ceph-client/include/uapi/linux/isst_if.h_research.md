# sources/distributed-fs/ceph-client/include/uapi/linux/isst_if.h

## Purpose
`isst_if.h` defines the ioctl ABI for Intel Speed Select Technology control and discovery through OS-to-hardware interfaces.

## Important APIs, Types, and Functions
The header exposes platform info, CPU mapping, PUNIT IO register access, mailbox commands, MSR commands, core-power state, CLOS parameters and CPU associations, TPMI instance counts, performance-level discovery/control, feature enablement, detailed frequency/TDP data, fabric info, CPU masks, base-frequency info, and turbo-frequency info. Ioctls use `ISST_IF_MAGIC` and command numbers for `ISST_IF_GET_PLATFORM_INFO`, `ISST_IF_GET_PHY_ID`, `ISST_IF_IO_CMD`, `ISST_IF_MBOX_COMMAND`, `ISST_IF_MSR_COMMAND`, CLOS/core-power operations, and SST-PP/BF/TF queries and controls.

## Control Flow
Userspace first queries platform support and command batching limits, maps logical CPUs to PUNIT CPUs, then sends batched IO, mailbox, MSR, or feature-specific requests. Many structures contain `get_set` fields that select read or write behavior.

## State and Persistence
Kernel/hardware state includes platform SST capabilities, performance profile, CLOS assignments, core-power enablement, and PUNIT/MSR values. Changes persist according to firmware/hardware policy and may be reset by reboot, package reset, or firmware control.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include Intel platform drivers, PUNIT/TPMI firmware interfaces, power/performance management daemons, and CPU topology mapping.

## Risks and Test Signals
Tests should cover max command counts, flexible single-element-array sizing, logical versus PUNIT CPU numbering, get/set semantics, permission checks for writes, unsupported feature reporting, and multi-socket/power-domain handling. ABI risk is high because firmware-specific structures must remain layout-stable.
