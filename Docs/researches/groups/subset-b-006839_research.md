# subset-b-006839 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd.c

## Purpose

`iommufd.c` is the broad functional selftest suite for `/dev/iommu` and the IOMMUFD userspace ABI. It exercises base ioctl validation, IO address space creation, IOVA mapping and unmapping, process ownership transfer, mock domain attachment, hardware page-table allocation, nested translation, invalidation, dirty tracking, VFIO type1 compatibility, virtual IOMMU objects, virtual event queues, hardware queues, and PASID attach/replace/detach behavior.

## Important APIs, Types, and Functions

The file uses `kselftest_harness.h` fixtures and variants: `iommufd`, `change_process`, `iommufd_ioas`, `iommufd_mock_domain`, `iommufd_dirty_tracking`, `vfio_compat_mock_domain`, `iommufd_viommu`, and `iommufd_device_pasid`. It drives public UAPI ioctls such as `IOMMU_DESTROY`, `IOMMU_IOAS_ALLOC`, `IOMMU_IOAS_MAP`, `IOMMU_IOAS_MAP_FILE`, `IOMMU_IOAS_UNMAP`, `IOMMU_IOAS_COPY`, `IOMMU_IOAS_IOVA_RANGES`, `IOMMU_IOAS_ALLOW_IOVAS`, `IOMMU_OPTION`, `IOMMU_HWPT_ALLOC`, `IOMMU_HWPT_INVALIDATE`, `IOMMU_HWPT_SET_DIRTY_TRACKING`, `IOMMU_HWPT_GET_DIRTY_BITMAP`, `IOMMU_GET_HW_INFO`, `IOMMU_FAULT_QUEUE_ALLOC`, `IOMMU_VIOMMU_ALLOC`, `IOMMU_VDEVICE_ALLOC`, `IOMMU_HW_QUEUE_ALLOC`, `IOMMU_VEVENTQ_ALLOC`, and `IOMMU_VFIO_IOAS`.

The tests depend heavily on helpers from `iommufd_utils.h`, including `test_ioctl_ioas_map*`, `test_cmd_mock_domain*`, `test_cmd_hwpt_alloc*`, `test_cmd_hwpt_invalidate`, `test_cmd_viommu_alloc`, `test_cmd_vdevice_alloc`, `test_cmd_pasid_*`, and dirty-bitmap helpers. Local helpers include `get_huge_page_size()`, `setup_sizes()`, `drop_cap_ipc_lock()`, `/proc/<pid>/status` parsers, `check_access_rw()`, `check_vfio_info_cap_chain()`, and `shuffle_array()`.

## Control Flow and State

`setup_sizes()` runs as a constructor, discovers base and huge page sizes, creates an aligned anonymous mapping at `buffer`, and creates a shared memfd mapping. Each fixture opens `/dev/iommu`, provisions IOAS and optional mock devices, runs a scenario, and uses `teardown_iommufd()` to close the FD and ask the kernel test driver to confirm page references returned to baseline.

The early `iommufd` tests validate command failure modes, command-size ABI rules, future-extension zeroing, global options, and VFIO compatibility ioctls without an attached compat IOAS. `change_process` maps file-backed pages, invokes `IOMMU_IOAS_CHANGE_PROCESS` in parent and child processes, and checks `VmPin`/`VmLck` accounting under no/user/mm accounting modes.

The `iommufd_ioas` fixture covers IOAS object lifetime, direct and fixed IOVA mapping, automatic IOVA allocation, reserved-region conflicts, allowed IOVA windows, unmap semantics, copy between IOAS objects, access-object reads and pins, forked-mm interactions, huge-page alignment options, dmabuf mapping and revocation, nested HWPT allocation, IOPF fault queues, and HWPT invalidation progress accounting. `iommufd_mock_domain` validates that mappings reach one or two mock domains, including anonymous memory, memfd-backed memory, huge pages, reference counts, domain replacement, and copy from access-pinned source IOAS objects.

`iommufd_dirty_tracking` maps buffers at multiple sizes, creates dirty-tracking HWPTs, toggles tracking, verifies device capabilities, marks mock dirty bits, reads bitmaps with and without clear, and repeats against unaligned bitmap pointers and huge-page page-table modes. The VFIO compatibility fixture binds an IOAS to the VFIO type1 or type1v2 compatibility path and validates info capability chains, mapping, unmapping, all-unmap behavior, and huge-map split behavior differences. The `iommufd_viommu` fixture constructs parent/nested HWPTs, virtual IOMMU objects, virtual devices, event queues, IOTLB/cache invalidation, queue IOVA ownership, and tombstone behavior. The final PASID fixture verifies RID and PASID domain compatibility, attach failures, attach/replace/detach state, IOPF on a PASID, non-PASID device restrictions, and preservation of old PASID mappings on replace failure.

Persistent state is mostly kernel IOMMUFD object state: IDs for IOAS, devices, HWPTs, vIOMMUs, vdevices, event queues, fault queues, PASID associations, pinned pages, dirty bits, and queued events. The user-space program also persists temporary buffers, memfds, child processes, and mmap regions for the duration of a test case. It intentionally destroys and recreates objects in varied orders to detect leaked references and lifetime bugs.

## Dependencies and Integration Points

The test requires the IOMMUFD kernel driver, `/dev/iommu`, the in-kernel `iommufd_test` selftest hooks, `linux/vfio.h`, capabilities for option changes and locked-memory accounting, hugepage support for huge variants, memfd and dmabuf support, eventfd, fork/pipe synchronization, and VFIO compatibility ioctls. It integrates with the kselftest harness and validates contracts shared by virtualization, VFIO replacement, nested IOMMU, dirty tracking, vIOMMU, PASID, and I/O page fault consumers.

## Risks and Test Signals

