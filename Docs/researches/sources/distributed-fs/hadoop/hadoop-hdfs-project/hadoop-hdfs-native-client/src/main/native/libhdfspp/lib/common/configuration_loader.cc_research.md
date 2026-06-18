<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.cc

## Purpose
Implements `ConfigurationLoader`, which searches Hadoop configuration directories, validates XML resources, and overlays property maps from files, streams, strings, or direct key/value settings.

## Important APIs, Types, And Functions
Important functions include `SetDefaultSearchPath`, `ClearSearchPath`, `SetSearchPath`, `AddToSearchPath`, `GetSearchPath`, `ValidateResources`, `UpdateMapWithFile`, `UpdateMapWithStream`, `UpdateMapWithString`, `UpdateMapWithBytes`, and `UpdateMapWithValue`. Helpers parse boolean `final` values and validate streams with RapidXML.

## Control Flow
The constructor seeds the search path from `$HADOOP_CONF_DIR` or `/etc/hadoop/conf`. Loading opens absolute paths directly or walks the search path for relative names. XML parsing requires a `<configuration>` root, then scans `<property>` children supporting both nested `<name>/<value>/<final>` nodes and attribute forms. Overlay writes uppercase keys unless an existing entry is marked final.

## State And Persistence
The loader stores only `search_path_`. Parsed maps are local copies used to construct immutable `Configuration`/`HdfsConfiguration` instances. No files are modified.

## Dependencies And Integration Points
Depends on RapidXML, `Status`, logging, and x-platform case-insensitive bool comparison. It is used by the C builder, `ConfigParser`, and `HdfsConfiguration` default loading.

## Risks
The search path separator is always `:`, even on Windows while file separator changes. Stream length is stored in `int`, which is unsuitable for very large files. Parse errors in normal load paths collapse to `false` without detailed `Status`. Final-value rejection returns false for that individual property but the caller often treats the overall file load as successful.

## Test Signals
Tests should cover env/default search paths, colon path parsing, absolute and relative file lookup, empty and invalid XML validation, property node and attribute styles, final overwrite prevention, multiple default resources, and Windows path behavior if supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/configuration_loader.cc -->
