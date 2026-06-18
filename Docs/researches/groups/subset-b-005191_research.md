# subset-b-005191 Research

Grouped research for the remoteproc core, diagnostics, ELF, virtio, ST, STM32, and TI K3 files listed in subset `subset-b-005191`. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_core.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_core.c

## Purpose
Implements the generic Linux remote processor framework core: registration, firmware boot, attach/detach, shutdown, resource-table parsing, carveout and IOMMU management, virtio resource discovery, crash handling, recovery, and module init/exit. Platform-specific drivers provide `struct rproc_ops`; this file supplies the shared lifecycle and resource orchestration that those drivers plug into.

## Important APIs, Types, And Functions
The exported API includes `rproc_alloc()`, `devm_rproc_alloc()`, `rproc_add()`, `devm_rproc_add()`, `rproc_del()`, `rproc_free()`, `rproc_put()`, `rproc_boot()`, `rproc_shutdown()`, `rproc_detach()`, `rproc_set_firmware()`, `rproc_get_by_phandle()`, `rproc_get_by_child()`, `rproc_report_crash()`, `rproc_add_carveout()`, `rproc_resource_cleanup()`, `rproc_mem_entry_init()`, `rproc_of_resm_mem_entry_init()`, and `rproc_da_to_va()`. Internal handlers cover `RSC_CARVEOUT`, `RSC_DEVMEM`, `RSC_TRACE`, and `RSC_VDEV`, while vendor resources are delegated through `ops->handle_rsc`.

Key state lives in `struct rproc`: `state`, `power`, `lock`, `firmware`, `bootaddr`, `table_ptr`, `cached_table`, `clean_table`, `table_sz`, carveout/mapping/trace/vdev/subdev/dump lists, `notifyids`, `max_notifyid`, feature bits, IOMMU domain, coredump policy, and recovery flags. Global state includes the RCU-protected `rproc_list`, IDA-backed device indices, the panic notifier, and the recovery workqueue.

## Control Flow
`rproc_alloc()` initializes a remoteproc device, copies platform ops, assigns default ELF and coredump callbacks when needed, creates lists, mutexes, work, and a device name. `rproc_add()` validates offline/detached state, adds the optional char device, registers the device, creates debugfs entries, optionally kicks asynchronous auto-boot or immediate attach, and finally exposes the instance through `rproc_list`.

Boot is refcounted through `rproc_boot()`. The first user either attaches to a detached processor or synchronously requests firmware and calls `rproc_fw_boot()`. Firmware boot performs sanity checking, IOMMU enablement, platform preparation, boot address extraction, firmware parsing, resource-table handling, carveout allocation, ELF segment loading, resource-table copy-back into remote memory, subdevice preparation, platform `start()`, subdevice start, and state transition to `RPROC_RUNNING`. Later boot calls only increment `power`.

Shutdown and detach are the inverse paths. `rproc_shutdown()` decrements `power`, stops subdevices, snapshots or resets resource tables, calls platform `stop()`, cleans resources, unprepares the device, disables IOMMU, frees cached tables, and returns to `RPROC_OFFLINE`. `rproc_detach()` similarly calls platform `detach()` and leaves externally booted firmware running while remoteproc services are disconnected.

Crash reporting is interrupt-safe: low-level drivers call `rproc_report_crash()`, which takes a wake reference and queues `rproc_crash_handler_work()`. The work item serializes with `rproc->lock`, ignores duplicate/offline crashes, marks `RPROC_CRASHED`, increments `crash_cnt`, and either leaves the processor crashed or calls `rproc_trigger_recovery()`. Recovery chooses attach-based detach/attach when `RPROC_FEAT_ATTACH_ON_RECOVERY` is set, otherwise stops, coredumps, reloads firmware, and restarts.

## State And Persistence Behavior
Persistent kernel state is device-model state, sysfs/debugfs/cdev exposure, the global RCU list, DMA/IOMMU mappings, allocated carveouts, registered platform `rproc-virtio` devices, and resource-table copies. Resource-table mutation is deliberately staged: firmware tables are copied into `cached_table`, then copied into loaded device memory after vrings and carveouts are assigned. Attached processors may also keep `clean_table` so detach can restore the remote-owned resource table.

The `power` atomic is a runtime usage count, not a device reference count. Device lifetime is owned by `get_device()`/`put_device()`, `rproc_get_by_phandle()`, and driver core release. Firmware names are mutable only while offline and are heap-owned strings.

## Dependencies And Integration Points
This file integrates with firmware loading, ELF loader callbacks, IOMMU, DMA coherent allocation, OF firmware-name parsing, reserved-memory carveout helpers, debugfs/sysfs/cdev, virtio via generated `rproc-virtio` platform devices, rpmsg through virtqueue interrupts, PM wake locks during recovery, panic notifier callbacks, and platform drivers through `struct rproc_ops`. It relies on `remoteproc_internal.h` for inlined ops dispatch and on `remoteproc_coredump.c` for dump collection.

## Risks
The resource-table parser trusts firmware-controlled offsets after bounded size checks; mistakes in truncation or offset arithmetic would affect kernel memory safety. Physical addresses are still written back into resource tables and 64-bit addresses are warned/truncated in 32-bit fields. IOMMU mappings and carveout lifetimes must remain balanced across boot failures, shutdown, detach, and recovery. Recovery paths assume coredump and restart work can sleep, so atomic callers must use `rproc_report_crash()` rather than `rproc_trigger_recovery()`. Refcount mistakes around `power`, `rproc_list`, or virtio platform devices can leave running processors, leaked mappings, or stale handles.

