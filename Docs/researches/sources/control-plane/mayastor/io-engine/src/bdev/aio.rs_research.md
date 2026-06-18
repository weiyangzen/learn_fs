<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/aio.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/aio.rs

Purpose: URI-backed implementation for SPDK AIO bdev creation, destruction, probing, and optional rescan.

Important APIs/types: `Aio` stores name/path, alias URI, block size, optional UUID, and rescan flag. `TryFrom<&Url>` parses path segments, detects whether the path is a block device, parses `blk_size`, `uuid`, and `rescan`, and rejects unknown query parameters. `CreateDestroy::create()` creates an AIO bdev with `create_aio_bdev`, sets UUID/alias, or rescans an existing bdev when requested. `destroy()` calls async `bdev_aio_delete`. `Probe` checks file existence with `probe_file`.

Control flow: existing bdev without `rescan` is an error; with `rescan`, `bdev_aio_rescan` updates block count. Creation looks up the bdev after SPDK returns success to attach metadata.

State and dependencies: mutates SPDK bdev registry and aliases. Depends on filesystem metadata, libspdk AIO APIs, futures oneshot callbacks, and `BdevError`.

Risks and test signals: default block size is `0` for block devices and `512` for files. Destroy is asynchronous and depends on callback delivery. Test with file-backed and block-device AIO URIs, UUID alias lookup, and resize/rescan scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/aio.rs -->
