# Group Research: group_677_libblockdev_sources_virtualization_libblockdev_src_plugins_smart_lib_551e7793d34d

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/virtualization/libblockdev`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/libatasmart.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/smart/libatasmart.c

This file implements the SMART plugin backend using `libatasmart`. It supports ATA SMART information retrieval and ATA self-test triggering, but explicitly reports SCSI SMART and SMART enable/disable as unavailable for this backend.

Key entry points:
- `_smart_close_plugin()` is a no-op backend close hook.
- `bd_smart_check_deps()` always returns `TRUE` because the backend is linked against libatasmart rather than checking an external utility.
- `bd_smart_is_tech_avail()` returns available for `BD_SMART_TECH_ATA`, unavailable for `BD_SMART_TECH_SCSI`, and unavailable for unknown technologies.
- `bd_smart_ata_get_info()` opens a device with `sk_disk_open()`, parses SMART data, and returns a populated `BDSmartATA`.
- `bd_smart_ata_get_info_from_data()` parses libatasmart blob data through `sk_disk_set_blob()`.
- `bd_smart_scsi_get_info()` always fails with `BD_SMART_ERROR_TECH_UNAVAIL`.
- `bd_smart_set_enabled()` always fails because libatasmart does not expose that control here.
- `bd_smart_device_self_test()` maps libblockdev self-test operations to `SkSmartSelfTest` and calls `sk_disk_smart_self_test()`.

The central conversion path is `parse_sk_data()`: it reads SMART data, asks libatasmart for overall health, parses status/capability fields, computes power-on time and power-cycle count, parses attributes into `BDSmartATAAttribute`, and terminates the attribute vector with `NULL`.

Attribute parsing:
- `parse_attr_cb()` copies libatasmart parsed attributes into libblockdev fields.
- Raw values are packed from six raw bytes into a 64-bit integer.
- `print_value()` mirrors a private libatasmart formatting helper for human-readable values.
- Units are translated from `SkSmartAttributeUnit` to `BDSmartATAAttributeUnit`.
- Attribute failure state is inferred from normalized value/worst versus threshold.
- If built with `HAVE_DRIVEDB_H`, the backend uses `drivedb_lookup_drive()` and `well_known_attrs` to distrust attributes whose smartmontools drive DB name does not match libblockdev’s whitelist.

Temperature handling is conservative: `calculate_temperature()` checks attributes 194 and 190, requiring millikelvin units for those IDs, and returns zero if no recognized temperature attribute is present. `parse_sk_data()` stores temperature as Kelvin after dividing millikelvin by 1000.

Important behavior and caveats:
- `extra` arguments are ignored in this backend, unlike the smartmontools backend.
- Several ATA fields are marked TODO or zero-filled, including automatic offline data collection, offline capabilities, and broader SMART capabilities.
- `bd_smart_ata_get_info_from_data()` leaks the opened `SkDisk` if `sk_disk_set_blob()` fails because it returns without `sk_disk_free(d)`.
- `bd_smart_scsi_get_info()` returns `FALSE` from a pointer-returning function; this works as `NULL` but is stylistically imprecise.
- Errors use locale-neutral `strerror_l(errno, _C_LOCALE)` via `smart-private.h`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/libatasmart.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smart-common.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/smart/smart-common.c

This file contains SMART plugin documentation, the shared SMART error domain, lifecycle glue, and boxed-struct copy/free helpers shared by backend implementations.

The top-level documentation explains two SMART backends:
- `libatasmart`, the default lightweight ATA-only backend.
- `smartmontools`, the heavier backend that shells out to `smartctl --json` and supports more device types, including SCSI/SAS.

The documentation also establishes important API semantics:
- The NVMe plugin should be used for NVMe health reporting.
- Callers should use tech availability queries because backend capabilities differ.
- ATA attributes expose both backend-specific names and libblockdev “well-known” names.
- Attribute interpretation is best-effort because vendors reuse SMART IDs and smartmontools JSON does not expose all formatting context.
- The `extra` argument is mainly meaningful for smartmontools, especially for `--device=` passthrough override.

Implemented functions:
- `bd_smart_error_quark()` returns the shared SMART `GQuark`.
- `bd_smart_init()` is currently a no-op returning `TRUE`.
- `bd_smart_close()` calls backend-specific `_smart_close_plugin()`.
- `bd_smart_ata_attribute_free()` frees an ATA attribute and owned strings.
- `bd_smart_ata_attribute_copy()` shallow-copies the struct then deep-copies owned strings.
- `bd_smart_ata_free()` frees a NULL-terminated ATA attribute vector and the `BDSmartATA`.
- `bd_smart_ata_copy()` shallow-copies scalar fields and deep-copies each attribute.
- `bd_smart_scsi_free()` frees `scsi_ie_string` and the `BDSmartSCSI`.
- `bd_smart_scsi_copy()` shallow-copies scalar fields and deep-copies `scsi_ie_string`.

Research relevance:
- This is the shared ABI/ownership layer for SMART boxed data.
- The copy functions preserve scalar fields exactly and only duplicate pointer-owned members.
- Backend implementations must return structures compatible with these ownership rules.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smart-common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smart-private.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/smart/smart-private.h

This private header defines backend-shared SMART internals. It is not part of the public libblockdev API.

Contents:
- Includes GLib, GObject, `blockdev/utils.h`, and `smart.h`.
- Defines `_C_LOCALE` as `(locale_t) 0` for locale-neutral libc error formatting.
- Defines `DriveDBAttr`, a simple `{ id, name }` pair used with the optional compiled smartmontools drive database parser.
- Defines `struct WellKnownAttrInfo`, mapping an attribute ID to:
  - libatasmart-style well-known name,
  - libblockdev pretty-value unit,
  - a NULL-terminated list of accepted smartmontools names.

The large `well_known_attrs[256]` table is a conservative translation/validation table for ATA SMART attribute IDs. It covers common HDD and SSD IDs such as raw read error rate, spin-up time, reallocated sector count, power-on hours, temperature attributes, pending sectors, UDMA CRC errors, wear/endurance attributes, and LBA counters.

Declared internal functions:
- `_smart_close_plugin()` lets common close code call backend-specific cleanup.
- `drivedb_lookup_drive()` returns optional drive-specific attribute definitions.
- `free_drivedb_attrs()` frees drive DB lookup results.

Research relevance:
- This table is the semantic bridge between libatasmart names and smartmontools names.
- Both SMART backends use it to decide whether an attribute should receive a trusted `well_known_name`.
- The table intentionally does not solve all vendor-specific remapping and leaves some TODO entries.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smart-private.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smart.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/smart/smart.h

This public header defines the SMART plugin API, public structs, enums, and exported functions.

Public error and tech enums:
- `BDSmartError`: technology unavailable, general failure, invalid argument.
- `BDSmartTech`: ATA and SCSI.
- `BDSmartTechMode`: info and self-test modes.

ATA API model:
- Defines offline data collection statuses and capability bits.
- Defines ATA self-test statuses.
- Defines miscellaneous ATA SMART capability bits.
- Defines pretty-value units: unknown, none, milliseconds, sectors, millikelvin, small percent, percent, and megabytes.
- Defines ATA attribute flags mirroring SMART attribute flag bits.

`BDSmartATAAttribute` stores:
- Attribute ID.
- Backend-specific `name`.
- Trusted normalized `well_known_name`, or `NULL`.
- Normalized value, worst, threshold.
- Past/current failure flags.
- Raw 64-bit value.
- Flag bitmask.
- Parsed pretty value, unit, and printable string.

`BDSmartATA` stores:
- SMART support/enabled and overall status.
- Offline data collection status/capabilities.
- Self-test status, remaining percent, and polling hints.
- SMART capabilities.
- NULL-terminated ATA attribute vector.
- Power-on time in minutes, power-cycle count, and temperature in Kelvin.

SCSI API model:
- `BDSmartSCSIInformationalException` enumerates SCSI informational exception ASC/ASCQ categories, including warnings and impending failure classes.
- `BDSmartSCSIBackgroundScanStatus` enumerates background scan states.
- `BDSmartSCSI` stores support/enabled/status, informational exception fields, background scan metrics, error counters, cycle counters, grown defect list, power-on time, and temperature fields.

Exported functions:
- Boxed free/copy helpers for ATA, ATA attributes, and SCSI structs.
- Plugin lifecycle/dependency functions: `bd_smart_check_deps()`, `bd_smart_init()`, `bd_smart_close()`, `bd_smart_is_tech_avail()`.
- Operational calls: ATA info from device or data, SCSI info, SMART enable/disable, and self-test execution.

Research relevance:
- This header is the authoritative contract for what the two SMART backends must populate.
- Some fields are explicitly backend-dependent; comments note that some are only supported by smartmontools.
- Temperature is documented as Kelvin, while internal backends convert from Celsius or millikelvin.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smart.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smartmontools.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/smart/smartmontools.c

This file implements the SMART plugin backend using the external `smartctl` command from smartmontools. It parses `smartctl --json` output into the public `BDSmartATA` and `BDSmartSCSI` structs.

Dependency handling:
- Requires `smartctl >= 7.0`.
- Uses `check_deps()` with a regex matching `smartctl ([\d\.]+) .*`.
- `_smart_close_plugin()` clears the cached dependency bitset.
- `bd_smart_is_tech_avail()` treats all SMART tech/mode combinations as supported if smartctl is available.
- `bd_smart_check_deps()` delegates to `bd_smart_is_tech_avail()`.

Error parsing:
- `get_error_message_from_exit_code()` explains smartctl low-bit failures for command parse, device open/identify, and SMART command/checksum problems.
- `parse_smartctl_error()` parses stdout JSON, validates `json_format_version`, extracts error messages, and treats only exit status bits `0x01`, `0x02`, and `0x04` as hard failures.
- This means health-related smartctl status bits outside `0x07` can still produce usable parsed data.

ATA parsing:
- `parse_ata_smart_attributes()` reads the `ata_smart_attributes.table` array and fills ID, name, normalized values, threshold, failure state, raw value/string, and flags.
- `lookup_well_known_attr()` validates smartmontools attribute names against `well_known_attrs`, assigns trusted libatasmart-style names, and attempts unit-specific pretty-value conversion.
- Millisecond values are parsed from smartctl time strings when possible.
- Temperature values are parsed from Celsius strings and converted to millikelvin.
- Unsupported units fall back to unknown.
- `parse_ata_smart()` reads support/enabled state, overall status, offline collection status, self-test status/polling, capabilities, attribute table, power-on time, power-cycle count, and current temperature.

SCSI parsing:
- `parse_scsi_smart()` reads SMART support/enabled/health status, SCSI informational exception fields, temperature warning, current/trip temperature, background scan status/progress/counts, start-stop/load-unload counters, grown defect list, read/write error counter logs, processed byte totals, and power-on time.
- ASC/ASCQ values are mapped into the public `BDSmartSCSIInformationalException` enum, including `0x0b` warnings and `0x5d` impending failure categories.
- Background scan status values are mapped to public enum values, with unknown values copied through.

Operational functions:
- `bd_smart_ata_get_info()` runs `smartctl --info --health --capabilities --attributes --json <device>`.
- `bd_smart_ata_get_info_from_data()` parses a JSON blob supplied by the caller, unlike the libatasmart backend which parses libatasmart binary blob data.
- `bd_smart_scsi_get_info()` runs `smartctl --info --health --attributes --log=error --log=background --json <device>`.
- `bd_smart_set_enabled()` runs `smartctl --json --smart=on/off <device>`.
- `bd_smart_device_self_test()` maps libblockdev self-test ops to smartctl `--abort` or `--test=...`.

Important behavior and caveats:
- `extra` arguments are passed through the exec utility, allowing smartctl options such as `--device=`.
- The backend depends on JSON key stability and is intentionally tolerant of many optional missing sections.
- Hard parsing errors are returned as `BD_SMART_ERROR_INVALID_ARGUMENT`.
- SCSI parsing currently ignores the `error` parameter and does not fail for missing optional sections.
- Temperature conversion here stores Celsius plus 273, while ATA attribute pretty values use millikelvin conversion logic.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/smart/smartmontools.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/swap.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/swap.c

This file implements the swap plugin: creating swap signatures, activating/deactivating swap, querying active status, and setting/validating labels and UUIDs.

Dependency handling:
- Requires `mkswap >= 2.23.2` for creation.
- Requires `swaplabel` for label and UUID mutation.
- Caches dependency checks in `avail_deps`, protected by `deps_check_lock`.
- `bd_swap_close()` clears the dependency cache.
- `bd_swap_is_tech_avail()` maps requested tech modes to the required utility masks.

Core functions:
- `bd_swap_error_quark()` returns the swap error domain.
- `bd_swap_init()` is a no-op returning `TRUE`.
- `bd_swap_mkswap()` builds `mkswap -f`, optionally adds `-L <label>` and `-U <uuid>`, appends the target device, and passes extra args to `bd_utils_exec_and_report_error()`.
- `bd_swap_swapon()` validates the target with libblkid before calling the kernel `swapon()` syscall.
- `bd_swap_swapoff()` calls the kernel `swapoff()` syscall.
- `bd_swap_swapstatus()` scans `/proc/swaps` for the device path, resolving `/dev/mapper/` and `/dev/md/` paths first.
- `bd_swap_check_label()` enforces the 16-character swap label limit.
- `bd_swap_set_label()` runs `swaplabel -L <label> <device>`.
- `bd_swap_check_uuid()` checks ASCII and validates RFC-4122 parsing with `uuid_parse()`.
- `bd_swap_set_uuid()` runs `swaplabel -U <uuid> <device>`.

`bd_swap_swapon()` validation flow:
- Starts a progress task.
- Creates a blkid probe and opens the device read-only.
- Retries `blkid_probe_set_device()` and `blkid_do_safeprobe()` on transient busy states.
- Requires detected `TYPE=swap`.
- Rejects old `SWAP-SPACE`, suspend signatures `S1SUSPEND`/`S2SUSPEND`, and unknown signatures.
- Computes swap page size from `SBMAGIC_OFFSET + strlen(SBMAGIC)` and rejects mismatches with system page size.
- Applies optional priority with `SWAP_FLAG_PREFER` and priority bit packing.
- Calls `swapon()` and reports completion or a detailed error.

Research relevance:
- This plugin mixes direct syscalls with external util-linux commands.
- Activation is intentionally defensive to avoid enabling stale suspend images or incompatible swap formats.
- `bd_swap_swapstatus()` is path-prefix based against `/proc/swaps`, so exact path formatting and symlink resolution matter.
- UUID validation lowercases input before parsing to tolerate uppercase ASCII UUIDs.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/swap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/swap.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/swap.h

This public header defines the swap plugin API.

Public definitions:
- `BD_SWAP_ERROR` maps to `bd_swap_error_quark()`.
- `BDSwapError` includes technology unavailable, unknown state, activation failure, old swap format, suspend image, unknown swap format, page-size mismatch, invalid label, and invalid UUID.
- `BDSwapTech` has one technology, `BD_SWAP_TECH_SWAP`.
- `BDSwapTechMode` includes create, activate/deactivate, query, set label, and set UUID.

Exported functions:
- Lifecycle: `bd_swap_init()`, `bd_swap_close()`.
- Availability: `bd_swap_is_tech_avail()`.
- Operations: `bd_swap_mkswap()`, `bd_swap_swapon()`, `bd_swap_swapoff()`, `bd_swap_swapstatus()`, `bd_swap_set_label()`, `bd_swap_check_label()`, `bd_swap_set_uuid()`, `bd_swap_check_uuid()`.

Research relevance:
- The error enum numeric order is used by Python overrides to map specific swap activation failures into more granular exception classes.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/swap.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/python/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/python/Makefile.am

This Automake file declares the Python build subtree.

Contents:
- `SUBDIRS = gi`
- `MAINTAINERCLEANFILES = Makefile.in`

Research relevance:
- Python support is organized under `src/python/gi`.
- No build logic beyond delegation is present here.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/python/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/python/gi/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/python/gi/Makefile.am

This Automake file declares the GI Python override subtree.

Contents:
- `SUBDIRS = overrides`
- `MAINTAINERCLEANFILES = Makefile.in`

Research relevance:
- The actual Python override module is built and installed from `src/python/gi/overrides`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/python/gi/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/python/gi/overrides/BlockDev.py -->
# File Research: sources/virtualization/libblockdev/src/python/gi/overrides/BlockDev.py

This Python file provides PyGObject overrides for libblockdev’s introspected `BlockDev` module. Its goals are more Pythonic constructors/default arguments, ergonomic extra command arguments, and richer exception classes.

Module setup:
- Imports the introspected `BlockDev` module through `gi.importer.modules`.
- Defines `bd_plugins`, mapping lowercase plugin names to `BlockDev.Plugin` enum values.
- Installs generic `__str__`, `__repr__`, and `__deepcopy__` behavior on all `GObject.GBoxed` subclasses in the module.
- `__repr__` renders size-like integer fields with `bytesize.Size`.

Boxed constructors and helper types:
- `PluginSpec` wraps `BlockDev.PluginSpec.new()`.
- `ExtraArg` wraps `BlockDev.ExtraArg.new()`.
- `FSMkfsOptions` creates an options object with Python defaults.
- `CryptoLUKSPBKDF`, `CryptoLUKSExtra`, `CryptoKeyslotContext`, and `CryptoIntegrityExtra` provide Python constructors for crypto boxed structs.
- `CryptoKeyslotContext` enforces exactly one of passphrase, keyfile, keyring, or volume key.

Extra argument handling:
- `_get_extra(extra, kwargs, cmd_extra=True)` accepts either a dict or list of `BlockDev.ExtraArg`.
- Additional keyword arguments become extra args.
- With `cmd_extra=True`, keyword names are prefixed with `--`; with `False`, names are passed as-is.
- Returns `None` if no extra args are present.

Function overrides:
- Adds defaults and keyword support for initialization, Btrfs, crypto, DM, loop, filesystem, LVM, MD RAID, s390 DASD, swap, partitioning, NVDIMM, and NVMe functions.
- Most wrappers save the original introspected function in a private variable, normalize defaults/extra args, and call the original.
- Filesystem and LVM wrappers dominate the file and mainly expose default arguments plus `extra`/`**kwargs`.
- Swap overrides include `swap_mkswap(device, label=None, uuid=None, extra=None, **kwargs)` and `swap_swapon(device, priority=-1)`.
- One-member enum workaround classes are defined for `DMTech`, `LoopTech`, `MDTech`, `SwapTech`, and `NVDIMMTech`.

Utility function:
- `plugin_specs_from_names(plugin_names)` converts a list of plugin name strings into `PluginSpec` objects using `bd_plugins`.

Exception model:
- `XRule` defines exception transformation rules.
- `ErrorProxy` lazily proxies plugin-prefixed functions and transforms exceptions.
- `BlockDevError` is the common base for libblockdev-specific Python exceptions.
- Plugin-specific exception classes include `BtrfsError`, `CryptoError`, `DMError`, `LoopError`, `LVMError`, `MDRaidError`, `MpathError`, `SwapError`, `PartError`, `FSError`, `S390Error`, `UtilsError`, `NVDIMMError`, `NVMEError`, and `SMARTError`.
- Swap has more granular subclasses for activation, old format, suspend image, unknown format, and page-size mismatch.
- `BlockDevNotImplementedError` maps GLib “function called, but not implemented” messages.
- Error proxies are exported as `btrfs`, `crypto`, `dm`, `loop`, `lvm`, `md`, `mpath`, `swap`, `part`, `fs`, `nvdimm`, `nvme`, `s390`, `smart`, and `utils`.

Research relevance:
- This file is the main compatibility/ergonomics surface for Python callers.
- It mirrors C error enum numeric codes in Python exception rules; changes to C enum ordering can break specific exception mapping.
- It makes `BlockDev.swap.swapon()` raise plugin-specific Python exceptions while `BlockDev.swap_swapon()` remains the raw introspected function.
- The `extra` keyword convention is a major bridge to C `BDExtraArg`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/python/gi/overrides/BlockDev.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/python/gi/overrides/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/python/gi/overrides/Makefile.am

This Automake file installs Python GI overrides.

Behavior:
- Only active when `WITH_PYTHON3` is set.
- Computes `py3libdir` using `python3 -c "import sysconfig; ..."` with `platbase=${exec_prefix}`.
- Installs `BlockDev.py` into `$(py3libdir)/gi/overrides`.
- Distributes `__init__.py` as a non-installed source.
- Cleans `Makefile.in` on maintainer clean.

Research relevance:
- This is the installation hook that makes PyGObject load the `BlockDev.py` overrides automatically.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/python/gi/overrides/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/utils/Makefile.am

This Automake file builds and installs the shared libblockdev utility library.

Build targets:
- Builds `libbd_utils.la`.
- Uses GLib, udev, and kmod CFLAGS.
- Enforces `-Wall -Wextra -Werror`.
- Uses libtool version info `3:0:0` and linker `--no-undefined`.
- Links GLib, math, GIO, udev, and kmod libraries.

Sources:
- `utils.h`
- `exec.c/.h`
- `sizes.h`
- `extra_arg.c/.h`
- `dev_utils.c/.h`
- `module.c/.h`
- `dbus.c/.h`
- `logging.c/.h`

Install outputs:
- Public headers under `$(includedir)/blockdev`.
- `blockdev-utils.pc` under pkg-config directory.

Research relevance:
- The files in this group are part of a shared utility library used by plugins, not private plugin-only helpers.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/blockdev-utils.pc.in -->
# File Research: sources/virtualization/libblockdev/src/utils/blockdev-utils.pc.in

This is the pkg-config template for `libbd_utils`.

Fields:
- Defines `prefix`, `exec_prefix`, `includedir`, and `libdir`.
- `Name: BlockDev-utils`
- Describes the library as utility functions used by libblockdev.
- Points to `https://github.com/storaged-project/libblockdev`.
- Uses `@VERSION@`.
- Requires `glib-2.0`.
- Exposes `-L${libdir} -lbd_utils`.
- Exposes `-I${includedir}`.

