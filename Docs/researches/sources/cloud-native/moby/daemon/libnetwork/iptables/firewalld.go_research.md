# sources/cloud-native/moby/daemon/libnetwork/iptables/firewalld.go

## Purpose
Integrates Docker's iptables programming with Linux firewalld over D-Bus. It detects firewalld, applies Docker zone/policy setup, proxies iptables calls through firewalld passthrough, and reacts to reload signals.

## Important APIs, Types, And Functions
- `Conn` stores D-Bus connection, runtime/config objects, and signal channel.
- `UsingFirewalld` and `FirewalldReloadedAt` expose current integration status.
- `firewalldInit`, `newConnection`, `signalHandler`, `dbusConnectionChanged`, `connectionEstablished`, `connectionLost`, `reloaded`, and `OnReloaded` manage lifecycle and callbacks.
- `checkRunning` probes service availability.
- `passthrough` calls `direct.passthrough`.
- `firewalldZone.settings`, `setupDockerZone`, and `setupDockerForwardingPolicy` create permanent Docker firewalld configuration.
- `AddInterfaceFirewalld` and `DelInterfaceFirewalld` manage runtime interface membership in the Docker zone.
- `interfaceNotFound` marks not-found errors.

## Control Flow
Initialization honors `DOCKER_TEST_NO_FIREWALLD`, connects to the system bus, checks running state, starts a signal handler when connected, ensures the `docker` zone and forwarding policy exist, and reloads firewalld if configuration was added. Reload signals invoke registered callbacks under a mutex and update an atomic timestamp.

## State And Persistence
Global process state tracks connection, running flag, callbacks, and last reload time. Persistent firewalld config is modified by adding the Docker zone and forwarding policy. Runtime zone interfaces are modified through D-Bus.

## Dependencies And Integration Points
Uses `github.com/godbus/dbus/v5`, containerd logging, and package-local iptables passthrough. `iptables.Raw` uses firewalld passthrough when `firewalldRunning` is true.

## Risks
Global mutable state and asynchronous D-Bus signals are concurrency-sensitive. Some operations ignore unknown-method or name-conflict errors for compatibility. Firewalld running in the host namespace is skipped in rootless mode by `iptables.go`. Runtime interface deletion returns a typed not-found error.

## Test Signals
`firewalld_test.go` runs only when D-Bus/firewalld are available. It tests initialization, reload callback recreation of rules, and passthrough add/delete.
