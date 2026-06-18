# File Research: sources/block-storage/lvm2/lib/label/hints.c

## Summary
Implements LVM’s runtime hint-file cache under `/run/lvm`, used to reduce device scanning by remembering which devices previously contained LVM labels.

## Main Responsibilities
- Manages `hints`, `newhints`, and `nohints` files and their locking protocol.
- Reads and validates hint files against version, global filter, filter, `scan_lvs`, devices-file setting, and a CRC/hash of scan-relevant device names.
- Applies hints by moving matching devices from the full scan list to the reduced scan list, optionally narrowed by a single VG command argument.
- Validates used hints after scanning against observed PVIDs, VG names, duplicate PVs, duplicate VG names, and unread devices.
- Writes fresh hint files after full scans, including device path, PVID, device major/minor, VG name, filters, devices-file, and device-set hash.
- Clears or invalidates hints for commands that change global PV/VG state or for `pvscan --cache`.

## Important Behavior
`get_hints()` returns either “use these hints” or “scan everything and maybe write new hints later.” Stale hints are detected before use by config/device-set checks and after use by comparing scan results to hint entries. `clear_hint_file()` touches `nohints`, takes an exclusive lock, empties the hint file, touches `newhints`, and keeps the lock until later write/unlock paths.

## State And Dependencies
Uses global `_hints_fd`, static path constants, `struct hint` lists, device iterators, lvmcache, command filter callbacks, devices-file lookups, CRC helpers, and flock-based synchronization.

## Risks And Invariants
The device-set hash depends on stable device iteration order. Hints intentionally err toward refresh rather than missing a device. Locking is split between shared readers, exclusive clear/recreate paths, and sentinel files, so callers must pair `get_hints()` new-hints outcomes with `write_hint_file()` to release the exclusive lock.
