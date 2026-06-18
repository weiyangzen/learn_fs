# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/impl/MembershipStoreImpl.java

Purpose: Implements the `MembershipStore` API for Namenode membership heartbeats, active namespace discovery, expired registration access, and manual Namenode state updates.

Important APIs/types/functions: implements `StateStoreCache`; maintains `activeNamespaces`, `activeRegistrations`, `expiredRegistrations`, and read/write locks. Key methods are `namenodeHeartbeat`, `loadCache`, `getNamenodeRegistrations`, `getExpiredNamenodeRegistrations`, `getNamespaceInfo`, `updateNamenodeRegistration`, and private `getRepresentativeQuorum`.

Control flow: heartbeats write the supplied `MembershipState` to the driver with updates allowed. `loadCache` refreshes cached records, splits expired records from active candidates, builds namespace info for non-unavailable registrations, groups registrations by Namenode key, and picks a representative record per Namenode using majority state when possible or newest record otherwise. Query methods read from the protected in-memory maps and return protocol responses.

State/persistence behavior: persisted state lives in driver `MembershipState` records; this class derives an in-memory, lock-protected view for router reads. `updateNamenodeRegistration` mutates only the active cache entry state and does not write it back to the state-store driver.

Dependencies/integration: integrates with resolver types `FederationNamenodeServiceState` and `FederationNamespaceInfo`, protocol request/response factories, `StateStoreUtils.filterMultiple`, and the parent cached `MembershipStore`.

Risks: cache-only updates can be overwritten by the next load; quorum fallback to newest record can hide disagreement; a null representative is possible for empty groups though groups are built from records; lock scope protects maps but not external mutation of returned `MembershipState` objects.

Test signals: tests should verify heartbeat writes, expired segregation, namespace suppression for unavailable state, quorum majority and no-majority fallback, partial-membership filtering, sorted registration responses, and cache-only update semantics.
