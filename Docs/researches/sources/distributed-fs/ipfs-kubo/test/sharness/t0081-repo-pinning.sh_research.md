## sources/distributed-fs/ipfs-kubo/test/sharness/t0081-repo-pinning.sh

Purpose: focuses on recursive, direct, indirect, and no-pin behavior across nested UnixFS directories and GC.

Important APIs and helpers: defines `test_pin_flag` and `test_pin`, uses `ipfs add -r`, `ipfs cat`, `ipfs dag get`, `ipfs pin ls/add/rm`, `ipfs repo gc`, `jq`, and daemon lifecycle helpers.

Control flow and state: builds a nested directory tree, records file and directory CIDs, verifies recursive root pin and indirect child pins, runs GC and confirms all reachable data remains, removes recursive pins, adds a mix of direct and recursive pins, then verifies GC removes unprotected subtrees while preserving directly or indirectly protected blocks. It also verifies failed recursive pinning does not remove existing direct pins and checks `--pin=false` for files and dirs.

Dependencies and integration points: covers pinset invariants, DAG link reachability, GC mark/sweep behavior, UnixFS DAG structure through `dag get`, and error handling for missing blocks.

Risks and test signals: catches pin classification bugs and dangerous rollback behavior after failed pin attempts. Signals are pin list content, cat/ls success or failure after GC, and expected no-pin absence from pin sets.
