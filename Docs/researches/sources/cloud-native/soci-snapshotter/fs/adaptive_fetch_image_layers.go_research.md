## sources/cloud-native/soci-snapshotter/fs/adaptive_fetch_image_layers.go

Purpose: manages parallel image layer download/unpack jobs, resource limits, on-disk temporary unpack state, and garbage collection.

Important APIs/types/functions: `SemaphoreWithNil`, `unpackJobs`, `newUnpackJobs`, `checkParallelPullUnpack`, `LayerUnpackJobStorage`, `LayerUnpackDiskStorage`, `imageUnpackJob`, `layerUnpackJob`, `LayerUnpackResourceController`, and garbage collector policies.

Control flow: create job manager from parallel config, validate limits, build global semaphores, start garbage collector, add image/layer jobs, claim layer jobs for unpack, acquire download/unpack leases, read ingest tarballs, verify empty unpack destination, and remove or cancel jobs. Disk storage recreates `root/unpack` fresh and creates random job dirs with `fs` subdirs.

State and persistence: in-memory image/layer maps plus temporary disk job directories under `unpack`; GC removes untracked disk jobs and expires long-running in-memory jobs.

Dependencies and integration: config parallel settings, containerd logging, OS filesystem, semaphores, and unpacker consumers.

Risks and test signals: random ID generation has finite retries; `newLayerUnpackDiskStorage` deletes existing unpack root on startup; expiry cancels whole image jobs. Tests cover validation, GC, disk storage, claims, paths, and disabled parallel struct creation.
