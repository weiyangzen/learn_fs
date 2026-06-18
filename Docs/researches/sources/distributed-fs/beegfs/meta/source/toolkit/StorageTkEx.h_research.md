## sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.h

Purpose: Declares metadata-specific storage toolkit helpers and storage format versions.

Important APIs/types/functions: Defines `STORAGETK_FORMAT_MIN_VERSION` as 3 and current version as 4. Declares storage-format operations and contained-dir iteration helpers. Inline helpers `getMetaInodeHashDir()` and `getMetaDentriesHashDir()` build first/second-level hash directory paths.

Control flow: Header inlines only string path composition.

State and persistence: Constants govern accepted on-disk storage format versions. Path helpers reflect the persistent hash-directory layout.

Dependencies and integration: Includes metadata config, common path, mutex, meta storage, and storage toolkit headers. Used by metadata startup, fsck helpers, and path-walking code.

Risks and test signals: Version constants are migration-sensitive. Tests should check path formatting uses hex directory names and that older supported format versions are accepted only through the cpp validation path.
