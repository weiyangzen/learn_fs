# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/package-info.java

Purpose: Package-level overview of the Router-Based Federation state store and its APIs.

Important APIs/types/functions: documents shared persistent values, serialized `BaseRecord` rows, pluggable `StateStoreDriver`, `StateStoreService`, and main APIs: `MembershipStore`, `MountTableStore`, `RouterStore`, and `DisabledNameserviceStore`.

Control flow: no runtime behavior; it defines conceptual flow from routers through API interfaces to driver-backed persistent records.

State/persistence behavior: explains that the state store tracks records shared by multiple routers and serializes them with a modular serializer, defaulting to protobuf.

Dependencies/integration: links package users to driver, service, record, and API packages.

Risks: text contains a typo in protobuf and may omit newer stores or protocol extensions; conceptual docs should be kept in sync with implementation support.

Test signals: Javadoc build and link validation.
