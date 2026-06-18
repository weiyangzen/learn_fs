# Group Research: group_837_linux_sources_os_linux_linux_fs_smb_client_trace_h_sources_os_linux__dba118c60896

This group covers Linux SMB/CIFS client tracing, transport/send-receive paths, UNC parsing, Windows-compatible UTF-16 uppercasing, CIFS/SMB xattr handlers, and shared SMB common wire definitions for SMB1, SMB2/3, FSCC, and MD4.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/trace.h -->
# File Research: sources/os/linux/linux/fs/smb/client/trace.h

## Scope
Read completely: 1,968 lines. This header defines the CIFS/SMB client tracepoint surface for ftrace/perf-style observability. It contains trace enums, enum-to-string mappings, event classes, concrete `TRACE_EVENT`/`DEFINE_EVENT` instances, and the final `trace/define_trace.h` inclusion.

## Purpose
`trace.h` is the central tracepoint declaration file for the SMB client. It exposes structured diagnostics for I/O, copy offload, file handle operations, locks, query/set info, compounds, command status, MID lifecycle, tree connect, opens, leases, connection setup, session setup, reconnects, ioctls, shutdown, credit accounting, Kerberos upcalls, tcon refcounts, read/write credit accounting, and generic EIO classification.

## Main Trace Domains
- EIO classification: `smb_eio_traces` enumerates many validation and protocol failure labels used by `smb_EIO*()` helpers throughout the client.
- Read/write credits: `smb3_rw_credits_traces` classifies credit transitions for netfs-style read/write subrequests.
- Tcon refs: `smb3_tcon_ref_traces` classifies tree connection refcount get/put/free observations.
- I/O events: `smb3_read_*`, `smb3_write_*`, `smb3_query_dir_*`, `smb3_zero_*`, and `smb3_falloc_*`.
- Copy/clone events: `smb3_copychunk_*` and `smb3_clone_*`.
- Handle events: flush, close, oplock-not-found, lock enter/done/error/cached, and lock conflicts.
- Info and compound events: query/set info, notify, hardlink, rename, unlink, EOF, reparse, WSL EA, mkdir, tree disconnect, mknod.
- Command/MID events: command enter/done/error, session expiry, slow responses, function enter/exit, sync errors.
- Session/transport events: connect, SMB Direct connect, Kerberos auth, key expiry, reconnect, missing session.
- Admin/control events: ioctl, unsupported ioctl, shutdown, shutdown error.
- Credit events: invalid credits across reconnect, timeout, insufficient credits, add/adjust/header/nonblocking/pending/wait/overflow/set credits.

## Structure
The file follows Linux tracepoint conventions:
- Defines `TRACE_SYSTEM cifs`.
- Uses `EM`/`E_` macro lists to define enums once, export enum values with `TRACE_DEFINE_ENUM`, and generate symbolic print mappings.
- Uses `DECLARE_EVENT_CLASS` for repeated payload shapes and small `DEFINE_*` wrappers for concrete event names.
- Uses direct `TRACE_EVENT` for bespoke payloads such as lock conflicts, cached opens/closes, Kerberos auth, tcon refs, read/write credits, and EIO labels.
- Ends with `TRACE_INCLUDE_PATH .`, `TRACE_INCLUDE_FILE trace`, and `#include <trace/define_trace.h>`.

## Key Payload Patterns
Trace records consistently include SMB identifiers:
- `xid` for client transaction tracking.
- `sesid`, `tid`, and `fid` for SMB session/tree/file handle identity.
- `mid`, `cmd`, and `status` for SMB2 command response flow.
- offsets and lengths for I/O, zeroing, copy, clone, and locks.
- `conn_id`, `hostname`, socket address, and current MID for connection and credit traces.
- lease keys, lease state, flags, and epoch for lease break/ack paths.

## Integration Points
This file is included indirectly by SMB client C files that emit tracepoints. It is tightly coupled to:
- `transport.c` for send, reconnect, MID, credit, and read receive errors.
- `smb2ops.c` for SMB2/3 credits, copychunk, clone, leases, encryption receive, and compound paths.
- `inode.c`, `link.c`, `reparse.c`, `ioctl.c`, and `xattr.c` through EIO labels and operation-specific trace events.
- CIFS stats and debugging paths that use slow-response and credit tracepoints.

## Notable Behaviors
- EIO labels make otherwise generic `-EIO` failures distinguishable by protocol validation site.
- Kerberos auth trace includes pid, uid, cruid, host, user, address, selected security flavor, upcall target, and rc.
- `smb3_rw_credits` traces carry both request/subrequest ids and server credit pool state.
- `smb3_tcon_ref` traces expose refcount lifecycle events for diagnosing mount/session/tcon lifetime bugs.
- The copy-range trace print format stores both source and target FIDs, but the `TP_printk` arguments print `target_fid` in the source-FID field as well. This affects trace readability, not protocol behavior.

## Risks And Review Focus
- Tracepoint payload layouts are a userspace ABI-like observability surface; changes can break tracing scripts.
- Event classes must keep types aligned with call sites, especially for FIDs and endianness-neutral values.
- EIO enum additions should preserve symbolic mapping consistency through all three macro phases.
- Trace strings that include usernames, hostnames, paths, and Kerberos details can expose sensitive operational metadata when tracing is enabled.

