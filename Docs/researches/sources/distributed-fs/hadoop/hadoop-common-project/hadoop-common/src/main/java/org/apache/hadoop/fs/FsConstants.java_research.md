# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsConstants.java

Purpose: `FsConstants` centralizes stable filesystem constants such as local filesystem URI, FTP scheme, viewfs URI/scheme/type, viewfs overload config-key pattern, and maximum symlink traversal depth.

Important APIs: constants `LOCAL_FS_URI`, `FTP_SCHEME`, package-visible `MAX_PATH_LINKS`, `VIEWFS_URI`, `VIEWFS_SCHEME`, `FS_VIEWFS_OVERLOAD_SCHEME_TARGET_FS_IMPL_PATTERN`, and `VIEWFS_TYPE`.

Control flow and state: this is an interface constant holder with no runtime behavior, no mutable state, and no persistence. Values are initialized at class loading.

Dependencies and integration: consumed by filesystem resolution, symlink resolution, local FS defaults, FTP integration, and viewfs mount/overload code. Values must remain compatible with URI parsing and config naming across Hadoop modules.

Risks: changing URI or scheme constants breaks configuration and path resolution compatibility. `MAX_PATH_LINKS` bounds recursive symlink resolution; increasing or decreasing it affects loop protection and legitimate deep chains.

Test signals: verify constants used by URI creation, viewfs configuration lookup, and symlink loop handling remain stable.
