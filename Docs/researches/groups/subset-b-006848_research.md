# subset-b-006848 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_vmcall_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_vmcall_test.c

## Purpose
`xen_vmcall_test.c` is a KVM selftest for userspace hypercall interception. It verifies that a guest `vmcall` and a guest call through the configured Xen hypercall page produce `KVM_EXIT_XEN` exits with the expected register payload, and that a Hyper-V hypercall page can still be used for a normal Hyper-V hypercall result after Xen interception is enabled.

## Important APIs, Types, And Functions
The test uses the KVM selftest helpers `vm_create_with_one_vcpu()`, `vcpu_set_hv_cpuid()`, `vm_ioctl()`, `vm_userspace_mem_region_add()`, `virt_map()`, `vcpu_run()`, `get_ucall()`, and `kvm_vm_free()`. Kernel-facing APIs include `KVM_CAP_XEN_HVM`, `KVM_XEN_HVM_CONFIG`, `struct kvm_xen_hvm_config`, `KVM_XEN_HVM_CONFIG_INTERCEPT_HCALL`, and the `KVM_EXIT_XEN`/`KVM_EXIT_XEN_HCALL` run-state payload. The guest writes `XEN_HYPERCALL_MSR`, `HV_GUEST_OS_ID_MSR`, and `HV_HYPERCALL_MSR`, and invokes hypercalls with inline assembly.

## Control Flow
`main()` requires Xen HVM hypercall interception support, creates one guest vCPU, exposes Hyper-V CPUID leaves, configures the Xen hypercall MSR, and maps two pages at `HCALL_REGION_GPA`: one for Xen and one for Hyper-V. `guest_code()` first executes `vmcall` directly and expects userspace to return `RETVALUE` in `rax`. It then writes the Xen hypercall page MSR and the Hyper-V guest/hypercall MSRs, calls a Xen hypercall slot based on `INPUTVALUE`, and finally calls the Hyper-V page with a deliberately misaligned input GPA expecting `HV_STATUS_INVALID_ALIGNMENT`. The host loop handles each `KVM_EXIT_XEN`, validates CPL, long mode, input number, and six arguments, writes `run->xen.u.hcall.result`, and otherwise handles guest ucall completion or assertion failures.

## State, Persistence, And Dependencies
All state is transient VM state: guest registers, MSRs, the mapped hypercall pages, and the current `kvm_run` exit payload. No persistent files are written. The test depends on x86 KVM selftest infrastructure, host kernel Xen HVM interception support, Hyper-V CPUID setup helpers, and a system that allows `/dev/kvm` test execution.

## Integration Points
This file integrates the Xen and Hyper-V emulation surfaces in one VM. It exercises the host userspace exit ABI for Xen hypercalls while relying on KVM's Hyper-V hypercall implementation for the invalid-alignment return. It is built and run by the KVM selftests framework under `tools/testing/selftests/kvm/x86`.

## Risks
The test is architecture- and feature-specific and skips unless `KVM_CAP_XEN_HVM` includes `KVM_XEN_HVM_CONFIG_INTERCEPT_HCALL`. Inline assembly register constraints are central to the test; compiler or ABI mistakes could make a failure look like a KVM bug. The test assumes the two-page GPA mapping is free and identity-mapped for guest calls. It validates only the configured simple hypercall payload and one Hyper-V error path, not broader hypercall page behavior.

## Test Signals
Strong success signals are two validated `KVM_EXIT_XEN` exits, guest assertions that both Xen paths return `RETVALUE`, the Hyper-V invalid-alignment status, and clean `UCALL_DONE`. Failure signals are a missing capability, wrong exit reason, mismatched hypercall fields, guest assertion aborts, or inability to configure/map the VM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xen_vmcall_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xss_msr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xss_msr_test.c

## Purpose
`xss_msr_test.c` verifies KVM's handling of the IA32_XSS MSR for x86 guests. It confirms that the MSR initializes to zero and that attempts to set every individual bit either fail as unsupported or, if support appears in the future, are accompanied by save/restore list coverage.

