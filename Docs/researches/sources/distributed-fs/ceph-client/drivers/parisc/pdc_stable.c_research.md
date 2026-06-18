# sources/distributed-fs/ceph-client/drivers/parisc/pdc_stable.c

## Purpose
This file exposes HP PA-RISC PDC Stable Storage through sysfs under `/sys/firmware/stable`. It provides read/write access to boot paths, path layers, autoboot/autosearch flags, OS-dependent storage areas, and diagnostic fields while caching firmware path entries in kernel objects.

## Important APIs, Types, And Functions
Core state is `struct pdcspath_entry`, which stores a stable-storage address, name, cached `pdc_module_path`, mapped Linux device, lock, readiness flag, and kobject. Path operations include `pdcspath_fetch()`, `pdcspath_store()`, `pdcspath_hwpath_read/write()`, `pdcspath_layer_read/write()`, and generic kobject show/store wrappers. Root sysfs attributes are implemented by `pdcs_size_read()`, `pdcs_autoboot_read/write()`, `pdcs_autosearch_read/write()`, `pdcs_timer_read()`, `pdcs_osid_read()`, `pdcs_osdep1_read/write()`, `pdcs_diagnostic_read()`, `pdcs_fastsize_read()`, and `pdcs_osdep2_read/write()`. Module lifecycle is `pdc_stable_init()`/`pdc_stable_exit()`.

## Control Flow
Initialization queries stable-storage size, rejects machines with less than 96 bytes, reads OSID, creates `/sys/firmware/stable`, installs root attributes, creates a `paths` kset, then fetches and registers the primary, alternative, console, and keyboard path entries. Each registered path gets `hwpath` and `layer` files plus a `device` symlink when a matching kernel device is found. Path writes parse user text, validate hardware paths by resolving to a real device, update cached state under a write lock, call `pdc_stable_write()`, and refresh the symlink. Flag and OS-dependent writes require `CAP_SYS_ADMIN`; OS-dependent writes also require Linux OSID.

## State And Persistence
The driver caches firmware data in `pdcspath_entry` objects but writes changes back to PDC Stable Storage, making them persistent across reboot. `pdcs_size` and `pdcs_osid` are initialized once. Read/write locks protect each path entry’s cached state. Sysfs kobjects and links persist until module exit.

## Dependencies And Integration Points
It depends on PDC stable-storage calls, PA-RISC hardware path conversion helpers, sysfs/kobject infrastructure, Linux capabilities, firmware kobject, and device model links. It exposes boot configuration to userspace tools and can affect firmware boot behavior.

## Risks
Writes can persistently corrupt firmware boot paths or OS-dependent data if parsing or user intent is wrong; warnings acknowledge limited recovery after failed PDC writes. Hardware path validation checks existence but not whether the target is a sensible boot device. Layer writes are less validated than hardware path writes. Some sysfs files trigger PDC calls and can be expensive. `pdcs_osdep2_read()` can print many lines into a single sysfs buffer if firmware reports a large optional area.

## Test Signals
Signals include `/sys/firmware/stable` creation, correct size/OSID reporting, path directories and device symlinks, successful readback after changing a path or layer, permission failures for unprivileged writes, and PDC read/write error propagation. Reboot validation should confirm persistent autoboot/autosearch/path changes match firmware behavior.
