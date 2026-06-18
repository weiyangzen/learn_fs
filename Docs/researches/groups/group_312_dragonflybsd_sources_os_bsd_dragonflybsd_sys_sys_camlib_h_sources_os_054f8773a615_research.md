# Group Research: group_312_dragonflybsd_sources_os_bsd_dragonflybsd_sys_sys_camlib_h_sources_os_054f8773a615

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/camlib.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/camlib.h

Userland CAM library interface for opening CAM devices, issuing CCBs, and encoding/decoding SCSI command buffers.

Key responsibilities:
- Defines `struct cam_device`, carrying user-supplied path/name/unit data, resolved SIM/bus/target/LUN identity, inquiry data, serial number, negotiated bus settings, and device fd.
- Defines the hard-coded transport device path `XPT_DEVICE` as `/dev/xpt0`.
- Declares open helpers by path, pass device, bus-target-lun tuple, or specific device name/unit.
- Declares CCB lifecycle and submission helpers: `cam_getccb`, `cam_freeccb`, `cam_send_ccb`.
- Declares SCSI buffer/CCB format build, encode, decode, and visitor-based argument hooks.

Dependencies:
- Includes CAM core headers `bus/cam/cam.h` and `bus/cam/cam_ccb.h`.
- Uses `MAXPATHLEN`, CAM ID widths, `struct scsi_inquiry_data`, and `__printflike`.

Notable risks:
- This is ABI-facing userland storage tooling surface; struct layout and function signatures must stay compatible with CAM consumers.
- Format-string based SCSI encoding/decoding relies on the undocumented format grammar implemented elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/camlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/caps.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/caps.h

DragonFly system capability restriction header, defining negative process capability bits and user/kernel APIs for applying or checking restrictions.

Key responsibilities:
- Represents 256 capabilities in `__syscaps_t`, with two bits per capability for SELF/EXEC inheritance state.
- Defines restriction application flags: none, self, exec, all, plus extra flags such as in-parent, nullcred, root-test bypass, and wheel bypass.
- Organizes capabilities into 16 groups, including root restrictions, process/sysctl/time/scheduler controls, exec SUID/SGID, credential mutation, jail, network, VFS, and mount restrictions.
- Declares userland `syscap_get()` and `syscap_set()`.
- Declares kernel helpers for exec inheritance, mutation under lock, and privilege checks against credentials or threads.
- Provides `__SYSCAP_ALLSTRINGS` for name tables.

Dependencies:
- Uses `machine/stdint.h`; kernel prototypes depend on `proc`, `thread`, and `ucred`.

Notable risks:
- Capability names are restrictions, not grants, so policy code must treat set bits as denial state.
- Comments state restrictions cannot be downgraded after application, implying OR-only monotonic semantics.
- The string tables need careful synchronization with numeric constants; group 8/9 string ordering appears suspicious relative to defined VFS capability numbers, and `"novfs_ioct"` appears misspelled.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/caps.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ccdvar.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ccdvar.h

Concatenated disk driver ABI and kernel state definitions for DragonFly’s CCD pseudo-disk.

Key responsibilities:
- Defines configuration inputs: `struct ccddevice` for initialization-time configuration and `struct ccd_ioctl` for ioctl-based user configuration.
- Defines CCD modes/flags: swap interleave, uniform interleave, mirroring, and parity.
- Describes component devices through `struct ccdcinfo`, including vnode, cdev, size, skip offset, and path.
- Defines irregular interleave groups in `struct ccdiinfo`.
- Defines pseudo-geometry and full `struct ccd_softc`, including component table, interleave table, devstat stats, disk overlay, raw cdev, mirror picker, and mirror locality blocks.
- Defines `CCDIOCSET` and `CCDIOCCLR` ioctls.

Dependencies:
- Includes `sys/conf.h`, `sys/devicestat.h`, `sys/disk.h`, `sys/diskslice.h`, and `sys/ioccom.h`.
- Uses vnode, cdev, lock, devstat, disk, and disk slice infrastructure.

Notable risks:
- `CCD_MAXNDISKS` allows very large component counts, so allocation and ioctl validation matter.
- User pointers in `ccd_ioctl` (`char **ccio_disks`) require careful copyin handling.
- Interleave and mirror logic depend on accurate component sizes and offset calculations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ccdvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cdefs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cdefs.h

Core compiler, language, visibility, attribute, and feature-test macro header used across DragonFly kernel and userland headers.

