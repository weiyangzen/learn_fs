## sources/distributed-fs/ipfs-kubo/test/sharness/t0095-refs.sh

Purpose: validates `ipfs refs` traversal ordering, recursion depth, uniqueness, edge formatting, and base conversion over a directory DAG with repeated subtrees.

Important APIs and helpers: defines `test_refs_output`, uses `ipfs add -r -Q`, `ipfs refs`, `test_cmp`, optional filtering/sorting, and daemon lifecycle helpers.

Control flow and state: builds a directory tree with repeated names and content, adds it recursively, records the root, and compares `ipfs refs` output under combinations of recursive traversal, `--unique`, `--edges`, `--max-depth`, and CID base options. It checks both offline and daemon-backed execution.

Dependencies and integration points: covers DAG traversal, UnixFS directory links, recursive ref emission, duplicate suppression, depth limiting, edge output formatting, and CID formatting.

Risks and test signals: catches nondeterministic refs output, broken depth handling, duplicate filtering mistakes, and edge-format regressions. Passing requires exact expected ref lists for each option set.
