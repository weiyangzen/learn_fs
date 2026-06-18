# Group Research: group_1079_linux_stable_sources_os_linux_linux_stable_fs_smb_client_trace_h_so_4424543b50d5

Scope: `Docs/research_subset_a.md`. All listed source files were read completely; no file was sampled.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/trace.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/trace.h

## Summary
Defines the Linux CIFS/SMB client tracepoint surface for ftrace/perf diagnostics. It declares symbolic trace enums for SMB EIO reasons, read/write credit transitions, and tree-connect reference transitions, then builds reusable `DECLARE_EVENT_CLASS` templates and concrete `TRACE_EVENT`/`DEFINE_EVENT` instances for the SMB client’s main runtime paths.

## Main Responsibilities
- Export symbolic trace enums for wire-parse errors, malformed response reasons, credit accounting transitions, and tcon reference lifecycle events.
- Trace read/write enter/done/error paths with request debug IDs, FIDs, TIDs, session IDs, offsets, lengths, and return codes.
- Trace copy-range, clone, zero-range, fallocate, query-dir, EOF, flush, close, lock, ioctl, shutdown, open, cached-open, cached-close, lease, reconnect, session, tree-connect, and query/set-info paths.
- Trace connection establishment and SMB Direct connection status with hostname, connection ID, destination socket address, and errors.
- Trace credit wait/add/adjust/timeout/overflow cases with current MID, server, credit pool, delta, and in-flight count.
- Trace Kerberos/SPNEGO auth metadata, tcon refs, read/write subrequest credit state, and compact `smb3_eio` symbolic failure records.

## Key Interfaces
- Enum sets: `smb_eio_traces`, `smb3_rw_credits_traces`, `smb3_tcon_ref_traces`.
- Exported enums: `enum smb_eio_trace`, `enum smb3_rw_credits_trace`, `enum smb3_tcon_ref_trace`.
- Important event families: `smb3_read_*`, `smb3_write_*`, `smb3_copychunk_*`, `smb3_clone_*`, `smb3_query_info_*`, `smb3_set_info_*`, `smb3_open_*`, `smb3_lease_*`, `smb3_connect_*`, `smb3_reconnect`, `smb3_*_credits`, `smb3_kerberos_auth`, `smb3_tcon_ref`, `smb3_rw_credits`, and `smb3_eio`.

