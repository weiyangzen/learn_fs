# Group Research: group_600_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__839c74dfe1de

Scope checked against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb2312.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb2312.h

## Purpose
Provides the kernel iconv mapping table for converting UTF-8 encoded code points to GB2312 byte values.

## Main Interfaces
- `KICONV_UTF8_GB2312_MAX`: declares the maximum mapping count as `7451`.
- `kiconv_utf8_gb2312[]`: static `kiconv_table_t` table, available only under `_KERNEL`.
- Entries encode UTF-8 byte sequences as packed integer keys and GB2312 byte pairs as integer values.
- Includes a fallback-style first entry mapping `0x0000` to `0x003F`.

## Dependencies And Relationships
This header assumes `kiconv_table_t` has already been defined by the including kernel conversion code. It is a generated/static data asset consumed by the kernel character conversion subsystem rather than a standalone API.

## Research Notes
The file is almost entirely data. It carries both CDDL/Sun copyright and Unicode data license text, and notes Sun modifications. The table includes punctuation, Greek, Cyrillic, kana, bopomofo, symbols, CJK ideographs, and fullwidth forms covered by the GB2312 mapping.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_gb2312.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kidmap.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kidmap.h

## Purpose
Defines the kernel API for mapping Windows SIDs to Solaris UIDs/GIDs and back, including single-request and batched lookup flows.

## Main Interfaces
- `idmap_get_handle_t`: opaque batch lookup handle.
- `idmap_stat`: 32-bit status type.
- Direct lookups:
  - `kidmap_getuidbysid()`
  - `kidmap_getgidbysid()`
  - `kidmap_getpidbysid()`
  - `kidmap_getsidbyuid()`
  - `kidmap_getsidbygid()`
- Batch lifecycle:
  - `kidmap_get_create()`
  - `kidmap_batch_get*()`
  - `kidmap_get_mappings()`
  - `kidmap_get_destroy()`
- Door/cache support:
  - `idmap_reg_dh()`
  - `idmap_unreg_dh()`
  - `idmap_get_door()`
  - `idmap_purge_cache()`

## Dependencies And Relationships
Includes `sys/idmap.h`, `sys/door.h`, and `sys/zone.h`. Every mapping call is zone-aware via `zone_t *`, and daemon communication is represented through door handles.

## Research Notes
The SID representation is split into a string SID prefix and integer RID. Returned SID prefix pointers refer to internal storage and must not be modified or freed by callers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kidmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klpd.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klpd.h

## Purpose
Defines kernel/user packet formats and kernel-private entry points for kernel-level privilege daemon calls and `pfexec` privilege policy checks.

## Main Interfaces
- Protocol/version constants:
  - `KLPDCALL_VERS`
  - `KLPDARG_*` argument type constants for vnode, integer, and port arguments.
- Kernel-only APIs:
  - `klpd_reg()`, `klpd_unreg()`
  - `klpd_call()`
  - `klpd_freelist()`, `klpd_rele()`
  - credential-held KLPD references via `crklpd_hold()`/`crklpd_rele()`
  - `pfexec_reg()`, `pfexec_unreg()`, `pfexec_call()`
  - `get_forced_privs()`, `check_user_privs()`
- Packet structures:
  - `klpd_head_t`
  - `klpd_arg_t`
  - `pfexec_arg_t`
  - `pfexec_reply_t`
- Offset helpers:
  - `KLH_PRIVSET()`
  - `KLH_ARG()`
  - `PFEXEC_REPLY_IPRIV()`
  - `PFEXEC_REPLY_LPRIV()`

## Dependencies And Relationships
Uses privilege sets, credentials, process-set IDs, pathnames, and variable argument lists. The packet structures are ABI-like layouts shared with daemon or syscall-facing code.

## Research Notes
Most variable-size data is addressed by offsets inside packed buffers, so callers must preserve buffer layout and alignment expectations. `pfexec_reply_t` can return credential changes, environment-scrub policy, authorization status, and initial/limit privilege sets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klpd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klwp.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klwp.h

