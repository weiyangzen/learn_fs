# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_core.c

## Purpose
Implements the generic Linux remote processor framework core: device registration, firmware boot, attach/detach, shutdown, resource-table parsing, carveout and IOMMU management, virtio resource discovery, crash reporting, recovery, and module init/exit. Platform drivers supply `struct rproc_ops`; this file supplies the common lifecycle and resource orchestration.

## Important APIs, Types, And Functions
Exports the main remoteproc API: `rproc_alloc()`, `devm_rproc_alloc()`, `rproc_add()`, `devm_rproc_add()`, `rproc_del()`, `rproc_free()`, `rproc_put()`, `rproc_boot()`, `rproc_shutdown()`, `rproc_detach()`, `rproc_set_firmware()`, `rproc_get_by_phandle()`, `rproc_get_by_child()`, `rproc_report_crash()`, `rproc_add_carveout()`, `rproc_resource_cleanup()`, `rproc_mem_entry_init()`, `rproc_of_resm_mem_entry_init()`, and `rproc_da_to_va()`. Internal handlers process `RSC_CARVEOUT`, `RSC_DEVMEM`, `RSC_TRACE`, and `RSC_VDEV`, with vendor resources delegated to `ops->handle_rsc`.

Important state lives in `struct rproc`: lifecycle `state`, atomic `power`, `lock`, firmware name, boot address, resource-table pointers and sizes, carveout/mapping/trace/rvdev/subdev/dump lists, notify IDR, IOMMU domain, crash counters, recovery flags, and coredump policy. Global state includes the RCU `rproc_list`, device-index IDA, panic notifier, and recovery workqueue.

## Control Flow
`rproc_alloc()` initializes a remoteproc device, copies ops, installs default ELF/coredump callbacks where needed, initializes lists and locks, and assigns a class device name. `rproc_add()` validates the initial state, adds optional cdev support, registers the device, creates debugfs entries, optionally auto-boots or attaches, and exposes the instance through `rproc_list`.

`rproc_boot()` is power-refcounted. The first caller either attaches to a detached processor or requests firmware and calls `rproc_fw_boot()`. Firmware boot performs sanity checks, enables IOMMU, calls platform prepare, extracts boot address, parses firmware/resource table, handles resources, allocates carveouts, loads segments, copies the prepared resource table into remote memory, starts subdevices and the processor, and marks `RPROC_RUNNING`. Shutdown and detach stop subdevices, snapshot/reset resource tables, call platform stop/detach, clean mappings/carveouts/vdevs/coredumps, unprepare hardware, disable IOMMU, and clear cached tables.

Crashes are reported by `rproc_report_crash()` from interrupt-safe contexts. It takes a wake reference and queues `rproc_crash_handler_work()`, which serializes with `rproc->lock`, ignores duplicates/offline processors, marks `RPROC_CRASHED`, increments `crash_cnt`, and either leaves the processor crashed or triggers boot-based or attach-based recovery.

## State And Persistence Behavior
Runtime state is held in the device model, sysfs/debugfs/cdev exposure, global RCU list, DMA/IOMMU mappings, allocated carveouts, registered `rproc-virtio` platform devices, and resource-table copies. Firmware resource tables are copied to `cached_table`, mutated by resource handling and virtio setup, then copied into loaded remote memory. Attached processors may also keep `clean_table` so detach can restore the remote-owned resource table. `power` is a runtime usage count and does not own the object lifetime.

## Dependencies And Integration Points
Integrates with firmware loading, default ELF loader callbacks, IOMMU, DMA coherent allocation, OF firmware-name parsing, reserved memory, debugfs/sysfs/cdev, virtio/rpmsg through `rproc-virtio`, PM wake locks, panic notifier callbacks, and platform-specific `rproc_ops`. It uses `remoteproc_internal.h` for optional-op dispatch and `remoteproc_coredump.c` for dump collection.

## Risks
Resource-table data is firmware-controlled; truncation and offset checks are critical for memory safety. Physical addresses are still written into 32-bit resource-table fields, with warnings for truncation. Cleanup must balance IOMMU mappings, carveouts, vdevs, cached tables, and device references across boot failures, shutdown, detach, and recovery. Recovery can sleep and must be entered through the queued crash path from atomic contexts. Refcount mistakes around `power`, `rproc_list`, or child devices can leak mappings or leave stale remoteproc handles.

## Test Signals
Exercise sysfs start/stop/detach, firmware switching while offline, malformed resource tables and ELF images, IOMMU fault crash reporting, debugfs crash injection, coredump generation, virtio/rpmsg probing, repeated boot/shutdown reference counting, auto-boot during register/unregister, panic callbacks, and KASAN/KMEMLEAK/lockdep across recovery and driver removal.
