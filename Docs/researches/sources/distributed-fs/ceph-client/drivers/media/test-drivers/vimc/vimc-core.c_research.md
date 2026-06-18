# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vimc/vimc-core.c

## Purpose
`vimc-core.c` owns VIMC module/platform registration and hard-coded media topology construction. It creates sensors, debayers, raw capture nodes, an RGB/YUV input, scaler, RGB/YUV capture node, and lens ancillary entities, links them, registers V4L2/media devices, and tears everything down.

## Important APIs, Types, and Functions
Module parameter `vimc_allocator` selects vmalloc or DMA-contig capture allocation. Topology is described by `ent_config[]`, `data_links[]`, `ancillary_links[]`, and `pipe_cfg`. Lifecycle helpers include `vimc_add_subdevs()`, `vimc_create_links()`, `vimc_unregister_subdevs()`, `vimc_release_subdevs()`, `vimc_register_devices()`, `vimc_probe()`, `vimc_remove()`, `vimc_init()`, and `vimc_exit()`.

## Control Flow
Module init registers a virtual platform device then a matching platform driver. Probe finds the VGA8x16 font for OSD text, configures the TPG font, optionally coerces DMA mask for DMA-contig mode, allocates `vimc_device`, initializes media and V4L2 devices, allocates the entity array, calls each entity type's `add()` callback, creates data and ancillary links, registers the media device, and exposes subdev nodes. Remove unregisters entity nodes, media device, and V4L2 device; final cleanup occurs through the V4L2 device release callback.

## State and Persistence
Runtime state is held in one `struct vimc_device` associated with the platform device. It owns the media device, V4L2 device, pipe config pointer, and array of entity device pointers. State exists only while the module/platform driver is loaded.

## Dependencies and Integration Points
The core depends on platform bus, DMA mask helpers, font support, media controller, TPG font setup, V4L2 device registration, and all `vimc_*_type` entity exports. User-space sees the resulting topology through media controller and V4L2 nodes.

## Risks and Edge Cases
The topology indexes in data and ancillary links must match `ent_config[]`; incorrect indices create wrong links or out-of-bounds access. Probe fails if the font is unavailable. Error paths must avoid double release because subdevice release is split between explicit failure cleanup and the V4L2 device release callback after successful registration. The TODO RGB/YUV input currently reuses the sensor implementation.

## Test Signals
Load/unload tests should verify all entities and links appear and disappear cleanly. `media-ctl -p` should show the expected topology. Tests should cover both allocator modes, link toggling between debayers/input and scaler, and failure injection around entity registration/link creation.