## Important APIs, Types, And Functions
The file uses KVM selftest helpers `vm_create_with_one_vcpu()`, `kvm_cpu_has()`, `vcpu_get_msr()`, `vcpu_set_msr()`, `_vcpu_set_msr()`, `kvm_msr_is_in_save_restore_list()`, and `kvm_vm_free()`. It uses `X86_FEATURE_XSAVES` to gate the test and `MSR_IA32_XSS` as the target MSR. `MSR_BITS` fixes the bit sweep at 64 bits.

## Control Flow
`main()` creates a VM with one vCPU and requires host XSAVES support. It reads `MSR_IA32_XSS`, asserts that it is zero, and writes zero back through the normal setter. It then checks whether IA32_XSS is present in KVM's save/restore list and iterates over all 64 single-bit values. Each `_vcpu_set_msr()` result must be either zero, indicating the write failed at the first entry, or one, indicating the single-entry MSR list was accepted. If any non-zero value is accepted, the test asserts that IA32_XSS is in the save/restore list.

## State, Persistence, And Dependencies
The only mutable state is the vCPU MSR value during test execution. There is no guest code and no persistent output. The test depends on x86 KVM, XSAVES CPU support, and the KVM selftest MSR helper behavior where `KVM_SET_MSRS` returns the count of entries successfully written.

## Integration Points
This is a targeted KVM x86 selftest for MSR emulation and migration state ABI expectations. It connects MSR write acceptance to the save/restore list used by userspace VMMs during migration or state capture.

## Risks
The test intentionally allows future kernels to accept non-zero IA32_XSS values, but only if save/restore coverage exists. It does not check combinations of bits, guest execution effects, or CPUID exposure beyond requiring XSAVES. A change in `_vcpu_set_msr()` return conventions would require corresponding updates to the assertions.

## Test Signals
Expected pass signals are zero initialization, successful zero write, no unexpected `KVM_SET_MSRS` return value, and save/restore list membership if any single-bit non-zero value is accepted. Failures point to initialization regression, unsupported return semantics, or migration-state exposure gaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/xss_msr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/Makefile

## Purpose
This Makefile builds the Landlock selftest binaries and helper executables. It collects all `*_test.c` files as generated test programs, adds the `fs_bench` benchmark, and defines statically linked extended helper programs used by tests that exec or coordinate subprocesses.

## Important APIs, Types, And Functions
Key make variables are `CFLAGS`, `KHDR_INCLUDES`, `LOCAL_HDRS`, `src_test`, `TEST_GEN_PROGS`, `TEST_GEN_PROGS_EXTENDED`, `LDLIBS`, and `LDFLAGS`. The file includes the shared kselftest `../lib.mk`, which supplies standard build and install targets.

## Control Flow
The file adds warning, optimization, and kernel-header include flags, records local headers, expands `*_test.c` into test binaries, appends `fs_bench`, and declares `true`, `sandbox-and-launch`, `wait-pipe`, and `wait-pipe-sandbox` as extended generated programs. It assigns `-lcap -lpthread` to test binaries and static linking to helper binaries both before and after including `lib.mk` so the rules work for plain target names and `$(OUTPUT)/`-prefixed targets.

## State, Persistence, And Dependencies
Build artifacts are generated in the kselftest output directory or local tree depending on the harness. The tests depend on installed kernel UAPI headers, libcap, pthreads, and a static-link-capable toolchain for helpers. The comment reminds developers to run `make -C ../../../.. headers_install` first.

## Integration Points
The Makefile is consumed by the Linux kselftest build system. `audit_test.c` and other Landlock tests depend on the extended helpers named in `common.h`, especially `wait-pipe-sandbox`.

## Risks
Missing libcap, static libc support, or stale UAPI headers can cause build failures unrelated to Landlock behavior. The wildcard-based `src_test` means new `*_test.c` files automatically become test binaries, which is useful but can expose incomplete work. Duplicated linker assignments are intentional for target-prefix coverage but easy to simplify incorrectly.