Research relevance:
- External consumers can compile/link against the utility library independently through pkg-config.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/blockdev-utils.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dbus.c -->
# File Research: sources/virtualization/libblockdev/src/utils/dbus.c

This file implements a D-Bus service availability helper using GIO.

Public functions:
- `bd_utils_dbus_error_quark()` returns the utility D-Bus error domain.
- `bd_utils_dbus_service_available()` checks whether a service is currently listed, activatable, and introspectable.

Availability flow:
- Uses an existing `GDBusConnection` if supplied, otherwise connects to the requested bus type.
- Calls `org.freedesktop.DBus.ListNames`.
- Calls `org.freedesktop.DBus.ListActivatableNames`.
- Searches both lists for `bus_name`.
- If found, calls `org.freedesktop.DBus.Introspectable.Introspect` on `obj_prefix` to verify access and possibly trigger activation.
- Returns `TRUE` only if the service is found and introspection succeeds.

Research relevance:
- This helper distinguishes “known/activatable name” from “usable service root”.
- Error details are mostly propagated from GIO calls; the local enum is defined but not used for custom errors in this implementation.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dbus.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dbus.h -->
# File Research: sources/virtualization/libblockdev/src/utils/dbus.h

This public header declares the D-Bus utility API.

Definitions:
- `BD_UTILS_DBUS_ERROR` maps to `bd_utils_dbus_error_quark()`.
- `BDUtilsDBusError` defines generic failure and no-exist variants.
- Declares `bd_utils_dbus_service_available()`.

