# Research: subset-b-007654

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lst.c -->
# sources/distributed-fs/lustre-release/lnet/utils/lst.c

## Purpose
`lst.c` implements the `lst` user-space command for Lustre/LNet self-test session administration. It creates and destroys self-test sessions, manages node groups, defines batches and tests, starts/stops/query batches, pings nodes, and samples LNet/RPC self-test counters. It supports a newer generic-netlink/YAML path for session and group discovery while keeping legacy ioctl paths against `IOC_LIBCFS_LNETST`.

## Important APIs, Types, and Functions
- Global session state: `session_key`, `session_features`, `trans_stat`, and `LST_INVALID_SID`.
- String expansion helpers: `lstr_t`, `expand_strs()`, `expand_lstr()`, `new_lstrs()`, and `lst_parse_nids()` implement numeric bracket expansion such as nid ranges before converting names with `libcfs_str2nid()`.
- Kernel transport wrapper: `lst_ioctl()` packages an operation code and payload in `libcfs_ioctl_data`, sends it through `l_ioctl(LNET_DEV_ID, IOC_LIBCFS_LNETST, ...)`, and classifies local, RPC, and framework failures.
- YAML/netlink helpers: `lst_yaml_session()`, `lst_yaml_groups()`, and `lst_yaml_display_groups()` emit YAML requests via liblnetconfig netlink helpers and parse scalar events from kernel replies.
- Command handlers: `jt_lst_new_session()`, `jt_lst_end_session()`, `jt_lst_show_session()`, `jt_lst_add_group()`, `jt_lst_del_group()`, `jt_lst_update_group()`, `jt_lst_list_group()`, `jt_lst_ping()`, `jt_lst_stat()`, `jt_lst_show_error()`, `jt_lst_add_batch()`, `jt_lst_start_batch()`, `jt_lst_stop_batch()`, `jt_lst_list_batch()`, `jt_lst_query_batch()`, and `jt_lst_add_test()`.
- RPC result memory helpers: `lst_alloc_rpcent()`, `lst_free_rpcent()`, `lst_reset_rpcent()`, and `lst_print_transerr()` operate on `struct lstcon_rpc_ent` lists with variable payload tails.
- Stat helpers: `lst_stat_req_param_t`, `lst_cal_lnet_stat()`, `lst_print_lnet_stat()`, and `lst_print_stat()` compute per-interval send/receive rates and bandwidth from paired counter snapshots.

## Control Flow
`main()` sets line-buffered output, calls `lst_initialize()` to read `LST_SESSION` and `LST_FEATURES`, initializes the LNet config library, then dispatches through `cfs_parser()` using `lst_cmdlist`. Most mutating commands first require `session_key != 0`. Session creation first tries `lst_yaml_session()` with create flags, then falls back to `lst_new_session_ioctl()` if netlink is unavailable and an explicit session key exists. Session and group listing similarly prefer YAML/netlink and fall back to ioctl enumeration.

Group and batch commands usually follow a count-then-operate pattern: discover a node count, allocate enough `lstcon_rpc_ent` result entries, invoke a self-test ioctl, then print per-node or aggregate results. `stat` keeps two result lists per target and alternates them so it can calculate deltas across sampling intervals. `stop` sends a stop ioctl, then repeatedly queries until running and failed counts reach zero. `add_test` parses the test type and parameters, validates source and destination groups, allocates result entries sized for the larger group, and sends `LSTIO_TEST_ADD`.

## State and Persistence Behavior
The process keeps only transient memory state. Persistent self-test state lives in the kernel LNet self-test subsystem and is selected by `session_key`. Environment variables provide startup state: `LST_SESSION` identifies the session key and `LST_FEATURES` limits advertised feature bits. `lst_yaml_session()` updates process globals after successful session creation by reading the kernel reply key and negotiated protocol feature mask. Command results and counters are printed; no local files are written.