Key responsibilities:
- Defines compiler feature probes such as `__has_attribute`, `__has_builtin`, and `__GNUC_PREREQ__`.
- Provides C/C++ declaration guards, public/hidden symbol visibility macros, and DSO visibility attributes.
- Defines token concatenation/stringification, ANSI compatibility shims, inline/const/volatile handling, and cache-line alignment helpers.
- Wraps GCC/Clang attributes for noreturn, const/pure, malloc-like, packed, aligned, section, nonnull, used, warn-unused-result, alloc-size, alloc-align, constructor, aliasing, weak references, and format checking.
- Defines `__offsetof`, `__containerof`, dequalification helpers, branch prediction macros, and C11 compatibility macros for `_Alignas`, `_Alignof`, `_Noreturn`, `_Static_assert`, `_Thread_local`, and `__generic`.
- Implements POSIX/XSI/BSD/ISO C visibility feature-test macro policy.
- Defines `__GLOBL` assembly-global helper for preserving kernel module sections.

Dependencies:
- Assumes compiler predefined macros and DragonFly integer typedefs from surrounding headers.

Notable risks:
- This file controls namespace exposure for virtually every public header; small changes can break both kernel and userland builds.
- It encodes old compiler compatibility paths alongside modern C11/C++11 behavior.
- The visibility and declaration macros are especially sensitive in C++ consumers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cdefs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cdio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cdio.h

CD-ROM audio, TOC, subchannel, volume, door, and transport ioctl ABI.

Key responsibilities:
- Defines MSF/LBA address union and CD TOC/subchannel data structures.
- Defines audio status values and subchannel payload formats for current position, media catalog, and track info.
- Defines ioctls for playing tracks, blocks, or MSF ranges; reading subchannels and TOC entries; setting audio patches/volume/channel modes; pause/resume/reset/start/stop/eject; allow/prevent removal; and close tray.
- Provides constants for LBA/MSF address formats and sub-Q data formats.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Uses bitfields and device protocol layouts; ABI depends on compiler layout compatibility on DragonFly targets.
- Several ioctl payloads contain user pointers that driver implementations must copy safely.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cdrio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cdrio.h

CD-R/CD-RW writer ioctl ABI for blanking, track setup, cue sheets, fixation, speeds, block size, and progress.

Key responsibilities:
- Defines `struct cdr_track` with data block type, preemphasis, and test-write flags.
- Defines raw, subchannel, Mode 1/2, XA, reserved, and vendor-specific data block type constants.
- Defines cue sheet entry and session format/type structures.
- Defines ioctls for blanking media, querying next writable address, initializing writer/track, sending cue sheets, flushing, fixating, setting read/write speeds, getting/setting block size, and querying progress.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- `struct cdr_cuesheet` contains a user pointer to cue entries; ioctl handlers must validate length and copy safely.
- Session and data block constants are protocol-facing and must match ATAPI/SCSI driver expectations.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cdrio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/checkpoint.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/checkpoint.h

Public checkpoint syscall/control header with small kernel helper structures.

Key responsibilities:
- Defines checkpoint operation constants: freeze, thaw, freeze-by-pid, and thaw-binary, with the latter two noted unsupported.
- Includes procfs status/fpregset/process-info types for kernel checkpoint state capture.
- Defines `pstate_t` and `lc_args_t` for kernel thread/process state collection.
- Declares userland `sys_checkpoint()` when not compiling kernel code.

Dependencies:
- Includes `sys/procfs.h`.

Notable risks:
- The public operation constants expose unfinished modes.
- Checkpoint state depends on procfs register/status structures, tying checkpoint ABI to process inspection data layout.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/checkpoint.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/chio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/chio.h

SCSI media changer ioctl ABI for picker, slot, portal, and drive robotics.

Key responsibilities:
- Defines changer element types for medium transport, storage slots, import/export portals, and data-transfer drives.
- Defines structures for MOVE MEDIUM, EXCHANGE MEDIUM, POSITION TO ELEMENT, device parameters, volume tags, element status, status requests, and volume-tag mutation.
- Defines element status flags for full/access/exception/import-export/source/SCSI identity validity.
- Defines ioctls for move, exchange, position, get/set picker, get parameters, initialize elements, get status, and set volume tag.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Comments warn element type numeric values are relied on by changer driver code as array offsets.
- Status request structures contain user pointers; driver copyin/copyout validation is critical.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/chio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ckpt.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ckpt.h

Kernel-only checkpoint file format/state header.

Key responsibilities:
- Defines maximum checkpointed threads as 256.
- Defines checkpoint file header, VM layout info, file descriptor/file-handle state, and signal/action state structures.
- Defines `CKFIF_ISCKPTFD` to mark the checkpoint file descriptor itself.
- Defines `struct vn_hdr` only when ELF word size is known, pairing vnode file handle with an ELF program header.
- Provides debug trace/printf macros under `_KERNEL` and `DEBUG`.

Dependencies:
- Kernel-only; includes `sys/types.h`, `sys/mount.h`, and `sys/signalvar.h`.
- Uses `fhandle_t`, `sigacts`, `itimerval`, `sigset_t`, and ELF program headers.

