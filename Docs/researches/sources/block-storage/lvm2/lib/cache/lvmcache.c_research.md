# File Research: sources/block-storage/lvm2/lib/cache/lvmcache.c

## Summary
Implements LVM2's in-memory scan cache for physical volumes, volume groups, labels, metadata areas, device identity, duplicate PV detection, and stale metadata tracking. It is populated mainly by label scanning, then corrected by full `vg_read()` metadata processing.

## Main Responsibilities
- Maintain global lookup tables from PVID, VGID, and VG name to cached `lvmcache_info` and `lvmcache_vginfo` records.
- Track one cached PV/device record per selected device, including label, format, device size, metadata/data/bootloader areas, bad MDAs, and scan-time metadata sequence information.
- Track one cached VG record per discovered VG, including VG name, VGID, format, status, system ID, lock type, creation host, latest scan checksum/size/seqno, summary mismatch flags, PV summaries, active infos, and outdated infos.
- Populate cache state through `lvmcache_label_scan()` and targeted VG rescans.
- Resolve duplicate devices that expose the same PVID, preferring multipath or MD aggregate devices when duplicates are merely components, and otherwise using device ID, active LV use, device size, previous device hint, mounted filesystem, DM/subsystem status, or first-seen order.
- Correct scan-time inaccuracies after full metadata read, especially PVs without metadata areas and PVs that still contain old VG metadata after removal.
- Preserve and expose bad, missing, outdated, and mismatched metadata areas for repair paths.
- Provide device-filter diagnostic text used when a requested device cannot be used.

## Key State
- `_pvid_hash`: maps PVID strings to selected `lvmcache_info`.
- `_vgid_hash`: maps VGID strings to `lvmcache_vginfo`.
- `_vgname_hash`: maps VG names when name lookup is unambiguous.
- `_vginfos`: master list of VG records, including orphan VG records.
- `_initial_duplicates`: duplicate devices found during the current label scan but not initially inserted into `_pvid_hash`.
- `_unused_duplicates`: duplicate devices not selected for use after duplicate resolution.
- `_found_duplicate_vgnames`: disables simple VG-name lookup when multiple accessible VGs share a name.
- `_outdated_warning`: suppresses repeated outdated-metadata repair hints.

## Important Control Flow
`lvmcache_init()` creates the hash tables and list heads. `lvmcache_add()` is called by label scanning when a label/PVID is discovered. It either creates an info record or detects an existing PVID on another device and saves that device in `_initial_duplicates`.

`lvmcache_label_scan()` clears duplicate lists, runs `label_scan()`, optionally scans extra devices found through devices-file validation, then calls `_choose_duplicates()` when duplicate PVIDs were seen. Chosen replacements are rescanned into cache, unchosen devices are recorded in `_unused_duplicates`, and warnings explain which device is used.

`_choose_duplicates()` first tries to collapse duplicates that are multipath or MD components. If not component-only, it compares candidate devices by stable identity and runtime evidence: configured device ID, whether a device backs an active LV, PV-summary size match, previous device hint, mounted filesystem, DM/subsystem membership, then first-seen order.

`lvmcache_extra_md_component_checks()` performs extra full MD component checks after label scan only when scan evidence suggests the PV may have been found on an MD component, such as PV/device size mismatch or a `/dev/md*` device hint on a non-MD device.

`lvmcache_update_vgname_and_id()` attaches a PV info to a VG info, creates VG records, handles duplicate VGIDs/names, tracks local versus foreign duplicate VG names, updates VG status/system ID/lock type, and records scan seqno/checksum mismatches across MDAs and devices.

`lvmcache_update_vg_from_read()` reconciles scan-time VG membership with the fully parsed VG metadata. It moves removed/stale PVs to `outdated_infos`, attaches no-MDA PVs to the correct VG, detects PVs claiming membership in a different VG, and copies ignored MDAs into the format instance when needed.

## Key Interfaces
- Cache lifecycle: `lvmcache_init()`, `lvmcache_destroy()`.
- Scan entry points: `lvmcache_label_scan()`, `lvmcache_label_rescan_vg()`, `lvmcache_label_rescan_vg_rw()`, `lvmcache_label_reopen_vg_rw()`.
- Device/VG mutation: `lvmcache_add()`, `lvmcache_del()`, `lvmcache_del_dev()`, `lvmcache_update_vgname_and_id()`, `lvmcache_update_vg_from_read()`.
- Lookup APIs: `lvmcache_info_from_pvid()`, `lvmcache_info_from_pv_id()`, `lvmcache_vginfo_from_vgname()`, `lvmcache_vginfo_from_vgid()`, `lvmcache_device_from_pv_id()`.
- Metadata area APIs: `lvmcache_add_mda()`, `lvmcache_get_mdas()`, `lvmcache_get_bad_mdas()`, `lvmcache_get_outdated_mdas()`, `lvmcache_fid_add_mdas_vg()`.
- Duplicate/stale checks: `lvmcache_has_duplicate_devs()`, `lvmcache_dev_is_unused_duplicate()`, `vg_has_duplicate_pvs()`, `lvmcache_has_old_metadata()`, `lvmcache_scan_mismatch()`, `lvmcache_verify_info_in_vg()`.

## Cross-File Interactions
This file sits between label scanning, device filtering, metadata parsing, and command processing. It depends on label and text-format code for labels and MDAs, device-cache and device-id code for device identity, filter code for wiping rejected component devices, metadata code for PV/VG structures, and `toolcontext` for configuration and device-type state.

## Risks
The highest-risk logic is duplicate PVID resolution, because selecting the wrong device can cause commands to operate on a clone, component path, or stale copy. Stale metadata handling is also delicate: equal seqnos with different checksums, old MDAs, no-MDA PVs, and PVs moved between VGs all require conservative behavior. The file uses global mutable state and manual list/hash ownership, so missed detach/free paths can leave stale pointers or inconsistent lookups.
