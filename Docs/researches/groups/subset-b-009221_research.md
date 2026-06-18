# subset-b-009221 Research

Grouped research report for the subset B work item. Each source file has a source-path-preserving section bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/procflow.c -->
# `sources/test-tools/filebench/procflow.c`

Purpose: Implements Filebench process-flow lifecycle management. A parser-defined `FLOW_MASTER` procflow describes an f-language process, and runtime worker procflows fork/exec child Filebench processes that attach to the shared memory segment and create their threadflows.

Important APIs and functions: Public entry points are `procflow_define()`, `proc_create()`, `proc_shutdown()`, `procflow_shutdown()`, and `procflow_exec()`. Internals include `procflow_createproc()` for `fork()`/`fork1()` plus `execlp()` or `system()`, `procflow_create_all_procs()` for cloning masters into instances, `procflow_find()`, `procflow_createnwait()` for monitor/wait behavior, `procflow_allstarted()`, `procflow_cleanup()`, and `procflow_cancel()`.

Control flow: `proc_create()` clears abort/error state, takes the shared run lock, starts the creator/waiter thread through `procflow_init()`, waits for all worker processes and threadflows to be defined, allocates interprocess shared memory if required, releases the run lock, records start time, and resets event generation. Child processes enter through `procflow_exec()`, find their procflow by name/instance, set `my_procflow`, apply nice value, run `threadflow_init()`, decrement `shm_procs_running`, and return. The creator thread continues in a wait loop and aborts the run on unexpected child exit.

State and persistence: State lives primarily in `filebench_shm`: procflow list, locks, abort flags, process counts, run lock, start time, and shared memory requirements. Per-process globals `my_pid` and `my_procflow` identify the current process. Process lifetime is persistent only for the active workload run; entities are allocated/freed through Filebench IPC allocators.

Dependencies and integration: Depends on `filebench.h`, `threadflow` via `threadflow_init()`/`threadflow_allstarted()`/`threadflow_delete_all()`, IPC locks and flags, `eventgen_reset()`, `ipc_ismcreate()`/`ipc_ismdelete()`, and platform process APIs. It is the bridge between parser-created procflow definitions and threadflow runtime execution.

Risks and test signals: Fork/exec argument handling depends on shared memory address/path compatibility between parent and child. Shutdown uses `SIGUSR1`, `kill()`/`sigsend()`, and wait loops, so stuck or already-exited children can expose race conditions. `procflow_sleep()` uses bitwise `&` rather than logical `&&`, which works for nonzero integers but is fragile. Tests should exercise multi-process workloads, abnormal child exit, start-time synchronization flags, `nice`, shared memory allocation/deletion, and signal-driven shutdown.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/procflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/procflow.h -->
# `sources/test-tools/filebench/procflow.h`

Purpose: Declares the Filebench process-flow object and the public process lifecycle API used by parser, runtime, and child-process entry code.

Important APIs and types: `procflow_t` stores process name, instance number, configured instance AVD, running flag, `pf_threads_defined_flag`, list linkage, PID, thread id, owned threadflow list, attributes, and nice value AVD. Public functions are `procflow_define()`, `proc_create()`, `procflow_shutdown()`, `proc_shutdown()`, and `procflow_exec()`.

Control flow and integration: Parser code creates `FLOW_MASTER` procflows with `procflow_define()`. Runtime code calls `proc_create()` to clone masters and start child processes. Child filebench instances call `procflow_exec()` using command-line process name and instance. Shutdown code uses `procflow_shutdown()` or `proc_shutdown()` to stop workers and clean shared memory.

State and persistence: The struct is allocated from Filebench IPC/shared-memory allocation classes and linked under `filebench_shm->shm_procflowlist`, allowing parent and child processes to coordinate via shared flags and lists.

Dependencies: Includes `filebench.h` for `avd_t`, `flag_t`, `pid_t`, `pthread_t`, constants such as `FLOW_MASTER`, and shared-memory definitions. It forward-references `struct threadflow` to avoid direct header coupling.

Risks and test signals: Any change to `procflow_t` affects shared memory ABI inside Filebench worker processes. Tests should cover parser-created process definitions, multi-instance cloning, child process lookup, and shutdown synchronization across process boundaries.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/procflow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/stats.c -->
# `sources/test-tools/filebench/stats.c`

Purpose: Collects, rolls up, clears, and reports Filebench runtime statistics for flowops and global I/O categories.

Important APIs and functions: Public functions are `stats_clear()` and `stats_snap()`. Static `stats_add()` accumulates counts, byte counters, total latency, min/max latency, and OS profile latency distribution buckets. `globalstats` is a heap-allocated array indexed by Filebench flow type.

Control flow: `stats_clear()` allocates `globalstats` if missing, zeros global and per-flowop stats, and records `fs_stime`. `stats_snap()` refuses to run before clear or after abort-error, sets `shm_bequiet` to freeze updates, preserves the original start time, zeros global and master flowop stats, sets end time, iterates runtime flowops, rolls each into both type-specific and global totals, rolls each into its `FLOW_MASTER` flowop by name, builds a per-operation text breakdown, optionally includes histogram buckets, emits the I/O summary, then clears `shm_bequiet`.

State and persistence: Stats are in memory only. Per-flowop counters live in each `flowop->fo_stats`; aggregate state is in `globalstats`. `shm_bequiet` is a shared flag used to reduce concurrent mutation during snapshotting.

Dependencies and integration: Depends on `flowop_find_one()`, `filebench_shm->shm_flowoplist`, `filebench_log()`, `gethrtime()`, `vars`, and `fbtime` conversion constants. It integrates with the scripting command layer through `stats clear` and `stats snap` behavior.

Risks and test signals: The 1 MiB string buffer uses repeated `strcat()` and can overflow if there are many flowops or large histograms. `stats_clear()` zeros only `sizeof(struct flowstats)` after already zeroing `FLOW_TYPES`, which is harmless but redundant-looking. Snapshot accuracy depends on cooperative `shm_bequiet`, not a full lock. Tests should verify summaries for read/write/AIO flowops, latency min/max initialization, histogram output, abort-error suppression, and repeated clear/snap cycles.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/stats.h -->
# `sources/test-tools/filebench/stats.h`

Purpose: Defines Filebench flow statistics data and exposes the stats clear/snapshot API.

Important APIs and types: `struct flowstats` tracks operation counts, read/write counts, byte totals, read/write bytes, 64 latency distribution buckets, total latency, max/min latency, and start/end timestamps used by global stats. Functions `stats_clear()` and `stats_snap()` are the exported commands. Macros classify active/IO flowops and derive IOPS-style counters.

Control flow and integration: Flowops update embedded `fo_stats` during execution. `stats.c` reads these fields at snapshot time and rolls them into global and master-flowop aggregates. The header is included by flowop, variable, and stats consumers that need the struct layout.

State and persistence: The struct is embedded in flowop/threadflow runtime structures and allocated in global arrays for reporting. Values are per-run, reset by `stats_clear()`, and not persisted outside logs.

Dependencies: Includes `filebench.h` and `fbtime.h` for common types and high-resolution time.

Risks and test signals: `STAT_CPUTIME` and `STAT_OHEADTIME` reference fields not present in this struct, suggesting stale macros or external expectations that should be checked before use. Tests should compile all stats macro consumers and validate min/max latency initialization and bucket array bounds.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/threadflow.c -->
# `sources/test-tools/filebench/threadflow.c`

Purpose: Implements Filebench thread-flow lifecycle management inside a procflow. It converts parser-defined master threadflows into runtime worker threads and tears them down during shutdown.

Important APIs and functions: Public functions are `threadflow_define()`, `threadflow_find()`, `threadflow_init()`, `threadflow_allstarted()`, and `threadflow_delete_all()`. Static helpers include `threadflow_define_common()`, `threadflow_createthread()`, `threadflow_kill()`, and `threadflow_delete()`.

