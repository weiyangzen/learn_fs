<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryConstants.java

## Purpose

Central registry/DNS/ZooKeeper configuration key and default-value contract. The source was read as a complete 388-line file for this research item.

## Important APIs, Types, and Functions

Defines configuration/path constants such as `KEY_DNS_ENABLED`, `DEFAULT_DNS_ENABLED`, `KEY_DNS_DOMAIN`, `KEY_DNS_BIND_ADDRESS`, `KEY_DNS_PORT`, `DEFAULT_DNS_PORT`, `KEY_DNSSEC_ENABLED`, `KEY_DNSSEC_PUBLIC_KEY`, `KEY_DNSSEC_PRIVATE_KEY_FILE`, `DEFAULT_DNSSEC_PRIVATE_KEY_FILE`, `KEY_DNS_ZONE_SUBNET`, `KEY_DNS_ZONE_MASK`, `KEY_DNS_ZONE_IP_MIN`, `KEY_DNS_ZONE_IP_MAX`, and more.

## Control Flow

Includes prefixes, DNS bind/zone/DNSSEC keys, registry security/auth keys, ZK quorum/retry/session keys, ACL defaults, and canonical path fragments.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `InterfaceAudience`, `InterfaceStability`. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Key stability is high-risk because configs, tests, and deployed clusters depend on literal strings.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/api/RegistryConstants.java -->
