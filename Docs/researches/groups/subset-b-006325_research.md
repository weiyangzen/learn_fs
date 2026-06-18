# subset-b-006325 research

This grouped report covers the requested source files in manifest order. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy.c -->
# sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy.c

## Purpose
`mdpy.c` is a sample Linux kernel mediated-device driver that exposes an emulated VFIO PCI display adapter. It creates `mdpy` mdev types for VGA, XGA, and HD framebuffer sizes and presents a simple mmap-capable display memory BAR to userspace VMMs.

## APIs, Types, And Functions
Important state is held in `struct mdev_state`: embedded `struct vfio_device`, virtual PCI config space, BAR mask, framebuffer memory, selected `mdpy_type`, and an `ops_lock`. The `mdpy_type` table defines sysfs mdev types and DRM formats. Core functions are `mdpy_create_config_space()`, `mdev_access()`, `mdpy_read()`, `mdpy_write()`, `mdpy_mmap()`, `mdpy_ioctl()`, and VFIO callbacks in `mdpy_dev_ops`. Module setup uses `alloc_chrdev_region()`, `mdev_register_driver()`, `class_register()`, `device_register()`, and `mdev_register_parent()`.

## Control Flow
Module init creates a parent device and registers mdev types. `mdpy_probe()` allocates a VFIO device and registers an emulated IOMMU-backed VFIO group device. Device init allocates config space and a `vmalloc_user()` framebuffer, initializes a gray gradient, and emits PCI config fields plus a vendor capability containing format, width, and height. VFIO read/write dispatch breaks accesses into aligned 4/2/1 byte chunks and routes them through `mdev_access()`. IOCTLs answer VFIO device, region, IRQ, reset, and graphics-plane queries.

## State And Persistence
All device state is volatile kernel memory. Config writes persist only in `vconfig`; framebuffer writes persist only until reset or device release. There is no disk persistence, migration stream, or external backing store. `ops_lock` serializes config and BAR accesses.

## Dependencies And Integration Points
The file depends on VFIO, mdev, PCI config constants, IOMMU emulation helpers, sysfs attribute groups, DRM fourcc, and local `mdpy-defs.h`. It integrates with QEMU or another VFIO consumer via VFIO PCI regions and the `VFIO_DEVICE_QUERY_GFX_PLANE` API.

## Risks And Test Signals
This is a sample driver, not hardware-backed production code. Risk areas include unchecked guest-visible semantics, small config space, no IRQ support, and simple BAR bounds handling. Useful signals are successful module load/unload, creation of mdev instances under sysfs, VFIO region queries, framebuffer mmap/read/write behavior, reset returning the gradient, and userspace display consumers correctly interpreting the graphics plane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mdpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mtty.c -->
# sources/distributed-fs/ceph-client/samples/vfio-mdev/mtty.c

## Purpose
`mtty.c` is a sample mediated VFIO PCI serial device driver. It emulates one- or two-port 16550-compatible UART devices over mdev, including guest-visible PCI config/BAR access, INTx/MSI eventfd signaling, and VFIO migration state transfer.

## APIs, Types, And Functions
Key types are `struct serial_port`, `struct rxtx`, `struct mtty_data`, `struct mtty_migration_file`, and `struct mdev_state`. The driver exposes two mdev types via `mtty_types`. Major functions include PCI setup (`mtty_create_config_space()`), config/BAR emulation (`handle_pci_cfg_write()`, `handle_bar_write()`, `handle_bar_read()`, `mdev_access()`), migration (`mtty_set_state()`, `mtty_step_state()`, `mtty_save_device_data()`, `mtty_resume_device_data()`), IRQ wiring (`mtty_set_irqs()`), and VFIO callbacks in `mtty_dev_ops`.

## Control Flow
Module init registers a char device, mdev driver, class, parent device, and mdev parent. Probe allocates a VFIO emulated device. Init reserves available UART ports atomically, initializes locks and config space, and advertises VFIO migration/logging callbacks. Guest reads/writes enter VFIO read/write methods, are split into aligned chunks, and then decode region index from the high VFIO offset bits. UART register writes update FIFO, divisor, line control, modem control, and interrupt conditions; reads synthesize RX/IIR/LSR/MSR values.

## State And Persistence
Runtime state is in memory: virtual PCI config, per-port UART registers, FIFO contents, eventfd contexts, migration state, and migration anon-inode files. Migration serializes `mtty_data` with magic/version/port count and per-port `serial_port` snapshots; resume validates the header before loading port state. There is no storage persistence.

## Dependencies And Integration Points
The file depends on VFIO/mdev, eventfd, anon inodes, Linux serial register definitions, PCI config constants, iommufd emulation helpers, and kernel synchronization primitives. It integrates with VFIO userspace through PCI regions, `VFIO_DEVICE_SET_IRQS`, and VFIO migration state-machine callbacks.

## Risks And Test Signals
Risk is concentrated in emulated device semantics, lock ordering between `state_mutex` and `reset_mutex`, eventfd lifetime, and migration file disabling. The sample intentionally has simplified dirty logging. Test signals include mdev creation capacity accounting, one- and two-port BAR behavior, interrupt trigger/mask/unmask paths, VFIO reset during migration, save/resume validation, and module unload after active work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfio-mdev/mtty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/Makefile -->
# sources/distributed-fs/ceph-client/samples/vfs/Makefile

## Purpose
This kbuild fragment declares VFS userspace sample programs: `test-fsmount`, `test-statx`, `mountinfo`, and `test-list-all-mounts`.

## APIs, Types, And Functions
It uses `userprogs-always-y` to always build the listed user programs when samples are enabled. `userccflags` adds include paths for `tools/testing/selftests/` and generated UAPI headers under `usr/include`.

## Control Flow
There is no runtime control flow. During kbuild, the samples build system consumes these variables, compiles each `.c` source into a user program, and applies the specified include directories.

## State And Persistence
No state is stored. Build outputs are produced by the surrounding kbuild machinery, not by this file directly.

## Dependencies And Integration Points
The file integrates with kernel sample kbuild rules and the local VFS sample sources. It depends on generated UAPI headers being available for recent syscalls and constants.

## Risks And Test Signals
The main risk is include-path drift when selftest or generated header locations change. Test signals are successful `make samples/vfs/` builds and all four declared binaries appearing in the sample output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/mountinfo.c -->
# sources/distributed-fs/ceph-client/samples/vfs/mountinfo.c

## Purpose
`mountinfo.c` demonstrates how pidfds, namespace file descriptors, `listmount()`, and `statmount()` can reproduce `/proc/self/mountinfo`-style output, optionally for another PID and recursively across child mount namespaces.

## APIs, Types, And Functions
Important wrappers are `statmount()` and `listmount()`, which build `struct mnt_id_req` and invoke raw syscalls. Formatting helpers are `show_mnt_attrs()`, `show_propagation()`, and `show_sb_flags()`. `dump_mountinfo()` prints one mount; `dump_mounts()` paginates mount IDs; `main()` parses `-e`, `-p`, and `-r` options and opens namespace fds.

