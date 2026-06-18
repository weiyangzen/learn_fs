# Group Research: group_444_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_hhook_h_sources_os_bs_a90ec3ee108a

Scope verified against `Docs/research_subset_a.md`: `sources/os/bsd/freebsd-src` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hhook.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/hhook.h

Defines the FreeBSD helper hook KPI used by Khelp modules to register callback hooks at named kernel hook points. It declares hook types for TCP, socket, and IPsec paths; registration flags for sleep behavior and VNET-local hook heads; and the `hhook_func_t` callback signature.

Core data structures are `struct hookinfo`, carrying callback/helper/user-data/type/id registration metadata, and `struct hhook_head`, carrying the hook queue, rmlock, type/id, VNET id, hook count, refcount, and global/VNET list links. Public routines support adding/removing hooks directly or by lookup, registering/deregistering hook heads, acquiring/releasing heads, testing virtualization, and running hooks.

The `HHOOKS_RUN_IF` and `HHOOKS_RUN_LOOKUP_IF` macros are important performance and correctness wrappers: the former avoids entering hook dispatch when no hooks are registered, while the latter performs lookup/refcount/release around infrequent call sites.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hhook.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hwt.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/hwt.h

User-visible Hardware Trace header defining ioctl commands and ABI structs for allocating, starting, stopping, configuring, servicing, and reading hardware trace sessions. It depends on `sys/hwt_record.h`, `cpuset_t`, VM offsets, and path limits.

The ioctl API uses magic `0x42` and exposes `HWT_IOC_ALLOC`, `START`, `STOP`, `RECORD_GET`, `BUFPTR_GET`, `SET_CONFIG`, `WAKEUP`, and `SVC_BUF`. Sessions can be per-thread (`HWT_MODE_THREAD`) or per-CPU (`HWT_MODE_CPU`) and identify a backend by name.

ABI structures are explicitly 16-byte aligned. `struct hwt_alloc` includes buffer size, mode, pid/cpuset, backend name, returned identity, and kqueue fd. `struct hwt_record_user_entry` mirrors record types for mmap/executable/kernel path records, buffer records, and thread records.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hwt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hwt_record.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/hwt_record.h

Defines the shared hardware-tracing record type enum used by both user ABI and kernel internals. Record kinds cover `MMAP`, `MUNMAP`, `EXECUTABLE`, `KERNEL`, thread create/name events, and trace buffer records.

Under `_KERNEL`, `struct hwt_record_entry` adds a `TAILQ_ENTRY` link and stores the kernel-side representation of each record. Path-bearing records use dynamically referenced `char *fullpath` plus address/base address; buffer records carry buffer id, current page, and offset; thread events carry a thread id.

This file is deliberately narrow and pairs with `hwt.h`, which defines the user-copy ABI form.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hwt_record.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/iconv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/iconv.h

Defines FreeBSD kernel iconv charset conversion limits, flags, sysctl ABI structs, user helper declarations, and kernel converter-class infrastructure. Charset and converter names are capped at 31 bytes, and conversion pair metadata is surfaced through versioned structs.

For userland, it declares functions such as `kiconv_add_xlat_table`, `kiconv_add_xlat16_*`, `kiconv_lookupconv`, `kiconv_lookupcs`, and charset quirk lookup. For kernel builds, it includes kobj/module/queue/sysctl dependencies and defines `struct iconv_converter_class`, `struct iconv_cspair`, and module declaration macros for converters and CES modules.

The kernel API includes open/close/convert functions, case-aware conversion, string/memory conversion helpers, VFS iconv bridge module support via `VFS_DECLARE_ICONV`, and internal converter stubs. Filesystems using on-disk encodings depend on this as a conversion plug-in interface.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/iconv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact.h

Defines the central exec image-activation structures used by `execve` handling. `struct image_args` tracks copied argument/environment strings, executable filename, fd, buffer state, and counts. `MAXSHELLCMDLEN` is one page.

`struct image_params` is the kernel execution context passed to image activators. It includes process/thread, vnode/object/attributes, file header, entry and relocation addresses, interpreter details, ELF auxargs, first page mapping, argv/envv output pointers, sysent vector, stack properties, credential transition state, ASLR flag state, interpreter vnode, and bookkeeping booleans.

