# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/RpcProgram.java

Purpose: abstract Netty handler base for ONC RPC server programs. It validates program/version, handles portmap registration, sends standard errors, and delegates valid calls to subclass logic.

Important APIs/types/functions: constructors, `register`, `unregister`, protected `register(PortmapMapping, boolean)`, `startDaemons`, `stopDaemons`, `channelRead`, `doPortMonitoring`, `sendRejectedReply`, abstract `handleInternal`, abstract `isIdempotent`, `getPort`, and `getPortmapUdpTimeoutMillis`.

Control flow: `register`/`unregister` build a `PortmapMapping` for every supported version and send UDP portmap requests. `channelRead` casts to `RpcInfo`, releases request data in finally, validates program number and version, sends accepted error replies for mismatch, then calls `handleInternal`. `doPortMonitoring` rejects unprivileged client ports unless allowed.

State and persistence: stores program metadata, configured/current port, version range, registration socket, timeout, and insecure-port policy; no durable state.

Dependencies and integration: used by RPC services and `SimpleTcpServer`. Depends on Netty, portmap helpers, `RpcAcceptedReply`, `RpcDeniedReply`, `RpcUtil`, and `VerifierNone`.

Risks: registration failures throw runtime exceptions. Port monitoring must be called by subclasses; base validation does not enforce it automatically. `channelRead` assumes parser produced `RpcInfo`.

Test signals: server and portmap tests cover mismatch replies, registration request construction, and insecure-port logic.