## Test Signals
Useful signals include boot/stop/attach/detach via `/sys/class/remoteproc/remoteproc*/state`, firmware switching while offline, malformed resource-table and ELF firmware rejection, successful cleanup after forced boot failures, IOMMU fault-triggered crash reporting, debugfs `crash` recovery injection, coredump generation, virtio/rpmsg device probing, repeated `rproc_boot()`/`rproc_shutdown()` refcount tests, module remove while auto-boot is pending, and lockdep/KASAN/KMEMLEAK checks across recovery and unregister paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_coredump.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_coredump.c

## Purpose
Builds remoteproc crash dumps as ELF core files and exposes them through the Linux devcoredump framework. It supports both full buffered dumps and inline dumps where userspace reads remote memory while recovery waits.

## Important APIs, Types, And Functions
Exports `rproc_coredump_cleanup()`, `rproc_coredump_add_segment()`, `rproc_coredump_add_custom_segment()`, `rproc_coredump_set_elf_info()`, `rproc_coredump()`, and `rproc_coredump_using_sections()`. `struct rproc_coredump_state` tracks the rproc, generated ELF header, and completion for inline dump lifetime. Dump segments are `struct rproc_dump_segment` entries on `rproc->dump_segments`; they may use default `rproc_da_to_va()` copying or a platform-supplied per-segment dump callback.

## Control Flow
Drivers add segments before a crash, optionally set ELF class/machine, and remoteproc core invokes `ops->coredump()` during recovery. `rproc_coredump()` computes ELF header/program-header size, allocates a vmalloc buffer, initializes ELF identity and program headers, optionally copies each registered segment into the buffer, and calls `dev_coredumpv()` for buffered mode. Inline mode passes only the header plus a read callback to `dev_coredumpm()` and waits for completion before recovery continues.

`rproc_coredump_using_sections()` follows the same policy but emits section headers and a string table, using each segment's `priv` string as the section name. `rproc_coredump_read()` maps user offsets across the generated header and segment list, calling `rproc_copy_segment()` for segment data.

## State And Persistence Behavior
Dump segment registrations persist on `rproc->dump_segments` until `rproc_coredump_cleanup()` runs during remoteproc resource cleanup. Buffered dumps transfer ownership of the vmalloc buffer to devcoredump. Inline dumps keep the header in `dump_state` until devcoredump calls the free callback, then complete a wait that blocks recovery. Invalid segment translations are represented as `0xff` bytes rather than aborting the dump.

## Dependencies And Integration Points
Depends on `remoteproc_elf_helpers.h` for ELF32/ELF64 field access, `rproc_da_to_va()` for device-address translation, `memcpy_fromio()` handling through the `is_iomem` flag, and devcoredump for userspace exposure. Core defaults `ops->coredump` to `rproc_coredump()` when a platform driver does not provide one.

## Risks
Inline mode intentionally stalls recovery until userspace reads the dump or devcoredump times out, which can lengthen outage time. Section-mode assumes `segment->priv` is a valid string. ELF size arithmetic depends on registered segment sizes; very large segment sets can fail vmalloc or expose long dump reads. A bad platform address translation produces partial dumps filled with `0xff`, so dump consumers must treat missing regions as diagnostic signal rather than valid memory.

## Test Signals
Test by registering normal and custom segments, forcing crashes with coredump modes `disabled`, `enabled`, and `inline`, validating generated ELF headers with `readelf`, confirming section names in section-mode dumps, verifying recovery waits only for inline mode, and injecting invalid device-address segments to confirm errors and `0xff` fill behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_debugfs.c

## Purpose
Provides debugfs diagnostics and control files for remoteproc instances. It exposes processor name, recovery policy, artificial crash injection, resource-table decoding, carveout memory information, trace buffers, and coredump policy.

## Important APIs, Types, And Functions
Framework-facing functions are `rproc_init_debugfs()`, `rproc_exit_debugfs()`, `rproc_create_debug_dir()`, `rproc_delete_debug_dir()`, `rproc_create_trace_file()`, and `rproc_remove_trace_file()`. File operations implement `name`, `recovery`, `crash`, `resource_table`, `carveout_memories`, `coredump`, and trace-buffer reads. `rproc_rsc_table_show()` decodes standard resource-table entries and `rproc_carveouts_show()` emits each carveout list entry.

## Control Flow
Module init creates a top-level directory named after `KBUILD_MODNAME` when debugfs is initialized. `rproc_add()` calls `rproc_create_debug_dir()` per instance, creating stable files under `remoteproc/remoteprocN`. Trace resources discovered while parsing firmware call `rproc_create_trace_file()` and are removed by `rproc_resource_cleanup()`.

Writes to `recovery` toggle `recovery_disabled` or call `rproc_trigger_recovery()`. Writes to `crash` parse an integer crash type and call `rproc_report_crash()`. Writes to `coredump` select disabled, buffered, or inline dump policy, unless the processor is already crashed.

## State And Persistence Behavior
Debugfs state mirrors live kernel objects and is removed on rproc deletion or module exit. It does not persist across reboot. The trace file reads directly from remote memory through `rproc_da_to_va()`, so its contents reflect the current remote buffer and may disappear when resources are cleaned. Recovery and coredump writes mutate `rproc->recovery_disabled` and `rproc->dump_conf`.

## Dependencies And Integration Points
Uses debugfs, seq_file show helpers, `copy_from_user()`, `simple_read_from_buffer()`, resource-table definitions from `linux/remoteproc.h`, and core translation/recovery/crash APIs. Trace files are created by `remoteproc_core.c` when handling `RSC_TRACE`.

## Risks
Debugfs is a privileged diagnostic interface, but `crash` deliberately triggers recovery paths and can disrupt a running remote processor. Resource-table output trusts the current `table_ptr` and performs presentation-only decoding without the same full validation used during firmware load. Trace reads use `strnlen()` on shared remote memory, so stale or changing buffers can yield partial output. The coredump and recovery string parsers use write length comparisons; tests should include newline and partial-command behavior.

