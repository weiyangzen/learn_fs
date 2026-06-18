## sources/distributed-fs/ipfs-kubo/test/sharness/t0152-profile.sh

Purpose: tests daemon profiling command behavior and the structure of generated profile archives.

Important APIs and helpers: uses `ipfs diag profile`, `unzip`, profile output files, `grep`, daemon launch/kill helpers, and checks for CPU, heap, goroutine, mutex, block, and stacktrace data.

Control flow and state: confirms profiling requires a running daemon, starts one, captures a default profile archive, verifies filename reporting and archive creation, repeats with `-o`, runs a profile with selected collectors, unpacks archives, and validates expected profile files are present while omitted collectors are absent from the small archive.

Dependencies and integration points: covers daemon debug/pprof collection, ZIP archive creation, CLI output, collector selection, and filesystem writes.

Risks and test signals: catches profiling available offline, missing collector outputs, invalid archive structure, and `-o` output path regressions. Passing requires archive existence and expected internal files after unzip.
