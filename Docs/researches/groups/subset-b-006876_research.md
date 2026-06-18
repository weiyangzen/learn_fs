# subset-b-006876 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test.c

Purpose: this is the main nolibc validation binary. It can be built either against nolibc, against a nolibc sysroot, or against a normal libc, and it compares startup state, syscall wrappers, stdlib/string helpers, formatted I/O, and optional stack-protector behavior. The test can also run as PID 1 under a tiny VM, where `prepare()` creates or mounts minimal `/dev`, `/proc`, and `/tmp` support and successful completion may power off the VM instead of returning normally.

Important APIs and types: `struct test` maps suite names to runners; `enum RESULT` and the `EXPECT_*` macro family centralize pass/fail/skip output; `CASE_TEST()` derives stable test IDs from source line numbers. Key helpers include `errorname()`, `test_program_invocation_name()`, `test_getdents64()`, `test_dirent()`, `test_getrandom()`, `test_file_stream*()`, `test_fork()`, `test_timer()`, `test_timerfd()`, `test_mmap_munmap()`, `test_namespace()`, `test_malloc()`, `expect_strtox()`, `expect_vfprintf()`, `test_scanf()`, `test_printf_error()`, and `run_protection()`.

Control flow: constructors set `constructor_test_value`; `main()` records `argc`, `argv`, `envp`, optionally calls `prepare()`, parses either `argv[1]` or `NOLIBC_TEST`, then executes named suites with optional numeric ranges. `run_startup()` validates argv/environ/auxv layout and constructor/linkage behavior. `run_syscall()` exercises many Linux syscalls and error paths, with guards for `/proc`, effective root, libc availability, and `brk()` support. `run_stdlib()` and `run_printf()` check conversion, memory, string, endian, device-number, scanf, printf, and allocation semantics. `run_protection()` forks a child that intentionally smashes a stack buffer and expects `SIGABRT` when nolibc stack protector is enabled.

State and persistence: the binary mutates process-local state heavily: environment parsing, current directory, UTS namespace, resource limits, temp files, stdio buffers, child processes, timers, and anonymous mappings. It may create `/dev`, `/proc`, `/tmp`, device nodes, and mounts when running as init. It writes only test output and does not persist repository state.

Dependencies and integration: it depends on Linux syscall availability, procfs, dev nodes such as `/dev/null`, `/dev/zero`, `/dev/full`, optional root privileges for namespace/chroot cases, and `nolibc-test-linkage.h`. `run-tests.sh` builds and executes this file across architectures via `Makefile.nolibc`.

Risks: line-number-derived test IDs make edits that insert/remove `CASE_TEST()` lines user-visible. Some cases have libc-specific expected behavior, architecture-specific page-size and `O_LARGEFILE` assumptions, and root/procfs-dependent skips. The PID-1 path can reboot or intentionally trigger QEMU debug-exit behavior, so it must be run only in the intended VM harness.

Test signals: individual lines emit `[OK]`, `[FAIL]`, or `[SKIPPED]`; suite totals and final exit status report aggregate errors. A passing test returns zero or powers off cleanly when PID 1; failures return nonzero and may be detected by QEMU/kernel selftest wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/nolibc-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/run-tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/run-tests.sh

Purpose: shell runner for building and running nolibc tests over many target architectures with prebuilt kernel.org nolibc cross toolchains.

Important APIs/functions: option parsing uses `getopt`; `crosstool_arch()` and `crosstool_abi()` translate selftest architecture names to toolchain triples; `download_crosstool()` fetches and extracts `${hostarch}-gcc-${version}-nolibc-${arch}-${abi}.tar.gz`; `swallow_output()` hides successful make output; `test_arch()` configures, builds, runs, and reports one architecture.

Control flow: defaults include GCC 15.2.0, host `x86_64`, cache-backed download/build directories, `system` mode, and all supported arch names. Options select jobs, download permission, cache paths, crosstool version, host arch, build directory, user/system mode, Werror, LLVM, and target arch list. If `-p` is set it downloads all selected toolchains before running. For each arch it checks toolchain presence, constructs a `make -f Makefile.nolibc` invocation with `XARCH`, `CROSS_COMPILE`, optional `LLVM`, and per-arch `O=`, then runs `defconfig` and either `run` or `run-user`.

State and persistence: downloads and extracts toolchains under `${XDG_CACHE_HOME:-$HOME/.cache}/crosstools/`, writes per-arch build trees under `nolibc-tests`, copies `run.out` to `run.out.$arch`, and leaves build artifacts for reuse. It does not edit source files.

Dependencies/integration: requires `curl`, `tar`, GNU `make`, `realpath`, kernel selftest `Makefile.nolibc`, and cross toolchains. It integrates with `nolibc-test.c` as the test payload and with QEMU/user-mode targets provided by nolibc make rules.

Risks: the script uses `set -e`, so an unsupported or failing architecture stops the entire run except for explicit unsupported LLVM/user combinations. Download URLs are fixed to kernel.org layout. `CFLAGS_EXTRA` is appended within `test_arch()` and can accumulate if exported externally. Some arch/mode combinations are skipped by printed message rather than kselftest TAP.

