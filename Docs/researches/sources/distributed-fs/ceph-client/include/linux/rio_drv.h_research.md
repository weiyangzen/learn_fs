# sources/distributed-fs/ceph-client/include/linux/rio_drv.h

Purpose: this header exposes RapidIO driver-service helpers for config-space access, doorbells, mailbox management, resource claiming, memory mapping, port-write handlers, driver registration, DMA, and driver data access.

Important APIs/types/functions: inline local config helpers wrap `__rio_local_read/write_config_{8,16,32}`. Device config helpers call `rio_mport_read/write_config_*` through `rdev->net->hport`, `destid`, and `hopcount`. Other helpers include `rio_send_doorbell()`, `rio_init_mbox_res()`, `rio_init_dbell_res()`, `RIO_DEVICE()`, message enqueue/dequeue helpers, resource request/release, inbound/outbound mapping, port-write registration, driver register/unregister, device get/put, optional DMA APIs, `rio_name()`, `rio_get_drvdata()`, `rio_set_drvdata()`, local device ID accessors, and `rio_init_mports()`.

Control flow: RapidIO drivers use inline helpers for config I/O and service requests. Resource helpers reserve mailbox/doorbell/memory ranges before use. Mailbox helpers request queues, enqueue outbound buffers or add inbound buffers, and retrieve completions through callbacks. Mapping helpers map RapidIO address windows. Driver registration connects `rio_driver` probe/remove with the bus.

State and persistence: the header manipulates state owned by `rio_dev`, `rio_mport`, resources, mailbox descriptors, and device-model driver data. It does not own independent state.

Dependencies and integration points: includes `rio.h`, resources, string helpers, and optional DMA engine. It is the main convenience API for RapidIO client drivers.

Risks: inline config helpers assume `rdev->net->hport` is valid and running. Resource initialization zeroes structures and sets flags; callers must still request/claim before use. Test signals include config access of all widths, mailbox/doorbell request-release cycles, memory map/unmap, driver bind/unbind, DMA prep, and missing/failed mport ops paths.