Notable risks:
- Header explicitly errors if included outside kernel/kernel-structures contexts.
- File-format structs contain reserved fields but no versioning beyond an unimplemented magic comment.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ckpt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/condvar.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/condvar.h

Kernel condition-variable interface.

Key responsibilities:
- Defines `struct cv` with a spinlock, waiter count, and description string.
- Declares init/destroy, wait, timed wait, signal/broadcast, and waiter-test functions.
- Provides wrappers for waits against either `struct lock` or `struct mtx`.
- Provides signal-interruptible and timeout variants through macros around internal functions.

Dependencies:
- Includes `sys/spinlock.h` and `sys/mutex.h`; forward-declares `struct lock`.

Notable risks:
- Wait macros depend on caller holding the matching lock type expected by the internal implementation.
- `cv_broadcastpri` ignores priority and aliases to broadcast.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/condvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/conf.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/conf.h

Kernel character-device, line-discipline, and swap-device configuration header.

Key responsibilities:
- Defines `struct cdev`, including ownership/perms, major/minor, parent, hash links, vnode lists, name, driver private pointers, dev_ops pointers, I/O size, sysref, tty/disk union, bio tracking, timestamps, pager object, property dictionary, and kqueue info.
- Defines `si_flags` values for hash state, permission override, dev_ops interception, devfs linkage, reprobe, and free-block support.
- Defines line discipline function typedefs and `struct linesw`.
- Defines `struct swdevt` for swap device accounting and vnode/cdev linkage.
- Declares kernel helpers for line discipline registration, device references/destruction/name lookup, zero-device check, minor extraction, and disk lookup by name.
- Defines default UID/GID constants used by device creation.

Dependencies:
- Kernel/kernel-structures only; includes queue, time, biotrack, sysref, event, proplib, and param headers.
- Uses dev_ops from `device.h` indirectly and vnode/disk/vm_object forward declarations.

Notable risks:
- `struct cdev` is central shared kernel state for devfs, disk, tty, pager, and kqueue paths; layout changes have broad blast radius.
- Multiple subsystems rely on the tty/disk union fields being interpreted correctly for the device type.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/conf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cons.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cons.h

Kernel console driver registration and console-device operation interface.

Key responsibilities:
- Defines console callback typedefs for probe, init, init-fini, term, get/check/put char, debugger control, and polling.
- Defines `struct consdev`, including callback vector, associated tty/cdev, priority, probe status, private pointers, unit, and flags.
- Defines console availability/debug support flags and console selection priorities.
- Provides `CONS_DRIVER` macro to register console devices in `cons_set`.
- Declares kernel console entry points: `cncheckc`, `cngetc`, `cninit`, `cninit_finish`, `cndbctl`, `cnputc`, and `cnpoll`.

Dependencies:
- Includes `sys/types.h`; kernel users rely on data-set registration macros and tty/cdev definitions elsewhere.

Notable risks:
- Console selection depends on probe routines setting `cn_probegood` and priority consistently.
- Console callbacks can be used in early boot/debug contexts, so implementations must tolerate limited kernel services.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cons.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/consio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/consio.h

Console, virtual terminal, video mode, font, mouse, screen saver, and terminal-emulator ioctl ABI.

Key responsibilities:
- Defines historical KD/GIO/PIO/CONS ioctl constants for text/graphics/pixel modes, border color, raster setup, screen maps, colors, adapter/mode info, blanking, cursor, bell, history, font data, screenshots, terminal info, keyboard selection, and vty switching.
- Defines mouse ioctl structures for position, mode, events, and operations.
- Defines font payload types for 8x8, 8x14, and 8x16 font tables.
- Defines `vid_info`, `scrshot`, `term_info`, and `vt_mode`.
- Declares kernel globals controlling break-to-debugger behavior.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.
- Some ioctl payload typedefs reference framebuffer/video types declared in other headers.

Notable risks:
- Many ioctl numbers and names are historical compatibility ABI and cannot be freely renumbered.
- Multiple ioctls carry user pointers, including screenshot buffers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/consio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/copyright.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/copyright.h

Kernel copyright string aggregation header.

Key responsibilities:
- Defines string macros for DragonFly, FreeBSD, and UCB copyright notices.
- Defines global `char copyright[]` concatenating DragonFly, FreeBSD, and UCB notices.
- DragonFly string covers 2003-2026 in this tree.

Dependencies:
- None beyond C string literal concatenation.

Notable risks:
- This header defines storage, not just declarations; including it from multiple translation units would create duplicate definitions unless used carefully.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/copyright.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpputil.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpputil.h

Preprocessor utility header for variadic macro metaprogramming.

Key responsibilities:
- Defines `VA_NARGS(...)` to count variadic arguments up to 64, with the documented caveat that empty args count as 1.
- Defines `__GENSTRUCT(tag, args...)`, dispatching to numbered macros that emit a `struct tag` with each argument as a field declaration.
- Provides `__GENSTRUCT1` through `__GENSTRUCT19`.

