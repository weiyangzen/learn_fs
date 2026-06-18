# Group Research: group_671_libblockdev_sources_virtualization_libblockdev_src_Makefile_am_sourc_b1863b8189c8

Scope source: `Docs/research_subset_a.md`, which includes `sources/virtualization/libblockdev`.

Files researched completely: 13 files, 2,850 lines, 104,387 bytes.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/Makefile.am

## Role
Top-level Automake entry for `src/`. It defines the build traversal order for libblockdev's source subtree.

## Contents
- `SUBDIRS = utils plugins lib python` builds utilities first, then plugin shared libraries, then the central `libblockdev` library, then Python bindings.
- `MAINTAINERCLEANFILES = Makefile.in` marks the generated Automake output as maintainer-clean.

## Dependencies and Interactions
- The ordering is meaningful: `src/lib/Makefile.am` links against `../utils/libbd_utils.la`, while plugins also link against utils.
- `plugins` is built before `lib`, but the core library dynamically loads plugin shared objects at runtime rather than statically linking them.

## Filesystem/Storage Relevance
This file is infrastructure only. Its main filesystem relevance is that it arranges build order for block-device utility code, filesystem/block plugins, the loader library, and bindings.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/lib/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/lib/Makefile.am

## Role
Build rules for the central `libblockdev.la` library, its generated plugin API wrappers, GObject introspection metadata, installed headers, and pkg-config file.

## Build Targets
- Includes `$(INTROSPECTION_MAKEFILE)` and descends into `plugin_apis`, where `.api` files generate C/H boilerplate wrappers.
- Builds `libblockdev.la` from `blockdev.c`, `blockdev.h`, `plugins.c`, and `plugins.h`.
- Links `libblockdev.la` with `../utils/libbd_utils.la`, GLib/GObject, and `-ldl`.
- Uses `-version-info 3:0:0`, `--no-undefined`, and exports symbols matching `^bd_.*`.
- Installs `blockdev.h` and `plugins.h` under `$(includedir)/blockdev`.
- Installs `${builddir}/blockdev.pc` into `$(libdir)/pkgconfig`.

## Introspection
- If `HAVE_INTROSPECTION` is enabled, it gathers generated plugin API headers for mdraid, swap, btrfs, lvm, crypto, dm, loop, mpath, part, fs, nvdimm, nvme, smart, and conditionally s390.
- Adds utility sources and core library sources to the GIR input set.
- Produces `BlockDev-3.0.gir` and corresponding typelib with `--identifier-prefix=BD` and `--symbol-prefix=bd`.

## Dependencies and Interactions
- The generated `blockdev.c` is derived from `blockdev.c.in`; this Makefile treats `blockdev.c` as maintainer-clean.
- The generated plugin API C files are included directly by `blockdev.c.in`, so `plugin_apis` generation is a prerequisite for a complete build.
- Conditional GObject flags for Btrfs and LVM reflect plugin API exposure that needs GObject type data.

## Filesystem/Storage Relevance
This is the build nexus for libblockdev's runtime plugin-loader API. It exposes a unified library interface while plugin implementations remain separate shared libraries.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/lib/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/lib/blockdev.c.in -->
# File Research: sources/virtualization/libblockdev/src/lib/blockdev.c.in

## Role
Template for the main libblockdev loader implementation. It initializes logging, reads plugin configuration, dynamically loads and unloads plugin shared objects, tracks loaded plugin state, and exposes public initialization/query APIs.

## Structure
- Includes `dlfcn.h`, libblockdev utilities, public core headers, and every generated plugin API wrapper C/H pair.
- S390 plugin wrappers are included only on `__s390__` or `__s390x__`.
- Defines the default config directory as `/etc/libblockdev/@MAJOR_VER@/conf.d/`.
- Maintains global state through `init_lock`, `initialized`, and a static `plugins[BD_PLUGIN_UNDEF]` table of `BDPluginStatus`.
- Keeps three order-sensitive arrays aligned with the `BDPlugin` enum:
  - default shared object names, such as `libbd_lvm.so.@MAJOR_VER@` and `libbd_btrfs.so.@MAJOR_VER@`;
  - plugin handle/spec state;
  - human-readable plugin names.

