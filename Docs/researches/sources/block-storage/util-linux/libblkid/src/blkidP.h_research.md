# File Research: sources/block-storage/util-linux/libblkid/src/blkidP.h

## Purpose
Internal header for libblkid. It defines private data structures, chain-driver interfaces, probe state, cache state, debug masks, constants, and non-public helper prototypes used across the library.

## Main Components
- Private `blkid_struct_dev` with device list links, tags, canonical/application names, preferred type, priority, device number, timestamps, flags, and label/UUID shortcuts.
- Private `blkid_struct_tag` for per-device NAME=value tags and per-tag-name lists.
- Chain identifiers for superblocks, topology, and partitions.
- `blkid_chain` and `blkid_chaindrv` abstractions that let each probing subsystem define idinfos, filters, default flags, probe operations, and binary data cleanup.
- `blkid_prval` for low-level probe result values.
- `blkid_idmag` and `blkid_idinfo` for magic-driven format detection and prober callbacks.
- `blkid_struct_probe`, holding the file descriptor, probed byte range, sector size, device identity, zone size, flags, buffers, hints, chain state, current results, parent/clone state, and whole-disk probe.
- `blkid_config` for config-driven evaluation order, uevent behavior, and cache file.
- `blkid_struct_cache` for cache file/device/tag state.
- Cache defaults for `/run/blkid/blkid.tab` and legacy `/etc/blkid.tab`.
- Error constants, device priority constants, debug masks, and bitmap filter macros.
- Internal prototypes for cache reading/writing, tag manipulation, probe buffer/value handling, UUID formatting, whitespace trimming, wiper state, filters, and partition helpers.

## Dependencies and Interactions
Includes the generated public `blkid.h`, util-linux list/debug/encoding helpers, block-device helpers, and common headers. Nearly every implementation file in this group depends on this header.

## Research Notes
This header reveals libblkid’s core architecture: public opaque objects are private structs, and low-level probing is organized as independently filterable chains over `blkid_idinfo` descriptors.