Dependencies:
- Includes `sys/cdefs.h` for `__CONCAT`.

Notable risks:
- The argument counter supports more arguments than the generated struct macros implement; calls above 19 fields will dispatch to undefined macros.
- This intentionally abuses preprocessor behavior and should be used only where existing local patterns require it.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpputil.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpu_topology.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpu_topology.h

Kernel CPU topology tree definitions and lookup API.

Key responsibilities:
- Defines `cpu_node_t` topology nodes with parent, children, child count, cpumask membership, level type, AMD compute unit ID, and physical memory value.
- Defines topology levels: package, chip, core, and thread.
- Provides `CPUSET_FOREACH` iteration macro over `ncpus`.
- Declares global topology metadata and root node.
- Declares lookup helpers for masks by level, CPU node by CPU ID/chip ID, highest node memory, and per-CPU HT/core/physical IDs.

Dependencies:
- Kernel/kernel-structures only for structs; kernel-only for externs/functions.
- Includes `sys/param.h` and `sys/cpumask.h`.

Notable risks:
- `child_node[MAXCPU]` fixes maximum fanout to global CPU count.
- Consumers must distinguish topology level types from CPU IDs and chip IDs.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpu_topology.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpuctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpuctl.h

CPU control device ioctl ABI for MSR, CPUID, and microcode/update operations.

Key responsibilities:
- Defines payloads for reading/writing MSRs, issuing CPUID, issuing CPUID with count/level type, and passing update blobs.
- Defines ioctls for read/write MSR, CPUID, update, set/clear MSR bits, and CPUID_COUNT.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- MSR writes and CPU updates are privileged and security-sensitive; `caps.h` has capability restrictions for WRMSR and update.
- `cpuctl_update_args_t` carries a user pointer and length.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpuctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpuhelper.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpuhelper.h

Kernel-only per-CPU helper message interface.

Key responsibilities:
- Defines callback type `cpuhelper_cb_t`.
- Defines `struct cpuhelper_msg`, with `lwkt_msg` as the required first field, callback, callback argument pointer, and integer argument.
- Declares helpers to assert CPU context, send helper messages to a CPU, reply, and initialize messages.

Dependencies:
- Kernel-only; includes `sys/msgport.h` and `sys/msgport2.h`.

Notable risks:
- The `lwkt_msg` first-field requirement is an ABI convention with LWKT messaging code.
- Callers must avoid sending work to the wrong CPU context or replying incorrectly.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpuhelper.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpumask.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpumask.h

CPU mask public wrapper and CPU lock type definitions.

Key responsibilities:
- Imports machine `__cpumask_t` and exposes it as `cpumask_t`.
- For userland, maps `CPU_ZERO`, `CPU_SET`, `CPU_CLR`, `CPU_ISSET`, `CPU_COUNT`, `CPU_AND`, `CPU_OR`, `CPU_XOR`, and `CPU_EQUAL` to machine helpers.
- Defines `CPU_SETSIZE` from cpumask width.
- Defines public `cpulock_t` and bit/counter masks for a combined exclusive bit plus auxiliary count lock.

Dependencies:
- Includes `machine/cpumask.h` and `machine/stdint.h`.

Notable risks:
- `cpumask_t` width is machine-dependent, so public CPU set size follows architecture limits.
- `cpulock_t` is public because it appears near process structures; callers must honor bit layout.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/cpumask.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/csprng.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/csprng.h

Kernel CSPRNG state and API header based on SHA-256 pools and ChaCha stream cipher state.

Key responsibilities:
- Defines call flags for try-lock behavior and unlimited `/dev/urandom` reads.
- Defines `struct csprng_pool` with byte count and SHA-256 context.
- Defines cache-aligned `struct csprng_state` with key, reseed count, ChaCha context, 32 entropy pools, per-source pool index table, spinlock, reseed callout, failed reseed counter, entropy source counters, last reseed time, and IBAA/L15 state.
- Declares initialization, random output, and entropy injection functions.
- Asserts SHA-256 digest length is 32 bytes.

Dependencies:
- Includes ChaCha, SHA-2, callout, spinlock, time, and `ibaa` headers.
- Uses `__cachealign` and `CTASSERT`.

Notable risks:
- State has fixed 256 source IDs and 32 pools.
- Correct locking and reseed scheduling are critical for entropy safety and avoiding blocking/read-path races.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/csprng.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ctype.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ctype.h

Kernel-only lightweight ASCII ctype macro header.

Key responsibilities:
- Defines kernel macros for `isspace`, `isascii`, `isupper`, `islower`, `isalpha`, `isdigit`, `isxdigit`, and `isprint`.
- Defines ASCII-only `toupper` and `tolower`.

Dependencies:
- Active only under `_KERNEL`.