## Research Takeaways
`trace.h` is not protocol logic, but it is critical for diagnosing the SMB client. It provides the vocabulary used to distinguish credit starvation, malformed responses, reconnect races, lease issues, failed FSCTLs, xattr/ACL validation, and encrypted/large-read receive failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/transport.c -->
# File Research: sources/os/linux/linux/fs/smb/client/transport.c

## Scope
Read completely: 1,291 lines. This file implements core SMB client transport mechanics: socket/RDMA sends, request credit reservation, MID allocation lifecycle integration, compound send/receive, cancellation, response waiting, channel selection, and large read response handling.

## Purpose
`transport.c` is the generic send/receive layer below SMB1 and SMB2/3 operation code. Higher-level protocol helpers build `struct smb_rqst` arrays, then this layer reserves credits, creates pending MID entries, serializes signing/sending under server locking, waits for demultiplexed responses, transfers response buffer ownership, and cleans up MIDs.

## Main Interfaces
- MID lifecycle: `cifs_wake_up_task()`, `__release_mid()`, `delete_mid()`.
- Sending: `smb_send_kvec()`, `smb_rqst_len()`, `__smb_send_rqst()`, internal `smb_send_rqst()`.
- Credits and waits: `wait_for_free_request()`, `wait_for_response()`, `cifs_wait_mtu_credits()`.
- Async calls: `cifs_call_async()`.
- Sync result handling: `cifs_sync_mid_result()`.
- Channel selection: `cifs_pick_channel()`.
- Sync/compound calls: `compound_send_recv()`, `cifs_send_recv()`.
- Receive discard/read path: `cifs_discard_remaining_data()`, `cifs_readv_receive()`.

## Send Path
`__smb_send_rqst()` handles the physical send path:
- Uses SMB Direct/RDMA via `smbd_send()` when enabled.
- Checks missing socket and fatal pending signals before starting.
- Corks TCP while sending the RFC1002 marker plus all request vectors/iter payloads.
- Blocks signals while the packet is being sent to avoid partial sends caused by interrupted syscall context.
- Sends the 4-byte RFC1002 length marker, then request kvecs, then optional iterator data.
- Uncorks TCP and signals reconnect on partial sends so the server discards incomplete SMB frames.
- Normalizes most socket send errors to `-ECONNABORTED` and requests reconnect.

`smb_send_kvec()` performs the low-level `sock_sendmsg()` loop with retry behavior:
- Uses `MSG_DONTWAIT` when `server->noblocksnd` is set.
- Retries `-EAGAIN` and `-EINTR` with pending task work.
- Bounds retry time to about 15 seconds.
- Treats zero-byte sends as retryable but unusual.

`smb_send_rqst()` wraps this for compression and encryption:
- `CIFS_COMPRESS_REQ` delegates to `smb_compress()`.
- Plain requests go directly to `__smb_send_rqst()`.
- `CIFS_TRANSFORM_REQ` prepends an SMB3 transform header, calls dialect `init_transform_rq`, sends the transformed compound, then frees transformed request state.

## Credit Handling
`wait_for_free_credits()` reserves credits before sending:
- Selects the relevant credit field with `server->ops->get_credits_field()`.
- Nonblocking operations, especially oplock breaks, can consume a credit immediately.
- Blocking waiters sleep on `server->request_q` until enough credits are available or timeout/signal/exiting state occurs.
- Single-credit normal requests avoid starving compounds by reserving the last `MAX_COMPOUND` credits when many requests are already in flight.
- Reconnect instance is returned to callers so stale credits can be detected before send.

`wait_for_compound_request()` handles multi-request compounds:
- If insufficient credits and nothing is in flight, returns `-EDEADLK` rather than waiting forever.
- Otherwise waits up to 60 seconds for the compound credit set.

The generic `cifs_wait_mtu_credits()` stub simply reports one byte count as the transfer size and zero explicit credits; SMB2/3 dialect code overrides large-MTU credit accounting elsewhere.

## MID And Response Flow
`cifs_call_async()`:
- Reserves or consumes existing credits.
- Locks the server send path.
- Rejects credits from an old reconnect instance.
- Calls dialect `setup_async_request()`.
- Enqueues the MID on `pending_mid_q`, sets callbacks/state, saves send time, sends the request, and rolls back MID/sequence state on failure.

`compound_send_recv()`:
- Initializes response buffer types.
- Validates session/server state and reserves credits for all compound parts.
- Serializes setup and send under `cifs_server_lock()`.
- Sets up one MID per request, with callbacks that return credits for each part and wake the caller only on the last response.
- Sends all requests as one compound.
- Updates SMB3.1.1 preauth hash for negotiate/session setup traffic.
- Waits for all MID responses.
- On interrupted wait, sends CANCEL requests and installs cancellation callbacks.
- Calls `cifs_sync_mid_result()` and dialect `check_receive()` for each response.
- Transfers response buffers to caller-owned `resp_iov` when requested.
- Deletes non-cancelled MIDs at exit.

`cifs_sync_mid_result()` maps MID states:
- `MID_RESPONSE_READY` succeeds.
- `MID_RETRY_NEEDED` maps to `-EAGAIN`.
- malformed response maps through an EIO trace.
- shutdown maps to `-EHOSTDOWN`.
- `MID_RC` returns the stored MID rc.
- unknown states are dequeued and treated as invalid.