Kernel declarations cover argument allocation/copying, permission checks, stack mapping, VM-space replacement, register setup, shell image activation, and pre/post exec hooks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact_aout.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact_aout.h

Describes classic BSD `a.out` executable headers and helper macros. It handles both little-endian and network-order encodings of the combined magic/machine-id/flag field and defines magic constants for `OMAGIC`, `NMAGIC`, `ZMAGIC`, and `QMAGIC`.

Macros calculate text/data addresses, offsets, relocation table offsets, symbol table offsets, string table offsets, alignment, and bad-magic checks. `struct exec` is the on-disk header containing segment sizes, symbol sizes, entry point, and relocation sizes.

The kernel-only declaration exposes `aout_coredump()`, showing this header still supports legacy coredump/image-format paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact_aout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact_binmisc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact_binmisc.h

Defines the user/kernel sysctl ABI for miscellaneous binary interpreter image activation. It allows administrators to register interpreter rules keyed by binary magic bytes, optional masks, and offsets, similar in purpose to Linux `binfmt_misc`.

`ximgact_binmisc_entry_t` is versioned and includes flags, magic offset/size, entry name, interpreter path plus arguments, magic bytes, and mask bytes. Limits include 32-byte names, 256-byte magic/mask, 64 entries, and matching only within the first page.

Sysctl names under `kern.binmisc` support add, remove, disable, enable, lookup, and list. User-settable flags enable entries, use masks, and optionally pre-open/cache interpreter vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact_binmisc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact_elf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact_elf.h

Kernel-only ELF image activation support header. It wraps machine ELF types and defines aux-vector helper macros, including pointer handling for LP64 kernels executing 32-bit ELF.

Key structures are `ElfN(Auxargs)` for loader-to-stack fixup data, `Elf_Brandnote` for ABI note recognition/translation, and `ElfN(Brandinfo)` for executable brand matching, interpreter path selection, sysent vector binding, and brand flags.

Exports cover brand registration/removal, FreeBSD auxarg fixups, core dump writing, note population/parsing, segment sizing, note registration, per-thread dump hooks, fallback brand, and FreeBSD/kFreeBSD brand notes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/imgact_elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/inotify.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/inotify.h

Defines FreeBSD’s Linux-compatible inotify ABI and kernel vnode event hooks. User-visible pieces include `struct inotify_event`, `inotify_init`, `inotify_init1`, `inotify_add_watch`, `inotify_add_watch_at`, and `inotify_rm_watch`.

Event and flag masks mirror Linux-style inotify semantics: access, modify, attrib, close, open, move, create, delete, delete-self, move-self, one-shot, mask-add/create, only-dir, no-follow, unmount, overflow, ignored, and is-dir. `_IN_NAMESIZE` computes aligned variable name storage.

Kernel macros `INOTIFY`, `INOTIFY_NAME`, `INOTIFY_MOVE`, and `INOTIFY_REVOKE` cheaply test vnode inotify flags before invoking `VOP_INOTIFY`; rename events use a shared cookie to pair moved-from and moved-to records.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/inotify.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/interrupt.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/interrupt.h

Defines the machine-independent interrupt event and handler framework. `struct intr_handler` stores filter and threaded handler callbacks, argument, flags, name, priority, owning event, and chain link. Handler flags represent network handlers, exclusivity, entropy, dead/suspended state, changed state, and MPSAFE behavior.

`struct intr_event` represents an interrupt source with handler list, lock, source cookie, interrupt thread, MD hooks for pre/post ithread, post-filter, CPU assignment, flags, cumulative handler flags, storm warning state, irq number, CPU binding, and phase/active counters.

APIs create/destroy events, add/remove/suspend/resume/describe handlers, bind events/ithreads, handle interrupts, manage affinity, and create/schedule/remove software interrupts. It also declares global interrupt statistics tables.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/interrupt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/intr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/intr.h

INTRNG-only interrupt-controller interface for mapping platform interrupt descriptions to interrupt sources. It includes machine interrupt definitions and rejects builds without `INTRNG`.

