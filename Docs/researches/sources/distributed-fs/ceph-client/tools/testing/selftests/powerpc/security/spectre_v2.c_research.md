# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/spectre_v2.c

Purpose: cross-checks the kernel-reported Spectre v2 mitigation state with observed userspace branch prediction/misprediction behavior.

Important APIs/types/functions: `do_count_loop()`, `setup_event()`, `get_sysfs_state()`, `spectre_v2_test()`, `enum spectre_v2_state`, PMU event constants, and external `pattern_cache_loop()`/`indirect_branch_loop()` are core.

Control flow: the test reads `/sys/devices/system/cpu/vulnerabilities/spectre_v2`, maps the text to an enum, opens branch prediction/misprediction PMU events, runs an architecture-specific loop, computes miss percent, and compares that rate against expected bands for vulnerable/not-affected/flush/disabled/serialization states.

State and persistence behavior: perf events are opened, enabled for the loop, read, reported, and closed. No kernel mitigation state is changed.

Dependencies and integration points: requires Power8+ PMU support, `../pmu/event.c`, `utils.c`, and `branch_loops.S`.

Risks and test signals: PMU group running/enabled mismatch fails immediately. A very high miss rate with software count-cache flush returns skip because firmware may have disabled count cache without Linux knowing.
