# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/ServiceRecordProcessor.java

## Purpose
`ServiceRecordProcessor` defines the contract for turning a registry `ServiceRecord` into DNS records managed by a `RegistryDNS.RegistryCommand`.

## Important APIs and types
Methods are `initTypeToInfoMapping(ServiceRecord)`, `getRecordTypes()`, and `manageDNSRecords(RegistryDNS.RegistryCommand)`.

## Control flow
Implementations initialize record descriptors from a service record, advertise valid DNS record types, and later execute add/remove commands for generated records. `BaseServiceRecordProcessor` provides the shared implementation for `manageDNSRecords`.

## State and persistence behavior
The interface has no state. Implementations normally hold transient descriptor state and mutate in-memory DNS zones through commands.

## Dependencies and integration points
It depends on `ServiceRecord`, `IOException`, and `RegistryDNS.RegistryCommand`. `RegistryDNS.op()` depends on this abstraction to choose application versus container processing.

## Risks and test signals
Implementations must make descriptor generation symmetric for add and remove. Tests should exercise the interface through `RegistryDNS.register` and `delete`, ensuring generated record identity is stable enough for removal.