## Channel Selection
`cifs_pick_channel()` selects an SMB multichannel transport:
- Walks `ses->chans` under `chan_lock`.
- Skips null, terminating, and reconnect-needed channels.
- Chooses the least-loaded eligible channel by `server->in_flight`.
- Uses a round-robin start index through `ses->chan_seq`.
- Falls back to primary channel if none else is eligible.

## Large Read Receive
`cifs_readv_receive()` handles READ response payload delivery into a netfs/CIFS I/O subrequest:
- Reads the rest of the READ response header into `server->smallbuf`.
- Detects session expiry and status-pending interim responses.
- Sets up an iov for signature/credit processing.
- Maps SMB status to Linux error.
- Validates that enough READ response header arrived.
- Validates data offset against the current read position and small buffer limit.
- Reads padding/junk before the data payload.
- Uses dialect read-data length helpers, with SMB Direct RDMA memory-registration handling when configured.
- Reads payload into `rdata->subreq.io_iter`.
- Discards any trailing data before dequeuing the MID.
- Marks malformed reads through EIO trace helpers.

## State And Synchronization
Important lock domains:
- `server->srv_mutex`/`cifs_server_lock()` serializes signing and socket send ordering.
- `server->req_lock` protects credits and `in_flight`.
- `server->mid_queue_lock` protects the pending MID queue and MID deletion state.
- `mid->mid_lock` protects wait cancellation callback changes.
- `ses->chan_lock` protects multichannel channel selection.
- `ses->ses_lock` protects session status checks for preauth hash updates.

## Error Handling
The file is defensive about:
- stale credits across reconnect instances.
- partial sends requiring reconnect.
- invalid MID states.
- compound send failures requiring MID rollback and credit return.
- interrupted waits and cancellation ownership.
- malformed READ responses, short headers, overlarge offsets, and length overflows.
- server exiting state before credit waits.

## Risks And Review Focus
- Credit accounting and reconnect instance checks are correctness-critical; leaking or double-returning credits can deadlock or overload sessions.
- MID ownership is subtle when waits are cancelled because demultiplex callbacks may release cancelled MIDs asynchronously.
- Compound response ownership depends on `resp_iov`, `resp_buf_type`, and `CIFS_NO_RSP_BUF`; mistakes can leak or double-free SMB buffers.
- Partial send handling must always reconnect, since a later SMB frame could otherwise be interpreted as the remainder of a broken frame.
- Read receive validation is security-sensitive because it consumes server-provided offsets and lengths.

## Research Takeaways
`transport.c` is the SMB client’s concurrency and flow-control core. It ties together credits, MIDs, reconnects, signing/encryption send serialization, compound response demultiplexing, cancellation, and large read payload delivery.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/unc.c -->
# File Research: sources/os/linux/linux/fs/smb/client/unc.c

## Scope
Read completely: 69 lines. This small file provides helper parsing for UNC strings.

## Purpose
`unc.c` extracts the server hostname and share name from CIFS/SMB UNC paths. The helpers allocate newly owned strings for callers.

## Main Interfaces
- `extract_hostname(const char *unc)`
- `extract_sharename(const char *unc)`

## Behavior
`extract_hostname()`:
- Rejects UNC strings shorter than three bytes.
- Skips leading backslashes.
- Requires a backslash delimiter between hostname and share.
- Allocates and returns a NUL-terminated copy of the hostname.
- Returns `ERR_PTR(-EINVAL)` for malformed input and `ERR_PTR(-ENOMEM)` for allocation failure.

`extract_sharename()`:
- Assumes the UNC starts with two leading separator characters and starts parsing at `unc + 2`.
- Finds the next backslash separator.
- Duplicates everything after that separator as the share string.
- Returns `ERR_PTR(-EINVAL)` or `ERR_PTR(-ENOMEM)` on failure.

## Integration Points
These helpers are used by CIFS mount/session setup and UNC normalization paths that need separate server/share fields from a canonical `\\server\share...` style string.

## Notable Behaviors
- Both helpers assume backslash separators.
- `extract_hostname()` tolerates more than two leading backslashes by skipping all initial `\\` characters.
- `extract_sharename()` is stricter in practice because it starts at `unc + 2`; callers must pass a valid canonical UNC string.
- Returned strings must be freed by the caller.

## Risks And Review Focus
- Input validity assumptions differ between hostname and sharename extraction.
- `extract_sharename()` does not explicitly check minimum length before `unc + 2`; it depends on callers providing valid UNC input.
- These helpers do not trim a path after the share; if the input contains `\\server\share\path`, `extract_sharename()` duplicates `share\path`, not just `share`.

## Research Takeaways
`unc.c` is a narrow allocation/parsing utility. Its correctness depends mostly on callers passing normalized UNC strings and knowing whether they need only a share component or a share-plus-path suffix.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/unc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/winucase.c -->
# File Research: sources/os/linux/linux/fs/smb/client/winucase.c

## Scope
Read completely: 649 lines. This file is a generated/static Windows-compatible UTF-16 uppercase mapping table plus one lookup function.