## Test Signals
Useful signals are successful `make -C tools/testing/selftests/landlock`, all `*_test` programs linking with `-lcap -lpthread`, and helper binaries building statically. Runtime signals come from kselftest execution of the produced binaries and optional `fs_bench` manual runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/audit.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/audit.h

## Purpose
`audit.h` is an inline helper implementation for Landlock audit selftests. It owns the raw netlink audit client, audit rule setup/removal, regex-based record matching, stale-record draining, and convenience matchers for Landlock domain allocation and deallocation records.

## Important APIs, Types, And Functions
The main types are `struct audit_filter`, which describes an audit filter rule keyed by record type and executable path, `struct audit_message`, which wraps a netlink header and several audit payload layouts, and `struct audit_records`, which counts access and domain records. Core helpers include `audit_send()`, `audit_recv()`, `audit_request()`, `audit_filter_exe()`, `audit_filter_drop()`, `audit_set_status()`, `regex_escape()`, `audit_match_record()`, `matches_log_domain_allocated()`, `matches_log_domain_deallocated()`, `audit_count_records()`, `audit_init()`, `audit_init_filter_exe()`, `audit_cleanup()`, and `audit_init_with_exe_filter()`.

## Control Flow
Audit setup starts with `audit_init()`, which opens `NETLINK_AUDIT`, enables audit, sets the audit PID to the test process, installs a short receive timeout, and drains stale messages from the backlog. `audit_init_with_exe_filter()` adds an exclude filter for all executables except the current test binary. Test code can also add `audit_filter_drop()` so only Landlock domain-drop records are allowed through. Matching flows through `audit_match_record()`: it compiles a regex, receives records until the type and content match, skips irrelevant records, records the last same-type mismatch for diagnostics, and optionally extracts the domain ID captured by `REGEX_LANDLOCK_PREFIX`. Deallocation matching temporarily extends the socket timeout when a specific domain ID is expected because domain release is asynchronous.

## State, Persistence, And Dependencies
The helpers mutate global kernel audit state for the active audit socket: enabled status, audit PID, and exclude rules. All state is process lifetime scoped but globally visible enough to conflict with a running audit daemon. Filtering stores executable paths without trailing NUL bytes. The file depends on Linux audit UAPI headers, netlink sockets, POSIX regex, socket timeouts, and kselftest logging macros.

## Integration Points
`audit_test.c` includes this header directly and uses its static functions inside kselftest fixtures. The helpers target Landlock-specific audit records `AUDIT_LANDLOCK_ACCESS` and `AUDIT_LANDLOCK_DOMAIN`, matching message formats emitted by the kernel. `common.h` supplies capability manipulation so tests can briefly gain `CAP_AUDIT_CONTROL` before calling these helpers.

## Risks
The helpers require exclusive audit socket ownership; `audit_init()` can fail with `-EEXIST` if auditd or another test owns the socket. Regexes are tightly coupled to audit message formatting, including field order and escaping. Domain deallocation records are asynchronous, so tests must avoid naïve zero-count assertions without a preceding scan. `audit_filter_exe()` currently supports only `AUDIT_EXE`; using other record types returns `-EINVAL`. Because the helpers alter audit rules, cleanup must run with sufficient capability to avoid contaminating subsequent tests.

## Test Signals
Good signals are successful audit initialization, correct matching of Landlock access/domain records, empty `audit_count_records()` after expected messages are consumed, and cleanup that removes both executable and drop filters. Failures identify audit daemon conflicts, netlink protocol errors, regex drift, timeout races, or missing kernel audit/Landlock support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/audit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/audit_test.c

## Purpose
`audit_test.c` validates Landlock audit logging semantics. It covers signal-scope denials, domain allocation and deallocation messages, log muting flags, fork and thread propagation, TSYNC behavior, and logging across `execve()` into helper binaries.

