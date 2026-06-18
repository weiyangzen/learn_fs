# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/TestGangliaSink.java

## Purpose
Tests `GangliaSink30` socket creation and server-list configuration.

## Important APIs, Types, And Functions
Uses `GangliaSink30.init()`, `getDatagramSocket()`, `getMetricsServers()`, `ConfigBuilder`, `DatagramSocket`, and `MulticastSocket`.

## Control Flow
Tests initialize the sink with default config, explicit `multicast=false`, explicit `multicast=true`, multicast TTL override, and a comma-separated servers property. Assertions inspect socket type, multicast TTL, and server count.

## State And Persistence Behavior
State is in the sink's configured socket and metrics server list. No external persistence.

## Dependencies And Integration Points
Exercises Ganglia metrics sink config parsing and Java networking socket classes.

## Risks
Sockets opened by `init()` are real OS resources. Multicast socket behavior and TTL APIs may vary in restricted environments.

## Test Signals
Default and disabled multicast should produce a non-multicast `DatagramSocket`; enabled multicast should produce `MulticastSocket` with TTL 1 or configured 3; two configured servers should parse into two targets.