Defines map-data types for ACPI, FDT, GPIO, MSI, and platform-specific mappings, plus `struct intr_irqsrc` for registered interrupt sources with device, IRQ id, flags, name, CPU mask, counter, handler count, event, optional solo filter, and MSI IOMMU data.

Exports PIC registration/root claiming, interrupt source registration/dispatch, IRQ resource activation/setup/teardown/description, map/unmap/clone, MSI/MSI-X allocation/release/mapping, SMP IRQ binding and secondary PIC init, IPI registration/setup/send/dispatch, and the main assembly-facing interrupt entrypoint.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/intr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ioccom.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ioccom.h

Defines FreeBSD ioctl command encoding. Command words contain direction bits, parameter length, command group, and command number. `IOCPARM_SHIFT`, `IOCPARM_MASK`, `IOCPARM_LEN`, `IOCBASECMD`, and `IOCGROUP` decode those fields.

Direction bits are `IOC_VOID`, `IOC_OUT`, `IOC_IN`, and `IOC_INOUT`; construction macros include `_IO`, `_IOR`, `_IOW`, `_IOWR`, and `_IOWINT`. `_IOC_NEWLEN` and `_IOC_NEWTYPE` rewrite the encoded parameter size.

Kernel compatibility helpers include `IOCPARM_IVAL` for old ABI support and `_IOC_INVALID` as an impossible filler command. Userland gets the `ioctl(int, unsigned long, ...)` prototype outside standalone builds.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ioccom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ioctl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ioctl.h

Userland umbrella header for ioctl definitions. It intentionally errors under `_KERNEL`, directing kernel code to include the specific `xxxio.h` header instead.

It includes `sys/ioccom.h` for ioctl encoding and then aggregates file, socket, and tty ioctl command headers: `filio.h`, `sockio.h`, and `ttycom.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ioctl_compat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ioctl_compat.h

Defines legacy 4.3BSD tty ioctl compatibility structures and constants, guarded by `COMPAT_43TTY`. It errors if included without that compatibility option.

Structures include `tchars`, `ltchars`, and `sgttyb`. Ioctls cover old line discipline get/set, hangup, terminal parameters, special characters, local mode get/set/bit operations, and old console behavior.

The header also defines historical tty mode flags such as `RAW`, `CBREAK`, `ECHO`, parity bits, delay masks, local erase/echoing modes, `TOSTOP`, `FLUSHO`, `PASS8`, `PENDIN`, and related shifted local-mode aliases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ioctl_compat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/iov.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/iov.h

Defines the public ioctl ABI and nvlist schema conventions for PCI SR-IOV configuration. It names top-level schema/config sections (`PF`, `VF`, `DRIVER`, `IOV`) and parameter metadata keys (`TYPE`, `DEFAULT`, `REQUIRED`).

The long embedded schema comments specify the accepted packed-nvlist format, validation rules, supported parameter types, VF key naming (`VF-<n>`), required/default behavior, and example schema/config layouts. These comments are effectively the ABI contract for userland SR-IOV management tools.

`struct pci_iov_schema` returns packed schema plus length/error; `struct pci_iov_arg` passes packed config. Ioctls are `IOV_CONFIG`, `IOV_DELETE`, and `IOV_GET_SCHEMA`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/iov.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/iov_schema.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/iov_schema.h

Kernel helper API for constructing SR-IOV configuration schema nvlists. Flags identify parameters with defaults and required parameters.

Exports allocation of schema nodes and typed parameter adders for bool, string, uint8/16/32/64, unicast MAC, and VLAN values. This complements `iov.h`: PF drivers use these helpers to describe configuration accepted by `IOV_CONFIG`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/iov_schema.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ipc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ipc.h

System V IPC common header defining `key_t`, `uid_t`, `gid_t`, `mode_t` exposure, `struct ipc_perm`, permission bits, creation flags, control commands, and `IPC_PRIVATE`.

Compatibility builds define `struct ipc_perm_old` and conversion helpers. Internal macros convert between IPC ids, array indices, and sequence numbers: `IPCID_TO_IX`, `IPCID_TO_SEQ`, and `IXSEQ_TO_IPCID`.

Kernel declarations include `ipcperm()` and shared memory lifecycle hooks for fork, exit, and object info. Userland exposes `ftok()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ipc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ipmi.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ipmi.h