The test is sensitive to kernel configuration, root permissions, huge-page availability, rlimit behavior, and mock-driver semantics. Several cases intentionally expect `EBUSY`, `ENOENT`, `EINVAL`, `EOPNOTSUPP`, `EFAULT`, `ENOSPC`, `ENODEV`, `EOVERFLOW`, or `ENOMEM`, so regressions often appear as changed errno, leaked refs in teardown, missing events, or stale cache/IOTLB state. Strong pass signals include successful TAP completion, no kselftest assertion failures, correct dirty-bit clear/no-clear behavior, VFIO cap-chain bounds preservation, and no object references left after closing `/dev/iommu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_fail_nth.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_fail_nth.c

## Purpose

`iommufd_fail_nth.c` is an IOMMUFD kernel-integrity selftest that sweeps Linux fault-injection points through successful IOMMUFD operation sequences. Its goal is not to prove functional results, but to find WARN/OOPS/KASAN-style failures and cleanup bugs in allocation and error unwinding paths.

## Important APIs, Types, and Functions

The file configures fault injection through debugfs and `/proc/self/task/<pid>/fail-nth`. `writeat()` writes debugfs knobs. `setup_buffer()` creates anonymous and memfd buffers. `setup_fault_injection()` enables useful fail-slab/page-allocation injection and quiets verbose logging. `struct fail_nth_state` records the fail-nth fd and iteration. `fail_nth_first()`, `fail_nth_next()`, and `__fail_nth_enable()` manage the sweep loop.

The `TEST_FAIL_NTH()` macro wraps a fixture test in a repeated setup/run/teardown loop. The single `basic_fail_nth` fixture tracks `/dev/iommu`, an access fd, a mock device id, and a PASID so teardown can clean partially-created state. The swept scenarios cover IOAS core operations, domain mapping, file-backed domain mapping, two-domain mapping, access read/write, access pinning, access pinning with domains, and device/vIOMMU/PASID operations.

## Control Flow and State

Constructors allocate buffers and attempt to configure fault injection. If debugfs fault injection is unavailable, every `TEST_FAIL_NTH` case skips. Otherwise, each test first runs once with injection disabled. Subsequent iterations write the current iteration number into `fail-nth`, re-run fixture setup and the operation sequence, then inspect and disable the fail-nth knob. The loop ends when the kernel reports that no failure point was consumed for the iteration.

The operation sequences deliberately start failure injection after setup that has already been tested, reducing the sweep surface. They return `-1` on any failed syscall or ioctl, allowing the harness to keep advancing the injected failure position. Teardown closes access fds, detaches any active PASID, closes `/dev/iommu`, and rechecks page references via shared IOMMUFD test helpers.

## Dependencies and Integration Points

This file depends on `CONFIG_FAULT_INJECTION`, debugfs mounted at `/sys/kernel/debug`, `/proc/self/task/.../fail-nth`, IOMMUFD selftest ioctls, `/dev/iommu`, and the shared `iommufd_utils.h` helpers. It is intended to be run with kernel debug features and often with `panic_on_warn=1` so kernel splats fail fast. It integrates directly with the IOMMUFD allocation, IOAS, pages, access, device, HWPT, vIOMMU, hardware queue, event queue, fault queue, and PASID paths.

## Risks and Test Signals

The arbitrary 1000-iteration guard can become too small as kernel allocation paths change. Debugfs and fault-injection permissions make the test environment-sensitive. Some cleanup steps can themselves hit injected faults, so the harness includes special handling for `EFAULT` while disabling injection. A useful pass signal is that all fail-nth positions are exhausted without assertion failures, leaked references, dangling PASID mappings, or kernel warnings. Failures are most meaningful when paired with kernel logs or panic-on-warn output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_fail_nth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_utils.h

## Purpose

`iommufd_utils.h` is the shared userspace helper layer for IOMMUFD selftests. It wraps IOMMUFD and in-kernel selftest ioctls in concise assertion macros, owns common buffers and page-size globals, and provides helpers for mock domains, IOAS mappings, HWPTs, invalidation, dirty tracking, access objects, dmabufs, hardware info, fault queues, vIOMMU objects, event queues, hardware queues, and PASID operations.

## Important APIs, Types, and Functions

The header imports `kselftest_harness.h` and `drivers/iommu/iommufd/iommufd_test.h`. It defines bit helpers, IOPT accounting constants, `DIV_ROUND_UP`, global `buffer`, `BUFFER_SIZE`, `mfd_buffer`, `mfd`, and `PAGE_SIZE`, and ioctl-size helpers such as `offsetofend()`.

Key wrappers include `_test_cmd_mock_domain*`, `_test_cmd_hwpt_alloc()`, `_test_cmd_hwpt_invalidate()`, `_test_cmd_viommu_invalidate()`, `_test_cmd_access_replace_ioas()`, dirty-tracking helpers, access-object helpers, dmabuf get/revoke helpers, `_test_ioctl_destroy()`, `_test_ioctl_ioas_alloc()`, `_test_ioctl_ioas_map()`, `_test_ioctl_ioas_unmap()`, `_test_ioctl_ioas_map_file()`, temporary memory-limit helpers, `_test_cmd_get_hw_info()`, `_test_ioctl_fault_alloc()`, `_test_cmd_trigger_iopf()`, `_test_cmd_viommu_alloc()`, `_test_cmd_vdevice_alloc()`, `_test_cmd_hw_queue_alloc()`, `_test_cmd_veventq_alloc()`, `_test_cmd_trigger_vevents()`, `_test_cmd_read_vevents()`, `_test_cmd_pasid_attach()`, `_test_cmd_pasid_replace()`, `_test_cmd_pasid_detach()`, and `test_cmd_pasid_check_hwpt()`.

## Control Flow and State

Most helpers build a UAPI or selftest command struct, call `ioctl()`, and copy returned IDs or counts back to caller storage. Assertion macros convert successful paths into `ASSERT_EQ(0, ...)` and failure paths into `EXPECT_ERRNO()`. The mapping helpers update caller-provided IOVA variables even on fixed and automatic IOVA paths. Invalidation helpers copy the kernel-updated `entry_num` back so tests can verify partial-progress semantics.

Dirty-bitmap helpers mark synthetic dirty bits in the mock domain, retrieve them through `IOMMU_HWPT_GET_DIRTY_BITMAP`, verify coalescing based on test page size versus PTE page size, then verify clear or no-clear behavior. Event helpers trigger virtual events, poll an event fd, read headers and payloads, check sequence gaps/lost-event flags, and validate virtual IDs. `teardown_iommufd()` closes the test fd, reopens `/dev/iommu`, and asks the test driver to check that the shared buffer's page refs are back to zero.

## Dependencies and Integration Points

This header is tightly coupled to the IOMMUFD UAPI headers and the kernel-only IOMMUFD selftest test command ABI. It is included by both the functional and failure-injection IOMMUFD tests. It relies on memfd, mmap, poll, fcntl, ioctl, `__u32`/`__u64` kernel types, kselftest assertions, and selftest mock constants such as `MOCK_APERTURE_START`, `MOCK_PAGE_SIZE`, `MOCK_NESTED_DOMAIN_IOTLB_NUM`, and `IOMMU_TEST_*`.

## Risks and Test Signals

Because helpers hide errno and assertion behavior, wrong helper selection can turn a meaningful error into a hard abort or vice versa. Several helpers assume `self->fd` and fixture fields exist, so they are macro-coupled to test fixture shape. The header has an unusual `#endif` before later helper definitions, meaning only the first part is include-guarded; duplicate inclusion could be risky. Useful validation signals are clean compilation, correct object IDs returned from wrappers, updated invalidation counts, successful page-reference teardown checks, and consistent errno expectations across all call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/iommu/iommufd_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/Makefile

## Purpose

This Makefile builds the IPC selftest program `msgque`. It normalizes x86 architecture names and supplies the correct 32-bit or 64-bit preprocessor symbols for IPC tests that may include architecture-sensitive kernel headers.

## Important APIs, Types, and Functions

