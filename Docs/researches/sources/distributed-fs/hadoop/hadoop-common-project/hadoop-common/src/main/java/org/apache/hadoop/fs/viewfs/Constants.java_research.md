# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/Constants.java

`Constants` is the shared key and default-value contract for viewfs. It defines mount-table prefixes, link key names, feature flags, defaults, and the read-only internal-directory permission used by `ViewFileSystem`.

Important constants include `CONFIG_VIEWFS_PREFIX`, `CONFIG_VIEWFS_MOUNTTABLE_PATH`, `CONFIG_VIEWFS_HOMEDIR`, `CONFIG_VIEWFS_DEFAULT_MOUNT_TABLE_NAME_KEY`, `CONFIG_NESTED_MOUNT_POINT_SUPPORTED`, `CONFIG_VIEWFS_LINK`, `CONFIG_VIEWFS_LINK_FALLBACK`, `CONFIG_VIEWFS_LINK_MERGE`, `CONFIG_VIEWFS_LINK_NFLY`, `CONFIG_VIEWFS_LINK_MERGE_SLASH`, `CONFIG_VIEWFS_LINK_REGEX`, `CONFIG_VIEWFS_RENAME_STRATEGY`, `CONFIG_VIEWFS_ENABLE_INNER_CACHE`, `CONFIG_VIEWFS_MOUNT_LINKS_AS_SYMLINKS`, `CONFIG_VIEWFS_IGNORE_PORT_IN_MOUNT_TABLE_NAME`, `CONFIG_VIEWFS_MOUNTTABLE_LOADER_IMPL`, and `CONFIG_VIEWFS_TRASH_FORCE_INSIDE_MOUNT_POINT`. `PERMISSION_555` is reused when synthetic mount-table directories and symlink-like mount entries are listed.

The interface has no control flow or mutable state, but it strongly shapes runtime behavior in `ConfigUtil`, `InodeTree`, `ViewFileSystem`, `ViewFileSystemOverloadScheme`, and `HCFSMountTableConfigLoader`. The default loader is `HCFSMountTableConfigLoader.class`.

Risks are compatibility risks: changing strings breaks existing core-site.xml deployments, and changing defaults can alter mount listing, caching, trash root, or URI-authority behavior. Tests should treat these constants as wire/configuration contract, checking exact property names and defaults used by parser and helper APIs.
