# sources/distributed-fs/ipfs-kubo/coverage/Rules.mk

Purpose: Makefile fragment for sharness coverage support. Important targets/variables are `coverage_deps`, `$(d)/ipfs`, `IPFS_COVER_DIR`, and `$(d)/sharness_tests.coverprofile`.

Control flow: prepares a `sharnesscover` directory, builds a coverage-enabled `ipfs` wrapper with `testrunmain`, adds dependencies when coverage goals are requested, exports coverage output directory, disables test plugins for the sharness coverage target, runs sharness tests through `ipfs-test-cover`, and merges generated coverage profiles with `gocovmerge`.

State and persistence: creates `coverage/sharnesscover`, `coverage/ipfs`, and `coverage/sharness_tests.coverprofile`; updates `CLEAN` and `COVERAGE` make variables.

Dependencies/integration: Kubo make system (`mk/header.mk`, `mk/footer.mk`), Go build helpers, sharness tests, `cmd/ipfs/ipfs-test-cover`, and `test/bin/gocovmerge`.

Risks: path manipulation prepends coverage wrapper to `PATH`; stale cover files are removed only through target setup/CLEAN. No direct unit tests; make/CI coverage jobs are the signal.