## Configuration Loading
- `get_config_files()` chooses `LIBBLOCKDEV_CONFIG_DIR` if set, otherwise the default config path.
- Only `.cfg` files are included, and they are sorted lexicographically with `GSequence`.
- `process_config_file()` reads a `sonames` string list per plugin section, preserving configured order despite prepending into GSLists.
- `load_config()` processes config files sequentially and logs/skips malformed files instead of aborting all initialization.
- Missing plugin soname lists are filled with built-in defaults.
- On non-s390 architectures, the S390 plugin default is explicitly removed unless requested.

## Plugin Loading and Unloading
- `unload_plugins()` calls each generated `unload_<plugin>()` wrapper for loaded handles, logging warnings on close failure.
- `load_plugin_from_sonames()` tries configured sonames until one loads, then stores the loaded soname in plugin state.
- `do_load()` dispatches each plugin to its generated `load_<plugin>_from_plugin()` wrapper.
- `load_plugins()` is the central policy function:
  - loads config and defaults;
  - optionally unloads/reloads existing plugins and clears stored sonames;
  - restricts load attempts to explicitly required plugins when `require_plugins` is non-NULL;
  - lets requested specs override default/configured sonames;
  - counts successfully loaded requested/default plugins;
  - returns whether all requested/default plugins loaded.

## Public Initialization API
- `bd_init()` initializes once, sets up logging if provided, loads all or required plugins, and treats missing requested/default plugins as `BD_INIT_ERROR_PLUGINS_FAILED`.
- `bd_ensure_init()` performs an atomic check-and-init/reinit under `init_lock`; if already initialized, it checks whether requested plugins are available before returning early.
- `bd_try_init()` is tolerant of plugin load failures: it returns the `load_plugins()` success state but documents that failure to load a plugin is not considered an error; it can also return loaded plugin names.
- `bd_reinit()` reloads or adds missing plugins. A NULL-first required-plugin array plus `reload=TRUE` is treated as an explicit unload-all request.
- `bd_try_reinit()` mirrors `bd_reinit()` with tolerant plugin-load semantics and optional loaded plugin names.
- `bd_is_initialized()` returns the locked global initialization state.

## Public Query API
- `bd_get_available_plugin_names()` returns a NULL-terminated array container of names for plugins with non-NULL handles. The strings themselves are static.
- `bd_is_plugin_available()` checks handle presence for a valid enum value.
- `bd_get_plugin_soname()` returns a newly duplicated loaded soname or NULL.
- `bd_get_plugin_name()` returns the static plugin name for a valid enum value.

## Error and Concurrency Behavior
- Initialization and reinitialization are serialized with `init_lock`.
- Dependency/plugin load failures are accumulated as boolean success plus GLib `GError`.
- Config directory open failure logs fallback to built-in config.
- Config file parse failures are warnings and do not stop later files.

## Filesystem/Storage Relevance
This file is the runtime switchboard that makes filesystem and block-device operations available through dynamically loaded plugins. For Btrfs, FS, LVM, DM, mdraid, NVMe, and related storage plugins, availability depends on this file successfully resolving plugin sonames and handles.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/lib/blockdev.c.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/lib/blockdev.h -->
# File Research: sources/virtualization/libblockdev/src/lib/blockdev.h

## Role
Public core header for initializing and querying the libblockdev library.

## API
- Includes `blockdev/utils.h`, GLib, and `plugins.h`.
- Defines the `BD_INIT_ERROR` quark and `BDInitError` values:
  - `BD_INIT_ERROR_FAILED`;
  - `BD_INIT_ERROR_PLUGINS_FAILED`;
  - `BD_INIT_ERROR_NOT_IMPLEMENTED`.
- Declares:
  - `bd_init`;
  - `bd_ensure_init`;
  - `bd_reinit`;
  - `bd_try_init`;
  - `bd_try_reinit`;
  - `bd_is_initialized`.

## Dependencies and Interactions
- Uses `BDPluginSpec` from `plugins.h`.
- Uses `BDUtilsLogFunc` from `blockdev/utils.h`.
- The declarations correspond directly to implementations in `blockdev.c.in`.

