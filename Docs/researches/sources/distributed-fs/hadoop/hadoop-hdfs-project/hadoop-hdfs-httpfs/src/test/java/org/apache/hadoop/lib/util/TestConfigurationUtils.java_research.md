# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/util/TestConfigurationUtils.java

Purpose: Unit tests for `ConfigurationUtils` loading, copying, default injection, and variable resolution.

Important APIs/types/functions: `ConfigurationUtils.load`, `copy`, `injectDefaults`, and `resolve`; tests also use compact XML resource `test-compact-format-property.xml`.

Control flow: load tests parse standard Hadoop XML and compact `<property name value>` XML from streams/resources. Copy overwrites target keys from source while preserving target-only keys. Inject defaults fills only missing target keys. Resolve creates a new configuration with raw `${a}` references resolved. Variable resolution confirms Hadoop `Configuration.get` resolves config and system properties while raw values remain unresolved until explicit resolve.

State and persistence: in-memory configurations plus a classpath resource stream.

Dependencies/integration: Hadoop `Configuration`, Java streams, and classloader resources.

Risks and test signals: useful signal for config migration/compatibility. It does not test malformed XML, close behavior, or duplicate keys.