It sets `ARCH` from `uname -m`, rewrites `i.86` and `x86_64` to `x86`, sets `CFLAGS` to `-DCONFIG_X86_32 -D__i386__` or `-DCONFIG_X86_64 -D__x86_64__` for x86 variants, appends `$(KHDR_INCLUDES)`, declares `TEST_GEN_PROGS := msgque`, and includes `../lib.mk`.

## Control Flow and State

Make evaluates architecture normalization before including the common kselftest make logic. Build state is limited to generated `msgque` output and the inherited selftest build variables.

## Dependencies and Integration Points

The Makefile depends on the selftests `lib.mk`, kernel header include settings, and a C compiler. It integrates the IPC directory into the broader kselftest build and install flow.

## Risks and Test Signals

The leading spaces before `override ARCH` are harmless in make condition bodies but should stay syntactically valid. Non-x86 architectures do not get extra arch defines. A pass signal is that `make -C tools/testing/selftests/ipc` emits the `msgque` binary and the runner can discover it as a generated program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/config

## Purpose

This config fragment records kernel options needed for the IPC message-queue checkpoint/restore selftest.

## Important APIs, Types, and Functions

It requests `CONFIG_EXPERT=y` and `CONFIG_CHECKPOINT_RESTORE=y`. `CONFIG_CHECKPOINT_RESTORE` is the functional requirement for `/proc/sys/kernel/msg_next_id` and related restore-style IPC behavior.

## Control Flow and State

There is no executable flow. The file is consumed by kselftest configuration tooling as desired Kconfig state.

## Dependencies and Integration Points

It integrates with kselftest config aggregation and the `msgque.c` test. The test also requires SysV IPC support at runtime, but this fragment only lists the checkpoint/restore-specific options.

## Risks and Test Signals

The fragment is minimal; missing SysV IPC options would have to be satisfied elsewhere. A validation signal is that a kernel built with this fragment exposes `/proc/sys/kernel/msg_next_id` and lets root set a target SysV message queue id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/msgque.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/msgque.c

## Purpose

`msgque.c` tests SysV message queue dump and restore behavior needed by checkpoint/restore. It creates a queue, sends two messages, copies queue metadata and messages without consuming them, destroys the original queue, recreates a queue with the same id via `/proc/sys/kernel/msg_next_id`, restores the messages, and verifies the restored queue contents.

## Important APIs, Types, and Functions

The test uses `msgget()`, `msgsnd()`, `msgrcv()`, `msgctl()`, `MSG_STAT`, `MSG_COPY`, `IPC_CREAT`, `IPC_EXCL`, `IPC_RMID`, and `/proc/sys/kernel/msg_next_id`. `struct msg1` stores message size, type, and text. `struct msgque_data` stores key, queue id, mode, qbytes, qnum, and copied messages. Main helpers are `fill_msgque()`, `dump_queue()`, `check_and_destroy_queue()`, and `restore_queue()`.

## Control Flow and State

`main()` requires root, derives a key with `ftok(argv[0], ...)`, creates a queue, fills it with two messages of different types and sizes, dumps the queue using `MSG_STAT` and `MSG_COPY`, drains and removes the original queue, writes the saved queue id to `msg_next_id`, recreates the queue with the same key/id, replays saved messages, and drains/removes it again. The persistent kernel state is the SysV queue id, metadata, and queued messages; user-space persists a heap copy of the messages between destroy and restore.

## Dependencies and Integration Points

The test depends on root privileges, SysV IPC, checkpoint/restore support for `msg_next_id`, `MSG_COPY` support, writable `/proc/sys/kernel/msg_next_id`, and `kselftest.h`. It integrates with CRIU-style restore semantics and validates kernel IPC namespace queue-id allocation.

## Risks and Test Signals

The test can collide with existing queues if the key or requested id is unavailable. `dump_queue()` scans only kernel ids 0 through 255, so environments with a higher index could miss the queue. `MSG_COPY` absence causes a skip. Useful pass signals are matching restored queue id, matching message count, sizes, types, and payloads, and successful `IPC_RMID` cleanup on all paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ipc/msgque.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ir/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ir/Makefile

## Purpose

This Makefile builds and registers the infrared loopback selftest. The shell script is the runnable test, while the C binary is generated as an extended helper.

## Important APIs, Types, and Functions

It sets `TEST_PROGS := ir_loopback.sh`, `TEST_GEN_PROGS_EXTENDED := ir_loopback`, `APIDIR := ../../../include/uapi`, and adds `-Wall -O2 -I$(APIDIR)` to `CFLAGS`, then includes `../lib.mk`.

## Control Flow and State

The common kselftest make rules build `ir_loopback` and install/run `ir_loopback.sh`. Build state is confined to the generated helper binary.

## Dependencies and Integration Points

It depends on UAPI headers that define LIRC and rc protocol constants. It integrates with the IR selftest runner and the `rc-loopback` module invoked by the shell wrapper.

## Risks and Test Signals