## Test Signals
Mount debugfs and verify files appear after `rproc_add()` and disappear after `rproc_del()`. Exercise `recovery` with enabled, disabled, and recover; `coredump` with disabled, enabled, inline; and `crash` with known crash IDs. Confirm `resource_table` and `carveout_memories` reflect firmware resources after boot, and trace files show either live text or the "not available" fallback after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_helpers.h

## Purpose
Provides inline helpers for class-neutral ELF32/ELF64 field access used by remoteproc firmware loading and coredump generation.

## Important APIs, Types, And Functions
`fw_elf_get_class()` reads `EI_CLASS` from a firmware image. `elf_hdr_init_ident()` initializes core ELF identity bytes. `ELF_GEN_FIELD_GET_SET()` generates getter/setter pairs for selected ELF header, program header, and section header fields. `ELF_STRUCT_SIZE()` generates `elf_size_of_hdr()`, `elf_size_of_phdr()`, and `elf_size_of_shdr()`. `elf_strtbl_add()` appends a name to the section string table and returns its offset.

## Control Flow
Callers inspect the firmware or target dump class once, then pass that class into generated helpers. For getters and setters, the helper casts the provided memory to either the 32-bit or 64-bit ELF structure and reads or writes the requested field. Coredump section-mode uses `elf_strtbl_add()` to fill the string table while advancing an optional caller-owned index.

## State And Persistence Behavior
The header has no global state. It mutates only caller-supplied ELF buffers. `elf_strtbl_add()` assumes the section-header string table has already been laid out in the ELF buffer and updates the caller's string-table index when provided.

## Dependencies And Integration Points
Included by `remoteproc_elf_loader.c` and `remoteproc_coredump.c`. It depends on Linux ELF definitions, `struct firmware`, and standard memory/string helpers available in kernel context.

## Risks
Helpers do not validate buffer bounds, string-table capacity, endianness, or class correctness; callers must perform those checks before use. `elf_hdr_init_ident()` always writes little-endian identity bytes, matching current coredump output but not a general-purpose endian abstraction. `elf_strtbl_add()` uses `strcpy()` into a caller-managed table, so incorrect size calculation in the caller can corrupt the generated ELF buffer.

## Test Signals
Compile coverage across 32-bit and 64-bit ELF paths is important. Validate generated coredump headers and section tables with ELF tooling, and feed 32-bit and 64-bit firmware images through the loader to confirm helper offsets and sizes match kernel ELF structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_loader.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_loader.c

## Purpose
Implements the default ELF32/ELF64 firmware loader for remoteproc. It validates firmware images, extracts boot addresses, loads `PT_LOAD` segments into remote-addressable memory, finds and caches `.resource_table`, and locates the loaded resource table after firmware copy.

## Important APIs, Types, And Functions
Exports `rproc_elf_sanity_check()`, `rproc_elf_get_boot_addr()`, `rproc_elf_load_segments()`, `rproc_elf_load_rsc_table()`, and `rproc_elf_find_loaded_rsc_table()`. The internal `find_table()` scans section headers for `.resource_table` and validates the remoteproc resource-table header.

## Control Flow
Sanity checking verifies firmware presence, minimum header size, ELF magic, supported ELF class, host-matching endianness, enough section-header space, nonzero program-header count, and a program-header offset within the image. Segment loading iterates program headers, skips non-loadable or empty segments, rejects `filesz > memsz`, rejects truncated file data, checks `memsz` fits in `size_t`, translates physical/device address through `rproc_da_to_va()`, then copies data and zeroes BSS using normal or I/O memory accessors.

Resource-table loading finds `.resource_table`, validates version, reserved fields, and offset array size, then copies it to `rproc->cached_table` and points `rproc->table_ptr` at the cached copy. After segments are loaded, `rproc_elf_find_loaded_rsc_table()` uses the section address and size to translate the loaded resource table in remote memory.

## State And Persistence Behavior
The loader writes firmware contents into memory already registered by core/platform carveout handling. It allocates `rproc->cached_table`, sets `table_ptr`, and records `table_sz`. The cached table is later mutated by resource handlers and virtio setup, copied into loaded remote memory by the core, and freed during shutdown or error cleanup.

## Dependencies And Integration Points
Used as the default loader by `rproc_alloc_ops()` when platform ops do not provide custom load/parse/sanity callbacks. It depends on `remoteproc_elf_helpers.h`, `rproc_da_to_va()`, and the remoteproc resource-table ABI. Platform drivers can override any part of this loader while still reusing individual exported helpers.

## Risks
The loader assumes firmware endianness matches the host. It validates enough global ELF structure to avoid common truncation issues, but `find_table()` trusts section-name table layout after sanity checks and does not provide a complete generic ELF verifier. Device address translation failures prevent load, so platform memory maps must be prepared before `load`. Firmware with a missing resource table currently causes `rproc_elf_load_rsc_table()` to fail; platform wrappers such as STM32 may intentionally downgrade that to a warning.

## Test Signals
Use valid ELF32 and ELF64 firmware, bad magic, wrong endianness, missing program headers, truncated program/section/resource tables, `filesz > memsz`, out-of-range segment offsets, oversized `memsz` on 32-bit, missing `.resource_table`, and segment addresses outside registered carveouts. Validate loaded BSS zeroing and resource-table copy-back into remote memory after vring allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_elf_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_internal.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_internal.h

## Purpose
Declares private cross-file remoteproc interfaces and small inline dispatch helpers shared by core, sysfs/debugfs, coredump, ELF loader, virtio transport, and platform drivers.

