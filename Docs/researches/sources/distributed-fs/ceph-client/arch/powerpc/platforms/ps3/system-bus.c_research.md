# sources/distributed-fs/ceph-client/arch/powerpc/platforms/ps3/system-bus.c

Purpose: Implements the PS3 platform bus, LV1 device open/close wrappers, MMIO region mapping, DMA mapping operations, device registration, driver registration, uevents, and device-driver matching for PS3 system devices.

Important APIs/types/functions: Exports `ps3_open_hv_device()`, `ps3_close_hv_device()`, `ps3_mmio_region_create()`, `ps3_free_mmio_region()`, `ps3_mmio_region_init()`, `ps3_system_bus_device_register()`, `ps3_system_bus_driver_register()`, and `ps3_system_bus_driver_unregister()`. Key structures include the root `ps3_system_bus`, `usage_hack`, `ps3_system_bus_type`, MMIO ops, and DMA ops for SB and IOC0 devices.

Control flow: Core init registers the root device and bus when PS3 LV1 firmware is present. Drivers match devices by `match_id` and optional `match_sub_id`; probe/remove/shutdown delegate to `ps3_system_bus_driver` callbacks. Device registration assigns parent, bus, release callback, DMA ops, and generated names by device type. Open/close route storage/network/USB devices through `lv1_open_device()/lv1_close_device()` and GPU/sound through `lv1_gpu_open()/lv1_gpu_close()`, with reference counters for shared devices.

State and persistence: Persistent state includes bus registration, the fake root device, static device counters for naming, DMA operation tables, and `usage_hack` counters protected by a mutex. MMIO regions remember bus address, length, page size, and returned LPAR address. DMA mappings persist in PS3 DMA regions external to this file until unmapped.

Dependencies and integration points: Integrates with Linux driver core, DMA API, PS3 LV1 device/MMIO/GPU calls, PS3 DMA region helpers, PS3 device descriptors from repository enumeration, module autoload through `MODALIAS=ps3:id:subid`, and system shutdown.

Risks: The `usage_hack` is an explicit FIXME rather than a general reference model and only covers selected devices. Several default or unexpected cases call `BUG()`. Scatter-gather and IOC0 operations are incomplete or assert in some configurations. DMA mapping returns may not consistently use `DMA_MAPPING_ERROR` on `ps3_dma_map()` failure.

Test signals: Driver binding and modalias autoload for PS3 devices, LV1 open/close balance under multiple clients, MMIO create/free, DMA coherent/map/unmap tests for SB and IOC0, shutdown callbacks, and hot error paths for failed LV1 calls are relevant.

Source read size: 807 lines, 19473 bytes.