Research relevance:
- The enum is broader than the current implementation, which mainly propagates GIO errors and returns `FALSE` for missing services without setting a custom no-exist error.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dbus.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dev_utils.c -->
# File Research: sources/virtualization/libblockdev/src/utils/dev_utils.c

This file implements block-device resolution and udev symlink discovery.

Functions:
- `bd_utils_dev_utils_error_quark()` returns the device-utils error domain.
- `_is_block_device()` uses `stat()` and `S_ISBLK` to verify a path is a block device.
- `bd_utils_resolve_device()` normalizes a device spec to `/dev/...`, resolves one symlink level, and verifies the result is a block device.
- `bd_utils_get_device_symlinks()` resolves the device, looks it up in udev’s block subsystem, and returns all devlinks known to udev.

Resolution details:
- If `dev_spec` lacks `/dev/`, `/dev/` is prepended.
- `g_file_read_link()` returning `G_FILE_ERROR_INVAL` is treated as “not a symlink”.
- Relative symlinks beginning with `../` are converted to `/dev/<target after ../>`.
- Other symlink targets are converted to `/dev/<target>`.
- All returned device paths are verified as block devices.

Research relevance:
- `bd_swap_swapstatus()` depends on this helper for `/dev/mapper/` and `/dev/md/` names.
- Only a single symlink read is performed; nested symlink behavior depends on the immediate `/dev` layout.
- udev lookup uses sysname from the resolved `/dev/<name>` path.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dev_utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dev_utils.h -->
# File Research: sources/virtualization/libblockdev/src/utils/dev_utils.h

