# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/csum.py

Purpose: Python wrapper for the generic `tools/testing/selftests/net/csum` helper, focused on NIC checksum offload RX/TX behavior.

Important APIs/functions: `NetDrvEpEnv`, `EthtoolFamily`, `test_receive()`, `test_transmit()`, `test_builder()`, `check_nic_features()`, `bkg()`, `wait_port_listen()`, remote helper deployment, and `ksft_run`.

Control flow: `main()` creates a local/remote endpoint, queries active ethtool checksum features, deploys the compiled `csum` helper remotely, dynamically builds IPv4/IPv6 RX/TX test cases, and runs them. RX tests run the local receiver while the remote sends crafted packets; TX tests run the remote verifier while the local NIC transmits offloaded packets.

State and persistence: Only transient background processes and remote-deployed helper binaries. It does not change NIC features.

Dependencies and integration points: Requires checksum offload features, remote endpoint environment, compiled `csum` helper, UDP/TCP traffic, and ethtool Netlink feature reporting.

Risks and test signals: Unsupported offloads skip relevant cases. Failures indicate checksum validation/offload regressions for TCP/UDP, invalid checksum handling, or zero UDP checksum semantics.
