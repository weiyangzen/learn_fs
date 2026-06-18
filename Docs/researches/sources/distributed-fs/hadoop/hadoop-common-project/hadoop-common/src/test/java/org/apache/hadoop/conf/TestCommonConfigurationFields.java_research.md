# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestCommonConfigurationFields.java

Purpose: configuration parity test ensuring properties declared in Hadoop Common-related configuration key classes are represented in `core-default.xml`, while allowing a curated set of XML-only or externally-owned keys.

Important APIs/classes: extends `TestConfigurationFieldsBase` and overrides `initializeMemberVariables`. Sets `xmlFilename`, `configurationClasses`, skip sets, and error modes. Configuration classes include `CommonConfigurationKeys`, `CommonConfigurationKeysPublic`, `LocalConfigKeys`, `FtpConfigKeys`, `SshFenceByTcpPort`, `LdapGroupsMapping`, `ZKFailoverController`, `SSLFactory`, `CompositeGroupsMapping`, `CodecUtil`, and `RuleBasedLdapGroupsMapping`.

Control flow: initialization chooses `core-default.xml`, enables `errorIfMissingConfigProps`, disables `errorIfMissingXmlProps`, then populates exact-property and prefix skip sets for FTP, S3A, O3, Azure/ABFS/WASB, ADL, GS, viewfs overload schemes, call queues, deprecated properties, HTTP/security/tracing/registry/private keys, and other keys owned outside the listed classes.

State and persistence: mutates inherited test configuration fields and skip sets only.

Dependencies/integration: relies on the base class to reflect constants from configuration classes and compare against XML. It guards consistency between runtime config key constants and shipped defaults.

Risks and test signals: skip lists can mask real drift if overused, while missing new classes can produce false XML-only gaps because `errorIfMissingXmlProps` is false. Tests should fail when a key constant in the listed classes lacks `core-default.xml` coverage, and maintainers should update skip reasons when moving keys between modules.