Notable risks:
- Macros evaluate arguments more than once in some cases, so callers should avoid side-effect expressions.
- Behavior is ASCII-only and not locale-aware.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ctype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/devfs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/devfs.h

DragonFly devfs node, mount, message, cloning, alias, and kernel API header.

Key responsibilities:
- Defines devfs node types and lightweight dirent/fid structures.
- Defines `struct devfs_node` with cdev, mount, dirent, vnode, parent, type, children, readdir cookie state, link/symlink state, ownership/perms/flags, timestamps, and child list.
- Defines kernel mount data, orphan tracking, clone handlers, aliases, dev_ops ref records, and a large `devfs_msg` union for asynchronous core operations.
- Defines devfs message IDs for device create/destroy, mount add/del, clone handler, find, alias, rules, scans, related destruction, inode-to-vnode, and sync.
- Defines node flags for linked/user-created/orphaned/cloned/hidden/invisible/pty/destroyed/rule-created/rule-hidden/link-wait states.
- Defines clone bitmap helpers and extensive kernel APIs for node allocation/free/link/unlink, perms, GC, message sending, mount registration, node/path resolution, device creation/destruction, aliasing, rules, scans, cdev private data, and wildcard matching.
- Defines public mount flags and `struct devfs_mount_info`.

Dependencies:
- Kernel paths include queue, lock, conf, msgport, dirent, device, and ucred headers.
- Tightly coupled to vnode, mount, cdev/dev_ops, kqueue, and LWKT messaging.

Notable risks:
- Node accessibility has two different hiding concepts: inaccessible hidden nodes and readdir-invisible nodes.
- The message union carries many pointer types and depends on correct message ID interpretation.
- `DEVFS_DEFAULT_MODE` macro includes a trailing semicolon in its definition, which is style-sensitive in expressions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/devfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/devfs_rules.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/devfs_rules.h

Devfs rule ioctl and kernel rule-application header.

Key responsibilities:
- Defines `struct devfs_rule` for in-kernel linked rules, including type/cmd, mount point, device name, link name, device type, mode, uid, gid, and queue link.
- Defines fixed-size `struct devfs_rule_ioctl` for userland ioctl exchange using `PATH_MAX` buffers.
- Defines rule selector bits for name, type, and jail.
- Defines rule command bits for link, hide, show, and permission changes.
- Defines ioctls to add, apply, clear, and reset rules.
- Declares kernel iteration callbacks to apply or reset rules on devfs nodes.

Dependencies:
- Includes `sys/ioccom.h`, `sys/queue.h`, and `sys/types.h`; kernel structures include `sys/devfs.h`.

Notable risks:
- Rule type and command bits overlap numerically by design but live in separate fields.
- Userland fixed path buffers must be validated and terminated before conversion to kernel pointer fields.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/devfs_rules.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/device.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/device.h

DragonFly character-device operation dispatch interface and device creation API.

Key responsibilities:
- Defines generic and per-operation device argument structs for open, close, read, write, ioctl, mmap, mmap_single, strategy, dump, psize, kqfilter, clone, and revoke.
- Defines typed function prototypes for each device operation and `struct dev_ops`, including metadata head and operation vector.
- Defines device type flags such as tape, disk, tty, memory, and seekable set.
- Defines kernel-only driver flags such as memory disk, can-free, track-close, master, no emergency pager, MPSAFE, KVABIO, and quick.
- Defines dev_ops major-number registration/linking structures and RB tree prototypes.
- Declares kernel dispatcher wrappers, dev_ops compile/intercept/restore helpers, device creation/destruction/alias/autoclone APIs, and sync.

Dependencies:
- Kernel-only for most content; includes types, tree, and syslink RPC.
- Uses cdev, ucred, file, uio, bio, knote, vm objects/pages/backing, and sysmsg concepts.

Notable risks:
- `struct dev_ops` field positions are explicitly hard-coded for static initialization.
- `lwkt`/syslink descriptors and dev argument structs form an internal ABI between generic dispatch and drivers.
- Operation wrappers must pass correct file/vnode/credential context for security and lifetime correctness.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/device.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/devicestat.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/devicestat.h

Device I/O statistics ABI and kernel accounting interface.

Key responsibilities:
- Defines `DEVSTAT_VERSION` and warns it must change when struct/enumeration ABI changes.
- Defines support flags, transaction direction flags, tag types, device priority classes, and device/interface type flags.
- Defines `struct devstat` with queue linkage, device identity, byte and operation counters for reads/writes/frees/other, busy count, block size, tag counters, creation/busy/start/completion times, support flags, device type, and priority.
- Declares kernel functions to add/remove entries and start/end transactions, including buffer-based completion.

Dependencies:
- Includes queue, time, and types headers.

Notable risks:
- Userland statistics consumers rely on exact struct/enumeration layout and `DEVSTAT_VERSION`.
- Busy-time accounting depends on balanced start/end transaction calls.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/devicestat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dirent.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/dirent.h