## Purpose
`winucase.c` implements `cifs_toupper()`, a Unicode uppercase conversion helper matching Microsoft’s Windows 8 uppercase mapping table. SMB clients need Windows-compatible case folding for case-insensitive comparisons and name handling.

## Data Structure
The file defines second-level 256-entry mapping tables for selected high-byte ranges:
- `t2_00`
- `t2_01`
- `t2_02`
- `t2_03`
- `t2_04`
- `t2_05`
- `t2_1d`
- `t2_1e`
- `t2_1f`
- `t2_21`
- `t2_24`
- `t2_2c`
- `t2_2d`
- `t2_a6`
- `t2_a7`
- `t2_ff`

`toplevel[256]` maps the high byte of a UTF-16 code unit to one of those second-level tables or `NULL`.

## Main Interface
`wchar_t cifs_toupper(wchar_t in)`:
- Extracts the upper byte of the input code unit.
- Looks up the relevant second-level table in `toplevel`.
- If no table exists, returns the original input.
- Extracts the lower byte and reads the mapped uppercase code unit.
- If the table entry is nonzero, returns it; otherwise returns the original input.

## Source And Generation
Comments state the tables were converted from Microsoft’s documented Windows 8 uppercase mapping table using `winucase_convert.pl`. This explains why the data is table-driven rather than using generic kernel NLS case conversion.

## Integration Points
The helper is part of CIFS Unicode handling and is used by name comparison/hash code that needs Windows/SMB-compatible uppercase behavior. It includes `<linux/nls.h>` and exposes a prototype before the definition to quiet sparse.

## Notable Behaviors
- Only single UTF-16 code units are mapped; this is not full Unicode case folding with multi-codepoint expansions.
- Zero in a table means “no mapping”; it does not map to NUL.
- Most high-byte ranges have no table and therefore return identity.
- ASCII lowercase maps to uppercase through `t2_00`.
- Latin, Greek, Cyrillic, Armenian, Georgian, enclosed alphanumerics, Glagolitic/Coptic-style ranges, Latin Extended ranges, and fullwidth ASCII ranges are represented where present in the Windows table.

## Risks And Review Focus
- The table must remain synchronized with SMB/Windows semantics, not necessarily Linux locale behavior.
- Because zero means no mapping, the data generator must avoid encoding any real uppercase mapping to codepoint zero.
- `wchar_t` width assumptions matter; this operates on 16-bit-style code units in SMB Unicode paths.
- Manual edits to the table are risky; regeneration from a known source is safer.

## Research Takeaways
`winucase.c` is a deterministic compatibility table. The logic is simple, but the data is protocol-important because case-insensitive SMB name behavior should match Windows servers closely.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/winucase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/client/xattr.c -->
# File Research: sources/os/linux/linux/fs/smb/client/xattr.c

## Scope
Read completely: 535 lines. This file implements CIFS/SMB VFS extended attribute handlers, including user EAs, OS/2-style aliases, DOS attribute pseudo-xattrs, creation-time pseudo-xattrs, and CIFS/SMB3 security descriptor xattrs.

## Purpose
`xattr.c` connects Linux xattr VFS operations to SMB server capabilities. It provides get/set/list handlers and exports `cifs_xattr_handlers[]` for CIFS inode/superblock operations.

## Xattr Names And Handler Classes
Pseudo/user names:
- `user.cifs.dosattrib`
- `user.cifs.creationtime`
- `user.smb3.dosattrib`
- `user.smb3.creationtime`

Security descriptor names:
- `system.cifs_acl`: DACL only.
- `system.cifs_ntsd`: owner/group plus DACL.
- `system.cifs_ntsd_full`: owner/group, DACL, and SACL.
- `system.smb3_acl`: DACL-only alias.
- `system.smb3_ntsd_sacl`: SACL only.
- `system.smb3_ntsd_owner`: owner/group only.
- `system.smb3_ntsd`: owner/group plus DACL alias.
- `system.smb3_ntsd_full`: full descriptor alias.

Handler flags distinguish `XATTR_USER`, CIFS ACL, POSIX ACL slots, and NTSD variants.

## Set Path
`cifs_xattr_set()`:
- Acquires a tcon link from the superblock.
- Gets an XID and builds a full path from the dentry.
- Rejects EA values larger than `CIFSMaxBufSize`.
- For user pseudo-xattrs:
  - `cifs.dosattrib` / `smb3.dosattrib` call `cifs_attrib_set()`.
  - `cifs.creationtime` / `smb3.creationtime` call `cifs_creation_time_set()`.
  - Other user attrs call dialect `set_EA` unless mounted with `CIFS_MOUNT_NO_XATTR`.
- For security descriptor attrs:
  - Copies user-provided descriptor into kernel memory.
  - Converts handler flag to CIFS ACL flags: owner, group, DACL, SACL.
  - Calls dialect `set_acl()` if available.
  - Forces inode revalidation on success.

`cifs_attrib_set()` and `cifs_creation_time_set()` build `FILE_BASIC_INFO` buffers and call dialect `set_file_info()`, then update cached CIFS inode fields on success.

## Get Path
`cifs_xattr_get()`:
- Acquires tcon, XID, and full dentry path.
- For pseudo-xattrs:
  - `cifs_attrib_get()` revalidates dentry attributes and returns cached DOS attributes.
  - `cifs_creation_time_get()` revalidates and returns cached creation time.
