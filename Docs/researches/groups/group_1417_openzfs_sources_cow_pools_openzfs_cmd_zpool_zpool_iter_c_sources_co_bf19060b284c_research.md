# Group Research: group_1417_openzfs_sources_cow_pools_openzfs_cmd_zpool_zpool_iter_c_sources_co_bf19060b284c

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/openzfs` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_iter.c -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_iter.c

This file implements command-side iteration helpers for pools and vdevs, plus the `zpool status/iostat -c` script execution framework.

Primary responsibilities:
- Maintains `zpool_list_t`, an AVL-backed ordered set of `zpool_handle_t` objects keyed by pool name.
- Provides high-level pool traversal via `for_each_pool()`.
- Provides vdev traversal via `for_each_vdev()`.
- Gathers per-vdev script output for `zpool status -c` / `zpool iostat -c`.

Important structures:
- `zpool_node_t`: wraps a pool handle, AVL node, and last-refresh timestamp.
- `zpool_list`: stores whether the list tracks all pools, whether property values are literal, an AVL tree, property-list expansion state, type, and refresh timestamp.
- `vdev_cmd_data_t` and `vdev_cmd_data_list_t` are declared in `zpool_util.h` and populated here.

Pool-list behavior:
- `pool_list_get()` creates the AVL tree and either:
  - iterates all pools with `zpool_iter()` when no CLI pool args are supplied, or
  - opens each named pool with `zpool_open_canfail()`.
- `add_pool()` inserts a pool into the AVL tree, expands properties with `zpool_expand_proplist()` when requested, and refreshes an existing node from a duplicate handle via `zpool_refresh_stats_from_handle()`.
- `pool_list_refresh()` supports two modes:
  - fixed explicit pool list: refreshes stats for existing handles only;
  - dynamic all-pools list: reruns `zpool_iter()`, adds new pools, refreshes old unavailable pools, and removes missing pools.
- `pool_list_iter()` skips unavailable pools unless the caller requests `unavail`.
- `for_each_pool()` is the simple wrapper used by most zpool subcommands.

Vdev iteration:
- `for_each_vdev()` fetches the pool config, looks up `ZPOOL_CONFIG_VDEV_TREE`, then delegates traversal to `for_each_vdev_cb()`.
- It intentionally ignores root vdevs and holes through the lower-level traversal helper.

Script execution path:
- `zpool_get_cmd_search_path()` uses `ZPOOL_SCRIPTS_PATH` if set, otherwise `$HOME/.zpool.d:<SYSCONFDIR>/zfs/zpool.d`, falling back to the system directory.
- `all_pools_for_each_vdev_run()` gathers vdevs across selected pools, runs requested comma-separated commands in parallel with a taskq, then builds a unique column list for display.
- `for_each_vdev_run_cb()` skips duplicate spare paths within the same pool, supports selected-vdev filtering by rendered vdev name, captures path, underlying path, pool name, command pointer, and enclosure sysfs path.
- `vdev_run_cmd_thread()` ignores command names containing `/`, searches executable scripts in the allowed search path, and runs the first match.
- `vdev_run_cmd()` constructs the script environment with `zpool_vdev_script_alloc_env()` and invokes `libzfs_run_process_get_stdout_nopath()`.
- `vdev_process_cmd_output()` accepts either `column=value` lines or a single unlabelled value. Duplicate column names are ignored. A line without a column terminates processing after adding the value.
- `process_unique_cmd_columns()` derives all unique script output columns and their display widths across all vdevs.
- `free_vdev_cmd_data_list()` frees all gathered strings, arrays, and per-vdev state.

Notable implementation details:
- AVL ordering uses `TREE_ISIGN(strcmp(pool-name))`.
- `add_pool_cb()` always returns 0 so `zpool_iter()` continues even on duplicate pools or property expansion failure.
- Dynamic refresh uses `zn_last_refresh` timestamps to distinguish newly refreshed handles from stale entries.
- Script dispatch parallelism scales to `5 * sysconf(_SC_NPROCESSORS_ONLN)`.
- Memory ownership is explicit: pool handles are closed by `pool_list_free()`, while script output strings are freed by `free_vdev_cmd_data_list()`.

Dependencies:
- `libzfs` for pool handles, configs, stats, and process execution helpers.
- `libzutil` / ZFS utility helpers for vdev script environment and path resolution.
- SPL-style AVL and taskq APIs.
- `zpool_util.h` for shared declarations.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_iter.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_util.c -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_util.c

This is a small shared utility implementation for the `zpool` command.

Functions:
- `safe_malloc(size_t)`: calloc-backed allocator that exits with an internal out-of-memory message on failure.
- `safe_realloc(void *, size_t)`: realloc wrapper that exits on allocation failure.
- `zpool_no_memory()`: asserts `errno == ENOMEM`, prints a localized out-of-memory message, and exits.
- `num_logs(nvlist_t *)`: counts child vdevs whose `ZPOOL_CONFIG_IS_LOG` flag is set.
- `array64_max(uint64_t array[], unsigned int len)`: returns the maximum value in a `uint64_t` array, defaulting to 0 for an empty scan.

Behavioral notes:
- Allocation helpers terminate the process rather than propagating allocation errors, matching CLI utility style.
- `num_logs()` returns 0 when the supplied nvlist has no `ZPOOL_CONFIG_CHILDREN` array.
- `num_logs()` only counts immediate children of the supplied nvlist, not nested descendants.

Dependencies:
- `zpool_util.h` for declarations and ZFS/nvlist types.
- `gettext()` for localized error messages.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_util.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_util.h -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_util.h

This header is the shared interface for zpool command helper modules.

Main declarations:
- Memory/error helpers: `safe_malloc()`, `safe_realloc()`, `zpool_no_memory()`.
- Small utility helpers: `num_logs()`, `array64_max()`, `zpool_get_cmd_search_path()`.
- Vdev construction helpers:
  - `make_root_vdev()`
  - `split_mirror_vdev()`
- Pool iteration helpers:
  - `for_each_pool()`
  - opaque `zpool_list_t`
  - `pool_list_get()`, `pool_list_refresh()`, `pool_list_iter()`, `pool_list_free()`, `pool_list_count()`
- Vdev iteration:
  - `for_each_vdev()`
- Script execution result containers:
  - `vdev_cmd_data_t`
  - `vdev_cmd_data_list_t`
  - `all_pools_for_each_vdev_run()`
  - `free_vdev_cmd_data_list()`
- Device/file validation and platform helpers:
  - `check_device()`
  - `check_sector_size_database()`
  - `vdev_error()`
  - `check_file()`
  - `check_file_generic()`
  - `after_zpool_upgrade()`
- Power helpers:
  - `zpool_power()`
  - `zpool_power_current_state()`

Important constants:
- `ZPOOL_SCRIPTS_DIR` is `SYSCONFDIR"/zfs/zpool.d"`, the system script directory for `zpool status/iostat -c`.

Important data contracts:
- `vdev_cmd_data_t` stores script result lines and optional column names for one vdev, plus vdev path, underlying path, pool name, command backpointer, and enclosure sysfs path.
- `vdev_cmd_data_list_t` stores all per-vdev command data, optional selected-vdev filter state, unique column metadata, and display widths.

External state:
- Declares global `libzfs_handle_t *g_zfs`, used throughout zpool command modules.

Dependencies:
- `libnvpair.h`, `libzfs.h`, and `libzutil.h`.
- The header is C++ guarded.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_util.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_vdev.c -->
# File Research: sources/cow-pools/openzfs/cmd/zpool/zpool_vdev.c

This file converts zpool CLI vdev arguments into validated nvlist vdev trees. It performs userland validation before handing configurations to libzfs/kernel code.

Primary responsibilities:
- Parse device, file, mirror, raidz, dRAID, spare, log, cache, special, and dedup vdev specifications.
- Validate that devices exist and are usable.
- Detect devices already in use.
- Validate replication consistency.
- Prepare, partition, label, and update whole-disk vdev nvlists.
- Build root vdev nvlists for create/add/replace flows.
- Build split-mirror vdev specifications.

Global state:
- `error_seen`: tracks whether `vdev_error()` has already printed the invalid-spec header.
- `is_force`: controls whether error text says `-f` may override issues or manual repair is required.

Error reporting:
- `vdev_error()` prints a single grouped header followed by formatted validation errors.

Leaf vdev construction:
- `make_leaf_vdev()` accepts:
  - full paths;
  - shorthand device names resolved with `zfs_resolve_shortname()`;
  - dRAID spare names;
  - regular files.
- It distinguishes disk vs file using whole-disk detection and `stat64`.
- It stores `ZPOOL_CONFIG_PATH`, `ZPOOL_CONFIG_TYPE`, optional `ZPOOL_CONFIG_WHOLE_DISK`, enclosure sysfs path, and optional `ZPOOL_CONFIG_ASHIFT`.
- If ashift was not explicitly provided, it checks a sector-size database and converts sector size to ashift.

Device-use checks:
- `check_file_generic()` opens a file and asks `zpool_in_use()` whether it belongs to an active/exported/potentially-active/spare pool.
- Active pools and spare reservations are hard errors; exported/potentially active pools may be force-overridden depending on state.
- `is_spare()` identifies dRAID spares and labeled hot spares, optionally checking a supplied pool config’s spare GUID list.
- `is_device_in_use()` recursively walks children, spares, and L2ARC devices and dispatches to `check_device()` or `check_file()`.

Replication validation:
- `replication_level_t` captures vdev type, child count, and parity.
- `get_replication()` walks top-level non-log, non-hole, non-indirect vdevs and detects:
  - mixed files and disks inside a group;
  - child size mismatches beyond `ZPOOL_FUZZ` of 16 MiB;
  - inconsistent vdev types;
  - inconsistent parity;
  - inconsistent mirror/raidz width.
- dRAID is treated as raidz-like for redundancy comparisons.
- raidz and mirror combinations are accepted only when their tolerated disk failures match.
- `check_replication()` compares new specs against existing pool replication when adding to a pool and allows all-log/spare-only specs to bypass replication checks.

Disk preparation:
- `make_disks()` recursively finds disk leaves.
- For non-whole disks it updates multipath device strings if needed and zeros the first 4 KiB unless the path is a spare.
- For whole disks it:
  - resolves the raw device path;
  - derives the partition path with `zfs_append_partition()`;
  - handles udev symlink removal for `/dev/disk` paths;
  - calls `zpool_prepare_and_label_disk()`;
  - waits for the partition path with `zpool_label_disk_wait()`;
  - zeros the partition label area;
  - updates `ZPOOL_CONFIG_PATH` to the partition path;
  - updates device id strings.
- Disk labeling is skipped during dry runs.

Grouping and dRAID parsing:
- `get_parity()` parses raidz/dRAID parity suffixes and enforces maximum parity.
- `is_grouping()` recognizes `raidz*`, `draid*`, `mirror`, `spare`, `log`, `special`, `dedup`, and `cache`, returning min/max child counts and canonical type.
- `draid_config_by_type()` parses `draid[parity][:<data>d][:<children>c][:<spares>s][:<width>w]`.
- dRAID validation handles failure groups/domains, data/parity/spare layout, width consistency, maximum children, and group-count calculation before storing:
  - `ZPOOL_CONFIG_NPARITY`
  - `ZPOOL_CONFIG_DRAID_NDATA`
  - `ZPOOL_CONFIG_DRAID_NSPARES`
  - `ZPOOL_CONFIG_DRAID_NGROUPS`
  - `ZPOOL_CONFIG_DRAID_NCHILDREN`

Spec construction:
- `construct_spec()` parses the CLI argv stream.
- It validates `ashift` from pool properties.
- It tracks context flags for log, special, dedup, and spare sections.
- It enforces single `spare`, `log`, and `cache` sections.
- Log grouped vdevs only support mirrors.
- It supports dRAID `fgroup` / `failure_group` and `fdomain` / `failure_domain` markers and validates consistent group/domain sizes.
- Failure domains are reordered before nvlist insertion so children are laid out appropriately.
- It builds a root nvlist with `VDEV_TYPE_ROOT`, top-level children, optional `ZPOOL_CONFIG_SPARES`, and optional `ZPOOL_CONFIG_L2CACHE`.
- It rejects an empty spec with no top-level, spare, or cache device.

Exported functions:
- `split_mirror_vdev()` optionally constructs a target device spec, labels disks unless dry-run, rejects grouping keywords as split target devices, then calls `zpool_vdev_split()`.
- `make_root_vdev()` is the main exported builder. It:
  - constructs the spec;
  - obtains current pool config when adding/replacing;
  - checks for in-use devices;
  - optionally checks replication;
  - ensures new pools contain at least one normal top-level vdev;
  - labels disks unless dry-run;
  - returns the final root nvlist.

Notable constraints:
- The parser deliberately performs many userland checks before kernel submission.
- Error paths often skip cleanup because the command will fail immediately, but successful paths free temporary child nvlists after copying them into parent arrays.
- Auxiliary vdevs such as logs, special, dedup, cache, and spares are treated differently from normal data vdevs during validation.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/cmd/zpool/zpool_vdev.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/Makefile.am -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/Makefile.am

This Automake fragment defines the `libzfs.la` build.

Build flags:
- `libzfs_la_CFLAGS` includes common AM/library flags, libcrypto flags, zlib flags, and `-fvisibility=hidden`.

Library registration:
- Adds `libzfs.la` to `lib_LTLIBRARIES`.
- Adds `libzfs.la` to `CPPCHECKTARGETS`.

Distributed libzfs sources include:
- `libzfs_impl.h`
- `libzfs_share.h`
- `libzfs_changelist.c`
- `libzfs_config.c`
- `libzfs_crypto.c`
- dataset, diff, import, iter, mount, pool, share, send/recv, status, and utility implementation files.

Platform-specific sources:
- FreeBSD builds add compatibility, NFS/SMB share, and zmount files under `os/freebsd`.
- Linux builds add mount, pool, NFS/SMB share, and utility files under `os/linux`.

Nondistributed compiled-in common sources:
- zcommon modules such as cityhash, features, delegation, fletcher variants, namecheck, props, value strings, and zpool props.
- Special handling includes `module/zfs/btree.c` and `module/zfs/range_tree.c` as sources rather than `LIBADD` dependencies so their symbols are not exported as libzfs API.

Link dependencies:
- `libzfs_core.la`
- `libnvpair.la`
- `libzutil.la`
- system/libs: `-lrt`, `-lm`, libcrypto, zlib, libfetch, gettext.
- FreeBSD adds `-lutil -lgeom`.

LDFLAGS:
- Version info is `7:0:0`.
- Adds `-Wl,-z,defs` when ASAN is not enabled.

Install/data outputs:
- Installs `libzfs.pc` as pkg-config data.
- Distributes ABI and suppression files plus OpenSSL third-party license metadata.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs.pc.in -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs.pc.in

This is the pkg-config template for libzfs.

Fields:
- `Name: libzfs`
- `Description: LibZFS library`
- `Version: @VERSION@`
- `URL: https://github.com/openzfs/zfs`

