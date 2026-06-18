# Group Research: group_675_libblockdev_sources_virtualization_libblockdev_src_plugins_lvm_lvm_c_23f9330e67e1

Scope checked: `Docs/research_subset_a.md` includes `sources/virtualization/libblockdev`. All files listed for this group were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm.c

## Role
Implements the public LVM plugin entry points for libblockdev. The file is a command-wrapper and parser layer around `lvm`, with additional direct `libdevmapper` use for logging and VDO stats support delegated to `vdo_stats.c`.

## Main Dependencies
- GLib for allocation, strings, mutexes, atomics, error domains, and pointer arrays.
- `blockdev/utils.h` for command execution, progress reporting, device helpers, and utility version checks.
- `libdevmapper` for DM logging setup.
- JSON-GLib for parsing `lvm --reportformat json_std`.
- Local `check_deps.h`, `dm_logging.h`, `lvm-private.h`, and `vdo_stats.h`.

## Dependency and Feature Gates
- `bd_lvm_init()` registers redirected device-mapper logging and sets verbosity based on `DEBUG`.
- `bd_lvm_close()` unregisters logging and clears cached dependency, feature, and module-dependency availability bits.
- `bd_lvm_is_tech_avail()` gates most operations on `lvm`, VDO on LVM VDO segtype plus `dm-vdo`, writecache on LVM writecache segtype, devices-file operations on `lvmdevices`, and config queries on `lvmconfig >= 2.03.17`.

## Command Execution Model
- Internal wrappers prepend `lvm` to argument vectors and optionally append global `--config=<...>` and `--devices=<...>` settings.
- `global_config_lock` protects global LVM config/devices state during command construction and execution.
- `call_lvm_and_parse_json_report()` centralizes JSON report parsing and returns a `JsonArray` owned by a caller-retained `JsonParser`.

## JSON Data Mapping
- `_lvm_json_get_string()` normalizes LVM empty string values to `NULL`.
- PV, VG, LV, and VDO JSON objects are mapped into the public structs declared in `lvm.h`.
- LV parsing hides several LVM internals: `segtype=error` is exposed as `linear`, bracketed internal LV names are stripped, `lv_role` arrays are joined, and tree output can represent physical segments, data sub-LVs, and metadata sub-LVs.
- `merge_lv_data()` merges repeated `lvs` rows from multi-segment LVs into one `BDLVMLVdata`.

## PV, VG, and LV Operations
- PV operations include create, resize, remove, move, scan, tags, single-PV info, and all-PV listing.
- VG operations include create, remove, rename, activate/deactivate, extend/reduce, tags, lock start/stop, single-VG info, and all-VG listing.
- LV operations include origin query, create, remove, rename, resize, repair, activate/deactivate, snapshot create/merge, tags, single/all LV info, and tree variants.
- Byte sizes are generally converted to KiB strings before calling LVM.
- `bd_lvm_lvresize()` adds `--fs ignore` on newer LVM to avoid filesystem checks.

## Thin, Cache, Writecache, and VDO
- Thin support creates thin pools/LVs/snapshots, queries pool names, and converts data/metadata LVs into pools.
- Cache support creates cache pool data/metadata LVs, converts them with `lvconvert --type cache-pool`, attaches/detaches cache pools, creates complete cached LVs, and extracts cache pool names from bracketed LVM output.
- Writecache creates a fast cache LV plus data LV and attaches it via `lvconvert --type writecache`, deactivating both LVs first.
- VDO creates/converts pools, toggles compression/deduplication, reports info, resizes logical VDO LVs, rejects physical pool shrink, and injects index memory/write policy through temporary LVM config.

## Filesystem/Storage Relevance
This file orchestrates logical block devices that filesystems are later placed on, including thin provisioning, snapshots, cache tiers, writecache, VDO dedupe/compression, shared VG lockspaces, and device filtering.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm.h

## Role
Public header for the LVM plugin ABI. It declares the LVM error domain, technology/mode enums, data structs returned to callers, ownership helpers, and all public plugin entry points.

## Public Data Model
Defines structs for PVs, VGs, LV segments, LVs, VDO pool info, VDO stats, and cache stats. These carry identity, UUIDs, sizes, tags, role/pool relationships, segment mappings, cache counters, and VDO state.