Defines the IPMI character-device ioctl ABI and protocol constants. It includes maximum address/RX sizes, channel/address defaults, address type constants, receive types, net function/command identifiers, chassis controls, device capability bits, message flags, and watchdog settings.

Ioctls use magic `'i'` and cover receiving messages, sending commands, registering/unregistering command handlers, event command control, and local BMC address/LUN get/set. Message structures are `ipmi_msg`, `ipmi_req`, `ipmi_recv`, `ipmi_cmdspec`, and address variants for generic, system-interface, and IPMB addresses.

On amd64, 32-bit compatibility command numbers and pointer-truncated structs are provided for `ipmi_recv32`, `ipmi_req32`, and `ipmi_msg32`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ipmi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/jail.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/jail.h

Defines the FreeBSD jail public ABI and kernel prison internals. Userland structures include `struct jail` API version 2, `struct xprison` version 3, jail states, and flags for create/update/attach/get/remove/descriptor behavior. Userland functions include `jail`, `jail_set`, `jail_get`, attach/remove variants, and descriptor attach/remove variants.

Kernel/private sections define `struct prison`, the central jail object with all-prison tree links, process list, parent/children, mutex, OSD, cpuset, VNET, root vnode, IP restrictions, RACCT proxy, MAC label, jail descriptors, child limits, allow flags, securelevel, statfs/devfs policy, lifecycle state, host identity strings, OS release/date, and refcounts.

It defines jail flags for persistence, hostname virtualization, IPv4/IPv6 restrictions, VNET, source-address selection, and removal/internal state. Allow flags cover hostname, SysV IPC, raw sockets, mount, quotas, socket address families, mlock, msgbuf, debugging, superuser-like checks, reserved ports, NFSD, extattr, time adjustment, routing, parent tamper, and audit.

The header also provides prison traversal macros, jail sysctl parameter declaration macros, and a broad kernel API for lookup, reference management, process linking, removal, IP checks, address-family checks, privilege checks, statfs enforcement, VFS allow registration, and RACCT iteration.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/jail.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/jaildesc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/jaildesc.h

Kernel-only jail descriptor support. `struct jaildesc` associates a file descriptor object with a `struct prison`, maintains the prison’s descriptor list link, a mutex, selinfo for event notification, and flags.

Flags identify removed jails and owning descriptors, where closing the descriptor removes the jail. Lock macros initialize/destroy/lock/unlock `jd_lock`.

APIs find descriptors from fd, allocate descriptors, get/set the associated prison, clean up descriptors for a prison, and deliver knote notifications.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/jaildesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/joystick.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/joystick.h

Small user-visible joystick ioctl header. `struct joystick` reports x/y axis values and two button states.

Ioctls allow setting/getting timeout and setting/getting X/Y offsets using group `'J'`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/joystick.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kassert.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kassert.h

Defines kernel and standalone assertion infrastructure. Kernel builds expose `panicstr`, `KERNEL_PANICKED()`, panic/vpanic declarations, and optional `kassert_panic` behavior depending on WITNESS/INVARIANT support.

With `INVARIANTS`, it enables `KASSERT`, vnode/mount assertions (`VNASSERT`, `MPASSERT`, `VNPASS`, `MPPASS`), poison-pointer debugging, and unreachable-segment panics. Without invariants, most checks compile away.

Also provides `CTASSERT`, `MPASS` variants, atomic pointer load alignment assertion, and `CRITICAL_ASSERT` for checking thread critical-section nesting.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kassert.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kbio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kbio.h

Keyboard ioctl and keymap ABI header. It defines keyboard modes (`K_RAW`, `K_XLATE`, `K_CODE`), lock and LED bits, keyboard type values, tone/sound/io-access ioctls, keyboard info, repeat-rate tables, and mux add/release controls.

