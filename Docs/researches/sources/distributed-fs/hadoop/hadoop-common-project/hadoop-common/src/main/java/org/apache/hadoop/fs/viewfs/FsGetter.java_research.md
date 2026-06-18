# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/FsGetter.java

`FsGetter` is a small extension seam for obtaining Hadoop `FileSystem` instances. It exposes `getNewInstance(URI, Configuration)` and `get(URI, Configuration)`, delegating to `FileSystem.newInstance` and `FileSystem.get` respectively.

The class has no state and no persistence behavior. Its purpose is integration flexibility: `ViewFileSystem` uses it when initializing chrooted target filesystems and when deciding whether to use an inner cache; `NflyFSystem` accepts it so tests or overload-scheme code can control how child filesystems are created; `ViewFileSystemOverloadScheme.ChildFsGetter` subclasses it to avoid recursive resolution when an overloaded scheme points at a target with the same scheme.

The main risk is cache semantics. `get` may return shared cached instances while `getNewInstance` returns independent instances, and viewfs code relies on that distinction for lifecycle and loop-avoidance behavior. Tests should use a fake or subclassed `FsGetter` to verify `ViewFileSystem` inner cache behavior, nfly child creation, and overload-scheme target instantiation without coupling tests to global `FileSystem` cache state.
