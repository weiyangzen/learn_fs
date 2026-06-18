# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMasterClientPool.java

Purpose: `BlockMasterClientPool` is a bounded resource pool of `BlockMasterClient` instances for worker-to-master communication.

Important APIs are constructors, `createNewResource`, and `close`. Control flow creates a `MasterClientContext` from global configuration and optional specified master address. New resources connect either to the primary master selection policy or the specified address, add the client to a concurrent queue for later close, and return it to the pool. `close` drains all ever-created clients from the queue into a Guava `Closer`.

State and persistence are in-memory pooled clients and the queue of clients to close. Dependencies include `ResourcePool`, `MasterClientContext`, `ClientContext`, optional `InetSocketAddress`, and Guava `Closer`. Integration points include `BlockMasterSync` and all-master registration code that needs clients to primary or standby masters. Risks include the close queue tracking created clients independently of current pool ownership, so callers must still release acquired clients; pool sizing is entirely configuration-driven. No direct tests in this subset, but a visible `Factory` supports testing.
