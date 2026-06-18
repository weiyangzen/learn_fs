# sources/cloud-native/soci-snapshotter/fs/parallel_unpacker.go

Purpose: applies a fetched layer archive into a mountpoint during parallel pull/unpack, optionally storing remotely fetched compressed content into the content store while unpacking.

Important APIs and flow: `NewParallelLayerUnpacker` wraps a fetcher, archive applier, resource controller, and discard flag. `Unpack` fetches the descriptor, acquires an unpack lease, optionally opens an ingest reader and starts a goroutine to `fetcher.Store` when the layer was remote and unpacked layers should be retained, prepares archive apply options including overlay whiteout conversion and parent lowerdirs from mounts, verifies the unpack destination is ready/empty, applies the archive to the mountpoint, logs latency, and waits for the optional store goroutine.

State and persistence: reads from the fetcher, writes extracted filesystem data into `mountpoint`, and may write the compressed layer into the content store from the ingest reader. Resource leases are held for the duration of unpack.

Dependencies and integration: depends on the parallel artifact fetcher, `LayerUnpackResourceController`, containerd archive/mount packages, overlay whiteout conversion, and the archive wrapper that performs digest verification/decompression.

Risks and test signals: storage and unpack consume related readers concurrently, so controller-provided ingest reader behavior is critical. `VerifyUnpackDestinationIsReady` is a security guard against unpacking into poisoned directories. Store errors surface only after archive apply completes via `errGroup.Wait`. No direct tests in this subset cover this file.
