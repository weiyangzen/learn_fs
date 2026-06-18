# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/tc_chains.sh

Purpose: tests tc chain behavior for flower filters: unreachable chains, `goto chain`, chain create/show/delete JSON output, and template enforcement. It runs in software and optionally offload mode.

Important functions are `unreachable_chain_test`, `gact_goto_chain_test`, `create_destroy_chain`, and `template_filter_fits`. Setup creates two hosts, clsact on H2, captures MAC addresses, and checks chain support with `check_tc_chain_support`. `create_destroy_chain` uses `tc -j chain` plus `jq` to verify chain IDs.

Control flow adds filters in non-default chains, sends one packet with `$MZ`, checks whether counters did or did not increment, validates chain lifecycle commands, then tests that filters must match per-chain templates. State is tc chains/templates/filters and host VRFs. Risks include iproute2 JSON differences, template cleanup when insertions intentionally fail, and offload behavior under `skip_sw`. Test signals are exact counter expectations for default vs chain 1 filters, `jq` selection success, expected failures for template-mismatched filters, and repeated execution after `tc_offload_check`.