## Important APIs, Types, And Functions
The file uses Landlock syscalls through wrappers: `landlock_create_ruleset()`, `landlock_restrict_self()`, and Landlock flags such as `LANDLOCK_SCOPE_SIGNAL`, `LANDLOCK_RESTRICT_SELF_LOG_SAME_EXEC_OFF`, `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF`, `LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON`, and `LANDLOCK_RESTRICT_SELF_TSYNC`. It uses the audit helpers from `audit.h`, capability helpers from `common.h`, kselftest fixtures and variants, `fork()`, `pthread_create()`, pipes, `kill(pid, 0)`, `waitpid()`, `mmap()` shared memory, and `execve()` of `wait-pipe-sandbox`. Local helpers include `matches_log_signal()`, `thread_audit_test()`, `thread_sandbox_deny_twice()`, and `matches_log_fs_read_root()`.

## Control Flow
The `audit` fixture disables broad capabilities, briefly enables `CAP_AUDIT_CONTROL`, initializes an audit socket filtered to the current executable, and removes the capability for the test body. `layers` repeatedly stacks signal-scoped Landlock domains in a child, triggers denied `kill()` checks, compares denial and allocation domain IDs, validates monotonically increasing domain IDs, verifies the layer limit returns `E2BIG`, then matches deallocation records in LIFO order from the parent. `thread` verifies that allocation logs identify the thread group ID rather than a secondary thread ID. `log_subdomains_off_fork` proves that muting set through `landlock_restrict_self(-1, LOG_SUBDOMAINS_OFF)` is inherited by a forked child even when the parent has no domain. `log_subdomains_off_tsync` propagates muting to a sibling thread with TSYNC, while `tsync_override_log_subdomains_off` verifies that a later TSYNC without the muting flag re-enables logging for subsequently stacked domains.

The `audit_flags` fixture runs the `signal` test across restrict flag variants. A child applies a signal-scoped ruleset, triggers denials, and either expects no logs for `LOG_SAME_EXEC_OFF` or matches access/allocation/deallocation records for normal logging. It also checks that repeated denials produce exactly the expected count and that deallocation denials match the domain ID. The `audit_exec` fixture uses a filter for `wait-pipe-sandbox`, then `signal_and_open` forks a child that restricts itself and execs the helper. Parent and child coordinate over pipes so the parent can check whether signal and filesystem read-dir denials are logged according to `LOG_NEW_EXEC_ON` and `LOG_SUBDOMAINS_OFF`.

## State, Persistence, And Dependencies
State is mostly process, credential, and kernel audit state: Landlock domain stacks, log-status bits in credentials/domains, audit filters, pipe synchronization, shared memory for domain IDs, and asynchronous deallocation records. No persistent test files are created by this file itself, but it depends on helper executables built by the Landlock Makefile. It requires kernel support for Landlock audit records and `CAP_AUDIT_CONTROL`, and it can conflict with a running audit daemon.

## Integration Points
This file is the main consumer of `audit.h` and `common.h`. It integrates kernel Landlock audit behavior with the kselftest harness and external helper programs (`wait-pipe-sandbox`) used to verify post-exec logging. It exercises interactions between Landlock LSM hooks, credential transfer, thread synchronization, signal permission checks, filesystem access checks, and audit netlink delivery.

## Risks
The tests are timing-sensitive around asynchronous domain deallocation and rely on the helper timeouts in `audit.h`. Audit message regexes must match exact kernel output formatting. Running auditd or another audit consumer can cause initialization failure. Pipe synchronization and thread return values must remain aligned or failures can deadlock or be misattributed. Some scenarios intentionally mutate audit filters mid-test to receive deallocation records, so missing cleanup can affect later tests. Cross-exec assertions rely on the helper binary behavior and executable path resolution.

## Test Signals
Pass signals include successful audit fixture setup/cleanup, matched denial/allocation/deallocation records with consistent domain IDs, no extra access records after drains, expected `-EAGAIN` when logging is muted, `E2BIG` at the maximum domain layer count, correct thread join status, and child exit success. Failures isolate regressions in logging flags, inheritance through fork or TSYNC, TGID attribution, domain lifetime accounting, executable filtering, or audit formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/audit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/base_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/base_test.c

## Purpose
`base_test.c` validates the basic user-space ABI behavior of Landlock syscalls. It focuses on argument validation, ABI/version query behavior, errata query behavior, ruleset file descriptor semantics, file descriptor transfer, and credential transfer paths.

