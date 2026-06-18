# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/config

## Purpose
This file declares kernel configuration requirements for the MPTCP selftest suite.

## Important Entries
It requires core MPTCP (`CONFIG_MPTCP`, `CONFIG_MPTCP_IPV6`), diagnostic modules (`CONFIG_INET_DIAG`, `CONFIG_INET_MPTCP_DIAG`), IPv6 and advanced routing, multiple routing tables, veth, netfilter/nftables/xtables support, BPF match, netem/ingress qdisc, pedit/csum actions, syncookies, and kallsyms.

## Control Flow and State
There is no executable control flow. The selftest framework uses these symbols to document or validate required kernel features.

## Dependencies and Integration
It supports scripts such as `mptcp_connect.sh`, `diag.sh`, and related MPTCP tests that need namespaces, routing, netfilter, tc, and MPTCP diagnostics.

## Risks and Test Signals
Missing symbols usually cause runtime skips or failures rather than direct config-file execution errors. The config is broad because the MPTCP suite tests transport, path manager, diagnostics, filtering, and failure behavior.
