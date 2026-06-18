# subset-b-005751 Research

Grouped research for the subset B work item. Each section preserves the source path in its title and is bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/super.c -->
## sources/distributed-fs/ceph-client/fs/romfs/super.c

Purpose: implements the ROMFS VFS driver for block and MTD-backed read-only ROM filesystem images. It wires the filesystem type, mount context, superblock parsing, inode allocation, directory lookup, directory iteration, and file data reads around the ROMFS on-media structures declared in `internal.h`.

Important APIs and types: `romfs_fs_type`, `romfs_context_ops`, `romfs_super_ops`, `romfs_dir_operations`, `romfs_dir_inode_operations`, `romfs_aops`, and the slab-backed `romfs_inode_info` cache are the main integration points. `romfs_iget()` is the central inode constructor; `romfs_read_folio()` is the page-cache read path; `romfs_readdir()` and `romfs_lookup()` walk directory file-header chains; `romfs_fill_super()` validates the image and installs the root dentry.

Control flow: module init creates `romfs_inode_cachep` and registers `romfs`. Mounting calls `romfs_init_fs_context()`, `romfs_get_tree()`, then either `get_tree_mtd()` or `get_tree_bdev()`. `romfs_fill_super()` sets read-only superblock properties, reads the first 512 bytes, validates magic, image size, and checksum, derives the root inode offset from the volume name length, calls `romfs_iget()`, and builds `s_root`. Lookup and readdir repeatedly use `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()` to follow `next` pointers and resolve hard-link file headers.

State and persistence: all persistent state is on the ROMFS image. Runtime state is limited to `s_fs_info` holding the image size, inode private offsets (`i_metasize`, `i_dataoffset`), page-cache folios, and the inode slab. The filesystem is forced `SB_RDONLY | SB_NOATIME`; reconfigure synchronizes and reasserts read-only.

Dependencies and integration: depends on VFS mount/context APIs, page cache, block and MTD helpers, dcache lookup, generic read-only file ops, special inode setup, endian conversion, and ROMFS device access helpers. `romfs_kill_sb()` must release MTD or block-device references matching the selected mount path.

Risks: malformed images can create long or looping directory chains; the code bounds traversal by `romfs_maxsize()` but checksum verification only covers the initial header. `romfs_iget()` notes that per-file checksum validation is not done. Directory names use a fixed `ROMFS_MAXFN` stack buffer. Error mapping in `romfs_readdir()` returns `0` after read errors, matching legacy directory iteration behavior but reducing observability.

Test signals: mount valid and invalid ROMFS images on both block and MTD configurations, verify checksum rejection, root offset derivation, hard-link resolution, symlink readback, special inode device numbers, executable bit propagation, short reads in `romfs_read_folio()`, `statfs` fields, and read-only remount behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/romfs/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/select.c -->
## sources/distributed-fs/ceph-client/fs/select.c

Purpose: provides the Linux `select(2)`, `pselect(2)`, `poll(2)`, and `ppoll(2)` implementations, including timeout accounting, restart behavior, wait-queue registration, busy-poll support, and compat syscall variants.

Important APIs and types: exported helpers include `poll_initwait()`, `poll_freewait()`, `poll_select_set_timeout()`, `select_estimate_accuracy()`, and `core_sys_select()`. Internal structures include `poll_table_page`, `fd_set_bits`, `poll_list`, `sigset_argpack`, and compat equivalents. Syscall entry points are declared with `SYSCALL_DEFINE*` and `COMPAT_SYSCALL_DEFINE*`.

Control flow: `poll_initwait()` prepares a `poll_wqueues` object whose `_qproc` is `__pollwait()`. `do_select()` validates requested fd sets with `max_select_fd()`, then loops over fd bits, calls `vfs_poll()`, records ready bits, optionally busy loops for network sockets, and sleeps through `poll_schedule_timeout()` until events, timeout, signal, or allocation error. `core_sys_select()` copies user fd sets into six bitmaps, invokes `do_select()`, and copies result sets back. `do_sys_poll()` copies `pollfd` arrays into a stack/page linked list, calls `do_poll()`, and writes `revents` back.

State and persistence: state is per syscall. Wait-queue entries hold file references and are freed by `poll_freewait()`. Timeout state is absolute `timespec64` plus syscall restart metadata in `current->restart_block` for `poll`. Signal-mask changes for `pselect` and `ppoll` are restored in `poll_select_finish()`.

Dependencies and integration: integrates with file descriptor tables under RCU, `vfs_poll()` implementations, wait queues, hrtimers, scheduler/freezer state, signal mask helpers, compat bitmap conversion, `copy_from_user()`/`copy_to_user()`, and `net_busy_loop` hooks.

Risks: concurrency depends on barriers between `pollwake()` and `poll_schedule_timeout()`; changing those paths can reintroduce lost wakeups. Large fd sets can allocate substantial memory, and compat select uses a parallel implementation that can drift. Timeout update behavior is ABI-sensitive, including `STICKY_TIMEOUTS`, read-only timeout pointers, and restart conversion from `-ERESTARTNOHAND`.

