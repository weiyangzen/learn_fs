# Research: subset-b-009815

This grouped report covers Samba source3 library and libads files assigned to `subset-b-009815`. Each source file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sock.c -->
# sources/user-network-fs/samba/source3/lib/util_sock.c

## Purpose
`util_sock.c` is the source3 socket utility layer for blocking and async socket setup, SMB packet-length reads, peer-name resolution, Unix-domain pipe socket creation, local-name detection, and small poll wrappers. It bridges POSIX sockets, Samba `tevent`, `tsocket`, interface discovery, memcache, and SMB packet conventions.

## Important APIs and Functions
Key exported entry points are `is_a_socket`, `read_fd_with_timeout`, `read_data_ntstatus`, `read_smb_length_return_keepalive`, `receive_smb_raw`, `open_socket_in_protocol`, `open_socket_in`, `open_socket_out_send`, `open_socket_out_recv`, `open_socket_out`, `get_peer_addr`, `get_remote_hostname`, `create_pipe_sock`, `get_mydnsfullname`, `is_myname_or_ipaddr`, `poll_one_fd`, and `poll_intr_one_fd`. `struct open_socket_out_state` owns the async connect fd, address, timeout, and cleanup callback. `struct name_addr_pair` is a singleton memcache value pairing a `sockaddr_storage` with a resolved remote name.

## Control Flow and Behavior
Read helpers either loop on `sys_read` until a minimum byte count is met or use `poll_intr_one_fd` with a millisecond timeout before each read. SMB receive first reads the 4-byte NetBIOS Session Service length, preserves keepalive behavior, validates the payload length against the caller buffer, optionally caps reads at `maxlen`, and writes a trailing zero word to reduce unterminated string hazards in older callers. Incoming socket setup normalizes address length, sets port, opens the requested socket type/protocol, applies `SO_REUSEADDR`, optionally `SO_REUSEPORT`, forces IPv6-only sockets where available, and binds. Outgoing connects are async: `open_socket_out_send` creates a TCP socket, sets an end time, calls `async_connect_send`, and `open_socket_out_connected` maps connect errors to NTSTATUS; the sync wrapper drives that request on a temporary event context.

## State and Persistence
This file has no durable storage, but it uses process singleton memcache for `get_peer_name` and `get_mydnsfullname` results. `create_pipe_sock` creates filesystem state by ensuring a protected socket directory, unlinking any previous socket path, and binding a Unix-domain socket. `open_socket_out_cleanup` owns fd lifetime, closing the fd on failed or canceled requests and transferring ownership only after successful recv.

## Dependencies and Integration Points
It depends on Samba socket helpers (`samba_sockaddr_set_port`, `print_sockaddr`, `sockaddr_equal`), `tevent`, `async_sock`, `tsocket`, `memcache`, loadparm (`lp_hostname_lookups`, `lp_netbios_name`), interface discovery (`get_interfaces`, `ismyaddr`), DNS helpers (`interpret_string_addr_internal`, `sys_getnameinfo`), and SMB length macros. It is used by SMB transport, daemon IPC pipe setup, remote client logging, name matching, and AD/Kerberos or LDAP connection code needing socket primitives.

## Risks and Edge Cases
Timeout reads on disk files can spin because poll/select always reports readiness; the comment explicitly warns about `mincnt` larger than file size. `receive_smb_raw` validates `len > buflen` but then truncates to `maxlen`, so callers must understand that `p_len` can be shorter than the NBSS payload. `matchname` rejects DNS reverse/forward mismatches to avoid spoofing but can produce `UNKNOWN` for misconfigured DNS. Unix socket path length uses `strlcpy` and rejects truncation. `get_mydnsfullname` caches canonical names and can become stale if DNS or hostname changes. `is_myname_or_ipaddr` performs DNS lookups for CNAME-like names and can block on resolver behavior.

## Test Signals
Useful tests include read timeout and EOF cases, keepalive and oversized SMB length handling, IPv4/IPv6 bind with `SO_REUSE*`, async connect success/failure/timeouts, Unix socket path length rejection, reverse DNS spoof checks, hostname lookup disabled mode, and `is_myname_or_ipaddr` matches for netbios name, aliases, localhost, loopback, configured interfaces, and DNS-resolved local addresses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_specialsids.c -->
# sources/user-network-fs/samba/source3/lib/util_specialsids.c

## Purpose
This file implements helpers for the Asserted Identity special SID namespace. It lets higher-level SID/name mapping code detect the asserted-identity domain SID itself or any SID whose domain portion is Asserted Identity.

## Important APIs and Functions
Exports are `sid_check_is_asserted_identity`, `sid_check_is_in_asserted_identity`, and `asserted_identity_domain_name`. The first compares directly with `global_sid_Asserted_Identity`; the second copies the input SID, strips the RID with `sid_split_rid`, and compares the remaining domain SID; the third returns the display domain string `"Asserted Identity"`.

## Control Flow and State
The implementation is stateless and deterministic. It performs no allocation except stack storage for the copied domain SID, and it does not persist data.

## Dependencies and Integration Points
It depends on `dom_sid_equal`, `sid_copy`, `sid_split_rid`, and the global SID constants from `../libcli/security/security.h`. It integrates with source3 SID mapping and name lookup paths that need to recognize Windows special identities.

## Risks and Test Signals
The main edge case is malformed or RID-less SIDs: `sid_split_rid` return value is ignored, so tests should cover exact domain SID, domain plus RID, unrelated SIDs, and empty or minimal SID shapes. A null `sid` is not guarded locally and must be prevented by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_specialsids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_specialsids.h -->
# sources/user-network-fs/samba/source3/lib/util_specialsids.h

## Purpose
This header declares the Asserted Identity SID helper interface used by source3 SID/name mapping code.

## Important APIs and Types
It forward-declares `struct dom_sid` and declares `sid_check_is_asserted_identity`, `sid_check_is_in_asserted_identity`, and `asserted_identity_domain_name`.

## Dependencies and Integration Points
The header includes `replace.h` for base portability types and leaves the full SID definition to callers. It is paired directly with `util_specialsids.c`.

## Risks and Test Signals
Because it only declares functions, compatibility risk is ABI/API drift if signatures change. Compile tests should verify inclusion from modules that only have a forward declaration available and from modules that include the full security headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_specialsids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_str.c -->
# sources/user-network-fs/samba/source3/lib/util_str.c

## Purpose
`util_str.c` provides source3 string helpers for case-insensitive comparison, bounded buffer traversal, multibyte-aware character counting and case conversion, list membership, name validation, shell escaping, size parsing, and efficient path assembly.