## Control Flow
The program opens a pidfd for the selected PID, gets its mount namespace fd through `PIDFD_GET_MNT_NAMESPACE`, reads namespace info with `NS_MNT_GET_INFO`, and lists all mounts using repeated `listmount(LSMT_ROOT, ..., last_mnt_id)`. Each mount ID is passed to `statmount()` with a mask requesting basic mount/superblock fields and strings, then printed in mountinfo order. Recursive mode advances through mount namespaces with `NS_MNT_GET_NEXT`.

## State And Persistence
State is process-local: selected PID, namespace fd, current namespace ID, pagination cursor, and stack-allocated `statmount` buffers. It does not mutate mounts or persist data.

## Dependencies And Integration Points
It depends on `samples-vfs.h`, raw syscall numbers for `statmount`/`listmount`/`pidfd_open`, namespace ioctls, and recent kernel support. It integrates with `/proc`-like mount diagnostics without reading `/proc/self/mountinfo`.

## Risks And Test Signals
Risks include syscall availability, fixed 4096-byte `statmount` buffer overflow responses, and assuming returned string offsets are valid when mask bits are set. Test signals include output matching `/proc/<pid>/mountinfo`, extended `-e` IDs being present, recursive namespace traversal stopping cleanly at `ENOENT`, and errors on older kernels being reported through `perror()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/mountinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/samples-vfs.h -->
# sources/distributed-fs/ceph-client/samples/vfs/samples-vfs.h

## Purpose
`samples-vfs.h` provides compatibility definitions for VFS sample programs that need new mount namespace, `statmount()`, `listmount()`, and mount attribute UAPI declarations before libc or installed headers may expose them.

## APIs, Types, And Functions
The header defines `die_errno()`, `struct statmount`, `struct mnt_id_req`, and `struct mnt_ns_info`. It supplies syscall numbers, request sizes, namespace ioctl numbers, mount ID constants, `STATMOUNT_*` masks, `STATX_MNT_ID_UNIQUE`, `MOUNT_ATTR_*`, and selected `MS_*` flags when absent.

## Control Flow
There is no executable control flow. Including programs use the structures to build raw syscall/ioctl requests and interpret returned variable-length strings through offsets into `statmount.str[]`.

## State And Persistence
No persistent state exists. Structure layout is ABI-significant for user/kernel exchange, particularly versioned `mnt_id_req` sizes and trailing string offsets.

## Dependencies And Integration Points
It depends on `<linux/types.h>`, `<sys/ioctl.h>`, and syscall/ioctl conventions. It is shared by `mountinfo.c` and `test-list-all-mounts.c` and bridges samples to evolving kernel UAPI.

## Risks And Test Signals
The main risk is layout or constant drift relative to current UAPI headers. Test signals include successful compilation against both old and new userspace headers and working `statmount`/`listmount` samples on kernels implementing these syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/samples-vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/test-fsmount.c -->
# sources/distributed-fs/ceph-client/samples/vfs/test-fsmount.c

## Purpose
`test-fsmount.c` demonstrates the fd-based mount API by creating an AFS superblock with `fsopen()`/`fsconfig()`, converting it to a detached mount with `fsmount()`, and attaching it at `/mnt` with `move_mount()`.

## APIs, Types, And Functions
It defines raw syscall wrappers for `fsopen`, `fsmount`, `fsconfig`, and `move_mount`. `check_messages()` drains fs context diagnostic messages, `mount_error()` reports them before exiting, and `E_fsconfig` wraps configuration failures.

## Control Flow
`main()` opens an AFS fs context, sets the `source` string to a public AFS cell, issues `FSCONFIG_CMD_CREATE`, calls `fsmount()` with read-only mount attributes, closes the context fd, and moves the detached mount to `/mnt` using `MOVE_MOUNT_F_EMPTY_PATH`.

## State And Persistence
The program creates kernel fs-context and mount file descriptors. It can persistently change the system mount table by attaching at `/mnt`; cleanup is external.

## Dependencies And Integration Points
It depends on recent fd-based mount syscalls, AFS filesystem support, network reachability for the sample source, privileges to mount, and `/mnt` availability. It integrates with the VFS mount API and fs-context diagnostic stream.

## Risks And Test Signals
Risks include requiring elevated privileges, mutating `/mnt`, relying on public AFS availability, and failing on kernels without syscall numbers. Test signals are successful mount attachment, diagnostic messages for invalid fsconfig/fsmount, and visible read-only AFS mount in mountinfo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/test-fsmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/test-list-all-mounts.c -->
# sources/distributed-fs/ceph-client/samples/vfs/test-list-all-mounts.c

## Purpose
`test-list-all-mounts.c` is a diagnostic sample that lists every mount in the current mount namespace and then walks subsequent mount namespaces using namespace ioctls.

## APIs, Types, And Functions
It wraps `statmount()` in `__statmount()` and `sys_statmount()`, with buffer growth on `EOVERFLOW`. `sys_listmount()` wraps `listmount()`. `main()` uses `sys_pidfd_open()`, `PIDFD_GET_MNT_NAMESPACE`, `NS_MNT_GET_INFO`, and `NS_MNT_GET_NEXT`.

## Control Flow
The program obtains a pidfd for itself, converts it to a mount namespace fd, fetches namespace metadata, then repeatedly calls `listmount()` in batches of ten IDs. For each ID it calls `sys_statmount()` with masks for superblock, mount basics, roots, points, options, filesystem type, namespace ID, and idmaps. When a namespace is exhausted it advances to the next namespace until `ENOENT`.

## State And Persistence
State is local to the process: list buffer, `last_mnt_id`, namespace fd, and dynamically allocated `statmount` buffers. It does not modify mounts or namespaces.

## Dependencies And Integration Points
It depends on `samples-vfs.h`, pidfd selftest helper headers, recent mount syscalls/ioctls, and idmap fields in `statmount`. It integrates with namespace enumeration from nsfs.

## Risks And Test Signals
Risks include older kernels returning `ENOSYS`/`EINVAL`, large outputs, and `statmount()` failures for individual mounts. Test signals include matching mount counts, clean namespace completion messages, idmap lines when masks are present, and graceful skip of mounts that fail `statmount()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/test-list-all-mounts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/test-statx.c -->
# sources/distributed-fs/ceph-client/samples/vfs/test-statx.c

## Purpose
`test-statx.c` exercises the `statx()` syscall and prints returned file metadata in a format close to `/bin/stat`, with optional raw hex dumping.

## APIs, Types, And Functions
It defines a raw `statx()` wrapper, `print_time()` for timestamp formatting, `dump_statx()` for structured metadata, and `dump_hex()` for raw buffer inspection. Command flags are `-F`, `-D`, `-L`, `-O`, `-A`, and `-R`.