## API Surface
Declares plugin lifecycle and availability, PE/thin/cache calculations, PV/VG/LV CRUD and query functions, tags, shared VG lockspace calls, VG config backup/restore, thin/cache/writecache/VDO operations, global config and devices filters, devices-file add/delete, VDO stats, and `lvmconfig` queries.

## Implementation Note
Not every declaration in this header is implemented in `lvm.c`; several helpers are provided by other LVM plugin source files not in this group. This header is the aggregate public ABI for the whole LVM plugin.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/lvm.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.c

## Role
Implements VDO stats retrieval and normalization. It sends a device-mapper target `stats` message, parses the YAML response, and returns a GLib hash table of string key/value statistics.

## Main Flow
`vdo_get_stats_full()` creates a `DM_DEVICE_TARGET_MSG` task, sets the device name and `stats` message, runs it, parses the YAML response with libyaml, flattens flow mappings into camelCase-like keys, and adds computed compatibility stats.

## Helpers and Computed Stats
- `get_stat_val64()`, `get_stat_val64_default()`, and `get_stat_val_double()` parse typed values from the hash table.
- Derived stats include write amplification, one-K block totals/used/available, used percent, savings/saving percent, journal batching/writing counters, and 512-byte emulation state.

## Error Handling
Device-mapper task creation, setup, execution, response retrieval, and YAML parser initialization failures become `BD_LVM_ERROR_DM_ERROR`. YAML scan failures are not explicitly checked inside the token loop.

## Filesystem/Storage Relevance
The file exposes telemetry for deduplicated/compressed VDO block volumes that may host filesystems, especially capacity reporting, savings reporting, and write-amplification monitoring.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.h

## Role
Internal header for the LVM VDO stats helper.

## Exposed Functions
Declares integer/double stat parsers and `vdo_get_stats_full()`. It includes only GLib and uses the `BD_VDO_STATS` include guard.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/lvm/vdo_stats.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mdraid.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/mdraid.c

## Role
Implements the libblockdev MD RAID plugin. It wraps `mdadm`, parses `mdadm` output into stable structs, performs MD UUID conversions, resolves MD names/nodes, and uses sysfs for state, bitmap, and sync-action controls.

## Main Dependencies
Uses GLib, blockdev utilities, `bs_size.h`, `glob`, `time`, POSIX access helpers, and dependency checking for `mdadm >= 3.3.2`.

## Parsing Model
- `parse_mdadm_vars()` parses colon-separated human output and equals-separated brief/export output.
- Examine parsing extracts RAID level, device count, name, array size, UUIDs, update time, events, metadata, and chunk size.
- Detail parsing extracts metadata, creation time, level, name, size values, device counts, clean state, UUID, and container.

## Operations
- Creates arrays with `mdadm --create`, optional spares, metadata version, bitmap, chunk size, and disk list.
- Destroys metadata with `--zero-superblock`.
- Stops, assembles, runs, nominates/denominates, adds, grows, fails, and removes members.
- `bd_md_activate()` treats already-active arrays as success.
- `bd_md_examine()` combines normal, export, and brief examine output for stable metadata.
- `bd_md_detail()` combines normal and export detail output.

## Sysfs and UUID Helpers
- Resolves MD names/nodes through `/dev/md/*`, `/dev/<node>`, and `/sys/class/block/<md>/md`.
- Reads `array_state`, reads/writes bitmap location, and writes validated sync actions.
- Converts mdadm UUID form to canonical dashed UUID form and back, with regex validation.

## Filesystem/Storage Relevance
This file manages Linux software RAID arrays that commonly back filesystems or higher block layers such as LVM.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mdraid.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mdraid.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/mdraid.h

## Role
Public header for the MD RAID plugin.

## Public Surface
Defines default MD superblock/chunk sizes, the MD error domain, examine/detail structs, tech/mode enums, lifecycle functions, availability checks, create/destroy/activate/deactivate/run, member add/remove, examine/detail, UUID conversion, node/name lookup, status, bitmap get/set, and sync-action request.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mdraid.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mpath.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/mpath.c

## Role
Implements the libblockdev multipath plugin. It combines `multipath` and `mpathconf` wrappers with direct libdevmapper queries to identify multipath maps and member devices.

