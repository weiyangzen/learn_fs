## sources/distributed-fs/ipfs-kubo/test/sharness/Rules.mk

Purpose: top-level make fragment that defines sharness test discovery, dependencies, execution, aggregation, and cleanup.

Important variables and control flow: defines `SHARNESS_$(d)`, `T_$(d)`, and `DEPS_$(d)` including helper binaries, `cmd/ipfs/ipfs`, result cleanup, and sharness installation. On Linux it copies plugin `.so` files into `test/sharness/plugins` when plugin tests are enabled. Each test target runs from its directory, optionally continuing on failure when `CONTINUE_ON_S_FAILURE=1`. Aggregate targets run `test-aggregate-results.sh` and `test-aggregate-junit-reports.sh`.

State and dependencies: creates plugin copies and `test-results`, exports `MAKE_SKIP_PATH=1`, and depends on make include conventions plus sharness scripts. `CLEAN` includes test result files.

Risks: dependency list is broad; missing helper binaries break many tests. Plugin copying is Linux-specific. Test signals are successful per-test execution, aggregate text status, and JUnit XML generation.
