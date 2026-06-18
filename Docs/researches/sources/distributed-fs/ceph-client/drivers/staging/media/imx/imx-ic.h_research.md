# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-ic.h

## Purpose
This header defines the shared private wrapper and operation table for i.MX Image Converter internal subdevices.

## Important APIs and Types
`struct imx_ic_priv` stores the IPU device, IPU SoC pointer, embedded V4L2 subdevice, task ID, and task-specific private pointer. `struct imx_ic_ops` contains subdev ops, internal ops, entity ops, and task-specific `init()`/`remove()` callbacks. It declares the two task operation providers: `imx_ic_prp_ops` and `imx_ic_prpencvf_ops`.

## Control Flow and State
The header has no executable control flow. It defines how `imx-ic-common.c` dispatches to task implementations. Task state is anchored through `imx_ic_priv.task_priv`.

## Dependencies and Integration Points
It depends on V4L2 subdev declarations and is included by the common IC registration wrapper plus PRP/PRPENCVF implementations. It is internal to the i.MX media staging driver.

## Risks and Test Signals
Risks include task implementations not filling required ops or failing to initialize `task_priv`, and common unregister assuming valid callbacks. Test signals are registration/unregistration of all task IDs, media entity operations present in the graph, and compile coverage when either task implementation changes.
