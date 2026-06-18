# File Research: sources/block-storage/lvm2/lib/metadata/integrity_manip.c

Purpose: implements dm-integrity layering for LVM RAID images, including metadata LV sizing/creation, integrity block-size selection, adding/removing integrity wrappers, metadata extension, mismatch reporting, and integrity setting serialization.

Read coverage: complete file read, 1,057 lines.

Key responsibilities:
- Finds integrity wrapper LVs from origin LVs and identifies integrity origins.
- Estimates integrity metadata size using data size, journal size, VG extent size, and fixed trial-derived metadata overhead rules.
- Creates temporary `_imeta` metadata LVs for integrity, allocated near each RAID image and zeroed before use.
- Extends existing integrity metadata LVs for RAID images when the protected origin grows.
- Removes integrity from all or selected RAID images by removing `_iorig` layers, detaching `_imeta`, clearing flags/settings, reloading active LVs, deactivating unused layers, and removing metadata/origin helper LVs.
- Parses integrity mode strings, accepting journal and bitmap modes.
- Chooses integrity block size based on device logical/physical block sizes, filesystem block size, command context (`lvcreate` versus `lvconvert`), active state, and user override.
- Adds integrity to RAID by creating per-image `_imeta` LVs, optionally reusing an existing metadata LV, inserting `_iorig` layers under each RAID image, replacing each image's first segment with an integrity segment, and setting default tag size/hash/mode/block size.
- Handles active versus inactive setup by either update/reload or commit plus activate, then clears `integrity_recalculate` after initial activation starts kernel initialization.
- Exposes helpers to clear or detect recalculate metadata flags, detect RAID integrity, retrieve settings, and aggregate mismatch counts across RAID images.
- Serializes selected dm-integrity settings into string lists for reporting/config output.

Important entry points:
- `lv_add_integrity_to_raid()`, `lv_remove_integrity_from_raid()`, `lv_extend_integrity_in_raid()`.
- `lv_integrity_from_origin()`, `lv_is_integrity_origin()`, `lv_raid_has_integrity()`, `lv_get_raid_integrity_settings()`.
- `integrity_mode_set()`, `lv_integrity_mismatches()`, `lv_raid_integrity_total_mismatches()`.
- `lv_clear_integrity_recalculate_metadata()`, `lv_has_integrity_recalculate_metadata()`, `integrity_settings_to_str_list()`.

Dependencies:
- Uses metadata, locking, activation, display, segment types, config defaults, LV creation, PV-list discovery, direct block-size probing, filesystem block-size probing, and dm-integrity status structures.
- Relies on RAID segment layout and image/meta LV conventions from the metadata layer.

Risk and edge cases:
- Integrity is limited to supported RAID levels: raid1, raid4, raid5, raid6, and raid10.
- Block-size selection is conservative for active LVs to avoid surprising applications with changed I/O constraints.
- Metadata LV creation and layer insertion have rollback logic, but some failures after VG writes may require manual cleanup.
- The code assumes per-image `_imeta` LVs can be allocated from the image's current PV list and currently treats metadata as single-PV in extension.
- Recalculate metadata must be cleared after initialization starts; otherwise future activations can restart initialization.