Test signals: exercise zero, finite, and infinite timeouts; signal interruptions and restart paths; invalid fd detection; high `nfds` with page-backed `poll_list`; compat 32-bit select/poll; pselect/ppoll mask restore; busy-poll sockets; writable timeout faults; and driver poll callbacks that return event masks before or after wait registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/select.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/seq_file.c -->
## sources/distributed-fs/ceph-client/fs/seq_file.c

Purpose: implements the generic `seq_file` framework used by procfs, debugfs, sysfs-like diagnostics, and many kernel virtual files to render record sequences safely through read and seek operations.

Important APIs and types: exported interfaces include `seq_open()`, `seq_read()`, `seq_read_iter()`, `seq_lseek()`, `seq_release()`, formatting helpers such as `seq_printf()`, `seq_write()`, `seq_put_decimal_*()`, path helpers, `single_open()`/private variants, and list/hlist/per-cpu iteration helpers. `seq_file_cache` provides slab allocation for `struct seq_file`.

Control flow: `seq_open()` allocates and attaches `struct seq_file` to `file->private_data`. Reads enter `seq_read_iter()`, lock `m->lock`, allocate a buffer lazily, use `start/show/next/stop` callbacks to fill records, grow the buffer on overflow, copy buffered bytes to the user iterator, and maintain `read_pos`, `index`, `count`, and `from`. `traverse()` reconstructs iterator position for seeks and preads. `seq_lseek()` uses `traverse()` for non-current offsets.

State and persistence: all state is per open file: mutex, callback table, buffer, buffer size, current record index, read position, private pointer, and partial-copy offsets. There is no persistent storage. Single-file helpers allocate a synthetic `seq_operations` table and optionally per-open private data.

Dependencies and integration: depends on VFS file operations, `iov_iter`, slab/vmalloc allocation, dcache path rendering, string escaping, hex dump helpers, list/RCU traversal primitives, and callers obeying `seq_operations` contracts.

Risks: buggy `.next()` methods that do not advance position are detected and rate-limited, but callers can still produce duplicate or skipped output. Unbounded record size can drive repeated buffer doubling up to `MAX_RW_COUNT`. RCU iteration helpers require callers to hold `rcu_read_lock()`. Path rendering and escape helpers must handle overflow through `seq_commit()` and `seq_has_overflowed()`.

Test signals: validate partial reads, pread after sequential reads, lseek to arbitrary offsets, buffer growth, `SEQ_SKIP`, callback errors, empty records, position-stable `.next()` warnings, `single_open_size()`, private-data release, list/hlist helper ordering, RCU helper usage under lockdep, and overflow behavior for formatting helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/seq_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/signalfd.c -->
## sources/distributed-fs/ceph-client/fs/signalfd.c

Purpose: implements `signalfd(2)` and `signalfd4(2)`, exposing pending signals selected by a mask as fixed-size `struct signalfd_siginfo` records readable from an anonymous inode file descriptor.

Important APIs and types: `struct signalfd_ctx` stores the inverted internal signal mask. Key functions are `do_signalfd4()`, `signalfd_read_iter()`, `signalfd_dequeue()`, `signalfd_poll()`, `signalfd_copyinfo()`, `signalfd_cleanup()`, and compat syscall wrappers.

Control flow: user syscalls copy a `sigset_t`, reject unexpected mask sizes or flags, remove uncatchable `SIGKILL`/`SIGSTOP`, invert the mask for kernel signal helpers, and either create a new anon inode or update an existing signalfd. Reads require at least one full `signalfd_siginfo`, repeatedly dequeue matching signals, translate `kernel_siginfo_t` by layout class, and copy records to the iterator. Blocking reads attach a wait entry to `current->sighand->signalfd_wqh` while holding `siglock` around dequeue checks.

State and persistence: per-fd state is only the signal mask in `signalfd_ctx`; pending signal queues remain task and thread-group state. Polling waits on the current task's `sighand` waitqueue rather than a persistent object-specific queue. `/proc` fdinfo renders the user-visible mask.

Dependencies and integration: uses anonymous inode files, signal dequeue/layout helpers, task sighand locking, wait queues, `iov_iter`, proc fdinfo, compat sigset conversion, and `O_CLOEXEC`/`O_NONBLOCK` flag ABI equivalence.

Risks: signalfd is tied to the current task at read/poll time, so behavior around shared file descriptors and task signal handlers is subtle. Mask inversion must stay consistent with signal core expectations. Copying siginfo requires updating when `siginfo_t` layouts evolve; the fixed 128-byte ABI is enforced by `BUILD_BUG_ON`.

Test signals: create and update signalfds, verify invalid flags and sizes, block vs nonblock reads, multiple records per read, signal mask exclusion of SIGKILL/SIGSTOP, `poll()` readiness, shared pending versus thread pending delivery, compat syscalls, fdinfo `sigmask`, and signal interruption returning restartable errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/signalfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Kconfig -->
## sources/distributed-fs/ceph-client/fs/smb/Kconfig