Control flow: Parser code creates `FLOW_MASTER` threadflows using `threadflow_define()`. In a child process, `threadflow_init()` locks the shared threadflow list, clones each master according to `tf_instances`, creates pthreads running `flowop_start()`, sets `pf_threads_defined_flag` once all runtime threadflows are defined, then joins created threads. `threadflow_allstarted()` waits for `tf_running` on runtime instances after proc creation. Shutdown calls `threadflow_delete_all()`, which skips masters, marks threads aborted, waits briefly, kills stubborn threads, deletes flowops, destroys locks, and frees threadflow objects.

State and persistence: Threadflows are stored in each procflow’s `pf_threads` list and allocated in Filebench IPC memory. Per-thread state includes unique id, pthread id, abort/running flags, local file descriptors, private memory size, flowop list, stats, and async I/O list when enabled. `shm_required` is incremented/decremented for `THREADFLOW_USEISM`.

Dependencies and integration: Depends on `filebench_shm` locks, IPC allocation, `flowop_start()`, `flowop_delete_all()`, parser-created AVDs, and procflow flags. It is called by `procflow_exec()` and by proc shutdown.

Risks and test signals: `threadflow_delete_all()` advances after freeing the current object in a way that can be risky if list links are invalidated; shutdown tests should stress multiple runtime threads. `pthread_kill(..., SIGKILL)` is process-wide on some systems or invalid for pthread-targeted cleanup assumptions. Shared-memory accounting for private memory must stay balanced. Tests should cover multiple instances, flowop deletion, `THREADFLOW_USEISM`, start-time waits, and thread create failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/threadflow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/threadflow.h -->
# `sources/test-tools/filebench/threadflow.h`

Purpose: Declares Filebench threadflow data structures, async I/O list support, thread attributes, and thread lifecycle APIs.

Important APIs and types: `threadflow_t` contains name, attributes, instance/running/abort flags, unique id, parent procflow pointer, pthread id, mutex, instance AVD, next pointer, per-thread flowop list, private memory, file descriptor and fileset arrays, stats, current flowop start time, optional AIO list, and I/O priority AVD. With `HAVE_AIO`, `aiolist_t` wraps `aiocb64` entries and read/write type. Public functions include `threadflow_define()`, `threadflow_find()`, `threadflow_init()`, `flowop_start()`, `threadflow_allstarted()`, and `threadflow_delete_all()`.

Control flow and integration: Parser-created threadflow masters are cloned by `threadflow_init()` at process start. `flowop_start()` is the execution entry point for worker threads. Procflow startup and shutdown call the exported functions to wait for thread start and delete runtime instances.

State and persistence: Threadflow objects live in Filebench IPC/shared memory and own per-thread runtime state for a workload process. File descriptors and fileset entries are local to each worker thread and are not persisted after run cleanup.

Dependencies: Includes `filebench.h`, `struct flowstats` via included definitions, and forward references procflow/flowop/fileset types.

Risks and test signals: `THREADFLOW_MAXFD` statically caps local file slots. Struct layout changes affect shared-memory users. Tests should compile with and without `HAVE_AIO`, verify thread-local fd rotation behavior, and run multi-thread workloads with private memory and I/O priority attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/threadflow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/utils.c -->
# `sources/test-tools/filebench/utils.c`

Purpose: Provides small portability and resource-limit helpers for Filebench: string allocation, fallback `strlcpy`/`strlcat`, Linux shared-memory limit tuning, and file descriptor limit tuning.

Important APIs and functions: `fb_stralloc()` heap-duplicates a string. `fb_strlcpy()` and `fb_strlcat()` are compiled when platform versions are unavailable. `fb_set_shmmax()` optionally writes a larger `/proc/sys/kernel/shmmax`. `fb_set_rlimit()` optionally raises `RLIMIT_NOFILE` first to the hard limit and then to a fixed large value.

Control flow: These helpers are direct utility calls from parser/runtime code. The resource functions become no-ops when their configure feature macros are absent. On Linux shmmax tuning failure, the code logs a fatal-level warning but returns so execution can continue.

State and persistence: String allocation returns process heap memory. `fb_set_shmmax()` changes a kernel sysctl and explicitly does not restore the original value. `fb_set_rlimit()` changes process resource limits for the current Filebench process.

Dependencies and integration: Depends on `filebench_log()`, `filebench.h`, configure macros, `parsertypes.h`, libc, `/proc/sys/kernel/shmmax`, and `setrlimit()`. The utilities smooth portability across Solaris and non-Solaris platforms.

Risks and test signals: Fallback `strlcpy`/`strlcat` return the copied length plus NUL, not the full source length semantics of BSD `strlcpy`/`strlcat`, so callers expecting truncation detection may be misled. `fb_stralloc(NULL)` would crash. Sysctl writes need privilege and are global. Tests should cover truncation behavior, no-op builds without feature macros, unprivileged shmmax handling, and fd limit changes.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/utils.h -->
# `sources/test-tools/filebench/utils.h`

Purpose: Declares Filebench utility functions and maps `fb_strlcpy`/`fb_strlcat` to native platform functions when available.

Important APIs: `fb_stralloc()`, `fb_strlcat()`, `fb_strlcpy()`, `fb_set_shmmax()`, and `fb_set_rlimit()`. The `HAVE_STRLCAT` and `HAVE_STRLCPY` branches define macros to native `strlcat`/`strlcpy`; otherwise external fallback functions are declared.

Control flow and integration: Included by parser, variable, and runtime modules needing portable string copying or startup resource tuning. It is a thin declaration layer over `utils.c`.

State and persistence: No state is declared here, but the resource-limit functions can mutate process or kernel state when implemented.

Dependencies: Includes `filebench.h` for Filebench common types and configure-derived declarations.

Risks and test signals: Macro substitution means callers may see either native or fallback semantics depending on configure results. Tests should build on platforms with and without native `strl*` functions and confirm prototypes match system headers.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/vars.c -->
# `sources/test-tools/filebench/vars.c`

Purpose: Implements Filebench variables and attribute value descriptors. It supports delayed binding from workload parser references to variable values that may be assigned later, including random and custom variables.

Important APIs and functions: Public AVD APIs are `avd_bool_alloc()`, `avd_int_alloc()`, `avd_dbl_alloc()`, `avd_str_alloc()`, `avd_var_alloc()`, and typed getters `avd_get_bool()`, `avd_get_int()`, `avd_get_dbl()`, `avd_get_str()`. Public variable assignment APIs are `var_assign_boolean()`, `var_assign_integer()`, `var_assign_double()`, `var_assign_string()`, `var_assign_random()`, and `var_assign_custom()`. String/introspection helpers include `var_to_string()` and `var_randvar_to_string()`. Local-variable helpers include `var_lvar_alloc_local()` and type-specific `var_lvar_assign_*()` functions.

Control flow: Parser allocation functions create static AVDs or variable-backed AVDs. `avd_var_alloc()` finds or creates a `var_t`, then `set_avd_type_by_var()` maps its current type to a direct pointer or leaves it as `AVD_VARVAL_UNKNOWN`. Getters resolve unknown variables lazily, optionally erroring and shutting down if the variable is still uninitialized. Assignment functions find or allocate variables on `shm_var_list` and set typed union values. Local variable assignment can copy values from global or local lists and component update can copy prototype values into new component-local variables.

State and persistence: Variables, AVDs, and strings are allocated with Filebench IPC allocators and stored in `filebench_shm->shm_var_list` or `shm_var_loc_list`. Random/custom values store pointers to distribution/custom-variable objects. Values persist for the loaded workload/run until shared memory cleanup.

Dependencies and integration: Depends on `ipc_malloc()`, `ipc_stralloc()`, `filebench_log()`, `filebench_shutdown()`, `fb_random` distribution interfaces, custom variables via `get_cvar_value()`, and parser modules that build workload attribute descriptors.

