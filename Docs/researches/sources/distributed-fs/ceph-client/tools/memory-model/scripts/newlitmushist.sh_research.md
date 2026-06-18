# sources/distributed-fs/ceph-client/tools/memory-model/scripts/newlitmushist.sh

Purpose: Runs only new or modified C-language litmus tests relative to an existing history directory, refreshing `.litmus.out` files without judging them.

Important APIs and functions: Like `initlitmushist.sh`, it sources `parseargs.sh`, uses `mselect7 -arch C`, process-count filtering, and delegates execution to `scripts/runlitmushist.sh`.

Control flow: It requires an existing `litmus` directory, mirrors litmus subdirectories into `LKMM_DESTDIR`, derives already-run tests from existing `.litmus.out` files, builds the full eligible test list, computes tests present in one set but not both with `sort | uniq -u`, detects source files newer than their output via a generated shell script, merges new and newer tests, and runs that list.

State and persistence behavior: Persistent state is the existing `litmus` tree and `LKMM_DESTDIR` output tree. It creates temporary list files and rewrites only selected output files through the runner.

Dependencies and integration points: Designed as the incremental partner to `initlitmushist.sh`; requires the same herdtools and local scripts.

Risks: Deletions are explicitly not handled. `uniq -u` set logic depends on exact path normalization. Filename shell generation for mtime checks assumes litmus paths are shell-safe.

Test signals: In a fixture destination, cover absent `litmus`, already-run unchanged tests, missing output tests, and source-newer-than-output tests; verify only required paths reach `runlitmushist.sh`.
