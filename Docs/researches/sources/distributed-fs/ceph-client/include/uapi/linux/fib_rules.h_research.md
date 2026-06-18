# sources/distributed-fs/ceph-client/include/uapi/linux/fib_rules.h

This header defines the rtnetlink ABI for policy routing/FIB rules. It describes rule messages, rule actions, flags, and nested attributes used to create, inspect, and delete routing rules.

Important exports include `struct fib_rule_hdr`, actions such as `FR_ACT_TO_TBL`, `FR_ACT_GOTO`, `FR_ACT_NOP`, `FR_ACT_BLACKHOLE`, `FR_ACT_UNREACHABLE`, and `FR_ACT_PROHIBIT`, flags such as `FIB_RULE_PERMANENT`, `FIB_RULE_INVERT`, `FIB_RULE_UNRESOLVED`, and attribute IDs `FRA_DST`, `FRA_SRC`, `FRA_IIFNAME`, `FRA_GOTO`, `FRA_PRIORITY`, `FRA_FWMARK`, `FRA_FLOW`, `FRA_TUN_ID`, `FRA_SUPPRESS_IFGROUP`, `FRA_SUPPRESS_PREFIXLEN`, `FRA_TABLE`, `FRA_FWMASK`, `FRA_OIFNAME`, `FRA_PAD`, `FRA_L3MDEV`, `FRA_UID_RANGE`, `FRA_PROTOCOL`, `FRA_IP_PROTO`, `FRA_SPORT_RANGE`, `FRA_DPORT_RANGE`, and `FRA_DSCP`.

Control flow is rtnetlink based: userspace sends `RTM_NEWRULE`, `RTM_DELRULE`, or `RTM_GETRULE`; kernel validates `fib_rule_hdr` plus attributes, inserts/deletes rules in priority order, and lookup code evaluates rules during route resolution. State is persistent in the running network namespace until deleted or namespace teardown; it is not on disk unless userspace network configuration persists it externally.

Dependencies include rtnetlink, route tables, network namespaces, l3mdev/VRF, mark/UID/protocol/port selectors, and address-family-specific FIB implementations. Integration points are `ip rule`, systemd-networkd, NetworkManager, container networking, VRFs, policy routing, and firewall marking.

Risks include rule priority conflicts, unsupported selector combinations, goto loops/unresolved references, namespace-specific behavior, and ABI extension mistakes in `FRA_*` numbering. Test signals include rtnetlink policy-rule selftests, `ip rule` roundtrip tests, route lookup tests with marks/ports/UID ranges/VRF, namespace isolation tests, and netlink attribute fuzzing.
