# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/device.h

## Purpose
Declares the core NVKM device object, chipset/family metadata, subdevice layout, interrupt state, privileged MMIO accessors, and device logging.

## Important APIs, Types, And Functions
Defines `enum nvkm_device_type`, `struct nvkm_device`, `nvkm_device_func`, `nvkm_device_quirk`, `nvkm_device_chip`, BAR IDs, resource callbacks, subdev/engine lookup, device find/delete, `nvkm_rd/wr/mask`, `NVKM_RD32`, device object class, and logging macros.

## Control Flow
Device functions implement preinit/init/fini/irq/resource flows. Subdevice and engine lookup traverse device layout. MMIO helpers read/write BAR0 PRI. Logging macros gate by device debug level.

## State And Persistence
Device state persists for the GPU lifetime: kernel device pointer, BAR0 PRI mapping, chip data, card type, chipset/revision, layout pointers, subdevice list, interrupt lists/locks, refcount, quirks, and debug config.

## Dependencies And Integration Points
Depends on core oclass/suspend/intr/layout definitions and underpins every NVKM subdevice, engine, interrupt, and NVIF device object.

## Risks
Device lifetime and refcount bugs affect all subdevices. Wrong card type/chip layout or BAR resource mapping can break initialization. MMIO accessors assume valid `pri`.

## Test Signals
GPU probe/remove, suspend/resume, IRQ delivery, subdevice init/fini ordering, BAR access, and debug logs validate behavior.