## Filesystem/Storage Relevance
This is the public entry point clients must use before invoking plugin APIs for filesystem, block, crypto, RAID, NVMe, or related storage operations.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/lib/blockdev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/lib/blockdev.pc.in -->
# File Research: sources/virtualization/libblockdev/src/lib/blockdev.pc.in

## Role
Pkg-config template for consumers of the core BlockDev library.

## Contents
- Defines substituted `prefix`, `exec_prefix`, `includedir`, and `libdir`.
- Publishes package metadata:
  - `Name: BlockDev`;
  - description for low-level block-device operations;
  - upstream URL;
  - `Version: @VERSION@`.
- Declares `Requires: glib-2.0`.
- Exposes link flags `-L${libdir} -lblockdev`.
- Exposes include flag `-I${includedir}`.

## Dependencies and Interactions
- Installed by `src/lib/Makefile.am`.
- Complements installed headers under `$(includedir)/blockdev`.

## Filesystem/Storage Relevance
This file lets external C projects discover compile and link flags for using libblockdev's storage/plugin initialization API.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/lib/blockdev.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/lib/plugin_apis/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/lib/plugin_apis/Makefile.am

## Role
Automake rules for generating core-library plugin API wrapper C/H files from `.api` specifications.

## Build Logic
- `API_FILES` discovers all `*.api` files in this directory.
- `SOURCE_FILES` and `HEADER_FILES` are derived by replacing `.api` with `.c` and `.h`.
- `all-local` depends on `generate_boilerplate`.
- Pattern rule invokes `scripts/boilerplate_generator.py` with `${PYTHON}` to generate files into the build directory.
- Generated and source API files are included in `dist_noinst_HEADERS`.
- Generated C/H outputs are removed via `CLEANFILES`.

## Dependencies and Interactions
- `blockdev.c.in` includes generated `plugin_apis/*.h` and `plugin_apis/*.c` directly.
- `src/lib/Makefile.am` includes generated headers in introspection scans.

## Filesystem/Storage Relevance
This file creates the dynamic dispatch wrappers that let the central library expose plugin APIs without statically linking plugin implementations.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/lib/plugin_apis/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/lib/plugins.c -->
# File Research: sources/virtualization/libblockdev/src/lib/plugins.c

## Role
Implements `BDPluginSpec` boxed-type helpers for plugin selection and GObject introspection/binding support.

## API Behavior
- `bd_plugin_spec_copy()`:
  - returns NULL for NULL input;
  - allocates a new `BDPluginSpec`;
  - copies the enum value;
  - duplicates `so_name`.
- `bd_plugin_spec_free()`:
  - returns on NULL;
  - frees `so_name` and the struct.
- `bd_plugin_spec_new()`:
  - constructs a new spec from plugin enum and optional soname;
  - duplicates the soname when provided.
- `bd_plugin_spec_get_type()`:
  - lazily registers `BDPluginSpec` as a static boxed GType;
  - uses the copy/free functions above.

## Important Detail
`BDPluginSpec.so_name` is declared `const gchar *` in the public struct, but this implementation duplicates and frees it. The comment notes this mismatch and preserves current allocation behavior.

## Dependencies and Interactions
- Used by public initialization APIs in `blockdev.c.in`.
- GType registration supports language bindings and introspection users that need boxed plugin specs.

## Filesystem/Storage Relevance
This is generic plugin-selection plumbing. It lets callers request specific storage plugins, such as Btrfs or LVM, and optionally force a specific plugin shared-object name.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/lib/plugins.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/lib/plugins.h -->
# File Research: sources/virtualization/libblockdev/src/lib/plugins.h

## Role
Public plugin metadata header.

## API
- Defines `BDPlugin`, the canonical plugin enum. Ordering is significant because `blockdev.c.in` keeps multiple arrays aligned to it.
- Plugin values include LVM, Btrfs, swap, loop, crypto, multipath, device mapper, mdraid, s390, partitioning, filesystem, nvdimm, nvme, smart, and `BD_PLUGIN_UNDEF`.
- Defines boxed type macro `BD_TYPE_PLUGIN_SPEC`.
- Defines `BDPluginSpec` with:
  - `name`, a `BDPlugin`;
  - `so_name`, optional shared-object name override.
- Declares constructors/copy/free helpers and plugin query functions.

