# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.h

## Purpose
Declares the opaque layout API used by the UDS index to manage persistent storage format, saved state, volume-region dm-bufio access, and backing-device replacement.

## Important APIs, Types, And Functions
The header forward-declares `struct index_layout` and exposes `uds_make_index_layout()`, `uds_free_index_layout()`, `uds_replace_index_layout_storage()`, `uds_load_index_state()`, `uds_save_index_state()`, `uds_discard_open_chapter()`, `uds_get_volume_nonce()`, and `uds_open_volume_bufio()`. `uds_make_index_layout()` takes a `struct uds_configuration`, a `new_layout` flag, and returns an initialized layout; `uds_open_volume_bufio()` returns a dm-bufio client positioned on the volume region.

## Control Flow
The header forms the boundary between high-level index lifecycle code and on-disk layout implementation. `index.c` calls it during index construction, save, load, recovery, storage replacement, and chapter-writer cleanup of saved open-chapter data. `volume.c` can use `uds_open_volume_bufio()` to access only the volume region without knowing the whole on-disk map.

## State And Persistence
The header intentionally hides serialized metadata and save-slot details. Callers only see the ability to create/load a layout, save/load index state, discard a saved open chapter, and fetch the volume nonce used to bind lower-level persisted structures to the layout.

## Dependencies And Integration Points
Includes `config.h`, `indexer.h`, and `io-factory.h`, so it connects configuration, public UDS types, block devices, and dm-bufio. It is included by `index.h`, `index.c`, and storage-facing volume code.

## Risks
Because the type is opaque, callers must respect API sequencing: create layout before volume/index construction, do not use after free, and drain requests before save. `uds_replace_index_layout_storage()` assumes the replacement device is compatible with the existing layout, so session-level checks and block-device management matter.

## Test Signals
Compile coverage should catch signature drift. Integration tests should verify callers can create, load, save, replace storage, open the volume bufio client, and recover the volume nonce without depending on private layout fields.
