<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Kconfig -->
# sources/distributed-fs/ceph-client/net/mptcp/Kconfig

## Purpose
Defines kernel configuration switches for Multipath TCP support, IPv6 support, SOCK_DIAG monitoring, and KUnit tests.

## Important APIs, Types, and Functions
`CONFIG_MPTCP` is the main boolean depending on `INET`; it selects `SKB_EXTENSIONS`, `CRYPTO_LIB_SHA256`, and `CRYPTO_LIB_UTILS`. `CONFIG_INET_MPTCP_DIAG` follows `INET_DIAG` and enables MPTCP sock-diag support. `CONFIG_MPTCP_IPV6` gates IPv6 MPTCP support when IPv6 is built-in. `CONFIG_MPTCP_KUNIT_TEST` builds MPTCP crypto/token tests.

## Control Flow
There is no runtime flow. The file controls compile-time inclusion: the rest of the MPTCP objects are considered only inside `if MPTCP`, and tests default to `KUNIT_ALL_TESTS` when requested.

## State and Persistence
Configuration state persists in the kernel build configuration. It controls whether MPTCP code, diagnostics, IPv6 branches, and KUnit modules exist in the compiled kernel.

## Dependencies and Integration Points
Integrates with the top-level networking Kconfig and the local `Makefile`. The selected crypto and skb extension options are required by `crypto.c`, option parsing, and skb MPTCP extension storage.

## Risks
The `MPTCP_IPV6` dependency is `IPV6=y`, so module-style IPv6 combinations are intentionally excluded. Missing selected crypto/skb extensions would cause compile or runtime failures in MPTCP option handling. Test config should remain non-production by default.

## Test Signals
Build matrix signals include `CONFIG_MPTCP=n`, MPTCP IPv4-only builds, IPv6-enabled builds, `INET_MPTCP_DIAG=m/y`, and `MPTCP_KUNIT_TEST=m/y` with KUnit execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/Kconfig -->