## Important APIs and Functions
Exports include `strnequal`, `skip_string`, `str_charnum`, `trim_char`, `in_list`, `string_truncate`, `strlower_m`, `strupper_m`, `fstr_sprintf`, `conv_str_size`, `talloc_asprintf_strupper_m`, `talloc_asprintf_strlower_m`, `validate_net_name`, `escape_shell_string`, and `full_path_tos`. Internal helpers `unix_strlower` and `unix_strupper` convert through UTF-16LE for multibyte-aware casing. `toupper_ascii_fast_table` provides a fast ASCII upper-case path.

## Control Flow and Behavior
Most functions optimize for common ASCII cases and fall back to Samba charset conversion when high-bit bytes are encountered. `trim_char` handles front and back trimming in place and falls back to `trim_string` when a potential multibyte boundary is encountered near the trim point. `in_list` tokenizes a configured list with `next_token_talloc`. `escape_shell_string` walks codepoints, preserving multibyte characters and tracking unquoted, single-quoted, double-quoted, and backslash-escaped states to add shell escapes only where needed. `full_path_tos` writes into a caller stack buffer when large enough and allocates from `talloc_tos()` only when necessary.

## State and Persistence
The file has no durable state. It uses stackframes and talloc ownership for temporary conversions and returned strings. `escape_shell_string` returns `SMB_MALLOC` memory requiring `SAFE_FREE` by callers, while the `talloc_asprintf_*` functions return talloc-owned buffers.

## Dependencies and Integration Points
It depends on Samba charset conversion (`push_ucs2_talloc`, `convert_string`, `strlower_w`, `strupper_w`, `next_codepoint`), loadparm utilities, token parsing, `smb_strtox` size parsing, and fixed-size Samba string types such as `fstring`. These helpers are widely integrated across path handling, configuration parsing, name validation, command invocation, and protocol string processing.

## Risks and Edge Cases
`string_truncate` is byte-count based and can cut multibyte strings. `strlower_m` and `strupper_m` assume case conversion does not expand the remaining buffer and forcibly terminates on conversion errors. `validate_net_name` only checks invalid characters within `max_len`; it does not reject names longer than `max_len` by itself. `escape_shell_string` is careful but shell escaping is inherently context sensitive, and callers must know it targets UNIX charset shell arguments. `full_path_tos` always inserts `'/'`, so callers must avoid double separators if that matters.

## Test Signals
Tests should cover ASCII and multibyte case conversion, conversion error termination, `skip_string` with unterminated buffers and pointer overflow, trimming complete strings and multibyte suffixes, list parsing with case sensitivity, shell metacharacters inside and outside quotes, invalid UTF-8 handling, and `full_path_tos` stack-buffer vs talloc allocation paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_str.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_tdb.c -->
# sources/user-network-fs/samba/source3/lib/util_tdb.c

## Purpose
`util_tdb.c` contains source3 convenience routines around TDB packing, unpacking, logging, data rendering, and chain locking with alarm-based timeouts.

## Important APIs and Functions
The packing API is `tdb_pack` and `tdb_unpack`, with format specifiers for 8-bit, 16-bit, 32-bit, 64-bit, pointer-present tokens, null-terminated strings, fstrings, and length-prefixed blobs. `tdb_open_log` wraps `tdb_open_ex` with Samba DEBUG logging and loadparm-driven mmap/hash-size decisions. `tdb_data_cmp`, `tdb_data_string`, and `tdb_data_dbg` compare and render `TDB_DATA`. Lock helpers are `tdb_chainlock_with_timeout`, `tdb_lock_bystring_with_timeout`, and `tdb_read_lock_bystring_with_timeout`.

## Control Flow and Behavior
`tdb_pack_va` walks the format string, computes the write length even when no buffer is supplied, and writes little-endian values when space is available. `tdb_unpack` performs bounds checks before each decode and returns the consumed byte count or `-1`. For fixed blobs it checks integer wrap before allocation. `tdb_open_log` honors `lp_use_mmap`, derives per-database hash size from `tdb_hashsize:<basename>`, and supplies a logging callback. Chain-lock timeouts install a SIGALRM handler, register the alarm flag with TDB, perform read or write chain lock, then clear the alarm and handler.

## State and Persistence
TDB files opened by `tdb_open_log` are durable database state. Packing formats define persistent on-disk encoding for source3 TDB consumers. The lock timeout path uses process-global signal state (`gotalarm`, SIGALRM handler, process alarm), which is transient but process-wide.

## Dependencies and Integration Points
It depends on TDB, Samba loadparm, DEBUG, `cbuf`, hex encoding, signal helpers, and byte-order macros. It is integrated by many source3 databases that need compact records, debug rendering, and bounded lock waits.

## Risks and Edge Cases
The varargs packing contract is strict: wrong argument types or null strings for `P`/`f` can crash or panic. `tdb_pack_va` writes an 8-bit value with `SSVAL`, which writes two bytes, although the length is one; this is legacy behavior worth preserving carefully. Signal-based timeouts can interfere with other SIGALRM users in the same process. `tdb_log` leaks no memory on normal paths, but if `vasprintf` succeeds with an empty string it returns without freeing `ptr`. Lock debug prints `key.dptr` as a string, which is unsafe for non-string keys in diagnostics.

## Test Signals
Useful tests include pack-size-only calls, round-trip for every format specifier, truncated unpack inputs, oversized blob lengths and wrap checks, `tdb_open_log` hash-size/mmap configuration, `tdb_data_cmp` null and prefix cases, and chain lock timeout behavior under contention.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_transfer_file.c -->
# sources/user-network-fs/samba/source3/lib/util_transfer_file.c

## Purpose
This file implements generic fixed-size buffered transfer between random-access file-like objects and a POSIX fd wrapper for normal files.

## Important APIs and Functions
`transfer_file_internal` copies `n` bytes using caller-supplied `pread_fn` and `pwrite_fn` callbacks. `transfer_file` wraps POSIX descriptors with `sys_pread` and `sys_pwrite` through `sys_pread_fn` and `sys_pwrite_fn`.

## Control Flow and State
The transfer allocates a 64 KiB buffer, loops until `total == n` or input EOF, reads at the current offset, then loops on writes until the whole read chunk is written. It returns bytes copied, `0` for zero-length input, or `-1` on read/write allocation errors. It has no durable state.

## Dependencies and Integration Points
It depends on Samba allocation macros, DEBUG, `sys_rw`, and `transfer_file.h`. It is a reusable utility for VFS or file-copy paths that need callback-based copying rather than stream `read`/`write`.

