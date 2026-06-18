# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/team/decoupled_enablement.sh

Purpose: Verifies independent `tx_enabled` and `rx_enabled` behavior for team member ports across team modes.

Important APIs/functions: Uses `team_lib.sh` `setup_team`, forwarding `lib.sh`, `teamnl setoption`, `tcpdump_start/stop/show/cleanup`, namespace setup, and ping. Local helpers include `environment_create`, `set_option_value`, `try_ping`, `did_interface_receive_icmp`, `team_test_mode_tx_enablement`, and `team_test_mode_rx_enablement`.

Control flow: Parses optional `-4` to switch from IPv6 to IPv4, then creates two namespaces connected by a veth pair and team devices. For each tested mode, it sets up sender/receiver teams and runs three scenarios for TX and RX: initially enabled ping succeeds, disabling one side causes ping failure, and re-enabling restores connectivity. Tcpdump distinguishes whether packets were transmitted when RX was disabled.

State and persistence: Creates namespaces, veth, team devices, IP addresses, team member options, and tcpdump captures. `trap cleanup_all_ns EXIT` removes namespaces.

Dependencies and integration: Requires team kernel modes, `teamnl`, `ping`, `tcpdump`, iproute2, and forwarding/team libraries. Default IPv6 uses `nodad`; IPv4 mode adjusts prefixes.

Risks: The receiver team is prepared once while sender teams are recreated per mode, so cleanup between modes depends on helper behavior. Packet capture timing can affect ICMP detection. Single-member topology tests enablement semantics, not load distribution.

Test signals: TX disabled should prevent packet transmission; RX disabled should still transmit packets but ping should fail; re-enabling each option should restore ping for all modes tested.
