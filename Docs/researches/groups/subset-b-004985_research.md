# Research: subset-b-004985

This grouped report covers the libnvdimm files under `sources/distributed-fs/ceph-client/drivers/nvdimm/` assigned to subset B item `subset-b-004985`. Each section is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/btt.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/btt.c

## Purpose
`btt.c` implements the Block Translation Table runtime for NVDIMM namespaces. It discovers or creates on-media BTT arenas, exposes the resulting translated namespace as a Linux block disk, and provides sector-level power-fail atomicity by writing data to reserved free blocks before atomically updating per-LBA map metadata. The code sits below the `nd_btt` device wrapper and above the namespace byte accessors supplied by `claim.c`.

## Important APIs, Types, And Functions
The primary external entry points are `nvdimm_namespace_attach_btt()` and `nvdimm_namespace_detach_btt()`, exported for the BTT personality driver. `btt_init()` constructs a `struct btt` from an `nd_btt`, raw namespace size, LBA size, namespace UUID, and parent region. `btt_fini()` tears down the gendisk, arenas, and debugfs state. The block device operations are `btt_submit_bio()` and `btt_getgeo()`.

Arena metadata helpers include `btt_info_read()`, `btt_info_write()`, `discover_arenas()`, `create_arenas()`, `btt_arena_write_layout()`, and `btt_meta_init()`. Map/log helpers include `btt_map_read()`, `btt_map_write()`, `btt_log_read()`, `btt_flog_write()`, `log_set_indices()`, `btt_freelist_init()`, `btt_rtt_init()`, and `btt_maplocks_init()`. I/O is split through `btt_read_pg()`, `btt_write_pg()`, `btt_do_bvec()`, `btt_data_read()`, `btt_data_write()`, and optional `btt_rw_integrity()`.

The file uses `struct btt` and `struct arena_info` from `btt.h`, `struct nd_btt` and `struct nd_region` from `nd.h`, and namespace byte APIs `nvdimm_read_bytes()` / `nvdimm_write_bytes()` through the `nd_namespace_common`.

## Control Flow
Attach begins in `nvdimm_namespace_attach_btt()`: it validates that UUID, namespace, and LBA size are configured, enables the namespace with `devm_namespace_enable()`, resolves BTT version/initial offset with `nd_btt_version()`, checks minimum raw size, and calls `btt_init()`. `btt_init()` initializes in-memory state, discovers existing arenas, or creates and writes new arena metadata when no existing layout is present and the region is writable. It then allocates a block disk, sets capacity, applies region read-only state, and initializes debugfs.

Existing arena discovery reads the first info block at each arena offset. A valid BTT superblock is parsed into `arena_info`, log padding layout is detected with `log_set_indices()`, the freelist is reconstructed from the latest log entries, and RTT/map-lock arrays are allocated. If no valid metadata is found at offset zero, the instance transitions to create mode. Create mode slices the namespace into arenas up to `ARENA_MAX_SIZE`, calculates data/map/log/info offsets, initializes map and log areas, writes duplicated info blocks, and marks `INIT_READY`.

BIO submission iterates each segment and rejects segments that are larger than a page, smaller than the BTT sector size, or not sector aligned. Reads map a premap LBA to a postmap block, publish the postmap in the read tracking table, re-read the map to detect races with writes, then copy persistent data or zero-fill trimmed entries. Writes acquire a per-region lane, choose that lane's free block, wait while any RTT entry references it, write data and integrity metadata to the free block, lock the map stripe, write a log transaction with old/new map entries, then update the map. The old postmap becomes the lane's next free block.

## State And Persistence Behavior
BTT persistence is held in each arena's primary and backup `struct btt_sb`, zero-initialized map table, lane log groups, and data area. The two-phase write sequence is: write new data to a free internal block, persist a log entry that records old and new map state, then persist the map update. On startup `btt_freelist_init()` replays incomplete transactions when a log entry says a map should have moved but the map still points to the old block.

Map entries encode trim and error bits in the top two bits. BTT treats all-zero maps as initial identity mapping and `MAP_ENT_NORMAL` as a normal initialized entry. Media read errors trigger persistent error tracking by setting the map error flag. Free-list entries with error state are zero-written by `arena_clear_freelist_error()` before reuse. The read tracking table is volatile state that prevents a writer from reusing a free block while a read may still be consuming it.

Version state is stored on `nd_btt`: v1.1 uses a 4 KiB initial offset, while v2.0 starts at zero. The file writes BTT metadata only when no valid metadata exists, so already formatted namespaces are reopened by discovery rather than reformatted.

## Dependencies And Integration Points
This file integrates with the block layer (`gendisk`, queue limits, bio accounting, optional integrity metadata), libnvdimm namespace byte accessors, badblock tracking through `is_bad_pmem()`, region lane allocation through `nd_region_acquire_lane()` / `nd_region_release_lane()`, debugfs, and the BTT device wrapper in `btt_devs.c`.

`nvdimm_namespace_attach_btt()` relies on `claim.c` for `devm_namespace_enable()` and on `btt_devs.c` for version validation. The block disk name comes from `nvdimm_namespace_disk_name()` in `namespace_devs.c`. Region read-only state is synchronized through `nvdimm_check_and_set_ro()` in `bus.c`.

## Risks And Edge Cases
The power-fail protocol depends on correct atomicity assumptions for 8-byte halves of 16-byte log entries and durable namespace writes. Misordered writes or incorrect `NVDIMM_IO_ATOMIC` handling would affect recovery. `log_set_indices()` supports legacy and fixed padding layouts; unknown padding schemes fail arena discovery. `lba_to_arena()` is a linear scan, acceptable for few arenas but a scaling risk for very large namespace layouts.

Concurrency is subtle: reads rely on RTT publication and a compiler barrier, while writes spin waiting for RTT entries before reusing free blocks. Incorrect lane management or map lock indexing can produce stale reads or double allocation. Error clearing currently logs failures and has a FIXME noting BTT should become read-only if clearing fails during init. Segment alignment rejection in `btt_submit_bio()` is a functional test point for callers.

## Test Signals
Useful tests include formatting a fresh namespace and verifying `btt_meta_init()` writes valid duplicated superblocks, reopening an existing namespace and checking log replay, inducing incomplete flog/map transactions, validating both old `(0,2)` and new `(0,1)` log padding schemes, exercising badblock/error flag persistence, read-after-write under concurrent lanes, discard/trim zero-fill behavior via map flags, and read-only region attach failure when metadata is absent. Block tests should verify capacity, disk read-only propagation, integrity metadata sizes for 520/528/4104/4160/4224-byte LBAs, and bio alignment errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/btt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/btt.h -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/btt.h

## Purpose
`btt.h` defines the on-media and in-memory data structures for the NVDIMM Block Translation Table implementation. It captures the BTT arena superblock layout, log entry format, map-entry bit encoding, free-list entries, and the `struct btt` / `struct arena_info` runtime handles consumed by `btt.c` and validated by `btt_devs.c`.