Test signals: per-arch output starts with a left-aligned `arch:` label; unsupported configurations print that status; successful make report output is filtered through `grep passed`; failures dump captured build/run output through `swallow_output()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/run-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ntb/ntb_test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ntb/ntb_test.sh

Purpose: hardware-oriented NTB selftest runner for a pair of non-transparent bridge endpoints. It can test two local loopback devices or coordinate with a remote host via SSH.

Important APIs/functions: `_modprobe()` loads/unloads modules locally and remotely; `split_remote()`, `read_file()`, `write_file()`, and `check_file()` abstract debugfs paths with optional `host:/path` syntax; `find_pidx()` maps peer ports; test functions cover port enumeration, link toggling, doorbells, scratchpads, messages, memory windows, ping-pong counters, MSI, and performance.

Control flow: the script parses options in three phases so options may appear before, between, or after local/remote device arguments. It cleans any already loaded NTB test modules, verifies root, optionally lists devices, then runs `ntb_tool_tests`, `ntb_pingpong_tests`, `ntb_msi_tests`, and `ntb_perf_tests`. `ntb_tool_tests()` derives peer indices, forces link events, exercises doorbells and shared data mechanisms, then removes `ntb_tool`. Performance tests run without DMA and optionally with DMA.

State and persistence: it writes debugfs control files under `${DEBUGFS:-/sys/kernel/debug}` and may write remote debugfs via SSH. It loads and unloads `ntb_tool`, `ntb_perf`, `ntb_pingpong`, `ntb_transport`, and `ntb_msi_test`, with cleanup controlled by `-C`. Temporary comparison files may be created under `/tmp` for remote memory-window reads.

Dependencies/integration: requires root, NTB hardware/drivers, mounted debugfs, working module loading, `dd`, `cmp`, and optionally passwordless root SSH to the remote host. It integrates with kernel NTB test modules and exposes failures through shell exit.

Risks: this is destructive to NTB test module state and link state, and remote command quoting/path handling is simple. A bug in remote temp cleanup uses string comparison against `/tmp/*`, so remote copied files may remain. The line `if ! [[ $$DONT_CLEANUP ]]; then` appears intended to test `DONT_CLEANUP` but expands `$$`, which can make cleanup trap behavior surprising.

Test signals: successful subtests print `Passed`; unsupported optional features print `Unsupported` or module-availability messages; mismatches print to stderr and exit nonzero due to `set -e` or explicit `exit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ntb/ntb_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/Makefile

Purpose: builds the openat2 selftest executables and links them with shared helper code.

Important settings: `CFLAGS` enables `-Wall -O2 -g` plus AddressSanitizer and UBSan. `TEST_GEN_PROGS` lists `openat2_test`, `resolve_test`, and `rename_attack_test`. `LOCAL_HDRS` declares `helpers.h`. Each generated program depends on `helpers.c`.

Control flow/integration: inclusion of `../lib.mk` connects this directory to the kselftest build/install/run framework. For GCC builds it adds `-static-libasan` so ASan is loaded first; clang/LLVM builds omit that flag because clang handles sanitizer linkage differently.

State and dependencies: build outputs are generated programs only. Runtime dependencies come from the C tests: openat2 syscall support, procfs, root/mount namespace permissions for resolver tests, and sanitizer runtime availability.

Risks: sanitizer flags can change timing and memory layout, which matters most for the rename race stress test. Systems without compatible sanitizer libraries or static ASan may fail at build/link time.

Test signals: the Makefile itself has no runtime signal; pass/fail comes from the three kselftest binaries it builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.c

Purpose: shared implementation for openat2 selftests. It normalizes raw syscall return values to either file descriptors or negative errno values and provides path comparison helpers.

Important APIs/functions: `needs_openat2()` currently returns true when `how->resolve` is nonzero. `raw_openat2()`, `sys_openat2()`, `sys_openat()`, and `sys_renameat2()` wrap syscalls or libc calls. `touchat()` creates a file relative to a directory fd. `fdreadlink()` reads `/proc/self/fd/<fd>`. `fdequal()` compares a returned fd target with an expected directory/path combination. The constructor `init()` asserts `struct open_how` size and sets global `openat2_supported`.

Control flow: constructor runs before test `main()`, calls `sys_openat2(AT_FDCWD, ".")`, closes the fd on success, and stores support status. Test files branch on `openat2_supported` to skip or fall back.

State and persistence: no persistent files except those created by callers through `touchat()`. It allocates strings for fd paths and requires callers to free `fdreadlink()` results.

Dependencies/integration: depends on procfs for fd link comparison and kselftest `ksft_exit_fail_msg()` via helper macros. It is linked into all openat2 test binaries through the Makefile rule.

Risks: `fdequal()` compares textual `/proc/self/fd` link targets, so mount namespace changes, deleted paths, or procfs absence can produce false negatives. `touchat()` uses `O_CREAT` without an explicit access mode, relying on default flag behavior used by these tests.

Test signals: this file has no standalone tests; failures surface as immediate kselftest exits from `E_*` helpers or as pass/fail decisions in openat2 test binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.h

Purpose: public helper contract for the openat2 selftests, including fallback syscall numbers, openat2 ABI structures, resolver flags, assertions, and wrapper declarations.

Important APIs/types: defines `struct open_how` with 64-bit `flags`, `mode`, and `resolve`; `OPEN_HOW_SIZE_VER0`; fallback `__NR_openat2`; fallback `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, `RESOLVE_NO_SYMLINKS`, `RESOLVE_BENEATH`, and `RESOLVE_IN_ROOT`; `ARRAY_LEN()` and `BUILD_BUG_ON()`. The `E_func` family wraps libc/syscall helpers and aborts through kselftest on unexpected failure.

Control flow/integration: C test files include this header to share ABI definitions independent of userspace headers. The `extern bool openat2_supported` flag is initialized in `helpers.c` and consumed by tests to report skip rather than fail when the kernel lacks openat2.

State and dependencies: no runtime state beyond the extern flag declaration. It depends on Linux integer types, errno, kselftest, and GNU extensions.

Risks: fallback syscall number `437` is architecture-sensitive in general, but the kernel selftest environment expects the correct arch headers or this fallback. Fallback flag definitions must remain synchronized with kernel UAPI or tests could check the wrong bits.

Test signals: indirectly controls hard failures via `E_*` macros and compile-time checks via `BUILD_BUG_ON()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/openat2_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/openat2_test.c

Purpose: validates the openat2 syscall ABI: extensible `struct open_how` sizing/zero-extension behavior, pointer misalignment handling, open flag validation, mode validation, resolve flag conflicts, and unknown bit rejection.

Important APIs/types/functions: `struct open_how_ext` simulates future ABI extensions; `struct struct_test` drives size/trailing-data cases; `struct flag_test` drives flag/mode/resolve cases. `test_openat2_struct()` uses `raw_openat2()` with 13 deliberate alignment offsets. `test_openat2_flags()` uses `sys_openat2()`, `fcntl(F_GETFL/F_GETFD)`, and kselftest result functions.

Control flow: `main()` sets a plan of `13 * 7 + 25` tests. The struct suite checks normal, larger zero-padded, too-small, zero-sized, and larger nonzero-tail arguments against expected success, `-EINVAL`, or `-E2BIG`. The flag suite checks combinations such as `O_TMPFILE` conflicts, `O_PATH` allowed/disallowed companions, valid and invalid `how.mode`, `RESOLVE_BENEATH | RESOLVE_IN_ROOT`, invalid resolve bits, and high unknown flag bits. Unsupported `openat2` skips tests; filesystem-specific `-EOPNOTSUPP` for valid `O_TMPFILE` combinations is skipped.

State and persistence: may create/unlink `/tmp/ksft.openat2_tmpfile` for `O_CREAT` cases. Otherwise state is transient fds and allocations.

Dependencies/integration: linked with `helpers.c`; relies on openat2 syscall support and kselftest output. Sanitizers are enabled by the directory Makefile.

Risks: architecture-specific `O_LARGEFILE` fallback is acknowledged as wrong for some architectures, so related flag validation may be fragile there. Misalignment tests rely on malloc and usercopy behavior rather than kernel-internal visibility.

Test signals: kselftest TAP-style pass/skip/fail lines for each struct variation and flag case; nonzero fail/error counts cause `ksft_exit_fail()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/openat2_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/rename_attack_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/rename_attack_test.c

Purpose: stress-tests `RESOLVE_BENEATH` and `RESOLVE_IN_ROOT` against a concurrent rename-exchange attack that attempts to make a relative path escape its starting directory.

Important APIs/functions: `setup_testdir()` creates a temporary root with `a/c` and `b`. `spawn_attack()` forks a child that continuously calls `renameat2(..., RENAME_EXCHANGE)` swapping `a/c` and `b`. `test_rename_attack()` performs 400000 open attempts against a deeply nested `c/../../...` victim path and classifies results.

Control flow: `main()` plans two tests and calls `test_rename_attack()` for `RESOLVE_BENEATH` and `RESOLVE_IN_ROOT`. Each run opens `a` as the starting dirfd, launches the rename loop, then calls `sys_openat2()` when supported or `openat()` fallback otherwise. It counts `-EAGAIN`, `-EXDEV`, other errors, successes, and escapes; any escape fails the test. The attacker is killed at the end.

State and persistence: creates a temporary directory under `/tmp` and a child process. It does not remove the temporary tree explicitly. It mutates directory names in a tight loop while the parent performs lookups.

Dependencies/integration: depends on `renameat2(RENAME_EXCHANGE)`, openat2 resolver semantics, procfs-based fd comparison from `fdequal()`, and scheduler timing. It is built with sanitizers via the Makefile.

Risks: race tests can be sensitive to CPU scheduling and sanitizer overhead. If openat2 is unsupported, the fallback openat path is expected to show vulnerability potential but the test still labels the resolver mode names; this path is primarily diagnostic.

Test signals: prints non-escape counters and a pass/fail line reporting number of escapes over 400000 runs. Any kselftest fail/error exits nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/rename_attack_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/resolve_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/resolve_test.c

Purpose: matrix test for openat2 path-resolution flags using a crafted directory tree with regular directories, relative and absolute symlinks, procfs magic links, a tmpfs mount point, and paths designed to escape or be scoped to a dirfd.

Important APIs/types/functions: `setup_testdir()` unshares the mount namespace, makes `/tmp` private, builds the test tree, mounts tmpfs at `mnt`, and creates all links/files. `struct basic_test` describes a case: optional starting directory, path, `open_how`, expected pass/fail, and expected fd target or errno. `test_openat2_opath_tests()` iterates 88 cases.

Control flow: `main()` requires effective root, sets a plan of 88, and runs the matrix. Tests auto-add `O_PATH` unless using `O_CREAT`, open the starting dirfd, duplicate it into a hardcoded fd used by procfs magic-link cases, then call `sys_openat2()`. Passing cases are checked with `fdequal()`, failing cases with negative errno. Unsupported openat2 converts all cases to skip.

State and persistence: creates a temp tree under `/tmp`, unshares/mutates the mount namespace, mounts tmpfs, creates files through `O_CREAT`, opens `/dev/null`, and allocates strings. It does not explicitly unmount/remove the tree, relying on process/mount namespace lifetime.

Dependencies/integration: requires root or CAP_SYS_ADMIN for `unshare(CLONE_NEWNS)` and mount operations, procfs for magic links and fd paths, and helper wrappers. It validates `RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, `RESOLVE_NO_XDEV`, `RESOLVE_NO_MAGICLINKS`, and `RESOLVE_NO_SYMLINKS`.

Risks: mount namespace and `/proc` assumptions make this unsuitable for restricted containers. Textual path comparison can be brittle under unusual `/tmp` or procfs configurations. The root requirement is enforced even though the file notes capability-specific checks would be more precise.

Test signals: kselftest prints one pass/fail/skip line per named resolver case. Any mismatch in fd target or errno increments fail count and exits nonzero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/openat2/resolve_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/Makefile

Purpose: builds the PCI endpoint kselftest binary.

Important settings: `CFLAGS` enables optimization, `-Wall`, kernel header includes, and `-Wl,-no-as-needed`. `LDFLAGS` links realtime, pthread, and math libraries. `TEST_GEN_PROGS` contains `pci_endpoint_test`.

Control flow/integration: inclusion of `../lib.mk` connects the binary to the kselftest build and install rules.

State/dependencies: no runtime state in the Makefile. The built test depends on the PCI endpoint test character device and kernel UAPI header `pcitest.h`.

Risks: link flags may be broader than currently needed but keep compatibility with harness/library usage. Missing kernel headers or endpoint config will fail build or runtime.

Test signals: build success produces the test executable; runtime signals come from `pci_endpoint_test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/config

Purpose: declares kernel configuration needed for the PCI endpoint tests.

Important settings: enables `CONFIG_PCI_ENDPOINT=y`, `CONFIG_PCI_ENDPOINT_CONFIGFS=y`, and test endpoint/function drivers `CONFIG_PCI_EPF_TEST=m` and `CONFIG_PCI_ENDPOINT_TEST=m`.

Control flow/integration: consumed by kselftest/kernel config tooling to ensure the endpoint subsystem, configfs support, endpoint function test driver, and endpoint test driver are available before running `pci_endpoint_test`.

State and dependencies: no runtime state. It describes module/built-in requirements.

Risks: having these configs does not guarantee suitable hardware, endpoint configuration, or `/dev/pci-endpoint-test.0` existence; runtime can still fail or skip.

Test signals: config is declarative; pass/fail comes from build config checks and the C selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/pci_endpoint_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/pci_endpoint_test.c

Purpose: kselftest harness for the PCI endpoint test driver exposed at `/dev/pci-endpoint-test.0`. It validates BAR accessibility, IRQ modes, data transfer paths, and doorbell support.

Important APIs/types/functions: `pci_ep_ioctl(cmd, arg)` normalizes `ioctl()` results to negative errno. Fixtures `pci_ep_bar`, `pci_ep_basic`, `pci_ep_data_transfer`, and `pcie_ep_doorbell` open/close the device. Variants cover BAR0-BAR5 and memcpy vs DMA data-transfer modes. It uses `struct pci_endpoint_test_xfer_param` and `PCITEST_*` ioctl commands from `pcitest.h`.

Control flow: BAR tests run `PCITEST_BAR` and `PCITEST_BAR_SUBRANGE`, skipping disabled/reserved/unsupported BARs and resource-short cases. Basic tests run consecutive BAR, legacy IRQ, MSI vectors 1..32, and MSI-X vectors 1..2048 after setting and confirming IRQ type. Transfer tests set AUTO IRQ and run read/write/copy across sizes 1, 1024, 1025, 1024000, and 1024001 with and without DMA. Doorbell test sets AUTO IRQ and skips unsupported doorbell.

State and persistence: opens a character device and changes endpoint IRQ mode through ioctls. No files are persisted.

Dependencies/integration: requires endpoint hardware or virtual setup, loaded endpoint test drivers, `/dev/pci-endpoint-test.0`, and the matching UAPI header.

Risks: hardware capabilities vary widely, so skips are expected. MSI-X loop is large and may be slow. Tests assume a single fixed test device name and can fail on systems exposing a different instance.

Test signals: kselftest harness `ASSERT`, `EXPECT`, and `SKIP` lines identify unsupported BARs/features, ioctl setup failures, or data/IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pci_endpoint/pci_endpoint_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/Makefile

Purpose: registers PCIe bandwidth-control shell tests with kselftest.

Important settings: `TEST_PROGS` is `set_pcie_cooling_state.sh`, the top-level executable. `TEST_FILES` is `set_pcie_speed.sh`, a helper installed beside the runner.

Control flow/integration: `../lib.mk` handles install and run integration. The top-level script discovers sysfs devices and invokes the helper.

State/dependencies: no build products. Runtime depends on sysfs, thermal cooling devices, and PCIe link-speed attributes.

Risks: helper must be installed in the working directory because the runner invokes `./set_pcie_speed.sh`.

Test signals: shell scripts print pass/fail/skip and return kselftest-compatible status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_cooling_state.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_cooling_state.sh

Purpose: top-level PCIe bandwidth-control test. It finds a thermal cooling device of type `PCIe_Port_Link_Speed`, maps it to the corresponding PCI device current-link-speed sysfs file, and delegates state transitions to `set_pcie_speed.sh`.

Important functions: `prerequisite()` enforces root, mounted sysfs, thermal cooling devices, and at least one PCIe link-speed cooling device. `find_pcie_port()` optionally filters by BDF and selects the port with the highest current speed delta. `find_sysfs_pci_dev()` derives `/sys/bus/pci/devices/<BDF>/current_link_speed`. `parse_arguments()` supports `-d <BDF>` and `-h`.

Control flow: parse args, run prerequisite checks, locate a cooling device, locate the PCI link-speed file, then execute `./set_pcie_speed.sh "$testport" "$sysfspcidev"` and return its status.

State and persistence: reads sysfs and delegates writes to the helper. It does not persist state itself.

Dependencies/integration: requires root, sysfs, thermal cooling device naming convention `PCIe_Port_Link_Speed[_BDF]`, readable PCI `current_link_speed`, and the helper installed in the current directory.

Risks: the script discovers sysfs mount via `mount -t sysfs | head -1`, which may be brittle with unusual mount output. Some path probes use unquoted globs/variables. The helper invocation assumes current working directory is the installed test directory.

Test signals: prerequisite failures print `skip all tests:` and exit 4. Helper pass/fail is propagated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_cooling_state.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_speed.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_speed.sh

Purpose: helper that writes PCIe thermal cooling states and checks that each state maps to the expected `current_link_speed` string.

Important data/functions: `PCIELINKSPEED` maps speed-state indices to strings from 2.5 through 64.0 GT/s PCIe. `set_state()` writes `cur_state`, sleeps one second, reads link speed, computes `expected_linkspeed=maxstate-state`, and records failure on mismatch. `cleanup_skip()` restores the old state and exits with kselftest skip code.

Control flow: reads `oldstate` and `maxstate`, installs an EXIT trap that restores state as skip on unexpected termination, then iterates from `maxstate` down to `oldstate`. After normal completion it clears the trap, prints `[PASS]` or `[FAIL]`, and exits with accumulated status.

State and persistence: mutates `$coolingdev/cur_state` and restores the original state only on trapped skip/error path. During successful runs the final state is `oldstate` because the loop descends to it.

Dependencies/integration: requires writable thermal cooling sysfs state files and readable PCI `current_link_speed`. It is called by `set_pcie_cooling_state.sh`.

Risks: assumes link-speed strings exactly match the array, and that one second is enough for hardware to settle. Array indexing fails conceptually if `max_state - state` exceeds known speeds.

Test signals: mismatch lines name expected and actual speeds; final line is `set_pcie_speed [PASS]` or `[FAIL]`; exit code is zero or one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pcie_bwctrl/set_pcie_speed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/Makefile

Purpose: builds perf event selftest binaries.

Important settings: `CFLAGS` includes kernel headers, `-Wall`, and `-Wl,-no-as-needed`; `LDFLAGS` links pthread. `TEST_GEN_PROGS` contains `sigtrap_threads`, `remove_on_exec`, `watermark_signal`, and `mmap`.

Control flow/integration: inclusion of `../lib.mk` gives standard kselftest build/run behavior.

State/dependencies: no persistent state. Runtime tests depend on `CONFIG_PERF_EVENTS`, perf_event_open permissions, signal delivery, mmap support, and hardware/software event sources.

Risks: perf permissions (`perf_event_paranoid`/capabilities) can cause skips or failures depending on the test. Some tests are timing-sensitive and use signals/forks/threads.

Test signals: build success produces four binaries; runtime results come from kselftest harness in each C file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/config

Purpose: declares the kernel config prerequisite for perf event selftests.

Important setting: `CONFIG_PERF_EVENTS=y`.

Control flow/integration: consumed by kselftest config tooling to ensure the perf events subsystem is available.

State and dependencies: declarative only; it does not ensure permissions or availability of particular PMU events.

Risks: runtime can still skip or fail if `perf_event_open` is restricted by sysctl/capabilities or if no mappable/AUX-capable event exists.

Test signals: none directly; C tests provide pass/fail/skip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/mmap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/mmap.c

Purpose: verifies perf ring-buffer and AUX mappings cannot be partially punched, overwritten, or invalidly remapped in ways that break perf VMA invariants.

Important APIs/types/functions: fixture `perf_mmap` owns a perf fd, mapped pointer, and reserved address region. Variants `rb` and `aux` cover base ring buffer and AUX buffer. `read_event_type()` reads PMU type IDs from `/sys/bus/event_source/devices/*/type`.

Control flow: setup reserves a PROT_NONE region, scans event sources for a `perf_event_open()` target that can be mmaped, optionally checks AUX support by setting `perf_event_mmap_page.aux_offset/aux_size`, then opens a final fd and maps the selected buffer at fixed addresses. Tests try invalid `mremap()` splits, valid whole remap, invalid `munmap()` holes, and invalid anonymous `MAP_FIXED` overlays.

State and persistence: creates perf fds and process mappings only; teardown unmaps the whole reserved region and closes the fd.

Dependencies/integration: requires sysfs event source directory, `perf_event_open`, mmapable event, and for AUX variant an AUX-capable PMU. Permission failures produce skip.

Risks: availability is platform-dependent. Pointer arithmetic on `void *` relies on GNU C. Fixed mapping behavior is sensitive to kernel VMA semantics being tested.

Test signals: setup skips with `perf not available`, `No mappable perf event found`, `No permissions`, or `No AUX event found`; assertions fail on unexpected mapping/remap/unmap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/remove_on_exec.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/remove_on_exec.c

Purpose: tests `perf_event_attr.remove_on_exec` combined with inherited `sigtrap` events. It ensures forked children inherit events, but execed children have inherited events removed without affecting parent or non-exec siblings.

Important APIs/functions: `make_event_attr()` creates an inherited hardware instructions event with `remove_on_exec=1` and `sigtrap=1`. `sigtrap_handler()` counts `TRAP_PERF` signals. Fixture installs SIGTRAP handler and opens the event with `PERF_FLAG_FD_CLOEXEC`. `exec_child()` is the exec target selected by `argv[0] == "exec_child"`.

Control flow: `fork_only` verifies a forked child can enable the inherited event and trigger SIGTRAP. `fork_exec_then_enable` forks one non-exec child and one exec child, waits for the exec child to spin, enables the event, verifies exec child remains alive until killed, and confirms parent/non-exec child still receive events. `enable_then_fork_exec` enables before fork+exec and expects no trap in the exec child. `exec_stress` repeats fork+exec with mixed disabled/enabled timing.

State and persistence: creates children, pipes, signal handlers, and a perf fd; no persistent files. Exec uses `/proc/self/exe`.

Dependencies/integration: needs perf hardware instruction event access, procfs, SIGTRAP `TRAP_PERF` definitions from kernel headers, and signal delivery.

Risks: busy waits on `signal_count` can hang if perf events never fire after setup succeeds. Hardware counter availability and perf permissions may vary. It intentionally kills exec children.

Test signals: kselftest assertions plus hangs/timeouts in buggy cases; exec children should remain running until killed if remove-on-exec works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/remove_on_exec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/sigtrap_threads.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/sigtrap_threads.c

Purpose: validates synchronous perf SIGTRAP delivery for inherited breakpoint events across threads, including enable, modify, stress, and enable/disable racing behavior.

Important APIs/types/functions: global `ctx` tracks desired thread signal sum, signal count, watched variable, and first `siginfo_t`. `make_event_attr()` creates a `PERF_TYPE_BREAKPOINT` event on `ctx.iterate_on` with `inherit_thread`, `remove_on_exec`, `sigtrap`, and `sig_data`. `sigtrap_handler()` verifies `TRAP_PERF`, records first siginfo, and subtracts the current tid from `tids_want_signal`. `test_thread()` coordinates through a barrier and repeatedly reads/writes the watched variable.

Control flow: fixture installs SIGTRAP handler, opens disabled perf event, and starts five threads blocked on a barrier. `remain_disabled` expects no signals. `enable_event` enables and expects one signal per thread plus one in parent. `modify_and_enable_event` changes attributes and validates new `sig_data`. `signal_stress` expects `NUM_THREADS * 3000` signals. `signal_stress_with_disable` toggles enable/disable until enough signals arrive.

State and persistence: process-local threads, atomic counters, signal handler, and perf fd. No filesystem state.

Dependencies/integration: requires hardware breakpoint perf support usable by the current user, pthreads, and kernel siginfo fields for perf.

Risks: timing-sensitive under heavy load; stress counts require reliable synchronous breakpoint delivery. Tests may hang if signals stop arriving after successful setup.

Test signals: kselftest assertions check counts, `si_addr`, `si_perf_type`, and `si_perf_data`; failures indicate perf inheritance or signal metadata regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/sigtrap_threads.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/watermark_signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/watermark_signal.c

Purpose: verifies a perf event configured with watermark wakeup can deliver asynchronous `SIGIO` to the owning process while waiting on a stopped child.

Important APIs/functions: `handle_sigio()` increments `sigio_count`; `do_child()` raises `SIGSTOP`, sleeps in a loop, raises `SIGSTOP` again, then exits. The test uses `PERF_TYPE_SOFTWARE` / `PERF_COUNT_SW_DUMMY`, `context_switch`, `watermark`, `wakeup_watermark=1`, `FASYNC`, `F_SETOWN`, and `F_SETSIG`.

Control flow: install SIGIO handler, fork child and wait for initial stop, open a perf event targeted at the child, configure async notification, mmap the perf buffer, enable the event, continue child, then expects `waitpid(..., WSTOPPED)` to be interrupted by SIGIO and `sigio_count >= 1`. Cleanup unmaps, closes, kills child, waits, and restores handler.

State and persistence: transient child, perf fd, mmaped ring buffer, and process signal handler. No persistent files.

Dependencies/integration: requires perf_event_open permission for child monitoring and signal delivery. Uses kselftest harness.

Risks: `mmap()` failure check compares against `NULL` rather than `MAP_FAILED`, so one failure mode may not be caught precisely. Timing depends on context-switch event generation and signal delivery.

Test signals: kselftest `EXPECT_*` assertions and stderr diagnostics; success requires at least one SIGIO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/perf_events/watermark_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/Makefile

Purpose: builds PID namespace selftests.

Important settings: `CFLAGS` adds debug info and kernel header includes. `TEST_GEN_PROGS` lists `regression_enomem`, `pid_max`, and `pidns_init_via_setns`. `LOCAL_HDRS` depends on the shared pidfd helper header.

Control flow/integration: includes `../lib.mk` for standard kselftest rules and pulls helper APIs from `../pidfd/pidfd.h`.

State/dependencies: no persistent state. Runtime requires PID and user namespaces, procfs remounting for some tests, and clone3/pidfd helpers.

Risks: tests need namespace permissions and may fail in locked-down containers.

Test signals: build outputs three executables; runtime pass/fail/skip comes from C files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/config

Purpose: declares namespace config prerequisites for PID namespace tests.

Important settings: `CONFIG_PID_NS=y` and `CONFIG_USER_NS=y`.

Control flow/integration: used by kselftest config checks before running PID namespace binaries.

State/dependencies: declarative only. It does not guarantee that unprivileged user namespaces are enabled by runtime policy.

Risks: sysctl or container policy can still block `unshare(CLONE_NEWUSER)` or `CLONE_NEWPID`.

Test signals: none directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pid_max.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pid_max.c

Purpose: verifies that `/proc/sys/kernel/pid_max` limits are enforced inside PID namespaces, including nested namespace interactions and ancestor limits.

Important APIs/functions: `do_clone()` wraps `clone()`/`__clone2()` with an allocated stack. Callback functions mount private procfs, write `pid_max`, fork many children, and validate PID allocation. Test cases are `pid_max_simple`, `pid_max_nested_limit`, and `pid_max_nested`.

Control flow: each test clones into a new PID and mount namespace. Callbacks make `/` private, detach/remount `/proc`, open `pid_max`, write 400 or 500, then fork children until limits should wrap or fail. Nested cases fill the outer namespace, create inner namespaces, and verify inner allocation cannot exceed the ancestor's configured limit.

State and persistence: mutates mount namespace, remounts procfs, writes pid_max inside the namespace, forks hundreds of short-lived children, and reaps them. Effects are namespace-scoped.

Dependencies/integration: depends on PID namespaces, mount namespaces, procfs, and `wait_for_pid()` from `pidfd.h`. Root or user namespace permissions must allow namespace creation and proc remounts.

Risks: high fork counts can be slow or affected by process limits. Incorrect cleanup could leave children until namespace teardown. The code assumes pid_max writes are namespace-scoped and accepted at the selected values.

Test signals: kselftest asserts clone success and child callback exit status zero; callback stderr messages identify limit violations or mount/write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pid_max.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pidns_init_via_setns.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pidns_init_via_setns.c

Purpose: tests creating a PID namespace via `unshare(CLONE_NEWPID)`, joining it through `setns()` on `pid_for_children`, and becoming init/PID 1 in the joined namespace. A second test validates `clone3()` `set_tid` across nested PID namespaces.

Important APIs/functions: uses pipe synchronization, `/proc/<pid>/ns/pid_for_children`, `setns()`, `fork()`, `sys_clone3()`, and `set_tid[] = {1, 1001}`. Helpers `pidns_init_via_setns_set_tid_*` parse `/proc/self/status` `NSpid:` to confirm assigned PIDs.

Control flow: first test optionally unshares a user namespace if unprivileged, parent creates new PID namespace, child joins it and forks grandchild, grandchild checks `getpid() == 1`. The set_tid test requires root, creates an outer PID namespace, wrapper creates a child, wrapper unshares user and PID namespaces, child joins wrapper's `pid_for_children`, clone3 creates grandchild with desired set_tid values, and grandchild verifies NSpid suffix.

State and persistence: creates nested namespaces and short-lived children only. Reads procfs status and namespace fds.

Dependencies/integration: requires PID/user namespace support, procfs, `clone3` set_tid support, and root for the set_tid case.

Risks: namespace policy restrictions can fail even when kernel config is enabled. The set_tid path relies on exact `NSpid:` formatting and available PID 1001 in the outer namespace.

Test signals: kselftest assertions; set_tid test skips when not root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/pidns_init_via_setns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/regression_enomem.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/regression_enomem.c

Purpose: regression test for PID namespace init death semantics and pid reservation error reporting. It expects a second fork in a PID namespace whose init has exited to fail with `ENOMEM`.

Important APIs/functions: single kselftest `TEST(regression_enomem)` uses optional `unshare(CLONE_NEWUSER)`, `unshare(CLONE_NEWPID)`, `fork()`, and shared `wait_for_pid()`.

Control flow: if unprivileged, first enters a user namespace. Then it unshares a new PID namespace, forks a child that exits successfully and is waited. A subsequent `fork()` is expected to fail with `errno == ENOMEM`, matching kernel behavior when the namespace's init process is gone.

State and persistence: namespace and child process state only; no files.

Dependencies/integration: requires user/PID namespaces and correct kernel fork error behavior.

Risks: container policy can block namespace creation. The expected `ENOMEM` is kernel-specific semantic behavior and should not be generalized to ordinary fork failures.

Test signals: kselftest pass on expected failure; assertion failure if second fork succeeds or reports a different errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pid_namespace/regression_enomem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/Makefile

Purpose: builds the pidfd selftest suite and the helper executable used by exec-related tests.

Important settings: `CFLAGS` includes debug info, kernel/tool includes, pthread, and `-Wall`. `TEST_GEN_PROGS` lists core pidfd, poll, wait, getfd, setns, file-handle, bind-mount, info, xattr, setattr, and autoreap tests. `TEST_GEN_PROGS_EXTENDED` builds `pidfd_exec_helper`.

Control flow/integration: inclusion of `../lib.mk` provides standard kselftest handling. The extended helper is installed/built but not run directly as a test.

State/dependencies: no runtime state. Runtime depends on pidfd syscalls, clone3, namespace support, pidfs ioctls, and sometimes mount APIs.

Risks: several listed programs are outside this subset but are part of the same build target. New kernel features such as autoreap/autokill may skip on older kernels.

Test signals: build success for all listed programs; runtime signals come from each binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/config

Purpose: declares kernel config prerequisites for pidfd tests.

Important settings: enables UTS, IPC, USER, PID, NET, TIME namespaces, cgroups, and checkpoint/restore.

Control flow/integration: used by kselftest config tooling to request namespace and checkpoint/restore functionality needed by pidfd tests.

State/dependencies: declarative only. It does not ensure runtime permissions, pidfs feature availability, or clone3 extensions.

Risks: feature tests may still skip/fail on older kernels or restricted environments even when these config symbols are enabled.

Test signals: none directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd.h

Purpose: shared pidfd test header providing fallback constants, pidfs ioctl definitions, `struct pidfd_info`, syscall wrappers, child creation, wait helpers, and EINTR-safe I/O helpers.

Important APIs/types: defines fallback `FD_PIDFS_ROOT`, `P_PIDFD`, clone flags, pidfd syscall numbers, `PIDFD_NONBLOCK`, `PIDFD_THREAD`, self pidfd constants, `PIDFD_GET_*_NAMESPACE`, `PIDFD_GET_INFO`, `PIDFD_INFO_*`, coredump flags, and `struct pidfd_info`. Helpers include `sys_waitid()`, `wait_for_pid()`, `sys_pidfd_open()`, `sys_pidfd_send_signal()`, `sys_pidfd_getfd()`, `sys_memfd_create()`, `create_child()`, `read_nointr()`, `write_nointr()`, and `sys_execveat()`.

Control flow/integration: test files include this header to avoid dependence on newest system headers. `create_child()` uses `clone3()` with `CLONE_PIDFD` and optional flags, returning the child pid while storing the pidfd. `wait_for_pid()` loops on EINTR and reports non-exited children through kselftest messages.

State and persistence: no persistent state. Helpers create processes/fds or perform syscalls on caller request.

Dependencies/integration: depends on kselftest, clone3 selftest definitions, Linux syscall ABI, and pidfs ioctl ABI.

Risks: fallback constants must stay synchronized with kernel UAPI. Tests compiled against older libc headers rely heavily on these definitions; mismatches can cause false failures.

Test signals: helper failures usually surface as kselftest assertion failures or diagnostic messages in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_autoreap_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_autoreap_test.c

Purpose: tests newer clone3 pidfd lifecycle extensions: `CLONE_AUTOREAP`, `CLONE_NNP`, and `CLONE_PIDFD_AUTOKILL`, including validation failures, exit reporting, reparenting, multithreaded exit, inheritance, no_new_privs, capabilities, and autokill ownership.

Important APIs/functions: fallback flag definitions, `drop_all_caps()`, `create_autoreap_child()`, and `create_autokill_child()` wrap clone3 argument setup. Tests use `poll()` on pidfds, `PIDFD_GET_INFO`, `sys_pidfd_send_signal()`, `waitpid()`, socketpairs, pthreads, `prctl(PR_SET_CHILD_SUBREAPER)`, and `PR_GET_NO_NEW_PRIVS`.

Control flow: early tests validate accepted/rejected flag combinations. Basic/signaled tests create autoreap children and verify pidfd readability, exit code/signal through `PIDFD_GET_INFO`, and no waitable zombie. Reparent and multithreaded tests verify autoreap across subreaper reparenting and after all threads exit. No-inherit confirms grandchildren are normal waitable children. NNP tests verify only `CLONE_NNP` sets no_new_privs and rejects thread use. Autokill tests verify closing the clone3-created pidfd kills the child, that ordinary `pidfd_open()` fds do not trigger autokill, and that capability/NNP requirements are enforced.

State and persistence: many short-lived children, pidfds, sockets, threads, signal kills, and capability changes. No files persisted. The `autokill_requires_cap_sys_admin` test drops all capabilities in its process.

Dependencies/integration: requires kernel support for these clone3 extension flags, pidfd polling, pidfs info ioctl, pthreads, and root/CAP_SYS_ADMIN for one positive capability test. Unsupported features skip on `EINVAL`.

Risks: this file targets very new kernel behavior; older kernels will skip or fail depending on errno. Capability dropping is irreversible within that test process. Timing uses sleeps and poll timeouts.

Test signals: kselftest harness assertions and skips; expected unsupported kernels report skip for feature-specific tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_autoreap_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_bind_mount.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_bind_mount.c

Purpose: validates pidfds as mountable pidfs objects: cloning a detached mount from a pidfd, attaching it to the filesystem, and reopening/verifying identity.

Important APIs/types/functions: fixture stores a temp path, temp fd, self pidfd, stat data, generation numbers from `FS_IOC_GETVERSION`, and unmount state. Tests use `sys_open_tree()`, `move_mount()`, procfs fd reopening, `fstat()`, and `ioctl(FS_IOC_GETVERSION)`.

Control flow: setup unshares mount namespace, creates a temp file path, opens a self pidfd, records stat and generation. `bind_mount` clones an open tree from the pidfd with `AT_EMPTY_PATH` and attaches it over the temp file. `reopen` opens `/proc/self/fd/<pidfd>` and compares identity. `bind_mount_reopen` mounts then opens the attached path and compares identity/generation. Teardown closes, unmounts if needed, and unlinks.

State and persistence: creates and removes a temp file, unshares mount namespace, may mount pidfs over that temp file, and opens pidfds. Mount effects are namespace-scoped.

Dependencies/integration: requires mount namespace permission, pidfs mount support, `open_tree`/`move_mount` wrappers from `../filesystems/wrappers.h`, procfs, and FS generation ioctl support.

Risks: restricted environments may block unshare or mount syscalls. Teardown asserts unmount/unlink success, so partial setup failures can cascade if state tracking is wrong.

Test signals: kselftest harness assertions; identity mismatch or mount/reopen failure fails the test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_bind_mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_exec_helper.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_exec_helper.c

Purpose: minimal exec target used by pidfd thread/exec tests. It parks the execed process until killed.

Important API/function: `main()` calls `pause()` and exits failure if `pause()` returns; otherwise process lifetime is controlled by signals.

Control flow: after exec, the process blocks in `pause()`. Normal test cleanup sends a signal, so this program does not report success independently.

State and persistence: no filesystem state; it only holds a process alive.

Dependencies/integration: built as `TEST_GEN_PROGS_EXTENDED` and executed by `pidfd_info_test.c` via `execveat(AT_FDCWD, "pidfd_exec_helper", ...)`.

Risks: must be discoverable in the test working directory. If it exits unexpectedly, pidfd exec tests fail.

Test signals: no direct TAP output; parent tests observe process/pidfd behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_exec_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_fdinfo_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_fdinfo_test.c

Purpose: validates `/proc/self/fdinfo/<pidfd>` `Pid:` and `NSpid:` reporting for live children in nested/sibling PID namespaces and for dead processes.

Important APIs/types/functions: `struct error` tracks pass/fail/skip/error states; `clone_newns()` creates children with `CLONE_PIDFD | CLONE_NEWPID | CLONE_NEWNS` and optional `CLONE_NEWUSER`; `verify_fdinfo()` reads fdinfo lines and compares expected strings; `child_fdinfo_nspid_test()` remounts procfs and checks a sibling pidfd resolves to `NSpid:\t0`.

Control flow: `test_pidfd_fdinfo_nspid()` creates child A in a new PID/mount namespace, then child B in a sibling namespace with A's pidfd. Parent verifies A and B fdinfo show host pid and namespace pid 1; B verifies sibling pidfd NSpid is 0. Both children are joined and results reported. `test_pidfd_dead_fdinfo()` creates a child, waits for it to exit, then verifies `Pid:` and `NSpid:` become `-1` before closing the pidfd.

State and persistence: creates namespace children, maps stacks with `mmap()`, remounts procfs inside children, and reads procfs fdinfo. No persistent files.

Dependencies/integration: requires PID/user/mount namespaces, procfs, clone pidfd support, and kselftest output helpers.

Risks: exact fdinfo formatting is part of the tested ABI; formatting changes are failures. Restricted unshare/clone policies will block tests. Error handling uses custom states and fatal exits for infrastructure errors.

Test signals: two planned kselftest results: sibling namespace NSpid behavior and dead process fdinfo behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_fdinfo_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_file_handle_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_file_handle_test.c

Purpose: tests pidfs file-handle export/import behavior through `name_to_handle_at()` and `open_by_handle_at()` for pidfds across same, child, foreign, exited, and reaped PID namespace scenarios.

Important APIs/types/functions: fixture creates self pidfd and three child pidfds using `create_child()` with user/PID namespace variants. Tests allocate `struct file_handle`, use `MAX_HANDLE_SZ`, `AT_EMPTY_PATH`, `AT_HANDLE_FID`, `FD_PIDFS_ROOT`, valid/invalid open flags, `fstat()` identity checks, `setns()`, and pidfd signal/wait helpers.

Control flow: same/child namespace tests obtain a handle from a child pidfd and reopen it via the parent's pidfd with several valid flags, comparing device/inode. Foreign namespace test creates a handle for the parent, enters a child PID/user namespace, forks, and confirms decode fails outside the caller hierarchy. Exited vs reaped tests show handles remain decodable after exit before reap but fail after reap. Flag tests verify allowed pidfd flags and reject creation/path flags. Lookup tests ensure pidfs does not support path lookup. Final tests validate `AT_HANDLE_FID` and decoding via `FD_PIDFS_ROOT`.

State and persistence: creates paused children, pidfds, namespace changes in a forked child, and signals/reaps children in teardown. No filesystem files.

Dependencies/integration: requires pidfs export operations, file handle syscalls, pidfd_open/send_signal/waitid, user/PID namespace support, and matching UAPI flags.

Risks: `setns()` in the foreign namespace test changes namespace state in the fixture process before forking, so test isolation relies on kselftest process model. Feature availability is new-kernel-specific. Teardown must avoid double-killing child3 when tests consume it.

Test signals: kselftest assertions for each file-handle decode/flag/lookup case; failures indicate pidfs export or namespace visibility regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_file_handle_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_getfd_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_getfd_test.c

Purpose: tests `pidfd_getfd()` for fetching a target process fd, permission denial, invalid flags, unknown fd, and a historical exiting-task race that should return `ESRCH` instead of misleading `EBADF`.

Important APIs/functions: local `sys_kcmp()` compares file identity; child helper creates a memfd and reports its fd number over a socketpair; fixture opens a pidfd for the child and keeps a control socket. Tests use `prctl(PR_SET_DUMPABLE, 0)` to disable ptrace access, `seteuid(65535)` when root, `sys_pidfd_getfd()`, `fcntl(F_GETFD)`, `poll()` on pidfd, and `KCMP_FILE`.

Control flow: fixture forks child, waits for remote memfd number, and opens pidfd. `disable_ptrace` commands child to disable dumpability and expects `EPERM`. `fetch_fd` gets the fd and verifies same underlying file through `kcmp()` unless unsupported. `test_unknown_fd` expects `EBADF`. `flags_set` expects `EINVAL` for nonzero flags. `no_strange_EBADF` kills child, waits for pidfd readability, and expects `ESRCH` when fetching from an exited task.

State and persistence: creates socketpair, child process, memfd, pidfd, and temporary fetched fd. No files persist.

Dependencies/integration: requires pidfd_getfd syscall, pidfd_open, memfd_create, ptrace permission checks, optional kcmp, and local UNIX sockets.

Risks: permission behavior depends on credentials/capabilities. `kcmp()` may be unavailable and is skipped. The race regression test depends on timing but polls for exit before fetching.

Test signals: kselftest harness; compile-time fallback main returns skip if `__NR_pidfd_getfd` is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_getfd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_info_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_info_test.c

Purpose: tests `PIDFD_GET_INFO` reporting for live, exited, reaped, signaled, successful, thread-specific, exec-transition, and supported-mask cases.

Important APIs/functions: fixture creates four children covering killed-not-reaped, killed-reaped, successful-not-reaped, and successful-reaped states. Tests use `ioctl(PIDFD_GET_INFO)`, `poll()` pidfds, `sys_waitid(P_PIDFD/P_PID)`, `PIDFD_THREAD`, pthread helpers, socket synchronization, and `sys_execveat()` of `pidfd_exec_helper`.

Control flow: basic tests verify credentials are available before reap, exit info appears after reap when requested, and non-requested exit info yields `ESRCH` for reaped processes. `success_reaped_poll` checks `POLLIN|POLLHUP` on reaped pidfd. `thread_group` creates a thread that outlives the leader, verifies thread pidfd opening rules, delayed notification, info for leader/thread pidfds, then kills the group and checks exit status for all pidfds. `thread_group_exec` and `_exec_thread` validate pidfd notification and exit-info behavior when a non-leader thread execs and assumes the leader pid. Supported-mask tests verify `supported_mask` is returned alone or with other fields.

State and persistence: creates children, threads, pidfds, sockets, and execs helper. It kills and reaps processes in tests and teardown.

Dependencies/integration: requires pidfd `PIDFD_GET_INFO`, pidfs thread pidfds, clone3, pthreads, exec helper in cwd, and newer supported-mask fields.

Risks: very sensitive to kernel pid/thread lifecycle semantics. Poll timeouts comment says 5 seconds but uses 10000 ms. Missing helper binary breaks exec tests.

Test signals: kselftest assertions on mask bits, credential/exit availability, poll revents, pids, and wait status macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_info_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_open_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_open_test.c

Purpose: tests `pidfd_open()` argument validation and basic `PIDFD_GET_INFO` consistency with `/proc/self/fdinfo`.

Important APIs/functions: `safe_int()`, whitespace trimming helpers, and `get_pid_from_fdinfo_file()` parse `Pid:` from fdinfo robustly. `main()` uses `sys_pidfd_open()`, `ioctl(PIDFD_GET_INFO)`, and credential getters.

Control flow: plan has four tests. It rejects invalid pid `-1`, rejects invalid nonzero flags, opens a pidfd for `getpid()`, parses fdinfo pid, then requests `PIDFD_INFO_CGROUPID` and validates returned pid, ppid, real/effective/saved/fs uid/gid fields, and nonzero cgroupid when the mask says it is present.

State and persistence: opens one pidfd and reads procfs fdinfo. No persistent state.

Dependencies/integration: requires pidfd_open, pidfs info ioctl, procfs fdinfo, and kselftest output.

Risks: the ppid mismatch diagnostic prints the wrong first variable in one message, but the comparison is correct. Credential expectations assume no concurrent credential changes.

Test signals: kselftest pass lines for invalid pid, invalid flags, open pidfd, and info validation; any validation error exits fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_open_test.c -->
