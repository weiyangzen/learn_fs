# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/YarnRegistryAttributes.java

## Purpose
`YarnRegistryAttributes` defines YARN-specific attribute keys used inside `ServiceRecord.attributes`.

## Important APIs and types
The class is final with a hidden constructor. Constants include `YARN_ID`, `YARN_PERSISTENCE`, `YARN_PATH`, `YARN_HOSTNAME`, `YARN_IP`, and `YARN_COMPONENT`.

## Control flow
There are no methods. Consumers call `ServiceRecord.get()` with these keys.

## State and persistence behavior
These keys are persisted as JSON attributes on service records. DNS processors use them to generate container names, reverse records, and persistence-category routing. Cleanup selectors use ID and persistence for record selection.

## Dependencies and integration points
The class is used by `RegistryDNS`, `ContainerServiceRecordProcessor`, `SelectByYarnPersistence`, and any YARN publisher or cleaner interacting with the registry.

## Risks and test signals
Missing attributes can cause processors to skip records, log warnings, or throw runtime exceptions. Tests should cover complete and incomplete YARN records, especially `yarn:ip`, `yarn:hostname`, `yarn:id`, `yarn:component`, and `yarn:persistence`.
