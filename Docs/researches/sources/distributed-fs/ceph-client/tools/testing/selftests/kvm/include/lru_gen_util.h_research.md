# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/lru_gen_util.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/lru_gen_util.h

Purpose: helper declarations for selftests involving multi-generation LRU (`lru_gen`) behavior under KVM workloads.

Important APIs/types/functions: exposes utility routines and constants used to inspect or manipulate kernel LRU generation controls and stats from tests.

Control flow and state: tests use these helpers to read sysfs/debugfs state, configure LRU generation knobs, run memory workloads, and compare before/after reclaim signals. Persistent state is external kernel MM configuration, not local process-only data.

Dependencies and integration: depends on generic `test_util.h` file-reading and assertion helpers and on kernel VM interfaces available on the host. It integrates with memory stress tests that create guest memory pressure.

Risks: host kernel configuration may omit or restrict LRU generation interfaces. Tests must skip cleanly when the feature is unavailable and avoid leaving host VM knobs changed.

Test signals: lru_gen-focused memory selftests validate successful parsing, feature detection, and cleanup. Skip paths are important signals on kernels without support.
