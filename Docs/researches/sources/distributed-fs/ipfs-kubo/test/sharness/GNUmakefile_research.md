## sources/distributed-fs/ipfs-kubo/test/sharness/GNUmakefile

Purpose: local entry makefile for running individual sharness scripts or the aggregate suite from the `test/sharness` directory.

Important targets and control flow: `all` depends on `aggregate`. `SH` expands `t[0-9][0-9][0-9][0-9]-*.sh`. The `.DEFAULT $(SH)` rule delegates to `$(MAKE) -C ../.. test/sharness/$@`, ensuring top-level make rules build dependencies and run the selected test. `ALWAYS` forces delegation.

State and dependencies: no direct state is written; state is handled by top-level make and the tests themselves. It depends on GNU make pattern/default behavior and the top-level `test/sharness/<script>` targets.

Risks: direct execution from this directory relies on top-level make rule names staying aligned. Test signal is the ability to run `make tXXXX-name.sh` or `make aggregate` locally and have dependency preparation happen centrally.
