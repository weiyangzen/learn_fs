# sources/distributed-fs/ceph-client/fs/smb/client/smb2ops.c

## Purpose

`smb2ops.c` is the dialect operation binding layer for the Linux CIFS/SMB client implementation. It supplies SMB2, SMB2.1, SMB3.0, and SMB3.1.1 implementations of the generic `struct smb_version_operations` and `struct smb_version_values` contracts used by the rest of the client. The file mostly adapts common VFS/CIFS actions into SMB2-family wire commands, controls dialect-specific capabilities, and implements SMB3-only behavior such as encryption transforms, multichannel interface discovery, copy offload, sparse/fallocate helpers, leases, durable replay markers, and query/passthrough compounds.

The final section is the main integration point: `smb20_operations` when legacy SMB2.0 is enabled, `smb21_operations`, `smb30_operations`, and `smb311_operations` populate function pointers consumed through `server->ops`; `smb20_values`, `smb21_values`, `smb3any_values`, `smbdefault_values`, `smb30_values`, `smb302_values`, and `smb311_values` describe fixed dialect constants such as protocol id, requested capabilities, header size, signing bits, lock flags, and lease context size.

## Important APIs, Types, and Functions

- Credit and MID management: `change_conf()`, `smb2_add_credits()`, `smb2_set_credits()`, `smb2_get_credits_field()`, `smb2_wait_mtu_credits()`, `smb2_adjust_credits()`, `smb2_get_next_mid()`, `smb2_revert_current_mid()`, `smb2_find_mid()`, and `smb2_find_dequeue_mid()` maintain request credits, in-flight accounting, reconnect instances, message ids, and pending MID lookup.
- Negotiation and sizing: `smb2_need_neg()`, `smb2_negotiate()`, `smb2_negotiate_wsize()`, `smb3_negotiate_wsize()`, `smb2_negotiate_rsize()`, and `smb3_negotiate_rsize()` reset MID state, call `SMB2_negotiate()`, and clamp negotiated I/O sizes against server maxima, large-MTU support, and SMB Direct limits.
- Server interface discovery: `SMB3_request_interfaces()` issues `FSCTL_QUERY_NETWORK_INTERFACE_INFO`; `parse_server_interfaces()` parses IPv4/IPv6 interface records, updates `ses->iface_list`, marks inactive interfaces, and maintains sorted interface preference through `iface_cmp()`.
- Filesystem/share discovery: `smb2_qfs_tcon()`, `smb3_qfs_tcon()`, `smb2_queryfs()`, and `smb311_queryfs()` issue QFS calls and, for SMB3.1.1 POSIX extensions, prefer `SMB311_posix_qfs_info()`.
- Path, file, xattr, and passthrough helpers: `smb2_is_path_accessible()`, `smb2_get_srv_inum()`, `smb2_query_file_info()`, `smb2_query_info_compound()`, `smb2_ioctl_query_info()`, `move_smb2_ea_to_cifs()`, `smb2_query_eas()`, and `smb2_set_ea()` convert kernel/VFS operations into open-query-close or open-set-close compounds.
- Copy, clone, sparse, and allocation helpers: `SMB2_request_res_key()`, `smb2_copychunk_range()`, `smb2_set_sparse()`, `smb2_set_file_size()`, `smb2_duplicate_extents()`, `smb3_zero_range()`, `smb3_punch_hole()`, `smb3_simple_falloc()`, `smb3_collapse_range()`, `smb3_insert_range()`, `smb3_llseek()`, `smb3_fiemap()`, and `smb3_fallocate()` implement offloaded copy, reflink-style extent duplication, sparse-file state, fallocate variants, hole/data seeking, and fiemap through SMB2 IOCTLs.
- Compound/replay helpers: `smb2_set_next_command()`, `smb2_set_related()`, `smb2_set_replay()`, and `smb2_should_replay()` manage compound alignment, related-operation flags, SMB3 replay flags, and exponential retry backoff.
- Status handling: `smb2_is_status_pending()`, `smb2_is_session_expired()`, `smb2_is_status_io_timeout()`, and `smb2_is_network_name_deleted()` interpret SMB2 status codes and update credits, session reconnect state, or tree reconnect flags.
- Oplocks and leases: `smb2_oplock_response()`, `smb2_downgrade_oplock()`, `smb3_downgrade_oplock()`, `smb2_set_oplock_level()`, `smb21_set_oplock_level()`, `smb3_set_oplock_level()`, `map_oplock_to_lease()`, `smb2_create_lease_buf()`, `smb3_create_lease_buf()`, `smb2_parse_lease_buf()`, and `smb3_parse_lease_buf()` bridge wire oplock/lease state into `CIFS_I(inode)->oplock`, lease keys, epochs, and cache purge decisions.
- Security, DFS, and special files: `smb2_get_dfs_refer()`, `get_smb2_acl_by_fid()`, `get_smb2_acl_by_path()`, `get_smb2_acl()`, `set_smb2_acl()`, `__cifs_sfu_make_node()`, `cifs_sfu_make_node()`, and `smb2_make_node()` handle DFS referrals, NT security descriptors, SFU-style device/symlink/socket/FIFO emulation, and reparse-point node creation.
- SMB3 encryption/decryption: `fill_transform_hdr()`, `smb2_aead_req_alloc()`, `smb2_get_aead_req()`, `smb2_get_enc_key()`, `crypt_message()`, `smb3_init_transform_rq()`, `decrypt_raw_data()`, `receive_encrypted_read()`, `receive_encrypted_standard()`, `smb3_receive_transform()`, and `smb3_handle_read_data()` construct AEAD scatterlists, choose session keys, apply AES-CCM/GCM transforms, decrypt compound responses, and offload large encrypted reads.