## Dependencies and Integration Points
The file integrates with libcfs ioctl plumbing, LNet nid parsing/printing, Linux generic netlink through liblnetconfig YAML helpers, and many UAPI structures from `linux/lnet/lnetctl.h` and `linux/lnet/lnetst.h`. It depends on kernel-side self-test operations such as `LSTIO_SESSION_NEW`, `LSTIO_NODES_ADD`, `LSTIO_BATCH_QUERY`, `LSTIO_TEST_ADD`, and `LSTIO_STAT_QUERY`. The parser integration is via `libcfs/util/parser.h`.

## Risks and Edge Cases
- YAML parsing is event-order sensitive and mostly scalar driven; malformed or changed reply shapes can lead to parser errors or incomplete output.
- Some string copies use `strncpy()` into fixed buffers without always forcing a trailing NUL after truncation.
- `lst_parse_nids()` can allocate large arrays if a user supplies very wide bracket ranges.
- Return code conventions are non-obvious: `lst_ioctl()` maps local errors to `-1`, RPC errors to `-2`, and framework errors to `-3`, while some callers intentionally ignore non-local failures.
- Stat delta math assumes matching result order between paired samples and can abort output if group membership changes.
- `lst_get_bulk_param()` accepts suffix multipliers and offsets from user input; overflow and boundary behavior should be tested around `LNET_MTU`, negative values, and malformed suffixes.

## Test Signals
Useful signals include parser tests for all commands and invalid option combinations; bracket expansion tests for single values, ranges, strides, and syntax errors; mocked `lst_ioctl()` tests for local/RPC/framework failure classification; netlink fallback tests for sessions/groups; batch stop/query loop behavior under running, failed, and unknown nodes; and stat tests with stable counters, wraparound-like counter changes, group reordering, and zero/negative sampling intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/lst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/routerstat.c -->
# sources/distributed-fs/lustre-release/lnet/utils/routerstat.c

## Purpose
`routerstat.c` is a small user-space monitor for LNet router statistics. It locates the LNet `stats` parameter file, reads the counters once or at a user-specified interval, and prints either absolute counters or per-second rates.

## Important APIs, Types, and Functions
- `counters_t` mirrors the expected eleven numeric fields in the LNet stats file: message allocation/max, errors, send/receive/route/drop counts, and byte lengths.
- `timenow()` returns wall-clock seconds as a `double` from `gettimeofday()`.
- `subul()` and `subull()` compute unsigned deltas with wraparound handling.
- `rul()` and `rull()` convert deltas to rates.
- `do_stat()` reads, parses, diffs against static previous state, and prints output.
- `main()` resolves the stats path with `cfs_get_param_paths(&path, "stats")`, opens the first match, and loops if an interval is supplied.

## Control Flow
The first call to `do_stat()` prints absolute counters because `last == 0.0`. Subsequent calls seek to the start of the open stats file, read and parse the counters, compute elapsed time from the previous sample, calculate deltas with wraparound helpers, and print rates for errors, byte throughput, and operation counts. `main()` returns immediately for interval zero; otherwise it sleeps `interval` seconds forever between samples.

## State and Persistence Behavior
The program keeps previous counters and timestamp in static variables inside `do_stat()`. It persists nothing and does not alter kernel state. The stats file descriptor remains open across the monitoring loop.

## Dependencies and Integration Points
It depends on libcfs parameter discovery from `<libcfs/util/param.h>` and the kernel-exposed LNet `stats` proc/sysfs parameter. It also uses standard POSIX file APIs, `glob_t`, and libc time/string functions.

## Risks and Edge Cases
- `atoi()` accepts invalid interval strings as zero, silently switching to one-shot mode.
- `do_stat()` exits the process on read or parse errors, so transient parameter read failures are fatal.
- It reads at most 1023 bytes and expects exactly the current stats file layout with eleven values.
- The first path returned by `cfs_get_param_paths()` is used without checking for multiple LNet instances.
- If the elapsed time is extremely small, printed rates can be noisy or divide by a near-zero value.

## Test Signals
Tests should cover absolute first-sample output, delta output with known elapsed time, unsigned wraparound deltas, malformed stats files, missing stats path, invalid interval input, and short/partial reads from a fake stats file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/routerstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/wirecheck.c -->
# sources/distributed-fs/lustre-release/lnet/utils/wirecheck.c

