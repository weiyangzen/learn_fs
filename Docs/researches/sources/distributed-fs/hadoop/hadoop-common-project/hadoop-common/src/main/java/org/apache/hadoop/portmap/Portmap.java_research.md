# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/portmap/Portmap.java

Purpose: standalone portmap/rpcbind service entry point for binding RPC program/version/transport tuples to ports.

Important APIs/types/functions: `main`, `start`, `shutdown`, test-visible address getters, and `getHandler`.

Control flow: `main` starts TCP and UDP listeners on port 111. `start` creates Netty boss/worker/UDP groups, configures a TCP pipeline with RPC frame decoder, parser, idle handler, portmap handler, and TCP response stage, configures a UDP pipeline with logging, parser, handler, and UDP response stage, binds both addresses, stores channels, and adds them to a channel group. `shutdown` closes all channels and shuts down groups.

State and persistence: process-local Netty bootstraps, channel group, channels, event loops, and one `RpcProgramPortmap` handler. Port mappings live in the handler only and are not persisted.

Dependencies and integration: depends on `RpcUtil`, `RpcProgramPortmap`, Netty, and `RpcProgram.RPCB_PORT`. Used by tests and can run as a daemon.

Risks: class is package-private final. Shutdown assumes groups were initialized. Binding privileged port 111 requires appropriate permissions. UDP and TCP maps are shared through one handler.

Test signals: `TestPortmap` covers startup on test ports, handler access, set/unset/get/dump behavior, and shutdown.
