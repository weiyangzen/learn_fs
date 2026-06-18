# Group Research: group_502_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_eb7d47a051d0

Scope confirmed against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_set_fileinfo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_set_fileinfo.c

Implements SMB1/TRANS2 file and path information mutation dispatch for `smbsrv`. Entry points include `smb_com_trans2_set_file_information`, `smb_com_trans2_set_path_information`, legacy `smb_com_set_information`, and `smb_com_set_information2`.

The core split is `smb_set_by_fid` versus `smb_set_by_path`. FID updates verify writable tree state, tolerate IPC/non-disk handles as successful no-ops where protocol-compatible, look up `sr->fid_ofile`, adopt the open-file credential via `smb_ofile_getcred`, and dispatch on `sinfo.si_node`. Path updates reject read-only trees, validate and reduce the pathname, look up the target node under the share root, then dispatch and release the node.

`smb_set_fileinfo` maps information levels to concrete handlers. It handles legacy `SMB_SET_INFORMATION`, `SMB_SET_INFORMATION2`, `SMB_INFO_STANDARD`, basic/disposition/EOF/allocation/rename levels, returns `NT_STATUS_EAS_NOT_SUPPORTED` for EA set, `NT_STATUS_NOT_SUPPORTED` for link information, and `NT_STATUS_INVALID_INFO_CLASS` otherwise.

Time handling deliberately treats zero and `UINT_MAX`/`-1` as “do not change”. `smb_set_information` also preserves Windows compatibility around `FILE_ATTRIBUTE_NORMAL`: if it is the only attribute in legacy setattr, attributes are not changed. Directory attribute attempts on non-directories are rejected.

`SMB_FILE_RENAME_INFORMATION` is limited to same-directory rename semantics. It rejects nonzero `rootdir`, empty or overlong names, and names containing `\`. It builds the destination path either from the original path parent or by deriving the share path from the node parent, sets `dst_fqi` hints, and delegates to `smb_setinfo_rename`.

Primary dependencies are `smb_mbc_decodef`, `smbsr_decode_*`, pathname reduction/lookup helpers, `smb_node_setattr`, and external set-info helpers such as `smb_set_basic_info`, `smb_set_disposition_info`, `smb_set_eof_info`, and `smb_set_alloc_info`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_set_fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sign_kcf.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sign_kcf.c

Kernel Cryptographic Framework backend for SMB signing and MAC generation. The file is the kernel counterpart to the user-space fake SMB server signing implementation.

`find_mech` resolves named crypto mechanisms with `crypto_mech2id`, logs unavailable mechanisms, and stores the mechanism type into `smb_crypto_mech_t`. SMB1 signing uses MD5 helpers: `smb_md5_getmech`, `smb_md5_init`, `smb_md5_update`, and `smb_md5_final`. Updates wrap raw buffers in `crypto_data_t`; update failure cancels the KCF context.

SMB2/SMB3 mechanism helpers expose SHA256 HMAC, AES-CMAC, and AES-GMAC lookup. `smb2_sign_init_hmac_param` sets the HMAC output length parameter, while `smb3_sign_init_gmac_param` initializes KCF GMAC parameters with an IV and no AAD.

The shared `smb2_mac` helper performs one-shot `crypto_mac` with a raw key measured in bits and a caller-supplied raw output buffer. Public wrappers support scatter/gather UIO input (`smb2_mac_uio`) and contiguous raw input (`smb2_mac_raw`). The common SMB2 signature case writes a 16-byte digest/signature buffer, while the raw helper accepts caller-specified MAC length.

This file contains no SMB protocol parsing. It is a cryptographic adapter used by higher-level SMB1/SMB2 signing code and depends on `sys/crypto/api.h`, `smb_kproto.h`, and `smb_kcrypt.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_sign_kcf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_signing.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_signing.c

Implements SMB1 message signing for the SMB server. The file calculates and verifies 8-byte SMB1 MAC signatures over mbuf chains using MD5 via the helper layer in `smb_sign_kcf.c`.

