# sources/distributed-fs/ceph-client/tools/testing/selftests/net/cmsg_so_mark.sh

Purpose: this script validates `SO_MARK` supplied either through `setsockopt` or through cmsg (`SCM_MARK` via `SO_MARK`) by proving that marked packets match a policy-routing rule and are rejected by a prohibit route.

Important APIs and commands: it uses `setup_ns`, `cleanup_ns`, namespace-local `ip rule add fwmark`, IPv4 and IPv6 prohibit routes in table 300, and `./cmsg_sender` options `-M` for setsockopt mark and `-m` for cmsg mark.

Control flow: the script creates one namespace, enables ping socket groups, creates a dummy interface with IPv4 and IPv6 addresses, and installs fwmark rules for both families. For each option source (`setsock`, `cmsg`, `both`), address family, and protocol (`u`, `i`, `r`), it first sends with `MARK + 1` and expects success, then sends with `MARK` and `-s` silent mode and expects sender return code 1 due to the prohibit route.

State and persistence: state is namespace-local link, addresses, rules, and routes. It is removed by the exit trap. No files are written.

Dependencies and integration points: depends on kernel support for `SO_MARK` cmsg handling, `cmsg_sender`, raw/ICMP/UDP socket support, and privilege to set marks and rules.

Risks and test signals: the script includes a dormant `diff` branch assignment that is never used because the `ovr` loop omits `diff`; that is harmless but suggests the matrix was reduced. Strong signals are the two return-code classes for every protocol/family/source combination.
