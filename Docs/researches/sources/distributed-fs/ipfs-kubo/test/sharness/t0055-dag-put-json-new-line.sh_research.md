## sources/distributed-fs/ipfs-kubo/test/sharness/t0055-dag-put-json-new-line.sh

Purpose: regression test ensuring JSON put as CBOR retrieves without an added trailing newline.

Important control flow: creates JSON files with and without trailing newline, runs `ipfs dag put` as CBOR, asserts both hashes are equal and match the expected value, then retrieves by hash and verifies the output has no trailing newline.

State and dependencies: writes tiny JSON fixtures and stores a CBOR DAG block in the repo. Depends on `ipfs dag put/get`, codec normalization, and exact expected CID.

Risks: newline normalization is subtle and user-visible for byte-sensitive DAG data. Test signal is equal CIDs for equivalent JSON input and retrieval bytes without an extra newline.
