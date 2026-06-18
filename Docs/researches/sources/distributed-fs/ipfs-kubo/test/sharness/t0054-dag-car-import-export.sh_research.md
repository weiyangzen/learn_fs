## sources/distributed-fs/ipfs-kubo/test/sharness/t0054-dag-car-import-export.sh

Purpose: tests CAR import/export behavior for DAGs, roots, pins, stats, large blocks, CARv2, IPLD codec decoding, and incomplete DAG pin failures.

Important helpers and control flow: `test_cmp_sorted`, `reset_blockstore`, `do_import`, and `run_online_imp_exp_tests` coordinate blockstore cleanup, multi-node online import/export, and output comparison. The script sets up an iptb testbed, stops nodes for offline cases, exports known DAGs, validates nonexistent CID errors, imports multiroot CARs with JSON/stats output, tests `--pin-roots=false`, naked root imports, block size enforcement and `--allow-big-block`, CARv2 import, dag-json/dag-cbor/json/cbor decode paths, and IPIP-402 partial DAG behavior.

State and dependencies: uses CAR fixtures, iptb-managed repos, pins, blockstores, and daemon state. Depends on `ipfs dag import/export`, `ipfs pin`, CAR test data, and sharness/iptb helpers.

Risks: CAR semantics are interoperability-critical; incomplete DAG handling differs depending on pinning. Test signals are exact root/stat output, pin state, block size errors, and expected exit code 1 on pin failure.
