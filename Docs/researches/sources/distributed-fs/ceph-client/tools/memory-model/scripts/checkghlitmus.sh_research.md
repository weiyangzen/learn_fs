# sources/distributed-fs/ceph-client/tools/memory-model/scripts/checkghlitmus.sh

Purpose: Fetches or reuses Paul McKenney's external `litmus` repository, selects C-language litmus tests with expected results and acceptable process counts, runs missing tests, and judges results.

Important APIs/types/functions: Sources `scripts/parseargs.sh` and `scripts/hwfnseg.sh`; uses temp directory `$T`, `git clone`, `mselect7 -arch C`, `scripts/runlitmushist.sh`, and `scripts/judgelitmus.sh`.

Control flow: Creates a temp workdir with cleanup trap, clones `https://github.com/paulmckrcu/litmus` if absent, mirrors directories into destination, computes already-run tests, computes eligible C tests with `Result:` comments and process-count filter, takes the symmetric difference to find needed tests, runs needed tests, judges all eligible short tests, prints run errors and `!!!` judge lines.

State and persistence: Creates/updates local `litmus` clone. Writes historical `.out` files under `LKMM_DESTDIR`. Uses temp files under `/tmp`.

Dependencies/integration: Requires network/git for first clone, herdtools `mselect7`, LKMM parseargs variables, historical run scripts, grep/sort/xargs utilities.

Risks: Network dependency makes first run non-hermetic. Uses `git checkout origin/master` without pinning a commit, so test corpus changes over time. File/path processing is newline/space fragile. `uniq -u` over combined sorted lists computes symmetric difference, so unusual duplicate cases can affect selection.

Test signals: Run with existing clone, no clone/network available, custom process limit, custom destdir, hardware suffix, and injected mismatches/errors in judge output.