Purpose: top-level SMB filesystem Kconfig menu fragment. It pulls in client, server, and SMB Direct configuration and defines aggregate SMB infrastructure symbols.

Important APIs and symbols: `source "fs/smb/client/Kconfig"`, `source "fs/smb/server/Kconfig"`, `source "fs/smb/smbdirect/Kconfig"`, `config SMBFS`, and `config SMB_KUNIT_TESTS`.

Control flow: Kconfig includes feature-specific fragments first, then derives `SMBFS` as `y` or `m` when either the CIFS client or SMB server is enabled. `SMB_KUNIT_TESTS` depends on `SMBFS && KUNIT` and defaults to `KUNIT_ALL_TESTS`, acting as a shared test umbrella for SMB code.

State and persistence: no runtime state. Its persistent effect is build configuration, influencing which directories are entered by Kbuild and which conditional code compiles.

Dependencies and integration: integrates with `fs/smb/Makefile`, KUnit, the client Kconfig, server Kconfig, and SMB Direct Kconfig. `SMBFS` is intentionally hidden/tristate infrastructure rather than a user-facing filesystem choice.

Risks: incorrect defaulting of `SMBFS` can omit common SMB code when only client or server is modular. KUnit enablement depends on `SMBFS`, so build matrix coverage needs both client and server combinations.

Test signals: run Kconfig permutations for `CIFS=y/m/n`, `SMB_SERVER=y/m/n`, `SMBDIRECT`, and `KUNIT_ALL_TESTS`; verify `fs/smb/common/` builds whenever needed and SMB KUnit tests appear only when dependencies are satisfied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Makefile -->
## sources/distributed-fs/ceph-client/fs/smb/Makefile

Purpose: top-level Kbuild dispatch for SMB filesystem subdirectories.

Important APIs and variables: `obj-$(CONFIG_SMBFS) += common/`, `obj-$(CONFIG_SMBDIRECT) += smbdirect/`, `obj-$(CONFIG_CIFS) += client/`, and `obj-$(CONFIG_SMB_SERVER) += server/`.

Control flow: Kbuild descends into common, SMB Direct, CIFS client, and server subdirectories depending on the matching Kconfig symbols. The file does not build objects directly.

State and persistence: no runtime state; it defines build graph persistence through Kbuild object lists.

Dependencies and integration: consumes symbols defined by the sibling Kconfig files. It is the bridge between aggregate `SMBFS` and implementation directories.

Risks: directory inclusion must match symbol ownership. A common-code symbol mismatch can produce link failures only in modular combinations.

Test signals: build all-y, all-m, client-only, server-only, and SMB Direct configurations; check that common objects are included for both client and server users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Kconfig -->
## sources/distributed-fs/ceph-client/fs/smb/client/Kconfig

Purpose: defines user-visible and internal configuration for the Linux SMB3/CIFS client module, including security, DFS, witness, xattrs, debugging, RDMA, FS-Cache, root filesystem, compression, and KUnit test options.

Important symbols: `CIFS` is the main tristate and selects networking, NLS, crypto, keyring, DNS, ASN.1/OID, and netfs support. Feature symbols include `CIFS_STATS2`, `CIFS_ALLOW_INSECURE_LEGACY`, `CIFS_UPCALL`, `CIFS_XATTR`, `CIFS_POSIX`, `CIFS_DEBUG`, `CIFS_DEBUG2`, `CIFS_DEBUG_DUMP_KEYS`, `CIFS_DFS_UPCALL`, `CIFS_SWN_UPCALL`, `CIFS_NFSD_EXPORT`, `CIFS_SMB_DIRECT`, `CIFS_FSCACHE`, `CIFS_ROOT`, `CIFS_COMPRESSION`, and `SMB1_KUNIT_TESTS`.

Control flow: options are dependency-gated. Some features select lower-level subsystems, such as `CIFS_SMB_DIRECT` selecting `SMBDIRECT`. `CIFS_ALLOW_INSECURE_LEGACY` controls SMB1 and SMB2.0 availability. `CIFS_UPCALL`, DFS, and SWN options enable user-space upcall integrations.

State and persistence: no runtime state, but selected options shape module contents, exported proc/debug behavior, allowed mount dialects, and security mechanisms.

Dependencies and integration: integrates with crypto API, keyrings/request-key, DNS resolver, ASN.1 parser generation, netfs, fscache, KUnit, and InfiniBand/RDMA.

Risks: defaults matter for security. Legacy dialect support defaults to enabled, while compression defaults disabled. `CIFS_DEBUG_DUMP_KEYS` intentionally exposes encryption keys and must remain clearly unsafe. Broken or overly broad dependencies can create impossible modular builds.

