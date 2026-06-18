# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.h

## Purpose
Defines the public VME framework ABI used by in-kernel VME client drivers. It names VME resource types, address spaces, cycle attributes, data widths, DMA route/attribute flags, device/driver objects, and the exported framework function prototypes implemented in `vme.c`.

## Important APIs, Types, and Constants
Key constants are `VME_A16/A24/A32/A64/CRCSR/USER*`, `VME_*_MAX`, cycle flags such as `VME_SCT`, `VME_BLT`, `VME_2eSST*`, privilege/data flags, `VME_D8/D16/D32/D64`, DMA attribute types and route flags, `VME_NUM_STATUSID`, `VME_MAX_BRIDGES`, `VME_MAX_SLOTS`, `VME_SLOT_CURRENT`, and `VME_SLOT_ALL`. `struct vme_resource` is the opaque client handle for master/slave/DMA/location-monitor resources. `struct vme_dev` wraps a driver-core `device`, bridge pointer, synthetic device number, and list links. `struct vme_driver` wraps a driver-core `device_driver` plus `match`, `probe`, and `remove` callbacks.

## Control Flow and State
This header has no executable flow, but it defines the contracts used when VME bridges register resources and VME client drivers request them. The `struct vme_resource.entry` points back into a bridge-owned resource list; its lifetime depends on the bridge and on the client calling the matching `vme_*_free()` API.

## Dependencies and Integration Points
Includes Linux bit operations and forward uses driver-core, DMA, list, and mmap descriptor types via included kernel headers in users. It is shared by the framework, fake bridge, TSI148 bridge, and user-space access driver.

## Risks and Test Signals
The flag model allows combinations that may not be valid for a particular bridge; runtime validation is split between `vme.c` and bridge callbacks. The `VME_A64_MAX` macro represents `U64_MAX + 1`, which cannot be stored in 64 bits and is used only as a conceptual bound. Test signals are successful compilation of bridge/client modules, correct compatibility filtering in resource requests, and user drivers not dereferencing `struct vme_resource.entry` directly.