## Control Flow
`main()` starts with `STATX_BASIC_STATS | STATX_BTIME` and `AT_SYMLINK_NOFOLLOW`. Options adjust sync behavior, symlink following, automount suppression, basic-stat request masking, and raw output. Each remaining argv path is passed to `statx(AT_FDCWD, ...)`, then optionally dumped as hex before formatted fields are printed.

## State And Persistence
State is transient per invocation: flags, mask, raw flag, and `struct statx`. The program is read-only and does not persist data.

## Dependencies And Integration Points
It depends on Linux `statx` UAPI, raw syscall numbers, libc time formatting, and header workarounds for glibc/kernel macro conflicts. It integrates with filesystem metadata and attribute-mask validation.

## Risks And Test Signals
Risks include unsupported `statx`, filesystem-specific missing mask bits, and local timezone formatting differences. Test signals include expected values for regular files, symlinks with and without `-L`, raw dumps matching structure size, and proper errors for inaccessible paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/vfs/test-statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watch_queue/Makefile -->
# sources/distributed-fs/ceph-client/samples/watch_queue/Makefile

## Purpose
This kbuild fragment declares the `watch_test` userspace sample for the watch queue API.

## APIs, Types, And Functions
It uses `userprogs-always-y += watch_test` and adds `usr/include` to `userccflags` so generated UAPI headers are visible.

## Control Flow
During sample builds, kbuild compiles `watch_test.c` as a userspace program whenever this sample directory is included.

## State And Persistence
No runtime state is held by the Makefile. It only contributes build variables.

## Dependencies And Integration Points
It integrates with kernel samples kbuild and depends on generated watch queue/keyctl UAPI headers.

## Risks And Test Signals
Risks are limited to header include path drift or omitted generated headers. Test signal is a successful `watch_test` binary build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watch_queue/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watch_queue/watch_test.c -->
# sources/distributed-fs/ceph-client/samples/watch_queue/watch_test.c

## Purpose
`watch_test.c` demonstrates the watch queue notification API by watching keyring change notifications through an `O_NOTIFICATION_PIPE`.

## APIs, Types, And Functions
Important APIs are `pipe2(O_NOTIFICATION_PIPE)`, `IOC_WATCH_QUEUE_SET_SIZE`, `IOC_WATCH_QUEUE_SET_FILTER`, and `keyctl(KEYCTL_WATCH_KEY, ...)`. `consumer()` reads and decodes notification records, while `saw_key_change()` formats `struct key_notification` messages.

## Control Flow
`main()` creates a notification pipe, sizes the watch queue, installs a filter for key notifications, attaches watches for the session and user keyrings, then calls `consumer()`. The consumer reads batches, iterates variable-length `watch_notification` records, validates record lengths, and switches on meta versus key notification types.

## State And Persistence
State is limited to pipe fds, installed watches, filter structure, and the read buffer. Watches persist only while the process/fds remain alive.

## Dependencies And Integration Points
It depends on watch queue UAPI, keyctl syscall support, keyring constants, and the kernel key retention service. It integrates with keyring update events and watch meta notifications for removal/loss.

## Risks And Test Signals
Risks include unsupported watch queues, permission failures for key watches, malformed/short records, and fixed buffer assumptions. Test signals are printed notifications after keyring operations, meta loss/removal handling, and clean read-loop behavior when the pipe closes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watch_queue/watch_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watchdog/Makefile -->
# sources/distributed-fs/ceph-client/samples/watchdog/Makefile

## Purpose
This kbuild fragment declares the `watchdog-simple` userspace watchdog sample.

## APIs, Types, And Functions
It uses `userprogs-always-y += watchdog-simple` to request unconditional sample build.

## Control Flow
There is no runtime flow. Kbuild consumes this variable to compile `watchdog-simple.c`.

## State And Persistence
No state is held here beyond build metadata.

## Dependencies And Integration Points
It integrates with the kernel samples userspace-program build path and the watchdog sample source.

## Risks And Test Signals
The only meaningful risk is the source not compiling under sample kbuild. The test signal is the presence of the built `watchdog-simple` binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watchdog/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watchdog/watchdog-simple.c -->
# sources/distributed-fs/ceph-client/samples/watchdog/watchdog-simple.c

## Purpose
`watchdog-simple.c` is a minimal userspace program that opens `/dev/watchdog` and periodically writes a byte to keep the watchdog from firing.

## APIs, Types, And Functions
The single `main()` uses `open()`, `write()`, `sleep()`, `close()`, `perror()`, and standard exit codes. It opens the watchdog device write-only.

## Control Flow
After opening `/dev/watchdog`, the program loops forever writing one NUL byte and sleeping ten seconds. If a write returns anything other than one byte, it breaks, closes the fd, and returns `-1`.

## State And Persistence
State is the watchdog fd and last write result. Opening and writing may arm or pet a hardware/software watchdog; device behavior may persist outside the process depending on driver configuration.

## Dependencies And Integration Points
It depends on a watchdog device node and watchdog driver semantics. It integrates with the Linux watchdog character device ABI.

## Risks And Test Signals
Running it on real hardware may keep or arm a system reset watchdog, and abrupt exit behavior depends on the driver magic-close policy. Test signals include successful open, regular writes visible via tracing, and expected error if `/dev/watchdog` is absent or permission denied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/watchdog/watchdog-simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/Makefile -->
# sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/Makefile

## Purpose
This kbuild fragment declares the `wq_stall` kernel module sample.

## APIs, Types, And Functions
It uses `obj-m += wq_stall.o`, making `wq_stall.c` build as an external-style loadable module under the kernel samples tree.

## Control Flow
Kbuild compiles and links `wq_stall.o` into `wq_stall.ko` when this sample directory is built.

## State And Persistence
No runtime state exists in the Makefile. Module artifacts are produced by kbuild.

## Dependencies And Integration Points
It integrates with kernel module build rules and the workqueue stall detector sample.

## Risks And Test Signals
Risks are limited to module build compatibility. Test signal is successful `wq_stall.ko` creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/wq_stall.c -->
# sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/wq_stall.c

## Purpose
`wq_stall.c` is a deliberate fault-injection sample module for validating the workqueue stall detector. It hides a worker from workqueue concurrency accounting so a queued item remains stuck long enough to trigger watchdog diagnostics.

## APIs, Types, And Functions
It defines a wait queue, `atomic_t wake_condition`, and two `work_struct`s. `stall_work1_fn()` triggers the stall; `stall_work2_fn()` reports when the second item eventually runs. `wq_stall_init()` schedules the first work item, and `wq_stall_exit()` wakes and flushes both work items.

## Control Flow
The first work item queues the second item on the same per-CPU pool, clears `PF_WQ_WORKER`, then sleeps in `wait_event_idle()`. Because the worker no longer calls `wq_worker_sleeping()`, the pool can believe a worker is still running and may not start another, leaving the second item pending until the watchdog reports a lockup. Module exit restores progress by setting the wake condition and flushing work.