## Dependencies and Interactions
- Consumed by `blockdev.h`, `plugins.c`, and `blockdev.c.in`.
- Any enum change must be reflected in the default soname array, plugin state array, and plugin-name array in `blockdev.c.in`.

## Filesystem/Storage Relevance
This header defines the plugin identity surface used to enable storage-specific modules. Btrfs is represented by `BD_PLUGIN_BTRFS`, filesystem operations by `BD_PLUGIN_FS`, and other block/storage subsystems by their own enum values.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/lib/plugins.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/Makefile.am -->
# File Research: sources/virtualization/libblockdev/src/plugins/Makefile.am

## Role
Build rules for top-level libblockdev plugin shared libraries and selected plugin subdirectories.

## Subdirectories
- Starts with `SUBDIRS = .`.
- Adds `fs` when `WITH_FS` is enabled.
- Adds `nvme` when `WITH_NVME` is enabled.
- Always adds `lvm` and `smart` subdirectories.

## Plugin Libraries
Conditionally builds plugin shared libraries:
- `libbd_btrfs.la`;
- `libbd_crypto.la`;
- `libbd_dm.la`;
- `libbd_loop.la`;
- `libbd_mdraid.la`;
- `libbd_mpath.la`;
- `libbd_nvdimm.la`;
- `libbd_swap.la`;
- `libbd_part.la`;
- `libbd_s390.la`.

## Common Build Pattern
Most plugin targets:
- include GLib/GIO and plugin-specific dependency CFLAGS;
- link `../utils/libbd_utils.la`;
- use `-version-info 3:0:0`;
- enforce `--no-undefined`;
- export symbols matching `^bd_.*`;
- include generated headers through `-I${builddir}/../../include/`;
- build with `-Wall -Wextra -Werror`.

## Btrfs Target
When `WITH_BTRFS` is set:
- builds `libbd_btrfs.la`;
- uses GLib, GIO, and libbytesize flags/libs;
- compiles `btrfs.c`, `btrfs.h`, `check_deps.c`, and `check_deps.h`.

## Installed Headers
The file conditionally installs public plugin headers matching enabled plugins. It also installs `fs.h` when `WITH_FS` is enabled, even though FS plugin implementation lives in a subdirectory.

## Notable Detail
The S390 block has two consecutive `libbd_s390_la_CPPFLAGS = ...` assignments; the second assignment overwrites the first rather than appending, so the earlier `-I${srcdir}/../utils/` include path is not retained by this Makefile fragment.

## Filesystem/Storage Relevance
This file determines which storage-operation plugins are actually built and installed. For this group, it is the build rule that turns `btrfs.c` and shared dependency checking into a loadable `libbd_btrfs` plugin.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/btrfs.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/btrfs.c

## Role
Implementation of the libblockdev Btrfs plugin. It provides Btrfs volume, device, subvolume, snapshot, filesystem, label, check/repair, resize, and device-stat APIs.

## Dependencies
- Requires the `btrfs` userspace utility at minimum version `3.18.2`.
- Recursive subvolume deletion requires `btrfs` version `6.12`.
- Requires the kernel `btrfs` module for plugin availability checks.
- Uses libbytesize to parse human-readable size strings from `btrfs filesystem show`.
- Uses Linux Btrfs ioctls for device statistics.

## Data Types and Memory Helpers
- Implements copy/free helpers for:
  - `BDBtrfsDeviceInfo`;
  - `BDBtrfsSubvolumeInfo`;
  - `BDBtrfsFilesystemInfo`;
  - `BDBtrfsDeviceStats`.
- Each copy helper deep-copies owned strings; each free helper releases strings and the struct.
- `bd_btrfs_error_quark()` defines the plugin error domain.

## Dependency Checking
- Static atomic bitmasks cache discovered utility/module availability.
- `bd_btrfs_init()` is a no-op returning TRUE.
- `bd_btrfs_close()` clears cached dependency state.
- `bd_btrfs_is_tech_avail()` checks base Btrfs utility and kernel module dependencies for all technologies, plus the `6.12` dependency for recursive subvolume deletion.

