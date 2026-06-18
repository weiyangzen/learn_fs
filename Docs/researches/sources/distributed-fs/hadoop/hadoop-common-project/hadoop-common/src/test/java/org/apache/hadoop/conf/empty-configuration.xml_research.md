# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/empty-configuration.xml

## Purpose

`empty-configuration.xml` is a minimal classpath configuration resource containing an empty `<configuration>` element. It supports tests that need a syntactically valid default resource without adding properties.

## Important APIs and types

- XML declaration and Apache license comment.
- Root `<configuration>` element with no `<property>` children.
- Loaded by `Configuration.addDefaultResource` in `TestConfigurationSubclass`.

## Control flow

There is no executable control flow. When added as a default resource, Hadoop `Configuration` parses it successfully and triggers normal resource/reload mechanics while contributing no key/value pairs.

## State and persistence behavior

The file is static test data stored in the source tree. It does not persist runtime state and intentionally leaves configuration property state unchanged.

## Dependencies and integration points

The resource integrates with `Configuration` classpath resource lookup and XML parser behavior. It is particularly useful for testing reload callbacks without changing defaults.

## Risks and edge cases

- If the resource is renamed or moved, tests using the absolute classpath path `/org/apache/hadoop/conf/empty-configuration.xml` will fail.
- Even an empty resource mutates global default-resource lists when registered through `addDefaultResource`.
- XML parser changes must continue to accept empty configurations.

## Test signals

The resource's signal is successful loading with no properties and normal reload behavior. Non-empty output from this resource would indicate accidental test fixture drift.
