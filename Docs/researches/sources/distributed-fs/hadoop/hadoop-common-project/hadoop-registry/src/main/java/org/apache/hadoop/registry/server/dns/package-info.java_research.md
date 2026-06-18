# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/package-info.java

## Purpose
This package descriptor documents DNS server classes for YARN application and service discovery through the registry.

## Important APIs and types
The package contains `RegistryDNS`, `RegistryDNSServer`, service-record processors, record creators, reverse-zone helpers, and privileged daemon startup support.

## Control flow
There is no executable code. The described package flow is: observe registry service records, translate them into DNS records, and serve DNS queries.

## State and persistence behavior
The package primarily maintains in-memory DNS zones derived from persistent registry entries in ZooKeeper.

## Dependencies and integration points
It integrates xbill DNS, registry client operations, YARN service-record attributes, and Hadoop service lifecycle.

## Risks and test signals
Package-level tests should combine an embedded registry with DNS query assertions to validate end-to-end discovery behavior, including add/update/delete events.
