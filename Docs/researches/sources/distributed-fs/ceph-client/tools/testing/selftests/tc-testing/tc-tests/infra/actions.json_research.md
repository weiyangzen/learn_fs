# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/infra/actions.json

Purpose: 19 infrastructure tests proving indexed tc action objects can be referenced from a matchall filter. Covered actions include pedit, mpls, bpf, connmark, csum, ct, ctinfo, gact, gate, ife, mirred, nat, police, sample, skbedit, skbmod, tunnel_key, and vlan.

APIs and control flow: Uses `$TC actions add|flush`, `$TC filter add|get`, and matchall `action <kind> index <n>`. Each case creates ingress plus an action object, binds it through a matchall filter, verifies the filter handle, and tears down action/qdisc state.

State/dependencies: State is kernel action objects keyed by kind/index and filter bindings. Requires `nsPlugin`, matchall, and all listed action modules.

Risks/test signals: Missing optional action modules can fail the file even when matchall is correct. Regexes mostly assert filter existence, not action-specific packet behavior. All cases expect exit `0`.
