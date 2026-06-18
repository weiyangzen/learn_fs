# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/setup_test.go

Purpose: builds a local test distribution and trustless gateway used by migration fetch tests.

Important APIs and control flow: `TestMain` creates fake package/version/archive data, wraps it into a CAR file, starts an `httptest` gateway backed by that CAR, stores `testIpfsDist` and `testServer`, then runs tests. Helpers generate fake tar.gz/zip archives, build UnixFS recursively into CAR storage, replace CAR roots, and create a blockservice-backed gateway.

State and persistence: writes temp package trees, archive files, CAR files, and starts an HTTP server; removes CAR file on exit.

Dependencies and integration: uses Boxo gateway/blockservice, go-car v2, UnixFS builder, IPLD link systems, multihash/cid, and unpack helper functions.

Risks and test signals: provides strong local integration coverage for HTTP fetchers without external network reliance. It is test-only but complex enough that failures can obscure fetcher failures.