- For user EAs:
  - Calls dialect `query_all_EAs()` unless `CIFS_MOUNT_NO_XATTR`.
- For NTSD/ACL xattrs:
  - Maps the handler flag to `OWNER_SECINFO`, `GROUP_SECINFO`, `DACL_SECINFO`, and/or `SACL_SECINFO`.
  - Calls dialect `get_acl()`.
  - Returns descriptor length for size probe or copies the descriptor into caller buffer if it fits.
- Converts `-EINVAL` to `-EOPNOTSUPP` before returning.

## List Path
`cifs_listxattr()`:
- Rejects forced shutdown with traced EIO.
- Rejects `CIFS_MOUNT_NO_XATTR`.
- Builds full path and calls dialect `query_all_EAs()` with a null EA name to enumerate attributes.
- Releases path, XID, and tcon resources on exit.

## Handler Registration
`cifs_xattr_handlers[]` registers:
- `user.*`
- `os2.*` treated like user xattrs.
- legacy `system.cifs_*` security names.
- newer `system.smb3_*` aliases.

The comments explicitly call out that the SMB3 names are aliases intended to avoid exposing the legacy “cifs” name to users for modern SMB2/3 mounts.

## State And Synchronization
The file does not own complex locks. It relies on:
- tcon references from `cifs_sb_tlink()`.
- XID accounting.
- path allocation/free helpers.
- inode revalidation and cached fields in `CIFS_I(inode)`.
- dialect operation callbacks for actual protocol operations.

## Security-Relevant Behavior
- Security descriptor xattrs can expose or modify owner/group/DACL/SACL depending on the requested name.
- SACL access depends on server-side permissions and dialect ACL implementation.
- The file copies user-provided security descriptors into kernel memory before passing them to protocol code.
- EA values are bounded by `CIFSMaxBufSize`.

## Risks And Review Focus
- In the ACL get path, `acllen` is a `u32`; assigning `-ERANGE` to it when the caller buffer is too small can produce a large positive return value when assigned to `rc`. This is a review-worthy bug pattern.
- Pseudo-xattr set paths trust exact `sizeof(__u32)` and `sizeof(__u64)` value sizes; userspace ABI expectations should remain stable.
- Security descriptor get/set semantics must stay aligned with `cifsacl.c` and dialect `get_acl`/`set_acl` implementations.
- `CIFS_MOUNT_NO_XATTR` suppresses server EAs but not pseudo-xattrs before the check in user get/set paths.

## Research Takeaways
`xattr.c` is the VFS adapter for SMB EAs and security descriptors. It mixes true server EAs, locally cached pseudo attributes, and ACL/NTSD protocol calls behind Linux xattr names.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/client/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/Makefile -->
# File Research: sources/os/linux/linux/fs/smb/common/Makefile

## Scope
Read completely: 6 lines. This Makefile builds shared SMB filesystem common code.

## Purpose
The file declares build output for routines shared by SMB client and server code.

## Contents
- SPDX: `GPL-2.0-only`.
- Comment: “Makefile for Linux filesystem routines that are shared by client and server.”
- Build rule: `obj-$(CONFIG_SMBFS) += cifs_md4.o`.

## Integration Points
When `CONFIG_SMBFS` is enabled, `fs/smb/common/cifs_md4.c` is built into the SMB common object set.

## Research Takeaways
This Makefile currently contributes only the CIFS-specific MD4 implementation to the common SMB build.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/cifs_md4.c -->
# File Research: sources/os/linux/linux/fs/smb/common/cifs_md4.c

## Scope
Read completely: 198 lines. This file implements an MD4 digest helper exported for CIFS/SMB code.

## Purpose
`cifs_md4.c` provides an in-tree MD4 implementation derived from historical CIFS and cryptoapi code. MD4 is needed for legacy NTLM-style password/hash operations in SMB authentication compatibility paths.

## Main Interfaces
- `int cifs_md4_init(struct md4_ctx *mctx)`
- `int cifs_md4_update(struct md4_ctx *mctx, const u8 *data, unsigned int len)`
- `int cifs_md4_final(struct md4_ctx *mctx, u8 *out)`

All three are exported with `EXPORT_SYMBOL_GPL`.

## Algorithm Structure
- Defines RFC1320 boolean functions `F`, `G`, and `H`.
- Defines rotate helper `lshift()`.
- Defines `ROUND1`, `ROUND2`, and `ROUND3` macros with MD4 constants.
- `md4_transform()` applies the three MD4 rounds to a 16-word block and accumulates state.
- `md4_transform_helper()` converts the current block from little-endian words to CPU order before transforming.

## State Handling
`struct md4_ctx` contains:
- four hash words.
- a 16-word block buffer.
- a byte counter.

`cifs_md4_init()` zeroes the context and sets the standard MD4 initial state:
- `0x67452301`
- `0xefcdab89`
- `0x98badcfe`
- `0x10325476`

`cifs_md4_update()`:
- Appends data into the partial block.
- Transforms complete 64-byte blocks.
- Leaves remaining bytes in `ctx->block`.
- Advances `byte_count`.

`cifs_md4_final()`:
- Adds `0x80` padding.
- Pads to the MD4 length field position.
- Writes bit length into block words 14 and 15.
- Performs the final transform.
- Converts hash words to little endian.
- Copies the 16-byte digest to `out`.
- Clears the context.