## State And Persistence
State is kernel-memory-only: work items, wait queue, atomic wake condition, and temporary mutation of `current->flags`. No persistence exists after module unload.

## Dependencies And Integration Points
It depends on workqueue internals, scheduler task flags, wait queues, and module lifecycle APIs. It integrates with workqueue watchdog diagnostics and kernel logs.

## Risks And Test Signals
This module intentionally creates a kernel stall and should only run in test environments. Risks include noisy lockup reports or delayed unload. Test signals are expected `BUG: workqueue lockup` diagnostics after roughly 30-60 seconds, second work item running after unload wakeup, and clean `flush_work()` completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/workqueue/stall_detector/wq_stall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/Lindent -->
# sources/distributed-fs/ceph-client/scripts/Lindent

## Purpose
`Lindent` is a shell wrapper around GNU `indent` that applies Linux-kernel-style formatting options.

## APIs, Types, And Functions
It defines a `PARAM` string of indent options, parses `indent --version`, extracts major/minor/patch fields, conditionally appends `-il0` for indent versions at least 2.2.10, and finally executes `indent $PARAM "$@"`.

## Control Flow
The script exits if no version is detected. It then compares version components using shell arithmetic and runs `indent` with calculated options against all passed files.

## State And Persistence
It mutates files passed to `indent`; no separate state is stored. Formatting changes are persistent in the working tree.

## Dependencies And Integration Points
It depends on GNU indent output format and POSIX shell utilities. It integrates with kernel developer workflows for mechanical source formatting.

## Risks And Test Signals
Risks include non-GNU indent formats, unquoted numeric comparisons on unexpected versions, and broad in-place formatting churn. Test signals are a zero exit code on valid C files and expected kernel indentation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/Lindent -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/Makefile -->
# sources/distributed-fs/ceph-client/scripts/Makefile

## Purpose
`scripts/Makefile` defines host tools, generated targets, subdirectories, and build flags for Linux kernel build helper programs.

## APIs, Types, And Functions
It uses kbuild variables such as `hostprogs-always-*`, `hostprogs`, `targets`, `subdir-*`, object lists, `HOSTCFLAGS_*`, and `HOSTLDLIBS_*`. It defines a `filechk_rust_target` rule to generate `target.json`.

## Control Flow
Kbuild evaluates configuration-dependent host programs: `kallsyms`, `recordmcount`, `sorttable`, `asn1_compiler`, `sign-file`, Rust doctest helpers, and tracepoint tools. It adds include paths and libraries as needed, generates Rust target data on x86 when Rust is enabled, and descends into plugin, genksyms, SELinux, IPE, and core script subdirs.

## State And Persistence
Generated host binaries, `target.json`, and `module.lds` are build artifacts. No runtime state is held by the Makefile.

## Dependencies And Integration Points
It integrates deeply with kbuild, host compiler/linker rules, libcrypto via `pkg-config`, Rust host tool support, ORC unwind metadata, and architecture-specific include paths.

## Risks And Test Signals
Risks include stale config gating, missing host libraries, incorrect architecture include selection, or Rust target regeneration drift. Test signals are successful kernel host-tool builds under relevant configs and correct incremental rebuilds when dependencies change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/as-version.sh -->
# sources/distributed-fs/ceph-client/scripts/as-version.sh

## Purpose
`as-version.sh` identifies the assembler backend and prints a canonical numeric version while enforcing the kernel minimum binutils version.

## APIs, Types, And Functions
Functions are `get_canonical_version()` and `check_integrated_as()`. The script executes the compiler/assembler command with `-Wa,--version -c -x assembler-with-cpp /dev/null -o /dev/null`, calls `scripts/min-tool-version.sh`, and prints `GNU <canonical>` or `LLVM 0`.

## Control Flow
If `-fintegrated-as` is present, the script reports LLVM integrated assembler and exits without a version check. Otherwise it captures the first assembler version line, recognizes GNU assembler, trims distribution suffixes, converts versions to `major*10000 + minor*100 + patch`, compares against the minimum, and exits with diagnostics if too old.

## State And Persistence
No state is persisted. Output is consumed by kbuild.

## Dependencies And Integration Points
It depends on shell, compiler assembler passthrough behavior, GNU assembler version output, and `min-tool-version.sh`. It integrates with compiler capability checks.

## Risks And Test Signals
Risks include changed version banner formats or unusual wrapper arguments. Test signals are expected `GNU 2xxxx` output for binutils, `LLVM 0` with `-fintegrated-as`, and failure on intentionally too-old versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/as-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/asn1_compiler.c -->
# sources/distributed-fs/ceph-client/scripts/asn1_compiler.c

## Purpose
`asn1_compiler.c` is a host build tool that parses a simplified ASN.1 grammar file and emits C/header files containing Linux ASN.1 BER decoder bytecode and action prototypes.

## APIs, Types, And Functions
Major types are `struct token`, `struct action`, `struct type`, and `struct element`. The pipeline is `tokenise()`, `build_type_list()`, `parse()`, `parse_type()`, `parse_compound()`, and `render()`. Rendering uses `render_element()`, `render_out_of_line_list()`, `render_opcode()`, and `render_more()`. It consumes `linux/asn1_ber_bytecode.h` constants.

## Control Flow
`main()` parses `-v`/`-d`, reads the grammar, derives a grammar name from the filename, tokenizes comments/directives/names/numbers/braces/actions, builds a sorted type index, parses each type assignment into an element tree, optionally dumps debug structure, opens output files, and renders two passes. Pass one computes bytecode offsets; pass two writes machine bytecode, action enum/table, header declarations, and `struct asn1_decoder`.

## State And Persistence
State is heap-allocated token/type/element/action lists. Output persistence is the generated `.c` and `.h` files. Actions are de-duplicated and sorted by name before indexed.

## Dependencies And Integration Points
It integrates with kbuild ASN.1 grammar rules, kernel ASN.1 decoder bytecode, and generated headers included by consumers. It supports tags, CHOICE, SEQUENCE, SEQUENCE OF, SET OF, ANY, optional/default elements, actions, and type references.

## Risks And Test Signals
Risks include intentionally limited grammar support, explicit failure for SET rendering, fixed token allocation estimate, strict formatting expectations, and generated-code ABI drift. Test signals are successful generation for in-tree `.asn1` grammars, stable bytecode output, action prototypes matching parser callbacks, and failure on undefined types or unsupported SET.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/asn1_compiler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/atomic-tbl.sh -->
# sources/distributed-fs/ceph-client/scripts/atomic/atomic-tbl.sh

## Purpose
`atomic-tbl.sh` is a shared shell library for scripts that generate Linux atomic operation headers from `atomics.tbl`.

