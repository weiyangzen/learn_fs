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
