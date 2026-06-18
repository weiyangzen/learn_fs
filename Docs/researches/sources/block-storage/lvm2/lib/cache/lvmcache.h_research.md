# File Research: sources/block-storage/lvm2/lib/cache/lvmcache.h

## Summary
Declares the public LVM cache API and the scan-time `lvmcache_vgsummary` structure used to pass lightweight VG metadata from label scanning into cache state.

## Main Responsibilities
- Define orphan VG naming macros.
- Forward-declare core LVM types used by the cache.
- Define `struct lvmcache_vgsummary`, containing VG name, VGID, status, creation host, system ID, lock type, seqno, MDA checksum/size, MDA number, mismatch flags, and PV summaries.
- Expose cache lifecycle, scan, lookup, update, metadata-area, duplicate-device, stale-metadata, bad-MDA, and diagnostic APIs.

## Key Interfaces
- Lifecycle and scan: `lvmcache_init()`, `lvmcache_destroy()`, `lvmcache_label_scan()`, VG rescan/reopen helpers.
- Cache update: `lvmcache_add()`, `lvmcache_add_orphan_vginfo()`, `lvmcache_update_vgname_and_id()`, `lvmcache_update_vg_from_read()`.
- Lookup: PVID, PV ID, VGID, VG name, cached label, cached device, format, device size, VG/PV name lengths.
- Format-instance integration: `lvmcache_fid_add_mdas()`, `lvmcache_fid_add_mdas_pv()`, `lvmcache_fid_add_mdas_vg()`.
- Duplicate and outdated handling: `lvmcache_has_duplicate_devs()`, `lvmcache_get_unused_duplicates()`, `lvmcache_has_duplicate_local_vgname()`, `lvmcache_get_outdated_devs()`, `lvmcache_del_outdated_devs()`.
- Metadata repair support: `lvmcache_has_old_metadata()`, `lvmcache_get_bad_mdas()`, `lvmcache_get_dev_mda()`.

## Important Behavior
The header intentionally hides `struct lvmcache_info` internals while exposing accessors and iterators. `valid_only` is present in lookup signatures, but the implementation currently does not make it a strong validity filter. `lvmcache_vgsummary` is explicitly scan-time summary data rather than authoritative full VG metadata.

## Cross-File Interactions
Used by label scanners, text-format metadata readers/writers, command processing, repair commands, device-id handling, and tool context initialization. `toolcontext.c` initializes orphan cache entries through this API.

## Risks
Because this is a broad internal API, changes to ownership expectations for returned labels, MDAs, or device lists affect many callers. The scan summary structure must stay aligned with text-format scan behavior; otherwise cache mismatch and repair logic can make incorrect decisions.
