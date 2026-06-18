## sources/distributed-fs/ipfs-kubo/test/sharness/t0087-repo-robust-gc.sh

Purpose: validates that `ipfs repo gc` handles missing, unreadable, and corrupted blocks without deleting protected data incorrectly.

Important APIs and helpers: defines `to_raw_cid`, `test_gc_robust_part1`, and `test_gc_robust_part2`; uses `random-data`, `ipfs add`, `ipfs refs -r`, `ipfs cat`, `ipfs pin rm`, `ipfs block rm`, `repo gc --stream-errors`, `cid-fmt`, `dd`, `chmod`, and direct block file lookup.

Control flow and state: creates multiblock data, maps root and leaf CIDs to block files, deletes one leaf, checks reads fail but GC still completes when safe, corrupts a protected root and requires GC to abort without sweeping, tests permission-denied block deletion, then repeats with multiple missing/corrupt blocks and `--stream-errors` to ensure separate errors are reported.

Dependencies and integration points: covers GC error aggregation, mark phase failure safety, block removal permissions, raw CID formatting, and blockstore integrity checks.

Risks and test signals: prevents GC from turning read corruption into data loss. Passing signals include aborted GC on corrupt pinned roots, preserved accessible leaves, partial cleanup only after unpin, and streamed error diagnostics for multiple failures.