## Main Dependencies
Uses GLib, blockdev utilities, `libdevmapper`, `/dev/block/<major>:<minor>` symlinks, `multipath >= 0.4.9`, and `mpathconf`.

## Operations
- `bd_mpath_flush_mpaths()` runs `multipath -F`, then verifies `multipath -ll` is empty.
- `bd_mpath_is_mpath_member()` lists all DM maps, filters maps whose first target is `multipath`, enumerates map dependencies, and compares dependency names to the input.
- `bd_mpath_get_mpath_members()` returns all dependency device names for multipath maps.
- `bd_mpath_set_friendly_names()` runs `mpathconf` with `--user_friendly_names y/n`.

## Error Notes
DM task failures map to `BD_MPATH_ERROR_DM_ERROR`; invalid `/dev/block` link formats map to `BD_MPATH_ERROR_INVAL`; remaining maps after flush map to `BD_MPATH_ERROR_FLUSH`.

## Filesystem/Storage Relevance
Multipath devices are stable block abstractions over multiple physical paths and may sit below filesystems, LVM, or MD RAID.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mpath.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mpath.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/mpath.h

## Role
Public header for the multipath plugin.

## API Surface
Declares the error domain, error codes, technology/mode enums, lifecycle, availability, map flushing, member detection, member listing, and friendly-name configuration. The API detects and configures maps but does not create them directly.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/mpath.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvdimm.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvdimm.c

## Role
Implements the deprecated NVDIMM plugin. It uses libndctl for most namespace discovery and state operations, and the `ndctl` CLI for namespace reconfiguration.

## Main Dependencies
Uses GLib, blockdev utilities, `ndctl/libndctl.h`, `uuid.h`, and the runtime `ndctl` tool for reconfigure mode.

## Operations
- Converts namespace mode strings/enums for raw, sector, memory, dax, fsdax, devdax, and unknown.
- Maps active block devices to namespace device names by walking all buses, regions, and namespaces.
- Enables/disables namespaces through libndctl.
- Reports single namespace info and lists namespaces with optional bus/region filters and optional idle namespace inclusion.
- Reconfigures namespaces via `ndctl create-namespace -e <namespace> -m <mode>` with optional force.
- Returns static supported sector-size arrays by namespace mode.

## Info Extraction
Detects backing BTT, PFN, and DAX objects; takes size/UUID/blockdev from the relevant wrapper when present; reports no blockdev and sector size 0 for DAX; defaults non-DAX sector size to 512 if libndctl reports 0.

## Filesystem/Storage Relevance
NVDIMM namespaces can expose persistent memory as raw block devices, sector-mode BTT devices, fsdax devices, or devdax memory.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvdimm.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvdimm.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvdimm.h

## Role
Public header for the deprecated NVDIMM plugin.

## Public Surface
Defines namespace errors, namespace mode enum values, `BDNVDIMMNamespaceInfo`, lifecycle/availability functions, mode conversion, block-device-to-namespace lookup, namespace enable/disable, info/listing, reconfiguration, and supported sector-size lookup.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvdimm.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/Makefile.am

## Role
Automake build definition for the NVMe plugin shared library.

## Build Details
Builds `libbd_nvme.la`, installs `nvme.h`, compiles with GLib/GIO/NVMe flags plus `-Wall -Wextra -Werror`, links blockdev utils plus GLib/GIO/NVMe libraries, exports `^bd_.*` symbols, and includes core, private, info, error, operation, fabrics, and dependency-checking sources.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-error.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-error.c

## Role
Implements the NVMe plugin error domain and internal conversion helpers from libnvme status/errno values to libblockdev `GError`s.

## Error Conversion
- `bd_nvme_error_quark()` returns the plugin's static GLib error quark.
- `_nvme_status_to_error()` clears success, maps negative status through `errno`, and maps positive NVMe status-code types to generic, command-specific, media, path, or vendor-specific libblockdev errors.
- `_nvme_fabrics_errno_to_gerror()` maps libnvme fabrics connection errors into invalid-argument, connect, already-connected, invalid, address-in-use, no-device, operation-not-supported, or refused codes, otherwise falling back to `errno`.

## Notes
The file centralizes NVMe error policy so other NVMe plugin files can report consistent GLib errors for both admin/status-code paths and NVMe-oF connection paths.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-error.c -->