## Important APIs, Types, And Functions
Defines `struct rproc_debug_trace` for trace debugfs entries and `struct rproc_vdev_data` for passing resource-table vdev information into the `rproc-virtio` platform driver. Declares core, virtio, debugfs, sysfs, cdev, vring, ELF, carveout, and rvdev helpers. Provides inline wrappers for optional `rproc_ops` hooks: `prepare`, `unprepare`, `attach`, `sanity_check`, `get_boot_addr`, `load`, `parse_fw`, `handle_rsc`, `find_loaded_rsc_table`, and `get_loaded_rsc_table`. Also includes feature-bit helpers and `rproc_u64_fit_in_size_t()`.

## Control Flow
Most wrappers return success or a neutral value when the platform hook is absent, except `rproc_load_segments()` which returns `-EINVAL` without a loader. Core code calls these wrappers to keep lifecycle logic independent of platform-specific optional operations.

## State And Persistence Behavior
The header itself persists no state. Its inline helpers read or mutate `rproc->features` and call function pointers stored in the copied `rproc->ops` table.

## Dependencies And Integration Points
It is the local contract among `drivers/remoteproc` implementation files and hides optional `CONFIG_REMOTEPROC_CDEV` behavior behind no-op stubs when the cdev interface is disabled. The declarations tie together resource parsing, debugfs trace files, sysfs class registration, virtio vring handling, and ELF helper defaults.

## Risks
Because wrappers silently skip absent hooks, platform drivers must understand which callbacks are truly optional for their mode. `rproc_attach_device()` returns success without an attach hook, but `rproc_validate()` separately prevents detached processors from registering without one. The declared `rproc_release(struct kref *)` appears stale relative to the current device-model release path, so new code should follow actual exported lifetime APIs instead.

