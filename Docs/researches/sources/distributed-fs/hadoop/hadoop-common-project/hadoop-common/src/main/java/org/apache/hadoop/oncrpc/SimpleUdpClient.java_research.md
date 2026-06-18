# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/oncrpc/SimpleUdpClient.java

Purpose: blocking UDP client for sending a single XDR RPC request and validating an accepted reply.

Important APIs/types/functions: constructors and `run`.

Control flow: resolves host, serializes request bytes, uses a provided `DatagramSocket` or creates one, sends a packet, sets receive timeout, receives up to 65535 bytes, parses an `RpcReply`, and throws if reply state is not accepted. It closes only sockets it created.

State and persistence: stores host, port, request, one-shot flag, optional socket, and timeout; no persistence. `oneShot` is stored but not used in control flow.

Dependencies and integration: used by `RpcProgram` to register/unregister with local portmap.

Risks: timeout applies to the shared caller-provided socket too. It only checks reply state, not xid or accept state. Large UDP responses above buffer size would truncate at datagram level.

Test signals: portmap registration and UDP server tests cover request/response behavior and timeout configuration.
