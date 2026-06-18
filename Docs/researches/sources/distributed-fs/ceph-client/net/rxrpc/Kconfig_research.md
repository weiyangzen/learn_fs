# sources/distributed-fs/ceph-client/net/rxrpc/Kconfig

## Purpose
Defines build-time configuration for AF_RXRPC session sockets, IPv6 support, packet loss/delay injection, dynamic debugging, security classes, and the rxperf test service.

## Important APIs, Types, and Functions
Top-level `AF_RXRPC` is tristate and depends on `INET`, selecting crypto, keys, and UDP tunnel support. Nested options include `AF_RXRPC_IPV6`, `AF_RXRPC_INJECT_LOSS`, `AF_RXRPC_INJECT_RX_DELAY`, `AF_RXRPC_DEBUG`, `RXKAD`, `RXGK`, and `RXPERF`.

## Control Flow
Kconfig controls object inclusion in the Makefile and feature guards in source. Security options select required crypto algorithms. Delay injection depends on sysctl; IPv6 support depends on kernel IPv6.

## State and Persistence
No runtime state. Configuration persists in the kernel build.

## Dependencies and Integration
Integrates AF_RXRPC with AFS use cases, key retention, crypto providers, UDP networking, proc/sysctl diagnostics, and optional performance testing.

## Risks and Test Signals
Risks include missing crypto dependencies for security modes, feature code not compiled under common configs, and stale help text claiming incomplete support. Test signals are allmodconfig/allnoconfig coverage, module builds with and without IPv6, RXKAD/RXGK crypto link checks, and sysctl availability when injection options are enabled.