## Risks and Test Signals
On a zero-length write callback, `transfer_file_internal` returns `total` but leaks the allocated buffer because that branch returns before `SAFE_FREE`; that is a concrete cleanup risk. Casting `off_t n` to `size_t` in `transfer_file` can misbehave for negative or too-large values on unusual platforms. Tests should cover short reads, short writes, zero write returns, callback errors, zero-byte transfers, and large transfers crossing the 64 KiB buffer boundary.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_transfer_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_tsock.c -->
# sources/user-network-fs/samba/source3/lib/util_tsock.c

## Purpose
`util_tsock.c` provides a generic tevent/tsocket async packet reader that reads an initial amount, asks a caller callback how many more bytes are needed, and repeats until the packet is complete.

## Important APIs and Functions
The public API is `tstream_read_packet_send` and `tstream_read_packet_recv`. `struct tstream_read_packet_state` stores the event context, stream, caller `more` callback, private data, dynamic buffer, and iovec. `tstream_read_packet_done` is the read completion callback.

## Control Flow and State
`send` allocates the state and initial buffer, starts `tstream_readv_send`, and registers the completion callback. On each completion, zero-byte reads are converted to `EPIPE`, errors are propagated, and a null `more` callback means the initial read is the full result. Otherwise the callback receives the current buffer and length and returns `-1` for invalid packet, `0` for complete, or a positive byte count to append. The buffer is grown with talloc and another read is issued.

## Dependencies and Integration Points
It depends on `tevent`, `tstream_context`, `tstream_readv_send/recv`, and Samba Unix error propagation helpers. It is useful for protocols with length-prefixed or self-describing packets layered over tsocket streams.

## Risks and Test Signals
The callback contract is central: a malicious or buggy `more` can request very large allocations, though integer wrap is checked. The helper reads exactly the requested chunks, so packet parsers must avoid underestimating remaining bytes. Tests should cover no-callback reads, multi-stage packet reads, callback `-1`, EOF, underlying stream errors, allocation failure, and size wrap rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_tsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_tsock.h -->
# sources/user-network-fs/samba/source3/lib/util_tsock.h

## Purpose
This header declares the async packet-read helper implemented in `util_tsock.c`.

## Important APIs and Types
It forward-declares `struct tstream_context` and declares `tstream_read_packet_send` plus `tstream_read_packet_recv`. The `more` callback accepts the current buffer, current length, and private data, and returns a signed byte count or error sentinel.

## Dependencies and Integration Points
It includes `replace.h` and `tevent.h`, making it suitable for modules already using Samba async request patterns. Integration is through standard tevent send/recv ownership rules.

## Risks and Test Signals
API risk is callback misuse: callers must keep private data valid until completion and must interpret `perrno` only when recv returns `-1`. Compile tests should verify inclusion without full tsocket internals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_tsock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_unixsids.c -->
# sources/user-network-fs/samba/source3/lib/util_unixsids.c

## Purpose
This file maps Samba's Unix Users and Unix Groups SID namespaces to Unix uid/gid concepts and provides namespace detection helpers.

## Important APIs and Functions
Exports are `sid_check_is_unix_users`, `sid_check_is_in_unix_users`, `uid_to_unix_users_sid`, `gid_to_unix_groups_sid`, `unix_users_domain_name`, `sid_check_is_unix_groups`, `sid_check_is_in_unix_groups`, and `unix_groups_domain_name`.

## Control Flow and State
Namespace checks compare against `global_sid_Unix_Users` or `global_sid_Unix_Groups`; "in namespace" checks copy the SID, split off the RID, and compare the domain. UID/GID conversion composes the namespace SID with the numeric id as RID. There is no persistent state.

## Dependencies and Integration Points
It depends on SID helpers from `security.h`. It integrates with source3 identity mapping and display-name code that needs synthetic SIDs for local Unix accounts/groups.

## Risks and Test Signals
The conversion narrows `uid_t`/`gid_t` into a RID field, so platform id width and range should be tested. Null SIDs are not checked locally. Tests should cover namespace domain SIDs, domain-plus-RID SIDs, composed uid/gid SIDs, unrelated SIDs, and boundary uid/gid values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_unixsids.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_unixsids.h -->
# sources/user-network-fs/samba/source3/lib/util_unixsids.h

## Purpose
This header declares the Unix Users and Unix Groups synthetic SID helper interface.

## Important APIs and Types
It forward-declares `struct dom_sid` and exposes checks, uid/gid SID composition, and display domain-name helpers.

## Dependencies and Integration Points
It includes `replace.h` for portability and is paired with `util_unixsids.c`. Callers are expected to include full SID definitions where they manipulate `struct dom_sid` storage.

## Risks and Test Signals
The header is low-risk but part of identity mapping ABI. Compile tests should cover consumers that include it before broader security headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_unixsids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_wellknown.c -->
# sources/user-network-fs/samba/source3/lib/util_wellknown.c

## Purpose
`util_wellknown.c` maps a fixed subset of Windows well-known SID domains and RIDs to human-readable names and maps those names back to SIDs.

## Important APIs and Data
Static maps define `rid_name_map` entries for World/Everyone, Local Authority, Creator Owner, and NT Authority. `special_domains` ties those maps to global SID constants and domain display names. Public functions are `sid_check_is_wellknown_domain`, `sid_check_is_in_wellknown_domain`, `lookup_wellknown_sid`, and `lookup_wellknown_name`.

## Control Flow and State
The file is stateless and table-driven. SID lookup strips a RID, finds the matching special domain, then scans known users for the RID. Name lookup optionally filters by supplied domain and scans each table for a case-insensitive name match before composing the output SID and returning the canonical domain string.

## Dependencies and Integration Points
It depends on SID operations, talloc string allocation, and Samba string comparisons. It integrates with account lookup paths, ACL display, and LSA-style name/SID translation for built-in well-known identities.

## Risks and Test Signals
The maps are intentionally partial; unmapped well-known RIDs return false. `lookup_wellknown_name` reads `*pdomain` and assumes it is non-null. Tests should cover exact domain detection, SID-with-RID detection, known and unknown RIDs, empty-domain name lookup, domain-qualified lookup, case-insensitive names, and talloc allocation failures where injectable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_wellknown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/version.c -->
# sources/user-network-fs/samba/source3/lib/version.c

## Purpose
This file exposes compiled Samba version and copyright strings through tiny function wrappers.

## Important APIs and Functions
`samba_version_string` returns `SAMBA_VERSION_STRING`; `samba_copyright_string` returns `SAMBA_COPYRIGHT_STRING`.