This public header declares device utility APIs.

Definitions:
- `BD_UTILS_DEV_UTILS_ERROR` maps to `bd_utils_dev_utils_error_quark()`.
- Defines `_C_LOCALE` for locale-neutral libc errors.
- `BDUtilsDevUtilsError` currently has one generic failure value.
- Declares `bd_utils_resolve_device()` and `bd_utils_get_device_symlinks()`.

Research relevance:
- Exposes `/dev` path resolution and udev devlink discovery to plugins and consumers.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/dev_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/exec.c -->
# File Research: sources/virtualization/libblockdev/src/utils/exec.c

This file implements shared subprocess execution, command logging, progress reporting, utility version checks, and a simple file-write helper.

Global state:
- `id_counter` and `task_id_counter` are protected by mutexes.
- `prog_func` is a global progress callback.
- `thread_prog_func` is thread-local and overrides the global callback.
- Commands are run with environment forced to `LC_ALL=C.UTF-8` and `LANGUAGE` unset.

Command argument handling:
- `_append_extra_args()` appends a NULL-terminated list of `BDExtraArg` option/value pairs to a command argv.
- Empty option or value strings are skipped.
- Extra args are appended after the base argv.

Synchronous capture path:
- `bd_utils_exec_and_capture_output_no_progress()` uses `g_spawn_sync()`.
- Captures stdout/stderr, logs command output, and returns the process exit code through `status`.
- Abnormal process termination is treated as a spawn failure.
- Nonzero normal exit is not itself a function failure in this API; callers inspect `status`.