`smb_sign_begin` initializes signing after session setup. It ignores anonymous/guest-like paths without a session key, serializes setup under the session lock, initializes the MD5 mechanism once per session, builds the MAC key from the user session key plus the NTLM response for non-extended-security logons, initializes sequence numbers, and enables signing/checking flags according to negotiated server security mode.

`smb_sign_calc` is the central signature function. It computes `head(MD5(MACKey || SMBMsg), 8)` after copying the SMB header into an aligned temporary union, replacing the signature field with the little-endian sequence number and zero padding, then digesting the remainder of the mbuf chain from after the SMB header. It returns failure if signing material is absent or KCF operations fail.

`smb_sign_check_request` verifies normal SMB1 requests using `sr->sr_seqnum`, skipping secondary transaction commands because they share the original transaction sequence. In debug builds, `smb_sign_find_seqnum` can search nearby sequence numbers and correct the session sequence for diagnostics. `smb_sign_check_secondary` verifies secondary transactions using `reply_seqnum - 1` and records the reply sequence number. `smb_sign_reply` computes and writes the response signature at offset 14.

`smb_sign_fini` frees the per-session signing mechanism during session teardown. Key state lives in `session->signing`, and the code assumes SMB1 fixed header layout constants: 32-byte header, signature offset 14, signature size 8.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_signing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_srv_oplock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_srv_oplock.c

Server-level SMB1/SMB2 oplock and SMB2 lease break orchestration. This file sits above the filesystem-level oplock state machine in `smb_cmn_oplock.c`, translating lower-level break indications into asynchronous server work and protocol-specific break messages.

`smb_oplock_ind_break` is the main callback used by FS-level oplock code. It is called while node ofile-list and oplock locks may already be held, so it only validates completion status, takes an oplock-break hold on the `smb_ofile_t`, allocates an `smb_request_t`, populates tree/user/ofile references, records break level and status, updates handle/lease state, and dispatches `smb_oplock_async_break` to the server notify taskq. Special completion statuses update local handle state directly: `STATUS_NEW_HANDLE` calls `smb_oplock_hdl_moved`, and `NT_STATUS_OPLOCK_HANDLE_CLOSED` calls `smb_oplock_hdl_closed`.

`smb_oplock_ind_break_in_ack` handles break indications generated while processing an SMB2 break acknowledgment. When possible, it appends post-work to the current request so the new break is sent only after the ack reply. If that is impossible, it falls back to taskq dispatch on a server session request.

`smb_oplock_async_break` marks the synthetic request active, calls `smb_oplock_send_break`, updates durable-handle NV state if dirty, completes the request, and frees it. `smb_oplock_send_break` chooses SMB2 lease, SMB2 oplock, or SMB1 oplock break output based on `ofile->f_lease` and the oplock dialect.

State updates are centralized in `smb_oplock_hdl_update`, which records `og_breakto`, marks breaks in progress, increments lease epochs when appropriate, and immediately applies non-ack-required breaks. Persistent durable handles are updated when break state changes without an ack requirement.

The wait helpers implement cancellation-aware synchronization. `smb_oplock_wait_ack` waits for a client ack to reduce oplock/lease state to the requested level, logs timeout details, and handles request cancellation states. `smb_oplock_wait_break` waits for all node-level break bits to clear, also with request cancellation support. `smb_oplock_wait_break_fem` is a simplified FEM path without request cancellation plumbing. Tunables define ack and default wait timeouts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_srv_oplock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_thread.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_thread.c

Small thread lifecycle abstraction used by the SMB server. It wraps kernel thread creation, cooperative stop signaling, and wait/continue helpers around `smb_thread_t`.

`smb_thread_init` zeroes and initializes a thread object with name, entry point, argument, priority, server pointer, mutex, condition variable, and magic/state values. `smb_thread_destroy` asserts the object is exited and tears down synchronization primitives.

`smb_thread_start` transitions from `EXITED` to `STARTING`, creates either an LWP-backed kernel thread for priorities below `MINCLSYSPRI` or a regular kernel thread, records the thread pointer and dispatch ID, then waits for the new thread to reach `RUNNING` or fail. The common `smb_thread_entry_point` sets `RUNNING`, invokes the real entry point unless killed early, then clears the thread pointer, marks `EXITING`, broadcasts, and exits via `lwp_exit` when needed or `thread_exit`.

