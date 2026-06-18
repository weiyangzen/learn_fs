## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-aggregate-results.sh

Purpose: aggregates sharness textual result files into a suite-level pass/fail summary.

Important control flow: invoked by `Rules.mk` target `aggregate`, it scans `test-results`, summarizes successes/failures/skips, and exits according to aggregate status. State is read from sharness result files and written to stdout/stderr rather than persistent domain state.

Dependencies and integration points: depends on the result format emitted by sharness scripts and shell utilities. It is the main local signal for `make test_sharness` style runs.

Risks: if individual tests are run without producing result files, aggregation can misreport or lack coverage. Test signal is an aggregate nonzero exit on failed sharness tests and readable summary output for CI logs.
