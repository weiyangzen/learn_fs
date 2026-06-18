# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ping.py

Purpose: Provides baseline data-plane connectivity tests for driver environments across IPv4, IPv6, TCP, checksum offload states, and XDP modes.

Important APIs/functions: Uses `NetDrvEpEnv`, `EthtoolFamily`, command helpers, `socat`, and BPF object `xdp_dummy.bpf.o`. Helpers `_test_v4`, `_test_v6`, and `_test_tcp` send ping/TCP traffic both directions. Setup helpers toggle checksum offloads and XDP generic/native/offload single-buffer and multi-buffer modes.

Control flow: Main creates endpoint environment, gathers interface info, resets MTU/XDP state, then runs default IPv4/IPv6 tests and XDP variants. Each case disables/enables checksum offload around ping and TCP transfer checks. XDP modes adjust MTUs and defer restoration.

State and persistence: Mutates MTU, XDP programs, checksum offload flags, and remote endpoint listener processes. Deferred cleanup restores offload and link settings.

Dependencies and integration: Requires local/remote endpoint from `NetDrvEpEnv`, `socat`, ethtool, iproute2 XDP attach support, bpftool-compatible BPF object, and optional offload support for native/offloaded cases.

Risks: Uses broad `except` in checksum/offload setup, so unsupported toggles may be silently ignored. Real devices need sleeps for XDP propagation; netdevsim/veth skip that delay. Shell `echo` of random strings assumes no hostile characters beyond lowercase.

Test signals: PASS means bidirectional small and large ping works, 64 KiB TCP payloads match exactly, and the same connectivity holds under each supported checksum/XDP configuration.