## Command-Based Operations
- `bd_btrfs_create_volume()` validates a non-empty device list, verifies each path exists, builds `mkfs.btrfs` arguments, and supports optional label, data RAID level, metadata RAID level, and extra arguments.
- `bd_btrfs_mkfs()` is an alias around `bd_btrfs_create_volume()`.
- `bd_btrfs_add_device()` runs `btrfs device add`.
- `bd_btrfs_remove_device()` runs `btrfs device delete`.
- `bd_btrfs_create_subvolume()` builds `mountpoint/name` and runs `btrfs subvol create`.
- `bd_btrfs_delete_subvolume()` delegates to `bd_btrfs_delete_subvolume_recursive()` with `recursive=FALSE`.
- `bd_btrfs_delete_subvolume_recursive()` optionally adds `--recursive`, requiring btrfs-progs 6.12 when recursive.
- `bd_btrfs_set_default_subvolume()` runs `btrfs subvol set-default <id> <mountpoint>`.
- `bd_btrfs_create_snapshot()` runs `btrfs subvol snapshot`, with `-r` for read-only snapshots.
- `bd_btrfs_resize()` runs `btrfs filesystem resize <size> <mountpoint>`.
- `bd_btrfs_check()` runs `btrfs check`.
- `bd_btrfs_repair()` runs `btrfs check --repair`.
- `bd_btrfs_change_label()` runs `btrfs filesystem label`.

## Query and Parsing Operations
- `bd_btrfs_get_default_subvolume_id()` runs `btrfs subvol get-default` and parses `ID <number>`.
- `bd_btrfs_list_devices()` runs `btrfs filesystem show`, scans lines with a regex for device id, size, used bytes, and path, and returns a NULL-terminated array.
- `bd_btrfs_list_subvolumes()` runs `btrfs subvol list -a -p`, optionally with `-s`, parses ID/parent/path output, and sorts returned subvolumes so parents/siblings precede children where possible.
- `bd_btrfs_filesystem_info()` runs `btrfs filesystem show` and parses label, UUID, number of devices, and used bytes.
- Empty output from subvolume listing is treated as a valid empty subvolume array when the utility reports no stdout.

## Ioctl-Based Device Stats
- `bd_btrfs_device_stats()` only checks the kernel module dependency, then opens the mountpoint read-only.
- Uses `BTRFS_IOC_FS_INFO` to learn device count and max id.
- Iterates device IDs, ignoring `ENODEV`, then uses `BTRFS_IOC_DEV_INFO` and `BTRFS_IOC_GET_DEV_STATS`.
- Returns per-device path and write/read/flush/corruption/generation error counters.
- Fails if no devices are found.

## Error Behavior
- Missing devices for volume creation produce `BD_BTRFS_ERROR_DEVICE`.
- Parse failures for queried command output produce `BD_BTRFS_ERROR_PARSE`.
- Utility execution errors are propagated through libblockdev utility helpers.
- Size parsing warnings are logged but do not necessarily fail the whole parsed record.

## Filesystem/Storage Relevance
This is the group’s main filesystem implementation file. It is not an in-kernel Btrfs implementation; it is a privileged userspace wrapper around btrfs-progs plus a small ioctl path for stats, exposing Btrfs administration through libblockdev's plugin API.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/btrfs.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/btrfs.h

## Role
Public header for the Btrfs libblockdev plugin.

## Constants and Errors
- Defines `BD_BTRFS_MAIN_VOLUME_ID` as `5`.
- Defines `BD_BTRFS_MIN_MEMBER_SIZE` as `128 MiB`.
- Declares `BD_BTRFS_ERROR` and `BDBtrfsError` values:
  - technology unavailable;
  - device error;
  - parse error.

## Data Structures
- `BDBtrfsDeviceInfo`: device id, path, size, used bytes.
- `BDBtrfsSubvolumeInfo`: subvolume id, parent id, path.
- `BDBtrfsDeviceStats`: device id, path, and Btrfs error counters.
- `BDBtrfsFilesystemInfo`: label, UUID, number of devices, used bytes.
- Declares copy/free helpers for each struct.

## Technology Model
- `BDBtrfsTech` categories:
  - filesystem;
  - multi-device;
  - subvolume;
  - snapshot.
- `BDBtrfsTechMode` bit flags:
  - create;
  - delete;
  - modify;
  - query;
  - delete recursive.