Risks and test signals: Several paths call `filebench_shutdown(1)` for invalid or unknown types, so late variable errors are fatal. String assignment allocates new strings without freeing previous values, acceptable for workload lifetime but not for repeated mutation stress. `var_lvar_assign_var()` stores a double source with `VAR_SET_INT`, likely a type bug. `avd_update()` is a stub, indicating local variable substitution may be incomplete or legacy. Tests should cover delayed binding, unknown variable errors, random/custom getters, string rendering, local variable inheritance, and reassignment behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/vars.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/vars.h -->
# `sources/test-tools/filebench/vars.h`

Purpose: Defines Filebench variable and attribute descriptor types and declares the variable/AVD API used by parser and runtime code.

Important APIs and types: `avd_type_t` distinguishes inline bool/int/double/string values, variable-backed typed pointers, unknown variable references, random variables, and custom variables. `struct avd` stores the selected type plus a union of direct values and pointers. `var_type_t` and `var_t` represent named variables with typed union storage and list linkage. Macros classify and set variable/AVD types. Public functions allocate AVDs, assign variables, resolve typed AVD values, update local variables, and stringify variables or random parameters.

Control flow and integration: Workload parsing uses `avd_*_alloc()` and `avd_var_alloc()` to attach attributes to process/thread/flowop definitions. Runtime code calls typed getters when it needs the current value. Assignment APIs back the f-language `set` command and random/custom variable setup.

State and persistence: The header describes objects allocated in Filebench shared memory, allowing values to be visible across process-mode worker instances. Variable values persist for a workload lifetime.

Dependencies: Includes `filebench.h` and forward references `randdist` and `cvar` objects through struct pointers.

Risks and test signals: Macros are multi-statement blocks without `do { } while (0)`, so use in conditional contexts can be unsafe. Typing is enforced at runtime, not compile time. Tests should include parser integration, macro use under normal call sites, and all typed getter conversions.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/vars.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/workloads/Makefile.am -->
# `sources/test-tools/filebench/workloads/Makefile.am`

Purpose: Automake manifest for installing Filebench workload model files.

Important APIs and build variables: `workloadsdir = @datadir@/filebench/workloads` selects the install location. `workloads_DATA` enumerates `.f` workload definitions such as filemicro, fileserver, oltp, webserver, varmail, videoserver, and stream workloads. `EXTRA_DIST = $(workloads_DATA)` ensures the same workload files are included in distribution tarballs.

Control flow: During `make install`, Automake installs every file listed in `workloads_DATA` into the configured data directory. During distribution packaging, `EXTRA_DIST` includes the workload files even though they are data rather than compiled sources.

State and persistence: No runtime state. The persistent effect is installation of workload model assets used by Filebench users and tests.

Dependencies and integration: Depends on Automake conventions and the presence of every listed `.f` file in the workloads directory. Integrated with the Filebench build and release packaging system.

Risks and test signals: Missing listed workload files break `make dist` or install. New workload files are not installed unless added here. Tests should run `make distcheck` or equivalent packaging checks and verify installed workload paths.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/workloads/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.github/ISSUE_TEMPLATE/config.yml -->
# `sources/test-tools/fio/.github/ISSUE_TEMPLATE/config.yml`

Purpose: Configures GitHub issue template behavior for fio.

Important settings: `blank_issues_enabled: true` permits users to open issues without a structured template. `contact_links` adds a general-questions link pointing users to the fio mailing list and notes that plain-text email is expected.

Control flow: GitHub reads this YAML when rendering the new-issue UI. It does not affect builds or runtime behavior.

State and persistence: Repository metadata only; no generated state.

Dependencies and integration: Depends on GitHub issue template schema. Integrates project support workflow with the external vger fio mailing list.

Risks and test signals: The URL is HTTP and external; if the mailing-list page changes, issue guidance degrades. Tests are mainly repository metadata validation or manual GitHub UI review.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.github/actions/build-qemu/action.yml -->
# `sources/test-tools/fio/.github/actions/build-qemu/action.yml`

Purpose: Composite GitHub Action that installs dependencies, builds QEMU from source, installs it, and removes build artifacts for fio VM-based tests.

Important APIs and inputs: Input `version` defaults to `9.1.0`. Steps install Ubuntu build dependencies, download `qemu-$INPUT_VER.tar.xz`, configure QEMU with KVM and `x86_64-softmmu`, build with `make -j $(nproc)`, run `sudo make install`, and delete the source directory.

Control flow: Called by the QEMU workflow before starting guest VMs. The action uses bash and `INPUT_VER` derived from `${{ inputs.version }}`.

State and persistence: Installs QEMU into the GitHub runner system path and temporarily consumes disk for source/build trees. It removes the source tree afterward but leaves installed binaries for later workflow steps.

Dependencies and integration: Depends on Ubuntu runners, apt packages, network access to `download.qemu.org`, `sudo`, build tools, KVM availability, and the caller workflow.

Risks and test signals: The action file has a misspelled `desription` key, harmless for execution but metadata quality risk. Building QEMU from source is time- and disk-heavy and can fail on upstream URL or package changes. Tests should execute the QEMU workflow, check installed `qemu-system-x86_64`, and monitor runner disk use.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.github/actions/build-qemu/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.github/actions/create-guest-image/action.yml -->
# `sources/test-tools/fio/.github/actions/create-guest-image/action.yml`

Purpose: Composite GitHub Action that creates a libguestfs VM image for fio guest testing.

Important APIs and inputs: Inputs are `distro` defaulting to `debian-12` and optional `extra_pkgs`. Steps install `libguestfs-tools`, relax permissions on `/boot/vmlinuz*` and `/dev/kvm`, generate an SSH key, and run `virt-builder` with hostname, SSH injection, host key generation, Debian network interface adjustment, and environment variables for GitHub and CI context.

Control flow: The QEMU workflow calls this before building QEMU and starting the VM. The generated image is named according to the distro by `virt-builder` defaults and then passed to the start-VM action.

State and persistence: Produces a guest image file in the runner workspace and writes an SSH key under `~/.ssh`. Environment entries persist inside the guest image.

Dependencies and integration: Depends on Ubuntu runner privileges, libguestfs image templates, KVM, SSH tooling, and caller-provided CI environment variables.

Risks and test signals: `chmod 0666 /dev/kvm` and broad `/boot/vmlinuz*` readability are CI-specific privilege changes. The network-interface sed assumes a Debian interface name. Tests should boot the produced image, verify SSH access, check injected environment variables, and confirm extra packages are installed by later guest scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.github/actions/create-guest-image/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.github/actions/start-vm/action.yml -->
# `sources/test-tools/fio/.github/actions/start-vm/action.yml`

Purpose: Composite GitHub Action that starts a QEMU/KVM guest VM and waits for SSH readiness.

Important APIs and inputs: Inputs include `qemu`, `image`, `ssh_fwd_port`, `options`, `ram`, and `host_key`. Steps install `wait-for-it`, configure KVM udev permissions, run QEMU in the background with host CPU, virtio disk, KVM, `q35`, user-mode networking and SSH port forwarding, then wait for the port and optionally add the host key.

Control flow: QEMU workflow calls this after creating the image and optional device backing files. Extra NVMe/null/other device options are appended directly to the QEMU command.

State and persistence: Leaves a background QEMU process running for subsequent workflow steps. Modifies runner udev rules and known_hosts when requested.

Dependencies and integration: Depends on QEMU binary availability, KVM support, root privileges for udev changes, and SSH server availability in the guest image.

Risks and test signals: The QEMU process is backgrounded without explicit PID tracking or teardown. `inputs.options` is command-line interpolated, so caller quoting must be correct. The wait timeout is short for slow boots. Tests should validate SSH command execution, device visibility in guest, and cleanup behavior after workflow completion.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.github/actions/start-vm/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.github/workflows/ci.yml -->
# `sources/test-tools/fio/.github/workflows/ci.yml`

