## sources/distributed-fs/ipfs-kubo/test/sharness/t0040-add-and-cat.sh

Purpose: broad sharness coverage for `ipfs add` and `ipfs cat` across files, directories, stdin, mount paths, raw leaves, wrapping, dereference behavior, named pipes, symlinked working directories, large/expensive data, and offline only-hash behavior.

Important helpers and control flow: `test_add_cat_file`, `test_add_cat_5MB`, `test_add_cat_raw`, `test_add_cat_derefargs`, `test_add_cat_expensive`, `test_add_named_pipe`, `test_add_pwd_is_symlink`, and `add_directory` generate content, run add variants, capture hashes, cat content back, and compare expected output. The script launches a daemon with mounts for FUSE cases, checks help text, stdin behavior, recursive directory output, CID version validation, and then separately verifies `--only-hash` cannot be catted from an offline daemon.

State and dependencies: writes many fixture files/directories, uses `.ipfs` repo/blockstore/pins, daemon/FUSE mounts, random-data, and shell comparison helpers.

Risks: high coverage but high timing/platform sensitivity around FUSE, named pipes, random data, and daemon lifecycle. Test signals are exact hashes/output, successful cat byte comparisons, expected failures for invalid CID version and absent only-hash blocks.
