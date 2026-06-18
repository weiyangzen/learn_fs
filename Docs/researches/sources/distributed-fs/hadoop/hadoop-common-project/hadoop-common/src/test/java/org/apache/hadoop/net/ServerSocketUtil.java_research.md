# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/ServerSocketUtil.java

## Purpose
Utility for tests that need available TCP ports or need to wait until a port is released.

## Important APIs, Types, And Functions
Provides `getPort(int port, int retries)`, private `isPortAvailable(int)`, `waitForPort(int, int)`, and `getPorts(int)`.

## Control Flow
`getPort()` tries a requested port or random port in `[port, 65535)`, binds a loopback `ServerSocket`, returns the successful port, and retries on `IOException`. `waitForPort()` polls once per second until binding succeeds or retries are exhausted. `getPorts()` opens `numPorts` ephemeral sockets, records their assigned ports, then closes all sockets.

## State And Persistence Behavior
State is a static `Random` and transient sockets. Returned ports are not reserved after the method returns.

## Dependencies And Integration Points
Used by tests that need low-collision ports for daemons or sockets. Depends on Java networking and loopback binding.

## Risks
All methods suffer TOCTOU races: another process can bind returned ports after sockets are closed. `getPort(0, ...)` randomizes from zero but skips zero. `isPortAvailable()` binds all interfaces, while `getPort()` binds loopback only, so semantics differ.

## Test Signals
Useful signals are successful bind/close with logged selected ports, retry failure throwing the last `IOException`, and `getPorts()` returning unique ports during its reservation window.