## Important APIs, Types, And Functions
The test uses `landlock_create_ruleset()`, `landlock_add_rule()`, `landlock_restrict_self()`, `struct landlock_ruleset_attr`, `struct landlock_path_beneath_attr`, `LANDLOCK_CREATE_RULESET_VERSION`, `LANDLOCK_CREATE_RULESET_ERRATA`, `LANDLOCK_RULE_PATH_BENEATH`, filesystem access rights such as `LANDLOCK_ACCESS_FS_READ_FILE`, `READ_DIR`, and `EXECUTE`, and logging flags used with `landlock_restrict_self()`. It also uses `prctl(PR_SET_NO_NEW_PRIVS)`, `open()`/`openat()`, `socketpair()`, `send_fd()`/`recv_fd()` from `common.h`, libkeyutils syscalls through `__NR_keyctl`, and kselftest assertions.

## Control Flow
`inconsistent_attr` probes `landlock_create_ruleset()` copy and size validation, including too-small buffers, NULL pointers, page-sized buffers, and non-zero trailing bytes. `abi_version` expects ABI version 9 and checks that query mode rejects non-zero attr pointers/sizes and unknown flags. `errata` queries the errata bitmask and validates incompatible argument combinations. `create_ruleset_checks_ordering`, `add_rule_checks_ordering`, and `restrict_self_checks_ordering` assert the priority order of invalid flags, invalid FDs, invalid types, invalid attrs, permission failures, and valid calls. Additional tests check that arbitrary FDs and logging-flag combinations produce `EBADFD`, `EBADF`, `EINVAL`, or success as expected.

`ruleset_fd_io` verifies that Landlock ruleset FDs reject read/write with `EINVAL`. `ruleset_fd_transfer` sends a ruleset FD across a UNIX socket to a child, where it is enforced and denies opening `/` while allowing `/tmp`; the parent remains unrestricted. `cred_transfer` enforces a directory-read-denying ruleset, then uses `KEYCTL_SESSION_TO_PARENT` from a child to exercise a credential installation path that bypasses normal `cred_prepare` and must preserve Landlock restrictions via credential transfer handling.

## State, Persistence, And Dependencies
The test mutates process credentials through capability dropping, `no_new_privs`, Landlock domain enforcement, UNIX socket FD passing, and session keyring manipulation. It opens `/tmp`, `/`, and `/dev/null` but does not persist files. It requires a kernel exposing Landlock ABI 9 semantics for the hard-coded version assertion and supporting the errata flag, keyctl session operations, and kselftest capability setup.

## Integration Points
`base_test.c` is a foundational Landlock selftest used to catch syscall ABI regressions independent of higher-level filesystem policy tests. It depends on `common.h` for capability management and FD passing and on `wrappers.h` for Landlock syscall wrappers. It interacts with the kernel's Landlock LSM hooks, anonymous inode/ruleset FD operations, UNIX SCM_RIGHTS, and keyring credential-transfer paths.

## Risks
The hard-coded ABI version expectation must be updated when the Landlock ABI advances. Error-ordering tests are intentionally brittle and will fail if the kernel changes validation precedence, even if user-visible behavior remains broadly compatible. `cred_transfer` depends on keyring permissions and session-keyring behavior that can vary with kernel configuration. Tests that call `prctl(PR_SET_NO_NEW_PRIVS)` or enforce Landlock affect the current process for the remainder of that test, so ordering and fixture isolation matter.

## Test Signals
Important pass signals are exact errno matches for invalid calls, successful valid ruleset creation/add/enforcement, inherited restrictions after SCM_RIGHTS transfer and keyctl credential transfer, and unchanged parent access in the FD-transfer test. Failures indicate ABI version drift, validation-order regressions, ruleset FD operation bugs, or lost Landlock state during credential replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/base_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/common.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/common.h

## Purpose
`common.h` provides shared inline helpers and constants for Landlock selftests. It centralizes capability setup/drop logic, UNIX file descriptor passing, Landlock ruleset enforcement helpers, helper binary names, and common network service fixture structures.

