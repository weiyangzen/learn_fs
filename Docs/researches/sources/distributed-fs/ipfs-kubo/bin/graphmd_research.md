# sources/distributed-fs/ipfs-kubo/bin/graphmd

## Purpose
This shell utility emits Graphviz DOT edges for the recursive MerkleDAG references under an IPFS path.

## Important APIs, Types, And Functions
It calls `ipfs refs -r --format="$fmt"` with node and edge templates, wraps output in `digraph { ... }`, and suggests piping to `dot`.

## Control Flow
The script requires exactly one IPFS path argument, prints usage otherwise, then emits graph attributes and indented edge lines.

## State And Persistence Behavior
It is read-only against the daemon/blockstore and writes DOT to stdout.

## Dependencies And Integration Points
It integrates `ipfs refs`, Graphviz, and recursive DAG traversal.

## Risks And Test Signals
Risks include large DAG output volume and needing a running API for `ipfs refs`. Signal is valid DOT renderable by `dot`.
