<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ima.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ima.c

Purpose: validates BPF IMA helpers and LSM hook behavior by measuring files under a temporary IMA setup, consuming hashes from a ring buffer, and checking fresh versus stale digest behavior plus deny behavior.

Important APIs/types/functions: `_run_measured_process()` forks and execs `./ima_setup.sh` commands; `process_sample()` collects up to `MAX_SAMPLES` 64-bit hashes from ringbuf records; `test_init()` resets BSS feature flags; `test_test_ima()` orchestrates six scenarios. It uses `ima__open_and_load()`, `ring_buffer__new()`, `ima__attach()`, `ring_buffer__consume()`, `mkdtemp()`, and `system()`.

Control flow: create and attach the IMA skeleton, prepare a measured directory with `ima_setup.sh setup`, then run tests for `bpf_ima_inode_hash`, `bpf_ima_file_hash`, stale inode hash after binary modification, fresh file hash after exec hook, kernel-read-file policy loading, and kernel-read-file denial. Cleanup invokes `ima_setup.sh cleanup`.

State and persistence: creates `/tmp/ima_measuredXXXXXX`, mutates test binaries/policies through the setup script, stores monitored child pid and enable flags in BSS, and uses process-global sample arrays. Cleanup is best-effort via shell script and skeleton/ringbuf destruction.

Dependencies and integration: depends on IMA kernel configuration, BPF LSM hooks, ring buffer map, `ima_setup.sh`, `/bin/true`, fork/exec/wait, and generated `ima.skel.h`. Integrated as `test_test_ima`.

Risks: highly environment-sensitive: IMA policy, helper availability, privileges, script behavior, and commit-dependent stale digest semantics can affect sample counts. Ring buffer capacity is only four samples, matching current scenarios. Early failures before `close_clean` may leave temporary measurement artifacts.

Test signals: asserts exact or minimum sample counts, nonzero hashes, equality/inequality against the saved `/bin/true` sample, expected command failures for deny mode, and zero samples after denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/test_ima.c -->