## Important APIs, Types, And Functions
Important helpers include `_init_caps()`, `disable_caps()`, `drop_caps()`, `_change_cap()`, `set_cap()`, `clear_cap()`, `set_ambient_cap()`, `clear_ambient_cap()`, `recv_fd()`, `send_fd()`, `enforce_ruleset()`, `drop_access_rights()`, and `set_unix_address()`. Shared types include `struct protocol_variant` and `struct service_fixture`. Constants include `TMP_DIR` and helper binary paths `bin_sandbox_and_launch`, `bin_wait_pipe`, and `bin_wait_pipe_sandbox`.

## Control Flow
Capability helpers first lock out root privilege regain with `SECBIT_NOROOT | SECBIT_NOROOT_LOCKED`, clear the current capability set, optionally repopulate a controlled permitted set needed by tests, and apply it with libcap. `set_cap()` and `clear_cap()` toggle effective bits for individual capabilities, while ambient helpers also manage inheritable state and `cap_set_ambient()`. `send_fd()` and `recv_fd()` construct or parse `SCM_RIGHTS` ancillary data on UNIX sockets. `enforce_ruleset()` sets `PR_SET_NO_NEW_PRIVS` then calls `landlock_restrict_self()`. `drop_access_rights()` creates and immediately enforces a ruleset. `set_unix_address()` builds unique abstract UNIX socket names from TID and an index.

## State, Persistence, And Dependencies
The helpers mutate process credentials, securebits, ambient capabilities, `no_new_privs`, and Landlock domain state. File descriptor passing transfers live kernel FDs between processes but writes no files. Dependencies include libcap, Linux securebits, Landlock wrappers, kselftest harness metadata, UNIX sockets, network socket address types, and standard process APIs.

## Integration Points
This header is included by multiple Landlock tests, including `audit_test.c` and `base_test.c`. It bridges kselftest metadata with Linux capabilities and Landlock enforcement, and its helper binary names must match the programs built by the Landlock Makefile.

## Risks
Capability and securebit changes are process-wide and hard to undo, so tests must be isolated by the harness. `_init_caps()` keeps a curated list of capabilities; new tests needing other capabilities must update it. `recv_fd()` assumes a valid control message is present and can report `-EIO` for malformed messages. Abstract UNIX socket names include `sys_gettid()`, so callers depend on wrapper availability and Linux-specific behavior.

## Test Signals
Indirect test signals are successful fixture setup in Landlock tests, expected capability elevation/drop behavior around audit control, successful ruleset enforcement, and correct FD transfer in `base_test.c`. Failures often appear as unexpected `EPERM`, missing audit setup privilege, failed `SCM_RIGHTS` transfer, or Landlock enforcement setup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/config

## Purpose
This kselftest config fragment lists kernel configuration options needed for the Landlock selftest suite. It ensures the test environment includes Landlock, audit, filesystems, networking, namespaces, cgroups, keys, and other kernel features touched by the tests.

## Important APIs, Types, And Functions
The file is declarative Kconfig input rather than C code. Key options are `CONFIG_SECURITY_LANDLOCK=y`, `CONFIG_SECURITY=y`, `CONFIG_AUDIT=y`, `CONFIG_KEYS=y`, `CONFIG_OVERLAY_FS=y`, `CONFIG_TMPFS=y`, `CONFIG_TMPFS_XATTR=y`, `CONFIG_PROC_FS=y`, `CONFIG_SYSFS=y`, `CONFIG_CGROUPS=y`, network options including `CONFIG_NET`, `CONFIG_INET`, `CONFIG_IPV6`, `CONFIG_NET_NS`, `CONFIG_AF_UNIX_OOB`, and MPTCP options.

## Control Flow
There is no runtime control flow. The kselftest tooling can use this file to identify required or recommended kernel config settings before running the Landlock tests.

## State, Persistence, And Dependencies
The file persists expected kernel build-time state. It does not mutate the system. It depends on kernel config option names remaining valid and aligned with the Landlock selftest coverage.

