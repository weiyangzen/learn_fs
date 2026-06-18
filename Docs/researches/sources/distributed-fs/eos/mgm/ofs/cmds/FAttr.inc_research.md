# Research: sources/distributed-fs/eos/mgm/ofs/cmds/FAttr.inc

## Purpose

`FAttr.inc` adapts EOS extended-attribute operations to XRootD's `XrdSfsFACtl` filesystem-attribute API. It reports support limits, maps requests to EOS attribute get/list/set/delete helpers, serializes names and values into XRootD-managed buffers, and returns per-attribute status codes.

## Important APIs, Types, and Functions

- Anonymous `GetFABuff(XrdSfsFACtl&, int sz)` allocates an `XrdSfsFABuff`, prepends it to `faCtl.fabP`, and reserves `sz` bytes.
- `XrdMgmOfs::FAttr(XrdSfsFACtl* faReq, XrdOucErrInfo&, const XrdSecEntity*)` handles support info and `faGet`, `faLst`, `faSet`, and `faDel`.
- Request-to-access mapping uses `AOP_Read` for get/list and `AOP_Update` for set/delete.
- It delegates to `_attr_get`, `_attr_ls`, `_attr_set`, and `_attr_rem`.

## Control Flow

If `faReq` is null, the function returns support limits (`usxMaxNsz`, `usxMaxVsz`) through the error environment or `ENOTSUP` if no env exists. Otherwise it derives path and CGI info from `faReq`, maps identity, applies namespace mapping and external authorization, and switches on request type.

For get, it strips any configured name prefix from requested attr names, fetches values one by one, records per-entry `faRC`, allocates one contiguous values buffer, and points `XrdSfsFAInfo::Value` into it. For list, it loads all attrs, allocates one buffer for null-terminated keys, optionally allocates another buffer for values when `retval` is set, and fills `faReq->info`. For set/delete, it loops over each attr, strips prefix, delegates to low-level mutation, and stores per-entry errno in `faRC`.

## State and Persistence Behavior

The adapter itself owns only response buffers allocated with `malloc` or `new`; XRootD owns eventual cleanup according to `XrdSfsFACtl` conventions. Set/delete persist changes through `Attr.inc` helpers, including audit and FUSE refresh side effects. Get/list are read-only.

## Dependencies and Integration Points

Dependencies include XRootD `XrdSfsFACtl`, EOS identity mapping, namespace mapping macros, external authorization, `Attr.inc` low-level helpers, and XRootD attr-size constants. It integrates modern xattr clients with EOS's older attr implementation.

## Risks and Edge Cases

- `pfx_len` is computed with `sizeof(faReq->nPfx)`, which is the fixed array size, not the runtime prefix string length; this needs tests because prefix stripping can be wrong if `nPfx` is not sized as intended.
- Value serialization for get/list does not null-terminate values; consumers must use `VLen`.
- Allocation failures must leave a consistent `faReq` state and return `SFS_ERROR`.
- List with values creates two buffers and overwrites `ptr` for the second; buffer ordering matters to cleanup.
- Delegated attr operations may return `SFS_ERROR` while overall set/delete loops continue and report per-entry `faRC`.

## Test Signals

Tests should cover support-info query, missing error env, get/list/set/delete with multiple attrs, prefix stripping, list with and without `retval`, binary/non-null-terminated values, allocation failure injection, per-entry status, hidden obfuscation key inheritance from `_attr_ls`, and security checks for update versus read.
