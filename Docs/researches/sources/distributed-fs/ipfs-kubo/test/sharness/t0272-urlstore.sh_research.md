## sources/distributed-fs/ipfs-kubo/test/sharness/t0272-urlstore.sh

Purpose: exercises Kubo's experimental URL-backed filestore path through `ipfs add --nocopy --cid-version=1` against gateway URLs. It proves URL store entries can be created only after `Experimental.UrlstoreEnabled` is set, can be read through `ipfs get`, show up in `ipfs filestore ls`, verify with `ipfs filestore verify`, and fail once the remote gateway content disappears.

Important commands and control flow: the script creates deterministic random files, adds them normally with trickle DAGs and no raw leaves, launches an offline daemon, then uses the daemon gateway as the remote URL source. `test_urlstore` is parameterized by the add command and runs the full lifecycle: disabled-urlstore failures, enable config, URL ingest, retrieval, filestore listing/verification, GC of unpinned URL blocks, removal of original gateway content, failed verification, large-file ingest, trickle CID parity, and base32 CID output checks.

State and persistence: state spans the IPFS repo, the daemon gateway, filestore URL metadata, pins, and GC. URL-store blocks point to external URLs plus offsets, so removing the original gateway blocks turns previously valid filestore entries into verification errors and unreadable data. The test deliberately toggles daemon lifetime around config and remote availability.

Dependencies and integration points: depends on sharness helpers, `random-data`, `curl`, gateway/API ports, `ipfs add/get/cat/pin/repo gc/filestore/cid`, and Kubo's filestore/urlstore internals. It integrates CID conversion, raw-leaf UnixFS generation, trickle DAG layout, and gateway fetch behavior.

Risks and test signals: the test is sensitive to large 50 MB data generation, daemon startup timing, gateway reachability, exact `filestore ls` formatting, and CID constants. It provides strong regression signals for URL-store enablement, metadata offsets, GC behavior, retrieval through URL references, and `--cid-base=base32` output.
