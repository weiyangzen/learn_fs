# subset-b-006882 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/mktestid.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/mktestid.sh

Purpose: writes a small provenance record for an rcutorture result directory, tying a test run to the current host, user, working tree, and command context. Important interfaces are the result-directory argument, standard Unix tools (`date`, `hostname`, `whoami`, `pwd`, `git status`, `git rev-parse`, `git diff`), and the created files under the supplied directory. Control flow is linear: validate or assume the directory, create an identifier/log fragment, query git state when available, and leave the metadata beside other run artifacts. State is persistent only in the result directory; the script does not mutate kernel config or source files. It integrates with `torture.sh`, `srcu_lockdep.sh`, and KVM rcutorture launchers that need reproducible run IDs. Risks are missing git metadata, invocation outside a kernel tree, unwritable result paths, and command output changing under concurrent repository updates. Test signals are non-empty provenance files in new result directories and graceful behavior in dirty or non-git worktrees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/mktestid.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/parse-build.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/parse-build.sh

Purpose: analyzes a kernel build log from an rcutorture scenario and emits diagnostics for build warnings, errors, and abnormal exits. The key inputs are the build output file and a title/scenario label; key outputs are messages on stdout and a `.diags` sidecar next to the parsed log. It sources `functions.sh` for `print_warning`/`print_bug` style reporting and relies on grep/sed filters for `Stop`, compiler `error:`, `warning:`, and Kconfig/build failure patterns. Control flow validates readability, truncates or initializes the diagnostics file, scans for known bad signatures, and removes an empty diagnostics file. State is file-based, so reruns overwrite or refresh sidecar diagnostics. Integration points are `kvm-recheck*.sh`, `torture.sh` summary collection, and per-scenario `Make.out`. Risks include false positives from harmless warning strings, missed compiler diagnostics with unfamiliar formats, and binary/log corruption. Useful tests feed clean, warning-only, and hard-error `Make.out` samples and assert exit/status plus `.diags` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/parse-build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/parse-console.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/parse-console.sh

Purpose: parses a guest console log for rcutorture success, failure, stalls, warnings, BUG/Oops, lockdep, KCSAN, hotplug, and ftrace evidence. Inputs are `file` and `title`; outputs are stdout warnings plus `$file.diags` and optional `$file.ftrace`. It sources `functions.sh`, calls `console-badness.sh`, and uses `extract_ftrace_from_console`. Control flow checks readability and NUL bytes, skips normal-termination checks for `rcuscale`/`refscale`, detects explicit `FAILURE` or `!!!` lines, validates monotonic `torture: ver:` sequences, summarizes badness classes, appends any nested diagnostics, and removes empty sidecars. State is persisted in diagnostic/ftrace sidecars only. It integrates with rcutorture recheck scripts and `torture.sh` failure summaries. Risks are brittle log regexes, binary console content from live QEMU, false lockdep count using separator lines, and suite-specific success semantics. Test signals include clean `SUCCESS`, bad sequence, hotplug failure, KCSAN-only BUG, stall, and ftrace extraction fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/parse-console.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/srcu_lockdep.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/srcu_lockdep.sh

Purpose: drives a matrix of SRCU lockdep validation runs and checks that expected successes and expected lockdep failures line up with kernel behavior. Important inputs are `--datestamp`, hard-coded `SRCU-P` KVM scenario choices, `CONFIG_FORCE_NEED_SRCU_NMI_SAFE=y`, and `rcutorture.test_srcu_lockdep`/`reader_flavor` bootargs. Control flow creates a temp workspace, parses options, loops over deadlock dimensions `d`, `t`, `c`, then tests mixed reader flavors `0x1` and `0xf`. Each iteration launches `kvm.sh`, moves its output into `$RCUTORTURE/res/$ds/...`, checks `.config` for `CONFIG_PROVE_LOCKING=y`, compares exit code against expected outcome, and records `kvm.sh.err` on mismatch. State is the rcutorture result tree and temp logs. Integration is from `torture.sh --do-srcu-lockdep`. Risks include expensive VM fan-out, dependence on lockdep config, assumptions about console paths, and cleanup only through shell traps. Test signals are zero exit for expected matrix behavior and explicit unexpected success/failure logs otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/srcu_lockdep.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/torture.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/torture.sh

