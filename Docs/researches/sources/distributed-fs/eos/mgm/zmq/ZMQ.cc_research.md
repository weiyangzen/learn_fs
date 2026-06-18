## sources/distributed-fs/eos/mgm/zmq/ZMQ.cc

Purpose: Implements the MGM ZeroMQ proxy used by the FUSE server path. It binds a ROUTER frontend, fans messages to in-process DEALER workers, parses FUSE heartbeat protobufs, and feeds `FuseServer::Server`.

Important APIs and functions: `ZMQ::ServeFuse` creates and detaches the task thread. `Task::run` configures sockets, keepalives, backend, injector, and worker threads before entering `zmq::proxy`. `Task::reply` injects replies to a client identity. `Worker::work` reads multipart messages and dispatches heartbeat/statistics.

Control flow: frontend receives client identity plus protobuf payload; the proxy sends work to workers over `inproc://backend`; workers parse `eos::fusex::container`, compute heartbeat clock delta, dispatch heartbeat and statistics to `gFuseServer.Client()`, and log unknown or unparseable messages.

State and persistence: state is process-local: a ZMQ context/sockets, detached worker threads, and the static `gFuseServer`. No durable persistence is performed.

Dependencies and integration: uses `zmq.hpp`, FUSE protobufs, MGM FuseServer, common timing/logging/string-to-hex utilities, and XRootD mutex for reply serialization.

Risks: worker threads are detached and allocated with `new`; workers delete themselves only on `ETERM`, while `Task` deletes thread objects but cannot join them. The worker constructor allocation is passed directly into detached thread creation, so startup failures could leak. `Task::reply` relies on a static mutex for injector socket safety.

Test signals: integration test socket bind/proxy startup, heartbeat parse and delta computation, statistics forwarding, malformed multipart handling, unparseable payload logging, reply framing, and clean shutdown on context close.