Dependencies and flags:
- Public requirement: `libzfs_core`.
- Private requirements: configured libcrypto and zlib pkg-config dependencies.
- Cflags expose `${includedir}/libzfs` and `${includedir}/libspl`.
- Public libs: `-L${libdir} -lzfs -lnvpair`.
- Private libs: `-luutil -lm -pthread`.

Use:
- Downstream consumers use this template after configure substitution to compile and link against installed libzfs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_changelist.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_changelist.c

This file implements libzfs changelists: ordered sets of datasets that need pre/post handling when properties such as `mountpoint`, `sharenfs`, `sharesmb`, `name`, `zoned`, `canmount`, or `volsize` change.

Primary purpose:
- Before a property change, gather affected datasets and remember whether they were mounted/shared/zoned.
- Prefix phase unmounts or unshares as needed.
- Postfix phase remounts and reshares according to new properties and previous state.

Important structures:
- `prop_changenode_t`: stores a dataset handle, prior shared/mounted/zoned state, whether postfix work is needed, and AVL node.
- `prop_changelist`: stores real and effective properties, companion share property, AVL tree, mount/gather flags, and whether any child is zoned.

Main workflow:
1. `changelist_gather()`
2. `changelist_prefix()`
3. caller changes property
4. `changelist_postfix()`
5. `changelist_free()`