If UAPI headers are stale, protocol constants may be missing, though the C file has compatibility fallbacks for older `lirc.h`. A pass signal is successful helper build and script-driven execution through `lib.mk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ir/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.c

## Purpose

`ir_loopback.c` validates the Linux IR encoder/decoder path using the `rc-loopback` device. It sends random LIRC scancodes for many protocols and expects the loopback receiver to decode the same protocol and scancode.

## Important APIs, Types, and Functions

The test uses `linux/lirc.h`, `LIRC_SET_REC_MODE`, `LIRC_SET_SEND_MODE`, `LIRC_MODE_SCANCODE`, `struct lirc_scancode`, sysfs `/sys/class/rc/<rcN>/protocols`, `/dev/lirc*`, `poll()`, `read()`, and `write()`. The `protocols[]` table maps `enum rc_proto` values to protocol names, scancode masks, and decoder names. `lirc_open()` locates a matching lirc character device under a sysfs rc device.

## Control Flow and State

`main()` expects write and read rc device names. It opens the receiver and sender, sets scancode receive/send modes, opens the receiver's protocol sysfs file, then iterates protocol definitions. For each protocol it enables the matching decoder, generates ten masked random scancodes, applies protocol-specific validity filters, writes a `struct lirc_scancode` to the sender, polls the receiver, reads a decoded scancode, and records pass/error counts. Kernel state includes enabled decoders, queued lirc scancodes, and the loopback device's transmit/receive state.

## Dependencies and Integration Points

The test depends on a loaded `rc-loopback` module, root access to sysfs protocol controls and lirc devices, LIRC UAPI support, and kselftest reporting. It integrates with IR protocol encoders, decoders, rc-core, lirc char devices, sysfs protocol selection, and the `ir_loopback.sh` wrapper.

## Risks and Test Signals

Decoding runs in a kernel thread, so timing is handled by a one-second poll but can still be sensitive on overloaded systems. Random scancode generation must avoid invalid NEC and RCMM encodings. Some protocols share decoders, so a decoder-selection regression can affect multiple table entries. Pass signals are matching protocol/scancode pairs and zero kselftest error count after all table entries complete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.sh

## Purpose

`ir_loopback.sh` is the runnable wrapper for the IR loopback C helper. It enforces root, checks that `rc-loopback` is available, loads it, discovers the generated rc device, and invokes `./ir_loopback`.

## Important APIs, Types, and Functions

The script uses `/sbin/modprobe -q -n rc-loopback`, `/sbin/modprobe rc-loopback`, `/sys/class/rc/rc*/uevent`, `grep`, and kselftest skip code `4`.

## Control Flow and State

The script exits skip when not root or the module is unavailable. It loads `rc-loopback`, finds an rc device whose uevent contains `DRV_NAME=rc-loopback`, passes that same device as sender and receiver to the helper, and exits with the helper status. State changes include loading the module and creating sysfs/dev nodes.

## Dependencies and Integration Points

It depends on root, modprobe, the `rc-loopback` kernel module, sysfs rc class entries, and the compiled `ir_loopback` binary in the current directory. It integrates the C helper into the kselftest `TEST_PROGS` model.

## Risks and Test Signals

If multiple rc-loopback devices exist, command substitution can yield multiple names and confuse the helper. The script does not unload the module after completion. Pass/fail signals come from the C helper; wrapper-level skip signals identify missing privileges or module support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/Makefile

## Purpose

This Makefile builds the `kcmp_test` selftest for the `kcmp(2)` syscall.

## Important APIs, Types, and Functions

It appends `$(KHDR_INCLUDES)` to `CFLAGS`, declares `TEST_GEN_PROGS := kcmp_test`, sets `EXTRA_CLEAN := $(OUTPUT)/kcmp-test-file`, and includes `../lib.mk`.

## Control Flow and State

The Makefile has no custom control flow beyond common kselftest build rules. It also arranges cleanup of the temporary file created by the test.

## Dependencies and Integration Points

It depends on kernel headers for `linux/kcmp.h` and kselftest `lib.mk`. It integrates the KCMP directory into generated selftest programs.

## Risks and Test Signals

The main risk is stale cleanup if `OUTPUT` does not match the runtime directory. A pass signal is successful compilation and removal of `kcmp-test-file` during clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/kcmp_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/kcmp_test.c

## Purpose

`kcmp_test.c` smoke-tests selected `kcmp(2)` comparisons between a parent and child process and validates the `KCMP_EPOLL_TFD` comparison path.

## Important APIs, Types, and Functions

It wraps `syscall(__NR_kcmp, ...)` in `sys_kcmp()`. It uses `KCMP_FILE`, `KCMP_FILES`, `KCMP_VM`, `KCMP_FS`, `KCMP_SIGHAND`, `KCMP_IO`, `KCMP_SYSVSEM`, `KCMP_EPOLL_TFD`, `struct kcmp_epoll_slot`, `epoll_create1()`, `epoll_ctl()`, `pipe()`, `dup2()`, `fork()`, and kselftest counters.

## Control Flow and State

The parent creates `kcmp-test-file`, a pipe, an epoll instance, and duplicated fd number 64. It adds both pipe ends to epoll as needed, forks, and the child opens the same file path independently. The child prints sample comparison values, then runs three planned checks: comparing the same file fd returns 0, comparing a process with itself for `KCMP_VM` returns 0, and `KCMP_EPOLL_TFD` finds the duplicated pipe target in the epoll set. The parent waits for the child.

## Dependencies and Integration Points

The test depends on `kcmp` syscall availability, epoll, fork, file descriptor inheritance, and kernel headers. It integrates with CRIU-style process resource comparison coverage.

## Risks and Test Signals

Permissions or ptrace restrictions can affect `kcmp()` across processes, though parent/child usually work. The parent returns 0 regardless of child failure status, so the runner primarily sees the child's kselftest exit in output rather than a propagated parent status. Strong local signals are the child's three PASS lines and no syscall errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/kcmp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/Makefile

## Purpose

This Makefile registers kexec selftests for supported architectures. It includes load and file-load shell tests on x86 and ppc64le, and adds the kexec jump binary/script only for 64-bit x86.

## Important APIs, Types, and Functions

It computes `ARCH_PROCESSED` from `ARCH`, gates test registration on `x86` or `ppc64le`, declares `TEST_PROGS := test_kexec_load.sh test_kexec_file_load.sh`, `TEST_FILES := kexec_common_lib.sh`, includes `../../../scripts/Makefile.arch`, and conditionally adds `test_kexec_jump.sh` plus `TEST_GEN_PROGS := test_kexec_jump` when `IS_64_BIT` and x86 are true.

## Control Flow and State

Make-time conditionals determine which tests exist for the target architecture. Build state includes the optional `test_kexec_jump` binary and installed shared shell library.

## Dependencies and Integration Points

It depends on common kselftest make logic, architecture helper make variables, shell scripts, kexec tooling, and a C compiler for the jump helper. It integrates the directory with kselftest build/install and runtime discovery.

## Risks and Test Signals

Unsupported architectures silently skip the whole Makefile body. Incorrect `ARCH` normalization can omit tests. A pass signal is that supported architectures install the expected shell tests and, on x86_64, build `test_kexec_jump`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/config

## Purpose

This kselftest config fragment lists security and IMA options relevant to kexec signature-policy tests.

## Important APIs, Types, and Functions

It requests `CONFIG_IMA_APPRAISE=y`, `CONFIG_IMA_ARCH_POLICY=y`, and `CONFIG_SECURITYFS=y`.

## Control Flow and State

There is no executable logic. The fragment is consumed by config-generation tooling.

## Dependencies and Integration Points

It aligns with `kexec_common_lib.sh` and `test_kexec_file_load.sh`, which inspect IMA appraisal, architecture policy, and securityfs runtime policy.

## Risks and Test Signals

The fragment does not request `CONFIG_KEXEC`, `CONFIG_KEXEC_FILE`, or signature-enforcement options, so test scripts still inspect the running kernel and skip or branch accordingly. A validation signal is that securityfs exposes IMA policy when the running kernel allows it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/kexec_common_lib.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/kexec_common_lib.sh

## Purpose

`kexec_common_lib.sh` is the shared shell library for kexec selftests. It provides logging, kselftest pass/fail/skip exits, root checks, running-kernel config discovery, Secure Boot detection, securityfs mounting, and IMA policy lookup.

## Important APIs, Types, and Functions

Key variables are `VERBOSE`, `IKCONFIG`, `KERNEL_IMAGE`, and `SECURITYFS`. Important functions include `log_info()`, `log_pass()`, `log_fail()`, `log_skip()`, `get_efivarfs_secureboot_mode()`, `get_ppc64_secureboot_mode()`, `get_arch()`, `get_secureboot_mode()`, `require_root_privileges()`, `kconfig_enabled()`, `get_kconfig()`, `mount_securityfs()`, and `check_ima_policy()`.

## Control Flow and State

Consumers source the file and then call its functions. `get_kconfig()` tries `/lib/modules/$(uname -r)/config`, `/proc/config.gz` after loading `configs`, and finally `scripts/extract-ikconfig` against the boot image or `configs.ko`. Secure Boot detection reads EFI variables or a ppc64le device-tree property. `mount_securityfs()` mounts securityfs if not already mounted. `check_ima_policy()` greps policy rules for an action and up to two key-value constraints.

## Dependencies and Integration Points

The library depends on root for kexec and securityfs operations, `grep`, `awk`, `find`, `hexdump`, `cut`, `modprobe`, `gunzip`, `mount`, `extract-ikconfig`, `/boot/vmlinuz-$(uname -r)`, efivarfs or ppc device-tree files, and IMA securityfs. It integrates with `test_kexec_load.sh`, `test_kexec_file_load.sh`, and `test_kexec_jump.sh`.

## Risks and Test Signals

Several conditionals use unquoted variables, so empty values can cause shell test errors in unusual environments. `kconfig_enabled()` returns 1 for found and 0 for not found, intentionally inverted from typical shell success. `SECURITYFS` is computed at source time and may be stale until mounted. Pass signals are reliable config extraction, correct Secure Boot classification, and accurate IMA policy detection for downstream tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/kexec_common_lib.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_file_load.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_file_load.sh

## Purpose

`test_kexec_file_load.sh` validates `kexec_file_load` behavior against kernel signature requirements, Secure Boot state, IMA appraisal policy, PE signatures, IMA xattrs, and appended module signatures.

## Important APIs, Types, and Functions

It sources `kexec_common_lib.sh` and uses `kexec --load --kexec-file-syscall`, `kexec --unload --kexec-file-syscall`, `pesign`, `getfattr`, `tail`, and kernel config probes. Functions include `is_ima_sig_required()`, `check_for_pesig()`, `check_for_imasig()`, `check_for_modsig()`, and `kexec_file_load_test()`.

## Control Flow and State

The script requires root, extracts kernel config, skips if `CONFIG_KEXEC_FILE` is absent, records IMA/security/keyring/signature policy booleans, detects Secure Boot, checks whether the current kernel image has PE, IMA, or appended signatures, then attempts a file-syscall kexec load. If loading succeeds, it unloads and verifies that success is consistent with signature policy. If loading fails, it maps failures such as missing keys or missing required signatures to expected pass outcomes.

Persistent state changes are limited to a transient loaded kexec image, an optional temporary `IKCONFIG`, and securityfs mount side effects from the shared library.

## Dependencies and Integration Points

The script depends on root, `kexec-tools`, current kernel image at `/boot/vmlinuz-$(uname -r)`, config extraction, optional `pesign`, `getfattr`, IMA/securityfs policy visibility, Secure Boot firmware state, and platform keyrings. It integrates kernel config policy, runtime IMA policy, and kexec syscall enforcement.

## Risks and Test Signals

This test treats some failures as pass when policy should reject unsigned images, so interpreting output requires the logged policy state. Missing `pesign` or `getfattr` causes skip even in paths where their signature type might not matter. Policy-rule presence is assumed to express intent even though IMA policy is sequential. Strong signals are correct load/unload behavior and pass messages that explain whether success or failure matched signature requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_file_load.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.c

## Purpose

`test_kexec_jump.c` is a low-level x86_64 helper that tests `KEXEC_PRESERVE_CONTEXT` jump behavior. It loads a tiny in-process purgatory segment, performs a kexec jump, returns to Linux, then jumps again to the alternate entry.

## Important APIs, Types, and Functions

The file uses inline assembly labels `purgatory_start`, `purgatory_start_b`, and `purgatory_end`, `struct kexec_segment`, `syscall(__NR_kexec_load, ...)`, `KEXEC_PRESERVE_CONTEXT`, and `syscall(__NR_reboot, ..., LINUX_REBOOT_CMD_KEXEC)`.

## Control Flow and State

The assembly emits two entry points. Each triggers `int3`, writes the next entry address into the saved return slot at `8(%rsp)`, and returns to Linux. `main()` loads the segment at physical address `0x400000`, asks the kernel to preserve context, invokes kexec reboot twice, and prints success if both returns work. Kernel state includes a loaded kexec image and preserved CPU/memory context.

## Dependencies and Integration Points

It is x86_64-specific, depends on root, `CONFIG_KEXEC_JUMP`, `kexec_load`, reboot syscall support, and a system that survives the debug exception path. It is wrapped by `test_kexec_jump.sh`.

## Risks and Test Signals

The test can crash or reboot the kernel if the kexec jump path is broken. The hard-coded load address and x86_64 assembly make it unsuitable for other architectures. A pass signal is returning from two kexec jumps and printing `Success`; failure may appear as syscall errno or system crash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.sh

## Purpose

`test_kexec_jump.sh` gates and runs the x86_64 `test_kexec_jump` helper. It skips unsafe or unsupported configurations and reports kselftest status.

## Important APIs, Types, and Functions

It sources `kexec_common_lib.sh`, calls `require_root_privileges()`, `get_kconfig()`, `kconfig_enabled()`, and `get_secureboot_mode()`, then executes `./test_kexec_jump`.

## Control Flow and State

The script requires root, checks `CONFIG_KEXEC_JUMP`, records IMA appraisal and architecture policy state, detects Secure Boot, skips when Secure Boot and architecture IMA policy are both enabled, and otherwise runs the helper. It passes if the helper exits 0 and fails if control returns with nonzero status.

## Dependencies and Integration Points

It depends on the common kexec library, generated `test_kexec_jump`, root privileges, kernel config extraction, and kexec jump support. It integrates security-policy gating with the dangerous kexec-jump runtime test.

## Risks and Test Signals

The most likely severe failure is a kernel crash rather than a clean script failure. The script intentionally skips secure-boot-plus-IMA-arch-policy systems. Pass signal is `kexec_jump succeeded`; skip signal means the environment cannot safely or meaningfully run it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_jump.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_load.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_load.sh

## Purpose

`test_kexec_load.sh` validates legacy `kexec_load` behavior under Secure Boot and IMA architecture policy. It expects loading to be blocked when secure boot and architecture policy require it, and otherwise treats a successful load as acceptable.

## Important APIs, Types, and Functions

It sources `kexec_common_lib.sh`, probes `CONFIG_KEXEC`, `CONFIG_IMA_APPRAISE`, `CONFIG_IMA_ARCH_POLICY`, and Secure Boot state, then uses `kexec --load $KERNEL_IMAGE` and `kexec --unload`.

## Control Flow and State

The script requires root, extracts config, skips without `CONFIG_KEXEC`, determines policy state, attempts a legacy kexec load, unloads on success, and compares the result against secure-boot and IMA-arch-policy expectations. It changes kernel state transiently by loading and unloading a kexec image.

## Dependencies and Integration Points

It depends on root, `kexec-tools`, a boot kernel image, config extraction, Secure Boot detection, and the shared kexec library. It integrates with policy enforcement for the legacy syscall path.

## Risks and Test Signals

A failed legacy load is only a pass under secure boot plus IMA architecture policy; otherwise it is a failure. A successful load under that policy is a failure. Pass logs distinguish `kexec_load succeeded` from expected `kexec_load failed`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kexec/test_kexec_load.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/arm64.conf -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kho/arm64.conf

## Purpose

`arm64.conf` supplies architecture-specific QEMU, kernel-image, command-line, and Kconfig settings for the Kexec Handover selftest on AArch64.

## Important APIs, Types, and Functions

It defines `QEMU_CMD="qemu-system-aarch64 -M virt -cpu max"`, serial driver Kconfig entries for PL010/PL011, `KERNEL_IMAGE="Image"`, and `KERNEL_CMDLINE="console=ttyAMA0"`.

## Control Flow and State

There is no executable flow beyond variable assignment when sourced by `vmtest.sh`.

## Dependencies and Integration Points

It depends on `qemu-system-aarch64`, an arm64 kernel build, and serial console support. It integrates with the shared KHO VM test script.

## Risks and Test Signals

If QEMU, CPU model, or serial config is unsupported, `vmtest.sh` will skip or fail during build/run. Pass signal is a QEMU serial log containing the KHO success marker after using these settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/arm64.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/init.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kho/init.c

## Purpose

`init.c` is the tiny static init program placed into the KHO test initrd. It mounts minimal filesystems, loads the embedded kernel with `kexec_file_load`, and reboots into it to exercise Kexec Handover restore.

## Important APIs, Types, and Functions

It uses `mount()`, `open()`, `read()`, `close()`, `syscall(__NR_kexec_file_load, ...)`, `KEXEC_FILE_NO_INITRAMFS`, and `reboot(RB_KEXEC)`/`reboot(RB_AUTOBOOT)`. `mount_filesystems()` mounts debugfs and proc. `kexec_load()` reads `/proc/cmdline`, opens `/kernel`, and calls `kexec_file_load()`.

## Control Flow and State

At boot as init, it mounts `/debugfs` and `/proc`, reads and null-terminates the current command line, opens `/kernel` from the initrd, loads it as a no-initramfs kexec target, and reboots with `RB_KEXEC`. Any failure falls back to `RB_AUTOBOOT`. Persistent state is the loaded kexec target and the KHO/debugfs kernel state observed by the subsequent boot.

## Dependencies and Integration Points

The program depends on nolibc-style static compilation in `vmtest.sh`, proc/debugfs mount support, `kexec_file_load`, `/kernel` in initrd, and kernel KHO options. It integrates with QEMU-based KHO validation.

## Risks and Test Signals

`COMMAND_LINE_SIZE` is hard-coded from x86 setup headers, which is acceptable for the test but not a general ABI. The code assumes `/proc/cmdline` read includes a newline and writes `cmdline[len - 1] = 0`. Pass signal is indirect: the second kernel boot logs `KHO restore succeeded` for `vmtest.sh` to grep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/vmtest.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kho/vmtest.sh

## Purpose

`vmtest.sh` builds and runs a QEMU-based Kexec Handover selftest. It prepares a kernel config with KHO and test support, builds the kernel and headers, creates a small initrd with `init.c` and the kernel image, boots QEMU, and checks serial output for successful KHO restore.

## Important APIs, Types, and Functions

The script uses `ktap_helpers.sh` and functions `usage()`, `cleanup()`, `skip()`, `fail()`, `build_kernel()`, `mkinitrd()`, `run_qemu()`, `target_to_arch()`, and `main()`. It runs `make olddefconfig`, kernel image builds, `headers_install`, static `$CROSS_COMPILE`gcc with nolibc include paths, `usr/gen_init_cpio`, and QEMU with `-kernel`, `-initrd`, `-append`, and serial-file logging.

## Control Flow and State

`main()` parses build directory, jobs, and target architecture. It prints a one-test KTAP plan, verifies cross-compile settings, creates a build directory, sources the target arch config, writes a KHO config fragment into `.config`, verifies required options survived `olddefconfig`, builds kernel and headers, builds the init binary, creates a cpio initrd containing `/init` and `/kernel`, runs QEMU with `kho=on panic=-1`, and greps the serial log for `KHO restore succeeded`.

Persistent state includes a build tree, temporary initrd files under `/tmp/kho-test.*`, and QEMU serial logs. Cleanup removes the temp directory and finishes KTAP.

## Dependencies and Integration Points

The test depends on a kernel source tree, make, a compiler or cross compiler, QEMU for the target, optional KVM/HVF/TCG acceleration, `gen_init_cpio`, nolibc headers, KHO kernel config, arch-specific `.conf` files, and KTAP helpers. It integrates kernel build, initrd generation, virtual boot, kexec handover, debugfs KHO test support, and kselftest reporting.

## Risks and Test Signals

The script uses `trap skip ERR`, so many preparation failures become skips rather than failures. It overwrites the build directory `.config` with the KHO fragment, so callers should use a dedicated build directory. QEMU command support and acceleration differ across hosts. The primary pass signal is a KTAP pass plus a serial log containing `KHO restore succeeded`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/vmtest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/x86.conf -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kho/x86.conf

## Purpose

`x86.conf` supplies architecture-specific settings for the Kexec Handover VM test on x86.

## Important APIs, Types, and Functions

It defines `QEMU_CMD=qemu-system-x86_64`, serial 8250 Kconfig, `KERNEL_IMAGE="bzImage"`, and `KERNEL_CMDLINE="console=ttyS0"`.

## Control Flow and State

The file only assigns variables when sourced by `vmtest.sh`.

## Dependencies and Integration Points

It depends on `qemu-system-x86_64`, x86 kernel image layout, and 8250 serial console support. It integrates with `vmtest.sh` target selection.

## Risks and Test Signals

Missing 8250 console support would hide the success marker from the serial log. Pass signal is QEMU boot and KHO success using these x86 settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kho/x86.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/Makefile

## Purpose

This Makefile registers the kmod stress-test shell script without building binaries. It prevents an argument-less `make` from running tests by defining a no-op `all` target.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := kmod.sh`, includes `../lib.mk`, and defines an empty `clean` target.

