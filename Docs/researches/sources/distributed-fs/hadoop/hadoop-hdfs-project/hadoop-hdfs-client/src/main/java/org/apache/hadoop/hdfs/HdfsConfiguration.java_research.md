# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/HdfsConfiguration.java

`HdfsConfiguration` is the HDFS-specific `Configuration` subclass that registers HDFS default resources and deprecated key mappings.

Its constructors mirror `Configuration`. The static initializer calls `addDeprecatedKeys()` before adding `hdfs-default.xml`, `hdfs-rbf-default.xml`, `hdfs-site.xml`, and `hdfs-rbf-site.xml`. `init()` intentionally does nothing except force class loading. `main()` dumps deprecated keys.

Class loading mutates global `Configuration` registries for default resources and deprecations; instances are normal mutable configurations. Dependencies are `HdfsClientConfigKeys`, `DeprecatedKeys`, and core Hadoop configuration APIs. HDFS client classes call `HdfsConfiguration.init()` to ensure key mappings and resources are available before lookup.

Risks are mostly compatibility and ordering: deprecations must be registered before defaults load, the static initializer only runs once per classloader, and missing mappings can break old configuration files silently. Test signals include `init()` class-loading behavior, expected default resources, old-to-new key translation for representative keys, constructor behavior, and `main()` dump execution.