Keymap support includes constants for key counts, states, dead keys, accent chars, function keys, and structures `keyent_t`, `keymap`, `accentmap`, `keyarg`, `fkeytab`, and `fkeyarg`. FreeBSD 13 compatibility structs preserve older byte-sized keymap layouts.

It defines special key codes for shift/control/alt, screen switching, function keys, accent/dead keys, debug/reboot/halt/paste actions, and output flags such as no-key, function-key, meta, backtab, special, release, and error. `KEYCHAR` and `KEYFLAGS` split packed key returns.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kbio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kcov.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kcov.h

Defines the KCOV coverage device ABI. It includes coverage comparison encoding from `sys/coverage.h` and ioctl encoding from `sys/ioccom.h`.

Constants define maximum entries, entry size, trace modes for PC and comparisons, and ioctls to enable, disable, and set buffer size. Comparison flag helpers alias the generic coverage macros.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kcov.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kdb.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kdb.h

Kernel debugger frontend/backend interface. It defines backend callback types for init, trace, per-thread trace, and trap handling, plus `struct kdb_dbbe` and `KDB_BACKEND()` linker-set registration.

Globals expose debugger active state, panic/trap entry flags, selected backend, current trap frame, PCB context, and current thread. APIs cover alternate breaks, entering/reentering debugger, backtraces, backend selection, initialization, panic/reboot, thread lookup/iteration/selection, and trap dispatch.

`kdb_why` reason strings classify debugger entry causes, including panic, kassert, trap, sysctl, boot flags, witness, VFS lock, watchdog, DTrace, and reboot. It also defines alternate-break return requests and debug access type constants.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kenv.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kenv.h

Defines constants for the `kenv(2)` syscall: get, set, unset, dump, dump loader environment, and dump static environment. Name and value syscall limits are both 128 bytes.

Kernel builds expose global environment state: dynamic environment flag, lock, kernel and machine-dependent environment pointers, static environment/hints buffers, and active `kenvp`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kenv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kern_prefetch.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kern_prefetch.h

Kernel-only prefetch helper. On amd64, `kern_prefetch()` emits a `prefetcht1` instruction against the supplied address while using the `before` pointer as an inline-assembly memory constraint.

Other architectures currently compile the helper to no operation, with a commented `__builtin_prefetch` placeholder.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kern_prefetch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kernel.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kernel.h

Core kernel initialization and tunable infrastructure header. It declares global clock/kernel variables under `_KERNEL`, then defines the ordered `sysinit_sub_id` initialization phases from tunables and VM through drivers, VFS, networking, syscalls, kthreads, SMP, RACCT, and final init.

`struct sysinit` and the `SYSINIT`/`C_SYSINIT`/`SYSUNINIT` macros place init/uninit records in linker sets, optionally wrapping through TSLOG. Ordering is controlled by subsystem id plus `SI_ORDER_*`.

Kernel tunable macros register typed loader/kernel environment tunables for int, long, ulong, int64, uint64, quad, bool, and string, with matching fetch helpers. The file also defines interrupt configuration hooks (`struct intr_config_hook`) and APIs to establish, disestablish, drain, or schedule one-shot hooks after interrupts are enabled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kerneldump.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kerneldump.h

Defines kernel dump on-disk/header ABI and kernel dump helper declarations. Dump headers are stored in network byte order, with `dtoh*`/`htod*` macros depending on host endian.

`struct kerneldumpheader` contains magic, architecture, version, arch version, dump length/time, encrypted key size, block size, hostname, version string, panic string, compression, dump extent, and parity. Supported compression values are none/gzip/zstd; encryption values are none/AES-256-CBC/ChaCha20. `struct kerneldumpkey` stores encryption metadata and variable encrypted key bytes.

Kernel declarations cover minidumps, generic dumps, physical-address chunk iteration, buffered dump writes, generated physical-address helpers, progress reporting, live dump start via device or vnode, and live dump eventhandler hooks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kerneldump.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kexec.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kexec.h

Defines FreeBSD’s kexec load ABI aligned with Linux concepts. User-visible `struct kexec_segment` contains source buffer, source size, physical destination, and destination size. `KEXEC_ON_CRASH` and `KEXEC_SEGMENT_MAX` are defined.