## Test Signals
Build-test configurations with and without `CONFIG_REMOTEPROC_CDEV`, platform drivers using default ELF hooks, custom loader platforms, attach-only platforms, vendor-resource handlers, and feature-bit bounds checking through `rproc_set_feature()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_sysfs.c

## Purpose
Registers the `remoteproc` device class and exposes the normal userspace control ABI under `/sys/class/remoteproc/remoteproc*/`. Attributes report and control recovery, coredump policy, firmware name, processor state, and display name.

## Important APIs, Types, And Functions
Exports `rproc_class`, `rproc_init_sysfs()`, and `rproc_exit_sysfs()`. Attribute handlers implement `recovery`, `coredump`, `firmware`, `state`, and `name`. `rproc_is_visible()` enforces read-only mode when `rproc->sysfs_read_only` is set.

## Control Flow
Class registration attaches a default attribute group to every remoteproc device. `state_store()` maps `start` to `rproc_boot()`, `stop` to `rproc_shutdown()`, and `detach` to `rproc_detach()`. `firmware_store()` delegates validation and locking to `rproc_set_firmware()`. `recovery_store()` toggles `recovery_disabled` or explicitly triggers recovery. `coredump_store()` changes dump policy unless the processor is currently crashed.

## State And Persistence Behavior
Writes directly mutate live `struct rproc` fields or initiate lifecycle transitions. Firmware changes persist only in kernel memory for the lifetime of the remoteproc instance and are rejected while running. `firmware_show()` reports `unknown` when attached to externally booted firmware. The class and attributes are recreated on module reload or boot.

## Dependencies And Integration Points
Used by `remoteproc_core.c` during module init and by `rproc_alloc()` through `rproc_class`. It depends on core lifecycle APIs, the coredump enum/string ABI, and the remoteproc state enum remaining synchronized with `rproc_state_string`.

## Risks
This is a stable userspace ABI, so spelling changes to attribute values would be externally visible. `recovery_disabled` is mutated without taking `rproc->lock`, relying on simple boolean semantics while recovery itself locks. `state_store()` allows userspace to request detach only when core state permits it; mismatched platform attach/detach support surfaces as runtime errors. Comments mention "default" coredump while accepted strings are `disabled`, `enabled`, and `inline`, so tests should reflect actual parser behavior.

## Test Signals
Check class registration, attribute visibility, read-only mode, state strings for every enum value, start/stop/detach command behavior, firmware writes while offline versus running, coredump write rejection while crashed, and recovery writes that recover a deliberately crashed processor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_virtio.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_virtio.c

## Purpose
Implements the remoteproc virtio transport. It turns `RSC_VDEV` resource-table entries into Linux virtio devices, allocates and wires vrings, maps virtio config space into the resource table, and routes mailbox kicks between remote processors and virtqueues.

## Important APIs, Types, And Functions
Exports `rproc_vq_interrupt()`. Internal `rproc_virtio_config_ops` implements virtio callbacks: features, status, find/delete virtqueues, reset, and config get/set. `rproc_virtio_probe()` consumes `struct rproc_vdev_data` passed by core, parses vrings, allocates notify IDs, adds an rvdev subdevice, and holds an rproc reference. `rproc_add_virtio_dev()` registers the actual `struct virtio_device` when the remoteproc subdevice starts.

## Control Flow
Core parses an `RSC_VDEV` and registers a `rproc-virtio` platform device. The platform driver's probe copies DMA range information from the remoteproc parent, coerces DMA mask, parses each resource-table vring, allocates vring memory entries through core helpers, and adds subdevice start/stop callbacks. When the remote processor starts, subdevice start calls `rproc_add_virtio_dev()`, which associates dedicated or fallback reserved memory, allocates a virtio device, and registers it. Virtio drivers then call `find_vqs()`, which creates vrings on preallocated carveout memory and writes assigned device addresses back into the resource table.

Outbound notifications call platform `ops->kick(rproc, notifyid)`. Inbound platform interrupts call `rproc_vq_interrupt()`, which uses `rproc->notifyids` to find the vring and dispatches `vring_interrupt()`. Stop removes child virtio devices; platform remove frees vring IDs and drops the rproc reference.

## State And Persistence Behavior
State is split across the resource table, `struct rproc_vdev`, `struct rproc_vring`, `rproc->notifyids`, vring carveout entries, registered platform devices, and child virtio devices. Virtio status, guest features, config space, vring device addresses, and notify IDs are stored in `rproc->table_ptr`, which may point to cached or loaded resource-table memory depending on lifecycle stage. DMA range maps are duplicated and freed with device release.

## Dependencies And Integration Points
Integrates with core resource parsing, reserved-memory helpers, DMA coherent memory pools, the Linux virtio core, `virtio_ring`, platform driver registration, and platform-specific mailbox/doorbell `kick` callbacks. It assumes standard remoteproc firmware resource-table vdev layout with at most two vrings per vdev.

## Risks
Packed rings are explicitly disabled because preallocated vring memory is used. Feature negotiation has a `BUG_ON()` if negotiated features exceed 32 bits, matching resource-table field width but risky if future virtio features grow. Resource-table config access checks bounds but silently returns after logging on out-of-bounds reads/writes. Correct cleanup depends on device release ordering because virtio devices hold the platform device and remoteproc references. Reserved-memory fallback to parent memory-region index 0 is best-effort and can silently fall back to global pools.

## Test Signals
Boot firmware with vdev and two vrings, verify virtio/rpmsg device registration, notify ID assignment, resource-table vring address/status/feature updates, inbound mailbox delivery through `rproc_vq_interrupt()`, stop/restart cleanup of virtqueues and child devices, missing `kick` rejection, reserved-memory vdev buffer assignment, and malformed resource tables with too many vrings or invalid vring size/alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/remoteproc_virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/st_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/st_remoteproc.c

## Purpose
Platform driver for ST ST40/ST231 remote processors. It controls clocks, reset lines, boot address programming through syscon, optional mailbox-based virtqueue signaling, reserved-memory carveouts, and ELF firmware loading through the remoteproc core.

## Important APIs, Types, And Functions
Defines `struct st_rproc_config` for SoC-specific reset and boot-address mask configuration, and `struct st_rproc` for clocks, resets, syscon boot register, and mailbox channels. `st_rproc_ops` supplies `kick`, `start`, `stop`, `parse_fw`, and default ELF callbacks. Probe and remove are `st_rproc_probe()` and `st_rproc_remove()`.

## Control Flow
Probe allocates an rproc, selects match data, parses reset controls, clock frequency, and boot syscon, prepares the clock, determines current reset state, marks an already-enabled processor running, otherwise sets the requested clock rate, optionally requests four mailbox channels, and registers the rproc. Firmware parsing enumerates reserved memory regions: normal regions are registered as ioremap-backed carveouts and `vdev0buffer` is registered as reserved memory for vdev DMA allocation, then the ELF resource table is loaded.

Start writes masked boot address bits into syscon, enables the clock, deasserts software reset, then deasserts power reset when present. Stop asserts resets and disables the clock. Mailbox callbacks map vq0/vq1 RX events to `rproc_vq_interrupt()`, and `kick()` sends the virtqueue ID on the matching TX channel.

## State And Persistence Behavior
Driver-private state persists in `rproc->priv`. Clock preparation lasts until remove; clock enable is tied to processor runtime. Reserved memory entries are added during firmware parsing and cleaned by core resource cleanup. Mailbox channels are held from probe to remove when present. If hardware is already running at probe, `rproc->power` is incremented and state is set to `RPROC_RUNNING`.

## Dependencies And Integration Points
Depends on DT compatible strings `st,st40-rproc` and `st,st231-rproc`, reset controller names, `clock-frequency`, `st,syscfg`, optional `mbox-names`, reserved memory, regmap/syscon, mailbox, and remoteproc ELF helpers. It integrates with remoteproc virtio/rpmsg through mailbox kicks.

## Risks
The start error path after power-reset failure asserts `sw_reset` under the `pwr_reset` label, so reset unwinding must be scrutinized for the intended hardware sequencing. Mailbox support is optional, but `kick()` assumes a requested TX channel for active rpmsg firmwares. Already-running detection treats both reset lines as authoritative and does not attach using the detached-state flow. Reserved-memory name matching uses `vdev0buffer` convention and may misclassify differently named pools.

## Test Signals
Test both ST40 and ST231 match data, missing/deferred resets and clocks, boot-address mask programming, already-running probe, start/stop reset sequencing, reserved-memory parsing with code/data and vdev buffer regions, optional no-mailbox operation, mailbox vq0/vq1 interrupts, and rpmsg traffic through `kick()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/st_remoteproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/st_slim_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/st_slim_rproc.c

## Purpose
Provides an exported allocation/teardown helper for ST SLIM-core based devices that want to register a SLIM core as a remoteproc. It maps SLIM memory/register resources, manages clocks, starts/stops the core, and supports ELF segment loading into IMEM/DMEM.

## Important APIs, Types, And Functions
Exports `st_slim_rproc_alloc()` and `st_slim_rproc_put()`. Internal ops are `slim_rproc_start()`, `slim_rproc_stop()`, and `slim_rproc_da_to_va()`. `slim_rproc_ops` supplies start/stop, address translation, ELF boot address, load, and sanity-check callbacks. It relies on `struct st_slim_rproc` from the public ST SLIM remoteproc header.