## Integration Points
The file includes `md4.h` and is built by `fs/smb/common/Makefile` under `CONFIG_SMBFS`. Consumers use it through `md4.h`.

## Security Notes
- MD4 is cryptographically broken and should only be used for legacy SMB/NTLM compatibility, not new security designs.
- The context is cleared in finalization, which is appropriate for password-derived hash material.

## Risks And Review Focus
- Length handling uses a 64-bit byte count but writes low/high bit length into 32-bit block words; this matches MD4 but depends on correct shifts.
- Endianness conversions are central to digest correctness.
- This implementation should not be generalized for non-legacy uses.

## Research Takeaways
`cifs_md4.c` is a small compatibility crypto primitive. Its main value is preserving legacy SMB authentication behavior while keeping the API local to SMB common code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/cifs_md4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/fscc.h -->
# File Research: sources/os/linux/linux/fs/smb/common/fscc.h

## Scope
Read completely: 566 lines. This header defines shared MS-FSCC wire structures and constants used by SMB client and server code.

## Purpose
`fscc.h` maps Microsoft File System Control Codes and file/filesystem information classes into packed Linux C structures. It provides common definitions for reparse points, copy/clone controls, integrity, allocated ranges, file metadata, directory entries, rename/link set-info buffers, filesystem info, DOS attributes, notify actions, and SMB3 POSIX filesystem information.

## Main Definition Areas

## Reparse Data
Defines packed structures for:
- generic reparse data buffers.
- GUID reparse buffers.
- mount point reparse buffers.
- symlink reparse buffers with `SYMLINK_FLAG_RELATIVE`.
- NFS reparse buffers with `NFS_SPECFILE_*` inode type constants.
- WSL/LX symlink reparse buffers.

These are used by SMB reparse-point handling for symlinks, junctions, special files, and WSL interoperability.

## FSCTL Data Structures
Defines buffers for:
- `duplicate_extents_to_file`
- `duplicate_extents_to_file_ex`
- integrity query/set responses and requests.
- allocated range queries.
- file-region queries.
- on-disk volume information.
- zero-data ranges for `FSCTL_SET_ZERO_DATA`.

These support clone/dedupe-like operations, sparse/range management, integrity streams, and volume metadata queries.

## File Information Structures
Defines:
- `struct smb2_file_all_info`
- `FILE_BASIC_INFO`
- `FILE_BOTH_DIRECTORY_INFO`
- `FILE_DIRECTORY_INFO`
- `struct smb2_file_eof_info`
- `FILE_FULL_DIRECTORY_INFO`
- `FILE_ID_FULL_DIR_INFO`
- `struct smb2_file_internal_info`
- `struct smb2_file_link_info`
- `struct smb2_file_network_open_info`
- `struct smb2_file_rename_info`

The link and rename structures use `__struct_group()` plus `static_assert()` so flexible filename data starts exactly after the packed header group.

## Filesystem Information
Defines filesystem info class numbers:
- volume, label, size, device, attribute, control, full size, object id, driver path, sector size.
- SMB3.1.1 POSIX info class `FS_POSIX_INFORMATION`.

Defines structures:
- `FILE_SYSTEM_ATTRIBUTE_INFO`
- `struct smb2_fs_control_info`
- `struct smb2_fs_full_size_info`
- `struct smb3_fs_ss_info`
- `FILE_SYSTEM_SIZE_INFO`
- `struct filesystem_vol_info`
- `FILE_SYSTEM_DEVICE_INFO`
- `FILE_SYSTEM_POSIX_INFO`

Also defines filesystem capability flags such as sparse files, hard links, persistent ACLs, reparse points, named streams, encryption, USN journal, block refcounting, POSIX unlink/rename support, and sector-size flags.

## File Attributes And Notify
Defines DOS/Windows file attribute bits and little-endian variants:
- readonly, hidden, system, directory, archive, normal, temporary, sparse, reparse, compressed, offline, not indexed, encrypted, integrity stream, no-scrub.
- aggregate `FILE_ATTRIBUTE_MASK`.

Defines SMB2 notify action values and `struct file_notify_information`.

## Integration Points
This header is included by SMB client/server protocol code that builds or parses:
- `QUERY_INFO` and `SET_INFO` file metadata.
- `QUERY_DIRECTORY` records.
- close/open returned network open info.
- filesystem statistics queries.
- change notify responses.
- reparse and FSCTL ioctl buffers.
- SMB3 POSIX statfs data.

## Notable Behaviors
- All wire structs are packed and use explicit endian-annotated types.
- Some legacy CIFS and SMB2 structures with similar names are intentionally not identical; comments call out differences.
- Several structures end in flexible arrays for variable path/name/security data.
- `FILE_SYSTEM_POSIX_INFO` follows the Samba SMB3 POSIX extension document rather than base MS-FSCC alone.

## Risks And Review Focus
- Wire layout drift is the primary risk; packed offsets must match protocol specifications.
- Flexible arrays require callers to validate server-provided lengths before access.
- Rename/link structures depend on `static_assert()` to catch accidental header layout changes.
- Attribute and filesystem capability flags are shared with user-visible behavior such as xattrs, statfs, fallocate, clone, symlink/reparse handling, and cache policy.