Purpose: Main fio CI workflow covering container builds, native Linux/macOS/Windows/Android-style builds, smoke tests, full tests, and Windows installer artifacts.

Important jobs and settings: Triggers are push, pull request, manual dispatch, and a daily scheduled run. `build-containers` runs distro container matrices for Debian, Fedora, Alma, Oracle, Rocky, and Ubuntu i686/x86_64. `build` runs a platform matrix for GCC, clang, macOS, Linux i686, Android target, Cygwin 32/64, and MSYS2 64, with install/build/smoke/full test scripts. Windows jobs install Cygwin or MSYS2 packages, build MSI installers, upload artifacts, and publish tagged Cygwin release assets.

Control flow: Each job checks out the repo, installs dependencies using `ci/actions-install.sh`, builds with `ci/actions-build.sh`, then runs smoke and full tests. Windows-specific steps handle line endings, toolchain installation, installer build, and dependency file cleanup.

State and persistence: Produces build outputs and optional Windows MSI artifacts. CI environment variables encode target build, architecture, OS, and compiler.

Dependencies and integration: Depends on GitHub Actions, container images, platform runners, Cygwin/MSYS2 third-party actions, fio CI scripts, and artifact/release actions.

Risks and test signals: Matrix includes an `android-recovery` include entry without a matching `build` list value, so it may not run unless GitHub matrix include semantics create it as intended. Action versions like `actions/checkout@v6` and upload-artifact v6 require current availability. Tests are the workflow itself; monitor dependency installation, installer creation, and full-test runtime across OSes.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.github/workflows/cifuzz.yml -->
# `sources/test-tools/fio/.github/workflows/cifuzz.yml`

Purpose: Runs OSS-Fuzz CIFuzz for fio on pull requests and manual dispatch.

Important jobs and settings: Single `Fuzzing` job on Ubuntu. It builds fuzzers with `google/oss-fuzz/infra/cifuzz/actions/build_fuzzers@master`, runs them for 600 seconds with `run_fuzzers@master`, and uploads crash artifacts from `./out/artifacts` if fuzz execution fails after a successful build.

Control flow: Build step creates fuzzers for OSS-Fuzz project `fio`; run step executes them; upload step preserves reproducer/crash data on failure.

State and persistence: Temporary fuzz build and output directories are created on the runner. Artifact upload persists crashes for review.

Dependencies and integration: Depends on OSS-Fuzz GitHub Actions, the external fio OSS-Fuzz project definition, and GitHub artifact upload.

Risks and test signals: Actions are pinned to `master`, which can change behavior. Ten-minute fuzzing is useful for regression smoke but not exhaustive. Tests should confirm fuzz targets still build under the OSS-Fuzz configuration and that failure artifacts are collected.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.github/workflows/cifuzz.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.github/workflows/qemu.yml -->
# `sources/test-tools/fio/.github/workflows/qemu.yml`

Purpose: Runs fio integration tests inside a QEMU guest with emulated storage configurations, especially NVMe passthrough/protection information, FDP, trim verification, and zoned block device tests.

Important jobs and settings: Triggered manually and on a daily schedule. The `qemu-guest` job uses Ubuntu 22.04, Debian 12 guest image, SSH/scp environment variables, and a matrix of configurations with QEMU device options, guest test commands, and extra packages.

Control flow: The job checks out the repo, creates a source tarball, creates a guest image, builds/installs QEMU, creates a backing `nvme0.img`, starts a VM with matrix-specific devices, transfers source into the guest, installs dependencies, builds fio, optionally dumps NVMe namespace info, then runs the matrix test command over SSH.

State and persistence: Creates guest disk image, NVMe backing image, source tarball, installed QEMU, and a long-running VM for the job duration. Test output is held in Actions logs.

Dependencies and integration: Uses the local composite actions in `.github/actions`, fio test scripts under `t/`, `nvme-cli`, `sg3-utils`, SSH, KVM, and QEMU storage device support.

Risks and test signals: Scheduled VM tests are resource-heavy and sensitive to QEMU, kernel, KVM, and guest image behavior. The same `nvme0.img` backing name is reused across configurations within independent matrix jobs. Test signals include guest build success, NVMe identify output, and pass/fail of targeted fio test scripts.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.github/workflows/qemu.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/.readthedocs.yaml -->
# `sources/test-tools/fio/.readthedocs.yaml`

Purpose: Configures Read the Docs builds for fio documentation.

Important settings: Uses RTD config version 2, Ubuntu 22.04 build image, Python 3 tooling, Sphinx configuration at `doc/conf.py`, and requests EPUB and PDF output formats.

Control flow: Read the Docs consumes this file to provision the build environment and run Sphinx documentation builds.

State and persistence: Produces hosted HTML plus additional EPUB/PDF artifacts through RTD; no repository runtime state.

Dependencies and integration: Depends on Sphinx configuration and documentation dependencies declared elsewhere in the project/RTD environment.

Risks and test signals: PDF/EPUB builds require complete Sphinx configuration and LaTeX/doc tooling support in the RTD image. Tests should run local Sphinx builds if dependencies are available and inspect RTD build logs after changes.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/.readthedocs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/FIO-VERSION-GEN -->
# `sources/test-tools/fio/FIO-VERSION-GEN`

Purpose: Shell script that derives and writes fio’s build version into `FIO-VERSION-FILE`.

Important variables and behavior: `GVF=FIO-VERSION-FILE`; default version is `fio-3.42`. Version resolution checks a release `version` file first, then `git describe --match "fio-[0-9]*" --abbrev=4 HEAD`, appending `-dirty` if the index differs from HEAD, and finally falls back to the default. It strips a leading `v` with `expr`, compares against the current generated file, and rewrites only when changed.

Control flow: The Makefile target `FIO-VERSION-FILE` invokes this script before compiling sources that need `FIO_VERSION`. It refreshes git index state before dirty detection.

State and persistence: Writes `FIO-VERSION-FILE` in the build directory and emits the selected version to stderr when it changes.

Dependencies and integration: Depends on POSIX shell, `git`, `expr`, `sed`, and Makefile inclusion of `FIO-VERSION-FILE`.

Risks and test signals: Builds outside git rely on `version` or the default. Dirty detection can mark generated or untracked-insensitive changes depending on git index behavior. Tests should run from release tarballs, clean git trees, dirty trees, and non-git source copies.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/FIO-VERSION-GEN -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/Makefile -->
# `sources/test-tools/fio/Makefile`

Purpose: Top-level build orchestration for fio, gfio, optional engines, test utilities, fuzz target, unit tests, docs, install, and cleanup.

Important APIs and build variables: Establishes `SRCDIR`, includes `config-host.mak`, sets `CPPFLAGS`, `FIO_CFLAGS`, `LIBS`, `PROGS`, scripts, core `SOURCE`, optional engine variables, `OBJS`, `FIO_OBJS`, `GFIO_OBJS`, test object/program groups, and install directories. `engine_template` switches between dynamic shared engines and static source inclusion.

Control flow: If `config-host.mak` is absent or stale, it runs `configure`. Conditional blocks add engines and OS-specific sources/libraries. `FIO-VERSION-FILE` is regenerated by `FIO-VERSION-GEN`, and `CFLAGS` embeds `FIO_VERSION`. Generic `%.o: %.c` compiles objects and writes dependency `.d` files. Targets link `fio`, `gfio`, test binaries, fuzz target, and unit tests. `test`, `fulltest`, `mock-tests`, `doc`, `install`, `clean`, and `distclean` provide developer and packaging workflows.

State and persistence: Produces object files, dependency files, binaries, dynamic engine `.so` files, generated parser files, docs, and installed files. `clean` removes most generated artifacts and calls mock-test cleanup.

Dependencies and integration: Depends on `configure`, `config-host.mak`, compiler/linker, platform libraries, optional library feature detection, parser generators, CUnit, GTK/Cairo for gfio, and many repo scripts/tests.