## Control Flow and State
Both functions return static compile-time strings and have no control-flow complexity or state.

## Dependencies and Integration Points
It includes `version.h`, where the generated or configured version macros are defined. Consumers use these wrappers for diagnostics, command output, and tests.

## Risks and Test Signals
Risk is build configuration drift rather than runtime behavior. Tests should assert non-null returned strings and that `version_test` prints the configured version string.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/version_test.c -->
# sources/user-network-fs/samba/source3/lib/version_test.c

## Purpose
`version_test.c` is a minimal executable test for `samba_version_string`.

## Important APIs and Functions
It defines `main`, calls `samba_version_string`, prints the result with a newline, and returns success.

## Control Flow and State
There is no state and only straight-line control flow.

## Dependencies and Integration Points
It includes source3 `includes.h`, which supplies the version function prototype. It integrates with build/test targets that verify version linkage.

## Risks and Test Signals
The comment misspells `samba_version_strion`, but behavior is unaffected. Useful signal is successful link and output matching `SAMBA_VERSION_STRING`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/version_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/winbind_util.c -->
# sources/user-network-fs/samba/source3/lib/winbind_util.c

## Purpose
`winbind_util.c` wraps libwbclient identity mapping and lookup operations behind source3-friendly functions, with stubbed no-winbind implementations when Samba is built without winbind.

## Important APIs and Functions
With `WITH_WINBIND`, exports include passwd lookups (`winbind_getpwnam`, `winbind_getpwsid`), name/SID translation (`winbind_lookup_name`, `winbind_lookup_name_ex`, `winbind_lookup_sid`), daemon health (`winbind_ping`), SID/id mapping (`winbind_sid_to_uid`, `winbind_sid_to_gid`, `winbind_xid_to_sid`), trust check (`wb_is_trusted_domain`), batch RID lookup (`winbind_lookup_rids`), id allocation, and user SID expansion (`winbind_lookup_usersids`). The `#else` branch returns false, null, or benign unknown results.

## Control Flow and State
The functions convert between Samba `dom_sid`/`unixid`/`lsa_SidType` and libwbclient structures, call `wbc*` APIs, copy results to talloc memory where needed, and free libwbclient-allocated memory. `winbind_lookup_name_ex` maps libwbclient errors to NTSTATUS and treats `SERVER_DISABLED` as `NONE_MAPPED` outside domain security.

## Dependencies and Integration Points
It depends on `nsswitch/libwbclient/wbclient.h`, SID structures, idmap NDR types, `tcopy_passwd`, loadparm security mode, and NTSTATUS mapping from `wbcErr`. It integrates with authentication, authorization, idmap, and account lookup code that should not call libwbclient directly.

## Risks and Test Signals
Memory ownership is mixed: libwbclient allocations must be freed with `wbcFreeMemory`, while returned Samba data is talloc-owned. `winbind_lookup_rids` does not explicitly check every talloc allocation after the three top-level arrays, so low-memory tests are useful. The stubs intentionally report unavailable services; callers must distinguish unsupported from not found. Tests should cover enabled and disabled builds, error mapping in `winbind_lookup_name_ex`, SID/id conversions, batch RID ownership, and no-winbind fallbacks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/winbind_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/winbind_util.h -->
# sources/user-network-fs/samba/source3/lib/winbind_util.h

## Purpose
This header declares the source3 winbind utility wrapper API.

## Important APIs and Types
It exposes name/SID lookup, SID/id mapping, winbind ping, trust-domain check, RID batch lookup, id allocation, and user SID expansion functions. It includes LSA and idmap generated headers plus libwbclient for `wbcErr`.

## Dependencies and Integration Points
The header is the integration contract between source3 identity consumers and `winbind_util.c`. It intentionally exposes Samba types (`dom_sid`, `unixid`, `lsa_SidType`) rather than raw libwbclient structures.

## Risks and Test Signals
Compile-time risk is header include ordering because it references generated NDR and libwbclient types. ABI tests should ensure signatures match both winbind-enabled and stub implementations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/winbind_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/wins_srv.c -->
# sources/user-network-fs/samba/source3/lib/wins_srv.c

## Purpose
`wins_srv.c` manages configured WINS server groups, tags, failover selection, and temporary dead-server markers. It supports multiple WINS namespaces by tagging server addresses in `wins server` configuration entries.

## Important APIs and Functions
Public functions are `wins_srv_is_dead`, `wins_srv_alive`, `wins_srv_died`, `wins_srv_count`, `wins_srv_tags`, `wins_srv_tags_free`, `wins_srv_ip_tag`, `wins_server_tag_ips`, and `wins_srv_count_tag`. Internal helpers are `wins_srv_keystr` for gencache keys and `parse_ip` for `tag:ip` entries.

## Control Flow and State
Dead WINS state is stored in `gencache.tdb` under `WINS_SRV_DEAD/<wins_ip>,<src_ip>` for 600 seconds. If Samba itself is a WINS server, many functions return loopback or a single `"*"` tag. Otherwise functions scan `lp_wins_server_list`, parse optional tags, de-duplicate tag lists, choose the first live server for a tag and source IP, or fall back to the first configured server if all are dead.

## Dependencies and Integration Points
It depends on loadparm WINS settings, IPv4 address helpers, `gencache`, and Samba allocation/string wrappers. It integrates with nmbd WINS registration and client WINS lookup logic that need failover across per-interface server groups.

## Risks and Test Signals
This code is IPv4-only (`struct in_addr`, `inet_ntoa`). `inet_ntoa` static buffers are copied quickly in most places, but logging with multiple calls can still be confusing. `wins_srv_tags` can leak partially allocated strings if allocation fails mid-list. Dead state is source-IP-specific, so tests must include multiple source addresses. Test signals include tag parsing, duplicate tag removal, local-WINS mode, all-dead fallback, gencache expiry, and `wins_server_tag_ips` empty/no-match behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/wins_srv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/xattr_tdb.c -->
# sources/user-network-fs/samba/source3/lib/xattr_tdb.c

## Purpose
`xattr_tdb.c` emulates POSIX extended attributes by storing NDR-encoded xattr arrays in a TDB/dbwrap database keyed by Samba file IDs.

## Important APIs and Functions
Public operations are `xattr_tdb_getattr`, `xattr_tdb_setattr`, `xattr_tdb_listattr`, `xattr_tdb_removeattr`, and `xattr_tdb_remove_all_attrs`. Internal helpers marshal/unmarshal `struct tdb_xattrs` (`xattr_tdb_pull_attrs`, `xattr_tdb_push_attrs`), fetch records (`xattr_tdb_load_attrs`), lock records (`xattr_tdb_lock_attrs`), and save records (`xattr_tdb_save_attrs`).

