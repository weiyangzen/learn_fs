# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/tools/TestHdfsConfigFields.java

## Purpose
`TestHdfsConfigFields` compares HDFS configuration key constants against `hdfs-default.xml` so missing constants or missing XML properties are detected, with an explicit skip list for deprecated, generated, internal, native, or cross-module properties.

## Important APIs, types, and functions
- The class extends `TestConfigurationFieldsBase`.
- `initializeMemberVariables()` sets `xmlFilename`, `configurationClasses`, error modes, `configurationPropsToSkipCompare`, `xmlPropsToSkipCompare`, and `xmlPrefixToSkipCompare`.
- Configuration classes include `HdfsClientConfigKeys` and nested groups, plus `DFSConfigKeys`.

## Control flow
The base class invokes `initializeMemberVariables`, reflects configuration key fields from listed classes, loads `hdfs-default.xml`, applies exact and prefix skip sets, and fails on missing properties according to enabled error modes.

## State and persistence behavior
The test builds in-memory sets only. It does not persist files.

## Dependencies and integration points
It integrates HDFS client/server config key classes with the default XML resource. It also encodes knowledge of deprecated keys, NFS module ownership, native FUSE keys, HTrace remnants, and dynamically generated NameNode edits-plugin keys.

## Risks and edge cases
Skip lists can become stale and hide missing coverage or produce false positives after config movement. Both `errorIfMissingConfigProps` and `errorIfMissingXmlProps` are true, so adding a key in either Java or XML usually requires updating the other or the skip list.

## Test signals
Passing indicates Java constants and `hdfs-default.xml` are aligned for user-visible HDFS config properties, except for documented skips.