Prefix behavior:
- `changelist_prefix()` acts only for `mountpoint` and `sharesmb`.
- It returns immediately if `CL_GATHER_DONT_UNMOUNT` is set.
- For mountpoint changes it unmounts affected filesystems.
- For SMB share changes it unshares SMB resources and commits SMB share updates.
- If an unmount fails, remaining nodes are marked as not needing postfix and already-processed nodes are restored through `changelist_postfix()`.
- Zoned children are skipped from the global zone.

Postfix behavior:
- `changelist_postfix()` returns immediately for `CL_GATHER_DONT_UNMOUNT`.
- For mountpoint changes it removes the old mountpoint for the last node.
- It walks the AVL in reverse order so parents are mounted before children.
- It refreshes properties, skips volumes, checks `sharenfs`, `sharesmb`, key availability, mounted state, and `canmount`.
- It remounts datasets that were mounted before, were legacy/none mountpoints, or need sharing and can be mounted.
- It shares or unshares NFS and SMB according to current properties and previous shared state.
- It commits share changes once after walking the list.
- It only propagates share option syntax errors; service-not-running style share failures are tolerated.

Gather behavior:
- `changelist_gather()` chooses AVL ordering:
  - by dataset name when the existing mountpoint is `legacy` or `none`;
  - by mountpoint otherwise, to handle mount hierarchies that differ from dataset hierarchy.
