# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_flower_cfm.sh

Purpose: tests flower classifier support for Connectivity Fault Management (CFM) fields: opcode, MD level, and combined level/opcode matching.

Important functions are `u8_to_hex`, `generate_cfm_hdr`, `match_cfm_opcode`, `match_cfm_level`, and `match_cfm_level_and_opcode`. `generate_cfm_hdr` assembles CFM header bytes from MD level, opcode, flags, and TLV offset. Setup creates two simple interfaces, clsact on H2, and caches MACs.

Control flow installs CFM protocol flower filters with handles, sends raw Ethernet frames using `$MZ` with Ethertype `0x8902` and generated headers, checks exact counters for matching and non-matching filters, and deletes filters. State is only tc filters and qdisc state plus the host interfaces. Dependencies are `tc_common.sh`, `lib.sh`, and `MZ`. Risks include raw packet formatting mistakes, tc/iproute2 support for `protocol cfm` and `flower cfm`, and repeated `pref 1` use relying on handles to distinguish filters. Test signals are exact counter values and `log_test` entries for opcode, level, and combined matches.
