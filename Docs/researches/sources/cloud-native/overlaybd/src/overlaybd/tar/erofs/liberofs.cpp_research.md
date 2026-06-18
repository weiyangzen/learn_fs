# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/liberofs.cpp

## Purpose
Builds EROFS images from tar streams using erofs-utils, then imports generated block mappings into an OverlayBD/LSMT target file as remote data mappings.

## Important APIs and Types
Defines `erofs_mkfs_cfg`, `erofs_mkfs`, `erofs_init_sbi`, `erofs_init_tar`, `erofs_write_map_file`, `erofs_close_sbi`, `erofs_close_tar`, and `LibErofs::extract_tar`. `LibErofs` is the public wrapper class.

## Control Flow
`extract_tar` prepares target and source `liberofs_file` vfops, initializes erofs superblock and tar parser state, configures rebuild options, opens a temporary block map file, runs `erofs_mkfs`, then replays the map file into the target via `IFileRW::RemoteData` ioctls. `erofs_mkfs` initializes or reads superblock state, rebuilds the inode tree from tar entries, dumps blobs, flushes buffers, writes the superblock, and resizes the erofs device.

## State and Persistence
Persistent output is written to the target Photon file through the target cache. The temporary map file records EROFS block-to-source offsets and is used to create LSMT remote mappings. Incremental mode depends on whether this is the first layer.

## Dependencies and Integration Points
Depends on erofs-utils tar/rebuild/blob/block-list APIs, LSMT `IFileRW::RemoteData`, shared EROFS Photon adapters, and Photon logging. It links through `erofs_lib` and is used by tar/image import flows.

## Risks
`meta_only` is accepted but unused. Global `rebuild_src_count` is static and not updated here, which may affect device numbering expectations. `std::tmpfile` failure is not checked before use. Map parsing is strict and can abort the import after EROFS data has already been written.

## Test Signals
Tests should build first and incremental EROFS layers from tar streams, verify generated images through `ErofsFileSystem`, check RemoteData mapping counts/offsets, and cover tar headers import mode.