- Property mapping:
  - rename (`ZFS_PROP_NAME`) is treated as a mountpoint-affecting operation and gathers all dependents;
  - `ZFS_PROP_ZONED` gathers all children;
  - `ZFS_PROP_CANMOUNT` and `ZFS_PROP_VOLSIZE` are treated as mountpoint related.
- For `sharenfs`, it also watches `sharesmb`; for `sharesmb`, it also watches `sharenfs`.
- It can gather mounted descendants from mnttab with `CL_GATHER_ITER_MOUNTED`.
- It always reopens and adds the target dataset itself after child/dependent gathering.
- It records legacy/none mountpoint state to guide postfix remount behavior.

Other operations:
- `changelist_rename()` updates stored dataset names after a rename and removes previous mountpoints.
- `changelist_unshare()` unshares all nodes for the requested protocol list and commits each protocol.
- `changelist_haszonedchild()` exposes whether gather found any zoned child.
- `changelist_remove()` removes and closes one named dataset from a gathered list.
- `changelist_free()` closes all dataset handles and destroys the AVL tree.

Notable helper logic:
- `isa_child_of()` treats `dataset`, `dataset/...`, and `dataset@...` as descendants.
- `change_one()` adds datasets that inherit the watched property, are included by all-children/all-dependents modes, or inherit companion share properties.
- For mountpoint changes, child iteration includes snapshots/clones only where the gather mode requires it.