## Integration Points
The fragment integrates with the Linux selftests configuration-checking workflow. It supports the C tests in this directory by documenting the kernel features they assume, including audit for `audit_test.c`, keys for `base_test.c`, and filesystem/network features used by broader Landlock tests.

## Risks
The config can become stale as tests add dependencies or kernel symbols are renamed. It lists options for the broader directory, not only the files in this work item, so a minimal environment for a single test may need fewer options. Missing `CONFIG_AUDIT` or `CONFIG_SECURITY_LANDLOCK` will cause high-level skips or failures rather than build errors.

## Test Signals
Good signals are config-check passes before running Landlock selftests and runtime availability of Landlock, audit netlink, keyrings, and relevant filesystems. Failures show up as skipped tests, missing syscalls/features, or fixture setup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/fs_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/fs_bench.c

## Purpose
`fs_bench.c` is a Landlock filesystem benchmark. It builds a very deep directory tree with one Landlock rule per directory and repeatedly performs file creation attempts from the deepest directory to measure the cost of expensive Landlock path-walk checks. It can disable Landlock with `-L` to provide a baseline.

## Important APIs, Types, And Functions
Important functions are `usage()`, `build_directory()`, `remove_recursively()`, and `main()`. It uses `landlock_create_ruleset()`, `landlock_add_rule()`, `landlock_restrict_self()`, `LANDLOCK_CREATE_RULESET_VERSION`, filesystem access rights `LANDLOCK_ACCESS_FS_IOCTL_DEV`, `WRITE_FILE`, and `MAKE_REG`, `LANDLOCK_RULE_PATH_BENEATH`, `prctl(PR_SET_NO_NEW_PRIVS)`, `mkdirat()`, `openat()`, `unlinkat()`, `times()`, and `CLOCKS_PER_SEC`.

## Control Flow
`main()` parses `-h`, `-L`, `-d D`, and `-n N`, prints benchmark parameters, records starting CPU times, calls `build_directory()`, runs `num_iterations` `openat(curr, "file.txt", O_CREAT | O_TRUNC | O_WRONLY, 0600)` attempts, records ending CPU times, prints system/user clock deltas, closes the deepest directory FD, and removes the generated tree. `build_directory()` optionally checks Landlock ABI >= 7, creates a ruleset handling write/make/ioctl rights, walks down `depth` nested `d` directories, adding an `IOCTL_DEV`-only rule for each current directory before creating the next child, then enforces the ruleset. `remove_recursively()` opens down to the deepest parent and removes `d` directories while walking back upward.

## State, Persistence, And Dependencies
The benchmark creates a nested `d/d/...` directory tree in the current working directory and removes it at the end. When Landlock is enabled it also creates a ruleset and enforces it on the process after tree creation, which should deny `MAKE_REG`/`WRITE_FILE` at the deepest directory and make each `openat()` fail with `EACCES`. It depends on Landlock ABI 7 or newer, writable current directory, enough path depth/inodes for the requested `-d`, and CPU time accounting through `times()`.

## Integration Points
The Makefile builds this as `fs_bench` alongside the Landlock tests, but it is a benchmark rather than a kselftest harness binary. It provides performance signals for Landlock filesystem access-check refactors and can be run manually with different depths and iteration counts.

## Risks
The default `-d 10000` creates a very deep tree and can be slow or fail on filesystem/path traversal limits. The check `if (fd == 0)` in the Landlock-enabled loop appears intended to detect success but only treats descriptor 0 as success; successful opens returning any other non-negative FD would be closed without error, weakening the assertion. If an error other than `EACCES` follows a prior syscall that left `errno` unchanged, diagnostics could be misleading. Cleanup assumes the expected directory shape and can fail if interrupted or run from a restricted/unexpected directory.

## Test Signals
Benchmark output reports system/user clocks and clocks per second. With Landlock enabled, every file creation should fail with `EACCES`; without `-L`, successful creation would indicate a policy or benchmark assertion issue. With `-L`, successful opens provide the baseline. Cleanup success leaves no nested `d` tree behind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/fs_bench.c -->
