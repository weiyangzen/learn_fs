## sources/distributed-fs/ipfs-kubo/test/sharness/t0250-files-api.sh

Purpose: large integration suite for the Mutable File System `ipfs files` API, covering mkdir, ls, stat, cp, read, write, rm, mv, flush, CID/hash config, sharding, and automatic shard/unshard behavior.

Important APIs and helpers: defines `restart_daemon`, `create_files`, `verify_path_exists`, `verify_dir_contents`, `test_sharding`, `test_files_api`, `tests_for_files_api`, and `test_add_large_sharded_dir`. Uses `ipfs files mkdir/ls/stat/cp/read/write/rm/mv/flush/chcid`, `ipfs add`, `ipfs repo gc`, `ipfs config Import.CidVersion`, `Import.HashFunction`, `Import.UnixFSHAMTDirectorySizeThreshold`, `cid-fmt`, `pollEndpoint`, daemon lifecycle helpers, and `dd`.

Control flow and state: runs the API matrix offline and daemon-backed. It creates fixture CIDs, checks root/default ls, stat formats and `--with-local`, rejects invalid root operations, copies immutable `/ipfs` content into MFS, validates long listings and base32 CIDs, reads with offsets/counts, writes with create/offset/truncate/raw-leaves/parents/flush flags, checks no-flush behavior against daemon API, moves directories, removes files and dirs including force and multiple-target cases, tests `chcid`, and validates root CID changes under import config. It then enables HAMT sharding, verifies sorted and unsorted listings, file reads and pins within sharded dirs, and tests automatic sharding/unsharding of a large directory near the threshold.

Dependencies and integration points: covers MFS DAG mutation, UnixFS importer settings, root persistence, daemon flush semantics, CID version/hash-function propagation, HAMT directory implementation, local refs visibility, and GC interaction.

Risks and test signals: catches high-blast-radius MFS regressions: corrupted root updates, wrong hashes, bad sparse writes, path creation mistakes, force removal semantics, daemon/offline divergence, and shard threshold errors. Signals are exact expected root/file hashes, byte-for-byte reads, directory listings, command failure codes, and sharded directory CIDs.