## Purpose
`wirecheck.c` is a generator for compile-time LNet wire protocol layout assertions. It prints a C function, `lnet_assert_wire_constants()`, containing `BUILD_BUG_ON()` checks for constants, struct sizes, member offsets, and member sizes from `linux/lnet/lnet-types.h`.

## Important APIs, Types, and Functions
- Assertion macros: `CHECK_DEFINE()`, `CHECK_VALUE()`, `CHECK_STRUCT()`, `CHECK_MEMBER()`, and `CHECK_MEMBER_IS_FLEXIBLE()` print C source assertions.
- Layout checkers: `check_lnet_handle_wire()`, `check_lnet_magicversion()`, `check_lnet_hdr_nid4()`, `check_lnet_ni_status()`, and `check_lnet_ping_info()`.
- `system_string()` runs host commands through `pipe()`, `fork()`, `dup2()`, `system()`, `fdopen()`, and `waitpid()` to capture one line of environment metadata.
- `main()` prints the generated assertion function, including host `uname -a` and compiler version information.

## Control Flow
At startup, `main()` captures system and GCC metadata, emits the function prologue, emits constant assertions for protocol magic/version and message types, delegates struct-specific checks to helper functions, then closes the function. The generated output is intended to be compiled elsewhere as a compatibility gate.

## State and Persistence Behavior
The program has no persistent state. Its only output is generated C code on stdout. It forks child processes for environment strings and aborts on unexpected pipe/fork/command/read failures.

## Dependencies and Integration Points
It integrates with the LNet wire definition header `linux/lnet/lnet-types.h` and the generated output is presumably compared or compiled as part of Lustre's build/test process. It requires a POSIX-like build host with `uname`, `gcc`, shell command execution, and Linux wait/pipe APIs.

## Risks and Edge Cases
- `system_string()` aborts on missing command output or nonzero status, making the generator brittle on non-GCC or restricted build environments.
- The command strings are constants, so shell injection is not the concern, but reliance on `gcc -v` is toolchain-specific.
- The fallback `strnlen` macro maps to `strlen`, which can read beyond a bounded buffer if used on unterminated strings; current inputs are expected command lines from `fgets()`.
- Protocol coverage is explicit; new wire structs or fields require manual additions or they will not be checked.

## Test Signals
Compile and run the generator in the target build environment, compile the generated C, and deliberately perturb selected struct definitions in a test branch to ensure the generated `BUILD_BUG_ON()` lines catch size/offset drift. Also test non-GCC environments if the build supports them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/utils/wirecheck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/Makefile -->
# sources/distributed-fs/lustre-release/lustre/llite/Makefile

## Purpose
This Makefile defines the Lustre llite client kernel module object composition. It builds `lustre.o` as a loadable module and lists the object files that make up the client-side filesystem implementation.

## Important APIs, Types, and Functions
There are no C APIs in this file. Important build variables are:
- `obj-m += lustre.o`, making `lustre.o` a module target.
- `lustre-objs`, collecting llite objects such as `dcache.o`, `dir.o`, `file.o`, `llite_lib.o`, `namei.o`, `xattr.o`, `crypto.o`, PCC, VVP, and foreign-file support.
- `lustre-$(CONFIG_FS_POSIX_ACL) += acl.o`, conditionally adding ACL support.
- `GCOV_PROFILE := y` when `CONFIG_GCOV_PROFILE_LUSTRE` is set.

## Control Flow
Kbuild expands `lustre-objs` and conditionally `lustre-y`, then links those objects into `lustre.o`. The file has no runtime control flow, but it determines which source files participate in the module for a given kernel configuration.

## State and Persistence Behavior
The Makefile affects build artifacts only. It does not define runtime state. Enabling GCOV changes instrumentation in the produced objects.

## Dependencies and Integration Points
It is consumed by Linux kernel Kbuild and depends on surrounding Lustre build infrastructure. It integrates with kernel config symbols `CONFIG_FS_POSIX_ACL` and `CONFIG_GCOV_PROFILE_LUSTRE`.