`smb_thread_stop` is cooperative. It sets `sth_kill`, broadcasts, waits for `EXITING`, joins by dispatch ID, then marks `EXITED` and clears kill state. It also handles already exiting or already exited states. `smb_thread_signal` wakes a running thread.

`smb_thread_continue`, `smb_thread_continue_nowait`, and `smb_thread_continue_timedwait` provide the canonical loop condition for worker functions. The locked helper interprets ticks `0` as indefinite wait, `-1` as nonblocking check, otherwise relative timed wait, and returns false once `sth_kill` is set.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_thread.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_create_directory.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_create_directory.c

Implements `TRANS2_CREATE_DIRECTORY`, the SMB1 transaction2 directory-create subcommand. It accepts a reserved field, directory name, and optional FEA list, though the implementation only returns an EA error offset of zero.

`smb_com_trans2_create_directory` requires a disk tree, decodes the pathname from the transaction parameter block, initializes and validates the pathname, performs directory-name-specific validation, then delegates creation to `smb_common_create_directory`. Filesystem errors are translated with `smbsr_errno`.

On success it encodes a single zero `EaErrorOffset` in the transaction response parameter block and returns `SDRC_SUCCESS`. IPC or non-disk shares are rejected with access denied.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_create_directory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_dfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_dfs.c

Contains SMB1 transaction2 DFS-related handlers.

`smb_com_trans2_report_dfs_inconsistency` is intentionally unimplemented and returns `SDRC_NOT_IMPLEMENTED`, matching CIFS guidance that clients should not send the reserved command and servers should report it as not implemented.

`smb_com_trans2_get_dfs_referral` implements DFS referral lookup over IPC only. It rejects non-IPC tree connections with access denied. For valid IPC requests it builds an `smb_fsctl_t` using `FSCTL_DFS_GET_REFERRALS`, transaction input counts, maximum output response size, request parameter mbuf, and response data mbuf. It delegates referral generation to `smb_dfs_get_referrals`.

The transaction response parameter block carries an API-level DOS error code derived from the NT status. On nonzero status it also raises the SMB error with that status and DOS error; otherwise referral data is already encoded in `xa->rep_data_mb`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_dfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_find.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_find.c

Implements SMB1 `TRANS2_FIND_FIRST2`, `TRANS2_FIND_NEXT2`, and `FIND_CLOSE2` directory enumeration. The file supports legacy and NT-style information levels, resume keys, close-on-EOS flags, backup intent, access-based enumeration interactions through lower layers, and exact wire encoding of returned entries.

`smb_find_args_t` carries fixed response size, info level, max count, flags, EOS state, last-name offset, and last resume key/name across enumeration helpers. `smb_trans2_find_max` limits the number of entries returned per request.

`FindFirst2` validates disk share use, decodes search attributes/count/flags/info level/path, rejects stream names, optionally switches to privileged backup credentials, computes fixed entry size, opens an `smb_odir_t`, encodes entries, handles no-match as `NT_STATUS_NO_SUCH_FILE`, optionally closes the search, and returns SID/count/EOS/EA error/last-name offset.

`FindNext2` decodes the existing search ID, count, info level, resume key, flags, and resume filename. It looks up the open directory through the tree with same-user enforcement, chooses continue-from-last or resume-by-name behavior, encodes more entries, optionally closes, and returns count/EOS/EA error/last-name offset. Comments document partial resume-by-name support: the server remembers the last returned name/key pair because arbitrary name resume is not generally possible without sorted directory storage.

`smb_trans2_find_entries` reads `smb_fileinfo_t` entries from the odir, encodes until count or output space is exhausted, patches the final `NextEntryOffset` to zero for modern levels, saves the last returned filename/cookie for future resume, probes one extra entry to detect EOS, and rewinds when an entry was read but not returned. `SMB_INFO_QUERY_EAS_FROM_LIST` currently returns an empty list because EAs are unsupported.