Test signals: build matrix with key feature combinations; confirm `vers=1.0/2.0` rejection when legacy support is disabled; verify SPNEGO/DFS/SWN userspace helper dependencies; run SMB KUnit tests with and without SMB1 support; test modular RDMA and FS-Cache combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Makefile -->
## sources/distributed-fs/ceph-client/fs/smb/client/Makefile

Purpose: Kbuild recipe for the CIFS/SMB2/SMB3 client module and related generated protocol mapping files and tests.

Important variables and rules: `obj-$(CONFIG_CIFS) += cifs.o`; `cifs-y` lists core objects such as transport, inode, file, directory, SMB2 operations, cached directory handles, Unicode conversion, ASN.1 support, and namespace/reparse handling. Conditional `cifs-$(CONFIG_...)` appends xattr, SPNEGO, DFS, SWN, FS-Cache, SMB Direct, rootfs, legacy SMB1, and compression objects. Generated targets include `smb1_mapping_table.c`, `smb1_err_*_map.c`, and `smb2_mapping_table.c`.

Control flow: the build always compiles core client logic when `CONFIG_CIFS` is enabled, then conditionally links feature objects. ASN.1-generated headers gate `asn1.o`. Perl generators convert protocol status headers into C mapping tables under Kbuild dependency tracking. KUnit test objects are compiled separately under SMB test symbols.

State and persistence: no runtime state; generated C files are build artifacts listed in `targets` for cleaning/tracking.

Dependencies and integration: integrates with Kbuild ASN.1 generation, SMB common status headers, feature Kconfig symbols, trace events include path, and KUnit.

Risks: generated mapping tables must be rebuilt when source status headers or generator scripts change. Feature object ordering affects unresolved symbols for conditional code paths. Legacy SMB1 rules are guarded by a non-empty config check, so both `y` and `m` must work.

Test signals: incremental builds after touching `nterr.h`, `smberr.h`, `smb2status.h`, and generators; all feature permutations; module link checks; KUnit test builds; and clean targets removing generated mapping files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/asn1.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/asn1.c

Purpose: glue between the generated SPNEGO NegTokenInit ASN.1 decoder and CIFS session negotiation state. It validates the outer SPNEGO OID and records advertised security mechanisms on `TCP_Server_Info`.

Important APIs: `decode_negTokenInit()` invokes `asn1_ber_decoder()`. `cifs_gssapi_this_mech()` validates the top-level mechanism is `OID_spnego`. `cifs_neg_token_init_mech_type()` handles each advertised mechanism OID and sets `server->sec_mskerberos`, `sec_kerberosu2u`, `sec_kerberos`, `sec_ntlmssp`, or `sec_iakerb`.

Control flow: SMB session setup passes the security blob and server object to `decode_negTokenInit()`. Generated decoder callbacks parse OIDs. Unknown outer OID fails with `-EBADMSG`; unknown inner mechanism OIDs are logged but not fatal, allowing negotiation to continue if a supported mechanism is also present.

State and persistence: state changes are boolean capability flags in the in-memory `TCP_Server_Info`. There is no allocation or persisted data in this file.

Dependencies and integration: depends on `asn1_ber_decoder`, `oid_registry`, generated `cifs_spnego_negtokeninit.asn1.h`, CIFS debug macros, and SMB session negotiation code.

Risks: security mechanism selection depends on accurate OID mapping. Treating unsupported inner mechanisms as non-fatal is flexible but requires later code to reject sessions with no usable mechanism. Blob length and BER validity are delegated to the ASN.1 core.

Test signals: feed valid SPNEGO blobs with Kerberos, MS Kerberos, NTLMSSP, IAKERB, and mixed mechanisms; invalid top-level OID; truncated BER; unsupported mechanism-only blobs; and verify server flags used by session setup and SPNEGO upcall selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/asn1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.c

Purpose: manages cached SMB directory handles and cached directory entries for the CIFS client. Cached fids reduce repeated directory opens when leases allow handle reuse, and are invalidated on lease breaks, reconnects, timeout, or explicit debug/proc actions.

Important APIs: external functions include `init_cached_dirs()`, `free_cached_dirs()`, `open_cached_dir()`, `open_cached_dir_by_dentry()`, `close_cached_dir()`, `drop_cached_dir_by_name()`, `close_all_cached_dirs()`, `invalidate_all_cached_dirs()`, and `cached_dir_lease_break()`. Key internals include `find_or_create_cached_dir()`, `path_to_dentry()`, `path_no_prefix()`, `smb2_close_cached_fid()`, and `cfids_laundromat_worker()`.

Control flow: `open_cached_dir()` converts the path to UTF-16, finds or creates a `cached_fid` under `cfid_list_lock`, resolves a dentry, optionally copies a parent lease key, issues a compounded SMB2 create plus query-info request, validates a lease with read caching, stores `file_all_info`, timestamps the cache entry, and returns a referenced cfid. Lease breaks remove entries from the active list, clear lease state, and queue work to drop dentries and close server handles. The laundromat periodically moves expired or dying entries to a local list and closes them asynchronously.