Error-reporting wrappers:
- `bd_utils_exec_and_report_error()` delegates to progress execution and requires exit code zero.
- `bd_utils_exec_and_report_error_no_progress()` delegates to status-error capture.
- `bd_utils_exec_and_report_status_error()` converts nonzero exit status into `BD_UTILS_EXEC_ERROR_FAILED`.
- `bd_utils_exec_and_capture_output()` requires successful execution and non-empty stdout, otherwise reports either process failure or no-output error.

Progress execution path:
- `_utils_exec_and_report_progress()` uses `g_spawn_async_with_pipes()`.
- Optionally writes a provided input string to stdin.
- Sets stdout/stderr pipes nonblocking.
- Polls both outputs concurrently.
- `_process_fd_event()` reads chunks, splits on newline or NUL, calls a progress extractor callback when supplied, and filters progress lines out of collected output.
- Reports started/progress/finished events through the configured progress callback.
- Waits with `waitpid()` and maps signal death to `128 + signal`.

Version utilities:
- `bd_utils_version_cmp()` compares numeric dotted versions with optional `-R` suffix and rejects unsupported formats.
- `bd_utils_check_util_version()` locates a utility in PATH, runs its version command, extracts a version with an optional regex, and compares it to a minimum.

Progress API:
- `bd_utils_init_prog_reporting()` sets the global callback.
- `bd_utils_init_prog_reporting_thread()` sets the current thread callback.
- `bd_utils_mute_prog_reporting_thread()` suppresses progress in the current thread even if a global callback exists.
- `bd_utils_prog_reporting_initialized()` reflects global/thread callback state.
- `bd_utils_report_started()`, `bd_utils_report_progress()`, and `bd_utils_report_finished()` dispatch progress events.