`smb_trans2_find_mbc_encode` handles all supported information levels, including legacy standard/EA-size, directory/full/id/both/name variants, and Mac HFS info sizing. It computes ASCII/Unicode name lengths, null terminators, 4-byte padding for modern levels, optional resume keys, 32-bit truncation for old size fields, short-name encoding, node IDs, timestamps, DOS attributes, and last-name offsets.

`FIND_CLOSE2` decodes the search ID, looks it up on the current tree, closes/releases the odir, and returns an empty SMB result.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_trans2_find.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree.c

Core SMB tree/share connection object management. The file defines the tree state machine, connection dispatch for disk/print/IPC shares, access checks, feature discovery, reference management, disconnect/deallocation, odir lookup, and enumeration/netinfo support.

`smb_tree_connect` applies a server threshold guard and calls `smb_tree_connect_core`. The core path lowercases the requested path, extracts and validates the share name, looks up the kernel share, rejects the print pseudo-share by name, enforces SMB3 encryption requirements when configured, and dispatches by share type to disk, IPC, or print handlers.

Disk tree connection validates service type, requires a configured root node, applies access checks, waits for durable-handle import to complete, builds optional-support flags for CSC/ABE/DFS/short names, allocates a tree, optionally invokes share exec-map hooks, and returns the TID. Print connection performs similar service/path/access handling with print enablement and pathname lookup. IPC connection validates service type, applies anonymous restrictions, and allocates a tree without an `snode`.

Access control combines anonymous/guest/admin-share checks, host-based share access, and share ACL access. Share ACL lookup uses `.zfs/shares/<share>` under the filesystem root when present; failures generally fall back to full access. Autohome shares grant only the owning UID.

`smb_tree_alloc` obtains a TID, gathers filesystem attributes for disk/print shares, initializes FID/ODID pools and open file/directory lists, sets state/refcount/access/resource metadata, records owner user references, applies read-only access masking, references the share root node, inserts into the session tree list, and increments server/session counters. `smb_tree_release` flushes deferred ofile/odir deletion queues, decrements references, and posts disconnected zero-ref trees for deferred deallocation. `smb_tree_dealloc` removes the tree from the session list, frees ID pools, releases root node and owner user, destroys locks/lists, and returns the object to cache.

`smb_tree_getattr`, `smb_tree_get_creation`, `smb_tree_get_volname`, and `smb_tree_get_flags` derive volume/create time, filesystem type, encryption setting, and capability flags such as ACLs, Unicode-on-disk, quotas, sparse, streams, readonly, DFS root, CATIA, continuous availability, oplocks, mount traversal, short names, case behavior, dirent flags, and ACL-on-create.

Other utilities include tree hold/internal hold, connected-state tests, PID-based close of files and searches, remote file close by unique ID, odir lookup with UID ownership enforcement, share connection logging, exec upcall metadata setup, and tree netconnect info encoding for user-space RPC consumers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree_connect.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree_connect.c

SMB1 protocol wrappers for tree connect, tree connect AndX, and tree disconnect. This file handles wire decode/encode and maps core tree statuses to legacy SMB errors, while `smb_tree.c` owns actual share connection logic.

`smb_tcon_puterror` translates core NT statuses into protocol-specific error classes/codes, including `ERRinvnetname`, `ERRaccess`, `ERROR_BAD_DEV_TYPE`, and generic server error.

`SMB_COM_TREE_CONNECT` pre-decodes path/password/service strings from the data block, initializes tree-connect arguments, starts DTrace probes, calls `smb_tree_connect`, and on success returns word count 2 with max buffer size and assigned TID.

`SMB_COM_TREE_CONNECT_ANDX` pre-decodes AndX command/offset, flags, password length and password bytes, path, and service. The command optionally disconnects the incoming TID first when `SMB_TCONX_DISCONECT_TID` is set, ignoring disconnect errors as required. It then connects the requested share, derives returned service string by tree type, and encodes one of three response formats: pre-NT dialect, NT dialect normal response, or extended response containing optional support, maximal access, and guest access.

