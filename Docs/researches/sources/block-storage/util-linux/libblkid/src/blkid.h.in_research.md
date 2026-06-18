# File Research: sources/block-storage/util-linux/libblkid/src/blkid.h.in

## Purpose
Public generated C header for libblkid. It declares opaque API types, version macros, cache APIs, device iteration APIs, evaluation helpers, low-level probe APIs, superblock/topology/partition APIs, return codes, and deprecated compatibility wrappers.

## Main Components
- Version macros populated by build configuration: `LIBBLKID_VERSION`, major/minor/patch, and date.
- Opaque typedefs for `blkid_dev`, `blkid_cache`, `blkid_probe`, `blkid_topology`, `blkid_partlist`, `blkid_partition`, `blkid_parttable`, and iterators.
- High-level cache and device APIs: `blkid_get_cache()`, `blkid_put_cache()`, `blkid_gc_cache()`, device iteration, and tag search.
- Device-number helpers: `blkid_devno_to_devname()` and `blkid_devno_to_wholedisk()`.
- Evaluate APIs for resolving tags/specs to device paths: `blkid_evaluate_tag()`, `blkid_evaluate_tag2()`, and `blkid_evaluate_spec()`.
- Probe lifecycle and setup APIs: `blkid_new_probe()`, `blkid_new_probe_from_filename()`, `blkid_free_probe()`, reset, hidden ranges, device assignment, dimension accessors, sector size, FD, hints, and value access.
- Superblock probing controls and result flags such as `BLKID_SUBLKS_LABEL`, `BLKID_SUBLKS_UUID`, `BLKID_SUBLKS_MAGIC`, and `BLKID_SUBLKS_FSINFO`.
- Topology probing controls and binary topology getters.
- Partition probing controls, partition filter APIs, partition flags such as `BLKID_PARTS_FORCE_GPT`, and binary partition/list/table accessors.
- Generic probing calls: `blkid_do_probe()`, `blkid_do_safeprobe()`, `blkid_do_fullprobe()`, wipe helpers, and result constants.
- Deprecated probe filter/request compatibility declarations.

## Dependencies and Interactions
This header is installed for external consumers and hides all internal structures behind opaque pointers. Implementation comes from the core files and chain drivers declared internally in `blkidP.h`.

## Research Notes
The public partition API reports starts and sizes in 512-byte sectors, while topology fields use bytes or device-specific values. Several functions are annotated with GCC attributes for `warn_unused_result`, `nonnull`, or deprecation.
