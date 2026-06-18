# File Research: sources/block-storage/mdadm/Incremental.c

This file implements `mdadm --incremental` behavior for udev-style device arrival, array auto-assembly, spare-device admission, scan/start of previously mapped arrays, container member assembly, and device removal from arrays.

Main entry points:
- `Incremental()` handles a newly seen block device. It validates policy, reads metadata, matches `mdadm.conf`, chooses or creates an md device, adds the component, updates the map file, and starts the array when enough safe devices are present.
- `IncrementalScan()` walks the mdadm map file and starts inactive mapped arrays or delegates container activation.
- `Incremental_remove()` handles device removal by failing and removing the member from native arrays or external containers.
- `incremental_external_test_spare_criteria()` checks external metadata spare criteria before adding a bare disk to a container.
- `Incremental_container()` assembles member arrays inside an external metadata container.

Incremental assembly flow:
- The incoming device must be a block device and allowed by `mdadm.conf` device rules.
- Container devices are detected early with `must_be_container()` and delegated to `Incremental_container()` after `load_container()`.
- Non-container devices are probed with `guess_super_type()` and `load_super()`. If no usable md metadata is found, `try_spare()` attempts to treat the device as a spare according to policy.
- `conf_match()` and homehost matching classify the array name as trusted local, local-any, foreign, or metadata-derived. Foreign arrays avoid trusting array names unless policy allows.
- The map file is locked while selecting or creating the md device to avoid races with concurrent incremental events.
- Existing arrays are found by UUID in the map file; otherwise `create_mddev()` chooses a new md device name from config, metadata name, or an automatically assigned name.
- New arrays are initialized with `set_array_info()` and receive the first device through `add_disk()`.
- Existing arrays are checked against one already attached member via duplicated supertype and `compare_super()` before accepting the new disk.
- For active native arrays, non-spare in-sync components are generally not re-added unless `--run` or policy allows re-add.
- Clustered arrays are skipped for normal incremental auto-start because cluster resource agents should control them.

Start decision:
- After a disk is attached, `count_active()` rereads each component superblock to determine the best event count, available slots, replacement devices, stale devices, and journal cleanliness.
- `enough()` decides whether the collected devices can start the array, with PPL treated as clean enough by setting the clean state bit.
- Arrays are started with `RUN_ARRAY` when sufficiently complete and trusted; otherwise sysfs `array_state=read-auto` is used for partial/foreign cases.
- Reshaping arrays that require backup are not started by `--incremental`; the user is directed to `--assemble`.
- Lockless bitmap metadata can set sysfs `bitmap_type=llbitmap` before start.
- After a successful start, devices rejected by the kernel due to age may be re-added if their policy allows `re-add`.

Container behavior:
- `Incremental_container()` loads container content, checks whether enough container devices are present, matches the container against config/homehost, and iterates member arrays.
- It skips metadata-blocked volumes, reuses existing map entries when present, or creates member md devices when allowed.
- Member naming can be matched through `mdadm.conf` `container` plus `member` rules, using `container2devname()` to resolve configured container references.
- Each member is assembled by `assemble_container_content()`, then udev is unblocked and a sysfs change event is emitted.
- `IncrementalScan()` detects map entries that represent container members and restarts scanning at the parent container when a specific member device is requested.

Spare handling:
- `try_spare()` is used when a device has no md component metadata or when metadata loading fails but policy permits spare use.
- Spare eligibility requires a policy domain and an action allowing `spare`.
- `is_bare()` checks whether the first and last 4 KiB are uniformly blank-like (`0x00`, `0x5a`, or `0xff`); non-bare devices require a same-slot target policy.
- `array_try_spare()` scans mapped arrays/containers for compatible metadata type, domain, size, target UUID, and degradation, preferring the target array or most degraded candidate.
- For containers, `incremental_external_test_spare_criteria()` can ask the metadata backend for size/domain criteria and verify the disk.
- `partition_try_spare()` supports virtual partition metadata by scanning `/dev/disk/by-path`, finding a compatible disk whose partition metadata fits, and copying its metadata to the new device.

Device rejection and active counting:
- `find_reject()` removes an older attached device with the same metadata disk number when a newer event-count device arrives and `add_disk()` reports `EBUSY`.
- `count_active()` loads all attached member superblocks, tracks maximum event count, records per-slot availability, rejects devices that think the best device is failed, rejects spare devices with future event counts, and returns active plus replacement count.
- Journal-device state is tracked with `max_journal_events`; a journal is considered clean when it is no more than one event behind the data devices.

Removal path:
- `Incremental_remove()` accepts either a kernel device name or direct `/dev/<name>` path, finds the containing array through `/proc/mdstat`, and initializes sysfs for that array.
- It tries an exclusive open to avoid racing active rebuild behavior, then may set active/clean arrays to `read-auto`.
- If `id_path` is supplied, the path is saved in policy state for bare replacement scenarios.
- External metadata arrays use `Incremental_remove_external()`, which marks the member faulty in each subarray and only removes it from the container if all subarray failure operations succeeded.
- Native arrays set the member state to faulty and then retry `remove` for up to 25 attempts with 200 ms sleeps, allowing kernel recovery/resync threads to quiesce.

Important implementation notes:
- The file is deliberately race-aware: it uses map-file locking, temporary exclusive opens, udev unblock/change events, and mdmon pings for external metadata.
- Policy is central. `mdadm.conf`, homehost, metadata enablement, path/domain rules, spare actions, same-slot rules, and re-add/force-spare actions all affect whether a device is used.
- The code avoids expensive full sysfs models in removal because disk-removal handling is considered critical and should not fail due to unrelated sysfs parsing issues.
- This file depends on mdadm metadata backends, policy/config parsing, map-file helpers, sysfs/mdstat helpers, udev integration, md device creation/open helpers, and shared assembly/manage routines.