## Public Operations
Declares plugin lifecycle and availability calls plus Btrfs operations for:
- volume creation and mkfs;
- adding/removing devices;
- subvolume create/delete/delete-recursive/list/default-id/default-set;
- snapshot creation;
- filesystem info, resize, check, repair, label change;
- device stats.

## Dependencies and Interactions
- Includes GLib, GObject, and `blockdev/utils.h` for types and `BDExtraArg`.
- Implemented by `btrfs.c`.
- Built and installed conditionally by `src/plugins/Makefile.am`.

## Filesystem/Storage Relevance
This header defines libblockdev's public Btrfs administration surface for consumers and bindings.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/btrfs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/check_deps.c -->
# File Research: sources/virtualization/libblockdev/src/plugins/check_deps.c

## Role
Shared dependency checker used by multiple libblockdev plugins. It caches runtime availability of command-line utilities, kernel modules, D-Bus services/API versions, and utility feature support.

## Utility Version Dependencies
- `check_deps()` accepts an atomic availability bitmask, requested dependency bits, an array of `UtilDep`, dependency count, a lock, and error output.
- It returns immediately if all requested bits are already cached.
- Otherwise it serializes checks with `deps_check_lock`, rechecks the cache, then calls `bd_utils_check_util_version()`.
- Successful checks set the matching bit with `g_atomic_int_or()`.
- Failures are accumulated into `GError`, prefixing existing errors when multiple checks fail.

## Kernel Module Dependencies
- `check_module_deps()` follows the same cache/lock pattern.
- Calls `bd_utils_have_kernel_module()` per requested module.
- Distinguishes helper errors from simple unavailable modules, producing `BD_UTILS_MODULE_ERROR_MODULE_CHECK_ERROR`.

## D-Bus Dependencies
- `_check_dbus_api_version()` connects to the specified bus, calls `org.freedesktop.DBus.Properties.Get`, extracts a version string, and compares it with `bd_utils_version_cmp()`.
- `check_dbus_deps()` first checks service availability via `bd_utils_dbus_service_available()`.
- If a version is configured, it also verifies the D-Bus API version before caching the dependency bit.
- Errors cover missing service, service-check failures, and insufficient API version.

## Utility Feature Dependencies
- `_check_util_feature()` locates the utility in `PATH`, runs it with a feature argument, and captures output.
- If the command returns no stdout or nonzero exit status, it can still inspect the error message text as output.
- Optional regex extraction can narrow output to a feature list.
- Checks feature availability with substring search.
- `check_features()` wraps this in the same atomic cache and lock pattern used by other dependency checks.

## Concurrency and Caching
- All public check functions are designed for repeated plugin calls.
- Atomic bitmasks avoid repeated external process/module/D-Bus checks once a dependency has been confirmed.
- Mutexes prevent concurrent duplicate checks when dependencies are not yet cached.

## Filesystem/Storage Relevance
Filesystem and block plugins use this file to gate operations on real runtime capabilities. For Btrfs specifically, `btrfs.c` uses it to require btrfs-progs versions and the Btrfs kernel module before running mutating or query operations.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/check_deps.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/check_deps.h -->
# File Research: sources/virtualization/libblockdev/src/plugins/check_deps.h

## Role
Internal shared header for plugin runtime dependency checks.

## Data Structures
- `UtilDep`: utility name, required version, optional version argument, and version regex.
- `DBusDep`: bus name, object prefix, bus type, required version, and property/interface/path fields for version probing.
- `UtilFeatureDep`: utility name, required feature, feature argument, and optional feature regex.

## API
Declares four checker functions:
- `check_deps()` for utility/version dependencies;
- `check_module_deps()` for kernel modules;
- `check_dbus_deps()` for D-Bus service and API dependencies;
- `check_features()` for utility feature discovery.

Each function accepts an atomic availability bitmask, requested dependency bits, dependency specs, dependency count, a mutex, and optional `GError`.

## Dependencies and Interactions
- Used by `btrfs.c` and other plugin implementations listed in `src/plugins/Makefile.am`.
- Implemented by `check_deps.c`.
- Depends on GLib types and libblockdev utility helpers indirectly through the C implementation.

## Filesystem/Storage Relevance
This header defines the reusable runtime-gating interface that keeps plugin operations from running when required tools, modules, services, or features are unavailable.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/plugins/check_deps.h -->