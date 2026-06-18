# sources/distributed-fs/lustre-release/lustre/mdc/mdc_reint.c

## Purpose

`mdc_reint.c` implements MDC reintegration RPCs: metadata-modifying operations sent to MDTs through `MDS_REINT` or related reint formats. It covers setattr, create, unlink, link, rename/migrate, and file resync, plus shared early-lock-cancel helpers that gather local locks to cancel with a modifying request.

## Important APIs, Types, And Functions

The main public functions are `mdc_setattr()`, `mdc_create()`, `mdc_unlink()`, `mdc_link()`, `mdc_rename()`, `mdc_file_resync()`, `mdc_resource_cancel_unused_res()`, and `mdc_resource_cancel_unused()`. `mdc_reint()` is the shared synchronous send helper that sets the request import state, takes a modifying-RPC slot, queues the request, releases the slot, and validates that a successful reply contains `RMF_MDT_BODY`.

## Control Flow

Each operation computes a set of local LDLM locks to cancel early based on `md_op_data` flags and FIDs, allocates the operation-specific request format, sizes variable fields, optionally obtains SELinux policy data, prepares the request with `mdc_prep_elc_req()`, calls the corresponding packer from `mdc_lib.c`, sets reply sizes, and sends via `mdc_reint()`.

`mdc_setattr()` cancels update and sometimes lookup locks for the target FID, packs optional EA data and zero-length epoch/log-cookie fields, and treats `-ERESTARTSYS` as success after the RPC layer has handled recovery semantics. `mdc_create()` allocates a child FID if the caller did not, cancels parent update locks, packs name/EA/security/encryption data, and implements explicit retry for `-EINPROGRESS` by rebuilding the request as long as the import generation has not changed. Directory create replies with LMV EA are validated and saved into the request buffer for replay, then body LMV validity is cleared so initialization can be delayed to lookup.

`mdc_unlink()` cancels parent update locks and, for the child FID, either full inode locks or only ELC bits depending on dirty Data-on-MDT data. `mdc_link()` cancels update locks on source and parent. `mdc_rename()` cancels relevant source parent, target parent, source child lookup, and migration target ELC locks, selects migrate versus rename format, and routes BFL-capable renames to `MDS_IO_PORTAL` when supported. `mdc_file_resync()` packs `REINT_RESYNC`, optional mirror ID compatibility field, and a remote lease handle from the lease lock.

## State And Persistence Behavior

These operations mutate persistent MDT namespace, attributes, layout, and resync state. Locally, they consume modifying-RPC slots, may cancel local locks early, and return a held request pointer to callers for reply inspection and request lifecycle. Create can save reply LMV layout data for recovery replay. Resync includes lease-handle and mirror-ID state that affects persistent layout synchronization.

## Dependencies And Integration Points

The file depends on `mdc_lib.c` packers, LDLM resource cancellation, PTLRPC modifying-RPC slots, `mdc_fid_alloc()` from request setup, SELinux policy helpers, Lustre FID and request format definitions, and connection compatibility helpers such as `exp_connect_mirror_id_fix()`. It is wired into `mdc_md_ops` by `mdc_request.c`.

## Risks

The main risks are failure and retry semantics for modifying operations. Requests that return `-EINPROGRESS` must be rebuilt after dropping the old request, but only while the import generation is stable. Early lock cancellation must avoid canceling dirty DOM data incorrectly; unlink explicitly switches between full and ELC-only bits based on `CLI_DIRTY_DATA`. Several error paths allocate a request and policy object before packing, so leaks are possible if cleanup is missed. Rename portal selection is version/connection sensitive. `mdc_reint()` expects `RMF_MDT_BODY` on successful replies; format mismatches become `-EPROTO`.

## Test Signals

Tests should cover chmod/chown/truncate/setstripe setattr, create with caller-allocated and MDC-allocated FIDs, mkdir with LMV reply, create retry on `-EINPROGRESS`, unlink with dirty and clean DOM data, hard link, rename and migrate, resync with mirror ID compatibility, early-lock-cancel behavior with cancelset enabled/disabled, SELinux policy packing errors, and `-ERESTARTSYS` recovery paths.
