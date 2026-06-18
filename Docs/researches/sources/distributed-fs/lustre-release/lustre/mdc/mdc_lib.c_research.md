# sources/distributed-fs/lustre-release/lustre/mdc/mdc_lib.c

## Purpose

`mdc_lib.c` centralizes client-side packing of MDC request capsules for metadata RPCs. It translates Linux/VFS credentials, attributes, open flags, FIDs, names, security contexts, encryption contexts, SELinux policy data, layout payloads, close intents, and reint records into the wire structures consumed by MDT handlers.

## Important APIs, Types, And Functions

Generic body helpers are `__mdc_pack_body()` and `mdc_pack_body()`, which populate `struct mdt_body` with current credentials, capabilities, optional FID, EA size, flags, and project ID. `mdc_pack_name()` validates and copies single path components into request fields. Security helpers are `mdc_file_secctx_pack()`, `mdc_file_encctx_pack()`, and `mdc_file_sepol_pack()`.

Operation-specific packers include `mdc_readdir_pack()`, `mdc_create_pack()`, `mdc_open_pack()`, `mdc_setattr_pack()`, `mdc_unlink_pack()`, `mdc_link_pack()`, `mdc_rename_pack()`, `mdc_migrate_pack()`, `mdc_getattr_pack()`, `mdc_swap_layouts_pack()`, and `mdc_close_pack()`. Internal translators include `set_mrc_cr_flags()` for 64-bit create/open flags split into low/high wire fields, `mds_pack_open_flags()` for Linux open mode to MDS flags, `mdc_attr_pack()` for VFS `ia_valid`/extended validity to MDS setattr flags, `mdc_setattr_pack_rec()`, `mdc_ioepoch_pack()`, and `mdc_close_intent_pack()`.

## Control Flow

Most functions assume the caller has already selected a request format and set capsule field sizes. They fetch client-side fields with `req_capsule_client_get()`, fill fixed wire records, and copy optional variable payloads. Create/open packing writes `RMF_REC_REINT`, name, layout/default-LMV/symlink data, file security context, encryption context, and SELinux policy. Getattr packing writes `RMF_MDT_BODY`, optional name, FID pairs, cross-reference/namehash validity bits, and requested EA size. Readdir uses `mbo_size` and `mbo_nlink` as overloaded offset/size fields.

Setattr packing converts VFS attr flags, IDs, sizes, timestamps, blocks, project ID, and lazy-size/lazy-blocks indicators, then optionally copies or constructs LOV EA removal data. Close packing reuses setattr record packing, clears zero-atime updates to avoid old-server atime corruption, packs the open handle into `RMF_MDT_EPOCH`, and adds close-intent payloads for release, migration, layout split/swap, PCC attach, or resync completion.

## State And Persistence Behavior

This file does not retain state. Its outputs become persistent or replayable only after callers send requests and, where needed, save request buffers for replay. It uses current task credentials and capabilities at pack time, so packed records reflect the caller's security context. Project ID is written into the Lustre message when the project ID is valid and a PTLRPC request is present.

## Dependencies And Integration Points

Dependencies include Linux user namespace credential conversion, current umask/capability APIs, Lustre request capsules, MDT wire record definitions, LOV/LMV layout structures, security policy helpers, and CL object headers. It is used by `mdc_reint.c` for modifying metadata RPCs, `mdc_locks.c` for intent-open/create/getattr/getxattr/layout packing, and `mdc_request.c` for getattr, xattr, close, root, readdir, HSM, fsync, and ioctl-related requests.

## Risks

The main risks are mismatched capsule sizes, stale wire-format compatibility, and incorrect flag translation. Many functions rely on `LASSERT()` rather than recoverable errors for bad caller setup. `mdc_pack_name()` detects concurrent rename length mismatches but still copies the current string. `mdc_open_pack()` always includes `MDS_OPEN_DEFAULT_LMV`, so server-side interpretation must remain compatible. Close intent packing multiplexes several meanings through `struct close_data`; incorrect bias combinations would pack incompatible fields.

## Test Signals

Tests should validate wire records for create, mkdir with LMV, symlink/layout data, open with delayed create/PCC/default LMV, getattr by name/FID, setattr with mode/owner/size/lazy-size/project ID, xattr/security/encryption contexts, unlink/link/rename/migrate, close release/resync/swap/split/PCC, and readdir offset/size packing. Cross-version tests are important for atime clearing, flag high/low packing, and optional fields.