Other helper:
- `bd_utils_echo_str_to_file()` writes a string to a file with `GIOChannel`, flushes/shuts it down, and prefixes errors with context.

Research relevance:
- This is the central utility path used by many plugins for external commands.
- It deliberately separates “spawn succeeded and status captured” from “command exit code was zero”.
- Locale forcing helps parsers consume predictable command output.
- The progress path treats NUL bytes like line separators for extractor callbacks.
- Command logging includes full argv and captured stdout/stderr.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/exec.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/exec.h -->
# File Research: sources/virtualization/libblockdev/src/utils/exec.h

This public header declares execution and progress-reporting utilities.

Types:
- `BDUtilsProgStatus`: started, progress, finished.
- `BDUtilsProgFunc`: callback receiving task ID, status, completion percent, and message.
- `BDUtilsProgExtract`: callback that parses a line from stdout/stderr and optionally extracts progress.

Error enum:
- `BDUtilsExecError` includes generic failure, no output, invalid version, utility unavailable, unknown version, low version, utility check error, feature check error, and feature unavailable.

Declared APIs:
- Command execution with or without progress.
- Output capture with or without progress.
- Execution with stdin input.
- Version comparison and utility version checks.
- Progress callback initialization, thread-local override, thread muting, and explicit progress reporting.
- Task ID allocation and task status logging.
- String-to-file write helper.