Dependencies:
- libzfs dataset iteration, mount, unmount, share, unshare, property, and handle APIs.
- AVL ordering from `sys/avl.h`.
- Zone awareness via `getzoneid()` and `GLOBAL_ZONEID`.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_changelist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_config.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_config.c

This file manages libzfs’s in-memory view of pool configuration namespace and exposes pool/root iteration helpers.

Primary concept:
- Pool configuration is stored kernel-side and mirrored from `/etc/zfs/zpool.cache`.
- Userland obtains it through `ZFS_IOC_POOL_CONFIGS`, which also works from local zones.

Important structure:
- `config_node_t`: AVL node containing pool name and duplicated pool config nvlist.

Namespace lifecycle:
- `namespace_reload()` initializes the namespace AVL on first use.
- It sends `ZFS_IOC_POOL_CONFIGS` with the handle’s generation counter.
- `EEXIST` means the namespace generation has not changed.
- `ENOMEM` expands the destination nvlist buffer and retries.
- On success, it updates `libzfs_ns_gen`, clears existing config nodes, reads the returned packed nvlist, duplicates each pool config, and inserts it into the AVL.
- `namespace_clear()` frees all configs, names, nodes, and destroys the AVL.

Pool config/stat helpers:
- `zpool_get_config()` returns the current config and optionally the old config pointer.
- `zpool_get_features()` ensures feature stats are present, refreshing pool stats if needed, then returns `ZPOOL_CONFIG_FEATURE_STATS`.
- `zpool_refresh_stats()` sends `ZFS_IOC_POOL_STATS`, expanding the buffer on `ENOMEM`. It updates:
  - old config pointer;
  - current config;
  - config buffer size;
  - pool state active/unavailable.