## APIs, Types, And Functions
It provides metadata predicates (`meta_has_ret`, acquire/release/relaxed checks, implicit relaxed checks), template discovery (`find_template`, `find_fallback_template`, `find_kerneldoc_template`), type/argument helpers (`gen_ret_type`, `gen_param_type`, `gen_params`, `gen_args`), kerneldoc generation, and prototype variant expansion (`gen_proto*`).

## Control Flow
Generator scripts source this file, then feed table rows into `gen_proto()`. The metadata string expands into fetch, return, acquire, release, relaxed, and full-order variants; concrete `gen_proto_order_variant()` is supplied by each generator.

## State And Persistence
It uses shell locals and environment variable `ATOMICDIR`. It writes generated text to stdout through caller-provided functions but persists nothing itself.

## Dependencies And Integration Points
It depends on POSIX shell and sourced templates under `scripts/atomic/fallbacks` and `kerneldoc`. It integrates all atomic header generators around a common metadata vocabulary.

## Risks And Test Signals
Risks include shell word-splitting in table arguments, missing templates, and mismatched metadata semantics. Test signals are regenerated atomic headers matching checked-in output and complete variants for every `atomics.tbl` row.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/atomic-tbl.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-fallback.sh -->
# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-fallback.sh

## Purpose
`gen-atomic-fallback.sh` generates `linux/atomic/atomic-arch-fallback.h`, providing raw atomic fallbacks and compile-time failures when architectures omit required primitives.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and implements `gen_template_fallback()`, `gen_order_fallback()`, `gen_proto_fallback()`, `gen_proto_order_variant()`, and special fallback emitters for `xchg`, `cmpxchg`, `try_cmpxchg`, local cmpxchg, and sync cmpxchg.

## Control Flow
The script prints header guards and helper includes, emits exchange/cmpxchg fallback macros, processes `atomics.tbl` rows for `atomic`/`int`, includes generic atomic64 when configured, processes rows for `atomic64`/`s64`, and closes the header. Each variant prefers `arch_*`, then relaxed/full-order fallbacks when legal, then template-generated fallback or an error.

## State And Persistence
State is shell-local and stdout text. Persistence occurs when `gen-atomics.sh` redirects output to the include tree.

## Dependencies And Integration Points
It depends on `atomics.tbl`, fallback templates, kerneldoc templates, and kernel macros such as `__atomic_op_acquire/release/fence`. It integrates architecture atomic definitions with generic kernel APIs.

## Risks And Test Signals
Risks include generating invalid fallback ordering, missing template coverage, and differences between macro and function arch definitions. Test signals are successful regenerated header compilation across architectures and expected errors when mandatory raw ops are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-fallback.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-instrumented.sh -->
# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-instrumented.sh

## Purpose
`gen-atomic-instrumented.sh` generates `linux/atomic/atomic-instrumented.h`, wrapping raw atomic operations with instrumentation hooks for KASAN/KCSAN-style checking.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and defines `gen_param_check()`, `gen_params_checks()`, `gen_proto_order_variant()`, and `gen_xchg()`. It emits calls such as `instrument_atomic_read()`, `instrument_atomic_write()`, `instrument_atomic_read_write()`, `instrument_read_write()`, `kcsan_release()`, and `kcsan_mb()`.

## Control Flow
The script prints header scaffolding, generates instrumented wrappers for `atomic`, `atomic64`, and `atomic_long` rows from `atomics.tbl`, then emits macro wrappers for `xchg`, `cmpxchg`, `try_cmpxchg`, local cmpxchg, and sync cmpxchg variants across memory-order suffixes.

## State And Persistence
It has no persistent state beyond generated stdout. The generated header becomes persistent when redirected by the orchestrator.

## Dependencies And Integration Points
It depends on atomic metadata helpers, raw atomic fallback headers, `linux/instrumented.h`, and KCSAN memory barrier conventions. It integrates sanitizers with normal atomic APIs while leaving raw APIs for noinstr contexts.

## Risks And Test Signals
Risks include wrong read/write classification for pointer parameters, missing ordering barriers, and macro argument evaluation mistakes. Test signals are successful sanitizer builds, generated wrappers invoking raw operations once, and KCSAN reports reflecting atomic accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-instrumented.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-long.sh -->
# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-long.sh

## Purpose
`gen-atomic-long.sh` generates `linux/atomic/atomic-long.h`, mapping `atomic_long_*` raw operations to either `atomic64_*` or `atomic_*` depending on `CONFIG_64BIT`.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and implements `gen_cast()`, `gen_args_cast()`, and `gen_proto_order_variant()`. It also emits `atomic_long_t`, `ATOMIC_LONG_INIT`, and conditional read aliases.

## Control Flow
The script prints header guards, typedefs `atomic_long_t` to `atomic64_t` on 64-bit or `atomic_t` otherwise, processes every `atomics.tbl` row, and emits raw `atomic_long` inline wrappers that cast pointer arguments to the correct underlying atomic type.

## State And Persistence
No state is persisted except generated stdout redirected by callers.

## Dependencies And Integration Points
It depends on generated raw atomic/atomic64 APIs, architecture type definitions, and `CONFIG_64BIT`. It integrates word-sized atomic operations with generic atomic code.

## Risks And Test Signals
Risks include incorrect pointer casts, mismatch between `long` width and atomic backend, and missing conditional-read aliases. Test signals include correct preprocessed output on 32-bit and 64-bit builds and passing atomic API compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-long.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomics.sh -->
# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomics.sh

## Purpose
`gen-atomics.sh` orchestrates regeneration of all generated atomic headers and Rust atomic helper C source.

## APIs, Types, And Functions
It defines `ATOMICDIR`, `ATOMICTBL`, and `LINUXDIR`, then uses a here-document mapping generator scripts to output paths. It invokes each script with `/bin/sh`, redirects to `include/<header>`, computes `sha1sum`, and appends the hash as a comment.

## Control Flow
The script iterates over four rows: instrumented header, atomic-long header, arch fallback header, and Rust helper source. Each output is regenerated from `atomics.tbl` and then annotated with its content hash.

## State And Persistence
It writes persistent generated files under `include/linux/atomic/` and `include/../rust/helpers/atomic.c` relative to the kernel tree.

## Dependencies And Integration Points
It depends on the other atomic generator scripts, `atomics.tbl`, `sha1sum`, and expected tree layout. It integrates with maintainer workflows for checking in regenerated atomic artifacts.

## Risks And Test Signals
Risks include path assumptions, partial regeneration on script failure, and hash churn when generator output changes. Test signals are deterministic regenerated files and matching appended hashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-atomics.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-rust-atomic-helpers.sh -->
# sources/distributed-fs/ceph-client/scripts/atomic/gen-rust-atomic-helpers.sh

## Purpose
`gen-rust-atomic-helpers.sh` generates C helper functions that expose selected Linux atomic APIs to Rust code.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and implements `gen_proto_order_variant()` to emit `__rust_helper` functions named `rust_helper_<atomic operation>()`.

