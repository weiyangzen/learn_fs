<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/livepatch_trampoline.c -->
## sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/livepatch_trampoline.c

Purpose: verifies BPF fentry/fexit attachment to a livepatched kernel function trampoline, specifically the livepatch sample that changes `/proc/cmdline` behavior.

Important APIs and functions: `load_livepatch()` locates `samples/livepatch/livepatch-sample.ko` using `KBUILD_OUTPUT` or a relative kernel tree. `unload_livepatch()` disables `/sys/kernel/livepatch/livepatch_sample/enabled` before unloading. `read_proc_cmdline()` opens and reads `/proc/cmdline`. `__test_livepatch_trampoline()` loads `livepatch_trampoline`, sets `my_pid`, attaches fentry/fexit either in default or reversed order, reads procfs, and checks hit counters.

Control flow: `test_livepatch_trampoline()` skips without `/sys/kernel/livepatch`, retries module loading once after unloading a stale module, runs `fentry_first` and `fexit_first`, then unloads the livepatch.

State and persistence: persistent kernel module/livepatch state is created temporarily and explicitly disabled/unloaded at the end. BPF state is skeleton BSS counters `fentry_hit` and `fexit_hit`.

Dependencies and integration: depends on kernel livepatch support, the sample livepatch module being built, `testing_helpers.h` module helpers, root privileges, procfs, and the generated skeleton.

Risks and test signals: success requires both trampoline programs to fire exactly once and the livepatch text to be visible. Risks include stale modules, missing build outputs, livepatch sysfs policy, and ordering bugs in fentry/fexit trampoline stacking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/livepatch_trampoline.c -->
