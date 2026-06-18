# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/mptcp_connect.sh

## Purpose
This shell test builds a four-namespace routed topology and uses `mptcp_connect` to validate MPTCP transfers over loopback, multi-hop IPv4/IPv6 paths, TCP fallback combinations, checksum mode, peek mode, MPTFO, transparent proxying, and full disconnect/reconnect.

## Important APIs and Functions
Setup code creates namespaces `ns1` to `ns4`, veth links, IPv4/IPv6 addresses, forwarding, optional checksum sysctls, random or requested ethtool feature changes, and netem loss/delay/reorder. Helpers include `cleanup`, `set_ethtool_flags`, `set_random_ethtool_flags`, `check_mptcp_disabled`, `do_ping`, `do_transfer`, `make_file`, `run_tests_lo`, `run_tests`, `run_test_transparent`, `run_tests_peekmode`, `run_tests_mptfo`, `run_tests_disconnect`, `display_time`, `log_if_error`, and `stop_if_error`.

## Control Flow and State
The script parses options for delay/loss/reorder, capture, file size, buffer sizes, transfer mode, TCP coverage, IPv4-only mode, and MPTCP checksums. It validates MPTCP can be disabled by sysctl, pings all namespace addresses, installs tc qdiscs, then runs transfer matrices. `do_transfer` starts a listener and connector, applies timeouts, optionally starts tcpdump, captures nstat counters before/after, compares transferred files both directions, and validates MPTCP counters such as MPCapable SYN/ACK, fallback, checksum errors, syncookie counters, and OoO notes.

## Dependencies and Integration
It depends on `mptcp_lib.sh`, `mptcp_connect`, `ip`, `tc`, `ethtool`, `nft` for transparent proxy cases, `tcpdump` when capture is enabled, `dd`, `/dev/urandom`, kernel MPTCP counters, and namespace/routing support. Wrapper scripts in this subset call it with `-C`, `-m mmap`, `-m sendfile`, or `-m splice`.

## Risks and Test Signals
The test intentionally randomizes file size, netem, and offload toggles unless fixed by options, which improves coverage but can affect reproducibility. Packet capture creates `.pcap` files when enabled. Transparent proxy and MPTFO cases are skipped if kernel support is absent. Pass signals are per-transfer TAP results, bidirectional file equality, expected MPTCP counter deltas, no checksum errors, and final zero `final_ret`.
