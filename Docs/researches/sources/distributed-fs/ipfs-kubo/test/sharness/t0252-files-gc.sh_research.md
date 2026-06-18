## sources/distributed-fs/ipfs-kubo/test/sharness/t0252-files-gc.sh

Purpose: verifies garbage collection preserves blocks reachable from MFS and handles incomplete directories safely.

Important APIs and helpers: uses `ipfs files write/mkdir/cp/read/stat`, `ipfs repo gc`, `ipfs cat`, `ipfs dag get`, `ipfs pin add`, `ipfs add --pin=false`, and `test_cmp`.

Control flow and state: writes `/hello.txt` through MFS and confirms GC does not remove it, reads it back, creates directories and direct pins, runs GC with incomplete nodes, adds an unpinned directory whose file can be removed by GC, copies the directory into MFS while missing content, then restores content and verifies GC preserves it once reachable. State is the MFS root, direct pins, unpinned blocks, and incomplete DAG links.

Dependencies and integration points: covers GC mark roots from MFS, direct pin interaction, DAG completeness checks, and UnixFS directory reachability.

Risks and test signals: catches data loss for MFS roots or GC crashes on incomplete MFS/directory state. Signals are successful `files read`/`cat` for protected blocks and expected failure for unprotected removed content.
