# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/HCFSMountTableConfigLoader.java

`HCFSMountTableConfigLoader` implements `MountTableConfigLoader` for mount-table XML files stored on a Hadoop-compatible filesystem. It lets `ViewFileSystemOverloadScheme` load mount-table resources from a configured path before building the in-memory `InodeTree`.

The main API is `load(String mountTableConfigPath, Configuration conf)`. It constructs a `Path`, chooses a child filesystem using `ViewFileSystemOverloadScheme.ChildFsGetter` to avoid overload recursion, lists files directly under the configured path, parses a version number from the penultimate dot-separated filename component, selects the highest version, opens it, loads it into a fresh `Configuration(false)`, and adds that resource into the caller's configuration. Invalid file names and missing valid versions are logged rather than thrown.

State is limited to the last `mountTable` path field during a load call. Persistence is external: versioned XML files are read from the configured filesystem; the in-memory `Configuration` is mutated by `addResource`.

Dependencies include `FileSystem`, `FSDataInputStream`, `RemoteIterator<LocatedFileStatus>`, `Path`, SLF4J, and the overload scheme child getter. Integration point is `ViewFileSystemOverloadScheme.initialize`, gated by `fs.viewfs.mounttable.path`.

Risks include ambiguous file naming, direct-file path handling versus directory listing, lack of strict failure when no file is found, version parsing from names with extra dots, and consistency during concurrent mount-table updates. Tests should cover highest-version selection, invalid names, empty directory warning behavior, configured single path expectations, resource loading, stream closing, and overload-scheme same-scheme target resolution.