State and persistence: state is per tree connection in `struct cached_fids`: active and dying lists, entry count, delayed work, and aggregate dirent counters. Each `cached_fid` holds path, dentry, fid, lease state, timestamps, refcount, close/put work, optional file-all-info, and cached dirent list/accounting. Nothing persists beyond mount lifetime.

Dependencies and integration: integrates with SMB2 create/query/close, lease keys, DFS prefix paths, dcache, tcon refcounting, workqueues (`cfid_put_wq`, `serverclose_wq`), debug tracing, and global directory-cache accounting.

Risks: lock ordering and refcount invariants are central. `close_cached_dir_locked()` assumes at least two references when called under the spinlock. Error paths must remove half-constructed entries and close any lease/open references. Prefix-path and dentry reconstruction can fail after DFS failover. Workqueue close paths must hold tcon references long enough to close on the server.

Test signals: cache hit and lookup-only miss, max cached dirs, create/query compound failure, replayable errors, lease break during construction, parent lease key propagation, invalidation on reconnect, laundromat timeout, unmount dentry dropping, directory-cache accounting decrement, encrypted shares, DFS prefix paths, and explicit open_dirs proc cache drop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.h

Purpose: declares cached directory handle and cached dirent data structures plus the public API used by the SMB client directory, inode, reconnect, and debug paths.

Important types: `struct cached_dirent` stores a cached name, position, and attributes. `struct cached_dirents` tracks validity/failure flags, the file instance associated with the cache, mutex, expected position, entry list, and accounting. `struct cached_fid` represents one cached open directory handle with lease/open/list state, path, refcount, SMB fid, tcon, dentry, work items, dirents, and trailing `smb2_file_all_info`. `struct cached_fids` is the per-tcon cache container with spinlock, active/dying lists, laundromat work, and aggregate counters.

Control flow: callers allocate per-tcon caches with `init_cached_dirs()`, use `open_cached_dir()` or `open_cached_dir_by_dentry()` to obtain referenced handles, release with `close_cached_dir()`, and invalidate via name, tcon, superblock, or lease-key APIs. `is_valid_cached_dir()` defines a reusable entry as one with both timestamp and lease.

State and persistence: all structures are in-memory mount/session state. Accounting exists per tcon and module-wide through `cifs_dircache_bytes_used`.

Dependencies and integration: depends on CIFS core types, list heads, workqueues, krefs, dentries, SMB2 fid/file-info types, and cifs superblock/tcon abstractions.

Risks: bitfield lease/open/list state must match implementation invariants in `cached_dir.c`. The flexible-array-containing `file_all_info` must remain last. Consumers must respect that `close_cached_dir()` cannot be called with `cfid_list_lock` held.

Test signals: compile users with and without handle cache, verify structure initialization and accounting, lockdep for API misuse, and lease validity transitions across open, lease break, reconnect, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cached_dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.c

Purpose: implements CIFS debug/procfs reporting and runtime toggles for `/proc/fs/cifs`, plus low-level dump helpers used by error paths.

Important APIs: exported or externally used functions include `cifs_dump_mem()`, `cifs_dump_mids()`, `cifs_proc_init()`, and `cifs_proc_clean()`. Proc show/write handlers cover `DebugData`, `open_files`, `open_dirs`, `Stats`, `cifsFYI`, `traceSMB`, `LinuxExtensionsEnabled`, `SecurityFlags`, `LookupCacheEnabled`, `mount_params`, optional DFS cache, and SMB Direct tunables.

Control flow: proc initialization creates entries under `fs/cifs`. Show handlers use `seq_file` to walk global server/session/tcon lists under `cifs_tcp_ses_lock` and finer-grained locks. DebugData prints feature flags, server/channel/session/share/interface/MID state, compression/encryption status, and witness registrations. Stats write resets counters when a boolean is accepted. SecurityFlags write parses booleans or numeric flags, validates against `CIFSSEC_MASK`, normalizes MUST flags, and updates `global_secflags`.

State and persistence: proc writes mutate global module state (`cifsFYI`, `traceSMB`, `linuxExtEnabled`, `lookupCacheEnabled`, `global_secflags`) and reset counters on servers/tcons. Proc output reflects live in-memory connection/session/open-file/cache state; no persistent storage exists.

Dependencies and integration: depends on procfs, `seq_file`, CIFS global lists and locks, SMB Direct, DFS cache, witness dump, cached directory invalidation, security flag definitions, and mount parameter descriptors.

Risks: diagnostic paths traverse complex live state while holding global locks, so output changes can introduce lock ordering or sleep-under-spinlock issues. SecurityFlags parsing is user-facing ABI. DebugData may disclose sensitive topology and, with debug key options elsewhere, can support secret exposure workflows. `open_dirs` write invalidates caches across all mounts.

Test signals: read all proc files with no sessions and active multichannel sessions, reset Stats, toggle cifsFYI/traceSMB/linux extensions/lookup cache, reject invalid security flags, verify MUST flag normalization, drop open_dirs cache, enable SMB Direct tunables, and run lockdep while sessions reconnect during DebugData reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.h

