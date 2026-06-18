# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/xdp_features.c

## Purpose

This userspace test validates that a netdev's advertised XDP feature flags match behavior detected by traffic. It can run as a device-under-test service or as a tester peer, coordinates over a TCP control channel, sends UDP echo traffic, attaches generated XDP skeleton programs, and reports whether a selected feature is detected and advertised.

## Important APIs, Types, and Functions

The global `env` stores verbosity, interface, tester/DUT role, selected `netdev_xdp_act`/`xdp_action`, and socket addresses. Key functions are `get_xdp_feature`, `get_xdp_feature_str`, `parse_arg`, `set_env_default`, `dut_echo_thread`, `dut_run_echo_thread`, `dut_attach_xdp_prog`, `recv_msg`, `dut_run`, `tester_collect_detected_cap`, `send_and_recv_msg`, `send_echo_msg`, `tester_run`, and `main`. It uses `xdp_features.skel.h`, `xdp_features.h`, libbpf XDP attach/query APIs, cpumap/devmap updates, and `network_helpers`.

## Control Flow

`main` initializes defaults, parses CLI options, opens/loads/attaches the skeleton, seeds rodata addresses, then branches into DUT or tester mode. The DUT accepts one control connection, handles TLV commands for start/stop/capability/stats, attaches an XDP program matching the requested feature, starts a UDP echo thread, and returns BPF map stats. The tester queries advertised features, attaches a receive/tx-check program, asks the DUT to start, sends echo datagrams repeatedly, fetches DUT stats, stops the DUT, and compares detected behavior with advertised flags.

## State and Persistence Behavior

State is process-local except for temporary XDP attachments and BPF maps inside the loaded skeleton. Signal handling sets `exiting`; cleanup destroys the skeleton and detaches XDP in role-specific paths.

## Dependencies and Integration Points

It depends on libbpf strict mode, skeleton-generated BPF programs/maps, IPv6 or IPv4-mapped IPv6 sockets, cpumap/devmap support, netdev XDP feature querying, and the shared TLV protocol in `xdp_features.h`.

## Risks and Test Signals

Risks include network timing, uninitialized address length/state bugs, driver-only mode limitations, stale XDP attachments on abnormal exit, and feature mismatch caused by traffic not reaching the BPF path. Signals are successful control handshake, XDP attach/query, nonzero DUT/tester map counters when expected, and final `[DETECTED]/[ADVERTISED]` comparison for each feature.