## Purpose
Defines the kernel light-weight process object, per-LWP resource accounting, syscall state, signal/debugger state, timers, contracts, and LWP-global kernel symbols.

## Main Interfaces
- `MAXSYSARGS`: maximum syscall arguments saved per LWP.
- End-of-syscall values:
  - `NORMALRETURN`
  - `JUSTRETURN`
- `struct lrusage`: per-LWP and per-process resource counters.
- `klwp_id_t`: pointer typedef for `_klwp`.
- `klwp_t`: full LWP state structure.
- LWP states:
  - `LWP_USER`
  - `LWP_SYS`
- Kernel symbols under `_KERNEL`:
  - `lwp_default_stksize`
  - `lwp_reapcnt`
  - `lwp_deathrow`
  - `reaplock`
  - `lwp_cache`
  - `segkp_lwp`
  - `lwp0`
  - `lwp_rtt()`

## Dependencies And Relationships
Includes thread, signal, PCB, microstate accounting, ucontext, LWP, and contract headers. It is tightly coupled with `kthread_t`, `proc`, signal delivery, `/proc`, profiling, syscall entry/exit, and contract templates.

## Research Notes
Microstate current state is kept in the thread, while per-LWP accounting arrays live here. The watchpoint array has four slots for exec/write/read/read cases, and syscall arguments are saved inline for restart/inspection paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/klwp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmdb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmdb.h

## Purpose
Defines control constants and kernel-control entry points for loading, unloading, and activating the kernel debugger `kmdb`.

## Main Interfaces
- Ioctl constants:
  - `KMDB_IOC`
  - `KMDB_IOC_START`
  - `KMDB_IOC_STOP`
- Activation flags:
  - `KMDB_F_AUTO_ENTRY`
  - `KMDB_F_TRAP_NOSWITCH`
  - `KMDB_F_DRV_DEBUG`
- Kernel control functions:
  - `kctl_attach()`
  - `kctl_detach()`
  - `kctl_get_state()`
  - `kctl_modload_activate()`
  - `kctl_deactivate()`
- `kctl_boot_activate_f`: boot-time activation callback type.

## Dependencies And Relationships
Includes `sys/modctl.h` and forward-declares `struct bootops`. Used by kmdb control-device and boot/module activation paths.

## Research Notes
The public surface is intentionally small: it is a control-plane header for debugger lifecycle transitions, not the debugger implementation itself.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem.h

## Purpose
Defines the kernel memory allocator client API, allocation flags, cache allocator API, and move-callback response types.

## Main Interfaces
- Allocation flags:
  - `KM_SLEEP`
  - `KM_NOSLEEP`
  - `KM_PANIC`
  - `KM_PUSHPAGE`
  - `KM_NORMALPRI`
  - `KM_NOSLEEP_LAZY`
  - `KM_VMFLAGS`
  - `KM_FLAGS`
- Basic allocator APIs:
  - `kmem_alloc()`
  - `kmem_zalloc()`
  - `kmem_free()`
  - `kmem_alloc_tryhard()`
  - `kmem_rezalloc()`
- Dump helpers:
  - `kmem_dump_init()`
  - `kmem_dump_begin()`
  - `kmem_dump_finish()`
- Cache flags:
  - `KMC_NOTOUCH`
  - `KMC_NODEBUG`
  - `KMC_NOMAGAZINE`
  - `KMC_NOHASH`
  - `KMC_QCACHE`
  - `KMC_KMEM_ALLOC`
  - `KMC_IDENTIFIER`
  - `KMC_PREFILL`
- `kmem_cache_t`: opaque cache type.
- `kmem_cbrc_t`: object move callback result enum.
- Cache APIs:
  - `kmem_cache_create()`
  - `kmem_cache_set_move()`
  - `kmem_cache_destroy()`
  - `kmem_cache_alloc()`
  - `kmem_cache_free()`
  - `kmem_cache_stat()`
  - `kmem_cache_reap_active()`
  - `kmem_cache_reap_soon()`
  - `kmem_cache_move_notify()`

## Dependencies And Relationships
Includes `sys/types.h` and `sys/vmem.h`. Kernel declarations are visible under `_KERNEL` or `_FAKE_KERNEL`.