Kernel-only structures stage segments through VM pages and track a loaded image’s entry point, mapping object/address/size, machine-dependent pages, and MD image data.

Userland exposes `kexec_load()`. Kernel exports machine-dependent load and reboot hooks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kexec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/khelp.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/khelp.h

Defines the kernel helper module KPI used with `hhook.h`. Helper classes currently cover TCP and socket helpers.

Public routines register/deregister helpers, initialize/destroy helper OSD storage, fetch helper OSD data by id, resolve helper ids by name, and add/remove helper hook registrations. This is the management layer above helper hook execution.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/khelp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kobj.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kobj.h

Defines FreeBSD’s kernel object method-dispatch system. It provides typedefs for objects, classes, methods, operation descriptors, and compiled operation tables.

Classes contain name, method table, object size, base classes, refs, and compiled ops. Objects begin with an ops pointer. `KOBJMETHOD`, `DEFINE_CLASS_*`, and `DECLARE_CLASS` support method-table and inheritance declarations.

Runtime APIs compile/free classes, create/init/delete objects, and perform cached method lookup through `KOBJOPLOOKUP`. The cache has 256 slots, with optional hit/miss stats. `kobj_error_method()` is the default ENXIO-like method implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kpilite.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kpilite.h

Defines lightweight scheduler pin/unpin helpers for restricted kernel builds where offsets are available and modules are tied. It includes generated `offset.inc`.

`sched_pin_lite()` and `sched_unpin_lite()` operate on `struct thread_lite`, assert the target is `curthread`, maintain `td_pinned`, and use interrupt fences around pin-state changes. It is a narrow KPI subset for code that cannot use full thread definitions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kpilite.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ksem.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ksem.h

Internal POSIX semaphore file-object structure header, only available to kernel or `_WANT_FILE` consumers. `struct ksem` contains refcount, mode, owner ids, semaphore value, condition variable, waiter count, flags, timestamps for file-stat behavior, MAC label, and optional path.

Flags mark anonymous semaphores and dead semaphores that reject new waiters.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ksem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kthread.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/kthread.h

Defines descriptors and APIs for kernel processes and kernel threads. `struct kproc_desc` and `struct kthread_desc` provide linker/SYSINIT-friendly daemon startup metadata: name, main function, and optional global proc/thread pointer storage.

APIs create, exit, resume, suspend, shutdown, and start kernel processes and threads. `kproc_kthread_add()` creates a thread in a process, creating the process if necessary; `kthread_add()` creates a thread in an existing process.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/kthread.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktls.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ktls.h

Defines kernel TLS record structures, socket option ABI structs, exported session state, and kernel session management APIs. User/shared structures describe TLS record headers, TLS 1.2/1.3 AEAD additional data, MAC data, nonce data, enable parameters, get-record header, and exported one-direction session state.

Constants cover TLS versions, record types, maximum message/parameter sizes, GCM/ChaCha/CBC IV sizes, and TX/RX direction ids. `struct tls_enable` carries keys, IV, algorithms, flags, TLS version, and initial record sequence.

Kernel `struct ktls_session` tracks OCF/session offload state, send tag, crypto params, workqueue index, refcount, mode, tasks, socket/inpcb, RX interface/VLAN, pending/reset flags, sequence data, pending records, destroy task, and generation. APIs enable TX/RX, frame/enqueue/free records, query/set modes and sequences, manage offload mismatch/reset, export sessions, copy keys, and refcount/free sessions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktls.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ktr.h

Kernel trace ring-buffer support. `struct ktr_entry` records timestamp, CPU, source line/file, description format, thread, and six parameters. Globals define CPU mask, runtime mask, entry count, verbosity, ring index, and buffer pointer.

When `KTR` is compiled in, `CTR0` through `CTR6` macros emit tracepoints if the compile-time class mask includes the class. Without `KTR`, they compile away. `TR*` aliases target the general class.

The file also defines graph-oriented event macros for schedgraph-style state, counter, point, start, and stop events with up to four attributes, plus `ITR*` init-trace macros that are fully omitted unless `KTR_INIT` is compiled.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktr_class.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ktr_class.h

