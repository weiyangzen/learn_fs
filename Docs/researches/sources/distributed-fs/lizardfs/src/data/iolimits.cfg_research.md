# sources/distributed-fs/lizardfs/src/data/iolimits.cfg

Purpose: sample local client/mount I/O limiting configuration.

Important syntax: commented `subsystem blkio` and `limit` examples for `unclassified` and hierarchical groups.

Control flow: consumed by client-side I/O limiting when configured; the shipped sample is entirely commented and therefore inert.

State and persistence: persisted local config template; no runtime state in the file itself.

Dependencies and integration: installed as a client example by `src/data/CMakeLists.txt`; points users to `iolimits.cfg(5)`.

Risks: same syntax as global limits can be confused with the master global limits file; operational semantics depend on the parser and cgroup/blkio support.

Test signals: no direct tests in this subset.
