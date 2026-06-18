## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-git.sh

Purpose: validates the git IPLD codec plugin by importing raw git objects and traversing decoded DAG structures.

Important commands and control flow: extracts a fixture repository archive, then `test_dag_git` finds git object files and stores them using `ipfs dag put --store-codec=git-raw --input-codec=0x300078 --hash=sha1`. It reads every produced hash with `ipfs dag get`, checks a known tag object JSON, and traverses paths through author, tree file hash, and nested parent/tree entries.

State and persistence: fixture git objects become IPFS DAG blocks in the test repo. The test runs once offline and once with a daemon, reusing the same logical object graph.

Dependencies and integration points: relies on plugin codec registration, git raw codec number, SHA-1 multihash support, `ipfs dag put/get`, tar fixtures, and path traversal through IPLD selectors.

Risks and test signals: catches missing git plugin support, codec-number changes, JSON representation drift, SHA-1 allowance issues, and path traversal regressions.
