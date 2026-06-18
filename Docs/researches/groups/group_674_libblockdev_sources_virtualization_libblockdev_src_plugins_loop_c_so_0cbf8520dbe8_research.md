# Group Research: group_674_libblockdev_sources_virtualization_libblockdev_src_plugins_loop_c_so_0cbf8520dbe8

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/loop.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/loop.c

## Purpose

`loop.c` implements libblockdev's loop-device plugin. It exposes GLib-style API wrappers around Linux loop ioctls, `/dev/loop-control`, `/dev/loopN`, and sysfs loop metadata so callers can create, inspect, resize, modify, and tear down loop devices.

All public operations use byte units and return `GError` details through the `BD_LOOP_ERROR` domain.

## Main Operations

- `bd_loop_init()` / `bd_loop_close()` are no-op plugin lifecycle hooks.
- `bd_loop_is_tech_avail()` reports all loop tech/mode combinations as supported by this implementation.
- `bd_loop_info()` opens a loop device, issues `LOOP_GET_STATUS64`, translates `lo_flags` into `BDLoopInfo`, and reads `/sys/class/block/<loop>/loop/backing_file`.
- `bd_loop_get_loop_name()` scans `/sys/block/loop*/loop/backing_file` and returns the loop device whose backing file exactly matches the requested path.
- `bd_loop_setup()` opens a file read-write, then delegates to `bd_loop_setup_from_fd()`.
- `bd_loop_setup_from_fd()` allocates a free loop device through `/dev/loop-control`, binds the provided fd with `LOOP_SET_FD`, applies status with `LOOP_SET_STATUS64`, optionally sets logical sector size with `LOOP_SET_BLOCK_SIZE`, and returns the loop name.
- `bd_loop_teardown()` detaches the backing file with `LOOP_CLR_FD`.
- `bd_loop_set_autoclear()` reads loop status, toggles `LO_FLAGS_AUTOCLEAR`, and writes status back.
- `bd_loop_set_capacity()` forces the loop driver to reread backing-file size using `LOOP_SET_CAPACITY`.

## Implementation Notes

`bd_loop_setup_from_fd()` serializes `LOOP_CTL_GET_FREE` with a static `GMutex` because concurrent access to `/dev/loop-control` is treated as unsafe in practice. Both status-setting and capacity-changing retry up to 10 times on `EAGAIN`, sleeping 100 ms between attempts.

The setup path deliberately opens the backing file `O_RDWR`; the requested loop read-only state is represented in loop flags and in how `/dev/loopN` is opened. If later status or block-size setup fails after `LOOP_SET_FD`, the code tries to clear the loop device with `LOOP_CLR_FD` and logs a warning if cleanup also fails.

## Data and Error Model

`BDLoopInfo` is owned by the caller and has explicit copy/free helpers. The implementation maps ENXIO from `LOOP_GET_STATUS64` to `BD_LOOP_ERROR_DEVICE`; most ioctl/open failures become `BD_LOOP_ERROR_FAIL` or `BD_LOOP_ERROR_DEVICE`.

Progress is reported through `bd_utils_report_started()`, `bd_utils_report_progress()`, and `bd_utils_report_finished()` for create, teardown, autoclear, and capacity operations.

## Dependencies and Integration

This file depends on Linux-specific loop kernel ABI headers and ioctls:

- `<linux/loop.h>`
- `LOOP_CTL_GET_FREE`
- `LOOP_SET_FD`
- `LOOP_SET_STATUS64`
- `LOOP_GET_STATUS64`
- `LOOP_CLR_FD`
- `LOOP_SET_CAPACITY`
- `LOOP_SET_BLOCK_SIZE`

It also integrates with libblockdev utility logging/progress helpers from `<blockdev/utils.h>`.

## Research Notes

The file is a Linux block-device integration layer rather than filesystem logic. Its filesystem relevance is enabling regular files to become block devices for filesystems, partition scanning, testing, virtualization images, and image-backed storage workflows.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/loop.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/loop.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/loop.h

## Purpose

`loop.h` declares the public libblockdev loop plugin API and data structures.

## Public Types

