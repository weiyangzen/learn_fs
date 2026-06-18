# subset-b-005761 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/trace.h -->
# sources/distributed-fs/ceph-client/fs/smb/client/trace.h

Read coverage: full file.

## Purpose
This header defines the CIFS/SMB client tracepoint surface for the Linux tracing subsystem. It is included by client code that emits `trace_smb3_*`, `trace_cifs_*`, and `trace_smb3_eio` events for request lifecycles, I/O errors, credit accounting, session/tree connection references, reconnects, authentication, leases, locks, opens, ioctls, shutdowns, and structured EIO reasons.

## Important APIs, types, and functions
The file exports trace enums through macro lists: `smb_eio_traces`, `smb3_rw_credits_traces`, and `smb3_tcon_ref_traces`. These become `enum smb_eio_trace`, `enum smb3_rw_credits_trace`, and `enum smb3_tcon_ref_trace`, are registered with `TRACE_DEFINE_ENUM`, and are printed through `__print_symbolic`.

The tracepoint API is mostly declarative: `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_EVENT`. Event classes cover read/write success and failure, other handle-based operations, copy range/reflink, EOF updates, fd operations, byte-range locks, query/set/notify info, compound path operations, SMB command enter/done/error, MID latency, function enter/exit, tree connect, open/create, leases, transport connect/reconnect, Kerberos auth, tcon refs, read/write credit flow, and detailed EIO causes.

## Control flow
At compile time, the tracing macros generate event descriptors and inline trace helpers. Runtime control flow is external: call sites collect identifiers such as xid, fid, tid, session id, offsets, lengths, credit counts, MID numbers, hostnames, and socket addresses, then call the generated trace helper. The tracepoint copies scalar fields and selected strings or sockaddr storage into the event payload inside `TP_fast_assign`, and `TP_printk` formats the tracefs output.

## State and persistence behavior
The header itself persists no SMB state. Its only durable ABI-like surface is trace event names, field names, enum values, and printed strings exposed under tracefs/perf/ftrace. Some tracepoints copy transient strings, user names, hostnames, and socket addresses into ring-buffer records, so the observable trace payload survives beyond the originating stack frame.

