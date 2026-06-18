# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/security/mitigation-patching.sh

Purpose: stress-tests runtime patching of powerpc security mitigation knobs by toggling them concurrently while optional memory stress runs.

Important APIs/types/functions: `do_one()` toggles one mitigation file for `TIMEOUT` seconds and restores its original value. The script targets `barrier_nospec`, `stf_barrier`, `count_cache_flush`, `rfi_flush`, `entry_flush`, and `uaccess_flush`.

Control flow: it enters `/sys/kernel/debug/powerpc`, records current kernel taint, starts one background toggler per available mitigation file, optionally starts `stress-ng` or `stress`, waits for all jobs, then verifies the taint value has not changed.

State and persistence behavior: writes debugfs mitigation controls and restores each file's original value at the end of its toggler. It observes persistent kernel taint as the main health signal.

Dependencies and integration points: requires bash, debugfs powerpc mitigation knobs, and optionally stress tooling. It is registered as `TEST_PROGS` in the security Makefile.

Risks and test signals: abrupt termination can leave a mitigation file at the last toggled value. Failure is new taint or inability to enter debugfs.