## Important APIs, Types, And Constants
Key constants include `BTT_SIG`, `MAP_TRIM_MASK`, `MAP_ERR_MASK`, `MAP_LBA_MASK`, `MAP_ENT_NORMAL`, arena min/max sizes, `BTT_DEFAULT_NFREE`, and `LOG_SEQ_INIT`. Macros `ent_lba()`, `ent_e_flag()`, `ent_z_flag()`, `set_e_flag()`, and `ent_normal()` abstract map-entry encoding.

`struct log_entry` and `struct log_group` define four 16-byte log slots per lane, with two real entries and two padding entries. The header documents both legacy and corrected padding layouts. `struct btt_sb` is the 4 KiB arena info block persisted twice per arena. `struct free_entry` tracks the volatile lane free block, sub-slot, sequence, and error state.

`struct arena_info` records arena geometry, offsets, free-list/RTT/map-lock pointers, flags, and valid log indices. `struct btt` records the gendisk, arena list, namespace/device references, LBA geometry, region, initialization state, arena count, and badblocks source.

The exported declarations are `nd_btt_arena_is_valid()` and `nd_btt_version()`.

## Control Flow
This header does not execute logic, but its layout drives BTT control flow. `btt.c` uses `struct btt_sb` to discover or create arenas, `struct log_group` to recover interrupted writes, `struct free_entry` to select per-lane replacement blocks, and `arena_info` offsets to translate logical LBAs to namespace byte offsets.

The log-format comment is operational: startup scans log groups to infer whether slots `(0,1)` or `(0,2)` contain active entries, then all subsequent log reads/writes use the detected `arena->log_index[]`.

## State And Persistence Behavior
`struct btt_sb` is persistent media state. It includes BTT UUID, parent namespace UUID, geometry, flags, arena-relative offsets to data/map/log/backup info block, and a checksum. `struct log_entry` persists transaction state for map updates. `struct arena_info` and `struct btt` are volatile state reconstructed from those media structures at attach time.

The map-entry bit convention is easy to misread: normal initialized entries are represented with both top bits set, while all-zero means initial identity. Error and trim flags are encoded inversely through helper logic in `btt.c`.

## Dependencies And Integration Points
The header depends only on Linux basic types but semantically depends on `ND_MAX_LANES` from `nd.h` through `BTT_DEFAULT_NFREE` once included in implementation context. It is included by BTT core code, BTT device code, and claim code for checksum size assertions and BTT personality operations.

## Risks And Edge Cases
Any change to `struct btt_sb`, `struct log_entry`, or flag constants is an on-media format change. The 4 KiB size and checksum position are asserted elsewhere, so padding must remain stable. The legacy log padding compatibility note is essential: removing it would strand old BTT layouts. The `MAP_LBA_MASK` and top-bit flags assume 32-bit map entries and constrain maximum internal LBAs.

## Test Signals
Compile-time assertions in `claim.c` cover 4 KiB generic superblock compatibility. Runtime tests should validate checksum compatibility, old/new log padding detection, arena size boundaries, parent UUID matching, and correct interpretation of normal, trim, error, and initial map states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/btt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/btt_devs.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/btt_devs.c

## Purpose
`btt_devs.c` implements the libnvdimm `nd_btt` device wrapper. It exposes sysfs configuration for BTT instances, manages BTT device allocation and release, probes existing BTT metadata on namespaces, validates arena superblocks, and selects BTT v1.1 versus v2.0 layout rules.

## Important APIs, Types, And Functions
Public functions are `to_nd_btt()`, `is_nd_btt()`, `nd_btt_create()`, `nd_btt_arena_is_valid()`, `nd_btt_version()`, and `nd_btt_probe()`. Internal creation is handled by `__nd_btt_create()`, while `__nd_btt_probe()` reads metadata and registers a discovered device.

Sysfs attributes include `sector_size`, `uuid`, `namespace`, `size`, and `log_zero_flags`. Supported BTT sector sizes include standard and integrity-tagged sizes: 512, 520, 528, 4096, 4104, 4160, and 4224 bytes.

## Control Flow
Seed creation uses `nd_btt_create()`, which allocates an empty `nd_btt`, names it `btt<region>.<id>`, initializes the device, and asynchronously registers it. Userspace can then set UUID, sector size, and namespace while the device is unbound. Probe of an existing namespace uses `nd_btt_probe()`: it ignores forced raw namespaces, accepts only none/BTT/BTT2 claim classes, creates an attached `nd_btt`, allocates a temporary superblock, and calls `__nd_btt_probe()`.

`__nd_btt_probe()` rejects namespaces smaller than 16 MiB, resolves BTT version with `nd_btt_version()`, copies external LBA size and UUID from the superblock, then registers the BTT device. If probe fails, the namespace is detached and the device reference is dropped.

## State And Persistence Behavior
This file owns volatile `nd_btt` configuration fields: UUID, LBA size, namespace claim pointer, size reported after BTT disk attach, version, and initial offset. Persistent state is read from `struct btt_sb` on the namespace. `nd_btt_arena_is_valid()` checks signature, parent namespace UUID when present, checksum, and logs the BTT arena error flag.

`nd_btt_version()` encodes the layout split: BTT2 starts at offset 0 with version 2.0, while legacy or unclaimed/BTT namespaces start at 4 KiB with version 1.1. This offset feeds `btt.c` via `nd_btt->initial_offset`, affecting every arena read/write.

## Dependencies And Integration Points
The file depends on BTT media structures from `btt.h`, namespace attach helpers from `claim.c`, common sysfs helpers from `core.c`, and namespace capacity/UUID helpers from `namespace_devs.c`. Device registration is through the NVDIMM bus helpers in `bus.c`. The actual block disk is created later by `btt.c`.

## Risks And Edge Cases
A BTT device cannot be reconfigured while bound because UUID and sector-size helpers reject active drivers. Incorrect claim-class handling can cause v1.1/v2.0 offset mismatch and failed discovery. `nd_btt_arena_is_valid()` temporarily zeroes `super->checksum` for validation and restores it; callers must pass mutable storage. The parent UUID check allows null parent UUID for compatibility.

## Test Signals
Tests should cover seed device sysfs writes before binding, `namespace` claim rejection for already claimed namespaces, forced-raw namespace skip, BTT1 and BTT2 metadata discovery, invalid signature/checksum/parent UUID rejection, minimum capacity enforcement, and `size` returning `-ENXIO` before the BTT driver is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/btt_devs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/bus.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/bus.c

## Purpose
`bus.c` implements the private `nd` bus type, bus and DIMM character-device ioctl dispatch, asynchronous device registration/removal, badblock/poison clearing coordination, device matching, and generic NVDIMM bus/device sysfs attributes. It is the central libnvdimm integration layer between provider drivers, NVDIMM child devices, namespace/personality drivers, and userspace ndctl ioctls.

## Important APIs, Types, And Functions
Key exported functions include `to_nvdimm_bus()`, `nvdimm_to_bus()`, `nvdimm_bus_register()`, `nvdimm_bus_unregister()`, `nd_device_register()`, `nd_device_unregister()`, `__nd_driver_register()`, `nd_synchronize()`, `nd_device_notify()`, `nvdimm_region_notify()`, `nvdimm_check_and_set_ro()`, `nvdimm_clear_poison()`, `nd_cmd_dimm_desc()`, `nd_cmd_bus_desc()`, `nd_cmd_in_size()`, and `nd_cmd_out_size()`.