- Missing/destroyed pools are detected through `ENOENT` or `EINVAL` and reported via the `missing` output flag.
- `zpool_refresh_stats_from_handle()` copies config/state from a source pool handle to a destination handle for the same pool, avoiding a duplicate kernel round trip.

Pool filtering:
- `zpool_skip_pool()` reads undocumented test-only environment variables once:
  - `__ZFS_POOL_EXCLUDE`: space-separated pools to skip.
  - `__ZFS_POOL_RESTRICT`: space-separated allowlist.
- Exclude wins first; restrict skips all non-listed pools.

Iteration:
- `zpool_iter()` reloads namespace unless already inside a pool iteration. This avoids invalidating parent iterator state during recursive calls.
- It opens each pool silently and passes the handle to the callback.
- Callback ownership follows zpool iterator convention: callbacks receive handles and are expected to close or transfer as appropriate based on callee behavior.
- `zfs_iter_root()` reloads namespace and creates root dataset handles for each pool, passing each to the callback, which must close the handle.

Dependencies:
- ioctl helpers from libzfs internals (`zcmd_alloc_dst_nvlist`, `zcmd_expand_dst_nvlist`, `zcmd_read_dst_nvlist`).
- AVL tree for sorted pool namespace.
- nvlist duplication/free APIs.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_config.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_crypto.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_crypto.c

This file implements userland ZFS encryption support in libzfs: key material acquisition, validation, wrapping-key derivation, encryption-root creation checks, key load/unload, and key rewrap/change-key behavior.

Key model:
- User-provided keys decrypt dataset master encryption keys.
- Raw and hex keys map directly to the fixed wrapping-key length.
- Passphrases are converted to wrapping keys with PBKDF2-HMAC-SHA1 using dataset salt and iteration count.
- Salt is stored as a hidden property; PBKDF2 iteration count is stored as a property.

Constants:
- Minimum passphrase length: 8.
- Maximum passphrase length: 512.
- Interactive prompt attempts: 3.
- Wrapping key length comes from `WRAPPING_KEY_LEN`.

Keylocation parsing:
- `zfs_prop_parse_keylocation()` accepts:
  - `prompt`;
  - URI strings matching the libzfs URI regex.
- Supported URI schemes are registered in `uri_handlers`:
  - `file`
  - `https`
  - `http`

Key material input:
- `libzfs_getpassphrase()` prompts on stdin, disables terminal echo, catches SIGINT, ignores SIGTSTP while reading, restores terminal state, and rethrows interrupts.
- `get_key_interactive()` rejects raw key entry from a terminal, optionally confirms newly entered keys, and validates passphrase/hex format before confirmation.
- `get_key_material_raw()` reads non-raw keys with `getline()` and trims newline. For raw keys, it reads 33 bytes to detect keys longer than the required 32 bytes.
- `get_key_material_file()` reads from `file://` paths.
- `get_key_material_https()` fetches HTTP/HTTPS key material using either libfetch or libcurl, depending on build configuration. It can dynamically load libfetch/curl symbols. The curl path writes into an unnamed or unlinked temp file, follows redirects, applies a 30 second timeout, honors SSL env vars, and requires a 2xx response.
- `get_key_material()` dispatches prompt or URI fetching, validates the result, and reports whether interactive retry is possible.