## Control Flow
`st_slim_rproc_alloc()` validates firmware name and DT compatibility, allocates an rproc, maps `dmem`, `imem`, `slimcore`, and `peripherals` resources, acquires and enables all available clocks, registers the rproc, and returns the private SLIM handle to the parent IP driver. Start gates/resets the CPU pipeline, disables STBus sync, clears and masks mailbox-like command/interrupt registers, enables the CPU, reads hardware and firmware revisions, and logs them. Stop masks channels, gates the pipeline clock, clears run enable, and warns if the core did not stop.

Address translation maps exact IMEM/DMEM bus addresses to ioremapped CPU addresses when the requested length fits the region.

## State And Persistence Behavior
The helper keeps clocks enabled for the lifetime between alloc and put, while start/stop manipulates SLIM control registers. Mapped memories are devm-managed with the platform device. The rproc exists until `st_slim_rproc_put()` calls `rproc_del()` and `rproc_free()`. There is no resource-table parser; firmware loading depends on direct address translation for ELF segments.

## Dependencies And Integration Points
Depends on platform resources named `dmem`, `imem`, `slimcore`, and `peripherals`; DT compatibility `st,slim-rproc`; clock providers; the remoteproc core; and ELF loader helpers. It is not a standalone platform driver in this file; another driver calls the exported alloc/put API.

## Risks
`slim_rproc_da_to_va()` only matches segment addresses equal to a region base, not offsets within a region, so firmware segment layout must match that expectation or loading will fail. Clocks remain enabled outside start/stop, which may be intentional for register/memory access but affects power. Stop uses register writes rather than reset controls and only warns if disable fails. There is no mailbox integration with remoteproc virtio in this file.

## Test Signals
Parent-driver tests should cover missing firmware name, incompatible DT, missing memory resources, deferred clocks, ELF segment load into IMEM/DMEM, start/stop register sequencing, firmware revision read from DMEM, repeated alloc/put cleanup, and segment addresses with region offsets to verify expected translation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/st_slim_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/stm32_rproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/stm32_rproc.c

## Purpose
Platform driver for STM32MP1 M4 remote processor control. It supports remoteproc-managed boot, attach/detach to bootloader-started firmware, hold-boot control through SCMI reset, SMC, or syscon, mailbox-based virtqueue and shutdown/detach signaling, watchdog crash reporting, reserved-memory carveouts, resource-table discovery, and power-management wake behavior.

## Important APIs, Types, And Functions
Private types include `struct stm32_syscon`, `struct stm32_rproc_mem`, `struct stm32_rproc_mem_ranges`, `struct stm32_mbox`, and `struct stm32_rproc`. `st_rproc_ops` supplies `prepare`, `start`, `stop`, `attach`, `detach`, `kick`, ELF loader callbacks, and `get_loaded_rsc_table`. Key helpers are `stm32_rproc_of_memory_translations()`, `stm32_rproc_prepare()`, `stm32_rproc_request_mbox()`, `stm32_rproc_set_hold_boot()`, `stm32_rproc_add_coredump_trace()`, `stm32_rproc_get_loaded_rsc_table()`, and `stm32_rproc_parse_dt()`.

## Control Flow
Probe coerces a 32-bit DMA mask, reads optional firmware name, allocates the rproc, sets ELF coredump info, parses watchdog IRQ, resets, hold-boot controls, optional PDDS, auto-boot flag, M4 state, and resource-table syscon, reads parent `dma-ranges` for PA/DA translation, detects if M4 is already running and marks `RPROC_DETACHED`, creates a workqueue, requests mailboxes, and registers the rproc.

Prepare iterates reserved memory regions, translates each physical address to device address, registers ioremap-backed carveouts, registers `vdev0buffer` as reserved-memory DMA pool, and adds coredump segments for mapped regions. Firmware parsing loads the resource table when present but only warns if absent. Start clears deep-sleep, releases hold boot, then reasserts hold boot for the next cycle. Attach adds trace buffers to coredump and holds boot. Detach notifies firmware over the detach mailbox and releases hold boot so the remote can auto-reboot. Stop optionally sends a shutdown mailbox message, holds boot, asserts reset, sets deep-sleep, and updates coprocessor state to off.

Mailbox callbacks queue work for vq0/vq1 so virtqueue interrupts run under `rproc->lock` and only while running or attached. `kick()` sends "kick" on the mailbox matching the virtqueue. `get_loaded_rsc_table()` reads a device address from syscon, translates it to physical, maps a fixed 1 KiB table window, and returns it for attach mode.

## State And Persistence Behavior
Private state tracks mapped reserved memories, mailboxes, syscon descriptors, watchdog IRQ, workqueue, and an optional mapped resource-table window. Reserved carveouts and coredump segments are registered during prepare and cleaned by core. Mailbox channels and workqueue persist from probe to remove. Wake IRQ state is registered when DT marks the device as wakeup-capable. A running bootloader-started M4 is represented as `RPROC_DETACHED` so remoteproc attaches rather than reloads firmware.

## Dependencies And Integration Points
Depends on STM32 DT bindings for resets, syscon properties (`st,syscfg-*`), parent `dma-ranges`, reserved memory, optional `st,auto-boot`, mailbox names `vq0`, `vq1`, `shutdown`, and `detach`, watchdog IRQ, and wakeup-source. Integrates with ARM SMCCC when configured, regmap/syscon, reset controllers, mailbox, PM wake IRQ, devm I/O mapping, remoteproc coredump, and virtio/rpmsg.

## Risks
The fixed `RSC_TBL_SIZE` of 1024 bytes assumes firmware reserves a sufficient table area and detach overwrites that whole window from `clean_table`. Missing resource tables are tolerated in parse_fw, so downstream features depending on vdev/trace resources will not appear. Mailboxes are optional except deferred probe, so firmware protocols must tolerate missing shutdown/detach channels. Hold-boot can be controlled by three mechanisms; DT mistakes can lead to the wrong control path. Remove calls `rproc_shutdown()` if power is positive and then `rproc_del()`, while `rproc_del()` also attempts shutdown, so idempotency relies on core state checks.

