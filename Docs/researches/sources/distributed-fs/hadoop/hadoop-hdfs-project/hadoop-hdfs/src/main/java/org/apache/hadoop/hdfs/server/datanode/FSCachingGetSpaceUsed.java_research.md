# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/FSCachingGetSpaceUsed.java

Purpose: `FSCachingGetSpaceUsed` is an HDFS DataNode specialization point for cached filesystem-space accounting. It extends Hadoop `CachingGetSpaceUsed` and adds builder context for an `FsVolumeImpl` and block-pool ID.

Important APIs: the abstract constructor delegates to `CachingGetSpaceUsed`. Nested `Builder` extends `GetSpaceUsed.Builder` with `setVolume/getVolume`, `setBpid/getBpid`, and an overridden `build` that detects subclasses of `FSCachingGetSpaceUsed` and installs a `Builder` constructor reflectively before delegating to the base builder.

Control flow and state: all mutable configuration is in the builder. `build` allows concrete implementations to receive the richer builder instead of the generic base builder. The built object inherits cached refresh behavior from `CachingGetSpaceUsed`; this class does not implement scanning itself.

Dependencies and integration points: it depends on `GetSpaceUsed`, `CachingGetSpaceUsed`, `FsVolumeImpl`, and the concrete classes configured as the builder's `klass`. Volume/block-pool context lets implementations compute HDFS-specific usage for a volume and block pool.

Risks: reflection requires subclasses to expose a constructor accepting exactly `FSCachingGetSpaceUsed.Builder`; missing constructors become `RuntimeException`. The raw `Class clazz` loses generic type safety. Misconfigured `volume` or `bpid` may be discovered only by the concrete implementation.

Test signals: verify builder chaining, volume/bpid propagation, reflective constructor selection for subclasses, fallback behavior for non-`FSCachingGetSpaceUsed` classes, and IOException propagation from concrete build paths.