Purpose: defines CIFS debug logging macros, severity/category bits, and declarations for memory, SMB packet, and MID dump helpers.

Important APIs and symbols: declares `cifs_dump_mem()`, `cifs_dump_mids()`, `dump_smb()`, `traceSMB`, and `cifsFYI`. Logging bits include `CIFS_INFO`, `CIFS_RC`, `CIFS_TIMER`, category constants `VFS`, `FYI`, `NOISY`, and `ONCE`. Macros include `cifs_info()`, `cifs_dbg()`, `cifs_server_dbg()`, and `cifs_tcon_dbg()`.

Control flow: when `CONFIG_CIFS_DEBUG` is enabled, macros route VFS messages to ratelimited `pr_err`, FYI messages to `pr_debug` only when `cifsFYI & CIFS_INFO`, and optional noisy messages under `CONFIG_CIFS_DEBUG2`. Server macros lock `server->srv_lock` around hostname access. Tcon macros prefix tree names when available. When debug is disabled, macros compile references in dead `if (0)` blocks to preserve type checking but emit nothing except `cifs_info()`.

State and persistence: reads global debug controls but owns no storage.

Dependencies and integration: depends on Linux printk/pr_debug variants, CIFS server/tcon structures at macro expansion sites, and procfs controls implemented in `cifs_debug.c`.

Risks: macros evaluate parameters in contexts that may hold locks; adding expensive expressions can still matter in enabled builds. `cifs_server_dbg()` assumes a variable named `server` is in scope, and `cifs_tcon_dbg()` assumes `tcon`, making call-site naming part of the API.

Test signals: compile with `CONFIG_CIFS_DEBUG` off/on and `CONFIG_CIFS_DEBUG2`; verify no unused-variable fallout; toggle `cifsFYI`; check ONCE/rate-limited behavior; and run lockdep around server debug logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_fs_sb.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_fs_sb.h

Purpose: defines CIFS mount flag bits and the CIFS-specific superblock state stored in `struct cifs_sb_info`.

Important APIs and types: mount flags include permission bypass, server inode use, direct I/O, xattr disable, SFU/SFM character remapping, POSIX paths/ACLs, Unix emulation, byte-range lock behavior, ACL handling, uid/gid override, fscache, Minshall-French symlinks, multiuser, strict I/O, backup intent, prefix paths, DFS disable, cache assumptions, and shutdown. `struct cifs_sb_info` holds tcon links, local NLS table, parsed mount context, active count, flags, prune work, RCU cleanup, optional prepath, serverino autodisable state, and root dentry.

Control flow: this header has no executable flow, but mount parsing and runtime code test `mnt_cifs_flags` to select behavior in path conversion, permission checks, caching, DFS, and network operations.

State and persistence: per-superblock state lives for the mount lifetime. Flags are atomic because multiple paths inspect or update mount behavior. `prepath` and `root` are available after mount setup.

Dependencies and integration: integrates with VFS superblock private data, tcon link management, rbtrees, delayed work, RCU, NLS, and `smb3_fs_context`.

Risks: flag exhaustion and bit overlap are high-impact because flags are persisted across many call sites. Atomic flag updates need consistent helper use. Prefix-path and root-dentry availability assumptions can break early mount or reconnect code.

Test signals: mount option matrix for each flag, remount/shutdown transitions, prefix path mounts, serverino autodisable matching, multiuser tlink pruning, DFS-disabled mounts, fscache/strict/direct I/O interactions, and lockdep around tlink tree access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_fs_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_ioctl.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_ioctl.h

Purpose: defines userspace-visible CIFS/SMB3 ioctl data structures and command numbers.

Important APIs and types: structures include `smb_mnt_fs_info`, `smb_mnt_tcon_info`, `smb_snapshot_array`, `smb_query_info`, `smb3_key_debug_info`, `smb3_full_key_debug_info`, `smb3_notify`, and `smb3_notify_info`. Ioctl commands include copychunk, set integrity, mount info, snapshots, passthrough query/set/fsctl, key dump, notify, full key dump, tcon info, and shutdown. Shutdown flags mirror XFS-style going-down modes.

Control flow: no executable code; `ioctl.c` and user tools include these layouts to marshal fixed and flexible-array payloads.

State and persistence: structures describe transient ioctl input/output. `__packed` fixes ABI layout, so field ordering and width are persistent userspace ABI.

Dependencies and integration: depends on SMB protocol constants such as key sizes and cipher types, Linux ioctl encoding macros, and userspace headers consuming the command numbers.

Risks: ABI compatibility is the main risk. Packed structs with flexible tails require careful size validation in handlers. Key dump ioctls expose session and encryption keys and must remain gated by debug/security policy. Boolean fields inside packed ABI need consistent userspace interpretation.

Test signals: ioctl size/offset checks on 32-bit and 64-bit userspace, snapshot enumeration buffer sizing, passthrough query input/output lengths, notify info flexible payload, key dump permission/config gating, and shutdown flag handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.c