## Control Flow and Persistence
File IDs are reduced to a 16-byte dev/inode-compatible key via `push_file_id_16` for backward compatibility. Reads fetch and decode a record, scan for the named EA, steal the value blob to caller memory, and set `ENOATTR` when absent. Sets fetch-lock the record, decode existing attributes, enforce `XATTR_CREATE` and `XATTR_REPLACE`, grow the EA array if needed, point the EA name/value at caller data, marshal, and store. Listing first calculates the required null-separated name-list length, checks buffer size, then copies names. Remove swaps the target entry with the last entry and either saves or deletes the record. Remove-all deletes the locked record.

## Dependencies and Integration Points
It depends on dbwrap, TDB data helpers, NDR generated xattr/file_id types, `file_id` utilities, errno conventions, and `XATTR_*` flags. It integrates with VFS modules that need xattr behavior on filesystems lacking native xattrs or for Samba-specific metadata.

## Risks and Edge Cases
Backward-compatible 16-byte file IDs can alias if newer file ID components matter. `xattr_tdb_setattr` stores pointers to caller `name` and `value` in the temporary structure before immediate marshal; this is safe only because save happens before those pointers go out of scope. On decode failure, some error paths return `-1` without setting a precise errno. `listattr` returns the required size with `errno=ERANGE`, matching xattr conventions. Tests should cover create/replace flags, missing records, corrupt NDR blobs, empty EA sets deleting records, list buffer sizing, value ownership after get, and remove-all idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/xattr_tdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/xattr_tdb.h -->
# sources/user-network-fs/samba/source3/lib/xattr_tdb.h

## Purpose
This header declares the TDB-backed xattr emulation API.

## Important APIs and Types
It includes generated `file_id` definitions and declares get, set, list, remove, and remove-all functions operating on `struct db_context`, `struct file_id`, and `DATA_BLOB`.

## Dependencies and Integration Points
It is consumed by VFS or metadata modules that already know their dbwrap database and file IDs. It keeps database creation/opening outside the helper API.

## Risks and Test Signals
The header lacks include guards in the viewed content, so repeated inclusion relies on surrounding headers or compiler tolerance. Compile tests should include it multiple times in a translation unit and verify declarations match `xattr_tdb.c`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/xattr_tdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_ldap_protos.h -->
# sources/user-network-fs/samba/source3/libads/ads_ldap_protos.h

## Purpose
This header declares LDAP-oriented ADS helper APIs that are implemented across libads LDAP modules. It is a prototype aggregation point for opening LDAP connections, extracting LDAP values, searching, reconnecting, processing results, and parsing AD-specific objects.

## Important APIs and Types
Declared APIs include `ldap_open_with_timeout`, `ads_msgfree`, `ads_get_dn`, pull helpers for strings, ranged strings, uint32, GUID, SID, security descriptors, and usernames, account/printer find helpers, `ads_do_search*` variants, retry/search-by-SID helpers, LDAP message iteration helpers, `ads_process_results`, `ads_dump`, GPO parsing, SD flag searches, token SID lookup, and joinable OU lookup.

## Control Flow and State
As a header, it has no runtime flow. Its API shape shows the central ADS pattern: most functions take `ADS_STRUCT *ads`, return `ADS_STATUS` or extracted talloc-owned values, and operate on `LDAPMessage` results that callers must free with `ads_msgfree`.

## Dependencies and Integration Points
It depends on LDAP types, ADS structures, GUID/SID/security descriptor types, and GPO forward declarations. It is consumed by libads callers that need LDAP operations without including every implementation-specific source header.

## Risks and Test Signals
Risk is prototype drift against implementation files such as `ldap.c`, `ldap_utils.c`, and schema/GPO modules. Compile coverage should include modules using ranged results, retry paths, and security descriptor flag searches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_ldap_protos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_proto.h -->
# sources/user-network-fs/samba/source3/libads/ads_proto.h

## Purpose
`ads_proto.h` is the broad libads public prototype header for source3 Active Directory operations, covering ADS structure construction, LDAP operations, SASL/TLS wrapping, machine account management, printer/user/group helpers, SPN management, keytab listing, and trust account password changes.

## Important APIs and Types
It defines `enum ads_sasl_state_e` with plain/sign/seal modes and `struct spn_struct`. It declares `ads_build_path`, `ads_build_dn`, `ads_build_domain`, `ads_init`, `ads_set_sasl_wrap_flags`, `ads_disp_sd`, `ads_keytab_list`, SPN add/delete/list functions, connection functions, LDAP search/modify helpers, machine account create/move/join/leave helpers, domain metadata queries, schema/config path lookups, SASL/TLS wrapper setup, `parse_spn`, and `sync_pw2keytabs`.

## Control Flow and State
As a header it has no state, but it exposes the libads lifecycle: allocate/init `ADS_STRUCT`, connect with credentials or machine account, perform LDAP/Kerberos/SASL operations, then disconnect via `ADS_STRUCT` destructor or explicit calls.

## Dependencies and Integration Points
It depends on `ADS_STRUCT`, `ADS_STATUS`, LDAP-related types, generated RPC/printing types, and credential types. It is a central integration point for `net ads`, domain join, authentication, keytab maintenance, printer publishing, and schema-aware security descriptor display.

## Risks and Test Signals
The header aggregates many modules, so conditional build coverage matters. Tests should compile AD-enabled and AD-disabled feature matrices and verify declarations remain synchronized with source definitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_status.c -->
# sources/user-network-fs/samba/source3/libads/ads_status.c

## Purpose
`ads_status.c` centralizes libads error construction, conversion to NTSTATUS, and human-readable error string formatting across LDAP, Kerberos, GSSAPI, system errno, and NTSTATUS domains.

## Important APIs and Functions
Exports are `ads_build_error`, `ads_build_nt_error`, `ads_ntstatus`, `ads_errstr`, and, under Kerberos support, `gss_err_to_ntstatus`. They operate on `ADS_STATUS` from `ads_status.h`.

## Control Flow and Behavior
The builders validate error-domain usage and fall back to system errors if called with the wrong constructor. `ads_ntstatus` switches on `error_type`, mapping errno through `map_nt_error_from_unix`, LDAP timeout to `NT_STATUS_IO_TIMEOUT`, generic LDAP to `NT_STATUS_LDAP`, Kerberos through `krb5_to_nt_status`, and NT errors directly. `ads_errstr` picks the corresponding string source; for GSS it calls `gss_display_status` for both major and minor codes and returns a talloc string.

