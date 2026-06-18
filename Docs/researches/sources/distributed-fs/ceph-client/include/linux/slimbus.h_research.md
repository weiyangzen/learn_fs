<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slimbus.h -->
# sources/distributed-fs/ceph-client/include/linux/slimbus.h

## Purpose
`slimbus.h` declares the Linux SLIMbus client-driver interface. SLIMbus is a low-power multi-drop bus often used for audio codecs and related components. The header defines device identity, driver registration, value/information element transfers, and stream-management APIs.

## Important APIs, Types, and Functions
The main types are `struct slim_eaddr`, `enum slim_device_status`, `struct slim_device`, `struct slim_driver`, `struct slim_val_inf`, and `struct slim_stream_config`. `slim_device` wraps `struct device`, enumeration address, controller pointer, logical address state, status, and a stream list protected by a spinlock. `slim_driver` provides `probe`, `remove`, `shutdown`, `device_status`, driver core metadata, and an id table.

Driver registration uses `slim_driver_register()`, `__slim_driver_register()`, `slim_driver_unregister()`, and `module_slim_driver()`. Device helpers include `slim_get_devicedata()`, `slim_set_devicedata()`, `of_slim_get_device()`, `slim_get_device()`, and `slim_get_logical_addr()`. Messaging APIs include `slim_xfer_msg()`, `slim_readb()`, `slim_writeb()`, `slim_read()`, and `slim_write()`. Stream APIs include `slim_stream_allocate()`, `slim_stream_prepare()`, `slim_stream_enable()`, `slim_stream_disable()`, `slim_stream_unprepare()`, and `slim_stream_free()`.

## Control Flow
The driver model flow is standard bus binding: a controller enumerates devices, assigns logical addresses, and the bus matches `slim_driver` entries by id table. Driver callbacks handle probe/remove and status changes when devices appear, disappear, or lose logical address validity. Element transfer flow builds `slim_val_inf` with offset, buffers, byte count, and optional completion, then submits it with a message code such as request/reply/change information or value. Stream flow allocates a per-device runtime, prepares it with channel/port/rate/format settings, enables data movement, disables it, unprepares, and frees it.

## State and Persistence Behavior
SLIMbus state is in kernel device objects and controller-managed runtime state. `slim_device.status`, `laddr`, and `is_laddr_valid` reflect bus presence and address assignment. Stream state persists in controller-specific `struct slim_stream_runtime` objects and per-device stream lists. No on-disk state exists.

## Dependencies and Integration Points
The header depends on the driver model, modules, completions, device-tree nodes, mod_devicetable IDs, list/spinlock infrastructure, and audio stream conventions (`SNDRV_PCM_STREAM_PLAYBACK`/capture values are referenced by contract). It integrates with SLIMbus controllers, codec/client drivers, device tree lookup, and ASoC-style audio stream setup.

## Risks and Test Signals
Risks include stale logical addresses, racing device status changes with stream operations, invalid channel/port masks, transfers exceeding the 16-byte element message limit, completion lifetime errors for async requests, and mismatched stream prepare/enable/disable/unprepare sequencing. Test signals include bus enumeration tests, device status callback coverage, read/write transaction failures, lockdep around stream list locking, ASoC playback/capture tests, and hotplug or controller reset scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/slimbus.h -->