Purpose: top-level overnight torture orchestrator for RCU, lock, SCF, scale, refscale, kvfree, RT, allmodconfig, clocksource watchdog, SRCU lockdep, and optional Rust/KUnit checks. It imports `functions.sh`, sets `RCUTORTURE` and `PATH`, sizes CPU/concurrency budgets from `identify_qemu_vcpus`, parses many `--do-*`, config, duration, CPU-limit, compression, and KCSAN options, then creates a datestamped result tree. Core APIs are shell functions `doyesno`, `torture_one`, and `torture_set`; external integration is `kvm.sh`, `kvm-again.sh`, `mktestid.sh`, `srcu_lockdep.sh`, `kcsan-collapse.sh`, `make`, and `kunit.py`. Control flow apportions duration among suites, performs optional build-only tasks, runs selected suites in normal/KASAN/KCSAN variants, records `$T/successes` and `$T/failures`, prints summaries, collapses KCSAN output, finds build/config diagnostics, and compresses KASAN/KCSAN `vmlinux` files with bounded parallelism. State persists under `tools/testing/selftests/rcutorture/res/$ds`, with temp bookkeeping in `$T`. Risks include quoting limitations noted in comments, architecture-specific defaults, very large artifacts, stale `last-resdir` files, and destructive assumptions around build trees. Test signals are success/failure counts, per-scenario logs, `Make.exitcode`, `kcsan.sum`, `.diags`, and final exit `0` or `2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/torture.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/lock/ver_functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/lock/ver_functions.sh

Purpose: supplies locktorture-specific boot-parameter assembly for rcutorture KVM scripts. It exports `locktorture_param_onoff` and `per_version_boot_params`, relying on common helpers `bootparam_hotplug_cpu` and `configfrag_hotplug_cpu` from the broader rcutorture shell environment. Control flow conditionally adds `locktorture.onoff_interval=3 locktorture.onoff_holdoff=30` when CPU hotplug is configured but not already controlled by boot parameters, then appends `locktorture.stat_interval=15`, `locktorture.shutdown_secs=$seconds`, and `locktorture.verbose=1`. State is not persisted by this file; it emits strings consumed by scenario launchers. Integration is with `kvm.sh` per-suite config handling. Risks are duplicate or conflicting bootargs, stderr informational output affecting callers that do not separate streams, and dependency on common helper definitions. Test signals are generated bootargs for hotplug/non-hotplug fragments and correct shutdown timing propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/lock/ver_functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/rcu/ver_functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/rcu/ver_functions.sh

Purpose: builds RCU torture bootargs that are compatible across kernel versions and scenario fragments. Important functions are `rcutorture_param_n_barrier_cbs`, `rcutorture_param_onoff`, `rcutorture_param_stat_interval`, and `per_version_boot_params`. Control flow avoids overriding user-specified `rcutorture.n_barrier_cbs` or `rcutorture.stat_interval`, conditionally enables CPU hotplug on/off testing, then emits shutdown, no-idle-HZ, verbose, and caller bootargs. It has no local persistence; its output string becomes QEMU kernel command-line state. Dependencies are common rcutorture shell helpers, config fragments, and callers that pass bootargs/config-file/seconds in the documented order. Integration is all normal `--torture rcu` scenario launching. Risks include grep matching unquoted bootarg strings, accidental duplicate parameters, and stale compatibility assumptions. Tests should cover explicit overrides, hotplug-enabled fragments, and expected `shutdown_secs` insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/rcu/ver_functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/rcuscale/ver_functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/rcuscale/ver_functions.sh

Purpose: emits suite-specific bootargs for `rcuscale` scenarios. The single public function `per_version_boot_params` appends `rcuscale.shutdown_secs=$3`, disables verbose output with `rcuscale.verbose=0`, and preserves caller-supplied bootargs. There is no local state or persistence; callers consume stdout as the kernel command line. Dependencies are the rcutorture shell framework’s convention for sourcing `ver_functions.sh` and passing bootparam/config/seconds arguments. Integration is with `kvm.sh`, `kvm-again.sh`, and `torture.sh` loops over `kernel/rcu/rcuscale.c` primitive names. Risks are minimal but include argument-order mistakes and missing shutdown parameter causing scale tests to run indefinitely. Test signals are exact bootarg strings for a sample seconds value and user bootargs preserved at the end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/rcuscale/ver_functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/refscale/ver_functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/refscale/ver_functions.sh

Purpose: emits version/suite boot parameters for `refscale` scenarios. Its `per_version_boot_params` function combines `refscale.shutdown_secs=$3`, `refscale.verbose=0`, and the incoming bootarg string. It does not inspect config fragments or persist state. Integration is with `torture.sh` and rcutorture KVM launchers that iterate `kernel/rcu/refscale.c` primitives and reuse earlier result directories through `kvm-again.sh`. Dependencies are shell argument ordering and the refscale module parameter contract. Risks are silent bad output if called outside the framework or with empty seconds, and loss of caller bootargs if quoting is wrong upstream. Test signals are deterministic emitted bootargs and successful refscale shutdown at the requested duration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/refscale/ver_functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/scf/ver_functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/scf/ver_functions.sh

Purpose: provides SCF torture boot-parameter generation. It defines `scftorture_param_onoff` and `per_version_boot_params`, mirroring lock/RCU helpers for CPU hotplug and adding `scftorture.stat_interval=15`, `scftorture.shutdown_secs=$3`, and `scftorture.verbose=1`. Control flow conditionally emits on/off arguments when bootargs do not already control hotplug and the config enables hotplug. State is only stdout used by `kvm.sh`. Dependencies are common helper functions and SCF module parameter names. Integration is `torture.sh` `--do-scftorture`, especially CPU-scaled runs with `scftorture.nthreads` and `csdlock_debug=1`. Risks are duplicate bootargs and changes to SCF parameter names. Tests should compare generated bootargs for hotplug and non-hotplug configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/configs/scf/ver_functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/Makefile

Purpose: registers four RDMA RXE shell tests with kselftest: namespace rping, IPv6 RXE, socket lifetime, and NETDEV_UNREGISTER cleanup. It uses `TEST_PROGS` and includes `../lib.mk`; no binaries are built. State is the generated kselftest run/install metadata, not runtime RDMA resources. Dependencies are shell, root privileges, `ip`, `rdma`, `ss`, `rping`, and kernel modules listed in `config`. Integration is the Linux selftests harness. Risks are scripts suppress stdout with `exec > /dev/null`, so failures rely on exit status and stderr; tests are destructive to fixed interface/netns names. Test signals are kselftest pass/fail status for each script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/config

Purpose: declares kernel configuration dependencies for the RDMA RXE selftests: `CONFIG_TUN`, `CONFIG_VETH`, and `CONFIG_RDMA_RXE`. There is no control flow or persistence beyond kselftest config discovery. It integrates with build/test environments that use selftest `config` files to enable modules/features. Risks are incomplete dependency declaration for user-space tools such as `rdma`, `rping`, and `iproute2`, and module versus built-in availability differences. Test signals are the ability to load/use `rdma_rxe`, create TUN/veth devices, and run the four scripts without skip/failure due to missing kernel support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_ipv6.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_ipv6.sh

Purpose: verifies RXE over an IPv6-addressed veth inside a network namespace and checks that UDP port 4791 appears and disappears with the RDMA link. It creates netns `net6`, veth pair `veth0`/`veth1`, address `2001:db8::1/64`, RXE link `rxe6`, and uses `ss -Hul6n`. Control flow suppresses stdout, installs an EXIT cleanup trap, checks module metadata for `tun`, `veth`, and `rdma_rxe`, loads `rdma_rxe`, builds namespace networking, adds the RXE link, verifies port listening, deletes the RDMA link, and verifies port closure. State is kernel networking/RDMA objects cleaned by trap. Dependencies are root, iproute2 RDMA tooling, module unload permission, and IPv6 support. Risks are fixed names colliding with other tests, stdout suppression hiding diagnostics, and module removal disrupting other RXE users. Test signals are exit zero plus absence of leftover namespace/link/port.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_ipv6.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_rping_between_netns.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_rping_between_netns.sh

Purpose: validates RXE traffic between host and a network namespace using a veth pair and `rping`. It creates namespace `test1`, veth `veth-a`/`veth-b`, IPv4 addresses `1.1.1.1/24` and `1.1.1.2/24`, RXE devices `rxe0` and `rxe1`, verifies UDP 4791 in both namespaces, pings the namespace endpoint, runs an `rping` server in the namespace, then runs a host client with `-C 3`. State is namespace, veth, RXE links, and a background server PID, all cleaned by trap. Dependencies are root, `rdma_rxe`, `rping`, `ip`, `rdma`, `ss`, and ICMP reachability. Risks include fixed private addresses/names, cleanup killing only the captured `rping` PID, module unload affecting concurrent tests, and stdout suppression. Test signals are successful ping, successful `rping`, and clean exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_rping_between_netns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_socket_with_netns.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_socket_with_netns.sh

Purpose: checks RXE UDP socket lifetime when multiple RXE links exist on TUN devices. It loads `tun` and `rdma_rxe`, creates `tun0`/`tun1` with `1.1.1.1/24` and `2.2.2.2/24`, creates `rxe0`/`rxe1`, verifies UDP 4791 remains open after adding links, deletes `rxe1`, checks the port stays active because `rxe0` remains, deletes `rxe0`, then checks the port closes. State is host TUN and RDMA links cleaned on EXIT. Integration is regression coverage for RXE shared socket reference counting. Risks are root-only operations, fixed interface names, suppressing stdout, and removal of modules used elsewhere. Test signals are the `ss -Huln sport = :4791` checks before and after targeted deletions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_socket_with_netns.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_test_NETDEV_UNREGISTER.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_test_NETDEV_UNREGISTER.sh

Purpose: validates that RXE cleans itself up when the underlying netdevice is unregistered. It creates TUN device `tun0`, assigns `1.1.1.1/24`, creates RXE link `rxe0`, checks UDP 4791 is listening, deletes the TUN device without deleting the RDMA link first, then verifies the RXE link and port are gone. State is host TUN/RDMA module state cleaned by trap. Dependencies are root, `rdma_rxe`, `ip tuntap`, `rdma link`, and `ss`. Integration targets the kernel NETDEV_UNREGISTER notifier path for RXE. Risks are fixed names, module unload races, and stdout suppression. Test signals are absence of `rdma link show rxe0` and no listening UDP 4791 after netdev deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rdma/rxe_test_NETDEV_UNREGISTER.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/Makefile

Purpose: builds the `resctrl_tests` kselftest binary from all C files in the directory. It sets hardened debug CFLAGS, imports kernel headers, records local headers, includes `../lib.mk`, adds `tools/include`, and makes the output binary depend on every `*.c`. State is build output in `$(OUTPUT)` only. Dependencies are x86 resctrl-capable headers and libc/perf/syscall APIs. Integration is the kselftest build/run harness and the adjacent `config` file. Risks are the wildcard all-C dependency causing full relinks for unrelated helper changes and architecture-specific source that is meaningful primarily on x86. Test signals are successful compilation and a runnable `resctrl_tests` binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cache.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cache.c

Purpose: shared cache measurement helper for CAT and CMT tests. Important APIs are `perf_event_attr_initialize`, `perf_open`, `perf_event_reset_enable`, `perf_event_measure`, `measure_llc_resctrl`, and `show_cache_info`; global state is `llc_occup_path`. Control flow configures a hardware perf event for cache misses, opens it against a PID/CPU, resets/enables/disables counters around cache fills, reads `struct perf_event_read`, or reads LLC occupancy from the resctrl path and appends results to a file or stdout. Dependencies are `perf_event_open`, ioctls, resctrl `llc_occupancy`, and kselftest logging. Integration is `cat_test.c` for cache misses and `cmt_test.c` for occupancy. Risks include stale global path, perf permission failures, partial reads, and parsing assumptions in downstream result checks. Test signals are result lines containing PID and LLC value plus pass/fail summaries from CAT/CMT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cat_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cat_test.c

Purpose: implements L3 CAT and non-contiguous CAT selftests. Key functions are `cat_run_test`, `cat_test`, `check_results`, `next_mask`, `arch_supports_noncont_cat`, `noncont_cat_run_test`, and exported `resctrl_test` objects `l3_cat_test`, `l3_noncont_cat_test`, `l2_noncont_cat_test`. Control flow discovers CBM masks, shareable bits, cache size, and requested bit count; writes root and control-group schemata; repeatedly flushes/fills a buffer; measures perf cache misses; then checks that reducing CBM bits changes miss rates enough on Intel. Non-contiguous tests compare CPUID/vendor expectations with `info/*/sparse_masks` and schemata write behavior. State includes result file `result_cat`, resctrl groups/schemata, CPU affinity, perf fd, and allocated buffer. Risks are noisy cache behavior, SNC/cache topology effects, non-Intel threshold differences, and sparse-mask ABI mismatch. Test signals are kselftest pass/fail plus printed average LLC values and percentage deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cat_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cmt_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cmt_test.c

Purpose: validates Cache Monitoring Technology LLC occupancy accounting. Key callbacks are `cmt_init`, `cmt_setup`, `cmt_measure`, `cmt_run_test`, and `cmt_feature_check`, exported as `cmt_test`. Control flow builds the `llc_occupancy` path for the selected L3 domain, sizes a fill buffer based on CBM bits and cache size, runs five one-second measurements through `resctrl_val`, reads resctrl occupancy, then compares average measured occupancy against expected span using absolute and percentage tolerances. State is `result_cmt`, global `llc_occup_path`, resctrl group `c1`, benchmark child, and optional fill buffer. Dependencies are L3 and `L3_MON/llc_occupancy`, SNC support, and shared helpers. Risks include noisy occupancy, unsupported SNC sub-node reporting, offline CPUs making SNC detection unreliable, and user benchmark behavior not matching fill-buffer assumptions. Test signals are printed cache size, span, average LLC occupancy, and pass/fail tolerance lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/cmt_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/config

Purpose: declares kernel configuration dependencies for resctrl selftests: `CONFIG_X86_CPU_RESCTRL=y` and `CONFIG_PROC_CPU_RESCTRL=y`. It has no executable flow. Integration is with kselftest configuration tooling that can prepare a kernel capable of mounting `/sys/fs/resctrl` and exposing CPU resource-control information. Risks are that runtime still needs suitable Intel/AMD/Hygon hardware, perf permissions, mounted sysfs/procfs, and root privileges; the config file cannot express all of those. Test signals are `check_resctrlfs_support()` passing and individual feature checks finding `MB`, `L3`, `L2`, and `L3_MON` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/fill_buf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/fill_buf.c

Purpose: provides the default memory/cache pressure benchmark used by resctrl tests. Important APIs are `alloc_buffer`, `mem_flush`, `fill_cache_read`, and `get_fill_buf_size`. Control flow allocates page-aligned memory, initializes one word per cache line, optionally flushes cache lines using x86 `clflush`/`sfence`, then repeatedly reads half-cacheline positions in a prime-step order (`FILL_IDX_MULT=23`) to reduce hardware prefetch predictability. State is the allocated buffer and `value_sink` consumption to defeat compiler optimization. Dependencies are architecture-specific cache flush assembly on x86, cache size helpers, and `MINIMUM_SPAN`. Integration is MBM/MBA/CMT default benchmark and CAT warmup/measurement loops. Risks are non-x86 flush no-ops, allocation size errors, infinite loop when `once=false`, and prefetcher-specific stability. Test signals are stable bandwidth/cache results and no optimized-away memory accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/fill_buf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/mba_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/mba_test.c

Purpose: validates Intel Memory Bandwidth Allocation by applying MB schemata percentages and comparing resctrl MBM with iMC perf counters. Key functions are `mba_init`, `mba_setup`, `mba_measure`, `show_mba_info`, `check_results`, and exported `mba_test`. Control flow initializes iMC perf events and resctrl MBM path, cycles allocations from 10 to 100 in steps of 10, performs five measurements per allocation using `measure_read_mem_bw`, parses `result_mba`, drops low-bandwidth data below `THROTTLE_THRESHOLD`, and checks average differences within 8 percent. State includes static allocation counters in `mba_setup`, result file, resctrl group `c1`, benchmark child, and perf fds. Dependencies are Intel MB resource, `L3_MON/mbm_local_bytes`, uncore iMC PMUs, and shared runner. Risks include static setup state across repeated invocations in one process, non-memory traffic counted differently by MBM/iMC, SNC limitations, and external bandwidth noise. Test signals are per-schemata diff lines and final MBA schemata pass/fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/mba_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/mbm_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/mbm_test.c

Purpose: validates Intel Memory Bandwidth Monitoring by comparing resctrl local bandwidth with iMC read counters. Key callbacks are `mbm_init`, `mbm_setup`, `mbm_measure`, `mbm_run_test`, and `mbm_feature_check`, exported as `mbm_test`. Control flow initializes iMC counters, sets MB schemata to 100 percent if MB allocation exists, runs five one-second measurements through `resctrl_val`, parses `result_mbm`, averages iMC and resctrl values, and requires difference within 8 percent. State is result file, resctrl group, benchmark child, fill buffer or user benchmark, perf fds, and MBM sysfs path. Dependencies are Intel, `L3_MON/mbm_total_bytes` and `mbm_local_bytes`, uncore PMU event files, and perf permissions. Risks are noisy memory traffic, division by zero if iMC average is zero, SNC reporting gaps, and user benchmarks with writes or low bandwidth. Test signals are average iMC/resctrl MB/s and printed diff percentage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/mbm_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl.h

Purpose: central contract for the resctrl selftest suite. It defines paths (`/sys/fs/resctrl`, `/sys/fs/resctrl/info`), vendor bitmasks, thresholds, `struct fill_buf_param`, `struct user_params`, `struct resctrl_test`, `struct resctrl_val_param`, `struct perf_event_read`, globals (`value_sink`, `snc_unreliable`, `llc_occup_path`), helper prototypes, and exported test objects. Control/data flow is callback-oriented: `resctrl_tests.c` selects a `resctrl_test`, shared helpers mount resctrl and set affinity/groups, and each test supplies feature/run/cleanup callbacks. State/persistence is primarily sysfs/resctrl groups, schemata, result files, child PIDs, and perf counters. Dependencies include kselftest, Linux perf ABI, sysfs cache topology, vendor CPU info, and kernel resctrl support. Risks are global mutable state, path-size assumptions, x86-centric features, and callback misuse. Test signals are compile coverage of all prototypes and runtime kselftest plans/results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl_tests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl_tests.c

Purpose: main executable for resctrl selftests. It registers the MBM, MBA, CMT, L3 CAT, L3 non-contiguous CAT, and L2 non-contiguous CAT tests; parses command-line options for test list, bits, CPU, and benchmark; detects CPU vendor from `/proc/cpuinfo`; mounts/unmounts resctrl around each test; and emits kselftest results. Important functions are `detect_vendor`, `run_single_test`, `alloc_fill_buf_param`, `init_user_params`, and `main`. State includes global `value_sink`, parsed `user_params`, allocated fill-buffer parameters, selected disabled flags, signal handlers, and mounted resctrl filesystem. Dependencies are root/resctrl support, vendor strings, shared test callbacks, and kselftest output APIs. Risks include failing hard on prepare errors, benchmark argument limit `BENCHMARK_ARGS`, disabling tests by group/name matching, and refusing pre-mounted resctrl. Test signals are skip/pass/fail lines per selected test and cleanup on signals through registered handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl_tests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl_val.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl_val.c

Purpose: shared memory-bandwidth validation engine and benchmark runner for MBM/MBA/CMT. It discovers uncore iMC PMUs under `/sys/bus/event_source/devices`, parses `events/cas_count_read`, configures perf events, reads MBM local bytes from resctrl, handles signals, forks a benchmark, and loops setup/measure callbacks until `END_OF_TESTS`. Key APIs are `initialize_read_mem_bw_imc`, `initialize_mem_bw_resctrl`, `measure_read_mem_bw`, `resctrl_val`, and signal registration helpers. State includes `imc_counters_config[]`, `imcs`, `mbm_total_path`, `bm_pid`, `current_test`, result files, benchmark buffer, CPU affinity, and resctrl task membership. Dependencies are uncore PMU naming, perf event scaling fields, resctrl monitor paths, `execvp` for custom benchmarks, and fill-buffer helpers. Risks include MAX_IMCS cap, mutable static state, killing benchmark with SIGKILL without wait, sysfs parsing fragility, and measuring all memory ops while iMC path counts reads. Test signals are result lines with iMC/resctrl bandwidth and cleanup after SIGINT/SIGTERM/SIGHUP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrl_val.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrlfs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrlfs.c

Purpose: filesystem/topology utility layer for resctrl tests. Important APIs include `mount_resctrlfs`, `umount_resctrlfs`, `get_domain_id`, `snc_nodes_per_l3_cache`, `get_cache_size`, `get_full_cbm`, `get_mask_no_shareable`, `taskset_benchmark`, `write_bm_pid_to_resctrl`, `write_schemata`, feature checks, `filter_dmesg`, `perf_event_open`, `count_bits`, and `snc_kernel_support`. Control flow reads `/proc/mounts`, sysfs cache IDs/sizes/maps, resctrl info files, creates control/monitor groups, writes `tasks` and `schemata`, filters dmesg, and probes SNC sub-node files. State is global `snc_unreliable`, resctrl mount state, group directories, schemata, task placement, and CPU affinity. Dependencies are root, sysfs/procfs layouts, resctrl ABI, CPU topology, and `dmesg`. Risks include refusing pre-existing resctrl mounts, fixed buffer sizes, offline CPU detection bugs, `mkdir(..., 0)` mode reliance, no rollback for partial group creation, and topology assumptions on non-x86. Test signals are mount/feature pass messages, successful schemata writes, and dmesg excerpts for resctrl errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/resctrl/resctrlfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/Makefile

Purpose: builds the ring-buffer mmap selftest `map_test`. It sets `TEST_GEN_PROGS = map_test`, includes `../lib.mk`, and otherwise relies on default kselftest build rules. State is only the built binary in `$(OUTPUT)`. Dependencies are kernel headers for trace mmap metadata and a kernel with tracefs/ring-buffer mmap support. Integration is kselftest discovery and the adjacent `config` file. Risks are minimal; failures usually come from missing headers or tracefs support at runtime. Test signals are successful build and kselftest execution of `map_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/config

Purpose: declares tracing dependencies for the ring-buffer mmap test, including tracefs/ring-buffer features required by `/sys/kernel/tracing`. There is no control flow. It integrates with kselftest config preparation so `map_test` can open tracefs files, configure buffer size, and mmap per-CPU trace buffers. Risks are that mount state, permissions, and trace options cannot be fully represented by the config file. Test signals are a mounted tracefs root and successful writes to tracing control files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/map_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/map_test.c

Purpose: validates tracefs ring-buffer mmap metadata/data behavior and exclusion with snapshot mode. Important helpers are `__tracefs_write`, `tracefs_reset`, `tracefs_cpu_map`, `tracefs_cpu_unmap`, plus kselftest fixtures `map` and `snapshot`. Control flow resets tracing, configures per-CPU buffer size variants (4K/8K sub-buffers), enables mmap behavior, maps metadata and data pages from tracefs per-CPU files, checks meta fields and reader/writer behavior, then verifies snapshot mode excludes mmap and mmap excludes snapshot. State is tracefs global tracing configuration, buffer size, enabled events/tracing state, file descriptors, and mmap mappings; teardown resets tracefs. Dependencies are root or tracefs write permission, `/sys/kernel/tracing`, and kernel ring-buffer mmap ABI. Risks are fixed global tracing state interfering with other tracing users, CPU0 assumptions, page-size/sub-buffer alignment, and cleanup on assertion failure. Test signals are harness results for `meta_page_check`, `data_mmap`, `excludes_map`, and `excluded_by_map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ring-buffer/map_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/Makefile

Purpose: top-level RISC-V kselftest dispatcher. It detects `ARCH` from `uname -m` unless overridden, sets `RISCV_SUBTARGETS` to `abi hwprobe mm sigreturn vector cfi` only when building for riscv, exports common CFLAGS/top_srcdir, and forwards `all`, `install`, `run_tests`, `emit_tests`, and `clean` into each subdirectory with per-subdir `$(OUTPUT)`. State is build output under subtarget directories. Dependencies are kselftest lib.mk expectations and RISC-V toolchains/headers. Risks include no-op behavior on non-riscv hosts, cross-compile needing `ARCH=riscv`, and subtarget build failures hidden inside loops unless make propagates errors. Test signals are subtarget binaries/scripts emitted only for RISC-V.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/abi/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/abi/Makefile

Purpose: builds the static RISC-V ABI pointer-masking selftest. It adds `tools/include`, sets `TEST_GEN_PROGS := pointer_masking`, includes `../../lib.mk`, and explicitly links `pointer_masking.c` statically. State is the output executable. Dependencies are RISC-V headers with tagged-address control constants or local fallbacks, static libc/toolchain support, and kselftest. Risks are static link failures in minimal cross toolchains and running only on kernels/hardware with pointer masking support. Test signals are successful build and harness output from `pointer_masking`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/abi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/abi/pointer_masking.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/abi/pointer_masking.c

Purpose: tests RISC-V pointer masking and tagged address ABI behavior. Key functions are `test_pmlen`, `set_tagged_addr_ctrl`, `test_dereference_pmlen`, `test_fork_exec`, `test_tagged_addr_abi_sysctl`, and `test_tagged_addr_abi_pmlen`. Control flow discovers valid PMLEN values through `PR_SET/GET_TAGGED_ADDR_CTRL`, checks user dereference acceptance/rejection with SIGSEGV recovery, verifies fork preserves masking while exec resets it, toggles `/proc/sys/abi/tagged_addr_disabled`, and checks kernel copy_to/from_user behavior using pipe and `/dev/zero`. State includes global min/max PMLEN, open `/dev/zero`, pipe fds, signal jump buffer, and sysctl contents modified during the test. Dependencies are RISC-V XLEN, prctl ABI, sysctl write permission, and signal context behavior. Risks include leaving sysctl disabled on abnormal exit, needing privileges for sysctl, fork/exec status assumptions, and hard-coded valid PMLEN set `{0,7,16}`. Test signals are planned kselftest results for PMLEN constraints, dereference, fork/exec, sysctl, and ABI copy paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/abi/pointer_masking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/Makefile

Purpose: conditionally builds the RISC-V control-flow integrity selftest `cfitests`. It adds kernel headers/tools includes, requires `-march=rv64gc_zicfilp_zicfiss -fcf-protection=full`, selects a cross GCC when needed, probes compiler support with a no-op build, and only defines `TEST_GEN_PROGS` if supported. State is output binary or a skipped build message. Dependencies are a CFI-capable RISC-V compiler, glibc/kernel headers with CFI/shadow-stack prctls, and `lib.mk`. Risks are silent skip on unsupported toolchains, hard-coded rv64 march, and dependence on glibc enabling landing pads/shadow stack for the binary. Test signals are build presence and runtime `cfitests` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/cfi_rv_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/cfi_rv_test.h

Purpose: shared low-level CFI helper header. It defines child exit codes and inline syscall macros `my_syscall5`/`my_syscall3` using RISC-V argument registers and `ecall`, and includes `shadowstack.h`. There is no persistence; the macros are compile-time integration points used by `cfitests.c` and `shadowstack.c` to call prctl and `map_shadow_stack` without libc wrappers. Dependencies are RISC-V register conventions, syscall numbers from asm-generic headers, and compiler support for register variables. Risks include clobber constraints being wrong for future compilers, sign-extension of syscall returns, and limited portability outside RISC-V. Test signals are successful direct prctl/syscall calls in CFI/shadow-stack tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/cfi_rv_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/cfitests.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/cfitests.c

Purpose: main RISC-V CFI test binary for landing pads, shadow stack status, CFI ptrace regsets, and shadow-stack subtests. Important functions are `sigsegv_handler`, `register_signal_handler`, `cfi_ptrace_test`, and `main`. Control flow checks `PR_GET_CFI` for branch landing-pad enablement and `PR_GET_SHADOW_STACK_STATUS` for shadow-stack enablement, installs a SIGSEGV handler distinguishing `SEGV_CPERR`, forks a traced child that executes a landing-pad-sensitive `jalr` sequence, reads `NT_RISCV_USER_CFI`, validates enabled CFI/shadow-stack bits and shadow-stack pointer, clears expected landing-pad state with `PTRACE_SETREGSET`, then calls `execute_shadow_stack_tests`. State is child process ptrace stop state, CFI regset, signal handlers, and shadow-stack runtime state. Dependencies are glibc/toolchain CFI enablement, ptrace regset ABI, and kernel CFI support. Risks are exiting hard rather than kselftest skip for missing enablement, fragile inline assembly, and ptrace status assumptions. Test signals are ptrace success messages and shadow-stack kselftest results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/cfitests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/shadowstack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/shadowstack.c

Purpose: implements RISC-V shadow-stack behavior tests called by `cfitests`. Key APIs are `shadow_stack_fork_test`, `shadow_stack_map_test`, `shadow_stack_protection_test`, `shadow_stack_gup_tests`, `shadow_stack_signal_test`, and `execute_shadow_stack_tests`. Control flow reads CSR_SSP during nested calls, verifies shadow stacks survive fork, maps/unmaps shadow-stack memory with `map_shadow_stack`, checks normal writes fault while `/proc/self/mem` GUP writes work, and verifies signal delivery with shadow stack enabled. State includes mapped shadow-stack pages, child processes/statuses, signal handlers, `/proc/self/mem` fd, and global `break_loop`. Dependencies are shadow-stack prctl/syscall support, CSR access, GUP semantics, SIGSEGV handler from `cfitests`, and kselftest. Risks include child reaching unreachable code after expected fault, not always unmapping on early returns, reliance on `/proc/self/mem`, and hard fail when status prctl is unavailable. Test signals are five planned shadow-stack subtest pass/fail lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/shadowstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/shadowstack.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/shadowstack.h

Purpose: declares the shadow-stack test callback table type and exported functions used by CFI tests. It defines `struct shadow_stack_tests` entries with a name and function pointer, the `csr_read` helper/macro for reading RISC-V CSRs, and prototypes such as `execute_shadow_stack_tests` and individual test functions. State is compile-time only. Dependencies are RISC-V CSR syntax and the implementation in `shadowstack.c`. Risks are function signature drift between header and implementation and CSR reads trapping if used without required architecture support. Test signals are successful compilation and valid CSR_SSP reads during runtime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/cfi/shadowstack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/Makefile

Purpose: builds RISC-V `hwprobe`, `cbo`, and `which-cpus` selftests. It adds local `sys_hwprobe.S` as a generated object/library, sets test programs, and includes `../../lib.mk`. State is output binaries and the syscall wrapper object. Dependencies are RISC-V syscall ABI, kernel headers exposing `struct riscv_hwprobe`, and compiler support for inline CBO assembly. Risks are build failures on non-RISC-V or older headers and runtime skips/fails on heterogeneous CPU extension availability. Test signals are three runnable binaries and kselftest pass/fail output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/cbo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/cbo.c

Purpose: validates `riscv_hwprobe` reporting and userspace behavior for Zicboz, Zicbom, Zicbop, and privileged `cbo.inval`. Key functions are `fault_handler`, instruction emitters for CBO/prefetch, `test_zicbop`, `test_zicbom`, `test_zicboz`, `test_no_*`, `check_no_zicbo_cpus`, and `main`. Control flow parses options to expect SIGILL for missing extensions, gets current CPU affinity, probes extension bits and block sizes, ensures extension presence is consistent across selected harts, executes CBO/prefetch instructions, handles faults by advancing PC, and verifies `cbo.zero` memory effects. State includes aligned `mem[4096]`, global `got_fault`, signal handlers, and CPU sets. Dependencies are RISC-V instruction encodings, hwprobe keys, signal ucontext layout, and taskset affinity. Risks are assert-heavy failures, heterogeneous CPU sets requiring user taskset, block-size assumptions (`<=1024` for zero check), and instruction encoding drift. Test signals are planned kselftest results for block sizes, faults, and memory zeroing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/cbo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/hwprobe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/hwprobe.c

Purpose: basic syscall ABI sanity test for `riscv_hwprobe`. It initializes eight key pairs, calls the syscall with a fake all-CPU set, verifies base keys remain recognized and base behavior includes IMA, checks valid NULL CPU-set behavior, checks invalid CPU-set argument combinations fail, verifies existing keys are maintained, and confirms unknown keys are overwritten with `-1` without blocking other pairs. State is local `pairs[]` and a fake CPU bitmap. Dependencies are `riscv_hwprobe` wrapper, kernel hwprobe ABI, and kselftest. Risks are assuming base key range and IMA behavior on all supported kernels, and using `ksft_exit_fail_msg` for sanity failures. Test signals are five planned pass/fail results plus hard failure on impossible base behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/hwprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/hwprobe.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/hwprobe.h

Purpose: local declaration point for the RISC-V hwprobe syscall wrapper. It includes the Linux hwprobe UAPI types and declares `long riscv_hwprobe(struct riscv_hwprobe *pairs, size_t pair_count, size_t cpusetsize, unsigned long *cpus, unsigned int flags)`. There is no runtime state. Integration is all hwprobe/vector tests needing a libc-independent syscall wrapper. Dependencies are compatible UAPI headers and `sys_hwprobe.S`. Risks are signature drift from kernel UAPI and include-order conflicts with system headers. Test signals are successful compilation and correct syscall return values in `hwprobe.c`, `cbo.c`, and `which-cpus.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/hwprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/sys_hwprobe.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/sys_hwprobe.S

Purpose: assembly syscall wrapper for `riscv_hwprobe`. It moves `__NR_riscv_hwprobe` into `a7`, executes `ecall`, and returns through the normal RISC-V calling convention. State is only CPU registers during the call. Integration is linked into hwprobe and vector helper tests so they can call the syscall even when libc lacks a wrapper. Dependencies are RISC-V syscall ABI, asm-generic syscall numbers, and toolchain assembly support. Risks are missing error normalization compared with libc wrappers and syscall number drift in old headers. Test signals are all hwprobe-based tests receiving expected kernel return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/sys_hwprobe.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/which-cpus.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/which-cpus.c

Purpose: tests and exposes the `RISCV_HWPROBE_WHICH_CPUS` flag. It can run as a selftest with no arguments or as a CLI that prints CPUs matching user-specified `key=value` pairs. Key functions are `print_cpulist`, `do_which_cpus`, and `main`. Control flow gets current affinity, optionally parses pairs, calls `riscv_hwprobe(..., RISCV_HWPROBE_WHICH_CPUS)`, and prints/validates CPU sets. The selftest checks invalid cpuset arguments, unknown keys, duplicate keys, matching all online CPUs, matching current affinity, and clearing all CPUs with inverted extension values. State is local CPU sets and probed extension masks. Dependencies are hwprobe ABI, CPU affinity APIs, and homogeneous base behavior. Risks include assert-driven termination on malformed CLI input, CPU hotplug changing counts, and assumptions about extension masks applying to all online CPUs. Test signals are seven kselftest results and useful `cpus:` CLI output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/hwprobe/which-cpus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/Makefile

Purpose: builds and runs RISC-V mmap layout tests. It creates generated files `mmap_default` and `mmap_bottomup`, registers `run_mmap.sh` as the test program, and includes `../../lib.mk`. State is the two small binaries and test script installation. Dependencies are kselftest harness, sys/mman, and shell `ulimit`. Risks include a target typo/dependency naming mismatch (`mmap_tests.h` versus local `mmap_test.h` in the explicit `$(OUTPUT)/mm` rule that is not the main generated-file path), and non-RISC-V execution not being meaningful. Test signals are successful build plus `run_mmap.sh` executing both layout binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_bottomup.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_bottomup.c

Purpose: verifies RISC-V uses bottom-up mmap layout when stack rlimit is unlimited. It contains one kselftest harness test `infinite_rlimit` that expects `memory_layout()` to return `BOTTOM_UP`. State is only two anonymous mappings created by the helper; no cleanup is needed before process exit. Integration is through `run_mmap.sh`, which sets `ulimit -s unlimited` before running this binary. Dependencies are kernel mmap layout policy and the helper header. Risks are running directly without changing stack limit, address-space randomization producing unexpected ordering, and no explicit `munmap`. Test signals are one harness pass/fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_bottomup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_default.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_default.c

Purpose: verifies default RISC-V mmap layout is top-down under the normal stack limit. It contains one kselftest harness test `default_rlimit` expecting `memory_layout()` to return `TOP_DOWN`. State is limited to two anonymous mappings. Integration is `run_mmap.sh`, which runs this before changing stack ulimit. Dependencies are kernel architecture mmap policy and the helper header. Risks include direct execution under an already unlimited stack, ASLR/layout changes, and no `munmap` before process exit. Test signals are one harness pass/fail result.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_default.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_test.h

Purpose: shared helper for RISC-V mmap layout tests. It defines `TOP_DOWN`, `BOTTOM_UP`, protection/flag constants, and `memory_layout()`, which performs two anonymous private mappings and returns whether the second address is higher than the first. State is the process virtual address space after two mappings. Dependencies are `mmap`, resource-limit-driven kernel layout selection, and kselftest harness includes. Risks are interpreting pointer ordering as layout direction under ASLR, not unmapping test allocations, and helper simplicity hiding failures where `mmap` returns `MAP_FAILED`. Test signals are correct expectations in `mmap_default` and `mmap_bottomup`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/mmap_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/run_mmap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/run_mmap.sh

Purpose: orchestrates the two mmap layout binaries with the correct stack rlimit. Control flow saves the original `ulimit -s`, runs `./mmap_default`, sets stack to unlimited, runs `./mmap_bottomup`, then restores the original limit. State is shell process resource limit, which affects child mmap policy. Dependencies are POSIX shell, `ulimit`, and the two built binaries in the working directory. Risks include not restoring the limit if the script exits early, relative path assumptions, and lack of `set -e` meaning a failure in `mmap_default` may not prevent continuing. Test signals are the exit status and harness output of both child programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/mm/run_mmap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/sigreturn/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/sigreturn/Makefile

Purpose: builds the static RISC-V `sigreturn` vector-context selftest. It adds `tools/include`, sets `TEST_GEN_PROGS := sigreturn`, includes `../../lib.mk`, and explicitly links `sigreturn.c` statically. State is only the output binary. Dependencies are RISC-V vector-capable toolchain headers and static link support. Risks are running on kernels without vector signal context support or hardware without V extension. Test signals are successful build and two harness tests in `sigreturn`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/sigreturn/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/sigreturn/sigreturn.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/sigreturn/sigreturn.c

Purpose: verifies RISC-V vector register state across signal delivery and sigreturn. It defines `simple_handle`, `vector_override`, and `vector_sigreturn`, with tests `vector_restore` and `vector_restore_signal_handler_override`. Control flow loads a value into vector register `v0`, deliberately faults with a null load, has the SIGSEGV handler advance PC, optionally locates the vector context in `ucontext` via `RISCV_V_MAGIC` and overwrites vector data, then reads `v0` after sigreturn. State is signal action and vector register/ucontext state. Dependencies are V extension assembly, Linux signal frame vector extension layout, `REG_PC`, and kselftest harness. Risks are aborting on missing vector magic, no skip path for non-vector hardware, and hard-coded context layout. Test signals are restored default value and handler-overridden value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/sigreturn/sigreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/Makefile

Purpose: builds RISC-V vector selftests and helper objects. It generates normal test programs `v_initval`, `vstate_prctl`, `vstate_ptrace`, `validate_v_ptrace`, extended nolibc executables `vstate_exec_nolibc` and `v_exec_initval_nolibc`, and helper objects from `v_helpers.c` and `../hwprobe/sys_hwprobe.S`. State is output binaries/objects. Dependencies are RISC-V vector-capable compiler, nolibc headers, static linking, hwprobe wrapper, and kselftest `lib.mk`. Integration covers prctl, ptrace, exec inheritance, and initial-vector-state tests. Risks are static/nolibc build fragility and cross-compiler extension support. Test signals are all binaries present and runnable, with helper object cleaned by `EXTRA_CLEAN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_exec_initval_nolibc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_exec_initval_nolibc.c

Purpose: nolibc exec-side helper for checking initial vector register values after exec. It executes minimal startup code, reads or touches vector state using inline assembly, and exits with a status consumed by the parent `v_initval`-style tests. State is only process vector registers and exit code. Dependencies are nolibc, RISC-V vector or XTheadVector instruction encoding, and the parent launcher. Integration is `TEST_GEN_PROGS_EXTENDED`, not a standalone kselftest. Risks are difficult diagnostics because nolibc helpers communicate mostly via exit status, illegal instruction on unsupported vector modes, and ABI dependence on exec resetting vector state. Test signals are expected child exit code observed by the parent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_exec_initval_nolibc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_helpers.c

Purpose: shared vector capability and exec-launch helpers. Key APIs are `is_xtheadvector_supported`, `is_vector_supported`, `get_vr_len`, and `launch_test`. Control flow uses `riscv_hwprobe` to check standard ZVE32X and T-Head vector extension bits, reads `vlenb` via CSR or encoded XTheadVector `vsetvli`, forks/execs a requested helper with flags indicating inherit and vendor-vector mode, and returns the child status. State is child process status and hardware vector length. Dependencies are hwprobe wrapper, vendor extension headers, inline assembly, fork/exec/wait. Risks include no error checking on hwprobe calls, vendor instruction clobbering vector state, limited child argument protocol, and ambiguous nonzero statuses. Test signals are correct skips for unsupported vector and expected child control values in prctl/exec tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_helpers.h

Purpose: declares shared vector helper functions for RISC-V vector tests: capability checks, vector register length discovery, and child launch. It has no runtime state. Integration is with `vstate_prctl.c`, `vstate_ptrace.c`, `validate_v_ptrace.c`, and initial-value tests. Dependencies are the implementation in `v_helpers.c` and linked `sys_hwprobe.o`. Risks are signature drift and consumers assuming helpers distinguish standard vector from XTheadVector consistently. Test signals are successful linking and correct skip/execute behavior in vector tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_initval.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_initval.c

Purpose: parent-side test for initial vector register state, including exec behavior through `v_exec_initval_nolibc`. It uses vector capability helpers and launches the nolibc child to ensure vector registers/control state start in the expected initialized condition. State is parent/child process status and vector support detection. Dependencies are `v_helpers`, hwprobe, vector instructions, and the extended child binary in the same output directory. Risks include relative path assumptions, unsupported hardware skips, and exit-code-only diagnostics from the nolibc child. Test signals are kselftest pass/fail for vector initial values and child exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/v_initval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/validate_v_ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/validate_v_ptrace.c

Purpose: deep validation of RISC-V vector ptrace regset semantics for standard Vector 1.0 and XTheadVector. It tests unavailable vector state (`ENODATA`), early debug CSR capture, syscall clobbering of vector state, invalid `PTRACE_SETREGSET` values, and valid CSR updates across clean/dirty vector context transitions. Key structures are kselftest fixtures `v_csr_invalid` and `v_csr_valid` with many variants for `vstart`, `vl`, `vtype`, `vcsr`, `vlenb` multipliers, VLEN bounds, and spec masks. Control flow forks a tracee blocked on `chld_lock`, attaches with ptrace, pokes the lock, advances over `ebreak` by editing `NT_PRSTATUS`, reads/writes `NT_RISCV_VECTOR`, and compares CSR/register state. State is child process, ptrace stops, vector regset buffers sized by `vlenb`, and global synchronization word. Dependencies are vector hwprobe, ptrace regsets, RISC-V CSR semantics, kselftest harness, and CPU support consistency. Risks are assert/assertion-heavy cleanup, leaked allocations on early ASSERT exit, architecture-specific magic constants, and timing around ptrace stops. Test signals are harness results for ENODATA, CSR equality, syscall illegal state, invalid EINVAL cases, and valid persistence across dirty state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/validate_v_ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_exec_nolibc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_exec_nolibc.c

Purpose: nolibc helper used by `vstate_prctl` to validate vector control inheritance and next-exec behavior. Control flow reads `PR_RISCV_V_GET_CONTROL`, optionally forks/execs itself to test inherit, otherwise forks a child that checks inherited control, executes a vector or XTheadVector instruction, and exits with control state; the parent interprets normal exit versus SIGILL according to current/next/off bits. State is vector control prctl state, child exit status, and exec argument flags. Dependencies are nolibc prctl/fork/exec/wait, vector instructions, and constants from Linux prctl headers. Risks include argument parsing using `strcmp(argv[n], "x")` in a way that treats `"x"` as false, exit status truncating control values, and sparse diagnostics. Test signals are exact control value returned to `vstate_prctl` and SIGILL when vector use is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_exec_nolibc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_prctl.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_prctl.c

Purpose: validates `PR_RISCV_V_GET_CONTROL` and `PR_RISCV_V_SET_CONTROL` semantics. It covers no-vector failure paths, enabling current vector state, refusal to disable current enabled vector state with `EPERM`, next-exec on/off, inherit/no-inherit behavior, and invalid control bit patterns. Key helper is `test_and_compare_child`, which sets control and launches `vstate_exec_nolibc`. State is process vector control prctl state and child process status. Dependencies are `v_helpers`, standard or XTheadVector support, prctl constants, and the extended nolibc helper. Risks include inherited vector state affecting later tests, child exit-code truncation, and no-vector tests only valid on hardware without vector. Test signals are kselftest harness results for each control case and printed mismatch diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_ptrace.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_ptrace.c

Purpose: smoke-tests ptrace get/set of RISC-V vector registers. A child marks itself traceable, writes `child_set_val` into vector register `v31`, traps with `ebreak`, then after parent modification reads `v31` and exits success only if it equals `parent_set_val`. The parent waits for SIGTRAP, fetches the vector regset header to learn `vlenb`, reallocates for all 32 vector registers, checks `v31`, writes the parent value through `PTRACE_SETREGSET`, advances PC via `NT_PRSTATUS`, and continues. State is child process ptrace state, allocated regset buffer, random values, and vector register contents. Dependencies are vector or XTheadVector support, ptrace `NT_RISCV_VECTOR`, and kselftest. Risks include pointer arithmetic on `void *`, cleanup if ptrace fails, and no deep CSR validation here. Test signals are two planned results: GETREGSET vector and SETREGSET vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/vector/vstate_ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/Makefile

Purpose: builds the `rlimits-per-userns` kselftest. It sets warning/debug CFLAGS, registers `TEST_GEN_PROGS := rlimits-per-userns`, and includes `../lib.mk`. State is the compiled output binary. Dependencies are user namespace support, libc, and root/capability context sufficient for UID/GID changes. Integration is with the adjacent config file. Risks are runtime privilege/environment requirements not expressed in the Makefile. Test signals are successful build and the binary’s pass/fail exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/config

Purpose: declares `CONFIG_USER_NS=y` for the rlimits-per-userns selftest. There is no code flow or persistent state. Integration is kselftest kernel configuration preparation for user namespace behavior under process limits. Risks are that the test also requires the ability to set UID/GID 60000, unshare user namespaces, and manipulate `RLIMIT_NPROC`; those are runtime policy issues outside this config. Test signals are successful `unshare(CLONE_NEWUSER)` in the child service path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/rlimits-per-userns.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/rlimits-per-userns.c

Purpose: verifies `RLIMIT_NPROC` accounting across user namespaces. The main process sets `RLIMIT_NPROC=1`, forks two children as root, each child sets PDEATHSIG, switches to UID/GID 60000, unshares a user namespace, and execs the same binary as a paused service (`I_AM_SERVICE=1`). The parent polls children and periodically sends SIGUSR1; the test passes when children are killed by SIGUSR1 rather than failing to start because the per-user process limit crossed user-namespace boundaries incorrectly. Key APIs are `setrlimit`, `fork`, `prctl(PR_SET_PDEATHSIG)`, `setgid`, `setuid`, `unshare(CLONE_NEWUSER)`, `execve`, `waitpid`, and signals. State includes service environment, child PIDs/statuses, UID/GID, and process rlimit. Dependencies are user namespaces, privileges to set IDs, and signal delivery. Risks are fixed UID/GID collisions, root-only assumptions, polling races, and noisy `warnx` output. Test signals are final "Test passed" and exit success only when both children die from SIGUSR1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rlimits/rlimits-per-userns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/Makefile

Purpose: builds the restartable sequences selftest suite, including shared `librseq.so`, generated tests, extended benchmarks/tools, and shell test drivers. It sets compiler/linker flags, handles Clang integrated assembler issues, overrides default targets so binaries depend on the shared object and headers, and builds variants with `BUILDOPT_RSEQ_PERCPU_MM_CID`, `BENCHMARK`, and `RSEQ_COMPARE_TWICE`. State is output binaries, shared library, rpath-linked test executables, and installed scripts/settings. Dependencies are pthread/dl, kernel headers, architecture-specific `rseq-*.h`, and dynamic loader behavior. Integration is kselftest `lib.mk` plus run scripts for parameter/syscall/legacy/timeslice tests. Risks include rpath assumptions, shared object load path, compiler asm-goto support, and many generated variants from one source. Test signals are successful build of `basic_test`, `basic_percpu_ops_test`, mm_cid variants, benchmarks, and scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/basic_percpu_ops_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/basic_percpu_ops_test.c

Purpose: stress-tests basic rseq per-CPU operations through a per-CPU spinlock and a per-CPU linked list. It can be built for CPU ID or mm_cid indexing via `BUILDOPT_RSEQ_PERCPU_MM_CID`. Key functions are `rseq_this_cpu_lock`, `rseq_percpu_unlock`, `test_percpu_spinlock_thread`, `test_percpu_spinlock`, `this_cpu_list_push`, `this_cpu_list_pop`, `test_percpu_list_thread`, and `test_percpu_list`. Control flow registers rseq for threads, uses `rseq_cmpeqv_storev` to acquire per-CPU locks, uses `rseq_cmpnev_storeoffp_load` for list pop without ABA concerns, spawns 200 threads for lock increments and 200 threads for list shuffling, then validates sums. State includes aligned per-CPU arrays sized by `CPU_SETSIZE`, thread registrations, list nodes, and CPU affinity. Dependencies are `librseq`, scheduler CPU IDs or mm_cid availability, pthreads, and atomics/barriers from rseq headers. Risks include external affinity changes, huge CPU_SETSIZE memory assumptions, abort-on-error assertions, and mm_cid availability. Test signals are process exit zero after printed `spinlock` and `percpu_list`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/basic_percpu_ops_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/basic_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/basic_test.c

Purpose: basic rseq registration and current CPU/node validation. It registers the current thread, iterates over allowed CPUs by temporarily pinning affinity, and asserts that `sched_getcpu`, `rseq_current_cpu`, `rseq_current_cpu_raw`, and `rseq_cpu_start` agree; it also compares `rseq_current_node_id` with the fallback node lookup. State is thread rseq registration and temporarily changed CPU affinity, restored afterward. Dependencies are `librseq`, scheduler affinity APIs, and node lookup helpers. Risks are assertion failure if affinity changes concurrently, registration failure because libc owns rseq or kernel lacks support, and not using kselftest skip semantics. Test signals are printed `testing current cpu` and exit zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/basic_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/check_optimized.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/check_optimized.c

Purpose: checks that optimized rseq registration path can be used. It calls `__rseq_register_current_thread(true, false)` and exits success only if registration succeeds. State is the current thread’s rseq registration. Dependencies are `librseq`, kernel rseq syscall support, and an environment where registration is allowed. Integration is an extended build artifact that can be used by scripts or packaging checks. Risks are minimal diagnostics and conflict with libc-managed rseq. Test signals are exit zero for optimized registration success and nonzero otherwise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/check_optimized.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/compiler.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/compiler.h

Purpose: compiler compatibility helper for rseq inline assembly templates. It defines `rseq_after_asm_goto()` as a volatile memory-clobber asm barrier to work around historical GCC/Clang `asm goto` miscompilations, token-combining macros, and `rseq_unqual_scalar_typeof` for C/C++ scalar type normalization. There is no runtime state; it shapes generated inline code. Dependencies are C11 `_Generic` for C, C++ type traits when compiled as C++, and compilers accepting empty volatile asm. Risks include broad barrier use affecting optimization, incomplete scalar coverage, and relying on this header in all asm-goto fallthrough/label paths. Test signals are successful compilation and stable rseq critical-section behavior across supported compilers/optimization levels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/legacy_check.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/legacy_check.c

Purpose: verifies legacy rseq ABI behavior where the kernel updates `cpu_id_start`, including during signal handling. Fixture setup calls `__rseq_register_current_thread(true, true)`, skips on `-ENOSYS` or `-EBUSY`, and installs a SIGUSR1 handler that reads `rseq_get_abi()->cpu_id_start`. The test overwrites `cpu_id_start` with `-1`, waits for kernel update, overwrites again, raises SIGUSR1, and checks both the ABI field and handler-observed value changed. State is the current thread’s legacy rseq area and `cpu_id_in_sigfn`. Dependencies are legacy registration availability, signal delivery, and kselftest harness. Risks include glibc-owned rseq causing skip, timing assumptions around `sleep(1)`, and no explicit unregister. Test signals are one harness pass for `legacy_test` or documented skips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rseq/legacy_check.c -->
