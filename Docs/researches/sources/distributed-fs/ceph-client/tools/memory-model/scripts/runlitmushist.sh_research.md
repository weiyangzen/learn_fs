# sources/distributed-fs/ceph-client/tools/memory-model/scripts/runlitmushist.sh

Purpose: Runs many litmus tests in parallel using the common LKMM environment and reports herd7 execution failures.

Important APIs and functions: Reads litmus file paths on stdin. It sources `hwfnseg.sh` and generates per-worker shell scripts containing `runtest`, which invokes `scripts/runlitmus.sh` and checks for `Observation` lines in the expected output file.

Control flow: After verifying the `litmus` directory, it creates one worker script per `LKMM_JOBS`. An awk pipeline estimates each test's process count from the last `P[0-9]+(` line, sorts by count, then distributes tests round-robin across worker scripts. Hardware runs skip tests rejected by `simpletest.sh`. It launches all worker scripts in background, waits, concatenates outputs, and summarizes `!!!` failures.

State and persistence behavior: Test result files are written by `runlitmus.sh`; this wrapper uses only temporary worker scripts and logs.

Dependencies and integration points: Used by init/new history scripts. Depends on bash arrays/arithmetic, awk, sort, grep, and the LKMM runner scripts.

Risks: Load balancing is heuristic. Generated shell lines assume safe filenames. Failure detection is tied to `!!!` marker text. In hardware mode, skipped complex tests may be invisible unless the caller separately tracks selection.

Test signals: Provide synthetic stdin with varying process counts and mock `runlitmus.sh`; verify distribution, observation checks, hardware simple filtering, failure summary, and exit code.
