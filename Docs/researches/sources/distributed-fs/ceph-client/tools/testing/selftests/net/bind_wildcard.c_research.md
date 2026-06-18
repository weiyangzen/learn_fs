# sources/distributed-fs/ceph-client/tools/testing/selftests/net/bind_wildcard.c

Purpose: Exhaustive matrix test for IPv4/IPv6 wildcard, loopback, v4-mapped, and `IPV6_V6ONLY` TCP bind conflict behavior, with and without `SO_REUSEADDR`/`SO_REUSEPORT`.

Important APIs/types/functions: Uses many fixture variants encoding two initial bind addresses, expected errno arrays for eight follow-up bind targets, optional `IPV6_V6ONLY`, and tests `plain`, `reuseaddr`, and `reuseport`. Helpers include `setup_addr()` and `bind_socket()`.

Control flow: Fixture prepares two variant-defined addresses and six canonical test addresses (`0.0.0.0`, `127.0.0.1`, `::`, `::1`, `::ffff:0.0.0.0`, `::ffff:127.0.0.1`). Each test iterates all eight binds on the same ephemeral port, sets v6-only/reuse options where applicable, binds, and checks success or `EADDRINUSE` against the variant's expected matrix. The first successful bind fixes the port via `getsockname()`.

State and persistence behavior: Uses up to eight socket descriptors per test. Kernel bind table conflict state is the target. No persistent files.

Dependencies and integration points: Requires IPv4, IPv6, v4-mapped address behavior, and kselftest harness.

Risks: Large variant matrix is maintenance-heavy; expectations encode Linux semantics in detail. Teardown closes all fd slots even if some were never assigned after failed setup paths.

Test signals: Passing across all variants demonstrates correct bind conflict resolution for wildcard/local/v4mapped/v6only combinations and reuse options.