## Dependencies and integration points
The file depends on kernel tracepoint infrastructure plus socket address definitions. It integrates with transport, session setup, tree connect, read/write, lease, close, xattr/security, reparse, compression, and error-handling paths throughout the SMB client. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace` require a matching include arrangement when `trace/define_trace.h` instantiates the events.

## Risks and test signals
Tracepoint field names and print formats are user-visible diagnostics; renaming or changing enum order can break tracing scripts. The copy range print formats display the source fid using `target_fid` in the current format expression, which is a diagnostic accuracy risk. String tracepoints can expose host/user/path data to privileged tracing consumers. Build tests should compile with tracing enabled, and runtime tests should enable representative `cifs:*` events in tracefs while exercising mount, negotiate/session setup, open/read/write/close, lease break, reconnect, copychunk, query info, and xattr paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/transport.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/transport.c

Read coverage: full file.

## Purpose
`transport.c` is the SMB client transport core. It sends request vectors over TCP or SMB Direct, manages MIDs and response waits, enforces SMB credit flow control, drives synchronous and asynchronous request lifecycles, handles compound request completion, chooses multichannel transports, and receives read response payloads into netfs I/O iterators.

## Important APIs, types, and functions
MID lifecycle helpers include `cifs_wake_up_task`, `__release_mid`, and `delete_mid`. Socket send helpers are `smb_send_kvec`, `smb_rqst_len`, `__smb_send_rqst`, and the wrapper `smb_send_rqst`, which adds compression or encryption transform headers. Credit management is implemented by `wait_for_free_credits`, `wait_for_free_request`, `wait_for_compound_request`, and `cifs_wait_mtu_credits`. Request APIs include `cifs_call_async`, `compound_send_recv`, and `cifs_send_recv`. Receive helpers include `cifs_sync_mid_result`, `wait_for_response`, `cifs_discard_remaining_data`, and `cifs_readv_receive`. `cifs_pick_channel` selects a session channel with the lowest observed in-flight load.

## Control flow
Sends start by acquiring credits, locking the server, setting up MIDs through dialect-specific `server->ops`, queuing them on `pending_mid_q`, saving send timestamps, and calling `smb_send_rqst`. The low-level TCP path writes an RFC1002 length marker, then all request kvecs and optional iter data, while signals are masked to avoid partial-SMB interruption. Partial sends trigger reconnect because subsequent bytes could be misparsed as the remainder of the previous PDU. The SMB Direct path delegates to `smbd_send`; compression delegates to `smb_compress`; encrypted requests build a transform request through `init_transform_rq`.

Synchronous compound calls set callbacks on every MID, send the chain in one socket-serialized sequence, wait for responses, cancel unfinished waits on interruption, validate each response with `check_receive`, and hand response buffers back to callers. Async calls set a callback/receive/handle tuple and return after a successful send. Read receive flow parses the read response header, handles session expiry and pending status, validates data offset and length, copies socket data into the target iterator or accounts RDMA memory registration data, discards trailing frame bytes, then dequeues the MID.

## State and persistence behavior
The file mutates server credit fields, `in_flight`, `max_in_flight`, reconnect instance, sequence numbers, pending MID queues, response buffers, `server->total_read`, and read subrequest byte counters. MID state transitions include submitted, response received, response ready, retry, malformed, shutdown, rc, and free. It updates statistics under `CONFIG_CIFS_STATS2`, including fastest/slowest command latency and slow response counters. No on-disk state is persisted, but network-visible sequencing and credit consumption are persistent protocol state.

## Dependencies and integration points
This code is tightly integrated with `cifsglob.h`, `cifsproto.h`, dialect-specific `server->ops`, SMB2 preauth hashing, SMB Direct, compression, transform/encryption, socket APIs, kernel wait queues, spinlocks, task work, and netfs read subrequests. Tracepoints from `trace.h` report slow responses, credit waits, insufficient credits, partial send reconnects, and malformed read frames.

## Risks and test signals
High-risk areas are partial send handling, credit starvation/deadlock, reconnect-instance races after credits are acquired, compound cancellation, buffer ownership when `resp_iov` takes `mid->resp_buf`, and malformed read response length/offset validation. Multichannel selection intentionally reads `in_flight` without `req_lock`, so tests should tolerate non-perfect load balancing. Test signals include xfstests over SMB2/SMB3 with signing/encryption/compression, forced reconnect during sends, signal interruption of synchronous requests, compound create/query/close flows, RDMA read coverage, credit exhaustion, and tracefs credit/partial-send events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/transport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/unc.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/unc.c

Read coverage: full file.

## Purpose
`unc.c` provides small helpers for parsing SMB UNC paths into hostname and sharename pieces. These helpers normalize the parts needed by mount/session/tree-connect setup code after UNC delimiters have already been reduced to backslashes.

## Important APIs, types, and functions
`extract_hostname(const char *unc)` validates that the UNC string is long enough, skips leading backslashes, finds the delimiter before the share name, allocates a new NUL-terminated host substring with `kmalloc`, and returns either the allocated string or an `ERR_PTR`.

`extract_sharename(const char *unc)` assumes the UNC starts with two leading characters, finds the next backslash, duplicates the remainder after that delimiter with `kstrdup`, and returns the allocated sharename path or an `ERR_PTR`.

## Control flow
The hostname path rejects too-short strings, all-backslash strings, and strings without a host/share delimiter. It copies only bytes before the delimiter. The sharename path skips the first two characters, locates the delimiter after the host, advances one byte, and duplicates everything after it. Both functions use kernel allocation with `GFP_KERNEL`.

## State and persistence behavior
No global state is changed. The only state produced is caller-owned heap memory that must be freed by the caller. Errors are encoded as `ERR_PTR(-EINVAL)` or `ERR_PTR(-ENOMEM)`.

## Dependencies and integration points
The file includes kernel fs, slab, inet, and ctype headers plus CIFS globals/prototypes. It integrates with mount and connection setup paths that need a server name for socket/session lookup and a share component for tree connect.

## Risks and test signals
`extract_sharename` assumes at least two leading characters and does not repeat the length/all-backslash validation used by `extract_hostname`; callers must pass canonical UNC input. Neither helper handles forward slashes or alternate delimiters. Test cases should cover `\\server\\share`, paths with subdirectories after the share, missing share delimiters, empty host, too-short strings, allocation failure injection, and caller freeing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/unc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/winucase.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/winucase.c

Read coverage: full file.

## Purpose
`winucase.c` implements Windows-compatible UTF-16 uppercase mapping for CIFS/SMB name comparison and case-insensitive hashing. The static data was generated from Microsoft Windows 8 uppercase mapping data and converted into C tables.

## Important APIs, types, and functions
The exported function is `wchar_t cifs_toupper(wchar_t in)`. It indexes a two-level table: the high byte selects an optional 256-entry page table from `toplevel`, and the low byte indexes a mapped uppercase character in that page. A zero table entry means no mapping, so the input character is returned unchanged.

The important data structures are the page tables `t2_00`, `t2_01`, `t2_02`, `t2_03`, `t2_04`, `t2_05`, `t2_1d`, `t2_1e`, `t2_1f`, `t2_21`, `t2_24`, `t2_2c`, `t2_2d`, `t2_a6`, `t2_a7`, and `t2_ff`, plus `toplevel[256]`.

## Control flow
`cifs_toupper` extracts `(in & 0xff00) >> 8`, looks up a second-level table, returns the input if no page table exists, then looks up the low byte. If the mapped value is nonzero it returns that uppercase value; otherwise it returns the original input.

## State and persistence behavior
All mapping state is immutable static const data. The function has no allocation, locking, reference counting, or external side effects. Its behavioral persistence is compatibility with Windows casefolding expectations for directory lookup, dcache names, and protocol comparisons.

## Dependencies and integration points
The file depends on `linux/nls.h` for `wchar_t`. It is consumed by CIFS Unicode conversion/comparison code and must match the server-side case-insensitive behavior closely enough for SMB shares that preserve case but search case-insensitively.

## Risks and test signals
The table is intentionally versioned to Windows 8 mappings, so newer Unicode casing changes may not be represented. The design supports BMP `wchar_t` values through two-byte indexing; behavior for any wider code unit is effectively based on low 16 bits. Regeneration risk is high because a misplaced table entry causes subtle lookup mismatches. Test signals include case-insensitive lookup tests for ASCII, Latin-1, Greek, Cyrillic, fullwidth Latin, and unmapped characters, plus comparing results with Windows/SMB server expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/winucase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/xattr.c -->
# sources/distributed-fs/ceph-client/fs/smb/client/xattr.c

Read coverage: full file.

## Purpose
`xattr.c` connects Linux VFS extended attribute operations to SMB extended attributes, DOS attribute pseudo-xattrs, creation-time pseudo-xattrs, and CIFS/SMB3 security descriptor xattrs. It exposes both legacy `system.cifs_*` names and newer `system.smb3_*` aliases.

## Important APIs, types, and functions
The VFS-facing API is `const struct xattr_handler * const cifs_xattr_handlers[]`, which contains user, OS/2, ACL, NTSD, SACL, owner, and full descriptor handlers. Core handlers are `cifs_xattr_get`, `cifs_xattr_set`, and `cifs_listxattr`. Pseudo-xattr helpers are `cifs_attrib_get`, `cifs_attrib_set`, `cifs_creation_time_get`, and `cifs_creation_time_set`.

Handler flags distinguish user EAs from `XATTR_CIFS_ACL`, `XATTR_CIFS_NTSD_SACL`, `XATTR_CIFS_NTSD_OWNER`, `XATTR_CIFS_NTSD`, and `XATTR_CIFS_NTSD_FULL`. Security descriptor requests map to SMB security-info bits such as `OWNER_SECINFO`, `GROUP_SECINFO`, `DACL_SECINFO`, and `SACL_SECINFO`, or CIFS ACL set flags.

## Control flow
Set operations acquire a tcon link, allocate a path buffer, build a full path from the dentry, reject oversized EA values, then dispatch by handler flag. User xattrs named `cifs.dosattrib` or `smb3.dosattrib` call `set_file_info` with `FILE_BASIC_INFO.Attributes`; creation-time names call `set_file_info` with `CreationTime`; other user EAs call dialect `set_EA` unless mounted with `NO_XATTR`. Security descriptor writes copy the user-supplied blob into kernel memory and call `set_acl` with the selected descriptor parts.

Get operations follow the same tcon/path setup. DOS attribute and creation-time reads revalidate inode attributes and copy cached `CIFS_I(inode)` fields. User EAs call `query_all_EAs`. Security descriptor reads call `get_acl` with the requested info bits and copy the returned descriptor if the caller buffer is large enough. `cifs_listxattr` lists server EAs unless xattrs are disabled or the share is forced down.

## State and persistence behavior
Successful DOS attribute and creation-time writes update cached inode fields and invalidate `CIFS_I(inode)->time` to force revalidation. User EA and ACL writes persist remotely through SMB server operations. Local state includes XID allocation/freeing, tcon link references, temporary path pages, and allocated ACL buffers.

## Dependencies and integration points
The file depends on VFS xattr handlers, CIFS mount flags, dentry path construction, server operation vectors (`set_file_info`, `set_EA`, `query_all_EAs`, `get_acl`, `set_acl`), security descriptor definitions, and CIFS inode private state.

## Risks and test signals
The security descriptor get path stores `-ERANGE` in an unsigned `u32 acllen` before assigning to `rc`, which deserves attention for signedness behavior. SACL access may require privileges on the server. Pseudo-xattrs bypass `NO_XATTR`, while ordinary user EAs honor it. Test signals should cover get/set/list with `user.*`, `os2.*`, DOS attributes, creation time, legacy and SMB3 ACL aliases, SACL/owner/full descriptor variants, small caller buffers, disabled xattrs, forced shutdown, and servers without EA/ACL operation support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/Makefile -->
# sources/distributed-fs/ceph-client/fs/smb/common/Makefile

Read coverage: full file.

## Purpose
This Makefile builds SMB common code shared by client and server components. In this subset it conditionally adds the CIFS MD4 implementation object.

## Important APIs, types, and functions
The only build rule is `obj-$(CONFIG_SMBFS) += cifs_md4.o`. It ties `cifs_md4.c` into the kernel build when SMB filesystem support is enabled.

## Control flow
Kbuild expands `obj-$(CONFIG_SMBFS)` based on the configuration value. When enabled as built-in or module, `cifs_md4.o` is compiled and linked into the corresponding SMB filesystem object set.

## State and persistence behavior
No runtime state exists. The persistent behavior is configuration-driven build inclusion.

## Dependencies and integration points
The Makefile integrates with Linux Kbuild and the `CONFIG_SMBFS` option. Its output object provides exported MD4 symbols used by SMB authentication code that needs NT hash compatible MD4 behavior.

## Risks and test signals
The main risk is configuration drift: if client or server code uses `cifs_md4_*` while `CONFIG_SMBFS` does not include this object, link failures result. Build tests should compile SMBFS as built-in and module, and ensure MD4 users resolve to `cifs_md4_init`, `cifs_md4_update`, and `cifs_md4_final`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/cifs_md4.c -->
# sources/distributed-fs/ceph-client/fs/smb/common/cifs_md4.c

Read coverage: full file.

## Purpose
`cifs_md4.c` implements the MD4 message digest algorithm for CIFS/SMB compatibility, notably NTLM/NT hash style authentication flows that historically require MD4 over UTF-16 password material.

## Important APIs, types, and functions
The exported API is `cifs_md4_init(struct md4_ctx *mctx)`, `cifs_md4_update(struct md4_ctx *mctx, const u8 *data, unsigned int len)`, and `cifs_md4_final(struct md4_ctx *mctx, u8 *out)`. Internal helpers include `lshift`, `F`, `G`, `H`, `ROUND1`, `ROUND2`, `ROUND3`, `md4_transform`, and `md4_transform_helper`.

## Control flow
Initialization zeros the context and seeds the four MD4 state words. Updates append input into a 64-byte block buffer, transform full blocks after converting little-endian words to CPU order, and keep trailing bytes buffered. Finalization appends the `0x80` bit, zero padding, and 64-bit bit count split into words 14 and 15, transforms the final block, converts the hash to little endian, copies 16 digest bytes to the output, and clears the context.

## State and persistence behavior
The mutable state is `struct md4_ctx`: four hash words, a sixteen-word block buffer, and `byte_count`. No global runtime state is changed. The final digest is persisted only through the caller-provided output buffer; the context is scrubbed after finalization.

## Dependencies and integration points
The file depends on kernel module infrastructure, endian helpers, string functions, and `md4.h`. It exports GPL symbols for use by SMB authentication code. Its implementation is intentionally self-contained rather than using a generic crypto API allocation path.

## Risks and test signals
MD4 is cryptographically broken and should only be used for protocol compatibility, never new security design. Padding and byte-count overflow behavior should be tested with RFC1320 vectors, empty input, inputs around 55/56/63/64/65 bytes, and multi-update inputs matching single-update digests. Endianness tests matter on big-endian architectures because block words are converted before transforms and digest words before output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/cifs_md4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/fscc.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/fscc.h

Read coverage: full file.

## Purpose
`fscc.h` defines common MS-FSCC wire structures and constants used by SMB client and server code for file system control payloads, reparse points, file information classes, filesystem information classes, directory entries, file attributes, notify records, and POSIX filesystem extension data.

## Important APIs, types, and functions
Key structure groups include reparse buffers (`reparse_data_buffer`, GUID, mount point, symlink, NFS, WSL symlink), clone/zero/integrity/ioctl payloads (`duplicate_extents_to_file`, `duplicate_extents_to_file_ex`, integrity request/response structs, `file_zero_data_information`), file info records (`smb2_file_all_info`, `FILE_BASIC_INFO`, directory info structs, eof/internal/link/network-open/rename info), filesystem info records (`FILE_SYSTEM_ATTRIBUTE_INFO`, `smb2_fs_control_info`, `smb2_fs_full_size_info`, `smb3_fs_ss_info`, `FILE_SYSTEM_SIZE_INFO`, `filesystem_vol_info`, `FILE_SYSTEM_DEVICE_INFO`, `FILE_SYSTEM_POSIX_INFO`), and notify payload `file_notify_information`.

Constants define FS information classes, file system capability bits, file attribute bits plus little-endian forms, notify action values, sector-size flags, NFS special file tags, duplicate-extents flags, and POSIX extension identifiers.

## Control flow
There is no executable control flow. The header defines packed layouts used by request construction and response parsing. Flexible arrays and static assertions ensure variable-length file names begin immediately after packed header groups for rename/link structures.

## State and persistence behavior
No runtime state is stored. The file describes persistent network protocol layouts; field order, packing, endian annotations, and constants must remain stable to interoperate with SMB peers.

## Dependencies and integration points
The header depends on Linux fixed-width and endian types and is included by SMB2 create/query/set/ioctl, reparse point, copy offload, directory enumeration, statfs, attribute, notify, and POSIX extension code. `xattr.c` indirectly relies on security-info constants shared with SMB2 query/set info paths.

## Risks and test signals
Layout drift is the main risk. Missing `__packed`, wrong endian type, or moving a field outside a `__struct_group` would corrupt wire compatibility. Tests should use compile-time offset/size checks where possible, packet decode tests for directory/query info responses, symlink/reparse round trips, clone/zero/integrity ioctl coverage, statfs/FS attribute queries, notify response parsing, and POSIX extension negotiation/query tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/fscc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/md4.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/md4.h

Read coverage: full file.

## Purpose
`md4.h` declares the CIFS MD4 context and digest API used by the common SMB MD4 implementation.

## Important APIs, types, and functions
Constants are `MD4_DIGEST_SIZE`, `MD4_HMAC_BLOCK_SIZE`, `MD4_BLOCK_WORDS`, and `MD4_HASH_WORDS`. `struct md4_ctx` stores the four-word hash state, sixteen-word block buffer, and total byte count. Function prototypes are `cifs_md4_init`, `cifs_md4_update`, and `cifs_md4_final`.

## Control flow
The header has no runtime control flow. It supplies the compile-time contract consumed by `cifs_md4.c` and callers.

## State and persistence behavior
`struct md4_ctx` is caller-owned mutable state. The header fixes its shape, so all update/final calls must use the same context instance for a digest stream. No global persistence exists.

## Dependencies and integration points
The header depends on `linux/types.h` for `u32`, `u64`, and `u8`. It integrates with the SMB common Makefile and any authentication code needing the exported MD4 helpers.

## Risks and test signals
Changing constants or context layout would break the implementation and any stack/static allocations. Test signals are compile coverage for all users, sparse/type checks, and MD4 known-answer tests through the public three-call API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/md4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smb1pdu.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/smb1pdu.h

Read coverage: full file.

## Purpose
`smb1pdu.h` defines minimal SMB1 protocol data units shared by common code, primarily the SMB1 header and negotiate request layout.

## Important APIs, types, and functions
`SMB1_PROTO_NUMBER` is the little-endian protocol marker for `0xff 'S' 'M' 'B'`. `struct smb_hdr` models the SMB1 header, including command, DOS/CIFS status union, flags, pid/tid/uid/mid fields, signature/sequence union, and word count. `SMB_NEGOTIATE_REQ` is a packed negotiate request with `struct smb_hdr`, `ByteCount`, and flexible `DialectsArray`.

## Control flow
There is no executable logic. These packed definitions are consumed by SMB1 negotiate and parsing code.

## State and persistence behavior
No state is stored in the header. The definitions encode wire-visible persistent protocol shape and field sizes.

## Dependencies and integration points
The file expects kernel endian conversion helpers to be available to users of `SMB1_PROTO_NUMBER`. It integrates with SMB1 negotiation and legacy CIFS header parsing paths.

## Risks and test signals
SMB1 is legacy and security-sensitive. Risks are wrong packing, endian misuse on `Tid` and `Uid` fields that are declared as `__u16`, and accidental changes to header size. Test signals include compile-time size checks, SMB1 negotiate packet construction tests, and parsing captures from known SMB1 servers when SMB1 support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smb1pdu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smb2pdu.h -->
# sources/distributed-fs/ceph-client/fs/smb/common/smb2pdu.h

Read coverage: full file.

## Purpose
`smb2pdu.h` is the common SMB2/SMB3 wire protocol definition header. It provides command codes, header layouts, negotiate/session/tree/create/read/write/lock/ioctl/query/set/notify/oplock/lease structures, dialect capabilities, crypto/compression constants, access masks, create options, security info bits, and POSIX extension layouts.

## Important APIs, types, and functions
Major constants include SMB2 command IDs in host and little-endian forms, cryptographic key/signature sizes, RFC header protocol numbers, SMB2 flags, dialect IDs, negotiate contexts, encryption/signing/compression algorithms, share flags/capabilities, file access/share/create options, create context names, lease/oplock constants, ioctl/copychunk structures, network interface response structures, query info classes, and security info masks.

Important structures include `smb2_hdr`, `smb3_hdr_req`, `smb2_pdu`, `smb2_err_rsp`, transform and compression headers, tree connect contexts and remoted identity data, negotiate request/response and negotiate context records, session setup/logoff/tree connect/close/read/write/flush/lock/echo/query directory/set info/change notify/create/ioctl/query info/oplock and lease break/ack PDUs. The header uses flexible arrays for variable payloads and static assertions for packed create-context offsets.

## Control flow
There is no runtime control flow. Client and server code use these packed structs to lay out outgoing requests and interpret incoming responses. The constants guide branch decisions in implementation files, such as negotiating dialects, computing signing/encryption transforms, validating read/write response sizes, building create contexts, and selecting query info classes.

## State and persistence behavior
The file has no local mutable state. It defines network-persistent state formats: session ids, tree ids, message ids, file ids, credit requests, lease keys, durable handle ids, negotiate capabilities, and security descriptors as represented on the wire. Any field layout or endian change is externally visible to SMB peers.

## Dependencies and integration points
The header depends on kernel type and build bug helpers. It is foundational for SMB client transport, session setup, tree connect, file create/open, I/O, locking, copy offload, compression/encryption, multichannel, RDMA, query/set info, notify, oplock/lease handling, and POSIX extensions. `transport.c` consumes read response sizing and command constants through dialect `server->vals` and ops; `xattr.c` uses security info flags defined here or adjacent common headers.

## Risks and test signals
Risks are dominated by wire compatibility: packing mistakes, wrong endian annotations, flexible-array length bugs, stale dialect capability constants, and unsafe assumptions about variable context padding. Security-sensitive areas include transform headers, signing/encryption algorithm negotiation, remoted identity contexts, security info masks, durable handle reconnects, and lease breaks. Test signals include build-time offset assertions, packet capture comparison against MS-SMB2 layouts, negotiate/session setup tests across SMB2.0 through SMB3.1.1, encrypted/compressed read/write, durable handles, leases/oplocks, copychunk/ioctl, query directory variants, POSIX create/query contexts, and malformed response fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/common/smb2pdu.h -->
