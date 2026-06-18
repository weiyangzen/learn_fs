# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ip_local_port_range.sh

Purpose: Wrapper that runs `ip_local_port_range` in an isolated namespace with required sysctl setup.

Important commands: Invokes `./in_netns.sh` and inside it enables `net.mptcp.enabled=1`, sets `net.ipv4.ip_local_port_range` to `40000 49999`, then executes `./ip_local_port_range`.

Control flow: A single shell command chain is passed to the namespace wrapper. With `set -e` inherited by `in_netns.sh`, any sysctl or test failure fails the wrapper.

State and persistence: Only temporary netns sysctls are changed. No file state.

Dependencies and integration: Depends on `in_netns.sh`, `sysctl`, MPTCP sysctl availability, and the compiled test binary.

Risks: Kernels without MPTCP sysctl support may fail before reaching protocol-specific skip or xfail behavior. The wrapper hardcodes the ephemeral range assumed by the C tests.

Test signals: Exit zero from the C harness after sysctls are applied.