The file defines `nvdimm_bus_type`, `nd_bus_driver`, the `nd` class for `ndctl<N>` devices, character-device file operations for bus and DIMM ioctls, command descriptor tables for bus and DIMM ND commands, and common `modalias`, `devtype`, `numa_node`, and `target_node` attributes.

## Control Flow
Provider registration calls `nvdimm_bus_register()`, which allocates a bus, initializes lists/waitqueue/reconfiguration mutex/badrange state, assigns an ID, initializes the device, and adds it to the `nd` bus. The internal `nd_bus_driver` probes the bus, creates the `ndctl` class device, adds the bus to `nvdimm_bus_list`, and exposes provider context.

Child device registration is asynchronous by default. `nd_device_register()` sets the bus, inherits NUMA node, references parent/device, and schedules `device_add()` in a private async domain. Removal can be async or sync, using `kill_device()` to serialize races, flushing bus operations with the reconfiguration mutex, and synchronizing the async domain when needed.

Driver matching maps devices to ND device type bits, including regions, DIMMs, BTT/PFN/DAX namespace personalities, and namespace types derived from the parent region. Bus probe wraps child driver probe with provider module pinning, probe-active accounting, and region seed advancement after successful or unsupported probes.

Ioctls open on `ndctl<N>` or `dimmctl<N>` store the minor in `file->private_data`. `nd_ioctl()` finds the selected bus or DIMM under `nvdimm_bus_list`, increments `ioctl_active`, and invokes `__nd_ioctl()`. `__nd_ioctl()` validates command descriptor, support masks, read-only restrictions, variable input/output envelope sizes, maximum buffer length, provider family support for `ND_CMD_CALL`, and `clear_to_send()` policy before forwarding to provider `ndctl()`.

## State And Persistence Behavior
The file manages in-kernel bus state: global bus list, bus IDs, active probes, active ioctls, badrange lists, and async registration. It does not persist data directly, but it forwards ND commands that read/write DIMM label storage and clear poison. `nvdimm_clear_poison()` checks ARS capability, validates clear granularity and alignment, sends `ND_CMD_CLEAR_ERROR`, then updates bus badranges and region badblocks for the cleared physical range.

Bus removal waits for active ioctls to drain, synchronizes async work, unregisters children, frees badrange entries, and destroys the `ndctl` device. This makes bus lifetime dependent on both userspace file operations and child driver operations.

## Dependencies And Integration Points
`bus.c` integrates with Linux driver core, async framework, char devices, sysfs, module ownership, badblocks/badrange management, ACPI/ND command ABIs from `ndctl.h`, and libnvdimm provider callbacks in `struct nvdimm_bus_descriptor`. It coordinates with `core.c` for bus locking, `dimm_devs.c` for DIMM deletion, `namespace_devs.c` for region seed advancement, and personality drivers through `nd_device_driver`.

## Risks And Edge Cases
Ioctl envelope parsing is security-sensitive: it copies bounded input/output prefixes first to determine variable sizes, enforces `ND_IOCTL_MAX_BUFLEN`, and then copies the whole user buffer. Any descriptor mismatch can lead to wrong copy lengths. Clear-error ioctls are deliberately blocked if the affected pmem namespace is active under a driver, forcing poison clearing through pmem where page/block state can be coordinated.

Async registration/removal races are controlled by `kill_device()`, `nd_synchronize()`, and probe-active wait queues; regressions here can cause use-after-free or stale sysfs devices. Read-only file descriptors block mutating commands, but provider `clear_to_send()` can add further restrictions. Bus removal must not free badrange or destroy ndctl while ioctls are active.

## Test Signals
Tests should cover bus registration/unregistration with multiple child devices, async add/remove races, driver type matching and modalias emission, ioctl rejection for unsupported commands and read-only mutating commands, variable-sized command envelopes, `ND_CMD_CALL` family masks, active namespace protection for `ND_CMD_CLEAR_ERROR`, badblock clearing notifications, `wait_probe` flushing, NUMA attribute visibility, and disk read-only synchronization with region `ro`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/claim.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/claim.c

## Purpose
`claim.c` implements shared claim and namespace byte-access helpers for libnvdimm namespace personality devices. It attaches/detaches namespaces to BTT/PFN/DAX devices, resets idle claim devices, parses the common `namespace` sysfs store operation, computes generic 4 KiB info-block checksums, and enables raw namespace I/O mappings.

## Important APIs, Types, And Functions
Exported or shared functions include `__nd_detach_ndns()`, `nd_detach_ndns()`, `__nd_attach_ndns()`, `nd_namespace_store()`, `nd_sb_checksum()`, `devm_nsio_enable()`, and `devm_nsio_disable()`. `to_nd_pfn_safe()` supports PFN attributes reused by DAX devices.

Internal helpers include `is_idle()`, `nd_detach_and_reset()`, and `nsio_rw_bytes()`.

## Control Flow
Attach requires the caller to hold the bus reconfiguration mutex. `__nd_attach_ndns()` rejects already claimed namespaces, sets `ndns->claim`, stores the namespace pointer in the personality device, and takes a namespace device reference. Detach clears the namespace's claim, nulls the caller's pointer, and drops the reference. The public detach wrapper takes a temporary namespace reference and grabs the bus lock before calling the internal detach.

`nd_namespace_store()` is the common sysfs handler for BTT/PFN/DAX `namespace` attributes. It rejects active claim devices, accepts either an empty string for detach or a `namespace*` child name, finds the namespace under the region, checks claim-class compatibility, enforces a minimum namespace size, and attaches if unclaimed. Empty string detaches and either unregisters idle non-seed claim devices or resets BTT/PFN/DAX configuration fields.

`devm_nsio_enable()` reserves the physical resource, installs `nsio_rw_bytes()` as the namespace byte accessor, initializes badblocks, populates them from the region, and memremaps the namespace. The disable path unmaps, exits badblocks, and releases the region.

## State And Persistence Behavior
Claim state is volatile kernel device state: `nd_namespace_common.claim` and each personality's `ndns` pointer. The helper deliberately ties references to claims to prevent namespace device teardown while claimed. BTT/PFN/DAX UUIDs and modes are reset on detach if the device remains as a seed.

`nsio_rw_bytes()` performs direct persistent-memory reads and writes. Reads check badblocks and use `copy_mc_to_kernel()` so machine-check recoverable faults become `-EIO`. Writes optionally clear poison for sector-aligned non-atomic writes, then use `memcpy_flushcache()` and `nvdimm_flush()` to make data durable. The generic info-block checksum uses `nd_fletcher64()` with the final checksum field zeroed.

## Dependencies And Integration Points
The file depends on device type helpers from BTT/PFN/DAX code, namespace and region types from `nd.h`, badblocks, provider poison clearing from `bus.c`, and persistent memory mapping/flushing primitives. It is used by BTT, PFN, DAX, and namespace probe code to share claim semantics.

