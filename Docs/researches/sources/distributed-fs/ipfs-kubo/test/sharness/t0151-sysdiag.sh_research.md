## sources/distributed-fs/ipfs-kubo/test/sharness/t0151-sysdiag.sh

Purpose: verifies `ipfs diag sys` reports expected system diagnostic fields and aligns with `uname`.

Important APIs and helpers: uses `ipfs diag sys`, `uname`, `grep`, and `test_cmp` style comparisons.

Control flow and state: initializes the repo if needed, runs `ipfs diag sys`, checks for expected keys in the output, runs `uname`, and compares relevant platform information. It does not depend on daemon state.

Dependencies and integration points: covers system diagnostics collection, platform metadata formatting, and CLI output compatibility with common Unix tools.

Risks and test signals: catches missing diagnostic keys, platform detection regressions, and output that drifts away from expected OS/kernel values. Passing requires key presence and similarity to `uname` output.