## Control Flow and State

Build control is minimal: no generated artifacts and no cleanup work.

## Dependencies and Integration Points

It integrates `kmod.sh` into kselftest and relies on kernel modules declared in `config`.

## Risks and Test Signals

The test driver is loaded at runtime rather than built here. A pass signal is that kselftest installs and invokes `kmod.sh` as a test program.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/config

## Purpose

This config fragment lists kernel modules needed by the kmod loader selftests.

## Important APIs, Types, and Functions

It requests `CONFIG_TEST_KMOD=m` and `CONFIG_TEST_LKM=m`.

## Control Flow and State

There is no executable flow; kselftest config tooling consumes it.

## Dependencies and Integration Points

`kmod.sh` expects `test_kmod` to expose sysfs knobs and `test_module` to be loadable. This fragment supplies those pieces as modules.

## Risks and Test Signals

If modules are built-in or unavailable under different names, the script's `modprobe` and sysfs assumptions can fail. A validation signal is `/sys/devices/virtual/misc/test_kmod0/` appearing after loading `test_kmod`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/kmod.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/kmod.sh

## Purpose

`kmod.sh` is a stress and regression test for the kernel module loader and usermode-helper module autoloading. It drives the `test_kmod` kernel test driver through sysfs knobs to exercise `request_module()` and filesystem `get_fs_type()` paths, concurrency limits, nonexistent modules/filesystems, modprobe path changes, and kernel address visibility restrictions.

