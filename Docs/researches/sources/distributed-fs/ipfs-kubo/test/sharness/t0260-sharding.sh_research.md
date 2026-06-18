## sources/distributed-fs/ipfs-kubo/test/sharness/t0260-sharding.sh

Purpose: tests UnixFS HAMT-sharded directory import, access, gateway/resolve support, and behavior with incomplete sharded DAGs.

Important APIs and helpers: defines `test_add_dir`, `test_add_dir_v1`, and `test_list_incomplete_dir`; uses `ipfs add -r -Q`, `ipfs get`, `ipfs ls`, `ipfs cat`, `ipfs resolve`, `ipfs block rm`, gateway `curl`, and config `Import.UnixFSHAMTDirectorySizeThreshold`.

Control flow and state: creates 2000-file test data, forces sharding off and on to compare deterministic CIDs, checks sharded and unsharded listings match, verifies cat errors match for directories, checks `ipfs ls --resolve-type=false --size=false` tolerates missing blocks, tests gateway and `ipfs resolve` access to sharded paths, imports CIDv1 sharded dirs, tests SHA3-256/CIDv1 sharded import, removes a child block, and verifies listing reports an incomplete fetch error.

Dependencies and integration points: covers UnixFS importer sharding thresholds, HAMT traversal, gateway path resolution, resolver integration, multihash/hash-function config, and incomplete DAG error handling.

Risks and test signals: catches incorrect sharded CIDs, inability to resolve files inside shards, and over-eager metadata fetches. Signals are expected root hashes, matching listings, file content via gateway/cat, and targeted missing-block errors.
