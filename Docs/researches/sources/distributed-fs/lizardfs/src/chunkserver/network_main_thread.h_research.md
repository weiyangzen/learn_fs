# sources/distributed-fs/lizardfs/src/chunkserver/network_main_thread.h

## Purpose
`network_main_thread.h` declares the chunkserver network listener module API.

## Important APIs, Types, and Functions
`mainNetworkThreadInit()` sets up listener configuration and event-loop callbacks. `mainNetworkThreadInitThreads()` creates worker objects and threads. `mainNetworkThreadGetListenIp()` and `mainNetworkThreadGetListenPort()` expose the advertised chunkserver service address.

## Control Flow
The init table calls normal initialization before master connection, then calls thread initialization in the late phase. Master registration later queries the listen address through this header.

## State and Persistence Behavior
No state is stored in the header. The implementation owns runtime sockets and workers and does not persist data directly.

## Dependencies and Integration Points
This header includes platform and integer types only. It is consumed by `init.h` and `masterconn.cc`.

## Risks and Edge Cases
The address getters are only meaningful after successful `mainNetworkThreadInit`. Calling them too early could expose default/uninitialized globals from the implementation.

## Test Signals
Startup-order tests should verify listener initialization precedes master registration. Address tests should verify configured host/port resolution is reflected by getters.