## State and Dependencies
There is no durable state. Dependencies are conditional LDAP, Kerberos, and GSS APIs, Samba NTSTATUS mappings, talloc, and DEBUG.

## Risks and Test Signals
`ads_errstr` returns talloc stack memory for GSS strings, so callers must not assume permanent storage. Constructor misuse is logged but not fatal. Tests should cover each `enum ads_error_type`, LDAP timeout mapping, success detection, GSS major/minor formatting, and disabled LDAP/Kerberos compile paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_status.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_status.h -->
# sources/user-network-fs/samba/source3/libads/ads_status.h

## Purpose
This header defines the `ADS_STATUS` error container and convenience macros used throughout libads.

## Important APIs and Types
`enum ads_error_type` identifies KRB5, GSS, LDAP, system, and NT error domains. `ADS_STATUS` stores the domain, either integer rc or NTSTATUS, and a GSS minor status. Macros include `ADS_ERROR_LDAP`, `ADS_ERROR_SYSTEM`, `ADS_ERROR_KRB5`, `ADS_ERROR_GSS`, `ADS_ERROR_NT`, `ADS_ERR_OK`, `ADS_SUCCESS`, and `ADS_ERROR_HAVE_NO_MEMORY`.

## Dependencies and Integration Points
It integrates every libads module that returns `ADS_STATUS`, especially LDAP and Kerberos code. It assumes NTSTATUS and LDAP constants are available in including contexts.

## Risks and Test Signals
`ADS_ERR_OK` treats non-NT errors as `rc == 0`, so callers must construct errors in the correct domain. Compile tests should cover macro use in modules with and without LDAP/Kerberos feature macros.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_status.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_struct.c -->
# sources/user-network-fs/samba/source3/libads/ads_struct.c

## Purpose
`ads_struct.c` builds LDAP distinguished-name/domain strings and initializes `ADS_STRUCT`, the central libads connection/config/auth object.

## Important APIs and Functions
Exports are `ads_build_path`, `ads_build_dn`, `ads_build_domain`, `ads_init`, and `ads_set_sasl_wrap_flags`. The static `ads_destructor` disconnects LDAP state when talloc frees an `ADS_STRUCT`.

## Control Flow and State
`ads_build_path` splits a realm using caller separators and builds a field-prefixed path either forward or reverse. `ads_build_dn` converts `AA.BB.CC` to `dc=AA,dc=BB,dc=CC`; `ads_build_domain` lowercases and converts `dc=` DN components back to dotted DNS. `ads_init` talloc-allocates and zeroes the structure, copies realm/workgroup/LDAP server strings, adjusts requested SASL state based on `lp_client_ldap_sasl_wrapping`, sets auth flags, allocates reconnect state, and stores the configured LDAP page size.

## Dependencies and Integration Points
It depends on `ads.h`, loadparm, string helpers, talloc, and LDAP cleanup when available. It is the first step for most AD flows, including machine joins, LDAP queries, keytab refresh, and security descriptor display.

## Risks and Test Signals
`ads_build_path` mixes manual allocation, `asprintf`, `SMB_STRDUP`, and length checks, so allocation and truncation tests are valuable. `ads_build_domain` mutates a duplicated DN and assumes simple `dc=` formatting. `ads_init` silently downgrades SASL state to plain when LDAPS/StartTLS wrapping is configured because the transport wrapper provides protection. Tests should cover null optional strings, SASL flag combinations, destructor disconnect behavior, DN round-trips, and page-size initialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/ads_struct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/authdata.c -->
# sources/user-network-fs/samba/source3/libads/authdata.c

## Purpose
`authdata.c` obtains Kerberos tickets from username/password credentials, validates an AP-REQ through Samba GENSEC, and extracts PAC authorization data for callers.

## Important APIs and Functions
Under `HAVE_KRB5`, `spnego_gen_krb5_wrap` wraps a Kerberos ticket in a GSS/SPNEGO-style ASN.1 application token. `kerberos_return_pac` is the exported high-level API returning canonical principal/realm and a `PAC_DATA_CTR`.

## Control Flow and State
`kerberos_return_pac` creates or uses a credential cache, builds `user@realm` if needed, calls `kerberos_kinit_password_ext`, rejects the no-preauth fallback signal where expire and renew times are zero, gets a service ticket with optional S4U2SELF impersonation, wraps it as `TOK_ID_KRB_AP_REQ`, starts a server-side Kerberos GENSEC context, feeds the AP-REQ to `gensec_update`, calls `gensec_session_info`, and retrieves the PAC from the auth context. Temporary memory, ticket blobs, session keys, and in-memory ccache are cleaned up on exit.

## Dependencies and Integration Points
It depends on Kerberos helpers, PAC utilities, ASN.1 helpers, GENSEC, auth4 context, loadparm, SPNEGO constants, and Samba credential-cache helpers. It integrates with authentication paths that need to validate a password via Kerberos and derive group/PAC data without a remote SMB server.

## Risks and Test Signals
This code manipulates sensitive passwords, tickets, session keys, and PAC data; cleanup and logging must avoid leaks. Behavior depends heavily on KDC policy, PAC availability, and GENSEC backend configuration. Tests should cover cache supplied vs unique memory cache, missing PAC, expired/preauth-required accounts, wrong password, S4U2SELF failures, canonical output ownership, and request_pac toggles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/authdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/cldap.c -->
# sources/user-network-fs/samba/source3/libads/cldap.c

## Purpose
`cldap.c` performs ADS CLDAP netlogon pings against a domain controller on UDP/389 and exposes a NETLOGON_NT_VERSION_5EX response helper.

## Important APIs and Functions
The static `ads_cldap_netlogon` builds a `tsocket_address` from a `sockaddr_storage`, calls `netlogon_pings` with a domain, requested ntversion, required flags, and timeout, and returns the first response. `ads_cldap_netlogon_5` requests `NETLOGON_NT_VERSION_5 | NETLOGON_NT_VERSION_5EX` and copies out `NETLOGON_SAM_LOGON_RESPONSE_EX`.

## Control Flow and State
The helper always targets LDAP port 389, asks for one wanted server, and uses a timeout of at least three seconds or half the LDAP timeout. It fails if no response arrives or if the response version is not 5EX. It has no durable state.

## Dependencies and Integration Points
It depends on CLDAP/netlogon client libraries, `tsocket`, loadparm ping protocol and timeout, NTSTATUS mapping, and generated netlogon NDR structures. It is used by ADS DC discovery and site/KDC selection logic.

