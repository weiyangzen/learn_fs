## sources/distributed-fs/ceph-client/tools/perf/tests/thread-maps-share.c

Purpose: verifies threads in the same process share `struct maps` and reference counts are maintained.
Important function: `test__thread_maps_share`.
Control flow: initializes machines, creates a process with leader and three threads plus another process missing its explicit leader, checks map pointer equality/refcounts, removes threads from machine rbtrees, then releases refs one by one while validating counts.
State and persistence: host machine/thread objects and map refs are created and destroyed within the test.
Dependencies and integration: `machine__findnew_thread`, `thread__maps`, `maps__refcnt`, `maps__equal`, and `thread__put`.
Risks: relies on machine behavior that creates an implicit leader for process 4; refcount expectations are exact.
Test signals: correct shared maps and decrementing refcounts across thread releases.
