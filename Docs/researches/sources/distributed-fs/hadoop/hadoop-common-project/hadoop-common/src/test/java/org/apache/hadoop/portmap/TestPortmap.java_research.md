# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/portmap/TestPortmap.java

Purpose: Integration tests for Hadoop's ONC/RPC portmap service over TCP and UDP.

Important APIs/types/functions: `Portmap`, `pm.start`, `pm.shutdown`, `getTcpServerLocalAddress`, `getUdpServerLoAddress`, `RpcCall.getInstance`, `RpcProgramPortmap`, `PortmapMapping`, `DatagramSocket`, `RpcReply.read`, and `PortmapMapping.key`.

Control flow: `@BeforeAll` starts a `Portmap` with short timeout on ephemeral localhost TCP/UDP addresses. `testIdle` connects a TCP socket and expects the server to disconnect idle clients. `testRegistration` sends a UDP PMAPPROC_SET request with a serialized mapping, reads the UDP reply, checks `MSG_ACCEPTED`, sleeps briefly, and verifies the handler map contains the registered mapping.

State and persistence: live portmap server, handler mapping table, UDP/TCP sockets, and per-instance xid counter.

Dependencies/integration points: Netty/simple RPC server internals, localhost networking, XDR, ONC/RPC security `CredentialsNone` and `VerifierNone`.

Risks: live network timing and fixed short timeouts can be flaky; handler map is inspected directly; UDP receive timeout is environmental.

Test signals: confirms idle TCP cleanup, UDP registration response, and mutation of the portmap registry.
