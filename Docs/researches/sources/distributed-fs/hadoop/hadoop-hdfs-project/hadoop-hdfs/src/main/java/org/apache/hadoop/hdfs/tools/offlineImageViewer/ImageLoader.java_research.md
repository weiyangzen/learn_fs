## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/ImageLoader.java

Purpose: `ImageLoader` is the legacy binary fsimage parser abstraction. Implementations accept a `DataInputStream`, traverse an image, and emit structural events to an `ImageVisitor`.

Important APIs and control flow: `loadImage(DataInputStream, ImageVisitor, boolean enumerateBlocks)` parses an image and controls whether individual file blocks are visited. `canLoadVersion(int)` declares supported layout versions. The nested `LoaderFactory.getLoader(version)` currently tries a single `ImageLoaderCurrent` instance and returns it if `canLoadVersion` matches; otherwise it returns `null`.

State, persistence, and dependencies: the interface itself has no state. Implementations own parser state and do not persist output directly; visitors do. It depends on `DataInputStream`, `IOException`, and Hadoop classification annotations.

Integration points: legacy `OfflineImageViewer.go()` reads the image version, asks this factory for a loader, and invokes `loadImage`.

Risks and test signals: adding support for a new layout version requires updating or adding loaders in the factory. Tests should verify unsupported versions return `null` and callers handle that path. Since the factory creates a new loader each call, implementation state is not shared across viewer runs.