## Control Flow
The script prints a generated-file header and includes `linux/atomic.h`, then processes `atomics.tbl` rows for `atomic`/`int` and `atomic64`/`s64`. Each generated helper calls the corresponding C atomic function and returns when the operation metadata requires a value.

## State And Persistence
No state is kept beyond generated stdout. The generated `rust/helpers/atomic.c` is persisted by `gen-atomics.sh`.

## Dependencies And Integration Points
It depends on atomic metadata helpers, Rust helper macro conventions, and the kernel Rust support layer. It integrates C atomic operations into Rust bindings without reimplementing atomic semantics.

## Risks And Test Signals
Risks include exposing operations Rust should not call, mismatched return types, and missing new atomic variants. Test signals are successful Rust-enabled kernel builds and regenerated helper source matching `atomics.tbl`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/atomic/gen-rust-atomic-helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/basic/Makefile -->
# sources/distributed-fs/ceph-client/scripts/basic/Makefile

## Purpose
`scripts/basic/Makefile` builds the essential `fixdep` host tool and defines early generated-file rules needed by the kernel build.

## APIs, Types, And Functions
It uses `hostprogs-always-y += fixdep`, defines `gen-randstruct-seed`, and creates rules for `randstruct.seed` and `include/generated/integer-wrap.h`.

## Control Flow
Kbuild always builds `fixdep`. When `CONFIG_RANDSTRUCT` is enabled, it runs `gen-randstruct-seed.sh`. When `CONFIG_UBSAN_INTEGER_WRAP` is enabled, it touches `integer-wrap.h` whenever the ignore list changes to force rebuilds.

## State And Persistence
Persistent build artifacts are the `fixdep` host binary, `randstruct.seed`, and generated integer-wrap header timestamp.

## Dependencies And Integration Points
It integrates with the earliest kbuild dependency-generation stage, GCC plugin/randomized layout support, and UBSAN integer-wrap build invalidation.

## Risks And Test Signals
Risks include incorrect early dependency ordering and stale generated headers. Test signals are successful clean builds, `fixdep` availability before normal dependency processing, and rebuilds when randomization or integer-wrap inputs change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/basic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/basic/fixdep.c -->
# sources/distributed-fs/ceph-client/scripts/basic/fixdep.c

## Purpose
`fixdep.c` is a host build tool that transforms compiler dependency files into kbuild `.cmd` snippets. It replaces broad dependencies on generated config headers with fine-grained dependencies on individual `include/config/<SYMBOL>` files.

## APIs, Types, And Functions
It uses `struct item` hash tables to de-duplicate files and config symbols. Key functions are `parse_dep_file()`, `parse_config_file()`, `use_config()`, `read_file()`, `is_ignored_file()`, `is_no_parse_file()`, and `in_hashtable()`.

## Control Flow
`main()` expects `<depfile> <target> <cmdline>`, prints `savedcmd_<target>`, reads the depfile, and parses make dependency syntax. The parser skips comments, whitespace, continuation backslashes, targets, and ignored `autoconf.h`. It records the first source file, prints normal dependencies, reads parseable dependency files, scans for standalone `CONFIG_` tokens, normalizes `_MODULE`, and emits wildcard config dependencies plus final make rules.

## State And Persistence
State is process-local hash tables and read buffers. Persistence is stdout redirected by kbuild into `.cmd` files. No source files are modified.

## Dependencies And Integration Points
It depends on POSIX file APIs and `xalloc.h`. It integrates with compiler `-MD` depfiles, kbuild command-line change tracking, module version tooling that parses `source_*`/`deps_*`, Rust dep-info comments, and kconfig’s `include/config/` file tree.

## Risks And Test Signals
Risks include make-syntax edge cases, escaped path handling, false-positive `CONFIG_` mentions, and failure to write full output. Test signals are minimal rebuilds after config changes, valid `.cmd` files, ignored binary Rust artifacts, and parse errors on malformed depfiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/basic/fixdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/bloat-o-meter -->
# sources/distributed-fs/ceph-client/scripts/bloat-o-meter

## Purpose
`bloat-o-meter` compares symbol sizes between two object files and reports growth, shrinkage, additions, removals, and total size delta.

## APIs, Types, And Functions
The Python script uses `argparse`, `os.popen()` to run `nm --size-sort`, and regex cleanup for generated `.NUMBER` suffixes. Main helpers are `getsizes()`, `calc()`, and `print_result()`.

## Control Flow
Arguments select text, data, combined, or categorized output and optional cross-tool prefix. The script reads old and new symbol tables, filters generated symbols, aggregates sizes by normalized name, computes common/new/removed deltas, sorts by delta, and prints summary plus per-symbol table.

## State And Persistence
State is in-memory dictionaries of symbol sizes. It does not write files.

## Dependencies And Integration Points
It depends on Python 3 and `nm` compatible output. It integrates with kernel size-regression review workflows and supports cross builds through an `nm` prefix.

## Risks And Test Signals
Risks include shell command construction with filenames, unexpected `nm` output, and name coalescing hiding distinct static symbols. Test signals are sensible totals for known object pairs and categorized output matching text/data symbol classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/bloat-o-meter -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/bootgraph.pl -->
# sources/distributed-fs/ceph-client/scripts/bootgraph.pl

## Purpose
`bootgraph.pl` converts timestamped `dmesg` initcall/debug output into an SVG timeline showing boot-time function durations and async waits.

## APIs, Types, And Functions
It uses Perl `Getopt::Long`, hashes for start/end/type/PID rows, and direct SVG text/rect printing. It supports `--header` to include `uname -a` and current date.

## Control Flow
The script reads stdin, records `calling <func>+` start lines, `initcall <func> returned` end lines, `async_waiting`/`async_continuing` spans, and stops collecting at memory-protection/freeing markers. It then scales the first-to-last time range to a 1950-pixel graph, assigns rows by PID, filters very short durations, and emits SVG rectangles and labels plus a timeline.

## State And Persistence
State is in memory while processing the log. The persistent artifact is SVG written to stdout by caller redirection.

## Dependencies And Integration Points
It depends on boot logs with `CONFIG_PRINTK_TIME` and `initcall_debug`. It integrates with boot performance analysis tooling.

## Risks And Test Signals
Risks include regex drift with log format changes, division by zero on degenerate logs, and SVG label escaping omissions. Test signals are non-empty SVG for valid dmesg input and an explanatory error/help path when no initcall data is found.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/bootgraph.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/bpf_doc.py -->
# sources/distributed-fs/ceph-client/scripts/bpf_doc.py

## Purpose
`bpf_doc.py` parses `include/uapi/linux/bpf.h` comments and enum/macro definitions to generate BPF helper and syscall documentation in RST, JSON, or C header form.

