# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/MountTableConfigLoader.java

`MountTableConfigLoader` is the private evolving SPI for loading viewfs mount-table configuration from an external location. It defines one method, `load(String mountTableConfigPath, Configuration conf)`, which implementations use to mutate the supplied Hadoop `Configuration` before the mount table is parsed.

There is no state, control flow, or persistence in the interface itself. The persistence contract is defined by implementations: the bundled `HCFSMountTableConfigLoader` reads XML resources from Hadoop-compatible filesystems. `Constants.DEFAULT_MOUNT_TABLE_CONFIG_LOADER_IMPL` points to that implementation, and `ViewFileSystemOverloadScheme` obtains a configurable implementation through `fs.viewfs.mounttable.config.loader.impl`.

Risks are API-contract risks. A loader may partially mutate configuration before throwing, may block initialization on slow storage, or may load keys that conflict with already-present core-site keys. Tests should verify that configured loader classes are instantiated, `load` is called before `ViewFileSystem.initialize`, IOExceptions propagate as initialization failures, and bad loader classes fail clearly.
