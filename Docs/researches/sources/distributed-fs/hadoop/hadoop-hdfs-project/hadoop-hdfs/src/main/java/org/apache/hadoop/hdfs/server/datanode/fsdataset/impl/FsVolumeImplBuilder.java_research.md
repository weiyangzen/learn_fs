# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsVolumeImplBuilder.java

`FsVolumeImplBuilder` centralizes construction of `FsVolumeImpl` and `ProvidedVolumeImpl` instances. It collects dataset, storage ID, storage directory, configuration, IO provider, and optional test `DF` usage.

The builder exposes package-private fluent setters and a test-only `setUsage`. `build()` branches on `StorageType.PROVIDED`, returning `ProvidedVolumeImpl` with a fallback `FileIoProvider` when needed. For normal storage it creates a `DF` rooted at the storage directory parent unless tests supplied one, then constructs `FsVolumeImpl`.

The builder has no persistence; it determines the runtime `DF` object used later for capacity, available-space, and mount accounting. It is used by `FsDatasetImpl` startup/dynamic volume paths and tests.

Risks are mostly validation gaps: required fields are not checked in the builder, so nulls fail in downstream constructors; accidental fallback `FileIoProvider` use can skip live instrumentation; incorrect PROVIDED detection creates the wrong volume type. Tests should cover PROVIDED/non-PROVIDED construction, injected usage preservation, fallback provider behavior, and malformed storage directory failures.