## Risks and Edge Cases
- Omitting a new source object from `lustre-objs` silently excludes functionality from the module.
- ACL code is only included when `CONFIG_FS_POSIX_ACL` is enabled; callers must provide compatible stubs or compile guards otherwise.
- GCOV instrumentation changes performance and object behavior enough that build/test lanes should distinguish coverage builds from production builds.

## Test Signals
Build tests should cover llite with and without `CONFIG_FS_POSIX_ACL`, and with `CONFIG_GCOV_PROFILE_LUSTRE`. Link failures or missing symbol errors are the main signals for object-list drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/acl.c -->
# sources/distributed-fs/lustre-release/lustre/llite/acl.c

## Purpose
`acl.c` implements llite POSIX ACL get/set operations, adapting VFS ACL interfaces across kernel versions and storing ACLs through Lustre metadata xattrs on the MDS.

## Important APIs, Types, and Functions
- `ll_get_acl_common()` is the shared implementation for access/default ACL retrieval.
- `ll_get_inode_acl()` and `ll_get_acl()` are exported entry points shaped by compatibility macros such as `HAVE_ACL_WITH_DENTRY` and `HAVE_GET_ACL_RCU_ARG`.
- `ll_set_acl()` serializes ACLs with `posix_acl_to_xattr()` and sends them through `md_setxattr()`.
- Key dependencies include `struct ll_inode_info`, `lli_replace_acl()`, `lli_install_acl()`, `ll_xattr_list()`, `md_setxattr()`, and VFS helpers `set_cached_acl()`/`forget_cached_acl()`.

## Control Flow
ACL reads reject RCU mode with `-ECHILD`. Access ACL reads first use the llite inode cache if `LLIF_ACL_VALID` is set. Otherwise the function maps ACL type to an xattr name/type, probes size through `ll_xattr_list()`, fetches the xattr into a stack or heap buffer, decodes it with `posix_acl_from_xattr()`, and updates llite/VFS ACL caches. Default ACLs are duplicated for return rather than installed into `lli_posix_acl`.

ACL writes validate type, reject default ACLs on non-directories unless clearing, serialize the ACL if present, and call `md_setxattr()` with either set or remove flags. On success the inode is marked not synced to MDS, VFS cache is updated, and access ACLs are installed in llite inode state. On failure cached ACLs are forgotten.

## State and Persistence Behavior
Persistent ACL state is stored on the metadata server as POSIX ACL xattrs. Client-side state includes VFS ACL cache entries and `ll_inode_info::lli_posix_acl` guarded by `lli_lock`. `lli_synced_to_mds` is cleared after a successful set, signaling local metadata synchronization state changed.

## Dependencies and Integration Points
This file bridges Linux VFS ACL operations, Lustre xattr listing/set paths, MDS RPC requests, and Lustre inode cache helpers. It uses `init_user_ns` for ACL xattr conversion.

## Risks and Edge Cases
- Kernel ACL API compatibility macros alter function signatures and need build coverage.
- The access ACL cache path relies on `LLIF_ACL_VALID`; stale flag handling elsewhere can affect permission checks.
- Heap allocation is used only when the ACL xattr exceeds the local stack buffer; both paths need error coverage.
- `md_setxattr()` request lifetime must always be released with `ptlrpc_req_put()`.

## Test Signals
Exercise get/set/clear access ACLs, default ACLs on directories, rejected default ACLs on regular files, missing ACL xattrs, unsupported xattrs, large ACL xattrs, RCU lookup behavior, cache invalidation after failed writes, and builds across supported kernel ACL signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/crypto.c -->
# sources/distributed-fs/lustre-release/lustre/llite/crypto.c

## Purpose
`crypto.c` adapts Lustre llite to fscrypt/llcrypt. When encryption support is enabled, it provides context get/set operations, encrypted open policy, encrypted filename preparation and presentation, keyless long-name handling, symlink decoding, dentry revalidation for nokey names, and superblock encryption feature flags. When disabled, it provides thin fallback wrappers.

