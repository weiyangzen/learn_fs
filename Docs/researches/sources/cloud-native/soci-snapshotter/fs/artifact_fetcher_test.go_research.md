## sources/cloud-native/soci-snapshotter/fs/artifact_fetcher_test.go

Purpose: validates artifact fetcher reference construction, local cache behavior, descriptor resolution, store verification, remote store creation, and SOCI artifact graph fetch.

Important APIs/types/functions: `TestConstructRef`, `TestArtifactFetcherFetch`, `TestArtifactFetcherResolve`, `TestArtifactFetcherFetchOnlyOnce`, `TestArtifactFetcherStore`, `TestNewRemoteStore`, `TestFetchSociArtifacts`, and fake local/remote stores.

Control flow: tests use ORAS memory stores and fake resolver/storage to simulate local miss, remote fetch, subsequent local hit, digest mismatch, localhost plain HTTP, and corrupted index/zTOC data.

State and persistence: all state is in memory; fake local store implements batch/delete/label methods needed by `FetchSociArtifacts`.

Dependencies and integration: SOCI index marshal/unmarshal, ORAS memory content, digest verification, containerd reference parsing.

Risks and test signals: good behavioral coverage for fetcher core. Tests do not cover real HTTP range requests, redaction paths, auth behavior, GC label failures, or remote status-code edge cases.
