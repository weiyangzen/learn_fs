# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/nfs/nfs3/Nfs3Base.java

## Purpose
`Nfs3Base.java` is the abstract base for starting and stopping an NFSv3 server over TCP.

## Important APIs, Types, and Functions
- Constructor stores `RpcProgram` and logs configured port.
- `getRpcProgram()` exposes the program.
- `start(boolean register)` starts the TCP server and optionally registers the NFSv3 TCP service with portmap and a shutdown hook.
- `startTCPServer()` constructs `SimpleTcpServer`, starts program daemons, runs the server, captures bound port, and terminates on failure.
- `stop()` unregisters the bound TCP port, stops program daemons, and shuts down the TCP server.
- `NfsShutdownHook` calls `stop()` with shutdown hook priority 10.

## Control Flow and State
State includes the `RpcProgram`, bound NFS port, and `SimpleTcpServer`. The server supports TCP only; UDP is deliberately not started.

## Dependencies and Integration Points
It depends on Hadoop ONCRPC server classes, portmap registration, `ShutdownHookManager`, SLF4J, and `ExitUtil`. Concrete NFS daemons subclass it with protocol-specific `RpcProgram` implementations.

## Risks and Edge Cases
Startup failure terminates the process. Registration happens after server startup, so a failure to register leaves a running server only until `terminate()` exits. `stop()` unregisters whenever a positive bound port exists.

## Test Signals
Integration tests should verify TCP binding, portmap registration/unregistration, daemon lifecycle, and no UDP registration for NFSv3.