## Research Takeaways
`fscc.h` is the SMB common vocabulary for file and filesystem metadata. Most high-level SMB client operations eventually consume or produce one of these packed structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/fscc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/md4.h -->
# File Research: sources/os/linux/linux/fs/smb/common/md4.h

## Scope
Read completely: 27 lines. This header declares the CIFS MD4 context and API.

## Purpose
`md4.h` exposes constants, state, and functions for the SMB common MD4 implementation in `cifs_md4.c`.

## Contents
Constants:
- `MD4_DIGEST_SIZE` = 16
- `MD4_HMAC_BLOCK_SIZE` = 64
- `MD4_BLOCK_WORDS` = 16
- `MD4_HASH_WORDS` = 4

State:
- `struct md4_ctx` with four hash words, sixteen block words, and a 64-bit byte counter.

Functions:
- `cifs_md4_init()`
- `cifs_md4_update()`
- `cifs_md4_final()`

## Integration Points
Included by SMB common/client authentication code needing the CIFS MD4 implementation. The implementation exports the three functions as GPL symbols.

## Notable Details
The comment says “Common values for ARC4 Cipher Algorithm,” but the definitions are MD4-specific. This appears to be a stale or copied comment.

## Research Takeaways
`md4.h` is a minimal compatibility API for legacy MD4 hashing in SMB code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/md4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smb1pdu.h -->
# File Research: sources/os/linux/linux/fs/smb/common/smb1pdu.h

## Scope
Read completely: 56 lines. This header defines minimal shared SMB1 PDU structures.

## Purpose
`smb1pdu.h` provides the SMB1 protocol magic value and the common SMB1 header layout, plus the negotiate request wrapper.

## Main Definitions
- `SMB1_PROTO_NUMBER`: little-endian protocol id `0x424d53ff`.
- `struct smb_hdr`: packed SMB1 header matching MS-CIFS/MS-SMB.
- `SMB_NEGOTIATE_REQ`: negotiate request with an SMB header, byte count, and variable dialect array.

## SMB1 Header Fields
`struct smb_hdr` includes:
- protocol bytes.
- command.
- status union for DOS error or CIFS/NT error.
- flags and `Flags2`.
- PID high.
- signature/sequence union.
- TID, PID, UID, MID.
- word count.

## Integration Points
Used by common SMB code and compatibility paths that need SMB1 header parsing or negotiation structure definitions.

## Notable Behaviors
- The structure is packed to match wire layout.
- Some fields are endian-annotated, while opaque or historical fields remain plain-width integers.
- Only the negotiate request is defined here; broader SMB1 command definitions live elsewhere in the client tree.

## Research Takeaways
`smb1pdu.h` is a small shared definition header for legacy SMB1 framing. It exists so common SMB code can identify and parse the basic SMB1 wire header without depending on the full client SMB1 PDU header.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smb1pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smb2pdu.h -->
# File Research: sources/os/linux/linux/fs/smb/common/smb2pdu.h

## Scope
Read completely: 1,784 lines. This header defines shared SMB2/SMB3 protocol command constants, flags, packed wire PDUs, negotiate contexts, create contexts, FSCTL ioctl payloads, query/set info classes, lease/oplock structures, and access-right constants.

## Purpose
`smb2pdu.h` is the core common SMB2/3 wire-format vocabulary. It is shared by client and server code so both sides build and parse the same packed protocol structures.

## Command And Size Constants
Defines host-endian and little-endian command ids for:
- negotiate, session setup, logoff, tree connect/disconnect, create, close, flush, read, write, lock, ioctl, cancel, echo, query directory, change notify, query info, set info, oplock break, and server-to-client notification.

Also defines:
- `NUMBER_OF_SMB2_COMMANDS`
- session key and signature sizes.
- AES-GCM/CCM key sizes.
- SMB3 encryption/decryption and signing key sizes.
- SMB2 max buffer size.
- default I/O sizes.
- SMB2 header size and protocol numbers for normal, encrypted transform, and compression transform frames.

## Header And Transform Structures
Defines:
- `struct smb2_hdr`
- `struct smb3_hdr_req`
- `struct smb2_pdu`
- `struct smb2_err_rsp`
- `struct smb2_transform_hdr`
- `struct smb2_compression_hdr`
- `struct smb2_compression_payload_hdr`
- `struct smb2_compression_pattern_v1`

These structures model normal SMB2 frames, SMB3 request headers with channel sequence fields, encrypted transform frames, and compressed frames.

## Tree Connect And Remoted Identity
Defines tree connect contexts:
- generic `tree_connect_contexts`.
- remoted identity blob and SID/group/privilege arrays.
- `remoted_identity_tcon_context`.
- `smb2_tree_connect_req_extension`.

Also defines tree connect request/response structures, tree disconnect request/response structures, share types, share flags, and share capabilities such as DFS, continuously available, scaleout, cluster, asymmetric, redirect-to-owner, compression, and isolated transport.

## Negotiation
Defines:
- security mode flags.
- global capabilities including DFS, leasing, large MTU, multichannel, persistent handles, directory leasing, encryption, and notifications.
- dialect ids from SMB2.0 through SMB3.1.1.
- SMB3.1.1 salt/preauth constants.
- negotiate context ids for preauth integrity, encryption, compression, netname, transport, RDMA transform, signing, and POSIX extension availability.