## Important APIs, Types, and Functions
- Context operations: `ll_get_context()`, `ll_set_context()`, and `ll_set_encflags()`.
- Open and feature flags: `ll_file_open_encrypt()`, `ll_sb_has_test_dummy_encryption()`, `ll_sbi_has_encrypt()`, `ll_sbi_set_encrypt()`, `ll_sbi_has_name_encrypt()`, and `ll_sbi_set_name_encrypt()`.
- Name processing: `ll_prepare_lookup()`, `ll_setup_filename()`, `ll_digest_long_name()`, and `ll_fname_disk_to_usr()`.
- Symlink and dentry helpers: `ll_get_symlink()` and `llcrypt_d_revalidate()`.
- `lustre_cryptops` registers Lustre-specific llcrypt operations including key prefix, context callbacks, dummy policy/context callback, empty-dir callback, and max name length.

## Control Flow
Context get reads the encryption xattr directly through `ll_xattr_list()` because there is no VFS handler for `encryption.*`, and regular files get `i_blkbits` set to the Lustre encryption block size. Context set has two modes: if `inode == NULL`, it stores the context inside `md_op_data` so create RPCs can carry it; otherwise it sends `md_setxattr()` with `XATTR_CREATE`, rejects root-directory encryption, releases the request, and installs encryption flags/cache.

Lookup setup detects keyless encrypted filename operation. Volatile names are passed through unchanged for server-side semantics. Otherwise it calls llcrypt setup, marks nokey/ciphertext dentries, converts missing-key `-ENOENT` into `-ENOKEY` where appropriate, and applies Lustre-specific critical-character encoding. For long keyless names, Lustre presents an encoded `struct ll_digest_filename` carrying the FID and ciphertext excerpt, because the server cannot perform fscrypt local name matching. Disk-to-user conversion reverses this path, including critical decoding and optional digest prefix insertion for old/new base64 client modes.

## State and Persistence Behavior
Persistent encryption context is stored as an MDS xattr. Client state includes inode encryption flags, xattr cache entries, llite superblock feature bits, dentry `DCACHE_NOKEY_NAME`, and prepared filename buffers that callers must free with llcrypt helpers. Dummy encryption state may come from llite superblock flags or stored dummy policy, depending on kernel fscrypt API availability.

## Dependencies and Integration Points
The file is tightly integrated with llcrypt/fscrypt APIs, Lustre xattr and metadata RPC paths, llite superblock/inode flags, Lustre FIDs, critical encode/decode helpers, and VFS dentry revalidation. It also has compatibility branches for several fscrypt API variants and a full fallback path when `HAVE_LUSTRE_CRYPTO` is not defined.

## Risks and Edge Cases
- Keyless long-name lookup depends on exact digest marker conventions and old-client compatibility flags.
- Buffer ownership is subtle: `ll_digest_long_name()` can replace `fname->crypto_buf.name` and frees the filename on error.
- Critical encoding/decoding changes name bytes sent over the wire; regressions can make encrypted names unreachable.
- `llcrypt_d_revalidate()` must return `-ECHILD` under RCU lookup and correctly invalidate nokey dentries after keys are added.
- Fallback stubs compile without Lustre crypto but still call llcrypt setup/open functions; behavior must remain coherent.

## Test Signals
Test encrypted create and lookup with keys present, lookup without keys, long encrypted filenames, old/new digest prefix modes, volatile filenames, `/.fscrypt` lookup under encrypted subdir mounts, symlink readlink without keys, `O_CIPHERTEXT` open with and without `O_DIRECT`, dentry revalidation after key insertion, and non-crypto builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/crypto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/dcache.c -->
# sources/distributed-fs/lustre-release/lustre/llite/dcache.c

## Purpose
`dcache.c` defines llite dentry operations and lookup-intent cleanup. It manages Lustre-specific dentry validity, RCU-safe dentry private data release, intent lock lifetime, alias invalidation, lookup result finalization, and VFS dentry revalidation.

## Important APIs, Types, and Functions
- Dentry ops: `ll_d_init()`, `ll_release()`, `ll_dcompare()`, `ll_ddelete()`, and `ll_revalidate_dentry()` are exported through `ll_d_ops`.
- Intent helpers: `ll_intent_drop_lock()`, `ll_intent_release()`, and `ll_lookup_finish_locks()`.
- Alias and lookup completion: `ll_prune_aliases()` and `ll_revalidate_it_finish()`.
- Important structures and flags include `struct ll_dentry_data`, `lld_invalid`, `lookup_intent`, LDLM lock handles, VFS dentry flags, and llcrypt nokey revalidation state.