Purpose: implements CIFS SPNEGO key management and request-key upcalls used to obtain Kerberos/SPNEGO session setup blobs from userspace helpers.

Important APIs: `cifs_spnego_key_type` defines the `cifs.spnego` key type. `cifs_get_spnego_key()` builds a key description and calls `request_key()`. `init_cifs_spnego()` registers the key type and installs a dedicated `.cifs_spnego` thread keyring under override credentials. `exit_cifs_spnego()` revokes and unregisters the key type. Key payload lifecycle is handled by `cifs_spnego_key_instantiate()` and `cifs_spnego_key_destroy()`.

Control flow: session setup calls `cifs_get_spnego_key()` with session and server state. The function constructs `ver`, host, IP, security mechanism, uid, cred uid, optional username, pid, and upcall target fields; then it uses `scoped_with_creds(spnego_cred)` so request-key caching occurs in the special keyring. The returned key payload is expected to contain `struct cifs_spnego_msg` with session key and security blob.

State and persistence: `spnego_cred` and its thread keyring persist for module lifetime. Individual keys are cached by the kernel keyring subsystem and hold copied payload bytes.

Dependencies and integration: depends on Linux keyrings/request-key, CIFS session/server state, address formatting, security mechanism flags from ASN.1 negotiation, tracepoints, and userspace cifs.upcall behavior.

Risks: key description formatting is ABI with userspace helpers; buffer length calculations must cover all fields. Usernames and hostnames are embedded directly in descriptions. Unknown server auth type falls back to `krb5`, which may hide negotiation issues. Debug2 can dump SPNEGO reply blobs.

Test signals: request-key upcalls for IPv4 and IPv6 servers, krb5/mskrb5/iakerb selection, mount versus app upcall target, user and cred uid fields, username omission, malformed helper payloads, key reuse/caching, module init failure unwinding, and module exit revocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.h

Purpose: declares the userspace-helper payload format and public SPNEGO key acquisition API for the CIFS client.

Important APIs and types: `CIFS_SPNEGO_UPCALL_VERSION` is the request-key protocol version. `struct cifs_spnego_msg` contains version, flags, session-key length, security-blob length, and flexible data containing session key followed by security blob. It declares `cifs_spnego_key_type` and `cifs_get_spnego_key()`.

Control flow: session setup includes this header to request a key and interpret the returned payload from `cifs_spnego.c` and userspace.

State and persistence: no state in the header; the struct layout is a stable kernel/userspace protocol for cifs.upcall-style helpers.

Dependencies and integration: depends on keyring type declarations and CIFS session/server types. It is enabled by `CONFIG_CIFS_UPCALL`.

Risks: any layout or version change needs userspace coordination. Flexible payload parsing must validate both lengths before use.

Test signals: compile with SPNEGO enabled, verify helper payload version matching, session-key/security-blob length validation, and compatibility with existing cifs.upcall implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_spnego.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.c

Purpose: implements the SMB Witness Service client-side registration and notification handling used for clustered/scale-out SMB shares. It communicates with a userspace witness daemon through generic netlink.

Important APIs and types: `struct cifs_swn_reg` tracks registration id, refcount, network name, share name, notification flags, and tcon. Public functions are `cifs_swn_register()`, `cifs_swn_unregister()`, `cifs_swn_notify()`, `cifs_swn_dump()`, and `cifs_swn_check()`. Global state is `cifs_swnreg_idr` protected by `cifs_swnreg_idr_mutex`.

Control flow: registration lookup extracts server/share from `tcon->tree_name`, reuses an existing matching registration or allocates a new IDR entry, then sends a generic-netlink register message with names, IP, notification flags, and Kerberos or NTLM auth attributes. Notifications look up registration id, dispatch resource-state changes to reconnect signaling, or client-move messages to store a new destination address, unregister/register around it, and signal reconnect. Unregister drops the refcount and sends an unregister message on final release.

State and persistence: registrations live in-memory and are refcounted across tcons sharing the same network/share name. Server `swn_dstaddr` and `use_swn_dstaddr` persist until reset to steer reconnects.

Dependencies and integration: depends on generic netlink family definitions, CIFS netlink attributes, tcon/session/server state, auth selection, reconnect signaling, hostname/share extraction, fscache include side effects, and proc DebugData through `cifs_swn_dump()`.

Risks: auth material, including NTLM passwords, is placed in netlink messages to the daemon. IDR entries are protected by a mutex, but notification lookup releases the mutex before using the registration, so lifetime assumptions depend on external serialization by netlink paths and active mounts. Client-move address handling must preserve port and avoid reconnect loops.

Test signals: register/unregister refcount sharing, missing or invalid netlink attributes, Kerberos and NTLM auth messages, resource unavailable/available notifications, client move to IPv4/IPv6, unregister/register failure during move, echo-task `cifs_swn_check()` retry, DebugData dump, and concurrent unmount while notifications arrive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.h