Risks and test signals: Conditional source inclusion is broad and platform-sensitive; missing config variables can silently omit engines. Dynamic engine linking uses a single object variable pattern that must match engine sources. Dependency generation uses sed/fmt fallback and may differ on Windows/Cygwin, hence the CI cleanup step. Test signals include `make`, `make test`, `make fulltest` on Linux, Windows installer builds, and optional unit tests with CUnit.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-aarch64.h -->
# `sources/test-tools/fio/arch/arch-aarch64.h`

Purpose: Provides fio’s AArch64 architecture contract: architecture id, pause/barrier primitives, find-first-zero, CPU clock, init hook, and direct syscall macros.

Important APIs: Defines `FIO_ARCH arch_aarch64`, `nop` as `yield`, full barriers with `__sync_synchronize()`, `arch_ffz()` using `rbit`/`clz`, `get_cpu_clock()` from `cntvct_el0` after `isb`, `arch_init()` setting `tsc_reliable = true`, and `__do_syscall0` through `__do_syscall6` using `svc 0` and registers `x8`, `x0`-`x5`.

Control flow and integration: Included via `arch.h` when `__aarch64__` is defined. Feature macros `ARCH_HAVE_FFZ`, `ARCH_HAVE_CPU_CLOCK`, `ARCH_HAVE_INIT`, and `FIO_ARCH_HAS_SYSCALL` enable generic code paths.

State and persistence: No persistent state beyond setting external `tsc_reliable` during arch initialization.

Dependencies: Uses inline assembly, Linux/AArch64 syscall ABI expectations, and common fio architecture enums.

Risks and test signals: Direct syscall macros are ABI-sensitive and assume Linux register conventions. CPU clock availability depends on user access to `cntvct_el0`. Tests should build/run fio on AArch64, exercise io_uring direct syscall paths, random timing code, and ffz users.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-aarch64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-alpha.h -->
# `sources/test-tools/fio/arch/arch-alpha.h`

Purpose: Minimal Alpha architecture support header for fio.

Important APIs: Defines `FIO_ARCH arch_alpha`, `nop` as an empty do-while, `read_barrier()` as `mb`, and `write_barrier()` as `wmb`.

Control flow and integration: Included from `arch.h` when `__alpha__` is defined. Generic fallback paths provide missing optional features such as CPU clock or arch init. `arch.h` also supplies Alpha-specific io_uring syscall numbers.

State and persistence: No state.

Dependencies: Depends on Alpha inline assembly mnemonics and compiler support.

Risks and test signals: Sparse implementation means generic timing and ffz paths must remain valid. Tests require at least cross-compilation for Alpha and, ideally, runtime smoke tests for memory ordering assumptions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-alpha.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-arm.h -->
# `sources/test-tools/fio/arch/arch-arm.h`

Purpose: Defines fio primitives for 32-bit ARM architectures.

Important APIs: Defines `FIO_ARCH arch_arm`. For ARMv4-v6 variants it uses `mov r0,r0` as `nop` and compiler memory barriers for reads/writes. For ARMv7A/ARMv7VE/ARMv8A it uses `nop` and `__sync_synchronize()` for barriers. Unsupported ARM variants produce a preprocessor error.

Control flow and integration: Selected by `arch.h` for `__arm__`. Generic code uses the defined barrier and nop macros while optional CPU-clock/syscall paths remain absent.

State and persistence: No state.

Dependencies: Relies on compiler-provided ARM architecture macros and inline assembly support.

Risks and test signals: Architecture macro coverage is explicit; newer or differently named ARM targets may fail with `unsupported ARM architecture`. Barrier strength differs between older and newer ARM paths. Tests should cross-compile for representative ARMv5/v6/v7 targets and run concurrency smoke tests on ARMv7+.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-arm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-generic.h -->
# `sources/test-tools/fio/arch/arch-generic.h`

Purpose: Generic fallback architecture header used when fio does not recognize the target architecture.

Important APIs: Defines `FIO_ARCH arch_generic`, empty `nop`, and compiler memory barriers for reads and writes.

Control flow and integration: Included by `arch.h` after a warning for unknown architectures. Optional features such as CPU clock, ffz, direct syscall shims, or arch-specific init are not declared, leaving generic implementations to cover them.

State and persistence: No state.

Dependencies: Requires only a compiler that accepts empty inline assembly memory clobbers.

Risks and test signals: Performance and timing precision may be lower, and platform-specific memory ordering requirements may not be fully represented. Tests should confirm fio still compiles and passes basic tests on unknown/cross targets using this fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-hppa.h -->
# `sources/test-tools/fio/arch/arch-hppa.h`

Purpose: Minimal HPPA architecture support for fio.

Important APIs: Defines `FIO_ARCH arch_hppa`, empty `nop`, and compiler memory barriers for reads/writes.

Control flow and integration: Selected by `arch.h` when `__hppa__` is defined. Generic code supplies missing optional primitives.

State and persistence: No state.

Dependencies: Inline assembly memory clobber support.

Risks and test signals: No hardware CPU clock or stronger hardware barriers are provided here; correctness depends on generic paths and compiler barrier sufficiency. Cross-build and basic runtime tests on HPPA are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-hppa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-ia64.h -->
# `sources/test-tools/fio/arch/arch-ia64.h`

Purpose: Provides IA-64 architecture primitives for fio.

Important APIs: Defines `FIO_ARCH arch_ia64`, pause hint `nop`, memory fence barriers, `ia64_popcnt()`, `arch_ffz()` using popcount arithmetic, `get_cpu_clock()` from `ar.itc`, and `arch_init()` setting `tsc_reliable = true`. Feature macros advertise init, ffz, and CPU clock support.

Control flow and integration: Included via `arch.h` for `__ia64__`. Generic timing and bit operations can use IA-64-specific implementations.

State and persistence: Mutates external `tsc_reliable` during init.

Dependencies: IA-64 inline assembly, `BITS_PER_LONG` configuration for bit operations, and compiler support for statement expressions.

Risks and test signals: IA-64 is uncommon, making bit operation and clock behavior easy to regress without cross-builds. Tests should compile for IA-64 and validate ffz semantics and monotonic clock handling where runtime is available.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-ia64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-loongarch64.h -->
# `sources/test-tools/fio/arch/arch-loongarch64.h`

Purpose: Minimal LoongArch64 architecture support for fio.

Important APIs: Defines `FIO_ARCH arch_loongarch64`, read/write barriers as `dbar 0`, and `nop` also as `dbar 0`.

Control flow and integration: Selected by `arch.h` when `__loongarch64` is defined. Optional CPU-clock, syscall, and ffz hooks are absent, so generic paths apply.

State and persistence: No state.

Dependencies: LoongArch inline assembly support.

Risks and test signals: Using a full barrier as `nop` may be conservative but expensive. Missing CPU clock support can affect timing fast paths. Tests should cross-compile and run basic I/O/rate workloads on LoongArch64.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-loongarch64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-mips.h -->
# `sources/test-tools/fio/arch/arch-mips.h`

Purpose: Minimal MIPS/MIPS64 architecture support for fio.

Important APIs: Defines `FIO_ARCH arch_mips`, sets `__SANE_USERSPACE_TYPES__` if absent to influence Linux type headers, and defines read/write barriers plus `nop` as compiler memory barriers.

Control flow and integration: Included by `arch.h` for `__mips__` or `__mips64__`. Generic code handles missing optional features.

State and persistence: No state.

Dependencies: Compiler memory clobber support and Linux userspace type header behavior.

Risks and test signals: The include guard name says `ARCH_MIPS64_H` while covering both MIPS and MIPS64; harmless but potentially confusing. Hardware barrier strength is minimal. Tests should cross-compile for 32- and 64-bit MIPS and run basic fio jobs if hardware/emulation is available.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-ppc.h -->
# `sources/test-tools/fio/arch/arch-ppc.h`

Purpose: Provides PowerPC/PowerPC64 fio architecture primitives for barriers, bit operations, and optional CPU clock.

