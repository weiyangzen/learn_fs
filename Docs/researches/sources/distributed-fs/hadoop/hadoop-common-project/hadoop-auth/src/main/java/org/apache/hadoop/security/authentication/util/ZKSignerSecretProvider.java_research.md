<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZKSignerSecretProvider.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZKSignerSecretProvider.java

## Purpose
Synchronizes rolling signer secrets across multiple servers through a ZooKeeper znode so load-balanced Hadoop Auth instances can validate each other's cookies.

## Important APIs, types, and functions
Configuration constants cover connection string, znode path, auth type, Kerberos keytab/principal, TLS keystore/truststore settings, custom Curator client sharing, and disconnect behavior. `init()` obtains or creates a Curator client, creates the znode if absent, pulls shared data, and schedules rollover aligned with the znode timestamp. `rollSecret()` shifts local secrets, advances `nextRolloverDate`, proposes new znode data, and pulls the winning next secret. `generateZKData()` serializes data version, next/current/previous secret lengths and values, and next rollover time. `pullFromZK()` parses znode data and znode version. `createCuratorClient()` delegates to `ZookeeperClient`.

## Control flow
On startup, every instance attempts to create the secret znode; one wins, others read existing data. Writes use ZooKeeper version checks so concurrent rollovers let one server's proposal win. New servers compute initial delay from the stored next rollover date, advancing by token-validity intervals if the date is already in the past.

## State and persistence
Persistent state is the znode payload containing secrets and next rollover time. Local state includes `nextSecret`, `zkVersion`, `nextRolloverDate`, `tokenValidity`, Curator client, disconnect policy, and inherited current/previous secrets.

## Dependencies and integration points
Extends `RolloverSignerSecretProvider`, uses Curator/ZooKeeper APIs, `ZookeeperClient`, servlet context custom-client attribute, and filter configuration. It integrates with `AuthenticationFilter` as a shared signer provider.

## Risks and test signals
Secrets are stored raw in ZooKeeper, so ACL/TLS/SASL configuration is critical. `pullFromZK()` logs and swallows unexpected parse/read failures, which can leave stale or null `nextSecret`. Rollover timing depends on local clocks. Tests should cover first creator vs joiner, BadVersion races, corrupt/newer znode data, missing path, custom Curator lifecycle, disconnect flag, TLS/SASL config propagation, delayed startup after missed rollovers, and cookie verification across instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/ZKSignerSecretProvider.java -->