## Test Signals
Test remoteproc boot and bootloader attach paths, hold-boot via SCMI reset, syscon, and SMC, optional/no resource-table firmware, mailbox vq interrupts and kicks, shutdown/detach acknowledgements and timeouts, watchdog crash IRQ recovery, coredump segment inclusion for reserved memories and trace buffers, suspend/resume wake IRQ behavior, `dma-ranges` translation failures, and missing optional syscon properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/stm32_rproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.c

## Purpose
Shared implementation for TI K3 remoteproc drivers. It handles mailbox callbacks/kicks, TI-SCI and reset-controller power sequencing, prepare/unprepare, start/stop, IPC-only attach/detach, loaded resource-table lookup, device-address translation, internal SRAM mapping, reserved-memory setup, and cleanup helpers.

## Important APIs, Types, And Functions
Exports `k3_rproc_mbox_callback()`, `k3_rproc_kick()`, `k3_rproc_reset()`, `k3_rproc_release()`, `k3_rproc_request_mbox()`, `k3_rproc_prepare()`, `k3_rproc_unprepare()`, `k3_rproc_start()`, `k3_rproc_stop()`, `k3_rproc_attach()`, `k3_rproc_detach()`, `k3_get_loaded_rsc_table()`, `k3_rproc_da_to_va()`, `k3_rproc_of_get_memories()`, `k3_mem_release()`, `k3_reserved_mem_init()`, and `k3_release_tsp()`.

## Control Flow
Mailbox callback handles remote crash and echo messages specially, ignores ready/control messages, drops unknown values above `max_notifyid`, and routes valid queue IDs to `rproc_vq_interrupt()`. Kicks send the queue ID over the single mailbox channel. Reset/release choose local reset control or TI-SCI module get/put depending on `uses_lreset`.

Prepare skips already-detached IPC-only cores, otherwise asserts local reset when applicable, verifies it remains asserted, and deasserts module reset through TI-SCI so internal RAM can be loaded. Unprepare asserts module reset unless detaching. Start releases reset; stop asserts reset. Attach/detach are NOPs for IPC-only mode but satisfy core validation.

Memory setup maps named internal memories from platform resources and reserved-memory regions from DT. Reserved-memory index 0 is used as the vring DMA pool, while later regions are mapped as static carveouts with device address equal to 32-bit physical start. Address translation checks internal memories by both remote device address and SoC bus address, then static reserved regions by device address.

## State And Persistence Behavior
`struct k3_rproc` stores mapped internal memories, mapped reserved memories, TI-SCI handles, reset control, mailbox, and dev pointer. Most resources are devm-managed. Reserved memory pool association is released by a devm action. IPC-only mode assumes a resource table at reserved memory region 1 base and returns a fixed 256-byte table window.

## Dependencies And Integration Points
Depends on TI-SCI device and processor control, reset controller, OMAP mailbox constants, reserved-memory DT entries, platform memory resources named by SoC-specific data, and remoteproc core/virtio. DSP and M4 drivers compose this common layer with their compatible-specific memory tables and boot rules.

## Risks
Remote crash mailbox messages are logged but do not call `rproc_report_crash()`, and K3 wrappers disable recovery, so automatic recovery is not supported here. IPC-only resource table size is hard-coded to 256 bytes and assumes reserved-memory region ordering. Reserved-memory device addresses truncate to 32-bit physical starts, excluding 64-bit region support. Address range checks use `da + len` arithmetic and should be considered for overflow if future 64-bit addresses are allowed. Mailbox message filtering relies on `max_notifyid` being initialized by resource handling.

## Test Signals
Test mailbox echo, ready, queue, crash, and unknown messages; local-reset and module-reset platforms; prepare/unprepare balance on boot failure and shutdown; internal SRAM and reserved DDR address translation; IPC-only loaded resource-table discovery; reserved-memory counts below two; mailbox request deferral; and repeated boot/stop cycles under TI-SCI tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.h -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.h

## Purpose
Defines the shared TI K3 remoteproc data structures and function prototypes used by K3 DSP, M4, and related remoteproc drivers.

## Important APIs, Types, And Functions
Defines `KEYSTONE_RPROC_LOCAL_ADDRESS_MASK`, `struct k3_rproc_mem`, `struct k3_rproc_mem_data`, `struct k3_rproc_dev_data`, and `struct k3_rproc`. Prototypes cover mailbox, reset/release, prepare/unprepare, start/stop, attach/detach, loaded resource table lookup, address translation, internal memory parsing, reserved memory setup, and TI-SCI processor-handle cleanup.

## Control Flow
The header has no direct control flow; it is the contract consumed by SoC-specific wrappers. Those wrappers populate `k3_rproc_dev_data`, allocate a remoteproc with `sizeof(struct k3_rproc)` private state, fill TI-SCI/reset/mailbox fields, and assign common callbacks in their `rproc_ops`.

## State And Persistence Behavior
`struct k3_rproc` is the persistent per-device private state. It owns pointers to internal memory mappings, reserved memory mappings, mailbox channel/client, reset controller, TI-SCI handles, TI-SCI device ID, SoC data, and optional private extension data.

## Dependencies And Integration Points
Requires remoteproc core types plus reset, mailbox, TI-SCI, and reserved memory concepts included by source files. It is included by `ti_k3_common.c`, `ti_k3_dsp_remoteproc.c`, `ti_k3_m4_remoteproc.c`, and other K3 remoteproc implementations.