- `BDLoopError` defines loop plugin error codes:
  - `BD_LOOP_ERROR_TECH_UNAVAIL`
  - `BD_LOOP_ERROR_FAIL`
  - `BD_LOOP_ERROR_DEVICE`
- `BDLoopTech` currently exposes one technology category, `BD_LOOP_TECH_LOOP`.
- `BDLoopTechMode` defines mode bits for create, destroy, modify, and query operations.
- `BDLoopInfo` describes a loop device:
  - backing file path
  - byte offset into backing file
  - autoclear flag
  - direct I/O flag
  - partition scan flag
  - read-only flag

## Public API

The header exposes:

- object lifetime helpers: `bd_loop_info_free()`, `bd_loop_info_copy()`
- plugin lifecycle: `bd_loop_init()`, `bd_loop_close()`
- availability probing: `bd_loop_is_tech_avail()`
- query helpers: `bd_loop_info()`, `bd_loop_get_loop_name()`
- creation helpers: `bd_loop_setup()`, `bd_loop_setup_from_fd()`
- destruction and modification helpers: `bd_loop_teardown()`, `bd_loop_set_autoclear()`, `bd_loop_set_capacity()`

## Integration Notes

The API is GLib-oriented: strings use `gchar`, booleans use `gboolean`, errors use `GError`, and returned objects/strings are caller-owned unless documented otherwise. It is intended to work both as a loaded libblockdev plugin and as a standalone library, with explicit init/close entry points.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/loop.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/Makefile.am

## Purpose

`Makefile.am` defines the Automake build rules for the libblockdev LVM plugin variants.

## Build Variants

The file conditionally builds two mutually related plugin libraries:

- `libbd_lvm.la` when `WITH_LVM` is enabled.
- `libbd_lvm-dbus.la` when `WITH_LVM_DBUS` is enabled.

Both variants install `lvm.h` under `$(includedir)/blockdev` when their corresponding build option is active.

## Shared Inputs

Both plugin variants share:

- `lvm.h`
- `lvm-private.h`
- `lvm-common.c`
- `vdo_stats.c`
- `vdo_stats.h`
- dependency checking helpers from `../check_deps.c`
- device-mapper logging helpers from `../dm_logging.c`

The non-D-Bus variant uses `lvm.c`; the D-Bus variant uses `lvm-dbus.c`.

## Compiler and Linker Settings

Both variants use GLib, GIO, devmapper, and YAML compiler/linker flags. The CLI-backed plugin additionally links JSON-GLib. Both libraries are built with:

- `-Wall -Wextra -Werror`
- `-version-info 3:0:0`
- `-Wl,--no-undefined`
- exported symbols matching `^bd_.*`
- include paths for generated headers, plugin-local headers, and shared plugin headers
- `PACKAGE_SYSCONF_DIR` defined from `$(sysconfdir)`

## Research Notes

This file is the switch point between two backend implementations for the same public LVM API: direct command/JSON handling in `lvm.c` and lvmdbusd/GDBus handling in `lvm-dbus.c`.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm-common.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm-common.c

## Purpose

`lvm-common.c` implements shared LVM plugin functionality used by both backend variants. It contains data copy/free helpers, LVM sizing calculations, global LVM configuration state, devices-file helpers, enum/string conversion helpers, VDO statistics glue, VG config backup/restore wrappers, and cache status parsing through device-mapper.

## Data Lifetime Helpers

The file provides deep copy and free functions for public LVM data structures:

- `BDLVMPVdata`
- `BDLVMVGdata`
- `BDLVMSEGdata`
- `BDLVMLVdata`
- `BDLVMVDOPooldata`
- `BDLVMCacheStats`

LV copy/free logic handles nested string vectors and segment arrays through private `copy_segs()` and `free_segs()` helpers.

## Size and Validity Calculations

The file defines reusable calculation APIs for LVM callers:

- supported PE sizes from 1 KiB to 16 GiB
- max LV size, differing for 64-bit and 32-bit builds
- rounding arbitrary byte sizes to PE boundaries
- LV physical size calculation
- thin-pool padding and metadata size estimates
- thin-pool metadata size validation
- thin-pool chunk size validation, including stricter power-of-two behavior when discard support is required
- default cache metadata size, at least 8 MiB or 0.1% of cache size