## Risks And Edge Cases
Locking discipline is critical: internal attach/detach asserts the bus reconfiguration mutex, while sysfs handlers must hold device and bus locks. `nd_namespace_store()` only accepts names beginning with `namespace` or empty strings, preventing arbitrary child claims. Minimum capacity is hard-coded to 16 MiB for claim hosting. `nsio_rw_bytes()` has distinct behavior for atomic writes: it refuses to clear poison for atomic or unaligned writes, returning `-EIO` instead.

## Test Signals
Tests should cover claim attach/detach, claim-class mismatch rejection, attaching already claimed namespaces, detaching seed and non-seed claim devices, namespace capacity checks, checksum compatibility with BTT/PFN superblocks, badblock read errors, poison clear on aligned writes, no poison clear on atomic writes, namespace resource reservation failure, and device-reference lifetime around detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/claim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/core.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/core.c

## Purpose
`core.c` provides libnvdimm module initialization, global bus locking helpers, shared physical-memory mapping cache, checksum and sysfs utility helpers, bus-level sysfs attributes, firmware activation controls, badrange insertion, and top-level init/exit sequencing for the NVDIMM core.

## Important APIs, Types, And Functions
Exported helpers include `nvdimm_bus_lock()`, `nvdimm_bus_unlock()`, `is_nvdimm_bus_locked()`, `devm_nvdimm_memremap()`, `nd_fletcher64()`, `to_nd_desc()`, `to_nvdimm_bus_dev()`, `nd_uuid_store()`, `nd_size_select_show()`, `nd_size_select_store()`, and `nvdimm_bus_add_badrange()`.

The internal `struct nvdimm_map` caches shared memremap/ioremap mappings by physical offset on a bus, using a bus list and kref. Bus sysfs attributes include `commands`, `wait_probe`, `provider`, and firmware `capability` / `activate`.

## Control Flow
The bus lock helpers walk from any child device to the parent `nvdimm_bus` and lock/unlock its `reconfig_mutex`. `devm_nvdimm_memremap()` runs under this lock, finds or allocates a shared map, takes a kref, and registers a devm release action that drops the map and unmaps/releases the physical region when the last user exits.

`nd_uuid_store()` and `nd_size_select_store()` are common sysfs store helpers that reject writes while a driver is bound. `wait_probe_show()` optionally calls provider `flush_probe()`, synchronizes NVDIMM async work, then locks/unlocks all child regions and namespaces to flush probe/remove side effects before returning.

Firmware activation sysfs exposes bus-level firmware capability and state. Writes to `firmware/activate` accept `live` or `quiesce`, check provider state, and either call provider activation directly or through `hibernate_quiet_exec()` for quiesced activation.

Initialization calls `nvdimm_bus_init()`, `nvdimm_init()`, `nd_region_init()`, and `nd_label_init()` in order. Exit warns if buses remain registered, then unregisters regions, DIMMs, bus infrastructure, and DIMM IDA state.

## State And Persistence Behavior
Core state includes global `nvdimm_bus_list`, `nvdimm_bus_list_mutex`, mapping-list cache entries, provider badranges, and firmware state obtained through provider callbacks. It does not persist labels directly, but its checksum helper is used for persistent superblocks and labels. `devm_nvdimm_memremap()` persistently reserves physical address windows for safe shared mappings until all devm users release them.

Firmware activation changes persistent device firmware state through provider operations, with sysfs reporting capability and armed/busy/idle state.

## Dependencies And Integration Points
`core.c` depends on Linux driver core, resource reservation, memremap/ioremap, suspend/hibernate quiet execution, sysfs, and provider `nvdimm_bus_descriptor` callbacks. It is used by nearly every file in this subset for bus locking, UUID/LBA sysfs parsing, checksums, and init sequencing.

## Risks And Edge Cases
The shared mapping cache keys only by offset, so callers must request consistent size/flags for a given offset; mismatched requests would reuse an incompatible mapping. The code warns if mapping allocation is attempted without the bus lock. Firmware activation must correctly gate unsupported states and avoid live activation when quiesce is requested. `nd_uuid_store()` frees the old UUID before allocating the new copy, so callers must handle allocation failure leaving no UUID.

## Test Signals
Tests should exercise bus-lock assertions, shared memremap kref reuse/release, mapping failure cleanup, UUID and size selection rejection while bound, `wait_probe` synchronization, firmware sysfs visibility with and without provider ops, live versus quiesce activation paths, badrange insertion, and init failure unwind at each subsystem boundary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/dax_devs.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/dax_devs.c

## Purpose
`dax_devs.c` implements the `nd_dax` device wrapper for NVDIMM namespaces configured for device-DAX mode. It reuses `struct nd_pfn` infrastructure for DAX metadata, creates DAX seed devices, and probes existing DAX info blocks on namespaces.

## Important APIs, Types, And Functions
Public functions are `to_nd_dax()`, `is_nd_dax()`, `nd_dax_create()`, and `nd_dax_probe()`. Internal allocation is handled by `nd_dax_alloc()`, while release uses `nd_dax_release()`.

The `nd_dax` device type is named `nd_dax` and uses `nd_pfn_attribute_groups`, reflecting that DAX and PFN devices share sysfs attributes around namespace, UUID, alignment, and mode.

## Control Flow
`nd_dax_create()` creates a seed DAX device only for memory regions, allocates an ID from the region's `dax_ida`, initializes the embedded PFN device through `nd_pfn_devinit()`, and registers it. `nd_dax_probe()` ignores forced-raw namespaces, accepts only none/DAX claim classes, allocates and attaches a DAX device under the bus lock, allocates a PFN superblock buffer, validates it with `nd_pfn_validate(nd_pfn, DAX_SIG)`, and registers or tears down the device based on validation.

## State And Persistence Behavior
Volatile state is held in `struct nd_dax`, whose first member is `struct nd_pfn`; this lets PFN helpers operate on DAX devices. Persistent state is the namespace's PFN/DAX info block validated by `nd_pfn_validate()` with `DAX_SIG`. Release detaches the namespace, frees the DAX ID, UUID, and device object.

## Dependencies And Integration Points
The file depends on `pfn.h` for DAX signatures and PFN helpers, `claim.c` for namespace attach/detach, `namespace_devs.c` for claim class and forced raw behavior, and `bus.c` for device registration. The actual device-DAX runtime is outside this file; this wrapper prepares libnvdimm device state.

## Risks And Edge Cases
The shared PFN/DAX representation requires correct `to_nd_pfn_safe()` behavior elsewhere; treating a DAX device as a standalone PFN container incorrectly would corrupt offsets. Probe failure after attachment must detach and drop the device to avoid stale claims. Forced raw bypass and claim-class filtering are essential to avoid auto-creating DAX wrappers for raw or BTT/PFN namespaces.

## Test Signals
Tests should cover seed creation only for memory regions, ID allocation failure cleanup, forced raw skip, claim-class rejection, valid DAX info-block registration, invalid signature detach/put behavior, sysfs attribute reuse from PFN, and release freeing the region `dax_ida` ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/dax_devs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/dimm.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/dimm.c

