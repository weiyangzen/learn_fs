# Group Research: group_676_libblockdev_sources_virtualization_libblockdev_src_plugins_nvme_nvme_bd49f4a024ca

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/virtualization/libblockdev`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-fabrics.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-fabrics.c

## Purpose

Implements the NVMe over Fabrics initiator-facing API for the libblockdev NVMe plugin. It wraps libnvme discovery/config/topology calls for connecting, disconnecting, matching sysfs controllers/namespaces, and managing global host NQN/host ID files.

## Main Responsibilities

- Parse `BDExtraArg` connection options into `struct nvme_fabrics_config`.
- Establish Fabrics controllers through libnvme host/controller objects.
- Disconnect controllers by subsystem NQN or controller device name.
- Find controllers associated with a namespace sysfs path.
- Find namespaces associated with a controller sysfs path.
- Read, generate, and write host NQN and host ID values.

## Important Functions

- `parse_extra_args()` accepts string options such as `config`, DH-HMAC-CHAP keys, queue counts, timeouts, TCP digest flags, TLS flags, host symbolic name, and libnvme 1.4 keyring/TLS key settings.
- `bd_nvme_connect()` validates required parameters, derives missing host NQN/host ID, reads the optional config file, creates a libnvme controller, and calls `nvmf_add_ctrl()`.
- `_disconnect()` scans live topology and disconnects matching controllers.
- `bd_nvme_disconnect()` removes all controllers matching a subsystem NQN.
- `bd_nvme_disconnect_by_path()` strips `/dev/` and removes a matching controller name.
- `bd_nvme_find_ctrls_for_ns()` scans libnvme topology and returns real sysfs controller paths connected to or sharing the requested namespace.
- `bd_nvme_find_namespaces_for_ctrl()` returns namespace sysfs paths under a matching controller plus subsystem-level namespaces.
- `bd_nvme_get_host_nqn()`, `bd_nvme_generate_host_nqn()`, `bd_nvme_get_host_id()`, `bd_nvme_set_host_nqn()`, and `bd_nvme_set_host_id()` manage host identity values.

## Dependencies and Interactions

- Uses libnvme topology APIs: `nvme_scan()`, `nvme_lookup_host()`, `nvme_create_ctrl()`, `nvmf_add_ctrl()`, `nvme_scan_topology()`, `nvme_disconnect_ctrl()`.
- Uses libnvme host identity helpers: `nvmf_hostnqn_from_file()`, `nvmf_hostid_from_file()`, `nvmf_hostnqn_generate()`.
- Uses shared NVMe error helpers from `nvme-private.h`.
- Writes host files under `PACKAGE_SYSCONF_DIR/nvme`, while comments note libnvme may use a different compiled `SYSCONFDIR`.

## Notable Details

- Default config file is `/etc/nvme/config.json`; `extra` option `config=none` disables config-file loading.
- If `transport_svcid` is omitted, TCP discovery uses the discovery port and TCP non-discovery currently falls through to the RDMA default port constant.
- Host ID can be derived from `uuid:` embedded in the host NQN when `/etc/nvme/hostid` is missing.
- Sysfs matching uses `realpath()` before comparing paths.
- The sysfs lookup functions ignore their `error` parameter and return an allocated, NULL-terminated array even if no match is found.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-fabrics.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-info.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-info.c

## Purpose

Implements NVMe information retrieval and GLib object lifecycle helpers for controller, namespace, SMART, error log, self-test log, and sanitize log data.

## Main Responsibilities

- Provide free/copy helpers for all public NVMe data structs.
- Open NVMe devices and allocate page-aligned ioctl buffers.
- Translate libnvme Identify Controller data to `BDNVMEControllerInfo`.
- Translate Identify Namespace and namespace descriptor data to `BDNVMENamespaceInfo`.
- Translate SMART / Health, Error Information, Device Self-test, and Sanitize log pages.
- Convert NVMe status fields into embedded `GError` values where public structs expose command-specific errors.

## Important Functions

- `bd_nvme_controller_info_free()` / `bd_nvme_controller_info_copy()` manage strings in controller info.
- `bd_nvme_namespace_info_free()` / `bd_nvme_namespace_info_copy()` deep-copy namespace IDs and LBA format arrays.
- `bd_nvme_error_log_entry_copy()` and `bd_nvme_self_test_log_entry_copy()` deep-copy embedded `GError`.
- `bd_nvme_self_test_result_to_string()` maps self-test result enum values to stable identifier strings.
- `_open_dev()` opens a device read-only and maps open failures through `_nvme_status_to_error()`.
- `_nvme_alloc()` allocates zeroed, page-aligned memory rounded to 4 KiB.
- `bd_nvme_get_controller_info()` issues Identify Controller and translates features, capacities, names, firmware, NVMe revision, self-test and sanitize capabilities.
- `bd_nvme_get_namespace_info()` issues Identify Namespace, optional descriptor list for NVMe 1.3+, optional independent namespace info for NVMe 2.0+, and builds LBA format metadata.
- `bd_nvme_get_smart_log()` reads SMART data and controller temperature thresholds.
- `bd_nvme_get_error_log_entries()` sizes the error log from `elpe`, reads all entries, and returns only entries with nonzero `error_count`.
- `bd_nvme_get_self_test_log()` reads current self-test progress and recent self-test results.
- `bd_nvme_get_sanitize_log()` reads sanitize state, progress, pass count, and time estimates.

## Dependencies and Interactions

- Uses libnvme ioctl helpers such as `nvme_identify_ctrl()`, `nvme_get_nsid()`, `nvme_identify_ns()`, `nvme_identify_ns_descs()`, `nvme_get_log_smart()`, `nvme_get_log_error()`, `nvme_get_log_device_self_test()`, and `nvme_get_log_sanitize()`.
- Uses shared `_nvme_status_to_error()` from `nvme-error.c`.
- Public struct definitions and enum mappings come from `nvme.h`.

## Notable Details

- 128-bit NVMe counters are reduced to `guint64`; the helper explicitly notes possible overflow.
- Controller model, serial, firmware, and subsystem NQN fields are stripped of trailing padding.
- Namespace descriptor parsing prefers descriptor-list EUI64/NGUID/UUID values and falls back to legacy Identify Namespace fields.
- SMART data units are converted to bytes using NVMe’s `1000 * 512` unit definition.
- Sanitize time estimate fields use `-1` when the device reports `0xffffffff`.
- LBA format relative performance is stored as `rp + 1` to match the public enum’s nonzero values.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-info.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-op.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-op.c

## Purpose

Implements active NVMe management operations: device self-test, low-level format, and sanitize.

## Main Responsibilities

- Map libblockdev self-test actions to NVMe Device Self-test command codes.
- Select a supported LBA format by requested data and metadata size.
- Run Format NVM with guardrails for namespace-versus-controller scope.
- Refresh kernel block state after format.
- Submit Sanitize commands with selected action and overwrite options.

## Important Functions

- `bd_nvme_device_self_test()` opens a controller or namespace device, resolves NSID when possible, and issues `nvme_dev_self_test()`.
- `find_lbaf_for_size()` identifies the current or requested LBA format index from Identify Namespace data.
- `bd_nvme_format()` validates formatting scope, maps secure erase options, calls `nvme_format_nvm()`, and updates kernel namespace/block state.
- `bd_nvme_sanitize()` maps sanitize action values and calls `nvme_sanitize_nvm()`.

## Dependencies and Interactions

- Uses `_open_dev()` and `_nvme_alloc()` from `nvme-info.c`.
- Uses `_nvme_status_to_error()` from `nvme-error.c`.
- Uses Linux ioctls `NVME_IOCTL_RESCAN`, `BLKBSZSET`, and `BLKRRPART` after format.
- Uses libnvme command argument structs: `nvme_dev_self_test_args`, `nvme_format_nvm_args`, and `nvme_sanitize_nvm_args`.

## Notable Details

- Controller character devices are detected when `nvme_get_nsid()` fails with `ENOTTY`; then NSID is set to all namespaces.
- Formatting a namespace is rejected with `BD_NVME_ERROR_WOULD_FORMAT_ALL_NS` when controller FNA says namespace format would affect all namespaces.
- When called on a controller device, `find_lbaf_for_size()` uses namespace ID 1 as the reference namespace.
- After namespace format with a changed LBA size, the code updates the block size and rereads the partition table.
- Sanitize returns immediately after command submission; progress is obtained through `bd_nvme_get_sanitize_log()`.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-op.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-private.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme-private.h

## Purpose

Private header shared by the NVMe plugin implementation files.

## Contents

- Defines `ZERO_INIT` with a clang-specific empty initializer fallback.
- Defines `_C_LOCALE` as the C locale handle used for locale-stable error text.
- Declares internal error helpers:
  - `_nvme_status_to_error()`
  - `_nvme_fabrics_errno_to_gerror()`
- Declares internal info helpers:
  - `_open_dev()`
  - `_nvme_alloc()`

## Dependencies and Interactions

- Included by `nvme.c`, `nvme-info.c`, `nvme-op.c`, and `nvme-fabrics.c`.
- Keeps cross-file helpers internal with `G_GNUC_INTERNAL`.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme-private.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme.c

## Purpose

Provides the NVMe plugin lifecycle functions and technology availability dispatch.

## Main Responsibilities

- Initialize the NVMe plugin.
- Close the NVMe plugin.
- Report supported NVMe technology categories.

## Important Functions

- `bd_nvme_init()` currently has no initialization work and returns `TRUE`.
- `bd_nvme_close()` currently has no cleanup work.
- `bd_nvme_is_tech_avail()` reports `BD_NVME_TECH_NVME` and `BD_NVME_TECH_FABRICS` as available, and rejects unknown technologies with `BD_NVME_ERROR_TECH_UNAVAIL`.

## Dependencies and Interactions

- Includes libnvme and plugin headers, but this file does not perform libnvme runtime probing.
- Public availability is broad; detailed failures are reported by operation-specific functions.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/nvme/nvme.h

## Purpose

Public API header for the libblockdev NVMe plugin.

## Main API Surface

- Error domain:
  - `bd_nvme_error_quark()`
  - `BDNVMEError`
- Technology categories:
  - `BD_NVME_TECH_NVME`
  - `BD_NVME_TECH_FABRICS`
  - info, manage, and initiator modes.
- Controller reporting:
  - `BDNVMEControllerFeature`
  - `BDNVMEControllerType`
  - `BDNVMEControllerInfo`
- Namespace reporting:
  - `BDNVMELBAFormat`
  - `BDNVMENamespaceFeature`
  - `BDNVMENamespaceInfo`
- Health/log reporting:
  - `BDNVMESmartLog`
  - `BDNVMEErrorLogEntry`
  - `BDNVMESelfTestLog`
  - `BDNVMESanitizeLog`
- Operations:
  - self-test, format, sanitize.
- Fabrics:
  - host NQN/ID management,
  - connect/disconnect,
  - namespace/controller sysfs lookup helpers.

## Important Functions Declared

- Lifecycle and availability:
  - `bd_nvme_init()`
  - `bd_nvme_close()`
  - `bd_nvme_is_tech_avail()`
- Info queries:
  - `bd_nvme_get_controller_info()`
  - `bd_nvme_get_namespace_info()`
  - `bd_nvme_get_smart_log()`
  - `bd_nvme_get_error_log_entries()`
  - `bd_nvme_get_self_test_log()`
  - `bd_nvme_get_sanitize_log()`
- Management:
  - `bd_nvme_device_self_test()`
  - `bd_nvme_format()`
  - `bd_nvme_sanitize()`
- Fabrics:
  - `bd_nvme_get_host_nqn()`
  - `bd_nvme_generate_host_nqn()`
  - `bd_nvme_get_host_id()`
  - `bd_nvme_set_host_nqn()`
  - `bd_nvme_set_host_id()`
  - `bd_nvme_connect()`
  - `bd_nvme_disconnect()`
  - `bd_nvme_disconnect_by_path()`
  - `bd_nvme_find_ctrls_for_ns()`
  - `bd_nvme_find_namespaces_for_ctrl()`

## Dependencies and Interactions

- Uses GLib/GObject types and `BDExtraArg` from blockdev utils.
- Structs are paired with copy/free helpers for introspection bindings and callers that need ownership-safe data handling.

## Notable Details

- The header documents destructive behavior for format and sanitize operations.
- `BD_NVME_SANITIZE_STATUS_IN_PROGESS` is retained as a deprecated misspelled alias for `BD_NVME_SANITIZE_STATUS_IN_PROGRESS`.
- Error values include both generic NVMe status categories and NVMe Fabrics connection failures.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/nvme/nvme.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/part.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/part.c

## Purpose

Implements the partition-table plugin using libfdisk. It supports MBR and GPT table creation, queries, partition creation/deletion/resizing, and selected partition metadata updates.

## Main Responsibilities

- Manage `BDPartSpec` and `BDPartDiskSpec` copy/free lifecycle.
- Open libfdisk contexts and write/reread labels.
- Create MBR or GPT partition tables.
- Query disk, partition, free-space, and best-fit free-region metadata.
- Create normal, extended, and logical partitions with alignment handling.
- Delete and resize partitions.
- Set GPT names, type GUIDs, UUIDs, and attributes.
- Set MBR partition IDs and bootable flags.
- Convert table/type enums to string identifiers.

## Important Helpers

- `get_part_num()` extracts the numeric suffix from a partition path, including paths ending in digit-separated `pN` style.
- `fdisk_ask_callback()` routes libfdisk info/warning prompts to libblockdev logging.
- `get_device_context()` creates, assigns, configures, and returns a libfdisk context.
- `close_context()` deassigns and unreferences a context.
- `write_label()` writes the in-memory disklabel, optionally locks the device with `flock()`, and asks the kernel to reread either changed partitions or the whole table.
- `get_part_type_guid_and_gpt_flags()` reads GPT type GUID, type name, and attributes for a partition.
- `get_part_spec_fdisk()` converts a libfdisk partition into `BDPartSpec`.
- `get_disk_parts()` returns partitions and/or free regions, adding synthetic metadata regions where libfdisk does not expose parted-style metadata areas.
- `get_max_part_size()` computes maximum resize size using partition/free-space ordering.

## Important Public Functions

- `bd_part_init()` initializes the C locale and records libfdisk version.
- `bd_part_is_tech_avail()` reports MBR and GPT as supported.
- `bd_part_create_table()` creates a new `dos` or `gpt` disklabel.
- `bd_part_get_part_spec()`, `bd_part_get_part_by_pos()`, `bd_part_get_disk_spec()`, `bd_part_get_disk_parts()`, and `bd_part_get_disk_free_regions()` provide query APIs.
- `bd_part_get_best_free_region()` selects the best region for normal, logical, or extended partition creation.
- `bd_part_create_part()` creates a partition, auto-selecting type for `BD_PART_TYPE_REQ_NEXT`.
- `bd_part_delete_part()` removes a partition.
- `bd_part_resize_part()` changes a partition size, with alignment and max-size handling.
- `bd_part_set_part_name()`, `bd_part_set_part_type()`, `bd_part_set_part_id()`, `bd_part_set_part_uuid()`, `bd_part_set_part_bootable()`, and `bd_part_set_part_attributes()` update partition metadata.
- `bd_part_get_part_table_type_str()` and `bd_part_get_type_str()` return stable string names.

## Dependencies and Interactions

- Uses libfdisk for table parsing, manipulation, alignment, partition typing, and kernel reread operations.
- Uses libblockdev utility progress/log APIs around mutating operations.
- Uses a dedicated C locale for stable `strerror_l()` text.
- Uses Linux/macros from the build environment, including `MiB` constants in size calculations.

## Notable Details

- GPT supports only normal partitions in `bd_part_create_part()`.
- MBR auto-selection creates logical partitions inside existing extended partitions; with three primary partitions it can create a new extended partition first, then create a logical partition inside it.
- For libfdisk versions before 2.36.1, creating a new extended partition forces a full partition-table reread.
- Resize-to-maximum has libfdisk-version-specific handling for default end alignment.
- Requested growth slightly beyond max size is clamped when the excess is within 4 MiB; larger excess is rejected.
- `bd_part_get_type_str()` expects enum-style single-bit values or zero; mixed flag values can map by integer log2 rather than by full flag composition.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/part.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/part.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/part.h

## Purpose

Public API header for the libblockdev partition plugin.

## Main API Surface

- Error domain:
  - `bd_part_error_quark()`
  - `BDPartError`
- Partition table types:
  - MBR/DOS,
  - GPT,
  - undefined.
- Partition type flags:
  - normal,
  - logical,
  - extended,
  - freespace,
  - metadata,
  - protected.
- Requested creation types:
  - normal,
  - logical,
  - extended,
  - next/auto.
- Alignment modes:
  - none,
  - minimal,
  - optimal.
- Data structs:
  - `BDPartSpec`
  - `BDPartDiskSpec`
- Technology categories and modes for MBR/GPT create, modify, and query operations.

## Important Functions Declared

- Lifecycle and availability:
  - `bd_part_init()`
  - `bd_part_close()`
  - `bd_part_is_tech_avail()`
- Table and query operations:
  - `bd_part_create_table()`
  - `bd_part_get_part_spec()`
  - `bd_part_get_part_by_pos()`
  - `bd_part_get_disk_spec()`
  - `bd_part_get_disk_parts()`
  - `bd_part_get_disk_free_regions()`
  - `bd_part_get_best_free_region()`
- Mutation operations:
  - `bd_part_create_part()`
  - `bd_part_delete_part()`
  - `bd_part_resize_part()`
  - metadata setters for name, type, ID, bootable flag, GPT attributes, and UUID.
- String conversion:
  - `bd_part_get_part_table_type_str()`
  - `bd_part_get_type_str()`

## Dependencies and Interactions

- Depends only on GLib at the public header level.
- Implemented by `part.c` using libfdisk.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/part.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/s390.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/s390.c

## Purpose

Implements the s390 storage plugin for DASD and zFCP device operations.

## Main Responsibilities

- Check availability of DASD and zFCP technologies.
- Format DASD devices using `dasdfmt`.
- Query DASD format and media type through sysfs/ioctl.
- Bring DASD devices online.
- Normalize DASD/zFCP device, WWPN, and LUN input strings.
- Bring zFCP devices/LUNs online.
- Remove zFCP SCSI devices and bring zFCP LUNs/devices offline.

## Important Functions

- `bd_s390_is_tech_avail()` requires `dasdfmt` only for DASD modify mode; zFCP needs no external dependency according to this implementation.
- `bd_s390_dasd_format()` runs `dasdfmt -y -d cdl -b 4096 /dev/<dasd>` plus extra args.
- `bd_s390_dasd_needs_format()` reads `/sys/bus/ccw/drivers/dasd-eckd/<dasd>/status` and detects `unformatted`.
- `bd_s390_dasd_online()` writes `1` to the DASD `online` sysfs attribute, first attempting `dasd_cio_free -d` if the device is ignored.
- `bd_s390_dasd_is_ldl()` and `bd_s390_dasd_is_fba()` use `BLKSSZGET` and `BIODASDINFO2`.
- `bd_s390_sanitize_dev_input()` normalizes device numbers to `0.0.xxxx`.
- `bd_s390_zfcp_sanitize_wwpn_input()` lowercases and ensures `0x` prefix.
- `bd_s390_zfcp_sanitize_lun_input()` lowercases, ensures `0x`, left-pads short LUNs to four hex digits, and right-pads to 16 hex digits.
- `bd_s390_zfcp_online()` ensures the zFCP device is online, verifies WWPN sysfs directory, writes the LUN to `unit_add`, and checks the `failed` attribute.
- `bd_s390_zfcp_scsi_offline()` scans `/proc/scsi/scsi`, resolves matching HBA/WWPN/LUN through sysfs, and writes to the SCSI device `delete` attribute.
- `bd_s390_zfcp_offline()` removes the LUN through `unit_remove`, checks for remaining LUNs, and runs `chccwdev -d`.

## Dependencies and Interactions

- Uses sysfs paths under `/sys/bus/ccw/drivers/dasd-eckd`, `/sys/bus/ccw/drivers/zfcp`, and `/sys/bus/scsi/devices`.
- Uses external commands:
  - `dasdfmt`
  - `dasd_cio_free`
  - `zfcp_cio_free`
  - `chccwdev`
- Uses Linux DASD ioctl definitions from `<asm/dasd.h>`.
- Uses libblockdev utility command/progress helpers.

## Notable Details

- DASD online returns an error if the device is already online.
- zFCP online logs a warning but continues if the CCW device is already online, because the LUN setup may still be incomplete.
- Input sanitizers normalize casing and shape but do not validate all characters as hexadecimal.
- Many sysfs/proc parsing paths return `BD_S390_ERROR_DEVICE` or `BD_S390_ERROR_IO` with the failing path in the message.
- `bd_s390_zfcp_offline()` checks for remaining LUNs via a glob pattern before offlining the device.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/s390.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/s390.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/s390.h

## Purpose

Public API header for the libblockdev s390 plugin.

## Main API Surface

- Error domain:
  - `bd_s390_error_quark()`
  - `BDS390Error`
- Technology categories:
  - DASD,
  - zFCP.
- Technology modes:
  - modify,
  - query.

## Important Functions Declared

- Lifecycle and availability:
  - `bd_s390_init()`
  - `bd_s390_close()`
  - `bd_s390_is_tech_avail()`
- DASD operations:
  - `bd_s390_dasd_format()`
  - `bd_s390_dasd_needs_format()`
  - `bd_s390_dasd_online()`
  - `bd_s390_dasd_is_ldl()`
  - `bd_s390_dasd_is_fba()`
- Input normalization:
  - `bd_s390_sanitize_dev_input()`
  - `bd_s390_zfcp_sanitize_wwpn_input()`
  - `bd_s390_zfcp_sanitize_lun_input()`
- zFCP operations:
  - `bd_s390_zfcp_online()`
  - `bd_s390_zfcp_scsi_offline()`
  - `bd_s390_zfcp_offline()`

## Dependencies and Interactions

- Publicly depends on GLib and blockdev utils for `BDExtraArg`.
- Implemented by `s390.c` using sysfs, procfs, ioctl, and external s390 tooling.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/s390.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/plugins/smart/Makefile.am

## Purpose

Automake build definition for the SMART plugin variants.

## Main Responsibilities

- Install `smart.h` when either SMART backend is enabled.
- Build `libbd_smart.la` when `WITH_SMART` is enabled.
- Build `libbd_smartmontools.la` when `WITH_SMARTMONTOOLS` is enabled.
- Share common SMART sources and dependency-check sources between variants.

## Build Behavior

For `WITH_SMART`:
- Builds `libbd_smart.la`.
- Uses `GLIB_CFLAGS`, `GIO_CFLAGS`, `SMART_CFLAGS`, and `DRIVEDB_H_CFLAGS`.
- Links blockdev utils, GLib/GIO, and SMART backend libraries.
- Sources include:
  - `smart.h`
  - `smart-private.h`
  - `smart-common.c`
  - `drivedb-parser.c`
  - `libatasmart.c`
  - `../check_deps.c`
  - `../check_deps.h`

For `WITH_SMARTMONTOOLS`:
- Builds `libbd_smartmontools.la`.
- Adds `JSON_GLIB_CFLAGS` and links `JSON_GLIB_LIBS`.
- Sources include:
  - `smart.h`
  - `smart-private.h`
  - `smart-common.c`
  - `drivedb-parser.c`
  - `smartmontools.c`
  - `../check_deps.c`
  - `../check_deps.h`

## Notable Details

- Both libraries use `-version-info 3:0:0`, `--no-undefined`, and export symbols matching `^bd_.*`.
- Both define `PACKAGE_SYSCONF_DIR` for runtime config path handling.
- `drivedb-parser.c` is common to both SMART implementations.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/drivedb-parser.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/smart/drivedb-parser.c

## Purpose

Parses compiled-in smartmontools drive database entries to map SMART attribute IDs to model-specific attribute names.

## Main Responsibilities

- Free arrays of `DriveDBAttr` records.
- Provide a no-op lookup when `drivedb.h` is unavailable.
- When `drivedb.h` is available, include the generated known-drives table.
- Parse `-v` preset definitions from drive database records.
- Match drive model and optional firmware regexes.
- Return a NULL-terminated array of SMART attribute ID/name mappings.

## Important Functions

- `free_drivedb_attrs()` frees each attribute name, each record, and the array.
- `parse_attribute_def()` parses smartmontools-style `id,format[+],name[,HDD|SSD]` attribute definitions and ignores definitions without an attribute ID.
- `parse_presets_str()` scans option-style preset strings and records parsed `-v` attribute definitions in a hash table.
- `drivedb_lookup_drive()` builds defaults when requested, overlays drive-specific presets for matching model/firmware entries, and converts the hash table to a `DriveDBAttr **`.

## Dependencies and Interactions

- Includes `smart.h` and `smart-private.h` for `DriveDBAttr`.
- Uses GLib regex and hash table APIs.
- Uses `bd_utils_log_format()` for debug logging on invalid regexes.
- The compiled-in `builtin_knowndrives` array is populated by including `<drivedb.h>` when `HAVE_DRIVEDB_H` is defined.

## Notable Details

- Entries with model families `VERSION`, `USB`, and `DEFAULT` are skipped during drive-specific matching; `DEFAULT` is handled separately when requested.
- Attribute definitions are keyed by numeric ID, so later matching presets replace earlier/default names.
- The firmware regex path compiles the firmware regex but matches it against `model`, not `fw`, which is a notable behavior to verify if firmware-specific presets matter.
- Returned attribute order follows hash-table iteration order, not numeric ID order.

<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/drivedb-parser.c -->