Important APIs: Defines `FIO_ARCH arch_ppc`, `__SANE_USERSPACE_TYPES__`, `read_barrier()` as `lwsync` on ppc64 or `sync` otherwise, `write_barrier()` as `sync`, `arch_ffz()` using count-leading-zero instructions, `mfspr()`, and `get_cpu_clock()` from time-base registers. For ppc64, `ARCH_HAVE_CPU_CLOCK` is enabled; for non-ppc64 it is disabled despite implementation. `arch_init()` currently returns 0 with disabled alternate timebase probing.

Control flow and integration: Selected by `arch.h` for PowerPC macros. Generic code can use `ARCH_HAVE_FFZ` and, on ppc64, CPU clock support.

State and persistence: Disabled code could set `arch_flags` and `tsc_reliable`; active init does not mutate state.

Dependencies: PowerPC inline assembly, `BITS_PER_LONG`, SPR register semantics, and external `arch_flags`/`tsc_reliable` declarations.

Risks and test signals: Non-ppc64 CPU clock is implemented but intentionally not advertised; changing this requires care. The ppc64 clock loop waits for nonzero TBRL and may be platform-sensitive. Tests should build ppc32/ppc64, validate ffz, and run timing/rate workloads on ppc64.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-riscv64.h -->
# `sources/test-tools/fio/arch/arch-riscv64.h`

Purpose: Provides RISC-V 64-bit fio architecture primitives and Linux direct syscall wrappers.

Important APIs: Defines `FIO_ARCH arch_riscv64`, `nop`, read/write fences, `get_cpu_clock()` using `rdtime`, `arch_init()` setting `tsc_reliable = true`, and `__do_syscall0` through `__do_syscall6` using `ecall` with `a7` syscall number and `a0`-`a5` arguments. `ARCH_HAVE_CPU_CLOCK`, `ARCH_HAVE_INIT`, and `FIO_ARCH_HAS_SYSCALL` are enabled.

Control flow and integration: Selected by `arch.h` for `__riscv` with `__riscv_xlen == 64`. Used by timing and syscall helper code.

State and persistence: Mutates external `tsc_reliable` during init.

Dependencies: RISC-V inline assembly and Linux syscall ABI. `rdtime` user availability depends on platform/kernel configuration.

Risks and test signals: Clobber lists differ between syscall macros (`__do_syscallM` clobbers `a1`); ABI correctness is critical. Tests should cross-build and run io_uring/syscall paths plus timing workloads on RISC-V 64.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-riscv64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-s390.h -->
# `sources/test-tools/fio/arch/arch-s390.h`

Purpose: Provides s390/s390x fio architecture primitives and CPU clock support.

Important APIs: Defines `FIO_ARCH arch_s390`, `nop`, barriers using `bcr 15,0`, `get_cpu_clock()` using `stckf` when `CONFIG_S390_Z196_FACILITIES` is set or `stck` otherwise, shifts the clock by 12, sets `ARCH_CPU_CLOCK_CYCLES_PER_USEC 1`, enables CPU clock/init, undefines `ARCH_CPU_CLOCK_WRAPS`, and sets `tsc_reliable = true` in init.

Control flow and integration: Selected by `arch.h` for `__s390x__` or `__s390__`. Timing code can use the architecture clock without wrap assumptions.

State and persistence: Mutates external `tsc_reliable` during init.

Dependencies: s390 inline assembly and optional facility configuration.

Risks and test signals: Clock scaling assumptions are architecture-specific. Tests should build/run on s390x, validate monotonic timing, and exercise rate limiting and latency accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-s390.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-sh.h -->
# `sources/test-tools/fio/arch/arch-sh.h`

Purpose: Provides Renesas SuperH 32-bit architecture support for fio, including runtime selection of stronger barriers when LL/SC support is detected.

Important APIs: Defines `FIO_ARCH arch_sh`, `nop`, `mb()` choosing `synco` when `ARCH_FLAG_1` is set or a compiler barrier otherwise, and maps read/write barriers to `mb()`. `arch_init()` walks ELF auxiliary vectors after `envp` to inspect `AT_HWCAP`; if `CPU_HAS_LLSC` is present, it sets `arch_flags |= ARCH_FLAG_1`.

Control flow and integration: Selected by `arch.h` for `__sh__`. Generic startup calls `arch_init()` because `ARCH_HAVE_INIT` is set.

State and persistence: Mutates global `arch_flags` for the current process.

Dependencies: `<elf.h>`, `Elf32_auxv_t`, Linux-style auxv layout, and SuperH inline assembly.

Risks and test signals: Assumes auxv immediately follows the environment vector. Incorrect auxv parsing could read invalid memory on unusual runtimes. Tests should run on or emulate SH and verify barrier selection with/without LL/SC.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-sh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-sparc.h -->
# `sources/test-tools/fio/arch/arch-sparc.h`

Purpose: Minimal 32-bit SPARC architecture support for fio.

Important APIs: Defines `FIO_ARCH arch_sparc`, empty `nop`, and compiler memory barriers for read/write barriers.

Control flow and integration: Selected by `arch.h` for `__sparc__` before the `__sparc64__` branch. Generic optional features are used.

State and persistence: No state.

Dependencies: Compiler support for inline assembly memory clobbers.

Risks and test signals: Ordering primitives are compiler-only, unlike SPARC64’s membar use. Branch ordering in `arch.h` should be checked because some SPARC64 compilers may also define `__sparc__`. Tests should compile for SPARC and SPARC64 and verify the intended header is selected.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-sparc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-sparc64.h -->
# `sources/test-tools/fio/arch/arch-sparc64.h`

Purpose: Provides SPARC64 architecture id and memory barriers for fio.

Important APIs: Defines `FIO_ARCH arch_sparc64`, empty `nop`, `membar_safe(type)` using a branch-around sequence with `membar`, `read_barrier()` as `#LoadLoad`, and `write_barrier()` as `#StoreStore`.

Control flow and integration: Intended for inclusion by `arch.h` on SPARC64. Generic paths cover optional clock/syscall/ffz features.

State and persistence: No state.

Dependencies: SPARC64 inline assembly and memory barrier syntax.

Risks and test signals: In `arch.h`, the `__sparc__` check precedes `__sparc64__`, so compilers defining both may select the 32-bit SPARC header instead. Tests should verify preprocessing on real SPARC64 toolchains.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-sparc64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-x86-common.h -->
# `sources/test-tools/fio/arch/arch-x86-common.h`

Purpose: Shared x86/x86_64 CPU feature detection for fio.

Important APIs: Defines `cpuid()` wrapper around arch-specific `do_cpuid()`, declares `ARCH_HAVE_INIT`, external `tsc_reliable` and `arch_random`, and implements `arch_init_intel()`, `arch_init_amd()`, and `arch_init()`. Intel-like vendors check TSC presence, invariant TSC via `0x80000007`, and RDRAND via CPUID leaf 1 ECX bit 30. AMD/Hygon check invariant TSC if extended leaf is available.

Control flow and integration: Included by `arch-x86.h` and `arch-x86_64.h` after they define `do_cpuid()`. Generic startup calls `arch_init()` to populate timing/random capability flags.

State and persistence: Sets process-global `tsc_reliable` and `arch_random`.

Dependencies: x86 CPUID instruction and vendor string conventions. Uses `<string.h>`.

Risks and test signals: Vendor string checks are explicit and may miss newer compatible vendors. RDRAND flag is only set in Intel-like path, not AMD. Tests should mock or run on Intel, AMD, Hygon, and virtualized CPUs to validate TSC reliability and random capability flags.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-x86-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-x86.h -->
# `sources/test-tools/fio/arch/arch-x86.h`

Purpose: Provides 32-bit x86 fio architecture primitives.