## APIs, Types, And Functions
Core classes are `APIElement`, `Helper`, `HeaderParser`, `Printer`, `PrinterRST`, `PrinterHelpersRST`, `PrinterSyscallRST`, `PrinterHelpersHeader`, `PrinterHelpersJSON`, and `PrinterSyscallJSON`. Parser methods locate documentation blocks, parse prototypes/descriptions/returns/attributes, parse `enum bpf_cmd`, parse `___BPF_FUNC_MAPPER`, and validate helper ordering/uniqueness.

## Control Flow
The CLI chooses target `helpers` or `syscall` and output format. `HeaderParser.run()` parses syscall docs/enums, helper docs/mapper definitions, validates helper ordering and enum values, then a printer emits the requested output. RST printers include generated license/header/footer material; header output maps kernel types to BPF-program-visible types and emits helper function pointer constants.

## State And Persistence
State is parser lists/sets/dicts of commands, helpers, enum values, and descriptions. Output is stdout; no files are written directly.

## Dependencies And Integration Points
It depends on Python 3, regexes matching `bpf.h` comment formatting, optional git/make for version/date metadata, and known BPF type mappings. It integrates with generated man pages, BPF helper headers, and documentation consistency checks.

## Risks And Test Signals
Risks include strict formatting causing parse stops, stale `known_types` mappings, duplicate helper descriptions, and enum/doc order drift. Test signals are successful `helpers` and `syscall` generation, JSON parseability, helper count matching `___BPF_FUNC_MAPPER`, and failure on undocumented or misordered helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/bpf_doc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/build-version -->
# sources/distributed-fs/ceph-client/scripts/build-version

## Purpose
`build-version` maintains and prints the monotonically increasing kernel build version stored in `.version`.

## APIs, Types, And Functions
It is a short shell script using `cat`, `expr`, redirection, and fallback assignment.

## Control Flow
The script reads `.version`; if it can increment it with `expr`, it uses the incremented value, otherwise it starts at `1`. It writes the new value back to `.version` and prints it.

## State And Persistence
`.version` is the persistent state. Each successful run mutates it.

## Dependencies And Integration Points
It depends on POSIX shell and `expr`. It integrates with kernel build versioning and generated compile metadata.

## Risks And Test Signals
Risks include concurrent invocations racing on `.version`, unwritable working directory, and nonnumeric file content resetting to `1`. Test signals are `.version` incrementing on repeated invocations and stdout matching the stored value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/build-version -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cc-can-link.sh -->
# sources/distributed-fs/ceph-client/scripts/cc-can-link.sh

## Purpose
`cc-can-link.sh` checks whether a compiler command can link a minimal C program without warnings treated as nonfatal.

## APIs, Types, And Functions
The shell script feeds a tiny C program to `$@` with `-Werror`, `-Wl,--fatal-warnings`, `-x c -`, and output `/dev/null`.

## Control Flow
It writes source through a here-document into the provided compiler command. Success or failure is the compiler/linker exit status.

## State And Persistence
No state is stored. Temporary compiler outputs target `/dev/null`.

## Dependencies And Integration Points
It depends on the caller passing a complete compiler command and linker accepting the options. It integrates with kbuild toolchain capability checks.

## Risks And Test Signals
Risks include compilers that do not accept GNU-style flags or wrappers that mishandle stdin. Test signal is exit 0 for a working native/cross linker and nonzero for compile-only or broken link setups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cc-can-link.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cc-version.sh -->
# sources/distributed-fs/ceph-client/scripts/cc-version.sh

## Purpose
`cc-version.sh` identifies the C compiler family and canonical version, enforcing the kernel’s minimum supported GCC or LLVM version.

## APIs, Types, And Functions
Functions are `get_c_compiler_info()` and `get_canonical_version()`. It preprocesses a small snippet to print `GCC` or `Clang` plus version components, then consults `min-tool-version.sh`.

## Control Flow
The script captures the compiler identity using `$@ -E -P -x c -`, maps it to a minimum version category, canonicalizes installed and minimum versions, fails with diagnostics if too old, and prints `<name> <canonical-version>` on success.

## State And Persistence
No state is persisted; stdout is consumed by kbuild.

## Dependencies And Integration Points
It depends on C preprocessor predefined macros, POSIX shell, and `min-tool-version.sh`. It handles multiword compiler commands such as `ccache gcc`.

## Risks And Test Signals
Risks include unknown compiler frontends, nonstandard macro definitions, and unexpected version component formats. Test signals are expected output for GCC/Clang, failure for too-old compilers, and handling of wrapper commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/cc-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-function-names.sh -->
# sources/distributed-fs/ceph-client/scripts/check-function-names.sh

## Purpose
`check-function-names.sh` rejects object files containing function names that conflict with section-name conventions used by `-ffunction-sections`.

## APIs, Types, And Functions
It uses `${NM:-nm}`, `awk`, and `grep -E` to find text/weak symbols named `startup`, `exit`, `split`, `unlikely`, `hot`, or `unknown`, with optional suffix after a dot.

## Control Flow
The script validates it received an existing object file, extracts candidate symbols, prints one error per bad symbol, and exits nonzero if any are found.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
It depends on nm output format and kbuild object-file checking. It integrates with linker script assumptions around text section names.

## Risks And Test Signals
Risks include false positives for intentionally named local functions and missed symbols if nm output changes. Test signals are nonzero exit with clear diagnostics for an object defining `startup()` and zero for normal objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-function-names.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-git -->
# sources/distributed-fs/ceph-client/scripts/check-git

## Purpose
`check-git` verifies that the kernel source tree is a Git repository at its top level.

## APIs, Types, And Functions
It uses `git -C <srctree> rev-parse --verify HEAD` and `git rev-parse --show-cdup`.

## Control Flow
The script derives `srctree` as `scripts/..`, fails if HEAD cannot be verified, and fails if `show-cdup` indicates the command is not at the repository root.

## State And Persistence
No state is stored.

## Dependencies And Integration Points
It depends on Git and a repository checkout. It integrates with build or release steps that require Git metadata.

## Risks And Test Signals
Risks include failure in source archives without `.git` and ambiguous behavior in worktrees/submodules. Test signals are exit 0 at the top of a valid Git tree and exit 1 outside one.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-git -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-sysctl-docs -->
# sources/distributed-fs/ceph-client/scripts/check-sysctl-docs

## Purpose
`check-sysctl-docs` is a gawk script that compares documented sysctl entries against implementation entries registered for a specified sysctl table.

## APIs, Types, And Functions
It uses awk arrays `documented`, `entries`, `file`, `seen`, and helper functions `trimpunct()` and `printentry()`. The caller must pass `-vtable=<name>`.

## Control Flow
Stage one reads the documentation file, treats section titles as documented sysctl names while skipping known non-entry titles, and records tokens. Stage two scans source files for `struct ctl_table`, `.procname`, `UCOUNT_ENTRY`, `register_sysctl*`, `kmemdup`, and `__register_sysctl_table` patterns. It prints each implemented entry and flags documented entries that were not seen.

