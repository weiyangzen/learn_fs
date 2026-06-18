## sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers_test.go

Purpose: validates parallel pull job manager, garbage collection, disk storage, and layer job behavior.

Important APIs/types/functions: `TestParallelPullUnpackValidation`, `TestNoGoroutinesAreLeakedWhenGarbageCollectionIsCancelled`, GC tests, `LayerUnpackVirtualStorage`, `TestLayerUnpackDiskStorage`, `TestLayerUnpackJob`, and `TestParallelStructCreation`.

Control flow: tests use a shortened GC interval, virtual storage for most GC behavior, temp dirs for disk storage, `goleak` for goroutine cleanup, and fake timestamps to simulate expired jobs.

State and persistence: temp directories and virtual `sync.Map` storage emulate persistent unpack jobs.

Dependencies and integration: exercises `newUnpackJobs`, storage interface, job claim/path methods, and `createParallelPullStructs` from nearby fs code.

Risks and test signals: strong coverage of lifecycle and cleanup. Tests do not exercise actual network download, decompression, semaphore blocking under contention, or destination poisoning beyond path setup.