Validation and derivation:
- `validate_key()` enforces exact raw/hex length, hex digits, and passphrase length on new-key verification.
- `hex_key_to_raw()` decodes a hex string into raw wrapping bytes.
- `derive_key()`:
  - copies raw keys;
  - decodes hex keys;
  - derives passphrase keys with `PKCS5_PBKDF2_HMAC_SHA1()`, little-endian salt, configured iterations, and `WRAPPING_KEY_LEN`.

Feature checks:
- `encryption_feature_is_enabled()` requires feature flags support and presence of the encryption feature in pool feature stats.
- `proplist_has_encryption_props()` detects encryption-related properties in a create property list.

Create-time encryption:
- `zfs_crypto_create()` validates encryption properties during dataset or pool-root creation.
- It handles parent dataset inheritance when a parent exists.
- For root dataset creation, it checks `feature@encryption` in pool properties because the feature may not be on disk yet.
- If encryption is off, any encryption-specific properties are rejected.
- If creating a new encryption root, `keyformat` is required.
- If `keyformat` is supplied without `keylocation`, keylocation defaults to `prompt`.
- It rejects `keylocation=prompt` when stdin is unavailable, such as receive streams using stdin.
- `populate_create_encryption_params_nvlists()` fetches key material, generates salt for passphrases, sets default PBKDF2 iterations if absent, rejects `pbkdf2iters` for non-passphrase keys, derives the wrapping key, and returns wrapping key bytes to the caller.
- `zfs_crypto_clone_check()` rejects encryption properties for clones because they must inherit from the origin dataset.

Encryption-root detection:
- `zfs_crypto_get_encryption_root()` returns false for unencrypted datasets, otherwise compares `ZFS_PROP_ENCRYPTION_ROOT` to the dataset name and optionally copies the encryption root name.

Loading keys:
- `zfs_crypto_load_key()` requires the encryption feature, encrypted dataset, and encryption-root target.
- It optionally accepts an alternate keylocation.
- It rejects loading an already loaded key unless `noop` is requested.
- For passphrases it reads existing salt and iterations from properties.
- It fetches and derives key material, then calls `lzc_load_key()`.
- Error mapping covers permission, invalid parameters, already loaded keys, busy datasets, incorrect keys, and unsupported suites.
- Interactive incorrect-key and other correctable failures can retry up to three attempts.
- `zfs_crypto_attempt_load_keys()` recursively attempts to load keys for all encryption roots below a filesystem/volume and prints success count. It is best effort, but returns failure if any attempted key load failed.

Unloading keys:
- `zfs_crypto_unload_key()` requires encryption feature, encrypted dataset, and encryption-root target.
- It rejects already unloaded keys.
- It calls `lzc_unload_key()` and maps permission, already unloaded, and busy errors.

Changing/rewrapping keys:
- `zfs_crypto_verify_rewrap_nvlist()` permits only `keyformat`, `keylocation`, `pbkdf2iters`, and user properties for normal change-key. With inherit-key mode, only user properties may be set.
- `zfs_crypto_rewrap()` implements both new-key and inherit-key paths:
  - requires encryption feature and encrypted dataset;
  - rejects clones because clone keys come from their origin;
  - validates raw properties through `zfs_valid_proplist()`;
  - for non-inherit mode, fills missing keyformat/keylocation from existing encryption-root props or requires them when promoting a non-root to a new encryption root;
  - fetches/derives new wrapping key data;
  - for inherit mode, requires current dataset to be an encryption root, requires encrypted parent, and requires parent key to be loaded;
  - requires current key to be loaded;
  - calls `lzc_change_key()` with `DCP_CMD_NEW_KEY` or `DCP_CMD_INHERIT`.
- It maps permission, invalid property, and unloaded-key errors to crypto failure reporting.

Other helper:
- `zfs_is_encrypted()` uses dmu stats flags when available, otherwise falls back to the encryption property.

Notable security and operational details:
- Raw keys are never accepted interactively.
- Terminal echo is restored even on read failure or signal.
- Key buffers are freed on all visible error paths, though not explicitly zeroed in this file.
- URI key retrieval supports both compile-time and dynamic-fetch backends.
- Create and rewrap paths tightly couple key material generation with property nvlist updates so kernel ioctls receive consistent wrapping-key metadata.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_crypto.c -->