Purpose: declares Witness Service APIs and provides no-op stubs when `CONFIG_CIFS_SWN_UPCALL` is disabled.

Important APIs: enabled builds expose `cifs_swn_register()`, `cifs_swn_unregister()`, `cifs_swn_notify()`, `cifs_swn_dump()`, `cifs_swn_check()`, `cifs_swn_set_server_dstaddr()`, and `cifs_swn_reset_server_dstaddr()`. Disabled builds inline success/no-op/false stubs.

Control flow: callers can unconditionally invoke SWN hooks. `cifs_swn_set_server_dstaddr()` copies the witness-provided destination address into `server->dstaddr` when `use_swn_dstaddr` is set; reset clears the flag.

State and persistence: header inline helpers read/write `TCP_Server_Info` address fields but own no independent state.

Dependencies and integration: depends on `cifsglob.h`, tcon/server types, generic netlink forward declarations, and optional SWN implementation.

Risks: no-op stubs mean callers must not assume witness functionality is active unless config and runtime registration succeed. Address override helpers directly mutate server destination state and must be used in reconnect code only.

Test signals: compile with SWN enabled and disabled, verify unconditional call sites link, exercise reconnect address override/reset, and confirm DebugData omits witness registrations in disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_swn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.c -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.c

Purpose: performs CIFS/SMB pathname and string conversion between wire-format UTF-16LE and local NLS encodings, including SFU and SFM reserved-character remapping.

Important APIs: external functions include `cifs_from_utf16()`, `cifs_utf16_bytes()`, `cifs_strtoUTF16()`, `cifs_strndup_from_utf16()`, `cifsConvertToUTF16()`, and `cifs_strndup_to_utf16()`. Internal helpers include `convert_sfu_char()`, `convert_sfm_char()`, `cifs_mapchar()`, `convert_to_sfu_char()`, `convert_to_sfm_char()`, and `cifs_local_to_utf16_bytes()`.

Control flow: inbound conversion walks UTF-16 words with unaligned little-endian loads, optionally maps SFU/SFM private-use codepoints back to reserved local characters, uses `uni2char()`, and falls back to UTF-8 surrogate/variation handling or `?`. Outbound conversion either delegates to `cifs_strtoUTF16()` for no remap, or scans source bytes, applies SFU/SFM mappings for reserved characters and trailing spaces/periods, converts through NLS `char2uni()`, and handles UTF-8 surrogate/IVS sequences with `utf8s_to_utf16s()`.

State and persistence: no global state. Behavior is driven by the local `nls_table`, source buffers, and remap mode selected from mount flags.

Dependencies and integration: depends on NLS tables, UCS-2/UTF-16 utility helpers, mount flags from `cifs_fs_sb.h`, SMB path-building code, and filename semantics for Windows, Services for Unix, and Services for Mac compatibility.

Risks: path separators cannot be remapped until path-building code changes, explicitly leaving slash/backslash limitations. Buffer sizing is caller-sensitive; `cifsConvertToUTF16()` assumes target capacity. Surrogate-pair and IVS handling is specialized for UTF-8 and can fall back to `?`. SFM trailing space/period handling has special cases for `.` and `..` symlink targets.

Test signals: UTF-8 and non-UTF-8 NLS conversions, malformed byte sequences, surrogate pairs, IVS sequences, SFU and SFM reserved character round trips, trailing space and period components, `.` and `..` preservation, max-length truncation, unaligned UTF-16 source buffers, and mount flag selection via `cifs_remap()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.h

Purpose: declares CIFS Unicode/NLS conversion APIs and constants for SFM/SFU reserved-character remapping.

Important APIs and symbols: defines SFM private-use codepoints for double quote, asterisk, question mark, colon, greater-than, less-than, pipe, slash, trailing space, and trailing period. Remap modes are `NO_MAP_UNI_RSVD`, `SFM_MAP_UNI_RSVD`, and `SFU_MAP_UNI_RSVD`. Declares conversion functions between UTF-16LE and local strings, duplication helpers, `cifs_toupper()`, and inline `cifs_remap()`.

Control flow: `cifs_remap()` inspects `cifs_sb_flags()` and gives priority to `CIFS_MOUNT_MAP_SFM_CHR` over `CIFS_MOUNT_MAP_SPECIAL_CHR`, selecting the remap mode passed into conversion functions.

State and persistence: no state in the header. Constants are part of cross-platform filename compatibility behavior and should be treated as stable.

Dependencies and integration: includes byteorder, types, NLS, UCS-2 utilities, CIFS globals, and mount flags through `cifs_sb_info`.

Risks: remap mode priority affects whether filenames round-trip with Mac-style or SFU-style encodings. Adding new reserved characters must align with server behavior and readdir/open symmetry.

Test signals: compile all conversion users, verify mount flag to remap mode mapping, round-trip filenames under each remap mode, and confirm no remap mode leaves reserved private-use values untouched except through normal NLS conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_unicode.h -->