Defines the bitmask classes used by KTR tracing. Classes include general, network, device, lock, SMP, subsystem, pmap, malloc, trap, interrupt, signal, process, syscall, init, eventhandler, VFS/VOP, VM, IPv4/IPv6, run queue, UMA, callout, GEOM, busdma, scheduler, buffer cache, and ptrace.

`KTR_ALL` enables all 32 bits. `KTR_COMPILE` defaults to all classes when `KTR` is defined and zero otherwise, controlling compile-time trace elision.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktr_class.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktrace.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/ktrace.h

Defines the process ktrace ABI: operations, flags, record headers, record types, facility bits, and kernel/user APIs. `KTROP_SET`, `CLEAR`, and `CLEARFILE` are combined with `KTRFLAG_DESCEND`.

Record headers have legacy timeval and versioned timespec/CPU forms. Record payloads cover syscall entry/return, pathname lookup, generic I/O, processed signals, context switches, user records, named struct dumps, sysctl names, process constructor/destructor, capability failures, page faults, exec args/envs, and extended errors. `KTR_DROP` and `KTR_VERSIONED` are high bits in record type.

Kernel helpers emit each record type, process exec/exit/fork tracing, user-return flushing, structured payloads, capability failures, and raw data. Userland exposes `ktrace()` and `utrace()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/ktrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/libkern.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/libkern.h

Kernel libc-like utility header. It provides inline BCD/binary/hex conversion helpers with assertion bounds, min/max/abs variants for several integer types, random/ARC4 routines, timing-safe compare, bsearch, qsort/qsort_r, pattern matching, memory/string routines, and string duplication helpers.

Bit helpers wrap compiler builtins for first/last set bit, integer log2, power-of-two rounding, and bit counts. `ilog2()` chooses constant or generic forms using compiler features and `_Generic`.

It also handles sanitizer interceptors for selected string functions, defines `index`/`rindex`, signed-extension helpers for bitfields, `fnmatch` flags, and `__ssp_real` integration for user builds with SSP headers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/libkern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/limits.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/limits.h

Defines standard integer and system limits by mapping to machine-provided `_limits.h` values and visibility macros. It covers char, signed/unsigned char, short, int, long, and optionally long long min/max values.

C23 visibility adds `*_WIDTH` macros. POSIX/XSI visibility adds `SSIZE_MAX`, `SIZE_T_MAX`, `OFF_MAX`, `OFF_MIN`, `LONG_BIT`, `WORD_BIT`, and `MQ_PRIO_MAX`. BSD visibility adds uid/gid and quad/uquad limits.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/limits.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/link_aout.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/link_aout.h

Defines legacy a.out runtime linker and shared-library structures, compatible with SunOS-style shared library schemes. It includes shared object descriptors (`sod`), runtime shared object maps (`so_map`), symbol-with-size entries (`nzlist`), section dispatch tables, RRS hash buckets, runtime symbols, and debugger interface state.

`struct _dynamic` describes the dynamic-linking interface, with version constants for Sun and BSD formats and macros to access GOT, PLT, relocation, symbol, hash, string, needed-object, and path sections plus their sizes.

It also defines ld.so entry points (`ld_entry`), crt0-to-rtld handoff (`crt_ldso`) and versions, hints-file header/bucket formats, maximum Dewey version components, bad-magic check, and the legacy hints path `/var/run/ld.so.hints`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/link_aout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/link_elf.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/link_elf.h

Defines ELF runtime linker/debugger public structures and helper prototypes. It includes `sys/elf.h`, search-origin flags for `Dl_serinfo`, and the `Link_map` structure representing loaded shared objects.

`struct r_debug` is the debugger rendezvous state with loaded-image map, breakpoint callback, add/delete/consistent state, and rtld base. `struct dl_phdr_info` is the callback payload for iterating program headers and includes relocation base, module name, phdr pointer/count, load/unload counters, and TLS metadata.

Exports `dl_iterate_phdr`, `_rtld_addr_phdr`, `_rtld_get_stack_prot`, `_rtld_is_dlopened`, and rtld variable get/set helpers, with ARM EABI unwind index lookup where applicable.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/link_elf.h -->