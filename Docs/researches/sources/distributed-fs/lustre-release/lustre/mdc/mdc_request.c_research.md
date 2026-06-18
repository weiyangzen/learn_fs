# sources/distributed-fs/lustre-release/lustre/mdc/mdc_request.c

## Purpose

`mdc_request.c` is the central MDC module implementation. It provides non-reint metadata RPCs, xattr operations, root and getattr lookup helpers, open/close replay management, directory page reads, statfs, HSM and quota ioctls, get_info/set_info dispatch, fsync/rmfid, import-event handling, FID allocation, llog setup, OBD/MD operation tables, changelog class allocation, and module init/exit.

## Important APIs, Types, And Functions

Major public or table-wired functions include `mdc_setup()`, `mdc_llog_finish()`, `mdc_fid_alloc()`, `mdc_set_open_replay_data()`, `mdc_replay_open()`, `mdc_commit_open()`, `mdc_save_lmm()` consumers, `mdc_create()`/reint functions through `mdc_md_ops`, and the `mdc_obd_ops`/`mdc_md_ops` tables. Internal functional areas include `mdc_get_root()`, `mdc_getattr()`/`mdc_getattr_name()`/`mdc_getattr_common()`, `mdc_xattr_common()` with `mdc_setxattr()`/`mdc_getxattr()`, `mdc_get_lustre_md()`, `mdc_close()`, directory read helpers (`mdc_getpage()`, `mdc_page_locate()`, `mdc_dirpage_add()`, `mdc_read_page()`), `mdc_statfs()`/async, ioctl helpers, `mdc_get_info()`/`mdc_set_info_async()`, `mdc_fsync()`, `mdc_rmfid()`, and `mdc_import_event()`.

## Control Flow

Startup runs `mdc_init()` as a late initcall: initializes libcfs, allocates the global changelog chrdev range, creates the changelog class, and registers the MDC OBD/MD type with `mdc_device_type`. Device setup later calls `mdc_setup()`, which runs common OSC setup, initializes tunables, sets Data-on-MDT defaults, registers cancel weighting and inode LVB ops, initializes changelog llog context, and registers the changelog char device.

Metadata reads use PTLRPC request capsules. `mdc_get_root()` sends `MDS_GET_ROOT`, optionally with a fileset, waits for a root FID, and checks subtree support after connect flags are known. `mdc_getattr()` and `mdc_getattr_name()` build getattrs, reserve layout/ACL/encryption fields, route plain getattr through the readpage portal to avoid modifying-RPC deadlocks, and retry with larger ACL buffers on `-ERANGE`. `mdc_xattr_common()` handles both `MDS_GETXATTR` and `MDS_REINT_SETXATTR`, packs names and values, sends SELinux policy data, and for modifying xattrs cancels local xattr locks early.

Open/close recovery is managed through `struct md_open_data`. Successful replayable opens get callback data and replay callbacks installed by `mdc_set_open_replay_data()`. `mdc_replay_open()` updates open handles in both live client handles and any already-built close request after a replay. `mdc_commit_open()` preserves committed open requests when needed for later close/eviction logic. `mdc_close()` selects close or close-intent format, may allocate volatile FIDs, packs lazy size/block updates if supported, fixes open replay state, sends through a modifying slot on the readpage portal, and handles committed-open `-ESTALE` as nonfatal.

Directory reads acquire a readdir intent lock, bind lock data to the inode, find a cached hash page, or issue `MDS_READPAGE` bulk RPCs. `mdc_getpage()` handles bulk sink setup, timeout resend with backoff, unwraps secure bulk data, and validates transferred bytes. Page helpers adapt LU page layout to native page size, add folios into the page cache by hash, and handle hash-collision edge cases.

Ioctl and info paths fan out to FID2PATH, HSM progress/state/request/copytool registration, quota, statfs, swap layouts, import recovery, active-state changes, and connection flags. HSM copytool messages are swabbed if needed and broadcast through kernelcomm; copytools are re-registered in a background thread on import active events. `mdc_import_event()` resets grants, flushes sequence clients, cleans LDLM/OSC state on invalidate, notifies observers, initializes grants/OCD-derived EA sizes, and triggers KUC re-registration after reconnect.

## State And Persistence Behavior

Persistent state lives on MDTs and llogs. Local MDC state includes import connection data, max/default MDS EA sizes, open replay records, close request references, directory page cache, LDLM namespace inode LVB pointers, changelog llog context, HSM copytool registrations, grant accounting, sequence client state, and global changelog chrdev registration. `mdc_get_info()`/`set_info_async()` also maintain local read-only flags and EA-size configuration. `mdc_rmfid()` submits batched FID removals asynchronously and copies per-FID result codes in its interpret callback.

## Dependencies And Integration Points

This file is the integration hub for Linux module/device APIs, PTLRPC, LDLM, OBD class operations, OSC common code, CL page cache helpers, Lustre llog, LMV/LOV metadata parsing, ACL/encryption/security contexts, quota, HSM kernelcomm, fid/seq allocation, and lprocfs. It registers the operation tables consumed by upper llite/LMV layers and delegates modifying namespace operations to `mdc_reint.c`, intent locking to `mdc_locks.c`, packing to `mdc_lib.c`, and device/DOM behavior to `mdc_dev.c`.

## Risks

The file has broad blast radius. Open/close replay uses multiple references and callbacks; incorrect ordering can leak requests, lose close handles, or replay stale creates. Directory hash page caching has explicit collision caveats. Bulk readdir resend must avoid infinite retry while preserving interruptibility. HSM ioctl paths copy user-derived variable data into request buffers and need size validation from upper layers. Import-event cleanup must coordinate LDLM namespace cleanup, OSC IO unplugging, grant reset, and observer notification. Module init error paths must unregister chrdev/class resources exactly once.

## Test Signals

High-value tests include root/fileset mount, getattr by FID/name with ACL `-ERANGE`, encrypted-file context fetch, getxattr/listxattr/setxattr edge cases, open replay through reconnect, close after committed open and `-ESTALE`, directory read cache and hash collision behavior, statfs old/new formats, FID2PATH partial `-EREMOTE`, HSM copytool registration/reregister/progress/state/request/data-version, quota iteration, swap layouts with early cancels, import event transitions, FID allocation after reconnect, module setup/fini, and changelog cdev integration.
