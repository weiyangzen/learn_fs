# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/meta/checkconf/ConfigurationStoreTest.java

Purpose: tests registration and node-loss bookkeeping for configuration records.

Important APIs/types/functions: uses `ConfigurationStore`, `ConfigRecord`, gRPC `ConfigProperty`, `PropertyKey`, and wire `Address`.

Control flow: setup creates two property lists using real known keys (`ZOOKEEPER_ELECTION_PATH`, `WORKER_FREE_SPACE_TIMEOUT`) with different values and two random addresses. `registerNewConf` registers both nodes and verifies both appear in the config map. `registerNewConfUnknownProperty` registers `unknown.property` and verifies the store preserves an unknown key name rather than dropping the record. `detectNodeLost` removes one address and verifies the other remains. `lostNodeFound` removes both, then marks one found and verifies only that node returns to the config map.

State and persistence behavior: state is an in-memory mapping from addresses to lists of config records plus lost-node tracking used to restore records when a node is found again.

Dependencies and integration points: supports configuration checker inputs and master node lifecycle notifications.

Risks: tests map membership but not record value/source equality for known properties. Random ports/hosts are fine because equality is object-value based.

Test signals: useful signal that configuration reports survive unknown keys and correctly react to node loss/recovery events.