Directory entry ABI for `getdirentries(2)` and filesystem readdir output.

Key responsibilities:
- Defines `ino_t` as 64-bit if not already declared.
- Defines `struct dirent` with inode/file number, name length, file type, reserved padding, and fixed `d_name[256]`.
- Handles POSIX/BSD namespace compatibility: kernel or strict POSIX exposes `d_ino`; BSD-visible userland exposes `d_fileno` with `d_ino` macro alias.
- Defines BSD-visible `DT_*` file type constants, including whiteout and database record file.
- Defines `_DIRENT_MINSIZ`, `_DIRENT_RECLEN`, `_DIRENT_DIRSIZ`, and `_DIRENT_NEXT` helpers with 8-byte alignment.

Dependencies:
- Includes `sys/cdefs.h` and `machine/stdint.h`.

Notable risks:
- The fixed `d_name` is a compatibility choice; code must still allocate records based on computed record length.
- Readdir-producing filesystems must correctly set `d_namlen`, NUL termination, and alignment.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disk.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/disk.h

Kernel disk object, media information, disklabel policy flags, and disk-management API.

Key responsibilities:
- Defines `struct disk_info` carrying media size or block count, block size, disklabel management flags, optional geometry, trim flag, and serial number.
- Defines disk slice/open policy flags for no labels, one slice, compatibility labels/partition A, raw extensions, quiet MBR handling, device mapper naming, and raw psize fallback.
- Defines `struct disk` with dev_ops pointers, flags, open count, raw and special cdevs, slices, disk_info, disk type, list linkage, cluster DMSG iocom, and destruction refs.
- Declares disk creation/destruction, info/type updates, open count, dump checks/config, enumeration, invalidation/unprobe, async/sync disk messages, bounds checks, and cluster iocom helpers.
- Defines disk message IDs for probe, destroy, slice reprobe, disk reprobe, unprobe, and sync.

Dependencies:
- Kernel/kernel-structures only; includes `diskslice.h`, queue, msgport, and `dmsg.h`.

Notable risks:
- `disk_info` allows either byte size or block count, not both; drivers must populate it consistently.
- Disk object participates in devfs, disklabel, dump, and DMSG cluster export paths.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disklabel.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/disklabel.h

Abstract disklabel dispatch layer for 32-bit and 64-bit DragonFly disk labels.

Key responsibilities:
- Defines `disklabel_t` union wrapping opaque, `disklabel32 *`, or `disklabel64 *`.
- Defines maximum pack name length.
- Defines `struct disklabel_ops`, including label type UUID, on-disk label size, and operations to read, set, write, clone, adjust reserved areas, get partition bounds, load partinfo, get partition count, get pack name, make a virgin label, and free labels.
- Provides typedef `disklabel_ops_t`.

Dependencies:
- Includes `sys/types.h` and `sys/uuid.h`.
- Forward-declares cdev, diskslice(s), disk_info, and partinfo.

Notable risks:
- This abstraction lets disk slice code handle multiple on-disk label formats; every op must agree on units and reserved-region semantics.
- `disklabel_t` is a tagged-by-context union with no runtime discriminator.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disklabel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disklabel32.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/disklabel32.h

Legacy BSD 32-bit sector-based disklabel on-disk format and ioctl ABI.

Key responsibilities:
- Defines label sector/offset for i386/x86_64 boot use, magic number, partition count, raw/swap/label partition indexes.
- Defines `struct disklabel32` with magic, drive type/subtype, type/pack names, geometry, spare/alternate cylinder data, hardware timing/skew fields, drive data, checksum, partition count, boot/superblock sizes, and fixed partition table.
- Defines `struct partition32` with sector count, sector offset, filesystem block/fragment metadata, filesystem type, and cpg/sgs union.
- Implements inline `dkcksum32()` XOR checksum over label through active partitions.
- Declares kernel `disklabel32_ops`.
- Defines ioctls to get, set, write, and get virgin 32-bit labels.

Dependencies:
- Includes types, optional kernel systm, and ioccom.
- Depends on disklabel ops declared by `disklabel.h` when used with abstraction.

Notable risks:
- Sector counts and offsets are 32-bit, limiting large-disk representation.
- Checksum depends on `d_npartitions`; invalid values can affect checksum scan bounds unless validated before use.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disklabel32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disklabel64.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/disklabel64.h

DragonFly 64-bit byte-offset disklabel on-disk format and ioctl ABI.

Key responsibilities:
- Defines 64-bit label magic, active/reserved partition counts, and reserved boot2 size.
- Defines `struct disklabel64` starting with 512 reserved bytes, followed by magic, CRC, alignment, partition count, storage UUID, total size, boot/base/stop/backup offsets, pack name, reserved space, and partition table.
- Defines `struct partition64` with slice-relative byte offset/size, filesystem type, reserved zero fields, type UUID, and storage UUID.
- Declares kernel `disklabel64_ops`.
- Defines ioctls to get, set, write, and get virgin 64-bit labels.