Important APIs: Defines `do_cpuid()` using `xchgl %%ebx` for PIC-safe EBX handling, includes `arch-x86-common.h`, defines `FIO_ARCH arch_x86`, huge page size 4 MiB, `rep;nop`, compiler barriers, `arch_ffz()` using `bsfl`, and `get_cpu_clock()` using `rdtsc` with `=A`. Enables ffz and CPU clock features.

Control flow and integration: Selected by `arch.h` for `__i386__`. Shared x86 init handles vendor and TSC/RDRAND feature discovery.

State and persistence: No state directly; common init mutates x86 globals.

Dependencies: 32-bit x86 inline assembly and compiler support for `=A`.

Risks and test signals: `rdtsc` reliability depends on `tsc_reliable` detection elsewhere. Tests should build i686 targets and run timing/rate tests under both bare metal and virtualized environments.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-x86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch-x86_64.h -->
# `sources/test-tools/fio/arch/arch-x86_64.h`

Purpose: Provides x86_64 fio architecture primitives, CPU clock, random instructions, bit operations, and Linux syscall wrappers.

Important APIs: Defines `do_cpuid()`, includes `arch-x86-common.h`, sets `FIO_ARCH arch_x86_64`, huge page size 2 MiB, `rep;nop`, compiler barriers, `arch_ffz()` using `bsf`, `tsc_barrier()` using `mfence`, `get_cpu_clock()` using `rdtsc`, RDRAND/RDSEED opcodes, `arch_rand_long()`, `arch_rand_seed()`, and `__do_syscall0` through `__do_syscall6` using the x86_64 Linux syscall ABI. Enables ffz, SSE4.2, CPU clock, and direct syscall support.

Control flow and integration: Selected by `arch.h` for `__x86_64__`. Generic random, syscall, and timing code can use these fast paths.

State and persistence: No direct state; common x86 init sets `tsc_reliable` and `arch_random`.

Dependencies: x86_64 inline assembly, Linux syscall calling convention, and CPUID feature detection.

Risks and test signals: `arch_rand_seed()` returns 0 regardless of carry flag, so callers cannot detect RDSEED failure from the return value. `arch_rand_long()` returns the retry counter register rather than a normalized boolean, so semantics need caller review. Direct syscall wrappers bypass libc and must match kernel ABI. Tests should cover direct io_uring syscalls, random seeding fallback, and TSC timing on varied CPUs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch-x86_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/arch/arch.h -->
# `sources/test-tools/fio/arch/arch.h`

Purpose: Central architecture abstraction dispatcher for fio.

Important APIs and types: Defines architecture enum values, generic `ARCH_FLAG_*` bits, external `arch_flags`, default `ARCH_CPU_CLOCK_WRAPS`, C/C++ atomic wrapper macros for add/sub/load/store with relaxed/acquire/release orderings, preprocessor selection of the target `arch-*.h`, fallback `tsc_barrier()` under `CONFIG_SYNC_SYNC`, default `arch_init()`, fallback io_uring syscall numbers, and `ARCH_HAVE_IOURING`.

Control flow: Included by platform-independent fio code. The preprocessor selects exactly one architecture header based on compiler macros, then generic code uses feature macros advertised by that header. If no arch header provides `ARCH_HAVE_INIT`, a no-op init is defined.

State and persistence: Declares but does not define `arch_flags`. Atomic wrappers operate on caller-owned state. Arch init may mutate globals depending on selected header.

Dependencies and integration: Depends on C11 `<stdatomic.h>` or C++ `<atomic>`, fio `lib/types.h`, `lib/ffz.h`, and every architecture-specific header.

Risks and test signals: Header selection order matters; `__sparc__` before `__sparc64__` may shadow SPARC64. The C atomic macros cast arbitrary pointers to `_Atomic typeof`, which is practical but relies on compiler extensions. Default io_uring syscall numbers are Linux-specific and overridden only for Alpha. Tests should run preprocessor/compile checks across all supported architectures and validate atomics under C and C++ compilers.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/arch/arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/backend.c -->
# `sources/test-tools/fio/backend.c`

Purpose: Implements fio’s main backend job scheduler and per-job execution engine. It starts jobs as threads or processes, coordinates startup, runs the I/O loop, verification loop, rate control, thinktime, cleanup, stats, triggers, and final result reporting.

Important APIs and functions: External entry point is `fio_backend()`. Other externally visible helpers include `sig_show_status()`, `io_queue_event()`, `in_flight_overlap()`, `log_inflight()`, `invalidate_inflight()`, `clear_inflight()`, `on_fsync_submitted()`, `on_fsync_completed()`, `init_io_u_buffers()`, `exec_trigger()`, and `check_trigger_file()`. Core static paths include `run_threads()`, `thread_main()`, `do_io()`, `do_verify()`, `do_dry_run()`, `reap_threads()`, `init_io_u()`, `cleanup_io_u()`, `fio_io_sync()`, `fio_file_fsync()`, `fio_syncfs()`, `check_min_rate()`, `usec_for_io()`, `handle_thinktime()`, `keep_running()`, and mount/write safety checks.

Control flow: `fio_backend()` loads a profile, sets aggregate logs, initializes dedupe state, startup semaphore, stats, helper thread, cgroup list, then calls `run_threads()`. `run_threads()` installs signal handlers, counts thread/process jobs, optionally serializes file setup, starts idle profiling, creates each job subject to start delays, stonewall, `wait_for`, and process/thread mode, waits for `TD_INITIALIZED`, releases job semaphores, reaps exits, then stops profiling and updates disk ticks. Each job executes `thread_main()`, which sets process identity, initializes locks/lists, waits on the startup handshake, applies uid/gid, zone index, compression, CPU affinity, NUMA, memory pinning, iologs, I/O priority, engine, io_u queues/buffers, verify async, cgroups, scheduler, files, random map, pre-run commands, rate-submit, timestamps, and then loops while `keep_running()`.

I/O and verification behavior: `do_io()` obtains `io_u` objects, fills verify metadata, logs write pieces, submits directly or through offload workqueues, processes queue statuses through `io_queue_event()`, handles residual short I/O, requeues busy/partial operations, enforces runtime, flow thresholds, rate minimums, latency targets, thinktime, fsync/syncfs, fill-device ENOSPC handling, and final completions. `do_verify()` syncs and invalidates caches, reads back logged writes/trims, handles experimental verify, seeds verify headers, sets verify completion callbacks, and reaps verification I/O. `do_dry_run()` advances write accounting without issuing I/O for verify-only replay state.

State and persistence: Global backend state includes startup semaphore, cgroup list/mount, exit value, abort flag, thread/process counts, aggregate bandwidth logs, counters such as `thread_number`, `nr_segments`, `done_secs`, and `overlap_check`. Per-job state is in `thread_data`, including runstate, semaphores, io_u queues, inflight verification arrays, file lists, rate counters, runtime stats, iologs, cgroup, NUMA, and engine-private data. Verify state may be loaded/saved to files or server state; logs and aggregate bandwidth files persist after runs.

Dependencies and integration: Integrates nearly every fio subsystem: ioengines, file setup, verify, iolog, diskutil, cgroup, profiles, random, memory allocation, server/client, stats, idletime, workqueue, mount checks, rate-submit, helper thread, pshared semaphores, zones, and fio time. Platform integrations include signals, fork/wait, pthreads, Linux `prctl`, `syncfs`, cgroups, ioprio, affinity, NUMA, and I/O scheduler switching.

Risks and test signals: This file is high-risk due to concurrency, process/thread dual mode, shared semaphores, signal termination, async engines, offload overlap, verify state, and cleanup ordering. Inflight verify logging uses atomics and aborts on invariant violations, so fsync ordering tests are important. Job startup timeout, stuck reap timeout, and mount-write prevention should be covered. Tests include normal `make test`, full fio job matrix, verify/verify_only/verify_backlog, time_based, rate_min, io_submit_mode=offload, process mode, cgroups, iolog replay, trimwrite, syncfs/end_fsync, mounted block device refusal, trigger files, and server backend operation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/backend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/blktrace.c -->
# `sources/test-tools/fio/blktrace.c`