## Control Flow

Most runtime entry points reach this file indirectly through `server->ops`. After negotiation selects a dialect, the matching `smb_version_operations` table drives higher-level CIFS code for open, close, read, write, directory, metadata, lock, lease, security, and transform behavior.

For ordinary metadata compounds, helpers follow a repeated pattern: select a channel with `cifs_pick_channel()`, convert paths to UTF-16, build one or more `smb_rqst` entries, mark `NextCommand` and `RELATED_OPERATIONS`, optionally mark replay after transient errors, call `compound_send_recv()`, validate response offsets/lengths, copy results back to kernel or userspace buffers, then free all request and response buffers. `smb2_query_info_compound()`, `smb2_ioctl_query_info()`, `smb2_set_ea()`, and `smb2_query_dir_first()` are representative.

Read/write data flow is split between synchronous wrappers and specialized receive paths. `smb2_sync_read()` and `smb2_sync_write()` inject persistent and volatile FIDs before calling `SMB2_read()` and `SMB2_write()`. For encrypted responses, `smb3_receive_transform()` validates the transform header and dispatches either normal compound decryption or a large-read path. Large encrypted reads can be copied into folio queues and decrypted on `decrypt_wq`; completion finds or dequeues the MID, copies data to the subrequest iterator, updates MID state, and invokes callbacks.

Fallocate and sparse-file control flow starts from `smb3_fallocate()`, dispatches by mode, invalidates/writes back local page cache where server-side IOCTLs will mutate data, updates EOF and netfs/fscache sizes when required, and uses `FSCTL_SET_ZERO_DATA`, `FSCTL_QUERY_ALLOCATED_RANGES`, or `FSCTL_SRV_COPYCHUNK_WRITE` depending on mode. Range collapse and insert are emulated with copychunk plus EOF and zeroing operations.

Credit control is continuous across request lifetimes. Send-side waits reserve credits through the dialect `wait_mtu_credits` callback; response handling returns credits with `smb2_add_credits()`, which also rebalances normal, echo, and oplock credit pools when in-flight requests drain. Reconnect instances prevent stale responses from returning credits to a new transport generation.

## State and Persistence Behavior

This source does not persist data outside the mounted SMB server, but it updates a large amount of in-memory client state that controls durable protocol behavior:

- `TCP_Server_Info` fields: normal/echo/oplock credits, `in_flight`, `max_in_flight`, `reconnect_instance`, `current_mid`, `channel_sequence_num`, `tcpStatus`, `total_read`, encryption contexts, multichannel primary/secondary identity, and receive buffers.
- `cifs_ses` fields: interface discovery state such as `iface_list`, `iface_count`, `iface_last_update`, `chan_lock`, and channel interface assignments. Interfaces are reference-counted and removed when missing from fresh server output.
- `cifs_tcon` fields: share capabilities, copychunk limits (`max_chunks`, `max_bytes_copy`, `max_bytes_chunk`), `broken_sparse_sup`, `need_reconnect`, POSIX extension state, bytes read/written, open counts, and SMB2 command statistics.
- `cifsInodeInfo` and netfs state: oplock/lease bits, lease keys and epochs, sparse attribute state, remote size, zero point, cache purge decisions, and fscache cookie size.
- `mid_q_entry` state: pending request lookup, deletion from queue, decrypted flag, response buffer size, response state, callbacks, and retry-needed state when reconnect races occur.

Server-visible persistence happens through SMB commands: file size changes, sparse/compression/integrity bits, ACLs, EAs, special SFU file content, snapshot queries, directory notifications, zeroed ranges, duplicate extents, and copychunk results are applied on the remote share. Local cache state is invalidated or resized around those operations to keep VFS, netfs, and server state coherent.

## Dependencies

The file depends heavily on CIFS/SMB client internals declared in `cifsfs.h`, `cifsglob.h`, `cifsproto.h`, `smb2proto.h`, `smb2pdu.h`, `smb2glob.h`, `cifs_ioctl.h`, `smbdirect.h`, `fscache.h`, `fs_context.h`, `cached_dir.h`, and `reparse.h`. Wire constants and structures come from SMB2/SMB3 protocol headers and FSCTL structures.

