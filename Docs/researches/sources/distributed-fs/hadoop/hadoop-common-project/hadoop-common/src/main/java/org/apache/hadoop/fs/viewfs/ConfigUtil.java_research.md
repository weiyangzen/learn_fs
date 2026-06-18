# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ConfigUtil.java

`ConfigUtil` is a public convenience API for writing and reading viewfs mount-table configuration keys. It centralizes the key layout defined by `Constants`, so callers do not need to manually compose `fs.viewfs.mounttable.<name>.*` properties.

Important APIs include `getConfigViewFsPrefix`, `addLink`, `addLinkMergeSlash`, `addLinkFallback`, `addLinkMerge`, `addLinkNfly`, `addLinkRegex`, `setHomeDirConf`, `getHomeDirValue`, `getDefaultMountTableName`, `isNestedMountPointSupported`, and `setIsNestedMountPointSupported`. `addLinkNfly` supplies a default `minReplication=2,repairOnRead=true` settings string when settings are omitted. `addLinkRegex` embeds optional interceptor settings using `RegexMountPoint.SETTING_SRCREGEX_SEP`.

There is no persistent state in this class; all effects are writes to a supplied `Configuration`. Control flow is simple key assembly with validation for home directory values starting with `/`. Dependencies are `Configuration`, `URI`, `StringUtils`, and the viewfs constants/regex separator.

Integration points are broad: tests and applications can create mount tables programmatically, while `InodeTree` later parses these same keys. The default mount table name feeds `ViewFileSystem.initialize` when no URI authority is provided.

Risks are mostly compatibility and formatting risks: `Arrays.toString(targets)` for merge links must remain parseable by `StringUtils.getStrings`, nfly settings must match `NflyFSystem.NflyKey`, regex settings cannot accidentally collide with source regex syntax, and invalid home paths fail eagerly. Tests should assert exact generated keys for named and default mount tables, nfly defaults, regex settings serialization, home-dir validation, and nested-mount boolean round trips.