`SMB_COM_TREE_DISCONNECT` is special because dispatch suppresses normal UID lookup. The pre-handler explicitly looks up UID and TID. The command returns `ERRinvnid` if either is invalid, sets `user_cr`, disconnects the tree, cancels outstanding requests for that tree, and returns an empty result.

The file also wraps each command in matching DTrace start/done probes.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_tree_connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_unlock_byte_range.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_unlock_byte_range.c

Implements legacy SMB1 `SMB_COM_UNLOCK_BYTE_RANGE`. The command unlocks a 32-bit byte range previously locked on a file handle.

The handler decodes FID, length, and offset from the parameter words, looks up the open file, rejects invalid handles, derives the SMB1 16-bit lock PID from `sr->smb_pid`, and calls `smb_unlock_range` with 64-bit offset and length conversions. If unlock fails, it reports `NT_STATUS_RANGE_NOT_LOCKED` / `ERROR_NOT_LOCKED`; otherwise it returns an empty SMB result.

The file also provides pre/post DTrace probe wrappers. The comments document SMB semantics that unlocking a range not locked should generate no protocol error, though this implementation maps non-success from `smb_unlock_range` to range-not-locked.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_unlock_byte_range.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_user.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_user.c

Core SMB user/session-logon object lifecycle. The file defines and implements user state transitions from logging on through logged on, logging off, logged off, and deferred deletion. It also owns credential privilege setup, admin detection, tree ownership accounting, netinfo encoding, and auth-logoff upcalls.

`smb_user_new` allocates a user from cache, assigns a UID from the session pool, creates an SMB2 session ID from the object address plus a low-bit generation counter, initializes state as `LOGGING_ON`, inserts into the session user list, increments server user counts, and cancels the session authentication timeout when the first user appears.

`smb_user_logon` transitions a logging-on user to logged-on, detaches auth socket/timeout, stores flags/domain/account/audit SID, duplicates strings, and calls `smb_user_setcred`. Blocking timeout cancellation and auth socket close happen outside the user mutex. `smb_user_logoff` handles logging-on and logged-on cases: it cancels pending auth resources, moves to `LOGGING_OFF`, disconnects owned trees for logged-on users, and notifies smbd of auth logoff unless the server is shutting down.

Reference management is state-aware. `smb_user_hold` only grants public holds for logged-on users, while `smb_user_hold_internal` is unconditional for internal ownership. `smb_user_release` flushes tree delete queues, decrements the refcount, and posts zero-ref logging-off users for deferred deletion. `smb_user_delete` removes the user from the session list, frees UID, schedules a session auth timeout if this was the last user and the session remains negotiated, synchronizes with the releasing mutex path, destroys credentials/strings/mutex, and frees the object.

Auth timeout handling uses `smb_user_auth_tmo` to allocate a synthetic request, take a user hold only if still logging on, and dispatch `smb_user_logoff_tq` to the worker taskq.

Credential setup maps SMB/Windows privileges to illumos privileges. Change-notify grants traverse bypass, take-ownership grants chown privileges, read/write file privileges grant DAC bypasses, and backup/restore create a privileged duplicate credential used for backup-intent access. `smb_user_has_security_priv` determines whether `ACCESS_SYSTEM_SECURITY` can be granted.

Other utilities include administrator SID/group detection, flexible user-name comparison (`name`, `domain\name`, `name@domain`), owned-tree count wait/broadcast support, user netinfo encoding for RPC, smbd auth-logoff door upcall throttling, and SID-based same-user comparison.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vops.c

Vnode/VFS adapter layer for SMB filesystem operations. Higher SMB service code is expected to go through `smb_fsop_*`, which then uses these `smb_vop_*` wrappers for local filesystem interaction with SMB-specific normalization.

Initialization allocates a lock-manager sysid and caller context used for range/share locking, sets an ignore PID, initializes CATIA translation tables, and tears them down in `smb_vop_fini`. Basic wrappers cover open, close, read, write, ioctl, zero-copy buffer request/return, fsync, statvfs, and checking for other opens or mappings.