## Important APIs, Types, and Functions

The script uses `/sys/devices/virtual/misc/test_kmod0/` files such as `config_test_case`, `config_num_threads`, `config_test_driver`, `config_test_fs`, `trigger_config`, `test_result`, `reset`, and `config`. It also uses `/proc/sys/kernel/modprobe`, optional `/proc/sys/kernel/kmod-limit`, `modprobe`, `kmod --version`, `capsh --drop=CAP_SYSLOG`, `/proc/modules`, and `/sys/module/<module>/sections/.*text`.

It defines test IDs `0001` through `0013`. Helper functions configure defaults, trigger tests, translate errno names and values, verify expected results, list tests, parse CLI modes, repeat cases, and watch tests indefinitely.

## Control Flow and State

The script checks requirements, applies overridable defaults, loads `test_kmod`, saves the current modprobe path, installs a trap to restore it, and runs all tests or selected tests. Each test resets the driver, configures driver or filesystem mode, writes module/filesystem names and thread counts, triggers the kernel test, and compares `test_result` to expected errno. High-concurrency cases intentionally exceed `kmod-limit` by a fraction. Visibility tests load `test_module`, compare privileged and CAP_SYSLOG-dropped address visibility, and require unprivileged output to be zeroed or hidden.

Persistent state includes loaded/unloaded modules, sysfs test-driver configuration, `/proc/sys/kernel/modprobe`, and possibly the default filesystem module state.

