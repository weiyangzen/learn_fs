# sources/distributed-fs/lustre-release/lustre/mdc/mdc_internal.h

## Purpose

`mdc_internal.h` is the private interface for Lustre's Metadata Client implementation. It ties together request-packing helpers, lock/intents, reintegration operations, request/module setup, changelog char-device lifecycle, ACL unpacking, Data-on-MDT device hooks, and small inline helpers shared across `mdc_*.c` files.

## Important APIs, Types, And Functions

The header declares request packers implemented by `mdc_lib.c`: `mdc_pack_body()`, `mdc_swap_layouts_pack()`, `mdc_readdir_pack()`, `mdc_getattr_pack()`, `mdc_setattr_pack()`, `mdc_create_pack()`, `mdc_open_pack()`, security/encryption/SELinux packing helpers, unlink/link/rename/migrate packers, and `mdc_close_pack()`. These functions standardize how MDC fills `req_capsule` fields for MDS/MDT RPCs.

Lock and intent declarations include `mdc_set_lock_data()`, `mdc_null_inode()`, `mdc_intent_lock()`, `mdc_enqueue()`, `mdc_enqueue_async()`, `mdc_resource_cancel_unused_res()`, `mdc_resource_cancel_unused()`, `mdc_cancel_unused()`, `mdc_revalidate_lock()`, `mdc_intent_getattr_async()`, `mdc_batch_add()`, and `mdc_lock_match()`. Reint and request declarations include create/link/rename/setattr/unlink/file-resync operations, `mdc_fid_alloc()`, `mdc_setup()`, `mdc_llog_finish()`, open replay helpers, `mdc_save_lmm()`, `mdc_commit_open()`, and `mdc_replay_open()`.

Changelog declarations expose `MDC_CHANGELOG_DEV_COUNT`, `MDC_CHANGELOG_DEV_NAME`, `mdc_changelog_class`, `mdc_changelog_dev`, `mdc_changelog_minor_idr`, `mdc_changelog_cdev_init()`, and `mdc_changelog_cdev_finish()`. Data-on-MDT declarations expose `mdc_device_type`, LDLM AST callbacks, `mdc_fill_lvb()`, and `mdc_finish_enqueue()`.

Inline helpers are `mdc_prep_elc_req()` for early-lock-cancel request preparation, an ACL unpacking stub when POSIX ACLs are disabled, and `mdc_body2lvb()` for copying DOM size/time/block fields from `struct mdt_body` to `struct ost_lvb`. The header also defines default and maximum inline reply sizes for Data-on-MDT.

## Control Flow

The header itself has no runtime control flow, but it encodes cross-file layering. Request-building code flows from callers in `mdc_request.c`, `mdc_locks.c`, and `mdc_reint.c` into packers in `mdc_lib.c`. Lock and intent operations in `mdc_locks.c` call replay and request helpers from `mdc_request.c`, and Data-on-MDT device code in `mdc_dev.c` calls `mdc_finish_enqueue()` to share LDLM intent completion logic. Setup flows through `mdc_setup()` into llog/changelog/device initialization.

## State And Persistence Behavior

The header declares shared module-level changelog device state and the MDC LU device type, but does not define persistent storage. `mdc_body2lvb()` is stateful in the sense that it translates authoritative MDT reply body values into client lock value blocks used for cache coherence. The changelog device globals represent kernel registration state for all MDC changelog devices.

## Dependencies And Integration Points

The header includes `<lustre_mdc.h>` and assumes Lustre core types such as `struct req_capsule`, `struct md_op_data`, `struct ptlrpc_request`, `struct obd_export`, LDLM lock types, `struct lu_fid`, and `struct sptlrpc_sepol`. It is the internal ABI among MDC compilation units and connects MDC to LDLM, PTLRPC, OBD, LLOG, ACL, Data-on-MDT, and Linux device-class functionality.

## Risks

Because this header is the private contract, signature drift can silently break multiple source files. `mdc_prep_elc_req()` hardcodes `LUSTRE_MDS_VERSION` and MDS early-cancel behavior, so callers must use it only for compatible opcodes. `mdc_body2lvb()` asserts `OBD_MD_DOM_SIZE`, making missing DOM size data a hard failure in paths that expect it. Changelog minor count is tied to `LMV_MAX_STRIPE_COUNT`, so scaling or namespace changes must keep the user-visible char-device limit in mind.

## Test Signals

Build coverage is the primary signal for this file because it coordinates many prototypes. Runtime signals come indirectly from tests of metadata RPC packing, intent locking, reint operations, changelog char devices, ACL-enabled/disabled builds, and DOM LVB update paths. Configuration matrix tests should include `CONFIG_LUSTRE_FS_POSIX_ACL` on and off.