## Purpose
`dimm.c` is the NVDIMM DIMM driver. It probes `nvdimm` devices, initializes per-DIMM driver data, unlocks or marks security/label state, reads namespace label-area geometry and label data, reserves DPA for active labels, and registers/unregisters the DIMM driver.

## Important APIs, Types, And Functions
The main driver callbacks are `nvdimm_probe()` and `nvdimm_remove()`. Module lifecycle entry points are `nvdimm_init()` and `nvdimm_exit()`, registering an `nd_device_driver` with type `ND_DRIVER_DIMM`.

The probe constructs `struct nvdimm_drvdata`, initializes its DPA resource root, namespace index state, device reference, and kref, then delegates most work to helpers in `dimm_devs.c`, `label.c`, and security code.

## Control Flow
Probe first sets up security event tracking. It checks whether config-data commands are available; `-ENOTTY` is treated as nonfatal for non-aliased DIMMs. If labels are supported, it clears stale locked state, allocates driver data, attempts security unlock, initializes namespace area geometry, and handles `-EACCES` specially as locked capacity. It then reads and validates label data; `-EACCES` here marks the DIMM locked and fails probe because regions cannot safely parse labels.

After label data is available, the driver takes the bus lock and, if a current namespace index exists, reserves DPA for all active labels through `nd_label_reserve_dpa()`. Successful reservation sets the DIMM labeling flag. Remove clears driver data under the bus lock and drops the driver-data kref.

## State And Persistence Behavior
Persistent label state is read from DIMM config data into `ndd->data`. Probe reserves volatile resource-tree entries under `ndd->dpa` for active labels so namespace creation and allocation code can reason about used DPA. Security state is refreshed during probe and may mark the DIMM locked, affecting later namespace probing.

## Dependencies And Integration Points
The file depends on security helpers in `dimm_devs.c`/security support, config-data access in `dimm_devs.c`, label parsing in `label.c`, DPA reservation, and bus locking from `core.c`. It registers with the NVDIMM bus infrastructure from `bus.c`.

## Risks And Edge Cases
The distinction between `-ENOTTY` and `-ENXIO` from config-data support affects whether a DIMM can probe without labels. Locked DIMMs can still enumerate labels if only capacity is locked, but label-data access failures stop probe. If DPA reservation fails after labels are read, probe unwinds and drops driver data, preventing regions from consuming ambiguous label state.

## Test Signals
Tests should cover DIMMs without config-data commands, locked DIMM status during namespace-area and label-data reads, security unlock failure tolerance, label validation failure with no current index, active label DPA reservation, labeling flag setting, probe failure unwind, and remove clearing `dev_get_drvdata()` plus releasing the final kref.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/dimm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/dimm_devs.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/dimm_devs.c

## Purpose
`dimm_devs.c` implements NVDIMM device creation helpers, DIMM sysfs attributes, config-data command wrappers, DIMM driver-data lifetime, security and firmware sysfs plumbing, DPA resource allocation/accounting, and DIMM count validation. It is the core per-DIMM support file behind the `nvdimm` device type.

## Important APIs, Types, And Functions
Config-data APIs are `nvdimm_check_config_data()`, `nvdimm_init_nsarea()`, `nvdimm_get_config_data()`, and `nvdimm_set_config_data()`. Device/lifetime APIs include `__nvdimm_create()`, `nvdimm_delete()`, `to_nvdimm()`, `to_ndd()`, `get_ndd()`, `put_ndd()`, `nvdimm_drvdata_release()`, `nvdimm_name()`, `nvdimm_kobj()`, `nvdimm_cmd_mask()`, and `nvdimm_provider_data()`.

Security and firmware helpers include `nvdimm_security_setup_events()`, `nvdimm_in_overwrite()`, `nvdimm_security_freeze()`, and sysfs attributes `security`, `frozen`, `firmware/activate`, and `firmware/result`. DPA helpers include `nd_pmem_max_contiguous_dpa()`, `nd_pmem_available_dpa()`, `nvdimm_allocate_dpa()`, `nvdimm_free_dpa()`, `nvdimm_allocated_dpa()`, and `nvdimm_bus_check_dimm_count()`.

## Control Flow
`__nvdimm_create()` allocates a DIMM ID and object, records provider data, command mask, flush hints, security and firmware ops, initializes security flags before sysfs visibility, initializes the device, and registers it synchronously or asynchronously depending on flags. `nvdimm_delete()` marks security frozen during shutdown, cancels delayed overwrite work, drops pending work references, and synchronously unregisters the device.

Config-data wrappers validate command support, enforce bounds against `nsarea.config_size`, split reads/writes by `max_xfer`, and call provider `ndctl()` with `ND_CMD_GET_CONFIG_DATA` or `ND_CMD_SET_CONFIG_DATA`. `nvdimm_init_nsarea()` obtains label-area geometry through `ND_CMD_GET_CONFIG_SIZE`.

Sysfs attributes expose command names, flags, active/idle state, available label slots, security state/mutation, firmware arm/disarm, and firmware result. Visibility depends on security flags/ops and provider firmware capability.

DPA helpers operate on the `ndd->dpa` resource tree under the bus lock. Availability checks align free ranges to per-DIMM region alignment and account for existing allocations. Max-contiguous checks temporarily reserve all free pmem space as `pmem-reserve`, scan it, then release the reservation.

## State And Persistence Behavior
The file maintains volatile `struct nvdimm` state, `struct nvdimm_drvdata`, and resource-tree DPA allocations that mirror persistent namespace labels. Config-data read/write commands persist label indexes and labels through provider firmware/ACPI methods. Security sysfs can persistently change DIMM passphrase/security state through `nvdimm_security_store()` and freeze/overwrite operations, while firmware sysfs arms activation state.

`nvdimm_drvdata_release()` frees all DPA resource allocations under the bus lock, releases cached label data, frees driver data, and drops the DIMM device reference.

## Dependencies And Integration Points
This file integrates with provider `nvdimm_bus_descriptor.ndctl`, security ops, firmware ops, label helpers, namespace allocation code, bus device registration, Linux resource trees, sysfs, delayed work, and badblock/flush infrastructure. `dimm.c` calls its config and lifetime helpers during probe/remove.

## Risks And Edge Cases
Config-data command sizes are provider constrained; incorrect `max_xfer` handling can truncate label reads/writes. `to_ndd()` warns if called without the bus lock, since the driver data can disappear during DIMM remove. Available-label reporting subtracts one slot as a reserve and warns on underflow. DPA alignment failures return zero availability, which can look like no capacity rather than explicit corruption. Security operations must not run during overwrite or active region use.

## Test Signals
Tests should cover command support detection, config-data chunking and bounds checks, provider command status failures, driver-data kref release freeing DPA resources, sysfs visibility for security/firmware combinations, freeze/overwrite busy behavior, DPA allocation/free/merge accounting, available label slot reporting, active/idle state under region use, and DIMM count checks after async registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/dimm_devs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/e820.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/e820.c