## Research Notes
This is the stable allocator-facing header; implementation details are intentionally opaque. `POINTER_IS_VALID()` and `POINTER_INVALIDATE()` support clients implementing move callbacks by detecting kmem scribbles in freed memory.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem_impl.h

## Purpose
Defines private implementation structures and constants for the illumos slab/magazine kernel memory allocator.

## Main Interfaces
- Debug flags:
  - `KMF_AUDIT`
  - `KMF_DEADBEEF`
  - `KMF_REDZONE`
  - `KMF_CONTENTS`
  - `KMF_STICKY`
  - `KMF_NOMAGAZINE`
  - `KMF_FIREWALL`
  - `KMF_LITE`
  - `KMF_HASH`
  - `KMF_RANDOMIZE`
  - `KMF_DUMPDIVERT`
  - `KMF_DUMPUNSAFE`
  - `KMF_PREFILL`
- Debug patterns:
  - `KMEM_FREE_PATTERN`
  - `KMEM_UNINITIALIZED_PATTERN`
  - `KMEM_REDZONE_PATTERN`
  - `KMEM_REDZONE_BYTE`
- Size encoding helpers:
  - `KMEM_SIZE_ENCODE()`
  - `KMEM_SIZE_DECODE()`
  - `KMEM_SIZE_VALID()`
- Core structures:
  - `kmem_bufctl_t`
  - `kmem_bufctl_audit_t`
  - `kmem_buftag_t`
  - `kmem_buftag_lite_t`
  - `kmem_slab_t`
  - `kmem_magazine_t`
  - `kmem_magtype_t`
  - `kmem_cpu_cache_t`
  - `kmem_maglist_t`
  - `kmem_defrag_t`
  - `kmem_dump_t`
  - `struct kmem_cache`
  - `kmem_log_header_t`
  - `kmem_move_t`
- Addressing/layout helpers:
  - `KMEM_BUFTAG()`
  - `KMEM_BUFCTL()`
  - `KMEM_BUF()`
  - `KMEM_SLAB()`
  - `KMEM_CPU_CACHE()`
  - `KMEM_HASH()`
  - `KMEM_IS_MOVABLE()`

## Dependencies And Relationships
Includes allocator, vmem, thread/lock, kstat, CPU, page, AVL, and list headers. This header is consumed by allocator implementation and diagnostic code, not ordinary drivers.

## Research Notes
The file documents allocator lock order: cache lock, CPU cache locks by CPU ID, then depot lock. Per-CPU magazine caches are padded to `KMEM_CPU_CACHE_SIZE` for alignment/cache behavior. Defragmentation state tracks move callbacks, pending moves, dead slab lists, and client misuse checks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kmem_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj.h

## Purpose
Defines the public/private kernel runtime linker object model, module metadata, kobj file-buffer helpers, symbol lookup APIs, and kobj memory/text allocation hooks.

## Main Interfaces
- `struct module_list`: linked list of module dependencies.
- `hotinline_desc_t`: hot-inline call descriptor.
- `symid_t`, `reloc_dest_t`, `module_mach`: symbol and relocation-related typedefs.
- `struct module`: loaded module record with ELF headers, sections, symbols, text/data/bss, dependencies, CTF, SDT, FBT, signature, and machine-specific data.
- `struct kobj_mem`: memory allocation tracking node.
- `struct _buf`: kobj file buffer state.
- `kobj_stat_t`: allocation/free counters.
- File buffer macros:
  - `kobj_getc()`
  - `kobj_ungetc()`
  - `B_OFFSET()`
  - `F_PAGE()`
  - `F_BLKS()`
- Kernel APIs:
  - module load/unload and lookup functions
  - symbol lookup and symbol name resolution
  - kobj file open/read/close/stat helpers
  - kobj allocation/free helpers
  - CTF and hot-inline setup
  - kobj virtual memory/text allocation
  - text window allocation/free
  - `kobj_printf()`

