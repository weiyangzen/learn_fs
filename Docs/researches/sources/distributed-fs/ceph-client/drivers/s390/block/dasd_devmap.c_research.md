# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_devmap.c

## Purpose

`dasd_devmap.c` owns DASD device mapping and much of the user-visible device configuration surface. It parses `dasd=` boot/module parameters, maps CCW bus IDs to stable DASD device indexes and feature flags, creates and deletes `struct dasd_device` instances, manages PPRC/copy-pair metadata, exposes sysfs attributes, and creates per-path sysfs kobjects.

## Important APIs, Types, and Functions

- `struct dasd_devmap` stores the bus ID, stable device index, feature bitmask, current `struct dasd_device *`, copy relation pointer, and autoquiesce mask.
- Global state includes `dasd_page_cache`, `dasd_probeonly`, `dasd_autodetect`, `dasd_nopav`, `dasd_nofcx`, `dasd_hashlists[256]`, `dasd_max_devindex`, and the `dasd_devmap_lock`.
- Parameter parsing is implemented by `dasd_call_setup()`, `dasd_busid()`, `dasd_feature_list()`, `dasd_parse_keyword()`, `dasd_evaluate_range_param()`, `dasd_parse_range()`, and `dasd_parse()`.
- Mapping/lifetime APIs include `dasd_add_busid()`, `dasd_busid_known()`, `dasd_device_from_devindex()`, `dasd_create_device()`, `dasd_delete_device()`, `dasd_device_from_cdev_locked()`, `dasd_device_from_cdev()`, `dasd_add_link_to_gendisk()`, and `dasd_device_from_gendisk()`.
- Copy relation support is implemented by `dasd_devmap_set_device_copy_relation()`, `dasd_devmap_get_pprc_status()`, `dasd_devmap_check_copy_relation()`, `dasd_copy_pair_show/store()`, and `dasd_copy_role_show()`.
- `dasd_dev_groups` exports the sysfs attribute groups for the ccw device, including base attributes, `capacity`, and `extent_pool`.
- `dasd_get_feature()` and `dasd_set_feature()` read/update devmap feature bits and mirror them into a live device.
- Path sysfs support is provided by `dasd_path_create_kobj()`, `dasd_path_create_kobjects()`, and `dasd_path_remove_kobjects()`.

## Control Flow

Boot/module parsing stores comma-separated `dasd=` tokens, then `dasd_parse()` processes each token as either a keyword or range. Keywords toggle global behavior such as autodetect, probeonly, nopav, nofcx, or fixed DMA page cache creation. Ranges are parsed from old-style devnos, full bus IDs, or `ipldev`; optional feature lists set readonly, diag, raw, erplog, and failfast bits. Each expanded bus ID is inserted with `DASD_FEATURE_INITIAL_ONLINE`.

Device creation starts from a CCW device. `dasd_devmap_from_cdev()` finds or creates a devmap, `dasd_alloc_device()` allocates a DASD device, and `dasd_create_device()` installs the device under `dasd_devmap_lock`, assigns the devindex and features, references the ccw device, stores driver data under the CCW lock, and creates the `paths_info` kset. Deletion removes the devmap pointer first, clears driver data, removes copy relation state, drops three creation references, waits for the refcount to reach zero, releases discipline data, unregisters path ksets, drops the ccw device, and frees the DASD device.

Sysfs attributes either operate on persistent devmap feature state, live device state, or discipline callbacks. Feature-style attributes include `failfast`, `readonly`, `erplog`, `use_diag`, `raw_track_access`, `aq_requeue`, `reservation_policy`, and `path_autodisable`. Live attributes include status, discipline, alias/vendor/uid, EER enablement, timeouts/retries, block timeout, host access count, path masks, path reset, HPF, path thresholds/intervals, FC security, copy role, ping, autoquiesce settings, and extent-pool/capacity callback values. Some toggles, notably `use_diag` and raw track access, are only accepted while the device is offline and mutually exclusive with the other mode.

Copy-pair setup parses `primary,secondary`, ensures the sysfs device is one side of the pair, creates devmaps for both sides, requires the secondary to be offline, links both devmaps to a shared `dasd_copy_relation`, and if the primary is already online validates PPRC state through the discipline. Clearing is allowed only when all secondary devices are offline, then devmaps and live device copy pointers are detached and references dropped.

## State and Persistence Behavior

The file persists desired DASD state for the lifetime of the module in devmap entries: bus ID to devindex, feature flags, autoquiesce masks, and configured copy relation metadata. Live `struct dasd_device` pointers are transient and protected by `dasd_devmap_lock` or CCW locks depending on access path. Sysfs writes update the devmap so settings can outlive a device going offline and also update the live device when present. There is no disk persistence in this file; persistence is kernel-memory lifetime and boot/module parameter replay.

## Dependencies and Integration Points

The code integrates with the CCW bus (`struct ccw_device`, `dev_set_drvdata`, `ccw_device_set_offline`), Linux block layer (`gendisk->private_data`, queue request timeout, readonly disk state), DASD core allocation/refcount/discipline APIs, DASD EER, path helpers, PPRC discipline callbacks, sysfs/kobject infrastructure, IPL metadata for `ipldev`, and module parameter/init setup. The exported feature and device lookup helpers are used by DASD disciplines and other DASD core code.

## Risks

This file contains many lock/refcount transitions; device creation/deletion and sysfs reads must avoid stale live device pointers. Several sysfs stores return after acquiring a device reference; error paths must put references consistently. Copy-pair setup is sensitive because misconfigured PPRC relations could route I/O to the wrong mirror side, so the code cross-checks all related devices. `use_diag`/raw toggles are intentionally constrained because changing discipline mode online would invalidate live state. Path kobjects are kept for device lifetime and must only be removed in offline context, as documented in the file.

## Test Signals

Useful validation includes parsing `dasd=` keywords/ranges/feature lists including `ipldev`, duplicate bus ID insertion preserving stable devindex, create/delete refcount drain, sysfs show/store behavior for each feature and live attribute, readonly propagation to gendisk, offline-only rejection for diag/raw mode changes, copy-pair setup/clear with online/offline combinations, PPRC validation failures, path kobject create/remove on path availability, and absence of devmap leaks after `dasd_devmap_exit()`.