## Risks and Test Signals
Network behavior and firewall drops dominate failures. `ads_cldap_netlogon_5` shallow-copies fields from a talloc-owned response; callers must ensure referenced subfields remain valid or understand generated struct ownership. Tests should cover address conversion failure, timeout/no response, required-flag mismatch, wrong ntversion, IPv4/IPv6 addresses, and successful pdc/domain response extraction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/cldap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/cldap.h -->
# sources/user-network-fs/samba/source3/libads/cldap.h

## Purpose
This header declares the libads CLDAP netlogon v5 helper.

## Important APIs and Types
It includes netlogon definitions and declares `ads_cldap_netlogon_5`, which takes a memory context, target socket address, realm, required flags, and output `NETLOGON_SAM_LOGON_RESPONSE_EX`.

## Dependencies and Integration Points
It is paired with `cldap.c` and consumed by AD discovery code that needs a compact CLDAP ping API.

## Risks and Test Signals
Compile coverage should verify generated netlogon types are visible. Runtime ownership expectations for strings inside the copied reply should be tested by callers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/cldap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/disp_sec.c -->
# sources/user-network-fs/samba/source3/libads/disp_sec.c

## Purpose
`disp_sec.c` prints Active Directory security descriptors, ACLs, ACEs, access masks, trustees, and object GUID annotations for diagnostic command output.

## Important APIs and Functions
Under `HAVE_LDAP`, `ads_disp_sd` is the public printer. Static helpers include `ads_disp_perms`, `ads_interprete_guid_from_object`, `ads_disp_sec_ace_object`, `ads_disp_ace`, and `ads_disp_acl`. The permission table maps selected AD/standard rights to text.

## Control Flow and State
`ads_disp_sd` lazily populates `ads->config.schema_path` and `ads->config.config_path` if possible, prints descriptor header/owner/group, then iterates SACL and DACL ACEs. Object ACE GUIDs are resolved first as schema attributes and then as extended rights. Output goes directly to stdout using `printf`.

## Dependencies and Integration Points
It depends on ADS schema/config lookup, GUID and SID formatting, security descriptor structures, and AD security right constants. It is integrated with tools such as `net ads` diagnostics rather than core server request paths.

## Risks and Test Signals
This is display code, but it mutates `ADS_STRUCT` config cache fields and assumes stdout is appropriate. The permission table contains duplicate `SEC_ADS_CONTROL_ACCESS` entries for change/reset password, so printed labels may be ambiguous. Tests should cover null descriptors, null ACLs, object ACEs with resolvable and unknown GUIDs, full-control masks, remaining unknown bits, and missing schema/config paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/disp_sec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/kerberos.c -->
# sources/user-network-fs/samba/source3/libads/kerberos.c

## Purpose
`kerberos.c` implements source3 Kerberos utility operations: password-based kinit, multi-secret kinit using passwords or NT hashes, explicit-KDC AS exchange over TCP, credential-cache destruction, key derivation from strings, KDC discovery formatting, and local private `krb5.conf` generation for AD domains.

## Important APIs and Functions
Public APIs are `kerberos_kinit_password_ext`, `kerberos_kinit_passwords_ext`, `ads_kdestroy`, `create_kerberos_key_from_string`, `kerberos_kinit_password`, and `create_local_private_krb5_conf_for_domain_internal`. Internal building blocks include `kerb_prompter`, `kerberos_kinit_generic_once`, password callback `kerberos_kinit_password_ext_cb`, explicit KDC transaction helpers (`kerberos_transaction_cache_create`, `kerberos_transaction_send/recv`, `kerberos_transaction`), multi-secret callback `kerberos_kinit_passwords_ext_cb`, `add_sockaddr_unique`, `print_canonical_sockaddr_with_port`, `get_kdc_ip_string`, and platform-specific `get_enctypes`.

## Control Flow and Behavior
`kerberos_kinit_generic_once` initializes a Kerberos context, optionally applies time offset, resolves the supplied ccache, parses the principal, configures get-init-creds options including renewable lifetime, forwardable tickets, canonicalization, optional PAC request, and optional NetBIOS address, calls a supplied credential callback, stores returned TGT credentials in the ccache, and returns canonical principal/realm and NTSTATUS mapping. `kerberos_kinit_passwords_ext` optionally builds an explicit KDC transaction cache, then tries each supplied password or NT hash until success or a non-preauth failure. With explicit KDC and `krb5_init_creds_step`, it drives the AS exchange itself over a tevent TCP stream, writing a 4-byte length-prefixed request and reading a length-prefixed reply.

## State and Persistence
The kinit paths write to a named Kerberos credential cache supplied by the caller. `ads_kdestroy` destroys that cache. `create_local_private_krb5_conf_for_domain_internal` creates `lock_path("smb_krb5")`, writes a temporary private krb5 config with realm/KDC/enctype settings, atomically renames it to `krb5.conf.<domain>`, and sets `KRB5_CONFIG` in the process environment. Optional compile-time `OVERWRITE_SYSTEM_KRB5_CONF` can symlink `/etc/krb5.conf`, which is intentionally marked as extreme legacy behavior.

## Dependencies and Integration Points
It depends on Kerberos libraries (MIT/Heimdal branches), Samba Kerberos wrappers, netlogon ping, KDC DNS discovery, secrets and loadparm settings, `tevent`, `tstream`, `tsocket`, local lock paths, and negative connection cache helpers. It integrates with domain join, machine-account authentication, password changes, PAC retrieval, and keytab refresh.

## Risks and Edge Cases
The prompter deliberately refuses new-password prompts to avoid library loops on expired keys. Explicit-KDC support requires `HAVE_KRB5_INIT_CREDS_STEP`; without it, explicit KDC is rejected. The multi-secret path uses a memory keytab for NT hash authentication with RC4-HMAC and must handle weak crypto policy elsewhere. `get_kdc_ip_string` relies on network pings and negative connection cache propagation, so generated configs can omit temporarily blacklisted DCs. Private `krb5.conf` creation changes process-global `KRB5_CONFIG`, affecting subsequent Kerberos operations. Tests should include MIT and Heimdal builds, wrong password vs preauth failure iteration, NT hash fallback, explicit KDC timeout, ccache errors, config generation with DNS lookup enabled/disabled, IPv6 KDC formatting, weak-crypto/enctype settings, and atomic rename failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/kerberos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/kerberos_keytab.c -->
# sources/user-network-fs/samba/source3/libads/kerberos_keytab.c

## Purpose
`kerberos_keytab.c` synchronizes the local machine password stored in Samba secrets to Kerberos keytabs and lists keytab contents. It supports configured keytab descriptors, default keytab generation, AD-synchronized SPNs/UPN/account names, kvno and enctype synchronization, aliases, and post-sync scripts.