## Control Flow
Dentry initialization allocates `ll_dentry_data`, marks the dentry invalid, and stores it in `d_fsdata`. Release clears `d_fsdata` and frees the data through `call_rcu()`. Dentry compare first checks name equality, then allows mountpoints and active parallel lookups, but refuses matches for Lustre-invalid dentries. Dentry delete returns true only for invalid dentries.

Intent cleanup decrements local and remote LDLM locks exactly once by zeroing modes after `ldlm_lock_decref()`. `ll_intent_release()` also drops extra request references attached to open/create dispositions and clears all dispositions. Revalidation first delegates to `llcrypt_d_revalidate()`, accepts intermediate parent lookups, handles foreign-symlink no-follow behavior, forces server relookup under `LOOKUP_REVAL`, rejects RCU revalidation with `-ECHILD`, and otherwise triggers statahead and directory depth updates as needed.

## State and Persistence Behavior
This file manipulates in-memory dentry cache state only. Persistent metadata is not changed. State includes `d_fsdata`, `lld_invalid`, dentry flags, inode alias lists, lookup intent lock handles, and references to `ptlrpc_request` objects.

## Dependencies and Integration Points
It integrates with VFS dentry operations, Linux RCU, Lustre LDLM locking, ptlrpc request lifetimes, llcrypt dentry validation, statahead, llite inode/FID helpers, and metadata lock data installation.

## Risks and Edge Cases
- Double-decrement of intent locks is prevented by zeroing modes; any new path must preserve that invariant.
- `ll_release()` explicitly handles NFS copying dentry ops and finding `d_fsdata == NULL`.
- Revalidation behavior differs for symlinks, foreign symlinks, parent lookups, RCU lookup, and explicit `LOOKUP_REVAL`.
- Invalid dentries are allowed to compare equal during `d_in_lookup()` to serialize parallel lookup; changing this can reintroduce lookup races.

## Test Signals
Exercise parallel lookup races, invalid dentry lookup avoidance, mountpoint dentries, intent release called multiple times, open/create request reference drops, encrypted nokey dentry revalidation, `LOOKUP_RCU`, `LOOKUP_PARENT`, `LOOKUP_REVAL`, symlink and foreign-symlink no-follow cases, and alias pruning after inode invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/dcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/dir.c -->
# sources/distributed-fs/lustre-release/lustre/llite/dir.c

## Purpose
`dir.c` implements llite directory file operations and many directory ioctls. It covers hash-cookie readdir, directory page caching/release, striped directory creation and layout get/set, MDT lookup helpers, HSM copytool control, quota iteration and aggregation, FID removal, layout/stat info ioctls, migration, ladvise ahead, PCC state/detach operations, directory seek/open/release/flush, and the exported `ll_dir_operations`.

## Important APIs, Types, and Functions
- Readdir path: `ll_get_dir_folio()`, `ll_release_dir_folio()`, `ll_dir_read()`, and `ll_iterate()`.
- Striping/layout: `ll_dir_setdirstripe()`, `ll_dir_setstripe()`, `ll_dir_get_default_lmv()`, `ll_dir_get_default_layout()`, `ll_dir_getstripe_default()`, and `ll_dir_getstripe()`.
- MDT and HSM: `ll_get_mdt_idx_by_fid()`, `ll_get_mdt_idx()`, `ll_ioc_copy_start()`, `ll_ioc_copy_end()`, and `copy_and_ct_start()`.
- Quota: `ll_quotactl_iter_list`, `ll_quota_iter_check_and_cleanup()`, `quotactl_iter_acct()`, `quotactl_iter_glb()`, `quotactl_iter()`, `quotactl_getallquota()`, and `quotactl_ioctl()`.
- Ioctl dispatcher: `ll_dir_ioctl()` handles a large command switch for lookup, LMV/LOV get/set stripe, remove entry, rmfid, quota, target count, connect flags, HSM, migrate, ladvise, PCC, and fallback ioctl routing.
- File ops: `ll_dir_seek()`, `ll_dir_open()`, `ll_dir_release()`, `ll_dir_flush()`, and `ll_dir_operations`.

