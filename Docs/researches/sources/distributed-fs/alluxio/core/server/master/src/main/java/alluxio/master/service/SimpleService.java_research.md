# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/SimpleService.java

Purpose: common lifecycle contract for master-adjacent services such as RPC, web, metrics sinks, and JVM monitoring.

Important APIs/types/functions: `start`, `promote`, `demote`, and `stop`. The Javadoc defines intended state transitions between standby and primary behavior.

Control flow: master process starts services in standby state, calls `promote` on gaining primacy, calls `demote` on losing primacy, and calls `stop` during shutdown. Concrete services decide whether promotion changes runtime behavior.

State and persistence: interface carries no state; implementations are responsible for idempotency or precondition checks. No persistence contract is included.

Dependencies/integration: referenced by master service factories and `AlluxioMasterProcess` service registration.

Risks: lifecycle preconditions are documented but not enforced by the interface. Implementations differ: some tolerate repeated stop, while RPC standby service rejects double promotion/demotion.

Test signals: lifecycle tests should verify concrete implementations against the documented contract, especially start-before-promote, demote-only-after-promote, and stop idempotency.