## Important APIs and Types
Public APIs are `sync_pw2keytabs` and `ads_keytab_list`. Core types are `enum spn_spec_type`, `struct pw2kt_specifier`, `struct pw2kt_keytab_desc`, `struct pw2kt_global_state`, and `struct pw2kt_keytab_state`. Important helpers parse configuration (`pw2kt_scan_spec`, `pw2kt_scan_line`, `pw2kt_default_cfg`), build entries from secrets (`pw2kt_process_add_pw`, `pw2kt_process_add_info`, `pw2kt_add_prefix`, `pw2kt_process_specifier`), reconcile keytabs (`pw2kt_process_keytab`, `pw2kt_process_kt2ar`), fetch AD metadata (`pw2kt_get_dc_info`), and choose defaults (`pw2kt_default_keytab_name`).

## Control Flow and Behavior
`sync_pw2keytabs` is a no-op outside domain-member role. It parses `sync machine password to keytab` or builds a default descriptor based on `kerberos method`, optionally queries AD for supported enctypes, kvno, SPNs, UPN, and sAMAccountName, initializes secrets, fetches or upgrades domain info, processes each keytab, and runs an optional sync script. `pw2kt_process_keytab` initializes Kerberos, optionally finds the strongest common AD/library enctype, expands configured specifiers into target principals, opens/creates the keytab, reads existing entries, then either replaces rolling negative-vno entries or, with real kvno sync, adds missing entries and removes stale entries by principal/vno/enctype comparison.

## State and Persistence
Persistent state includes local keytab files, Samba secrets database domain info, optional AD LDAP metadata reads, and optional side effects from `sync machine password script`. Keytab entries may include current, old, older, and next-change machine passwords with kvnos `kvno`, `kvno-1`, `kvno-2`, and `kvno+1`, or synthetic negative vnos when AD kvno sync is disabled.

## Dependencies and Integration Points
It depends on Kerberos keytab APIs, Samba Kerberos wrappers, `ads_init`/LDAP machine-account queries, secrets database upgrade/fetch, loadparm options (`sync machine password to keytab`, aliases, DNS hostnames, kerberos method), string helpers, and `smbrun`. It integrates with domain join/password rotation and service authentication that relies on local keytabs.

## Risks and Edge Cases
Configuration parsing is strict: malformed `:` or `,` separators fail the whole sync. Without `machine_password`, a descriptor is skipped. Enctype sync fails if AD and local Kerberos library share no supported enctype. Keytab reconciliation is fault-tolerant for remove failures but still returns add/open errors. Negative vno handling is unusual and warns about unexpected existing entries. Tests should cover disabled config, default config for each kerberos method, malformed specifiers, alias/additional-hostname expansion, AD metadata failures, secrets fetch failures, kvno sync vs negative-vno mode, enctype preference selection, stale entry removal, post-sync script failure, and `ads_keytab_list` output/error cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/kerberos_keytab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/kerberos_proto.h -->
# sources/user-network-fs/samba/source3/libads/kerberos_proto.h

## Purpose
This header declares libads Kerberos helper APIs for kinit, ccache destruction, local krb5 config generation, PAC retrieval, password setting, and key derivation.

## Important APIs and Types
It defines `DEFAULT_KRB5_PORT`, forward-declares `PAC_DATA_CTR` and `samr_Password`, includes Kerberos system headers and `ads_status.h`, declares `kerberos_kinit_password_ext`, `kerberos_kinit_passwords_ext`, `ads_kdestroy`, `kerberos_kinit_password`, `create_local_private_krb5_conf_for_domain_internal`, inline wrappers for normal and join-time krb5 config creation, `kerberos_return_pac`, `ads_krb5_set_password`, `kerberos_set_password`, and `create_kerberos_key_from_string` under `HAVE_KRB5`.

## Dependencies and Integration Points
It is consumed by `authdata.c`, `krb5_setpw.c`, domain join code, and keytab/password flows. The inline wrappers encode an important policy distinction: normal configs allow DNS KDC lookup, while join-time configs disable it to avoid replication races after machine account creation.

## Risks and Test Signals
Header risk lies in conditional Kerberos type visibility and inline policy changes. Compile tests should cover Kerberos-enabled and disabled builds and ensure callers get the correct DNS lookup behavior through the two inline wrappers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/kerberos_proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/krb5_setpw.c -->
# sources/user-network-fs/samba/source3/libads/krb5_setpw.c

## Purpose
`krb5_setpw.c` implements Kerberos password set/change flows for ADS: setting another principal's password using an existing ccache and changing the authenticating principal's own expired/current password using raw initial credentials.

## Important APIs and Functions
Public functions under `HAVE_KRB5` are `ads_krb5_set_password` and `kerberos_set_password`. Internal helpers are `kpasswd_err_to_krb5_err`, `kerb_prompter`, and `ads_krb5_chg_password`.

## Control Flow and Behavior
`ads_krb5_set_password` requires a ccache name, initializes Kerberos, optionally parses a target principal, resolves the ccache, calls `krb5_set_password_using_ccache`, maps kpasswd result codes, and cleans up principal, ccache, and context. `ads_krb5_chg_password` parses the principal, configures short-lived non-forwardable/proxiable initial creds for `kadmin/changepw@REALM`, adds a NetBIOS Kerberos address to avoid Heimdal local-address issues, obtains initial creds with the old password and custom prompter, then calls `krb5_set_password`. `kerberos_set_password` chooses the own-password change path when auth and target principals match; otherwise it creates a unique memory ccache, kinit's as the auth principal, and sets the target password through that ccache.

## State and Persistence
Password changes persist on the KDC/AD. The different-principal path creates and destroys a temporary memory credential cache. No local durable files are written by this file.

## Dependencies and Integration Points
It depends on Kerberos libraries, Samba Kerberos wrappers, `kerberos_kinit_password`, ADS status mapping, NetBIOS name configuration, and ASN.1 include infrastructure. It integrates with password change tools and domain administration flows.

## Risks and Test Signals
Kpasswd result mapping is lossy but maps common policy/access/principal/enctype failures. The own-password path intentionally avoids ccache use and relies on service principal canonicalization behavior that differs between MIT and Heimdal; MIT canonicalization is disabled in a documented bug block. Sensitive old/new passwords should not be logged. Tests should cover same-principal vs admin-set paths, missing ccache, bad old password, policy reject, unknown principal, ccache creation/destruction, kadmin/changepw realm construction, and MIT/Heimdal conditional behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/libads/krb5_setpw.c -->