## Dependencies and Integration Points

The test requires root, `modprobe`, `kmod` version greater than 19, `test_kmod`, `test_module`, a default filesystem module that is not already loaded, `capsh` for visibility tests, enough memory for stress cases, and kselftest skip semantics. It integrates with kernel request-module concurrency, usermode-helper execution, filesystem module autoloading, and kernel pointer/address exposure policy.

## Risks and Test Signals

The source contains `errno_val_to_name()` without an opening `{`, which would be a shell syntax error if unchanged in execution. Environment defaults are referenced with `set -e` and unbound-variable-sensitive patterns, so exported overrides matter. Tests mutate `/proc/sys/kernel/modprobe` and must restore it. Pass signals are all selected test cases printing expected errno names and the final trap reporting completion; skip signals indicate missing modules, tools, root, or old kmod.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/kmod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest.h

## Purpose

`kselftest.h` is the low-level C reporting API for Linux selftests that do not use `kselftest_harness.h`. It emits TAP-compatible output, tracks pass/fail/skip/xfail/xpass/error counters, and exits with kselftest-standard status codes.

## Important APIs, Types, and Functions

The header defines `KSFT_PASS`, `KSFT_FAIL`, `KSFT_XFAIL`, `KSFT_XPASS`, `KSFT_SKIP`, `ARRAY_SIZE`, optional x86 `__cpuid_count`, and `struct ksft_count`. Key functions are `ksft_print_header()`, `ksft_set_plan()`, `ksft_print_cnts()`, `ksft_print_msg()`, `ksft_print_dbg_msg()`, `ksft_perror()`, `ksft_test_result_*()`, `ksft_test_result_code()`, `ksft_exit_*()`, `ksft_finished()`, `ksft_min_kernel_version()`, and `ksft_reset_state()`.

## Control Flow and State

The API keeps static process-local counters and a plan count. Tests print a TAP header, set a plan, emit result lines, then call a finish or exit helper. Result helpers increment counters before printing, so the current test number is derived from aggregate counters. Exit helpers print totals and call `exit()` with the proper kselftest code. `ksft_exit_skip()` emits `1..0 # SKIP` if no tests ran, or a skip result if a plan/results already exist.

## Dependencies and Integration Points

It depends on libc unless `NOLIBC` is defined. It integrates with nearly every C selftest and with runner scripts that interpret exit codes and TAP/KTAP output. It also provides compatibility definitions used by older compiler environments.

## Risks and Test Signals

`ksft_print_dbg_msg()` passes a `va_list` into `ksft_print_msg()` as though it were normal varargs, so debug output may be wrong if enabled. `ksft_finished()` treats xpass as successful for exit purposes, which is intentional in this API but can surprise consumers. Pass signals are correct TAP version, plan, ordered result lines, totals, and standard exit codes consumed by the kselftest runner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ksft.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ksft.py

## Purpose

`ksft.py` is a small Python kselftest reporting helper. It mirrors a subset of the C kselftest API for Python tests by printing TAP output, counting pass/fail/skip results, and exiting with standard kselftest codes.

## Important APIs, Types, and Functions

It defines global `ksft_cnt`, `ksft_num_tests`, `ksft_test_number`, and constants `KSFT_PASS`, `KSFT_FAIL`, and `KSFT_SKIP`. Public functions include `print_header()`, `set_plan()`, `print_cnts()`, `print_msg()`, `test_result_pass()`, `test_result_fail()`, `test_result_skip()`, `test_result()`, `finished()`, `exit_fail()`, and `exit_pass()`.

## Control Flow and State

Python tests call header/plan helpers, then result helpers. `_test_print()` emits `ok` or `not ok` with the current test number and optional directive, then increments `ksft_test_number`. `finished()` exits success only if pass plus skip count equals the plan; failures produce exit code 1. `print_cnts()` emits totals in the same broad format as the C helper, with xfail/xpass/error fixed at zero.

## Dependencies and Integration Points

The module depends only on Python `sys`. It integrates Python selftests into the same TAP and exit-code expectations as the shell runner.

## Risks and Test Signals

There is no xfail/xpass/error support and no automatic plan mismatch detail beyond final fail. Descriptions are printed directly and should already be safe single-line TAP text. Pass signals are well-formed TAP lines, accurate counters, and exit code 0 when all planned tests passed or skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ksft.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ktap_helpers.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ktap_helpers.sh

## Purpose

`ktap_helpers.sh` provides shell functions for emitting KTAP/TAP output and kselftest-compatible exit statuses. It is used by shell tests and runners that need consistent result formatting.

## Important APIs, Types, and Functions

It defines counters `KTAP_TESTNO`, `KTAP_CNT_PASS`, `KTAP_CNT_FAIL`, `KTAP_CNT_XFAIL`, `KTAP_CNT_SKIP`, exit constants `KSFT_PASS`, `KSFT_FAIL`, `KSFT_XFAIL`, `KSFT_XPASS`, `KSFT_SKIP`, and `KSFT_NUM_TESTS`. Public functions include header/message/plan helpers, skip-all, pass/fail/xfail/xpass/skip result functions, counter printing, `ktap_exit_fail()`, `ktap_exit_pass()`, `ktap_exit_skip()`, `ktap_finished()`, and aliases expected by older tests.

