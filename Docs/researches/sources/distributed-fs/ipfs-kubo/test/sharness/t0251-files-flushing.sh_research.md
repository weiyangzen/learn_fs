## sources/distributed-fs/ipfs-kubo/test/sharness/t0251-files-flushing.sh

Purpose: focused test for MFS flush persistence after copying content into files.

Important APIs and helpers: defines `verify_path_exists` and `verify_dir_contents`, uses `ipfs add`, `ipfs files cp`, `ipfs files ls`, and daemon lifecycle helpers.

Control flow and state: starts a daemon, adds a small file, copies it from `/ipfs/<hash>` into `/file` in MFS, and verifies the path exists/listing is correct. The relevant state is the flushed MFS root and file entry.

Dependencies and integration points: covers MFS root mutation through daemon, flushing to repo state, and immutable-to-mutable file copy.

Risks and test signals: catches writes that appear in memory but do not flush/persist. Passing requires `ipfs files ls` and path existence checks to see `/file` after the copy.
