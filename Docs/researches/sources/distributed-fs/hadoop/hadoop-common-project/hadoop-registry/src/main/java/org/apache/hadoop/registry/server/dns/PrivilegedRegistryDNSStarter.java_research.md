# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/server/dns/PrivilegedRegistryDNSStarter.java

## Purpose
`PrivilegedRegistryDNSStarter` is an Apache Commons Daemon entry point that lets Registry DNS bind a privileged port before dropping into normal service launch.

## Important APIs and types
It implements `Daemon` with `init`, `start`, `stop`, and `destroy`. State includes `Configuration conf`, `RegistryDNS registryDNS`, and `RegistryDNSServer registryDNSServer`.

## Control flow
`init()` parses daemon arguments into a `RegistryConfiguration`, validates that `KEY_DNS_PORT` is in the privileged range 1-1023, creates a `RegistryDNS`, and calls `initializeChannels(conf)` early. `start()` launches `RegistryDNSServer` with the pre-initialized `RegistryDNS`. `destroy()` stops the launched server.

## State and persistence behavior
It creates socket/channel state in `RegistryDNS` before full server startup. It does not persist registry data.

## Dependencies and integration points
It integrates Commons Daemon, `DNSOperationsFactory`, `RegistryConfiguration`, generic Hadoop options, registry DNS constants, and `RegistryDNSServer.launchDNSServer`.

## Risks and test signals
The port check rejects non-privileged ports, so this starter is not a general launcher. `stop()` is empty while `destroy()` stops the service, which may matter to daemon containers. Tests should validate privileged-port guard behavior, early channel initialization idempotence, and cleanup when `init()` partially fails.
