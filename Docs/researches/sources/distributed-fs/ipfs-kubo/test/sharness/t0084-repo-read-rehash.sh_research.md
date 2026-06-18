## sources/distributed-fs/ipfs-kubo/test/sharness/t0084-repo-read-rehash.sh

Purpose: verifies repository read-time hash validation and `repo verify` reporting when block files are swapped or corrupted.

Important APIs and helpers: defines `test_check_bad_blocks`, uses `ipfs add --raw-leaves`, `ipfs cat`, `ipfs repo verify`, `cid-fmt`, `grep`, and daemon lifecycle helpers.

Control flow and state: creates content with multiple blocks, swaps or tampers with block files in the flatfs blockstore, confirms `ipfs cat` fails on modified data, confirms `repo verify` reports the bad multihash, then adds and reads a fresh raw-leaf block as a sanity check.

Dependencies and integration points: covers blockstore path layout, CID/multihash validation, UnixFS read path, and verify output normalization through `cid-fmt`.

Risks and test signals: catches unsafe reads that trust filenames over block bytes and verify output that omits corrupted blocks. Passing requires read failure for tampered content and matching multihash in `repo verify` output.
