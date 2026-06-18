## sources/distributed-fs/ipfs-kubo/test/cli/update_test.go

Purpose: offline, deterministic CLI coverage for the `ipfs update` command tree, including read-only release queries, daemon-lock behavior, full binary install, revert, and stash cleanup.

Important APIs and helpers: `TestUpdate`, `TestUpdateWhileDaemonRuns`, `TestUpdateInstall`, `TestUpdateRevert`, and `TestUpdateClean` use `httptest.Server`, `TEST_KUBO_UPDATE_GITHUB_URL`, and `TEST_KUBO_VERSION` to avoid real GitHub calls. Helpers `newMockGitHubReleases`, `copyBuiltBinary`, `buildTestTarGz`, and `buildTestZip` fabricate release metadata, platform asset names, archives, and SHA-512 sidecars. Control flow checks help text, `check`, `versions`, JSON encodings, same-version install rejection, missing-stash revert errors, then copies the built `ipfs` binary to a temp path so install/revert mutate a disposable executable.

State and persistence: tests create `$IPFS_PATH/old-bin` stashes, replace a temporary binary, verify archive checksums and backup names, and preserve unrelated files during `clean`. Windows-specific fallbacks validate manual move paths when in-place executable replacement is locked. Dependencies include archive libraries, SHA-512, runtime OS/arch selection, Kubo CLI harness, and testify.

Risks: install/revert tests are intentionally not parallel because concurrent forks can cause ETXTBSY on Unix-like systems. Test signals include stdout/stderr content, JSON shape, stash presence/removal, exact binary bytes, and successful read-only update commands while a daemon holds the repo lock.
