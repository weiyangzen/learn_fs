# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/resources/test-fake-default.xml

## Purpose
`test-fake-default.xml` is a fake Hadoop default configuration file used by unit tests around configuration defaults and deprecated-key handling.

## Important Properties
It defines `tests.fake-default.new-key=tests.fake-default.value` with a description saying it is the default value for the "new" key of a deprecated pair.

## Control Flow
Configuration tests load this resource as if it were a `*-default.xml` file and verify default lookup/deprecation behavior.

## State And Persistence
The XML is static test metadata. It contributes an in-memory default configuration entry during tests.

## Dependencies And Integration Points
It integrates with Hadoop `Configuration` tests, particularly tests of deprecation maps and default resource loading.

## Risks
Because this is a fake default resource, using it outside tests can pollute configuration namespaces. Renaming the key without updating deprecation tests would break expected old/new key mapping.

## Test Signals
Tests should verify that the new key resolves to `tests.fake-default.value` and that deprecated aliases map to the same effective value where configured.
