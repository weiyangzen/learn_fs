# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/types/yarn/PersistencePolicies.java

## Purpose
`PersistencePolicies` defines YARN-specific lifecycle strings for service records.

## Important APIs and types
Constants are `PERMANENT`, `APPLICATION`, `APPLICATION_ATTEMPT`, and `CONTAINER`. They are intended for the `yarn:persistence` attribute in `ServiceRecord`.

## Control flow
No methods are present. Runtime consumers compare service-record attributes with these policy strings or equivalent literals.

## State and persistence behavior
The policy value is persisted as a string attribute in service records. Server cleanup and DNS code use it to decide whether a record describes an application-level service or a container-level endpoint.

## Dependencies and integration points
It references `ServiceRecord` in documentation. `SelectByYarnPersistence` selects records by policy, and `RegistryDNS` treats the literal `container` as the container DNS path.

## Risks and test signals
Because policies are not enums, typoed values become silent non-matches. Tests should verify that cleanup selectors and DNS registration use the same policy string values as publishers.