Purpose: Adds Linux blktrace binary replay and merge support to fio. It detects trace files, converts queued block trace records into fio `io_piece` replay entries, infers workload direction/depth/block sizes, and can merge multiple trace files with scaling and iteration parameters.

Important APIs and functions: Public functions are `is_blktrace()`, `init_blktrace_read()`, `read_blktrace()`, and `merge_blktrace_iologs()`. Key helpers include `discard_pdu()`, `trace_add_file()`, `trace_add_open_close_event()`, `store_ipo()`, `queue_trace()`, `handle_trace_fs()`, `handle_trace_discard()`, `handle_trace_flush()`, `byteswap_trace()`, depth tracking helpers, `init_merge_param_list()`, `find_earliest_io()`, `merge_finish_file()`, `read_trace()`, and `write_trace()`.

Control flow: `is_blktrace()` reads one `blk_io_trace` header and checks magic, with optional endian swap detection. `init_blktrace_read()` opens the file, records swap mode, clears file state, bumps runstate to setup, calls `read_blktrace()`, restores runstate, and requires at least one replay device. `read_blktrace()` streams records, validates magic/version, skips PDU payloads, tracks queue/merge/complete depth, skips writes in read-only mode, converts only queue actions into fio replay pieces, supports chunked iolog reads, records open/close file actions, sets direction flags, max block sizes, and inferred iodepth. Merge support initializes per-trace cursors, validates/scales trace records, writes earliest-time records to a merged output trace, supports repeated iterations, and rewrites the job’s `read_iolog_file` to the merged file.

State and persistence: Uses `td->io_log_rfile`, `io_log_blktrace_swap`, `io_log_last_ttime`, `io_log_current`/highmark/checkmark, `td->io_log_list`, `td->files`, `td->o.size`, direction flags, max block sizes, and inferred `iodepth`. Merging creates a persistent merged blktrace file and mutates thread options to read it.

Dependencies and integration: Linux-only when `FIO_HAVE_BLKTRACE` is enabled. Depends on fio iolog/file APIs, `linux-dev-lookup` for major/minor device resolution, endian helpers, `blktrace_api.h` record layout, replay options such as `replay_align`, `replay_scale`, `replay_skip`, `read_iolog_chunked`, `merge_blktrace_*`, and global `read_only`.

Risks and test signals: `trace_add_file()` returns the cached fileno even if lookup fails, so initial cache value correctness matters. `merge_blktrace_iologs()` opens the output file before checking allocation and does not explicitly handle `fopen()` failure before `setvbuf()`. Depth inference is approximate and capped for stacked devices. Tests should cover native and byte-swapped traces, read/write/trim/flush records, zero-byte trace warnings, read-only skip behavior, device redirection, chunked replay buffer resizing, multiple-device traces, and merged traces with scalars/iterations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/blktrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/blktrace.h -->
# `sources/test-tools/fio/blktrace.h`

Purpose: Declares fio’s blktrace replay interface and cursor state, with stubbed no-op implementations when blktrace support is unavailable.

Important APIs and types: Under `FIO_HAVE_BLKTRACE`, `struct blktrace_cursor` tracks a trace file, current `blk_io_trace`, trace length, endian swap flag, scalar percentage, current iteration, and iteration count. Exported functions are `is_blktrace()`, `init_blktrace_read()`, `read_blktrace()`, and `merge_blktrace_iologs()`. Without support, static inline stubs return false.

Control flow and integration: Included by iolog/init code that needs to detect or replay binary block traces. Conditional compilation lets non-Linux/non-blktrace builds compile without the implementation.

State and persistence: Cursor state is transient during merge. Replay state is stored in `thread_data` by `blktrace.c`.

Dependencies: Requires `<asm/types.h>` and `blktrace_api.h` when enabled, plus fio `thread_data` declarations from surrounding includes.

Risks and test signals: Stub `merge_blktrace_iologs()` returns `false` as an `int`, which is zero/success-like and should match caller expectations carefully. Tests should compile both with and without `FIO_HAVE_BLKTRACE`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/blktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/blktrace_api.h -->
# `sources/test-tools/fio/blktrace_api.h`

Purpose: Provides local copies of Linux blktrace constants and wire structs used by fio to parse binary trace files without depending on a specific kernel header version.

Important APIs and types: Defines trace category bits `BLK_TC_*`, `BLK_TC_SHIFT`, `BLK_TC_ACT()`, basic action enum values such as queue/merge/issue/complete/remap, notify enum values, combined action macros `BLK_TA_*` and `BLK_TN_*`, `BLK_IO_TRACE_MAGIC`, `BLK_IO_TRACE_VERSION`, `struct blk_io_trace`, `struct blk_io_trace_remap`, and `struct blk_user_trace_setup`.

Control flow and integration: `blktrace.c` reads `struct blk_io_trace` records from binary files, validates magic/version, checks action/category bits, endian-swaps fields, and skips PDU payloads based on `pdu_len`.

State and persistence: Defines binary layouts for persisted blktrace files and ioctl setup structures; it has no runtime state itself.

Dependencies: Includes `<asm/types.h>` for fixed-width kernel-style integer aliases.

Risks and test signals: Because this mirrors kernel ABI, drift from current kernel blktrace definitions could break parsing or setup compatibility. Tests should parse known-good traces from representative kernels and compare action decoding against `blkparse` output.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/blktrace_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/cairo_text_helpers.c -->
# `sources/test-tools/fio/cairo_text_helpers.c`

Purpose: Provides small Cairo text drawing helpers for gfio graph/printing UI code, handling horizontal and vertical text alignment around a point.

Important APIs and functions: Public functions are `draw_centered_text()`, `draw_right_justified_text()`, `draw_left_justified_text()`, and `draw_vertical_centered_text()`. Static `draw_aligned_text()` handles centered, left, and right horizontal alignment by measuring `cairo_text_extents_t` and adjusting the drawing origin.

Control flow: Each public horizontal helper delegates to `draw_aligned_text()` with an alignment constant. That helper selects a normal font face, sets font size, measures text, adjusts `x` and `y`, then calls `cairo_show_text()`. The vertical helper measures extents, adjusts coordinates, saves the Cairo state, translates to the pivot, rotates -90 degrees, translates back, draws text, and restores state.

State and persistence: Mutates the passed Cairo context’s font face, font size, current point, and temporarily its transformation matrix. `draw_vertical_centered_text()` restores transformations but not necessarily all text settings.

Dependencies and integration: Includes `cairo_text_helpers.h`, Cairo, GTK, and math for `M_PI`. Integrated into gfio/graphical output builds via the Makefile’s `GFIO_OBJS`.

Risks and test signals: Uses Cairo toy text API, so complex text shaping is not handled. Alignment depends on extents and may be font/backend-sensitive. Tests should render sample labels at each alignment and compare visually or by screenshot in gfio graph outputs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/cairo_text_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/cairo_text_helpers.h -->
# `sources/test-tools/fio/cairo_text_helpers.h`

Purpose: Declares Cairo text helper functions used by fio’s graphical frontend code.

Important APIs: Exposes `draw_centered_text()`, `draw_right_justified_text()`, `draw_left_justified_text()`, and `draw_vertical_centered_text()`, each taking a `cairo_t`, font name, x/y coordinates, font size, and text string.

Control flow and integration: Included by graph/printing UI modules that need aligned labels. The implementation is compiled into gfio-related objects when graphical support is enabled.

State and persistence: No state declared. Functions mutate the supplied Cairo context during drawing.

Dependencies: Includes `<cairo.h>` and therefore requires Cairo development headers in gfio builds.

Risks and test signals: Header is simple, but consumers must pass a valid Cairo context and non-null strings. Build tests should cover gfio enabled/disabled configurations; UI tests should check label placement.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/cairo_text_helpers.h -->
