# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/impl/DisabledNameserviceStoreImpl.java

Purpose: Implements `DisabledNameserviceStore`, the state-store API for marking HDFS nameservices disabled or enabled in Router-Based Federation.

Important APIs/types/functions: constructor accepts a `StateStoreDriver`; methods are `disableNameservice`, `enableNameservice`, and `getDisabledNameservices`.

Control flow: disabling creates a `DisabledNameservice` record for the nameservice id and writes it without requiring update or duplicate errors. Enabling creates the same partial record and removes it from the driver. Reads iterate cached records and return a sorted `TreeSet` of nameservice ids.

State/persistence behavior: the durable marker is presence or absence of a `DisabledNameservice` record. The read path relies on the parent store cache, so cache refresh timing affects visibility.

Dependencies/integration: integrates with admin protocol request/response classes through the abstract `DisabledNameserviceStore`, the state-store driver, and `DisabledNameservice` record type.

Risks: `disableNameservice` treats an existing marker as success/no-op because duplicate errors are disabled; stale cache can return old disabled sets; no validation of empty nameservice ids is performed here.

Test signals: disable/enable idempotency, driver remove behavior, sorted returned set, and cache refresh integration should be covered.