## Control Flow
Readdir uses directory-entry hash values as cookies rather than byte offsets. `ll_iterate()` prepares encryption state, handles end-of-directory, resolves a parent FID for striped directories, prepares `md_op_data`, rejects foreign directories with `-ENODATA`, then delegates to `ll_dir_read()`. `ll_dir_read()` fetches a folio by hash index, iterates `lu_dirent` entries, emits decrypted or raw names through `dir_emit()`, advances to `ldp_hash_end`, removes colliding pages when needed, and maps internal end offsets to 32-bit or native user-visible cookies.

Striped directory creation validates LMV magic/count/hash flags, downgrades unsupported hash types for older MDS connections, applies umask/security context/encryption inheritance, sends `md_create()` with `CLI_SET_MEA`, prepares the returned inode, applies security and encryption flags, then drops references. Layout getters request metadata EAs with `md_getattr()`, swab wire-endian structures for userspace, and optionally fall back to root default layout.

`ll_dir_ioctl()` is the main control hub. It copies and validates user arguments per command, uses Lustre metadata or OBD control operations, converts layout/stat structures for userspace, and carefully releases requests and allocated buffers on exits. Quota iteration first gathers global records from QMT and usage records from MDT/OST QSDs, merges them into a per-superblock iterator list under `quotactl_iter_lock`, returns a mark/count to userspace, and later drains entries through `LUSTRE_Q_GETALLQUOTA`.

## State and Persistence Behavior
Directory page cache state is held in the inode mapping unless pages are collision pages or striped-directory temporary pages. File-private state `ll_file_data::lfd_pos` tracks internal 64-bit hash position, while `fd_partial_readdir_rc` stores deferred partial-readdir errors surfaced by `flush`. Persistent filesystem state is changed by setstripe/setdirstripe, remove-entry, rmfid, quota mutation, HSM requests/progress, migration, and PCC detach operations through MDS/OBD RPCs. Quota all-iteration state is temporarily persisted in `sbi->ll_all_quota_list` until userspace drains or cleanup expires it.

## Dependencies and Integration Points
The file integrates with the Linux VFS file_operations interface, folio/page cache APIs, Lustre metadata client RPCs (`md_read_page`, `md_create`, `md_getattr`, `md_setattr`, `md_rmfid`), LMV/LOV layout formats, llcrypt filename conversion, SELinux/security initialization, HSM coordinator ioctls, quota OBD interfaces, PCC helpers, and llite stats accounting. It depends heavily on UAPI ioctl structures from Lustre headers.

## Risks and Edge Cases
- Readdir correctness depends on stable hash-cookie semantics, collision-page handling, and 32-bit API translation.
- Encrypted readdir changes emitted names and can fail mid-page if filename conversion fails.
- `ll_dir_ioctl()` has many user-copy paths; size, NUL-termination, magic, and overflow checks are critical.
- Layout handling must distinguish LOV, LMV, default LMV, specific stripes, composite layouts, and foreign LMV blobs.
- HSM archive completion compares data versions and intentionally reports `-EBUSY` without retry if content changed.
- Quota iterator state is process/time marked and cleaned after 24 hours; partial userspace drains or buffer shortages must not leak list entries.
- Some stat size adjustments for encrypted files appear to round an initially zero local field before assigning body size in the no-key case, which deserves focused review against expected statx behavior.

## Test Signals
Exercise readdir over normal, striped, colliding-hash, encrypted-key, encrypted-nokey, 32-bit API, and foreign directories. Test setstripe/getstripe for LOV v1/v3/specific/composite, LMV default/raw/foreign, unsupported hash downgrades, root default fallback, and too-small user buffers. Ioctl tests should cover invalid user sizes, missing NUL names, HSM request/progress/copy start/end, quota permission checks and iterator drain/cleanup, subdir `rmfid` visibility filtering, migration validation, ladvise ahead constraints, PCC state/detach by cached and uncached inodes, seek cookie translation, and partial-readdir flush errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/dir.c -->
