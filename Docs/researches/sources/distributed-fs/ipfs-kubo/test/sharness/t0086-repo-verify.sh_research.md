## sources/distributed-fs/ipfs-kubo/test/sharness/t0086-repo-verify.sh

Purpose: tests `ipfs repo verify` on deterministic and random block corruption.

Important APIs and helpers: defines `sort_rand` and `check_random_corruption`, uses `random-files`, `ipfs add -r`, direct file corruption in `.ipfs/blocks`, `ipfs repo verify`, and backup/restore shell operations.

Control flow and state: corrupts a selected block file, asserts verify exits nonzero, restores the block, and asserts verify succeeds. It then generates a larger random directory, adds it recursively, and repeats random corruption checks to broaden block coverage.

Dependencies and integration points: covers flatfs storage layout, recursive add block generation, repo verification traversal, and failure exit codes.

Risks and test signals: catches verify false negatives, false positives after restore, and traversal gaps over larger DAGs. The key signals are nonzero status for corrupted blocks and zero status after restoring original bytes.