## Control Flow and State

Each result helper prints an `ok` or `not ok` line with the current test number, increments the matching counter, and advances `KTAP_TESTNO`. Finish helpers compare counters to plan, print totals, and exit. Skip-all emits a zero-plan skip and exits skip. The script holds all state in shell globals, so sourced callers share one counter set.

## Dependencies and Integration Points

It depends only on POSIX-ish shell features and is sourced by `runner.sh`, `kho/vmtest.sh`, and other shell selftests. It bridges shell tests into the same result vocabulary as C and Python helpers.

## Risks and Test Signals

Because state is global, tests running in subshells may need manual counter reconciliation, as `runner.sh` does for network namespaces. Message arguments are echoed directly. Pass signals are monotonic test numbers, accurate totals, and expected exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/ktap_helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/module.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/module.sh

## Purpose

`module.sh` is a generic wrapper for selftests implemented as loadable kernel modules. It loads a named module, removes it on success, and reports pass/fail/skip using simple kselftest text.

## Important APIs, Types, and Functions

It parses `<description> <module_name> [modprobe args...]`, uses `/sbin/modprobe -q -n` for availability, `/sbin/modprobe -q` to load, `/sbin/modprobe -q -r` to remove, and checks root by testing write access to `/dev`. Functions include `main()`, `parse_args()`, `assert_root()`, `assert_have_module()`, `run_module()`, `say()`, `fail()`, and `skip()`.

## Control Flow and State

The script validates arguments, skips if not root or the module is unavailable, loads the module with optional args, removes it if load succeeds, and emits `<description>: ok`. A load failure emits `[FAIL]` and exits 1. Runtime state is the module loaded/unloaded state.

## Dependencies and Integration Points

It depends on `/sbin/modprobe`, root privileges, and kernel modules whose init/exit functions perform the actual test. It is intended to be called by per-module wrapper scripts under selftests.

## Risks and Test Signals

The root check is indirect and may not match all permission models. If module removal fails, the script still says ok because it does not check remove status. Pass signal is successful module load and nominal remove; skip signal identifies missing privilege or module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/module.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/prefix.pl -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/prefix.pl

## Purpose

`prefix.pl` prefixes every line of streamed test output with `# ` so raw test logs become TAP comments. It preserves unbuffered behavior for runner pipelines.

## Important APIs, Types, and Functions

The script uses Perl `sysread()` one byte at a time, `IO::Handle`, binary stdin/stdout modes, and stdout autoflush.

## Control Flow and State

It tracks whether the next byte begins a new line. At line start it prints `# `, then echoes bytes until newline, where it marks the next byte as needing a prefix. EOF exits 0.

## Dependencies and Integration Points

It depends on Perl and is called by `runner.sh` through `tap_prefix()` when available. It integrates arbitrary test stdout/stderr into TAP-safe comments while preserving streaming behavior.

## Risks and Test Signals

Byte-at-a-time IO is simple but potentially inefficient for very large logs. Binary mode avoids newline translation surprises. Pass signal is every emitted line being prefixed with `# ` without delaying output until process exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/prefix.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/runner.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/runner.sh

## Purpose

`runner.sh` is the common shell runner for executing selftest programs in a directory. It applies per-test settings, optional timeouts and arguments, prefixes test output as TAP comments, maps exit codes to KTAP result lines, and can run tests inside temporary network namespaces.

## Important APIs, Types, and Functions

The runner requires `BASE_DIR` before sourcing, then sources `kselftest/ktap_helpers.sh`. It exports defaults such as `timeout_rc=124`, `logfile`, `per_test_logging`, `per_test_log_dir`, `RUN_IN_NETNS`, and `kselftest_default_timeout=45`. Functions include `tap_prefix()`, `tap_timeout()`, `run_one()`, `in_netns()`, `run_in_netns()`, and `run_many()`.

## Control Flow and State

`run_one()` resets timeout state, derives a sanitized environment variable name for per-test args, reads optional `settings` lines into `kselftest_*` variables, applies timeout override, chooses an executable, `ksft_runner.sh`, or shebang interpreter path, runs the command from its directory under nested `timeout` if available, prefixes all output into the log, captures the exit code, and emits pass/skip/xfail/timeout/fail KTAP. `run_many()` either runs tests sequentially or dispatches them in parallel network namespaces and reconciles counters from child exit codes.

Persistent state includes logs, optional per-test log files, environment variables for timeout and arguments, and temporary network namespaces/logs during `RUN_IN_NETNS`.

## Dependencies and Integration Points

The runner depends on `ktap_helpers.sh`, `timeout`, `stdbuf`, Perl or sed for prefixing, `tr`, `ip netns` for namespace mode, settings files, and test executable/shebang conventions. It is central to kselftest collection execution.

## Risks and Test Signals

Settings are parsed with simple `cut` and `eval`, so malformed settings can affect the runner environment. Command strings are run through `eval`, making sanitized argument variables important. Namespace mode requires manual counter reconciliation because results happen in subshells. Pass signals are correctly prefixed logs, timeout annotations, and result lines matching child exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest/runner.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_deps.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_deps.sh

## Purpose

`kselftest_deps.sh` checks build-time library dependencies for kselftests. It parses selftest Makefiles for static and dynamic `LDLIBS` patterns, compiles a trivial C program with each library set, reports pass/fail dependencies, and can print a filtered target list.

## Important APIs, Types, and Functions

The script accepts `[-p] <compiler> [test_name]`. It uses `grep`, `awk`, `sed`, `find`, temporary files, arrays for pass/fail targets/libs, and the provided compiler. Major functions are `usage()`, `main()`, `all_tests()`, `l1_test()` through `l5_test()`, `check_libs()`, and `print_results()`.

## Control Flow and State

`main()` requires execution from the top-level `tools/testing/selftests` directory, parses `-p`, creates a trivial C source, reads top-level `TARGETS`, builds filtered Makefile lists for five LDLIBS patterns, optionally restricts to one test, runs dependency checks, and prints totals. `check_libs()` compiles the trivial program with each library token or set, records failures, removes failed targets from the suggested target list, and records unique pass/fail target and library summaries.

State is held in temp source/object/bin files and temp pass/fail logs removed by traps. It does not modify source files.

## Dependencies and Integration Points

It depends on bash, coreutils, grep/sed/awk/find, and a native or cross compiler. It integrates with the selftests top-level Makefile and per-test Makefile conventions for `LDLIBS`, `VAR_LDLIBS`, pkg-config fallbacks, and `IOURING_EXTRA_LIBS`.

## Risks and Test Signals

Parsing Makefiles with grep can miss complex make expressions or split libraries incorrectly. The script installs multiple `trap ... EXIT` handlers sequentially, so later traps replace earlier ones and some temp files may not be cleaned. `shift` inside getopts handling is unusual and can affect argument parsing. Pass signals are compile success for required libraries and an accurate suggested target list when `-p` is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_deps.sh -->
