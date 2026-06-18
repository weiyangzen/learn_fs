<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterProcess.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterProcess.java

## Purpose
Common base for Alluxio master processes that own a journal system, primary selector, master registry, RPC/web bind/connect addresses, simple services, and readiness checks.

## Important APIs, Types, And Functions
- Constructor configures bind/connect addresses and registers the master start time metric.
- `configureAddress` assigns a random port only in HA mode when configured port is zero.
- Abstract `createBaseRpcServer` and `createWebServer` are implemented by concrete processes.
- `createRpcExecutorService`, `getSafeModeManager`, `registerService`, `getMaster`, `getRegistry`, and address getters expose shared behavior.
- Readiness APIs poll RPC leader serving, web serving, and metrics serving.

## Control Flow
Construction resolves all service addresses before runtime starts. Services are registered by factories after process construction. Readiness methods use `CommonUtils.waitFor` with configured timeout and convert interruption/timeout to boolean results.

## State And Persistence Behavior
The class itself has no persistent storage. It holds the journal system reference that concrete subclasses start, stop, promote, and demote. Runtime state is service list, registry, addresses, and start timestamp metric.

## Dependencies And Integration Points
Integrates Alluxio process interface, journal system, primary selector, registry, simple services, RPC/web service implementations, metrics system, and network configuration utilities.

## Risks And Edge Cases
Single-master mode rejects port zero to avoid an undiscoverable master. In HA mode, random port assignment mutates global configuration. Readiness depends on service implementation type checks, so custom services must fit expected `RpcServerService`/`WebServerService` contracts.

## Test Signals
Useful signals are port validation, HA random port assignment, service readiness polling, metric registration, and registry/master lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/MasterProcess.java -->