Research relevance:
- The comments document output ordering caveats: stdout and stderr are read simultaneously with no guaranteed ordering for progress extraction.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/extra_arg.c -->
# File Research: sources/virtualization/libblockdev/src/utils/extra_arg.c

This file implements the boxed `BDExtraArg` helper used to pass command-line extra arguments through libblockdev APIs.

Functions:
- `bd_extra_arg_copy()` deep-copies `opt` and `val`.
- `bd_extra_arg_free()` frees owned strings and the struct.
- `bd_extra_arg_list_free()` frees a NULL-terminated vector of `BDExtraArg*`.
- `bd_extra_arg_get_type()` registers `BDExtraArg` as a boxed GObject type.
- `bd_extra_arg_new()` constructs a new extra arg, storing empty strings for NULL option/value inputs.

Research relevance:
- This boxed type is exposed to GI/Python and consumed by `exec.c`’s `_append_extra_args()`.
- It models option and value separately, allowing options without parameters by using empty or NULL values.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/extra_arg.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/extra_arg.h -->
# File Research: sources/virtualization/libblockdev/src/utils/extra_arg.h

This public header defines the `BDExtraArg` boxed type.

Contents:
- `BD_UTIL_TYPE_EXTRA_ARG` macro.
- `bd_extra_arg_get_type()` declaration.
- `BDExtraArg` struct with owned `gchar *opt` and `gchar *val`.
- Copy, free, list-free, and constructor declarations.

