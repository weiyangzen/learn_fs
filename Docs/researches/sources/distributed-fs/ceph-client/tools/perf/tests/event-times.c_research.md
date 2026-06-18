# sources/distributed-fs/ceph-client/tools/perf/tests/event-times.c

Purpose: `event-times.c` verifies that software event `cpu-clock:u` reports equal enabled and running time across different attach/enable modes.

Important APIs and state: attach helpers cover enable-on-exec child workload, current thread enabled, current thread disabled then enabled, CPU disabled then enabled, and CPU enabled. `test_times` creates an evlist, parses the event, requests total enabled/running read formats, attaches, does busy work, detaches, reads counts, and checks equality.

Control flow: the suite iterates all attach/detach combinations, preserving a skip result for permission failures. Child workload mode prepares and starts `true`; CPU mode may skip on `EACCES`.

State and persistence: evlists, thread maps, CPU maps, and workload process state are owned and cleaned up per test. No files persist.

Dependencies, integration, risks, and tests: it depends on perf event open permissions, process spawning, and stable software clock behavior. Risks include scheduling races, insufficient CPU permissions, and a possible typo-like `detach__disable` name that enables rather than disables before read. Test signals are `count.ena == count.run` for each successful attach mode.