## Purpose
`e820.c` is a small platform driver that exposes legacy e820 type-12 persistent memory ranges as libnvdimm pmem regions. It creates an NVDIMM bus named `e820`, walks legacy persistent-memory resources, and registers each range as a pmem region.

## Important APIs, Types, And Functions
The platform driver callbacks are `e820_pmem_probe()` and `e820_pmem_remove()`. `e820_register_one()` converts each `struct resource` from the iomem walk into an `nd_region_desc` and calls `nvdimm_pmem_region_create()`.

## Control Flow
Probe initializes a static `nvdimm_bus_descriptor` with provider name `e820` and module owner, registers an NVDIMM bus under the platform device, stores it as driver data, then calls `walk_iomem_res_desc()` for `IORES_DESC_PERSISTENT_MEMORY_LEGACY`. Each matching resource gets target NUMA node information, online NUMA node mapping, and `ND_REGION_PAGEMAP` set before region creation. On any failure, the bus is unregistered and an error is logged.

Remove retrieves the bus from platform driver data and unregisters it, which cascades through bus cleanup and child device unregister paths.

## State And Persistence Behavior
This driver does not persist labels or metadata; it translates firmware-provided e820 persistent memory ranges into libnvdimm runtime devices. The static descriptor's provider identity is stable for the driver's lifetime. Region state derives from system firmware memory maps.

## Dependencies And Integration Points
The file depends on platform driver infrastructure, `walk_iomem_res_desc()`, NUMA helpers, memory hotplug target-node mapping, and libnvdimm region creation APIs. It provides a bus provider path for systems without ACPI NFIT-style NVDIMM descriptions.

## Risks And Edge Cases
Because the descriptor is static, the driver assumes only one effective provider configuration. If no legacy pmem resources are found, probe fails and unregisters the bus. NUMA target node may be offline, so `numa_map_to_online_node()` is used for allocation locality while preserving the physical target node separately.

## Test Signals
Tests should cover systems with zero, one, and multiple e820 pmem ranges; probe failure unwind after bus registration; correct NUMA and target-node values; `ND_REGION_PAGEMAP` propagation; and remove-triggered bus unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/e820.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/label.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/label.c

## Purpose
`label.c` implements NVDIMM and CXL namespace label parsing, validation, allocation, garbage collection, claim-class encoding, and persistent label updates. It owns the copy-on-write namespace-index protocol used to safely update DIMM label storage and the logic that maps active labels to DPA resource reservations.

## Important APIs, Types, And Functions
Public functions include `sizeof_namespace_label()`, `nvdimm_num_label_slots()`, `sizeof_namespace_index()`, `nd_label_reserve_dpa()`, `nd_label_data_init()`, `nd_label_active_count()`, `nd_label_active()`, `nd_label_alloc_slot()`, `nd_label_free_slot()`, `nd_label_nfree()`, `nsl_validate_type_guid()`, `nsl_get_claim_class()`, `nd_pmem_namespace_label_update()`, and `nd_label_init()`.

Validation helpers include `best_seq()`, `__nd_label_validate()`, `nd_label_validate()`, `nsl_validate_checksum()`, `slot_valid()`, and label access helpers from `nd.h`. Update helpers include `nd_label_write_index()`, `__pmem_label_update()`, `init_labels()`, `del_labels()`, and claim-class GUID/UUID conversion functions.

## Control Flow
`nd_label_data_init()` reads the DIMM config-data area. It first computes the maximum possible index size using 128-byte labels, allocates the full config-data buffer, reads enough bytes to validate both namespace indexes, probes label size by trying 128 and 256 bytes, identifies the current index, copies it to the next index staging area, then reads only active labels based on the free bitmap.

Validation checks namespace-index signature, version-implied label size, checksum, nonzero sequence, offsets, index size, and label-slot bounds. If both indexes are valid, `best_seq()` chooses the active one using the two-bit sequence progression. Active label iteration walks clear bits in the free bitmap and verifies slot number plus checksum.

Label updates are copy-on-write. `nd_pmem_namespace_label_update()` first writes labels with `NSLABEL_FLAG_UPDATING` for all mappings, then rewrites them without the flag after all mappings succeed. `__pmem_label_update()` allocates a free slot from the next index, fills a new label with UUID/name/flags/position/cookie/DPA/size/LBA/claim class/checksum, writes the label, reaps old labels for the same UUID or marked victims, then writes the next namespace index with an incremented sequence. Only after index write success does it update in-memory label tracking.

Delete frees slots for matching UUIDs, may clear label tracking when no active labels remain, and writes a new index. Initial label-area creation writes both namespace indexes with initialized free bitmaps and sequences.

## State And Persistence Behavior
Persistent state lives in two namespace indexes and an array of labels in DIMM config-data storage. Indexes are never updated in place as current; the alternate index is staged and written with a new sequence, then current/next pointers swap in memory. Labels are also written into free slots before the index that references them becomes active. This protects against partial writes and lets startup recover by choosing the best valid index.

The code supports EFI labels and CXL labels. EFI labels use GUIDs and interleave-set cookies; CXL labels use UUIDs for equivalent type and abstraction fields and treat some EFI concepts as always valid. DPA reservations mirror active labels in volatile resource trees using IDs like `pmem-<uuid>`.

## Dependencies And Integration Points
The file depends on DIMM config-data command wrappers in `dimm_devs.c`, checksum helper `nd_fletcher64()` from `core.c`, DPA resource allocation in `dimm_devs.c`, namespace update requests from `namespace_devs.c`, and interleave-set cookies/type GUIDs from region code. It initializes known BTT/PFN/DAX/CXL GUIDs and UUIDs at libnvdimm startup.

## Risks And Edge Cases
Label-size auto-detection must avoid trusting unvalidated media. Sequence comparison uses only two bits, so invalid equal or zero sequences are rejected. The update protocol can leave `UPDATING` labels if interrupted between first and second passes; readers and tooling must understand that flag. Slot allocation requires the bus lock; missing locking can race with namespace provisioning. The code preserves unknown claim classes by not overwriting existing abstraction identifiers when claim class is unknown.

## Test Signals
Tests should cover empty/invalid label areas, valid single and dual indexes, sequence wrap behavior, 128-byte and 256-byte EFI labels, CXL label fields, checksum failures, free bitmap slot allocation/free, active label counting, DPA reservation from labels, namespace grow/shrink/delete label updates, interrupted update with `UPDATING`, claim-class GUID/UUID mapping, and label-area initialization from scratch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/label.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/label.h -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/label.h

## Purpose
`label.h` defines the persistent namespace label formats and label-management API for libnvdimm. It covers UEFI namespace indexes, EFI namespace labels, CXL region and namespace labels, known abstraction GUID/UUID strings, label flags, and helper declarations used by label, DIMM, namespace, and BTT code.

## Important APIs, Types, And Constants
Important constants include namespace-index signature and alignment values, label UUID/name sizes, `NSLABEL_FLAG_ROLABEL`, `NSLABEL_FLAG_LOCAL`, `NSLABEL_FLAG_BTT`, `NSLABEL_FLAG_UPDATING`, BTT info constants, label minimum size, and known GUID/UUID strings for BTT, BTT2, PFN, DAX, CXL region, and CXL namespace.

