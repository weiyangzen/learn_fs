# sources/distributed-fs/ipfs-kubo/test/cli/dag_layout_test.go

Purpose: verifies Kubo’s default UnixFS DAG layout is balanced, while `--trickle` produces non-uniform leaf depths.

Important APIs/functions: `TestBalancedDAGLayout`, recursive `collectLeafDepths`, `IPFSAddDeterministic`, `InspectPBNode`, `cid format -f %c`, and optional CAR export via `DAG_LAYOUT_CAR_OUTPUT`.

Control flow: the balanced subtest adds a 45 MiB deterministic file and asserts all leaf depths are equal. The trickle subtest adds a similarly sized file with `--trickle` and asserts min/max leaf depths differ. The recursive walker treats raw blocks or PB nodes without links as leaves.

State/persistence: temporary daemon blockstores and optional exported CAR files.

Dependencies/integration: UnixFS importer layout selection, dag-pb inspection helpers, deterministic file generation, CID codec formatting, and refs reachable through the blockstore.

Risks/test signals: useful cross-implementation compatibility signal for IPIP-499. It is moderately expensive due to 45 MiB test vectors and recursive DAG traversal.
