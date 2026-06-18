# sources/cloud-native/soci-snapshotter/fs/unpacker.go

Purpose: implements layer unpacking for converting remote/lazy layers into local unpacked snapshots and provides archive application with asynchronous digest verification.

Important APIs and flow: `Unpacker` exposes `Unpack`. `Archive` abstracts tar application. `asyncVerifier` copies a stream into a digest verifier in a goroutine and later reports `Verified`. `NewLayerArchive` installs containerd decompression and a default 64 KiB buffer pool when not supplied. `AsyncTeeReader` feeds one reader to the archive path and asynchronously writes copied chunks to a verifier pipe. `layerArchive.Apply` decompresses, optionally tees uncompressed data for verification, applies the archive with containerd whiteout handling, drains trailing data, then checks uncompressed and compressed verifier results. `layerUnpacker.Unpack` fetches a layer, stores it first if remote-only, fetches again locally, builds overlay parent options, and applies the archive.

State and persistence: unpack writes filesystem changes into `mountpoint`. If the fetcher reports non-local content, `Store` persists the compressed layer before apply. `bufferPool` recycles byte slices for teeing but has no durable state.

Dependencies and integration: integrates with the package `Fetcher` interface, containerd mounts/archive/whiteout conversion, internal decompression hooks, OCI descriptors, and overlay lowerdir mount options.

Risks and test signals: `AsyncTeeReader` does not propagate write errors from the async writer to the reader path. `asyncVerifier.started` is not synchronized, though typical use is single-threaded setup. Digest verification requires callers to start the compressed verifier elsewhere before `Apply` checks it. Unit tests cover fetch/store/apply failure counts, happy paths, async tee behavior, and benchmark tee performance.