## Dependencies And Relationships
Includes module control, ELF, machine ELF, vmem, SDT, bootstat, and types headers. `struct module` is the central loaded-module representation used by krtld, module loading, symbol export, tracing metadata, and debugger/symbol consumers.

## Research Notes
The header is shared by early boot/runtime linker code and kernel module support. Architecture support is explicitly limited to i386, sparc, and amd64 for `kobj_vmem_init()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_impl.h

## Purpose
Defines implementation-private interfaces for the kernel runtime linker/loader, including boot auxiliary attributes, module flags, notification hooks, allocation flags, early-boot vector overrides, and relocation/export routines.

## Main Interfaces
- Boot attribute constants:
  - `BA_DYNAMIC` through `BA_NUM`
- `val_t`: boot auxiliary value/pointer union.
- `struct proginfo`: segment size/alignment descriptor.
- Module flags:
  - `KOBJ_EXEC`
  - `KOBJ_INTERP`
  - `KOBJ_PRIM`
  - `KOBJ_RESOLVED`
  - `KOBJ_RELOCATED`
  - `KOBJ_NOPARENTS`
  - `KOBJ_IGNMULDEF`
  - `KOBJ_NOKSYMS`
  - `KOBJ_EXPORTED`
- Notification support:
  - `kobj_notify_f`
  - `kobj_notify_list_t`
  - `KOBJ_NOTIFY_MODLOADING`
  - `KOBJ_NOTIFY_MODUNLOADING`
  - `KOBJ_NOTIFY_MODLOADED`
  - `KOBJ_NOTIFY_MODUNLOADED`
- Allocation flags:
  - `KM_WAIT`
  - `KM_NOWAIT`
  - `KM_TMP`
  - `KM_SCRATCH`
- Core functions:
  - `kobj_init()`
  - `kobj_notify_add()`
  - `kobj_notify_remove()`
  - `do_relocations()`
  - `do_relocate()`
  - `kobj_mod_alloc()`
  - `kobj_hash_name()`
  - `kobj_segbrk()`
  - `kobj_lookup_kernel()`
  - `kobj_export_module()`
  - `kobj_load_primary_module()`
  - link-map helpers `kobj_lm_append()`, `kobj_lm_lookup()`, `kobj_lm_dump()`

## Dependencies And Relationships
Includes `sys/kdi.h`, `sys/kobj.h`, and varargs support. It exposes early boot hooks, bootops, kmdb argv, kernel debugger interface data, and standalone vector setup/restore.

## Research Notes
Under `KOBJ_OVERRIDES`, early kobj code redirects `bcopy`, `bzero`, and `strlcat` to kobj-managed function pointers until the kernel is fully linked. `KOBJ_LM_PRIMARY` and `KOBJ_LM_DEBUGGER` distinguish primary and debugger link maps.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_lex.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_lex.h

## Purpose
Defines the small lexer interface used by selected kernel modules to parse on-disk system files through kobj file buffers.

## Main Interfaces
- Character classification macros:
  - `isunary()`
  - `iswhite()`
  - `isnewline()`
  - `isalphanum()`
  - `isnamechar()`
- `token_t`: token enum covering punctuation, whitespace, EOF, strings, numeric values, and names.
- Debug-only `tokennames[]`.
- Parser helpers:
  - `kobj_get_string()`
  - `kobj_free_string()`
  - `kobj_getvalue()`
  - `kobj_file_err()`
  - `kobj_lex()`
  - `kobj_find_eol()`

## Dependencies And Relationships
Includes `sys/ctype.h` and uses `struct _buf` from kobj file handling. It is intended for a few kernel modules, not broad general kernel parsing.

## Research Notes
String helper ownership is explicit: strings returned through `kobj_get_string()` must be released with `kobj_free_string()`. `kobj_file_err()` includes file context and prints through kernel error reporting.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj_lex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksensor_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksensor_impl.h

## Purpose
Defines implementation glue for the kernel sensor subsystem.

## Main Interfaces
- `ksensor_init()`: initializes the subsystem.
- Operation vectors:
  - `ksensor_op_kind()`
  - `ksensor_op_scalar()`
- Callback types:
  - `ksensor_create_f`
  - `ksensor_remove_f`
- Registration APIs:
  - `ksensor_register()`
  - `ksensor_unregister()`

## Dependencies And Relationships
Includes `sys/sensors.h` for public sensor ioctl structures and device types. Registration is keyed by `dev_info_t *`.

## Research Notes
This is a small internal header connecting sensor providers to central ksensor device operations. It separates provider registration callbacks from ioctl operation handlers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksensor_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksocket.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksocket.h

## Purpose
Defines the opaque kernel socket API, callback events, callback registration structure, socket operation wrappers, reference management, and direct receive callback support.

## Main Interfaces
- `ksocket_t`: opaque kernel socket handle.
- Callback flag bits:
  - `KSOCKET_CB_CONNECTED`
  - `KSOCKET_CB_CONNECTFAILED`
  - `KSOCKET_CB_DISCONNECTED`
  - `KSOCKET_CB_NEWDATA`
  - `KSOCKET_CB_NEWCONN`
  - `KSOCKET_CB_CANSEND`
  - `KSOCKET_CB_OOBDATA`
  - `KSOCKET_CB_CANTSENDMORE`
  - `KSOCKET_CB_CANTRECVMORE`
  - `KSOCKET_CB_ERROR`
- `ksocket_callback_event_t`: callback event enum.
- `ksocket_callback_t`, `ksocket_callbacks_t`: callback declarations and vector.
- Socket APIs:
  - `ksocket_socket()`, `ksocket_bind()`, `ksocket_listen()`, `ksocket_accept()`, `ksocket_connect()`
  - send/receive variants including `sendmsg`, `sendmblk`, `recvmsg`
  - socket option, name, ioctl, poll, shutdown, callback, close functions
  - `ksocket_hold()`, `ksocket_rele()`
- Direct receive:
  - `ksocket_krecv_f`
  - `ksocket_krecv_set()`
  - `ksocket_krecv_unblock()`

## Dependencies And Relationships
Avoids directly including STREAMS by forward-declaring `struct msgb`; it also forward-declares `struct nmsghdr`. All operations take credentials where required.

## Research Notes
The direct receive mode bypasses sockfs buffering: the callback must consume all delivered data and returns a boolean indicating whether lower layers may continue or must apply backpressure.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksocket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstat.h

## Purpose
Defines the kernel statistics ABI, `/dev/kstat` ioctls, kstat header structure, data type layouts, flags, snapshot/update semantics, I/O queue accounting helpers, timer statistics, and kernel creation/deletion APIs.

## Main Interfaces
- `kid_t`: unique kstat ID type.
- Ioctls:
  - `KSTAT_IOC_CHAIN_ID`
  - `KSTAT_IOC_READ`
  - `KSTAT_IOC_WRITE`
- `kstat_t`: generic kstat header and kernel-private callbacks.
- 32-bit ABI form under `_SYSCALL32`: `kstat32_t`.
- Kernel locking/callback macros:
  - `KSTAT_ENTER()`
  - `KSTAT_EXIT()`
  - `KSTAT_UPDATE()`
  - `KSTAT_SNAPSHOT()`
- Kstat types:
  - `KSTAT_TYPE_RAW`
  - `KSTAT_TYPE_NAMED`
  - `KSTAT_TYPE_INTR`
  - `KSTAT_TYPE_IO`
  - `KSTAT_TYPE_TIMER`
- Flags:
  - `KSTAT_FLAG_VIRTUAL`
  - `KSTAT_FLAG_VAR_SIZE`
  - `KSTAT_FLAG_WRITABLE`
  - `KSTAT_FLAG_PERSISTENT`
  - `KSTAT_FLAG_DORMANT`
  - `KSTAT_FLAG_INVALID`
  - `KSTAT_FLAG_LONGSTRINGS`
- Data structures:
  - `kstat_named_t`
  - `kstat_intr_t`
  - `kstat_io_t`
  - `kstat_timer_t`
- Kernel APIs:
  - creation/install/delete functions
  - named/timer initialization
  - I/O queue transition helpers
  - timer start/stop helpers
  - zone add/remove/find
  - hold/release by KID or name

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, and under kernel builds `sys/t_lock.h`. Kstats are exposed to userland through `/dev/kstat` while providers initialize and update data in kernel.

## Research Notes
The comments are part of the contract: variable-size kstats must be virtual and locked, snapshots copy data into wired kernel buffers, and long string named kstats require special buffer layout. I/O statistics use accumulated time and length-time products maintained only through helper functions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstr.h

## Purpose
Defines kernel STREAMS helper operations for opening streams, pushing/popping modules, linking, messaging, ioctls, close, and autopush configuration.

## Main Interfaces
- Autopush operation constants:
  - `SET_AUTOPUSH`
  - `GET_AUTOPUSH`
  - `CLR_AUTOPUSH`
- STREAMS helper APIs:
  - `kstr_open()`
  - `kstr_plink()`
  - `kstr_unplink()`
  - `kstr_push()`
  - `kstr_pop()`
  - `kstr_close()`
  - `kstr_ioctl()`
  - `kstr_msg()`
  - `kstr_autopush()`

## Dependencies And Relationships
Includes `sys/stream.h`, using STREAMS types such as `vnode_t`, `mblk_t`, and `timestruc_t`. This is a kernel interface to STREAMS plumbing operations.

## Research Notes
`kstr_autopush()` operates over major/minor ranges and an array of module names, making this header part of STREAMS configuration machinery as well as runtime stream manipulation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksyms.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksyms.h

## Purpose
Defines kernel symbol snapshot support for the `ksyms` subsystem.

## Main Interfaces
- Under `_KERNEL`:
  - `ksyms_lock`: reader/writer lock protecting ksyms state.
  - `ksyms_arena`: vmem arena for symbol storage/export.
  - `ksyms_snapshot()`: copies a snapshot through a caller-supplied copy callback.

## Dependencies And Relationships
Includes `sys/kobj.h`, tying ksyms to the kernel runtime linker/module symbol model and vmem infrastructure.

## Research Notes
The copy callback signature lets snapshot code abstract the destination, such as kernel buffer copying or userland-oriented copying.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksyms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksynch.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksynch.h

## Purpose
Provides the DKI/DDI-specified synchronization-primitives include point.

## Main Interfaces
- Includes `sys/t_lock.h`.

## Dependencies And Relationships
This file exists because the DKI/DDI specifies its presence. Actual synchronization primitive definitions come from `sys/t_lock.h`.

## Research Notes
There are no independent types or functions here. Its role is compatibility and standard include naming.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ksynch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest.h

## Purpose
Defines the ktest userspace ioctl ABI and the kernel module test registration/result API hidden behind `_KERNEL`.

## Main Interfaces
- Naming and serialization constants:
  - `KTEST_SEPARATOR`
  - `KTEST_DEF_TRIPLE`
  - `KTEST_MAX_NAME_LEN`
  - `KTEST_MAX_TRIPLE_LEN`
  - `KTEST_MAX_LOG_LEN`
  - nvlist key strings
  - `KTEST_SER_FMT_VSN`
- Safety limit:
  - `KTEST_IOCTL_MAX_LEN`
- Ioctls:
  - `KTEST_IOCTL_RUN_TEST`
  - `KTEST_IOCTL_LIST_TESTS`
- Enums:
  - `ktest_test_flags_t`
  - `ktest_result_type_t`
- ABI structures:
  - `ktest_result_t`
  - `ktest_run_op_t`
  - `ktest_list_op_t`
- Kernel-only opaque handles:
  - `ktest_module_hdl_t`
  - `ktest_suite_hdl_t`
  - `ktest_test_hdl_t`
  - `ktest_ctx_hdl_t`
- Kernel module API:
  - module/suite/test creation and registration
  - module hold/release and symbol lookup helpers
  - input retrieval
  - result and message helpers
- Test macros:
  - `KT_PASS`, `KT_FAIL`, `KT_ERROR`, `KT_SKIP`
  - assertion macros for signed, unsigned, pointer, boolean, and zero checks
  - goto variants
  - error-result assertion variants

## Dependencies And Relationships
Includes DDI, module-control, param, and type headers. The header explicitly owns both ioctl ABI and in-kernel ktest module ABI.

## Research Notes
Assertion macros record source line numbers and return or jump on failure. The distinction between fail and error is encoded in separate result helpers and macro families. Input-bearing tests are marked with `KTEST_FLAG_INPUT`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest_impl.h

## Purpose
Defines private in-kernel data structures for the ktest facility.

## Main Interfaces
- Under `_KERNEL`:
  - `ktest_module_t`: module list node, name, suite/test counts, and suite list.
  - `ktest_suite_t`: suite list node, owning module, name, test count, and test list.
  - `ktest_test_t`: test list node, owning suite, name, function pointer, and input requirement flag.
  - `ktest_ctx_t`: runtime context with test pointer, result pointer, input buffer, and input length.

## Dependencies And Relationships
Includes `sys/ktest.h`, `sys/list.h`, and `sys/types.h`. It should only be used by the ktest implementation, not by userspace or test modules.

## Research Notes
The file explicitly states that external consumers should use `sys/ktest.h`. These structures back the opaque handles exposed in the public ktest header.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ldterm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ldterm.h

## Purpose
Defines STREAMS line-discipline terminal state, buffer sizing, flow-control thresholds, EUC/PCCS/UTF-8 codeset metadata, display-width helpers, and internal state flags for `ldterm`.

## Main Interfaces
- Buffer and flow-control constants:
  - `IBSIZE`, `OBSIZE`, `EBSIZE`
  - `TTXOLO`, `TTXOHI`, `HIWAT`, `LOWAT`, `LDCHUNK`
- Mode helpers:
  - `V_MIN`
  - `V_TIME`
  - `RAW_MODE`
  - `CANON_MODE`
- EUC/codeset constants:
  - `EUCSIZE`, `EUCIN`, `EUCOUT`
  - special display widths such as `EUC_TWIDTH`, `EUC_BSWIDTH`, `UNKNOWN_WIDTH`
  - `LDTERM_DATA_VERSION`
  - `LDTERM_CS_TYPE_EUC`, `LDTERM_CS_TYPE_PCCS`, `LDTERM_CS_TYPE_UTF8`
  - `LDTERM_CS_MAX_BYTE_LENGTH`
  - `LDTERM_CS_MAX_CODESETS`
- UTF-8 range and decoding constants for Unicode planes, CJK extension ranges, variation selectors, and bit extraction.
- Data structures:
  - `ldterm_eucpc_data_t`
  - `ldterm_cs_data_user_t`
  - `ldterm_cs_data_t`
  - `ldterm_unicode_data_cell_t`
  - `ldterm_cs_methods_t`
  - `ldtermstd_state_t`
- State flags:
  - `TS_XCLUDE`
  - `TS_TTSTOP`
  - `TS_TBLOCK`
  - `TS_QUOT`
  - `TS_ERASE`
  - `TS_SLNCH`
  - `TS_PLNCH`
  - `TS_TTCR`
  - `TS_NOCANON`
  - `TS_RESCAN`
  - `TS_MREAD`
  - `TS_FLUSHWAIT`
  - `TS_MEUC`
  - `TS_WARNED`
  - `TS_CLOSE`
  - `TS_IOCWAIT`
  - `TS_IFBLOCK`
  - `TS_OFBLOCK`
  - `TS_ISPTSTTY`

## Dependencies And Relationships
Uses terminal/STREAMS types such as `termios`, `mblk_t`, `eucioc_t`, buffer-call IDs, and timeout IDs from surrounding kernel headers included by implementation files. It is the shared state contract for the `ldterm` line discipline implementation.

## Research Notes
The comments warn that codeset type values and `LDTERM_CS_TYPE_MAX` must be updated sequentially with `LDTERM_DATA_VERSION`. `ldtermstd_state_t` contains both classic terminal modes/state and multibyte character tracking, including EUC width arrays and non-EUC scratch/callback data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ldterm.h -->