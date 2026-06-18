# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm.sh

Purpose: main rcutorture KVM orchestration script. It parses user options, selects scenarios, packs builds/runs into CPU-aware batches, generates a run script, executes it, and records results.

Important APIs and functions: sources `functions.sh`, calls `mkinitrd.sh`, `configNR_CPUS.sh`, `configfrag_boot_cpus`, `configfrag_boot_maxcpus`, `kvm-assign-cpus.sh`, `kvm-get-cpus-script.sh`, `kvm-test-1-run.sh`, and `kvm-end-run-stats.sh`. It manages many environment variables such as `TORTURE_SUITE`, `TORTURE_MOD`, `TORTURE_ALLOTED_CPUS`, `TORTURE_BUILDONLY`, KASAN/KCSAN/GDB options, qemu args, memory, jitter, and shutdown grace.

Control flow: change to kernel top-level, parse options, optionally kill previous lock holders, acquire nonblocking flock, ensure initrd, load suite config list, expand repeated configs, compute CPU counts, greedily bin-pack scenarios, generate a shell script that builds scenarios in batch and runs qemu with optional jitter/affinity, provide dryrun views, or execute and save batches/scenarios metadata.

State and persistence: creates result directory `res/<datestamp>`, log, `torture_suite`, test id, per-scenario dirs, generated `batches` and `scenarios`, STOP file path, and many build/run artifacts. It holds `.kvm.sh.lock`.

Dependencies and integration: top-level interface for local rcutorture selftests, rerun tooling, remote tooling, and series tooling.

Risks and test signals: powerful script that builds kernels, runs qemu, changes `.config`, and consumes CPU. Argument validation is regex-based and quoting is simple. The generated script is the key artifact for debugging dryrun behavior.