Persistent structures are `struct nd_namespace_index`, `struct cxl_region_label`, `struct nvdimm_efi_label`, `struct nvdimm_cxl_label`, and the union wrapper `struct nd_namespace_label`. `struct nd_label_id` holds resource names such as `pmem-<namespace uuid>`.

The inline `nd_label_next_nsindex()` returns the alternate index for copy-on-write updates, or `-1` when no valid index exists. Declared APIs include label-data initialization, index sizing, active-label iteration, slot allocation/free, free count, and `nd_pmem_namespace_label_update()`.

## Control Flow
This header does not perform runtime control flow beyond `nd_label_next_nsindex()`. Its layouts drive validation and updates in `label.c`: namespace index blocks describe the active label array and free bitmap, while namespace labels describe per-DIMM pieces of a namespace and their claim personality.

## State And Persistence Behavior
All major structures in this file are on-media config-data formats. `nd_namespace_index` is the label set superblock with sequence, offsets, size, checksum, and free bitmap. EFI labels carry namespace UUID/name, flags, interleave information, DPA range, slot, optional type/abstraction GUIDs, and checksum. CXL labels use CXL table layouts and UUIDs for type/abstraction identities.

Because these layouts are persistent ABI, field order, sizes, endianness annotations, and reserved bytes are compatibility-sensitive. The `NSLABEL_FLAG_UPDATING` flag is part of the update protocol.

## Dependencies And Integration Points
The header depends on `linux/ndctl.h`, sizes, UUID/GUID, and I/O types. It is included by `nd.h` for label accessors, `label.c` for validation/update logic, `dimm.c`/`dimm_devs.c` for label storage handling, and `namespace_devs.c` for namespace construction and updates.

## Risks And Edge Cases
Persistent structure changes can break existing DIMM labels. EFI label fields past `align` must be gated by `efi_namespace_label_has()` in `nd.h`, because older label sizes do not contain later fields. CXL and EFI labels differ in semantics; code must not assume interleave cookies or GUID fields exist for CXL. The free bitmap may include padding bits that must remain zero.

