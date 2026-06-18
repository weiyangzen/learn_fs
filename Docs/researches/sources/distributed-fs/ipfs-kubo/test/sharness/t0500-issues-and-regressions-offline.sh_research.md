## sources/distributed-fs/ipfs-kubo/test/sharness/t0500-issues-and-regressions-offline.sh

Purpose: offline regression collection for historical Kubo issues around stdin handling, help commands, large stdin adds, and `ipfs refs -e` output.

Important commands and control flow: verifies `ipfs init` works when stdin is occupied, `ipfs cat --help` and `ipfs pin ls --help` return under a timeout while stdin remains open, adds a 1 MiB random stream from stdin, runs recursive refs with edge output, and compares first-level refs extracted from edge output against `ipfs refs`.

State and persistence: initializes a repo, stores a 1 MiB object, and generates temporary hash/ref output files.

Dependencies and integration points: depends on command stdin behavior, timeout helper, UnixFS add, refs traversal, and edge formatting.

Risks and test signals: catches command hangs when stdin is open, regressions in refs output shape, and large stdin add failures. There is a typo in the test description text ("woks"), but it does not affect behavior.