## Risks
Because the structures are shared across multiple drivers, changes to field meaning or memory-region ordering affect all K3 remoteproc variants. `KEYSTONE_RPROC_LOCAL_ADDRESS_MASK` is declared here but not used by the subset files, so additions should verify whether existing drivers expect local address masking elsewhere.

## Test Signals
Build coverage for every K3 remoteproc driver that includes this header, plus probe tests that populate all `struct k3_rproc` fields used by common callbacks. ABI is internal to the kernel tree, so compile-time and runtime probe coverage are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_dsp_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_dsp_remoteproc.c

## Purpose
Platform driver for TI K3 C66, C71, and C7xV DSP remote processors. It binds SoC-specific internal memory definitions to the K3 common layer, programs DSP boot address through TI-SCI processor control, supports remoteproc-managed and IPC-only modes, and registers with the remoteproc core.

## Important APIs, Types, And Functions
Defines `k3_dsp_rproc_start()`, `k3_dsp_rproc_probe()`, `k3_dsp_rproc_remove()`, `k3_dsp_rproc_ops`, memory tables `c66_mems`, `c71_mems`, `c7xv_mems`, and device-data structures for each DSP class. Compatible strings include `ti,j721e-c66-dsp`, `ti,j721e-c71-dsp`, `ti,j721s2-c71-dsp`, and `ti,am62a-c7xv-dsp`.

## Control Flow
Probe gets match data and firmware name, allocates an rproc, disables recovery, conditionally installs common prepare/unprepare for local-reset devices, requests mailbox, obtains TI-SCI and device ID, gets reset and TI-SCI processor handle, requests processor control, maps internal memories, initializes reserved memories, queries initial TI-SCI power state, chooses `RPROC_DETACHED` for IPC-only mode when already powered, then registers the rproc.

Start validates that `rproc->bootaddr` satisfies the SoC-specific alignment requirement, programs TI-SCI processor config with that boot address, then calls common `k3_rproc_start()` to release reset. Remove detaches only if the remoteproc is currently attached.

## State And Persistence Behavior
Per-device state is `struct k3_rproc` in `rproc->priv`, with devm-managed resources and a devm rproc registration. `rproc->recovery_disabled = true` means crashes are not automatically recovered. IPC-only mode persists by leaving the remote DSP running and using attach/detach NOPs plus loaded resource table from reserved memory.

## Dependencies And Integration Points
Depends on TI-SCI processor and device ops, reset control, OMAP mailbox, DT memory resources named by the chosen DSP memory table, reserved memory regions, and the K3 common helper layer. Virtio/rpmsg integration flows through common mailbox and loaded resource-table handling.

## Risks
Boot address alignment differs by DSP family; incorrect firmware entry points fail before reset release. `k3_dsp_rproc_ops` does not explicitly set ELF loader callbacks, so core default ELF loader is installed by `rproc_alloc_ops()`. Recovery is disabled and common crash mailbox handling only logs. IPC-only mode depends on TI-SCI power state accurately reflecting externally booted firmware.

## Test Signals
Test all compatibles and memory tables, missing firmware-name, TI-SCI phandle/device ID errors, reset and processor-control failures, boot-address alignment failures, remoteproc mode boot/stop, IPC-only attach/detach when `is_on` reports powered, reserved-memory resource-table discovery, mailbox rpmsg traffic, and remove while attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_dsp_remoteproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_m4_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_m4_remoteproc.c

## Purpose
Platform driver for TI K3 Cortex-M4F remote processors, currently matching AM64 M4FSS. It composes the K3 common remoteproc layer with AM64 IRAM/DRAM definitions, TI-SCI/reset resources, mailbox, reserved-memory setup, and remoteproc or IPC-only mode detection.

## Important APIs, Types, And Functions
Defines `k3_m4_rproc_ops`, `k3_m4_rproc_probe()`, AM64 memory table `am64_m4_mems`, device data `am64_m4_data`, and compatible `ti,am64-m4fss`. Ops use common prepare/unprepare, start/stop, attach/detach, kick, address translation, and loaded resource table lookup.

## Control Flow
Probe gets match data and firmware name, allocates an rproc, disables recovery, fills `struct k3_rproc`, gets TI-SCI handle and device ID, gets reset control, obtains and requests TI-SCI processor control, maps internal memories, initializes reserved memory, queries TI-SCI reset/power state, marks `RPROC_DETACHED` when powered for IPC-only mode, requests mailbox, and registers the rproc with devm cleanup.

## State And Persistence Behavior
Private K3 state is devm-owned through the platform device. Local reset is used by this device data, so prepare/unprepare manage module access and local reset sequencing through common code. Like the DSP driver, recovery is disabled and IPC-only mode leaves already-powered firmware running.

## Dependencies And Integration Points
Depends on AM64 DT compatible, firmware-name, `ti,sci`, `ti,sci-dev-id`, reset control, internal resources named `iram` and `dram`, reserved-memory regions, TI-SCI processor control, mailbox, and the K3 common implementation. Virtio/rpmsg uses the common mailbox and resource table path.

## Risks
The `r_state` value from TI-SCI is queried but only `p_state` controls mode selection, so reset-state nuances do not affect attach/remoteproc choice. There is no remove callback beyond devm cleanup; active attached/running state relies on devm remoteproc removal behavior. Recovery is disabled, so production fault handling must be external. The AM64 data sets boot alignment but the M4 start path uses common `k3_rproc_start()` directly and does not validate alignment in this file.

## Test Signals
Test AM64 probe with valid and missing resources, TI-SCI errors, reserved-memory setup, mailbox request failures, remoteproc boot/stop with local reset, IPC-only attach path when powered, firmware-name parsing, IRAM/DRAM address translation, rpmsg traffic, and driver unbind while the remote processor is running or attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/ti_k3_m4_remoteproc.c -->