Kernel dependencies include VFS and inode helpers, page cache and netfs/fscache APIs, folio queues, scatterlists, crypto AEAD, UUID generation, userspace copy helpers, wait queues, spinlocks, list/kref handling, socket address structures, and fiemap/fallocate interfaces. Optional behavior is gated by `CONFIG_CIFS_XATTR`, `CONFIG_CIFS_SMB_DIRECT`, `CONFIG_CIFS_STATS2`, `CONFIG_CIFS_DFS_UPCALL`, and `CONFIG_CIFS_ALLOW_INSECURE_LEGACY`.

The file calls many protocol primitives implemented elsewhere: `SMB2_open*`, `SMB2_close*`, `SMB2_query_info*`, `SMB2_ioctl*`, `SMB2_read`, `SMB2_write`, `SMB2_lock`, `SMB2_echo`, `SMB2_tcon`, `SMB2_tdis`, `SMB2_sess_setup`, `SMB2_logoff`, `SMB2_set_eof`, `SMB2_query_acl`, `SMB2_set_acl`, `SMB311_posix_qfs_info`, signing-key generators, negotiate validation, and path/reparse helpers.

## Integration Points

The primary integration point is the dialect vtable assignment. Higher layers do not call most static helpers directly; they call `server->ops->open`, `server->ops->queryfs`, `server->ops->fallocate`, `server->ops->receive_transform`, and similar callbacks. SMB2.1 adds large-MTU credit handling and leasing; SMB3.0 switches to SMB3 sizing, share capability dump, close-with-getattr, encryption transforms, integrity, duplicate extents, validate-negotiate, fallocate, and multichannel interface query; SMB3.1.1 adds POSIX mkdir and POSIX statfs query when available.

This file is also a bridge between transport receive code and request completion. `smb2_next_header()` parses compound next-command boundaries, `smb3_receive_transform()` decrypts encrypted frames before normal response handling, and MID lookup binds wire `MessageId` and command ids back to pending client requests.

VFS integrations include `llseek`, `fiemap`, fallocate, xattrs, ACLs, mknod, path accessibility checks, directory enumeration, statfs, and ioctl passthrough. Network integration appears in SMB Direct I/O-size clamping and multichannel interface selection. DFS integration uses an IPC or fallback tcon to request referrals and parse them into DFS target nodes.

## Risks and Edge Cases

- Credit accounting is concurrency-sensitive. `smb2_add_credits()` and `smb2_adjust_credits()` must avoid returning stale reconnect-generation credits, underflowing `in_flight`, starving echo/oplock credits, or accepting excessive server credit grants.
- Compound request setup is fragile around padding and encryption. `smb2_set_next_command()` flattens iovecs when encryption is required because padding iovecs are not handled by the encryption layer; changes to request layout can break compounds.
- Response validation is critical. Query-info, copychunk, directory, encrypted read, and allocated-range paths perform explicit length/offset checks; missing checks would expose kernel memory corruption or userspace copy bugs from malformed server replies.
- Cache coherency is easy to regress in range mutation paths. Zeroing, hole punching, collapse, insert, and clone operations must write back or invalidate local page cache and update `netfs_inode`, inode size, zero point, and fscache size consistently.
- Replay handling is subtle. Only replayable errors should trigger `smb2_should_replay()`, and SMB3 replay flags must be set on every appropriate request in a compound after backoff.
- Multichannel interface parsing must preserve active references and sorted preference while deleting inactive interfaces. Incorrect kref or list handling could race channel selection.
- Encryption/decryption paths depend on session lookup by `SessionId`, the correct AEAD key length for AES-128 versus AES-256 and CCM versus GCM, correct associated-data length, transform nonce construction, scatterlist sizing, and safe large-read offload lifetime management.
- Some server behaviors are deliberately tolerated, such as empty network interface lists, Azure snapshot sizing quirks, Samba sparse support not reflected in FS attributes, Windows read responses with odd data offsets, and copychunk servers returning revised limits.

## Test Signals

Useful validation signals include successful kernel builds across configs with and without `CONFIG_CIFS_XATTR`, `CONFIG_CIFS_SMB_DIRECT`, and legacy SMB2.0 support; static analysis for endian, overflow, and userspace-copy paths; and CIFS/SMB xfstests that exercise SMB2.1, SMB3.0, and SMB3.1.1 mounts.

Runtime coverage should include mount negotiation and reconnect, credit exhaustion and recovery, multichannel interface refresh, encrypted compounds and large encrypted reads, DFS referrals, ACL and EA get/set, copychunk and duplicate extents, sparse file hole/data seeking, fiemap, fallocate modes (`PUNCH_HOLE`, `ZERO_RANGE`, `COLLAPSE_RANGE`, `INSERT_RANGE`, `KEEP_SIZE`), directory enumeration, passthrough query/ioctl, snapshot enumeration, notify, lease/oplock break handling, and network-name-deleted tree reconnect.

Tracepoints and counters provide operational signals: `trace_smb3_add_credits`, `trace_smb3_wait_credits`, `trace_smb3_rw_credits`, copychunk/clone/fallocate/zero/query-dir traces, MID callback behavior, `/proc` or debugfs SMB2 command sent/failed counters from `smb2_print_stats()`, and server logs for negotiated capabilities, encryption, leases, and FSCTL support.