Packed negotiate context structures include:
- `smb2_neg_context`
- `smb2_preauth_neg_context`
- `smb2_encryption_neg_context`
- `smb2_compression_capabilities_context`
- `smb2_netname_neg_context`
- `smb2_transport_capabilities_context`
- `smb2_rdma_transform_capabilities_context`
- `smb2_signing_capabilities`
- `smb2_posix_neg_context`
- `smb2_negotiate_req`
- `smb2_negotiate_rsp`

## Session, Logoff, Close, Read, Write, Flush, Lock, Echo
Defines request/response structures and flags for:
- `smb2_sess_setup_req` / `rsp`, including binding and encryption flags.
- logoff.
- close with post-query attributes and close response metadata.
- read requests/responses, unbuffered/compressed read flags, channel flags, and RDMA transform response flags.
- write requests/responses with write-through and unbuffered flags.
- flush.
- byte-range lock request/response and lock element flags.
- echo.

## Directory, Notify, Device Flags, Set Info
Defines:
- query-directory flags and request/response structures.
- device type and device characteristic constants.
- set-info request/response and `SMB2_SET_INFO_IOV_SIZE`.
- change-notify flags, completion filters, request/response structures.
- server-to-client notification structure and session-closed notification type.

## Create/Open And Create Contexts
Defines:
- oplock levels, including internal `SMB2_OPLOCK_LEVEL_NOCHANGE`.
- impersonation levels.
- little-endian desired access, share access, create disposition, and create options flags.
- create context names such as extended attributes, security descriptor, durable handle, maximal access, timewarp, on-disk id, lease, POSIX, app instance ids, SVHDX, and AAPL.
- create request and response structures.
- POSIX create context.
- durable handle v1/v2 request/reconnect/response contexts.
- maximal access request/response.
- lease v1/v2 contexts.
- disk id response.
- app instance id/version contexts.

## IOCTL And FSCTL Payloads
Defines:
- `smb2_ioctl_req` and `smb2_ioctl_rsp`.
- copychunk request/response payloads.
- resume key response.
- SMB socket address structures for IPv4 and IPv6.
- network interface info response and RSS/RDMA capability constants.
- integrity checksum choices and flags.
- validate negotiate request/response.

These definitions back SMB3 copy offload, multichannel interface discovery, integrity streams, and validate-negotiate behavior.

## Query Info, POSIX Info, Oplock/Lease Breaks
Defines:
- SMB2 info type constants for file, filesystem, security, quota.
- file information class numbers, including query-directory-compatible values and SMB3 POSIX info.
- security info flags such as owner, group, DACL, SACL, label, scope, backup, and protected/unprotected DACL/SACL.
- EA scan flags.
- `smb2_query_info_req` / `rsp`.
- `smb311_posix_qinfo`.
- oplock break, lease break, and lease ack structures.
- structure size constants for SMB2.0 and SMB2.1 oplock break acknowledgements.

## Access Rights
The final section defines non-endian access-right constants:
- file read/write/append/list/traverse/EA/attribute/delete rights.
- `DELETE`, `READ_CONTROL`, `WRITE_DAC`, `WRITE_OWNER`, `SYNCHRONIZE`.
- `SYSTEM_SECURITY`, `MAXIMUM_ALLOWED`, and generic read/write/execute/all.
- helper masks such as `FILE_READ_RIGHTS`, `FILE_WRITE_RIGHTS`, `FILE_EXEC_RIGHTS`, `SET_FILE_EXEC_RIGHTS`, and `SET_MINIMUM_RIGHTS`.

These are used by ACL, create/open, chmod-like behavior, and security descriptor logic.

## Integration Points
This header is central to:
- SMB2/3 client PDU builders/parsers in `fs/smb/client`.
- SMB server code that parses or emits SMB2/3 frames.
- common FSCC and ACL code through shared security/access constants.
- transport and stats code through command ids and response sizes.
- encryption, compression, multichannel, leasing, durable handles, copy offload, and POSIX extension paths.

## Notable Behaviors
- Names intentionally follow Microsoft protocol field casing rather than normal kernel style.
- All wire structures are packed.
- Many fields use explicit little-endian types; FIDs are documented as opaque endianness in several structures.
- Some contexts contain flexible arrays and protocol-required padding comments.
- The header mixes base SMB2, SMB3, SMB3.0.2, SMB3.1.1, POSIX extension, RDMA, compression, signing, encryption, and copychunk definitions.

## Risks And Review Focus
- Wire layout changes are high risk; structure sizes and offsets must match MS-SMB2.
- Flexible-array payloads require strict caller-side bounds validation.
- Dialect-specific fields must be zero or ignored correctly for older dialects.
- Security and access-right constants are used in ACL-sensitive code; mismatches affect authorization behavior.
- Some comments note expansion or padding concerns, such as validate-negotiate dialect count and compression context padding.

## Research Takeaways
`smb2pdu.h` is the shared SMB2/3 protocol contract for this tree. It is not executable logic, but it defines nearly every object that SMB client/server code sends, receives, signs, encrypts, validates, and exposes to higher filesystem logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/common/smb2pdu.h -->