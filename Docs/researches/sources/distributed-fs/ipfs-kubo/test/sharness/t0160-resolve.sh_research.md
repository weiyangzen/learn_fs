## sources/distributed-fs/ipfs-kubo/test/sharness/t0160-resolve.sh

Purpose: validates `ipfs resolve` over `/ipfs`, `/ipld`, and `/ipns` paths, including recursion, partial resolution, CID base preservation, and PeerID CID codec errors.

Important APIs and helpers: defines `test_resolve_setup_name`, `test_resolve`, `test_resolve_cmd`, `test_resolve_cmd_b32`, and `test_resolve_cmd_success`. Uses `ipfs add`, `ipfs dag put`, `ipfs key gen/list`, `ipfs name publish --allow-offline --ttl=0s`, `ipfs resolve`, `cid-fmt`, and daemon lifecycle helpers.

Control flow and state: prepares a nested UnixFS tree, an IPLD DAG, self and alternate IPNS keys, then checks resolution of roots and child paths. It publishes IPNS names to different targets, tests chained IPNS recursion, tests `-r=false` partial resolution, verifies recursion limit errors, and repeats base32 CID cases including a meaningful error when a PeerID is represented as CIDv1 with `dag-pb` instead of `libp2p-key`. A daemon-backed success subset runs online.

Dependencies and integration points: covers namesys cache bypass via TTL 0, UnixFS resolver, IPLD path resolver, key management, CID formatting, and daemon/offline command parity.

Risks and test signals: catches wrong terminal paths, infinite IPNS recursion, base conversion loss, and opaque codec errors. Passing requires exact resolved path strings and targeted error messages.
