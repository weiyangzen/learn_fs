# sources/distributed-fs/coda/coda-src/librepair/restest.cc

Purpose: small command-line harness for exercising directory resolution against Unix directory replicas. It expects a set of replica paths, converts them to `resreplica` structures, runs `dirresolve`, and prints generated repair lines.

APIs and flow: `main` calls `getunixdirreps(argc - 1, argv + 1, &dirs)`, then invokes `dirresolve` with a callback that prints strings and an output `listhdr **`. On success, it iterates each replica repair list and calls `repair_printline`.

State and dependencies: depends directly on `resolve.cc` globals and `repio` printing. It does not free all allocated state or provide scripted assertions; output is human-inspected. The visible prototype in this file is stale relative to the full `dirresolve` signature in `resolve.h`, so build coverage depends on conditional declarations or historical source skew. Risk is mainly bitrot as an old manual test.
