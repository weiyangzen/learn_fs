# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-nfs/src/main/java/org/apache/hadoop/mount/MountdBase.java

## Purpose
`MountdBase.java` is the abstract base for starting and stopping the Hadoop mountd daemon that serves the NFS mount protocol over UDP and TCP.

## Important APIs, Types, and Functions
- Constructor stores the `RpcProgram` that handles mount requests.
- `getRpcProgram()` exposes the program.
- `start(boolean register)` starts UDP and TCP servers, optionally registers both transports with portmap, and installs a shutdown hook.
- `stop()` unregisters bound UDP/TCP ports and shuts down both servers.
- Private `startUDPServer()` and `startTCPServer()` construct `SimpleUdpServer`/`SimpleTcpServer`, start program daemons, run servers, capture bound ports, and terminate the process on startup failure.
- `Unregister` shutdown hook calls `stop()` with priority `10`.

## Control Flow and State
State includes `rpcProgram`, bound UDP/TCP ports, and server instances. Startup begins UDP, then TCP, then registers with portmap if requested. Failure during server startup unregisters any partially registered transport, shuts down the server, and calls `ExitUtil.terminate(1, e)`.

## Dependencies and Integration Points
It depends on Hadoop ONCRPC `RpcProgram`, `SimpleUdpServer`, `SimpleTcpServer`, portmap `PortmapMapping`, `ShutdownHookManager`, SLF4J, and `ExitUtil`. Concrete mount daemons subclass this base with an implementation-specific `RpcProgram`.

## Risks and Edge Cases
`rpcProgram.startDaemons()` is called once for UDP and once for TCP startup; implementations must tolerate that. Startup failure is fatal. `stop()` unregisters regardless of whether `start(register)` was called with registration enabled, but only if bound ports are positive.

## Test Signals
No direct test in this subset. Integration tests should verify port registration/unregistration, dual transport startup, and shutdown hook behavior.
