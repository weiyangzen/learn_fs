## sources/distributed-fs/openafs/src/libuafs/afsload/examples/simple.conf

Purpose: Minimal afsload scenario that validates core create, read, truncate, unlink, and expected failure behavior.

Important structure: Global `nodeconfig` sets rank-specific cache and log paths. Steps perform a chdir into `/afs/.localcell/afsload`, create `foo`, read it from all nodes, truncate/write from node 1, unlink from node 0, then verify `access_r foo` fails with `ENOENT`.

Control flow: Each `step` is a synchronization boundary. Some actions run on all nodes with `node *`; others run on single nodes. The named read step demonstrates human-readable Test::More output.

State and persistence: Mutates one file named `foo` under the selected AFS directory and writes rank logs under `/tmp/afsload`. Cache directories must exist before run.

Dependencies and integration: Uses `chdir`, `creat`, `read`, `truncwrite`, `unlink`, `fail`, and `access_r` action implementations plus MPI and libuafs runtime.

Risks: Assumes the target path exists and is writable. A failed run can leave `foo`, causing later `creat` with `O_EXCL` to fail. Requires at least two worker nodes because node 1 is referenced.

Test signals: Useful smoke test for config parsing, step naming, wildcard ranges, single-node actions, expected failure handling, and basic AFS visibility across nodes.