Dependencies:
- Includes types, optional kernel systm, ioccom, and uuid.

Notable risks:
- All offsets are slice-relative bytes, unlike 32-bit labels; conversion bugs can corrupt partition bounds.
- The first 512 bytes are excluded from CRC and preserved on writeback.
- Active partition limit is 16 while virgin-label space reserves room for 32.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/disklabel64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/diskmbr.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/diskmbr.h

Legacy MBR partition table constants, type names, and partition entry format.

Key responsibilities:
- Defines MBR sector offsets, partition entry size/count, extended partition constants, boot signature offset/value, and many partition type IDs.
- Defines DragonFly BSD partition type `0x6C`, with comment noting previous use of `0xA5` and GRUB conflicts.
- Provides a static partition type-to-name table when not standalone.
- Defines packed logical `struct dos_partition` fields for CHS start/end, type, LBA start, and sector count.
- Uses compile-time assertion to ensure entry size is 16 bytes.
- Provides CHS sector/cylinder extraction macros.

Dependencies:
- Includes `sys/types.h`; defines fallback `CTASSERT` if absent.

Notable risks:
- CHS sector numbers are one-based in MBR, while block I/O is zero-based.
- The static name table in a header can create per-translation-unit copies.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/diskmbr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/diskslice.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/diskslice.h

Disk slice/partition management ABI and kernel helpers for minor encoding, open masks, probing, and partition info.

Key responsibilities:
- Defines special slice IDs: compatibility slice, whole-disk slice, base slice, and whole-slice partition.
- Defines disk ioctl ABI for write-label control, slice info, sync slice info, kernel dump toggle, recluster, media size, sector size, and `DIOCGPART`.
- Defines support limits for disk units, slices, reserved partitions, and in-kernel partitions.
- Defines `struct diskslice` with device, sector offset/size, reserved sectors, type/storage UUIDs, foreign type, flags, label, label ops, per-partition dev pointers, open mask, write-label flag, and open count.
- Defines `struct diskslices` holding global slice array metadata, sector conversion values, and initial slice array.
- Defines `struct partinfo` with byte offset/size, block count/size, reserved blocks, filesystem type, disk geometry, and UUIDs.
- Provides inline minor-number builders/extractors for unit/slice/partition and open-mask helpers.
- Declares MBR/GPT init, open/close/ioctl/size/check helpers, slice structure allocation/free, disk error reporting, and disk bio sorting.

Dependencies:
- Includes types, disklabel, uuid, ioccom, and kernel conf/systm when needed.
- Couples cdev minor layout to disk and devfs device creation.

Notable risks:
- Minor-number bit layout is hard-coded and shared by creation/extraction helpers.
- Reserved block handling protects in-band labels and parent overlaps; filesystem writes must honor it.
- `DIOCGSLICEINFO` exposes `struct diskslices`, so layout compatibility matters for consumers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/diskslice.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dkstat.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/dkstat.h

Kernel-only legacy disk/tape statistics extern header.

Key responsibilities:
- Declares global counters `tk_nin`, `tk_nout`, and `tk_rawcc`.

Dependencies:
- Kernel/kernel-structures only; includes `sys/types.h`.

Notable risks:
- Header errors if included from normal userland.
- These are global counters, so users need to know where accounting is updated and synchronized.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dkstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dmap.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/dmap.h

Virtual swap-to-physical swap disk map definitions.

Key responsibilities:
- Defines `NDMAP` as 38 swap map entries.
- Defines `struct dmap` with current process swap size, allocated physical swap amount, and first disk block for each chunk.
- Defines `struct dblock`, returned by swap mapping lookup, with base physical contiguous drum block and size.

Dependencies:
- Includes `sys/types.h` and `sys/blist.h`.

Notable risks:
- This is low-level VM/swap mapping state; `swblk_t` units must match VM and swap allocator expectations.
- Fixed `NDMAP` constrains direct map entries.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dmsg.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/dmsg.h

DragonFly DMSG mesh/cluster protocol and kernel I/O communication state header, used by HAMMER2 and block-device clustering paths.

