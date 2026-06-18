# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/integration/SelectByYarnPersistence.java

## Purpose
`SelectByYarnPersistence` is a `RegistryAdminService.NodeSelector` implementation that selects service records matching a specific YARN ID and persistence policy.

## Important APIs and types
Constructor arguments are `id` and `targetPolicy`, both required non-empty. `shouldSelect(String, RegistryPathStatus, ServiceRecord)` compares `serviceRecord.get(YARN_ID, "")` and `serviceRecord.get(YARN_PERSISTENCE, "")` to the configured values.

## Control flow
Registry admin cleanup code can instantiate this selector and pass candidate paths/status/records through `shouldSelect`. Only records with both matching ID and matching persistence policy are selected.

## State and persistence behavior
The selector stores immutable match criteria. It does not mutate registry state; `RegistryAdminService` would perform deletes for selected nodes.

## Dependencies and integration points
It depends on Apache Commons `StringUtils`, Hadoop `Preconditions`, `RegistryPathStatus`, `ServiceRecord`, `YarnRegistryAttributes`, and `RegistryAdminService.NodeSelector`.

## Risks and test signals
The path and status parameters are ignored, so selection is purely attribute-based. Tests should verify constructor validation, missing attributes returning false, exact string matching, and integration with admin cleanup deletion flows.
