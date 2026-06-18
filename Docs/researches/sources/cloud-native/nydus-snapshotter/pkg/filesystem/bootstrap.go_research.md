# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/bootstrap.go

This file implements bootstrap readiness validation before a snapshot is mounted. It prevents `nydusd` from reading partially written `image.boot` and related `.blob.meta` files. `waitForReadyBootstrapWithRetry` repeatedly calls `validateBootstrapAndBlobMeta` and requires two consecutive equal `bootstrapState` observations before returning success.

`validateBootstrap` opens the bootstrap, requires a regular file, reads up to `layout.MaxSuperBlockSize`, detects RAFS v5/v6 via `layout.DetectFsVersion`, and for v6 validates size alignment based on block bits at `layout.RafsV6SuperBlockOffset + 12`. `validateBlobMetaFiles` finds sibling `*.blob.meta` files, sorts them, and validates each is a regular non-empty readable file. `detectV6BlockSize` currently accepts 512 and 4096 byte block sizes.

State is derived from file size and blob-meta filenames/sizes; persistence belongs to snapshot preparation. Integration points include `Filesystem.Mount`, RAFS layout constants, and the retry utility. Risks include accepting stable but semantically incomplete files, limited v6 block-bit support, and relying on consecutive polling instead of writer-side atomic rename. Tests cover stable changes, misalignment, v5 acceptance, too-small headers, blob-meta sorting, and block-bit errors.