Key responsibilities:
- Documents mesh connection, SPAN advertisement/relay, stacked transactions, message state flags, abort semantics, header alignment, inline/out-of-band auxiliary data, and CRC rules.
- Defines 64-byte `struct dmsg_hdr` with magic/endian, salt, msgid, circuit, link verifier, encoded command/flags/size, aux CRC/bytes/descriptor, error, and header CRC.
- Defines protocol limits for header, aux data, and ring buffer sizing.
- Defines transaction flags, protocol IDs for link/debug/HAMMER2/block/VOP, command masks, alignment helpers, and command constructors.
- Defines link-layer commands for PAD, PING, AUTH, CONN, SPAN, and ERROR.
- Defines link connection and span structures with media/peer/PFS UUIDs, masks, type/version/status, distance/rnss, media block info, and labels.
- Defines debug shell command and block protocol commands for open/close/read/write/flush/freeblks/error with associated request/response structures.
- Defines general DMSG error constants and `union dmsg_any` for maximum-size message storage.
- Under kernel structures, defines transactional state, message, aux data, and `kdmsg_iocom` stream controller with root state, state trees, message queue, callbacks, auto connection/span state, and helper thread fields.
- Declares kernel DMSG iocom lifecycle, reconnect, auto-initiate, drain, allocation, write, reply/result, aux detach/free functions.

Dependencies:
- Includes types and uuid; kernel structures include tree and thread.
- Uses RB trees, TAILQs, locks, file descriptors, kernel threads, malloc types, and subsystem-specific pointers such as HAMMER2 and block-device state.

Notable risks:
- All extended headers must be 64-byte aligned; command encoding includes structure size and must match actual struct layout.
- Transaction lifecycle is complex: both sides create/delete, stacked child transactions must abort/terminate correctly, and relays translate ids/circuits.
- CRC calculation has special handling for `hdr_crc` being treated as zero.
- Header comments note auth is often omitted, so transport and endpoint trust assumptions must be reviewed in callers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dmsg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/domain.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/domain.h

Network protocol domain registration structure header.

Key responsibilities:
- Defines `SLIST_HEAD(domainlist, domain)`.
- Defines `struct domain` with address family, name, init hook, externalize/dispose hooks, protocol switch range, list linkage, routing table attach data, interface attach/detach/up/down hooks, and AF-dependent ifnet data support.
- Declares kernel global domain list and local domain.
- Declares `net_add_domain`.
- Defines `DOMAIN_SET` SYSINIT registration macro.

Dependencies:
- Includes `sys/queue.h`; forward-declares mbuf and ifnet.
- Uses `struct protosw` defined elsewhere.

Notable risks:
- Domain registration order uses SYSINIT priority and affects protocol availability.
- Routing/interface hooks are per-address-family and must handle lifecycle symmetry.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/domain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dsched.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/dsched.h

Kernel disk scheduler integration stub/header.

Key responsibilities:
- Defines disk scheduler policy name length.
- Declares hooks for disk create, update, and destroy.
- Provides placeholder no-op macros for future buffer/process/thread enter/exit accounting.

Dependencies:
- Kernel-only; includes queue, bio, biotrack, lock, conf, msgport, sysctl, and disk headers.

Notable risks:
- Most hooks are placeholders, so consumers may assume scheduling/accounting exists when macros currently compile away.
- Disk scheduler lifecycle must track disk create/update/destroy with disk_info changes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dsched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dtype.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/dtype.h

Legacy disk device type and filesystem type constants plus optional name tables.

Key responsibilities:
- Defines disk hardware/device type constants such as SMD, MSCP, SCSI, floppy, CCD, Vinum, and DiskOnChip.
- Under `DKTYPENAMES`, defines `dktypenames` and `DKMAXTYPES`.
- Defines partition filesystem type constants including unused, swap, historical UNIX/FFS/LFS/MSDOS/ISO9660, Vinum, RAID, CCD, HAMMER, HAMMER2, UDF, EFS, ZFS, NANDFS, encrypted, and unspecified.
- Under `DKTYPENAMES`, defines `fstypenames`, `fstype_to_vfsname`, and `FSMAXTYPES`.

Dependencies:
- Includes `sys/types.h`.
- Optional tables depend on `NELEM` being available from including context.

Notable risks:
- Numeric filesystem type values are on-disk label ABI and should not be reused casually.
- Some names map to NULL VFS names, so automount/probe code must tolerate unsupported legacy values.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dtype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dvdio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/dvdio.h

DVD structure and CSS/RPC authentication ioctl ABI.

Key responsibilities:
- Defines `struct dvd_layer` for physical layer metadata including book type/version, size/rate, layers, path/type, density, BCA, and sector bounds.
- Defines `struct dvd_struct` for READ DVD STRUCTURE requests with format, layer, copy-management fields, length, and 2048-byte data buffer.
- Defines `struct dvd_authinfo` for REPORT KEY/SEND KEY operations, including AGID, ASF/CPM/CP_SEC/CGMS flags, region/RPC data, LBA, and key/challenge buffer.
- Defines DVD structure format constants, report-key/send-key format constants, AGID invalidate value, and ioctls for report key, send key, and read structure.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Bitfield layout and ioctl struct ABI must match driver/userland expectations.
- Authentication operations are stateful around AGID and media region/RPC data.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/dvdio.h -->