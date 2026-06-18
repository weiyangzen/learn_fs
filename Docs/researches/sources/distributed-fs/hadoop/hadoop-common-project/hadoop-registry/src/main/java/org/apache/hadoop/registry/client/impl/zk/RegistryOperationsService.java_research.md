# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/impl/zk/RegistryOperationsService.java

## Purpose
`RegistryOperationsService` implements the public `RegistryOperations` API on top of `CuratorService`. It is the bridge from logical registry operations and JSON service records to ZooKeeper znodes.

## Important APIs and types
The class extends `CuratorService` and implements `RegistryOperations`. Public operations are `mknode`, `bind`, `resolve`, `exists`, `stat`, `list`, and `delete`. It uses `RegistryUtils.ServiceRecordMarshal` for JSON bytes, `RegistryTypeUtils.validateServiceRecord` for validation, `BindFlags.OVERWRITE`, `RegistryPathStatus`, and client ACLs from `RegistrySecurity`.

## Control flow
`mknode` validates the path and calls `zkMkPath` with persistent mode and client ACLs. `bind` validates the path and record, marshals the `ServiceRecord`, and calls `zkSet` with overwrite controlled by flags. `resolve` reads bytes from ZooKeeper, unmarshals and validates the record. `stat` converts ZooKeeper `Stat` into a registry-facing `RegistryPathStatus` using last path entry, creation time, data length, and child count.

## State and persistence behavior
All persistence is ZooKeeper znode persistence below the registry root. Bound records are persistent znodes containing marshalled JSON. The service does not add application-level version checks around updates, so last writer wins when overwrite is enabled.

## Dependencies and integration points
It depends on `CuratorService`, registry API interfaces, bind flags, registry path/type utilities, ZooKeeper `CreateMode` and `Stat`, and ACLs from `RegistrySecurity`. It is used directly by registry clients and by `RegistryDNSServer` for watching and resolving records.

## Risks and test signals
`validatePath` currently performs no checks, so path correctness depends on lower-level utilities and ZooKeeper. `bind` validates before writing, so tests should include invalid service record rejection, overwrite/no-overwrite behavior, resolve round trips, stat field mapping, and ACL behavior in secure mode. Race behavior in inherited `zkSet` should be tested with concurrent binders if correctness matters.
