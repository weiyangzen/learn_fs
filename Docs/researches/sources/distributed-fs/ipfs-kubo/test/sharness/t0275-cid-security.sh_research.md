## sources/distributed-fs/ipfs-kubo/test/sharness/t0275-cid-security.sh

Purpose: verifies Kubo rejects insecure CIDs and unsafe multihashes on write and read paths. It guards `verifcid` policy by checking `ipfs add`, `ipfs block put`, `ipfs cat`, `ipfs get`, repo GC, and traversal through a maliciously linked block.

Important commands and control flow: after repo init, it asserts `ipfs add --hash shake-128` fails with a "potentially insecure hash functions not allowed" reason and `ipfs block put --mhlen 19` fails with "digest too small". Helper `test_cat_get` runs the same read-side rejection offline and online. Helper `test_gc` injects prepared bad block files directly into the flatfs blockstore and expects `ipfs repo gc` to remove them. The final online case injects a valid-looking block that links to insecure content and ensures `ipfs cat` exits quickly with code 1 instead of hanging.

State and persistence: the test bypasses normal blockstore writes by copying fixture `.data` files into `$IPFS_PATH/blocks/*`, so it validates defensive reads and GC cleanup of persisted invalid blocks, not just API validation.

Dependencies and integration points: uses fixture data under `t0275-cid-security-data`, sharness helpers, daemon lifecycle, `go-timeout`, and CID/security validation shared by blockstore and DAG traversal.

Risks and test signals: failures may indicate policy drift in `verifcid.DefaultAllowlist`, flatfs layout changes, error-message churn, or traversal paths that fail to validate linked CIDs. Timeout assertion is important because rejecting malicious links must be bounded.
