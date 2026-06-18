## sources/distributed-fs/ipfs-kubo/test/sharness/t0271-filestore-utils.sh

Purpose: tests `ipfs filestore` utility commands for listing, verification, missing/changed file detection, bad-block removal, and duplicate reporting.

Important APIs and helpers: defines `test_init_filestore`, `test_init_dataset`, `test_init`, `test_filestore_adds`, `test_filestore_state`, `test_filestore_verify`, `test_filestore_rm_bad_blocks`, and `test_filestore_dups`. Uses `ipfs add --raw-leaves --nocopy`, `ipfs filestore ls`, `filestore verify`, `verify --remove-bad-blocks`, `filestore dups`, `ipfs cat`, `random-data`, `dd`, and daemon lifecycle helpers.

Control flow and state: initializes filestore-enabled repos and deterministic datasets, adds files by reference, validates root hash and utility listing order, reads referenced files, verifies all entries, renames a source file to simulate missing data, restores it, corrupts source bytes to simulate changed data, removes bad blocks with verify, and checks duplicate detection. The suite runs across configured command contexts through `$IPFS_CMD`.

Dependencies and integration points: covers filestore metadata persistence, source file path tracking, block verification against external files, block removal side effects, duplicate block mapping, and daemon/offline command routing.

Risks and test signals: catches stale references, false verification success after external mutation, unsafe bad-block removal, and unstable listing order. Signals are exact `filestore ls/verify` output, failed `cat` for missing/changed backing files, successful reads after restore, and duplicate reports.
