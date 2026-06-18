## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-dag-jose.sh

Purpose: validates the `dag-jose` IPLD plugin codec in offline and daemon-backed modes. It proves fixture files can be encoded as `dag-jose`, decoded back to their original codec, and rendered through other DAG output codecs.

Important commands and control flow: helper `test_dag_jose` iterates fixture files under `t0280-plugin-dag-jose-data`, derives input codec from the parent directory, runs `ipfs dag put --store-codec dag-jose --input-codec=<codec>`, then `ipfs dag get --output-codec <codec>` and diffs against the original. A second pass gets the same CIDs as `dag-cbor` and `dag-json` to ensure cross-codec traversal/rendering.

State and persistence: stored DAG nodes are inserted into the local repo, then read both offline and through a launched daemon. No permanent config is changed beyond test repo initialization.

Dependencies and integration points: depends on Kubo plugin registration, IPLD codec table, `ipfs dag put/get`, fixture codecs, `find`, `xargs`, and shell quoting.

Risks and test signals: regressions show up as missing plugin registration, broken codec roundtrips, fixture parsing changes, or DAG output codec incompatibility. The test is broad across fixtures but has limited assertion detail beyond successful diff/get.