Research relevance:
- `BDExtraArg` is the common typed transport for optional command-line switches across many plugins and language bindings.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/extra_arg.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/logging.c -->
# File Research: sources/virtualization/libblockdev/src/utils/logging.c

This file implements shared logging helpers for libblockdev utilities.

State:
- Default log function is `bd_utils_log_stdout`.
- Default log level is `BD_UTILS_LOG_DEBUG` in debug builds and `BD_UTILS_LOG_WARNING` otherwise.

Functions:
- `bd_utils_init_logging()` sets the log callback or disables logging with `NULL`.
- `bd_utils_set_log_level()` changes the threshold.
- `bd_utils_log()` logs a preformatted message if callback and threshold permit.
- `bd_utils_log_format()` formats a printf-style message with `g_vasprintf()` and logs it.
- `bd_utils_log_stdout()` maps syslog-style levels to GLib logging:
  - debug to `g_debug()` only in debug builds,
  - info/notice to `g_info()`,
  - warning/error to `g_warning()`,
  - emergency/alert/critical to `g_critical()`.

Research relevance:
- `exec.c` depends on this for command execution logs.
- Debug logs are compiled out unless the build enables debug.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/logging.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/logging.h -->
# File Research: sources/virtualization/libblockdev/src/utils/logging.h

This public header declares shared logging utilities.

Definitions:
- Defines syslog-compatible numeric levels directly because GObject Introspection cannot use redefined syslog constants cleanly.
- Defines `BDUtilsLogFunc(level, msg)` callback type.
- Declares logging initialization, log-level setting, direct logging, formatted logging, and stdout/GLib logging helper.

Research relevance:
- Provides the log API consumed by execution utilities and plugins without requiring callers to include syslog constants through GI.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/logging.h -->