## Test Signals
Tests should validate exact structure sizes for supported label versions, namespace-index free bitmap rounding, alternate-index selection, EFI v1.1/v1.2 field availability, CXL label parsing, GUID/UUID constant parsing, and update behavior involving `NSLABEL_FLAG_UPDATING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/namespace_devs.c -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/namespace_devs.c

## Purpose
`namespace_devs.c` implements NVDIMM namespace device creation, discovery from labels, namespace sysfs attributes, DPA allocation changes, UUID/label updates, claim-class selection, page-map policy, and seed-device creation for namespace/BTT/PFN/DAX provisioning. It translates DIMM labels and region mappings into `nd_namespace_pmem` or `nd_namespace_io` devices.

## Important APIs, Types, And Functions
Public functions include `nd_is_uuid_unique()`, `pmem_should_map_pages()`, `pmem_sector_size()`, `nvdimm_namespace_disk_name()`, `nd_dev_to_uuid()`, `__reserve_free_pmem()`, `release_free_pmem()`, `__nvdimm_namespace_capacity()`, `nvdimm_namespace_capacity()`, `nvdimm_namespace_locked()`, `nvdimm_namespace_common_probe()`, `devm_namespace_enable()`, `devm_namespace_disable()`, `nd_region_create_ns_seed()`, `nd_region_create_dax_seed()`, `nd_region_create_pfn_seed()`, `nd_region_create_btt_seed()`, and `nd_region_register_namespaces()`.

Major internal flows include namespace sysfs stores for `alt_name`, `size`, `uuid`, `sector_size`, `holder_class`, and `force_raw`; DPA allocation helpers `scan_allocate()`, `grow_dpa_allocation()`, `shrink_dpa_allocation()`, and `merge_dpa()`; label scanning helpers `create_namespace_pmem()`, `scan_labels()`, and `create_namespaces()`; and active label lifecycle helpers `init_active_labels()` / `deactivate_labels()`.

## Control Flow
Region activation calls `nd_region_register_namespaces()`. It locks the bus, initializes active labels for each mapping by taking `nvdimm_drvdata` references and incrementing DIMM busy counts, determines namespace type, and creates either a direct I/O namespace or label-derived pmem namespaces. Each created device gets an ID/name, lockdep class, and async registration; the first registered namespace becomes the region seed.

Label scanning starts from mapping 0, skips labels outside the mapping, detects conflicting extents with the same UUID, and calls `create_namespace_pmem()`. That function validates interleave-set cookies, checks every mapping has exactly one compatible label at each position, validates DPA ranges against NFIT mappings, moves selected labels to the front of each mapping list, copies UUID/name/LBA/claim class from position 0, sums raw sizes, and sets the namespace resource. If no labels are discovered, it publishes a zero-sized pmem namespace for userspace provisioning.

Sysfs mutation paths take the device lock and bus lock, wait for probe idleness where needed, reject active drivers or claims, mutate in-memory namespace fields or DPA resources, then call `nd_namespace_label_update()` to persist label changes. Size changes allocate or free per-DIMM DPA across mappings with alignment checks and may unregister non-seed zero-sized namespaces.

## State And Persistence Behavior
Namespace runtime state includes namespace device objects, UUIDs, alternate names, LBA sizes, resources, claim class, force-raw flag, and region seed pointers. Persistent state is updated through label writes in `label.c` whenever size, UUID, name, sector size, or holder class changes on pmem namespaces.

DPA allocations are represented as volatile resources under each DIMM's `ndd->dpa`, named by label ID. Size growth scans valid free holes, respects region alignment and contiguity, and can grow adjacent existing resources. Shrink scans from the end and frees or adjusts resources. `nd_namespace_pmem_set_resource()` converts DPA allocation offsets back to SPA resource ranges for the namespace device.

`force_raw` changes runtime mapping policy but is just a namespace field in this file. `pmem_should_map_pages()` decides whether raw pmem should use struct-page backed memremap based on config, region flags, BTT/PFN exclusions, force-raw, system RAM overlap, and architecture memremap mode.

## Dependencies And Integration Points
The file integrates with label APIs, DIMM DPA resource APIs, region/interleave metadata, BTT/PFN/DAX seed creation, claim attach/probe helpers, PMEM mapping policy, Linux sysfs/device core, IDA allocation, badblock-aware namespace enabling, and the NVDIMM bus lock. It is a central bridge between persistent labels and user-visible namespace devices.

## Risks And Edge Cases
Provisioning is highly lock-sensitive: UUID uniqueness and DPA resource trees require the bus lock. Namespace mutation while a driver or claim is active is rejected to avoid changing backing storage under users. Rename is blocked if old labels already exist in active label lists because updating UUIDs in place could lose the namespace. Mixed label versions across mappings can make BTT claim-class selection fail. Alignment errors often manifest as zero available capacity or `-EINVAL`.

Label scan tolerates alternate interleave-set cookies for compatibility but rejects missing positions, duplicate UUIDs, invalid DPA ranges, and conflicting extents. Zero-size namespaces are used as seeds, so tests must distinguish seed deletion behavior from ordinary namespace deletion.

## Test Signals
Tests should cover namespace discovery from complete and incomplete label sets, alternate-cookie acceptance, conflicting extents, DPA range validation, zero-label seed creation, namespace size grow/shrink/delete, UUID uniqueness and rename blocking, holder-class persistence for BTT/PFN/DAX, BTT v1/v2 claim-class selection from label versions, sector-size updates, force-raw mode, `pmem_should_map_pages()` policy branches, locked DIMM rejection, and region namespace registration partial failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/namespace_devs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd-core.h -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/nd-core.h

## Purpose
`nd-core.h` is the private libnvdimm core header. It defines internal `struct nvdimm_bus` and `struct nvdimm`, declares global bus state, exposes internal bus/device/region/label/namespace helper prototypes, and provides configuration fallbacks for optional security and claim support.

## Important APIs, Types, And Declarations
The key private types are `struct nvdimm_bus` and `struct nvdimm`. The bus holds provider descriptor, waitqueue, global list link, device, ID, probe/ioctl activity counters, mapping cache list, reconfiguration mutex, and badrange state. The DIMM holds provider data, command mask, device, busy counter, ID, flush hints, security state/ops/work, and firmware ops.

Declarations cover bus initialization, bus walking, ndctl device creation/destruction, async synchronization, device registration, region seed creation, UUID uniqueness, mapping label cleanup, DPA allocation queries, namespace claim attach/detach, namespace sysfs store, safe PFN conversion, and namespace I/O enable/disable.

The inline `nvdimm_security_flags()` calls provider security ops and warns if mutually exclusive security state bits are reported together.

## Control Flow
This header routes cross-file calls rather than executing high-level logic. It establishes which helpers are internal to libnvdimm and which compile to stubs when `CONFIG_NVDIMM_KEYS` or `CONFIG_ND_CLAIM` is disabled. Device and namespace files rely on these declarations to call across module boundaries without exposing all internals publicly.

## State And Persistence Behavior
The structures define volatile kernel state for buses and DIMMs. Security state mirrors persistent or hardware-backed DIMM security properties, but the header itself only stores cached flags and operation pointers. Badrange state records known bad physical ranges for the bus. Mapping cache state supports shared memremap lifetime.

## Dependencies And Integration Points
`nd-core.h` includes public libnvdimm/device/mutex/nd headers and the private `nd.h`. It is included by most implementation files in this subset. It binds together provider callbacks, NVDIMM bus registration, DIMM devices, region creation, namespace labels, BTT/PFN/DAX seeds, and optional security/claim features.

## Risks And Edge Cases
Because this header exposes private structure layouts across files, changes affect many compilation units. Security state validation warns on providers that report incompatible flags but does not repair them. Optional stubs returning `-EOPNOTSUPP` or `-ENXIO` must match callers' expectations; otherwise features may silently disappear under configuration changes.

## Test Signals
Test signals are mainly compile/config based: builds with and without `CONFIG_NVDIMM_KEYS`, `CONFIG_ND_CLAIM`, BTT, PFN, and DAX should validate stub behavior. Runtime tests should watch for security state warnings, bus activity counters, namespace attach/detach behavior, and badrange propagation across files that consume this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd.h -->
# sources/distributed-fs/ceph-client/drivers/nvdimm/nd.h

## Purpose
`nd.h` is the main private libnvdimm type and helper header shared by namespace, DIMM, region, label, BTT, PFN, and DAX code. It defines core runtime structures, label field accessors for EFI versus CXL formats, region/mapping state, claim-device structures, feature stubs, and many cross-file function prototypes.

## Important APIs, Types, And Declarations
Major types include `struct nvdimm_drvdata`, `struct nd_region_data`, `struct nd_mapping`, `struct nd_region`, `struct nd_btt`, `struct nd_pfn`, `struct nd_dax`, and generic `struct nd_gen_sb`. Important enums include NVDIMM I/O constants, label flags, mapping lock classes, PFN modes, and async modes.

The header provides many static inline label accessors: `nsl_get/set_name`, slot, checksum, flags, DPA, rawsize, isetcookie, position, nlabel, nrange, LBA size, UUID, and raw UUID bytes. These hide EFI/CXL label layout differences. Other inlines include namespace index pointer helpers, `efi_namespace_label_has()`, DPA iteration macros, `nsl_validate_nlabel()`, `nd_inc_seq()`, `nd_info_block_reserve()`, and `is_bad_pmem()`.

Function declarations cover device registration, DIMM config data, security, BTT/PFN/DAX creation/probe/validation, region namespace registration, bus locking, DPA allocation, namespace capacity/locking/probe, badblock population, namespace enable/disable, PFN setup, region activation, disk naming, sector size, and pmem page-mapping policy.

## Control Flow
The header centralizes cross-file control contracts. For example, namespace code uses label accessors to interpret active labels, label code uses region/mapping definitions to persist updates, BTT/PFN/DAX wrappers use claim-device structures, and bus code uses registration prototypes. Feature-conditioned inline stubs return clean failure values when BTT/PFN/DAX/claim support is disabled.

The label accessor flow is especially important: callers pass `nvdimm_drvdata`, and the accessor chooses CXL or EFI fields based on `ndd->cxl`. This avoids scattering format checks across allocation and discovery code.

## State And Persistence Behavior
`struct nvdimm_drvdata` caches persistent label storage (`data`), namespace-area geometry, EFI/CXL label size mode, current/next namespace indexes, and the volatile DPA resource root. `struct nd_region` holds persistent-memory region geometry, mappings, badblocks, seed devices, lane state, and flush operation. `struct nd_btt`, `struct nd_pfn`, and `struct nd_dax` hold claim personality configuration backed by persistent info blocks or labels.

`struct nd_gen_sb` defines the common 4 KiB checksum shape for BTT/PFN info blocks. Label accessors read and write little-endian persistent fields and must preserve ABI-specific differences.

## Dependencies And Integration Points
`nd.h` depends on public libnvdimm, badblocks, block device, device, mutex, ndctl, types, and `label.h`. It is included by almost every libnvdimm implementation file and bridges to external PMEM, region, PFN, DAX, and security code not all present in this subset.

## Risks And Edge Cases
Inline helper mistakes propagate broadly and may corrupt persistent labels. `efi_namespace_label_has()` must gate access to newer EFI label fields for older label sizes. `nd_inc_seq()` encodes the namespace-index sequence cycle used for copy-on-write persistence; changing it breaks index selection. Optional stubs must preserve caller semantics for disabled configs. `is_bad_pmem()` assumes 512-byte sector units for badblock queries.

## Test Signals
Tests should cover EFI and CXL label accessor round trips, old EFI label-size field gating, namespace-index pointer math, DPA iteration macros, sequence progression, BTT/PFN/DAX config-off builds, badblock checks, claim personality structure layout expectations, and region/mapping state consumed by namespace discovery and DPA allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvdimm/nd.h -->