Attribute handling is SMB-aware. `smb_vop_getattr` retrieves extended attributes when `VFSFT_XVATTR` is supported, maps readonly/hidden/system/archive/reparse/offline/sparse and creation time, falls back to mtime as creation time otherwise, and adjusts stream attributes so named streams inherit most metadata from the unnamed stream but use their own size. It also normalizes directories to size/allocation zero and one link, and ensures ordinary files have `FILE_ATTRIBUTE_NORMAL` when no DOS attributes are set. `smb_vop_setattr` masks settable DOS attributes, splits stream size changes from unnamed-stream metadata updates, builds `xvattr_t` when possible, and applies size to the stream vnode with `zone_kcred` when needed.

Name operations wrap lookup/create/remove/link/rename/mkdir/rmdir with case-insensitive flags and optional CATIA name conversion. Lookup handles empty names, `..` at share root, mount-root traversal races, optional returned on-disk names, privilege-based ACL-check skipping for traverse checks, and optional attribute fetch. Create works around filesystems that ignore nonzero size at create by setting size afterward.

Directory enumeration uses `VOP_READDIR` with `edirent_t` support when `VFSFT_DIRENTFLAGS` is available and access-based filtering when requested. Stream helpers map SMB named streams to extended attributes using `SMB_STREAM_PREFIX`, manage xattr directory lookup/creation, and strip/restore on-disk stream prefixes.

ACL helpers read/write either POSIX draft ACLs or ACE ACLs via `VOP_GETSECATTR`/`VOP_SETSECATTR`, detect ACL type through `_PC_ACL_ENABLED`, and compute effective access by probing every relevant ACE or Unix permission bit. `smb_vop_access` adds Windows delete semantics by checking parent `ACE_DELETE_CHILD` and parent list permission for read attributes.

Locking helpers translate SMB share modes into `VOP_SHRLOCK` structures and byte-range locks into mandatory `VOP_FRLOCK` calls when NBMAND is available. Advisory locks are only used when `smb_allow_advisory_locks` permits the dangerous fallback.

CATIA support maps Windows-incompatible UNIX filename characters to Unicode substitutes and back, including create/link/rename/mkdir rejection when reverse conversion would produce `/`. The lookup tables are initialized once and conversion routines preserve original names on decode/space failures.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vss.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vss.c

Implements SMB Volume Shadow Copy Service support for ZFS-style snapshots exposed through Windows `@GMT-YYYY.MM.DD-HH.MM.SS` tokens.

`smb_vss_enum_snapshots` handles `FSCTL_SRV_ENUMERATE_SNAPSHOTS` responses. It requires at least the 16-byte count response size, derives the mounted dataset path for the open file, and either returns only the snapshot count or queries and encodes a token list. Count/list/map operations are delegated to smbd through door upcalls. Encoded responses include returned count, token count, byte size, each GMT token in ASCII/Unicode form, and a final Unicode null for compatibility.

`smb_vss_lookup_nodes` resolves an active node to the corresponding node inside a requested snapshot. SMB1 supplies a GMT token string; SMB2+ uses the request timewarp timestamp. The function gets the current node mount path, maps the token/time to a snapshot name, obtains the filesystem root vnode, and calls `smb_vss_lookup_node`.

`smb_vss_lookup_node` builds `.zfs/snapshot/<snapname>/<relative path from fsroot to node>`, looks up the vnode under the filesystem root, and wraps it in an `smb_node_t`. It returns `ENOENT` if no corresponding snapshot node exists.

Token parsing helpers validate the exact `@GMT-NNNN.NN.NN-NN.NN.NN` format, find tokens in paths, extract the first token, and remove it from the original path so normal lookup proceeds against the non-token path. `smb_vss_extract_gmttoken` copies the fixed-size token into the caller buffer, null terminates it, removes it from the path, and returns `ENOENT` when no token is present.

The file depends on SMB door/XDR types for snapshot count/list/name mapping and assumes `.zfs/snapshot` layout for actual vnode lookup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_vss.c -->