The shared constants include `SECTOR_SIZE`, `DEFAULT_PE_SIZE`, thin-pool metadata bounds, thin-pool chunk bounds, and cache metadata minimums.

## Global Config and Device Filtering

`global_config_lock`, `global_config_str`, and `global_devices_str` hold process-local libblockdev LVM configuration. These settings do not modify system `lvm.conf`; they are injected into later LVM calls as `--config` and `--devices`.

The APIs are:

- `bd_lvm_set_global_config()`
- `bd_lvm_get_global_config()`
- `bd_lvm_set_devices_filter()`
- `bd_lvm_get_devices_filter()`

The devices filter checks `BD_LVM_TECH_DEVICES` availability before storing a comma-separated device list.

## Enum and String Conversion

The file maps LVM cache and VDO enums to strings and back where needed:

- cache mode: `writethrough`, `writeback`, `unknown`
- VDO operating mode: `recovering`, `read-only`, `normal`, `unknown`
- VDO compression state: `online`, `offline`, `unknown`
- VDO index state: `error`, `closed`, `opening`, `closing`, `offline`, `online`, `unknown`
- VDO write policy: `auto`, `sync`, `async`, `unknown`

Invalid values populate `BD_LVM_ERROR`.

## VDO Statistics

`bd_lvm_vdo_get_stats_full()` builds the kernel dm-vdo map name as `<vg>-<pool>-vpool` and delegates to `vdo_get_stats_full()`.

`bd_lvm_vdo_get_stats()` converts selected hashtable entries into a fixed `BDLVMVDOStats` structure. Missing numeric values are represented with `-1`, and `writeAmplificationRatio` falls back to `-1` if unavailable.

## LVM Devices File Helpers

`_lvm_devices_enabled()` checks whether the LVM devices file is enabled by querying `lvmconfig`. It first checks full config, including libblockdev's global config, then falls back to default config.

`bd_lvm_devices_add()` and `bd_lvm_devices_delete()` wrap `lvmdevices --adddev` and `lvmdevices --deldev`, optionally passing `--devicesfile=<file>`. They fail with `BD_LVM_ERROR_DEVICES_DISABLED` if the devices file feature is not active.

## Config and Backup/Restore Helpers

`bd_lvm_config_get()` wraps `lvmconfig`, allowing section/setting selection, type selection, values-only output, optional global-config injection, and arbitrary extra arguments.

`_vgcfgbackup_restore()` is the shared implementation for:

- `bd_lvm_vgcfgbackup()`
- `bd_lvm_vgcfgrestore()`

Both call `lvm vgcfgbackup` or `lvm vgcfgrestore`, optionally with `-f <file>`, and include global config when set.

## Cache Stats

`bd_lvm_cache_stats()` queries a cached LV with libdevmapper:

1. Calls `bd_lvm_lvinfo()` to determine whether the cached object is a thin pool data LV or a normal cached LV.
2. Builds the device-mapper name with `dm_build_dm_name()`.
3. Runs a `DM_DEVICE_STATUS` task.
4. Parses cache target parameters with `dm_get_status_cache()`.
5. Converts sector-based block counts into bytes.
6. Detects writethrough/writeback mode from feature flags.

Failures are reported as `BD_LVM_ERROR_DM_ERROR`, `BD_LVM_ERROR_CACHE_NOCACHE`, or `BD_LVM_ERROR_CACHE_INVAL`.

## Research Notes

This file is backend-independent glue. It is storage-stack relevant because it encodes LVM sizing policy, device-filter behavior, cache and VDO metadata interpretation, and device-mapper status conversion used by higher-level block and filesystem provisioning workflows.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm-common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm-dbus.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm-dbus.c

## Purpose

`lvm-dbus.c` implements the libblockdev LVM plugin backend using `lvmdbusd` over the system D-Bus. It exposes the public `bd_lvm_*` API by translating operations into lvmdbusd object lookups, property reads, method calls, and asynchronous job polling.

## D-Bus Model

The file defines object prefixes and interfaces for:

- manager: `/com/redhat/lvmdbus1/Manager`
- PVs, VGs, LVs, hidden LVs, thin pools, cache pools, and VDO pools
- job objects under `/com/redhat/lvmdbus1/Job/`
- standard D-Bus properties and introspection interfaces

A static `GDBusConnection *bus` is initialized against the system bus. `bd_lvm_init()` sets up this connection and initializes libdevmapper logging; `bd_lvm_close()` flushes/closes the connection, resets dependency caches, and disables devmapper log redirection.

## Dependency and Feature Checks

The backend caches availability checks for:

- utilities: `lvm`, `lvmdevices`, `lvmconfig`
- D-Bus service: `com.redhat.lvmdbus1`
- lvmdbusd version needed for writecache
- LVM segtypes: `vdo`, `writecache`
- kernel module: `dm-vdo`

`bd_lvm_is_tech_avail()` maps each `BDLVMTech` to required dependencies. Pure calculation techs are always available for query mode; VDO requires lvmdbusd, LVM VDO feature support, and `dm-vdo`.

## Core Call Flow

The main helper is `call_lvm_method()`:

1. Verifies lvmdbusd availability.
2. Optionally locks `global_config_lock`.
3. Merges extra parameters, `BDExtraArg` entries, global `--config`, and global `--devices` into lvmdbusd's extra-argument dictionary.
4. Appends a one-second lvmdbusd timeout and the extra dictionary to the method parameter tuple.
5. Logs task status and starts progress reporting.
6. Calls the requested D-Bus method synchronously.

`call_lvm_method_sync()` handles the result. It accepts immediate object results, immediate no-result success, or job object paths. For jobs, it polls `Complete`, reports `Percent`, reads `Result`, fetches `GetError` on failure, and removes the job object afterward.

Convenience wrappers dispatch by object id, LV, thin pool, and VDO pool.

## Object Lookup and Property Parsing

The backend uses lvmdbusd manager `LookUpByLvmId` to map LVM IDs such as `vg/lv` or `/dev/sda` to object paths. It uses D-Bus `Get` and `GetAll` for property access, and `Introspect` to enumerate objects under PV/VG/LV/pool prefixes.

Property decoders build libblockdev structures:

- `get_pv_data_from_props()` fills PV fields, tags, missing state, and related VG details.
- `get_vg_data_from_props()` fills VG size, free space, extent counts, PV count, tags, and exportable state.
- `get_lv_data_from_props()` fills LV identity, size, attr, percents, segtype, roles, VG name, origin, pool, move PV, and tags.
- `get_vdo_data_from_props()` maps lvmdbusd VDO mode/state/policy strings and boolean-like feature strings into `BDLVMVDOPooldata`.

Extra LV helpers discover pool data LVs, metadata LVs, segment placement, hidden image/metadata LVs, and related VG names by chasing object-path properties.

## PV Operations

The file implements:

- `bd_lvm_pvcreate()`
- `bd_lvm_pvresize()`
- `bd_lvm_pvremove()`
- `bd_lvm_pvmove()`
- `bd_lvm_pvscan()`
- PV tag add/delete
- `bd_lvm_pvinfo()`
- `bd_lvm_pvs()`

Notable behavior: `bd_lvm_pvremove()` uses `-ff` and `--yes`; if lvmdbusd reports the PV object does not exist, removal is treated as a successful no-op for a non-PV device.

## VG Operations

The file implements:

- `bd_lvm_vgcreate()`
- `bd_lvm_vgremove()`
- `bd_lvm_vgrename()`
- `bd_lvm_vgactivate()` / `bd_lvm_vgdeactivate()`
- `bd_lvm_vgextend()` / `bd_lvm_vgreduce()`
- VG tag add/delete
- lockspace start/stop via `--lockstart` and `--lockstop`
- `bd_lvm_vginfo()`
- `bd_lvm_vgs()`

VG creation converts PV names to object paths and injects `--physicalextentsize` using the resolved PE size. Reducing missing PVs passes a force extra parameter.

## LV Operations

The basic LV API includes:

- origin query
- create/remove/rename/resize/repair
- activate/deactivate
- classic snapshot create/merge
- tag add/delete
- LV info and LV tree info
- LV listing with optional VG filtering