## State And Persistence
State is awk memory only; output is diagnostics on stdout/stderr. No files are modified.

## Dependencies And Integration Points
It depends on GNU awk features, source formatting conventions, and sysctl registration patterns. It integrates documentation checks with source grep results.

## Risks And Test Signals
Risks include regex brittleness, macro-heavy sysctl definitions being missed, and documentation tokenization false positives. Test signals are documented entries marked as implemented and clear `No implementation for` lines for missing docs/source mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-sysctl-docs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-uapi.sh -->
# sources/distributed-fs/ceph-client/scripts/check-uapi.sh

## Purpose
`check-uapi.sh` checks UAPI header backward compatibility between a base ref or dirty tree and a past Git ref by compiling installed headers and comparing ABI with `abidiff`.

## APIs, Types, And Functions
Key functions include `gen_suppressions()`, `tree_is_dirty()`, `get_file_list()`, `add_to_incompat_list()`, `do_compile()`, `run_make_headers_install()`, `install_headers()`, `check_uapi_files()`, `check_individual_file()`, `compare_abi()`, `check_deps()`, `run()`, and `main()`.

## Control Flow
CLI options choose base/past refs, job count, error log, ambiguity handling, quiet, and verbose modes. The script validates tools and refs, creates a temp dir, generates libabigail suppressions, installs UAPI headers for both refs, diffs the installed trees, then compiles each past-ref header into a debug shared object for both versions and runs `abidiff`. Checks run in bounded parallel background jobs.

## State And Persistence
State lives in a temporary directory containing header installs, compiled `.bin` files, logs, suppressions, and incompatibility lists. The temp dir is removed on exit. Optional error logs persist at the caller-provided path.

## Dependencies And Integration Points
It depends on Git, make `headers_install`, abigail `abidiff` >= 2.4, a C compiler, architecture headers, `usr/include/Makefile`, and libdw for clang. It integrates with UAPI review, CI, and architecture-specific header installation.

## Risks And Test Signals
Risks include long runtime, tool version sensitivity, suppressed changes hiding real ABI breaks, and compile failures from headers that need exclusion. Test signals are success when only additive UAPI changes occur, failure logs for removed/changed ABI, and prerequisite exit code when tools or refs are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check-uapi.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check_extable.sh -->
# sources/distributed-fs/ceph-client/scripts/check_extable.sh

## Purpose
`check_extable.sh` validates that relocations from an object’s `__ex_table` section point only to expected executable sections, helping catch invalid exception table entries.

## APIs, Types, And Functions
It uses `file`, `objdump`, `addr2line`, `grep`, `awk`, and shell functions including `find_section_offset_from_symbol()`, `find_symbol_and_offset_from_reloc()`, `find_alt_replacement_target()`, `handle_alt_replacement_reloc()`, `is_executable_section()`, `handle_suspicious_generic_reloc()`, `diagnose()`, and `check_debug_info()`.

## Control Flow
The script exits early for non-ELF files or objects without `__ex_table`. It extracts relocations from `__ex_table`, filters a whitelist of `.text` and `.fixup`, resolves suspicious relocations to section offsets, special-cases `.altinstr_replacement`, warns for unknown executable sections, errors for non-executable targets, and exits nonzero if an error was found.

## State And Persistence
State is shell variables and diagnostic output. No files are modified.

## Dependencies And Integration Points
It depends on binutils output formats and optional debug info for useful `addr2line` output. It integrates with kernel object validation for exception tables.

## Risks And Test Signals
Risks include regex parsing failures, missing debug info reducing diagnostics, and new legitimate faulting sections requiring whitelist updates. Test signals are exit 0 for normal objects and clear warnings/errors for crafted invalid `__ex_table` relocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/check_extable.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkdeclares.pl -->
# sources/distributed-fs/ceph-client/scripts/checkdeclares.pl

## Purpose
`checkdeclares.pl` scans header files for duplicate forward `struct name;` declarations.

## APIs, Types, And Functions
It uses Perl strict mode, a `usage()` helper, per-file `%declaredstructs` counts, and a regex matching lines that contain only a struct forward declaration.

## Control Flow
The script requires at least one filename, opens each file, counts matching struct declarations, then prints a warning for any struct declared more than once. If no duplicates are found, it prints a clean summary.

## State And Persistence
State is in-memory counts per file and a total duplicate counter. It does not modify files.

## Dependencies And Integration Points
It depends on Perl and simple header formatting. It integrates with manual cleanup checks and complements include duplication scripts.

## Risks And Test Signals
Risks include ignoring macro/ifdef context and missing declarations with attributes or comments. Test signals are warnings for duplicated `struct foo;` lines and clean output for unique declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkdeclares.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checker-valid.sh -->
# sources/distributed-fs/ceph-client/scripts/checker-valid.sh

## Purpose
`checker-valid.sh` verifies that a sparse-like checker binary supports `__typeof_unqual__` without reporting an error.

## APIs, Types, And Functions
It checks command availability, creates a temporary file with `mktemp`, installs a cleanup trap, writes a tiny C snippet, runs the checker command, and uses `awk` to return `1` when no line contains `error` and `0` otherwise.

## Control Flow
The script exits 1 if the checker executable is missing. Otherwise it runs the checker on the temporary C file and prints the awk-derived validity flag.

## State And Persistence
Only a temporary file is created and removed on exit. No persistent state remains.

## Dependencies And Integration Points
It depends on POSIX shell, `mktemp`, `awk`, and the checker command. It integrates with sparse capability detection.

## Risks And Test Signals
Risks include treating any stderr line containing `error` as failure and relying on checker behavior where exit status may not reflect errors. Test signals are output `1` for a valid checker and `0` for a checker that rejects `__typeof_unqual__`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checker-valid.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkincludes.pl -->
# sources/distributed-fs/ceph-client/scripts/checkincludes.pl

## Purpose
`checkincludes.pl` detects duplicate `#include` directives and can optionally remove earlier duplicates in place.

## APIs, Types, And Functions
It uses Perl strict mode, `usage()`, a `-r` option flag, `%includedfiles` counts, and stored `@file_lines`. The include regex matches `<...>` and `"..."` forms.

## Control Flow
Without `-r`, the script counts includes per file and prints duplicate diagnostics. With `-r`, it rewrites each file, suppressing duplicate include lines until only one instance remains, then prints the number removed.

## State And Persistence
In reporting mode, state is memory-only. In remove mode, it persistently rewrites input files.

## Dependencies And Integration Points
It depends on Perl and straightforward preprocessor syntax. It integrates with source cleanup workflows and should be used cautiously around conditional includes.

## Risks And Test Signals
Risks include ignoring macro/ifdef semantics and rewriting files destructively under `-r`. Test signals include duplicate diagnostics in normal mode and reduced include count with a removal summary in `-r` mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/checkincludes.pl -->
