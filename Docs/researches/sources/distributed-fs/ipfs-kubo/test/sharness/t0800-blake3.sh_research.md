## sources/distributed-fs/ipfs-kubo/test/sharness/t0800-blake3.sh

Purpose: validates BLAKE3 multihash support across block, DAG, UnixFS add, and cat paths.

Important commands and control flow: defines known raw CIDs for `foo\n` using 32, 64, and 128 byte BLAKE3 digests. It runs `ipfs block put --mhtype=blake3 --cid-codec=raw` with default and explicit digest lengths, verifies `block get`, runs `ipfs dag put --hash=blake3` with raw codecs and `dag get`, then adds a raw-leaf file with `--hash=blake3` and checks `ipfs cat`.

State and persistence: stores raw blocks and UnixFS content in the local repo. No daemon is needed.

Dependencies and integration points: depends on multihash BLAKE3 registration, digest-length handling, raw codec, DAG command path, UnixFS add hash selection, and hard-coded CID constants.

Risks and test signals: catches missing BLAKE3 support, digest-length mishandling, CID generation changes, and read path incompatibilities. The comments warn that newline handling changes will produce different known hashes.