## Integration Notes
This header is included by SMB client C files that emit `trace_smb3_*`, `trace_cifs_*`, and `trace_smb3_eio` calls. The final `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `<trace/define_trace.h>` inclusion make it the provider for tracepoint definitions when compiled in the trace-defining translation unit.

## Risks
The file is declarative but high leverage: trace field order and `TP_PROTO`/`TP_ARGS` signatures must stay synchronized with all call sites. Symbolic enum edits can affect user-space trace decoding. Some trace classes carry paths, usernames, hostnames, socket addresses, FIDs, and security/auth context, so diagnostic usefulness must be balanced against data exposure in trace logs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/transport.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/transport.c

## Summary
Implements core SMB client transport mechanics: MID lifecycle, socket/RDMA send paths, credit waiting and reservation, synchronous and asynchronous request dispatch, compound request handling, channel selection for multichannel sessions, cancellation, response waiting, and read-response receive/discard logic.

## Main Responsibilities
- Manage MID completion and release through `cifs_wake_up_task()`, `__release_mid()`, `delete_mid()`, `cifs_sync_mid_result()`, and compound callbacks.
- Send SMB request vectors over TCP or SMB Direct RDMA via `smb_send_kvec()`, `__smb_send_rqst()`, and `smb_send_rqst()`.
- Add RFC1002 length markers, cork/uncork TCP sockets, mask signals during sends, detect partial sends, and force reconnect when a partial frame may corrupt stream framing.
- Support compressed and encrypted/transform sends by invoking compression helpers or dialect `init_transform_rq`.
- Gate requests on SMB credits with `wait_for_free_credits()`, `wait_for_free_request()`, and `wait_for_compound_request()`.
- Dispatch asynchronous requests through `cifs_call_async()` and synchronous/compound requests through `compound_send_recv()` and `cifs_send_recv()`.
- Pick an eligible multichannel server with `cifs_pick_channel()`, preferring the least loaded non-reconnecting channel.
- Receive large read responses into netfs iterators with `cifs_readv_receive()`, including malformed-response detection and discard handling.
- Discard unread frame bytes after errors with `cifs_discard_remaining_data()`, `__cifs_readv_discard()`, and `cifs_readv_discard()`.

## Control Flow
Sends reserve credits, validate the reconnect instance, allocate/setup MID entries, place MIDs on `pending_mid_q`, serialize signing/send work under the server lock, send request vectors, and wait for response state transitions. Compound sends allocate one MID per request part, use callbacks on each part to collect credits, wake the caller from the last response, update SMB3.1.1 preauth hashes during negotiate/session setup, and transfer response buffers to callers when requested.

Read receive validates the header, handles session-expired and status-pending responses, maps server errors, checks data offset/length against the frame size, reads data into the request iterator or accounts for RDMA memory registration, discards trailing bytes, dequeues the MID, and transfers `server->smallbuf` ownership to the MID.

## State And Synchronization
Uses `server->req_lock` for credits and in-flight counters, `server->srv_lock` for TCP status, `server->mid_queue_lock` for pending MID queues, per-MID locks for cancellation state, `server` send lock for serialized signing/socket send, and `ses->chan_lock` for channel selection. Correctness depends on matching credit ownership to reconnect instances and ensuring MIDs are not freed while demultiplex or callback paths can still see them.

## Risks
High-risk areas are partial TCP sends, signal interruption after partial frames, reconnect-instance races after credit reservation, compound cancellation, response-buffer ownership transfer, and read-response length/offset validation. Credit starvation logic intentionally reserves compound capacity; mistakes can cause deadlocks, request storms, or underutilization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/unc.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/unc.c

## Summary
Provides small UNC parsing helpers for the SMB client.

## Main Interfaces
- `extract_hostname(const char *unc)`: validates a UNC-like string, skips leading backslashes, finds the next backslash delimiter, allocates and returns the hostname portion.
- `extract_sharename(const char *unc)`: skips the initial two characters, finds the share-name delimiter, and duplicates the remainder as the share name.

## Behavior
Both functions return allocated strings on success and `ERR_PTR()` on failure. `extract_hostname()` checks minimum length, rejects all-backslash strings, requires a hostname/share delimiter, and returns `-EINVAL` or `-ENOMEM`. `extract_sharename()` assumes a conventional leading `\\`, requires the next `\`, duplicates the share substring, and returns `-EINVAL` or `-ENOMEM`.

## Dependencies And Risks
The code depends on callers passing normalized UNC strings using backslash delimiters. `extract_sharename()` performs less validation than `extract_hostname()` and directly starts at `unc + 2`, so malformed short strings must be filtered by callers or earlier normalization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/unc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/winucase.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/winucase.c

## Summary
Contains a generated Windows-compatible UTF-16 uppercase mapping table and the CIFS helper that applies it. The tables were derived from Microsoft’s Windows 8 uppercase mapping data and post-processed for kernel use.

## Main Interfaces
- `cifs_toupper(wchar_t in)`: returns the Windows uppercase equivalent for a UTF-16 code unit when a mapping exists; otherwise returns the input unchanged.

## Structure
The file defines second-level 256-entry `wchar_t` tables for selected high-byte ranges, including Latin, Greek, Cyrillic, extended Latin, fullwidth ASCII, and other ranges needed by Windows casefold behavior. The `toplevel[256]` table maps the high byte of an input code unit to the appropriate second-level table or `NULL`.

## Behavior
`cifs_toupper()` extracts the upper byte, finds a second-level table, indexes by lower byte, and returns the mapped uppercase value only when the table entry is nonzero. Missing top-level tables and zero entries preserve the original character.

## Dependencies And Risks
This function supports CIFS/SMB filename comparison semantics where Windows casing differs from generic Unicode or Linux NLS behavior. The main risk is table drift relative to server behavior; changing generated mappings can affect case-insensitive lookup, dcache aliasing, and path matching.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/winucase.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/xattr.c

## Summary
Implements CIFS/SMB VFS extended attribute handlers. It exposes user and OS/2 EA passthrough, pseudo-xattrs for DOS attributes and creation time, and system xattrs for CIFS/SMB3 security descriptors.

## Main Responsibilities
- Set pseudo-xattrs `user.cifs.dosattrib`, `user.smb3.dosattrib`, `user.cifs.creationtime`, and `user.smb3.creationtime` by translating them to `FILE_BASIC_INFO` updates.
- Get pseudo-xattrs from cached/revalidated inode metadata.
- Pass ordinary `user.*` and `os2.*` EAs through protocol operations `set_EA` and `query_all_EAs`, unless `CIFS_MOUNT_NO_XATTR` is set.
- Get and set CIFS/SMB3 ACL/security descriptor xattrs through server `get_acl` and `set_acl` operations.
- Provide `cifs_listxattr()` by querying all EAs from the server.
- Register `cifs_xattr_handlers[]` for user, os2, legacy `system.cifs_*`, and newer `system.smb3_*` names.

## Key Interfaces
- Set path: `cifs_xattr_set()`, `cifs_attrib_set()`, `cifs_creation_time_set()`.
- Get path: `cifs_xattr_get()`, `cifs_attrib_get()`, `cifs_creation_time_get()`.
- List path: `cifs_listxattr()`.
- Handler table: `cifs_xattr_handlers`.

## Security Descriptor Handling
Supported system xattrs include DACL-only, owner+DACL, owner-only, SACL-only, and full owner/group/DACL/SACL forms. Handler flags are translated into CIFS ACL selector bits for set operations and SMB security information flags for get operations.

## Risks
This file bridges untrusted user buffers, path construction, server operations, and security metadata. Important checks include EA value size limits, exact pseudo-xattr sizes, `NO_XATTR` mount handling, forced-shutdown handling in listxattr, and revalidation before returning pseudo attributes. SACL/full descriptor access depends on lower-layer authorization and server behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/Makefile

## Summary
Build file for SMB routines shared by client and server code.

## Behavior
When `CONFIG_SMBFS` is enabled, the common SMB object list includes `cifs_md4.o`.

## Integration Notes
This Makefile is minimal but determines whether the local MD4 implementation in `cifs_md4.c` is built into the shared SMB common code. Changes affect both client/server consumers that depend on the common SMB configuration.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/cifs_md4.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/cifs_md4.c

## Summary
Implements MD4 hashing for CIFS/SMB common code. It is derived from older CIFS and Linux crypto API MD4 implementations and exports a small init/update/final interface.

## Main Interfaces
- `cifs_md4_init(struct md4_ctx *mctx)`: zeroes context and initializes MD4 IV words.
- `cifs_md4_update(struct md4_ctx *mctx, const u8 *data, unsigned int len)`: buffers input, transforms full 64-byte blocks, and tracks byte count.
- `cifs_md4_final(struct md4_ctx *mctx, u8 *out)`: appends MD4 padding and bit length, performs final transform, writes the little-endian digest, and clears context.

## Internal Logic
The file defines MD4 primitives `F`, `G`, `H`, rotate helper `lshift()`, round macros, `md4_transform()`, and `md4_transform_helper()` for little-endian block conversion. The transform performs the three MD4 rounds over 16 32-bit words and accumulates into the hash state.

## Integration Notes
The symbols are exported with `EXPORT_SYMBOL_GPL`, and `md4.h` defines context sizes and prototypes. This implementation is likely used for legacy NTLM/CIFS authentication compatibility rather than general-purpose cryptographic strength.

## Risks
MD4 is cryptographically broken and should remain limited to protocol compatibility. Correctness-sensitive areas are byte-count overflow assumptions, final padding length, little-endian conversion, and context clearing after finalization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/cifs_md4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/fscc.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/fscc.h

## Summary
Defines packed structures and constants from MS-FSCC that are shared by SMB client/server code. It is a protocol schema header for reparse data, FSCTL payloads, file information classes, filesystem information classes, attributes, notify records, and POSIX filesystem info.

## Main Content
- Reparse buffers: generic, GUID, mount point, symlink, NFS special file, and WSL symlink formats.
- Server-side clone/copy and allocation structures: `duplicate_extents_to_file`, `duplicate_extents_to_file_ex`, `file_allocated_range_buffer`, query-file-regions request/response, and zero-data request.
- Integrity and disk info structures: get/set integrity info, on-disk volume info, sector-size info, and checksum flags.
- File information records: all-info, basic-info, directory-info variants, EOF info, internal info, link info, rename info, and network-open info.
- Filesystem info classes and records: attribute, control, full-size, size, volume, device, sector, and POSIX information.
- Attribute and capability constants: filesystem capabilities, file attributes and little-endian variants, notify action codes, and POSIX fs info fields.

## Integration Notes
Consumers use these packed layouts to build or parse SMB2/3 query-info, set-info, FSCTL, reparse, directory enumeration, notify, and POSIX extension payloads. Static assertions on rename/link structures protect flexible-array offsets for set-info builders.

## Risks
This header must match wire layouts exactly. Structure packing, endian annotations, flexible arrays, and size comments are part of the ABI. Incorrect constants can break sparse file handling, reparse point parsing, clone/copy, filesystem capability detection, or POSIX extension interpretation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/fscc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/md4.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/md4.h

## Summary
Declares the CIFS MD4 context, digest/block size constants, and exported MD4 helper prototypes.

## Main Interfaces
- Constants: `MD4_DIGEST_SIZE`, `MD4_HMAC_BLOCK_SIZE`, `MD4_BLOCK_WORDS`, `MD4_HASH_WORDS`.
- `struct md4_ctx`: stores four hash words, sixteen block words, and byte count.
- Prototypes: `cifs_md4_init()`, `cifs_md4_update()`, `cifs_md4_final()`.

## Integration Notes
Used by `cifs_md4.c` and any SMB common/client code needing legacy MD4 hashing. The context layout is private to this implementation but exposed through the header for stack or embedded allocation.

## Risks
The API exposes a legacy cryptographic primitive. Callers must not use it for new security properties beyond required SMB/NTLM compatibility.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/md4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smb1pdu.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/smb1pdu.h

## Summary
Defines common SMB1 protocol header structures and the SMB1 negotiate request layout.

## Main Content
- `SMB1_PROTO_NUMBER`: little-endian protocol marker for SMB1.
- `struct smb_hdr`: packed SMB1 header with protocol bytes, command, DOS/CIFS status union, flags, signature/sequence union, TID/PID/UID/MID, and word count.
- `SMB_NEGOTIATE_REQ`: negotiate request containing `struct smb_hdr`, byte count, and variable dialect array.

## Integration Notes
This shared header supports SMB1/CIFS negotiation and common header parsing/building in client/server code. It intentionally mirrors MS-CIFS/MS-SMB wire layout and uses packed fields plus endian-specific types.

## Risks
The header is protocol ABI. Field type, packing, and endian mistakes would corrupt SMB1 parsing or signing. SMB1 is legacy and security-sensitive, so this header should remain narrowly scoped to compatibility paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smb1pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smb2pdu.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/common/smb2pdu.h

## Summary
Large shared SMB2/SMB3 protocol schema header. It defines command IDs, dialect IDs, header formats, negotiate contexts, transform/compression headers, tree/session/create/read/write/lock/ioctl/query-info PDUs, lease/oplock data, access masks, file information classes, security info flags, and helper constants.

## Main Content
- SMB2 command IDs in host and little-endian forms, protocol numbers, header size constants, flags, crypto/signing key sizes, and default I/O sizes.
- Core wire headers: `smb2_hdr`, `smb3_hdr_req`, generic PDU header, error response, encryption transform header, and compression transform/payload headers.
- Tree-connect definitions including remoted identity contexts, share types, share flags, share capabilities, tree connect/disconnect request and response layouts.
- Negotiate/session definitions: dialect IDs, global capabilities, SMB 3.1.1 negotiate contexts for preauth, encryption, compression, netname, transport, RDMA transform, signing, POSIX extensions, negotiate request/response, and session setup request/response.
- File operation PDUs: logoff, close, read, write, flush, lock, echo, query directory, set info, change notify, server-to-client notifications, create/open, and ioctl request/response layouts.
- Create contexts: extended attributes/security descriptor tags, durable handles, leases, maximal access, POSIX create, app instance IDs, Apple context tag, disk ID, and durable reconnect variants.
- IOCTL payloads: copychunk, resume key, network interface info, validate negotiate info, integrity checksum constants, and SMB socket address structures.
- Query info definitions: info types, file information classes, security descriptor selector flags, EA scan flags, query-info request/response, SMB3.1.1 POSIX query-info response, oplock/lease break and lease ack PDUs.
- Access control constants: desired access bits, generic rights, share access, create disposition/options, and host-endian file permission bit masks.

## Integration Notes
This header is consumed by SMB client and server code that constructs or parses SMB2/3 wire messages. It deliberately keeps mixed-case field names from protocol specifications to make layouts easier to compare with MS-SMB2. Structures are packed, many fields use explicit `__le*` annotations, and several flexible arrays model variable-length trailing buffers.

## Risks
This is protocol ABI surface. Incorrect packing, endian type, field order, size constant, or flexible-array offset can silently corrupt network PDUs. Security-sensitive constants such as signing/encryption algorithms, security information flags, access masks, and create options must remain aligned with the protocol and with server/client validation paths. Changes can affect negotiation compatibility, encryption/compression, durable handles, leases/oplocks, copy offload, directory enumeration, ACL retrieval, and POSIX extension behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/common/smb2pdu.h -->