LV creation supports optional type and PV placement. For striped LVs with an explicit PV list, the code passes `stripes=<pv_count>` instead of a generic type option. LV resize adds `--fs ignore` when the installed LVM version is at least `2.03.19`, avoiding filesystem-related resize checks.

LV listing merges objects from normal LV, thin-pool, cache-pool, VDO-pool, and hidden-LV namespaces. `bd_lvm_lvs_tree()` additionally populates segment and hidden data/metadata LV arrays.

## Thin Provisioning

Thin-related operations include:

- `bd_lvm_thpoolcreate()`
- `bd_lvm_thlvcreate()`
- `bd_lvm_thlvpoolname()`
- `bd_lvm_thsnapshotcreate()`
- `bd_lvm_thpool_convert()`

Thin pool creation uses lvmdbusd `LvCreateLinear` with thin-pool-specific extra options such as `poolmetadatasize`, `chunksize`, and `profile`. Converting an existing data and metadata LV into a thin pool calls `CreateThinPool`, then optionally renames the resulting pool.

## Cache and Writecache

Cache support includes:

- cache pool creation from data and metadata LVs
- attaching and detaching cache pools
- combined cached-LV creation
- cache pool name discovery
- converting existing LVs into a cache pool

`bd_lvm_cache_create_pool()` is a multi-step workflow: create the cache data LV, create the metadata LV, then call `CreateCachePool`. It reports progress at each stage.

Writecache support includes:

- `bd_lvm_writecache_attach()`
- `bd_lvm_writecache_detach()`
- `bd_lvm_writecache_create_cached_lv()`

Writecache attach explicitly deactivates both the data LV and cache LV before calling `WriteCacheLv`.

## VDO

VDO support includes:

- `bd_lvm_vdo_pool_create()`
- compression enable/disable
- deduplication enable/disable
- `bd_lvm_vdo_info()`
- virtual LV resize
- physical pool resize
- conversion of an existing LV into a VDO pool
- VDO LV pool-name query

VDO creation and conversion pass compression/deduplication as extra parameters. Index memory and write policy are injected by temporarily extending `global_config_str` under `global_config_lock`, because these settings are only available through LVM config. Physical VDO pool resize refuses reductions with `BD_LVM_ERROR_NOT_SUPPORTED`.

## Compatibility and Edge Cases

The code contains several explicit compatibility choices:

- Calculation techs are available without lvmdbusd.
- LV segtype arrays are simplified by using the first segment type; `"error"` is normalized to `"linear"`.
- PV tags must be modified through the owning VG interface, so unassigned PVs cannot be tagged.
- Cache pool names are parsed from bracketed hidden LV names.
- VDO default pool/LV names are synthesized when callers pass `NULL`.
- Several operations use extra options to avoid interactive prompts or filesystem handling.

## Research Notes

This file is a high-level block storage orchestration backend. It does not implement filesystems directly, but it provisions and modifies the LVM devices on which filesystems are created, resized, snapshotted, cached, thin-provisioned, or exposed to virtualization stacks.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm-dbus.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm-private.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm-private.h

## Purpose

`lvm-private.h` defines private constants and shared globals for libblockdev's LVM plugin implementations.

## Constants

- `SECTOR_SIZE` is fixed at 512 bytes.
- `DEFAULT_PE_SIZE` is 4 MiB.
- `USE_DEFAULT_PE_SIZE` is 0.
- `RESOLVE_PE_SIZE(size)` maps `0` to `DEFAULT_PE_SIZE`; otherwise it preserves the caller-supplied size.
- `LVM_MIN_VERSION` is `2.03.17`.
- `LVM_VERSION_FSRESIZE` is `2.03.19`.

## Shared Globals

The header declares:

- `global_config_lock`
- `global_config_str`
- `global_devices_str`

These are defined in `lvm-common.c` and used by both backend implementations to inject process-local LVM configuration and device filters into command or D-Bus operations.

## Research Notes

This is a small private coordination header. Its main impact is ensuring consistent byte-sector assumptions, default PE sizing, minimum LVM version checks, and shared config/device-filter handling across LVM backends.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm-private.h -->