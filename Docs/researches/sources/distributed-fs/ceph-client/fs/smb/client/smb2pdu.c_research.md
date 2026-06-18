# sources/distributed-fs/ceph-client/fs/smb/client/smb2pdu.c

## Purpose
`smb2pdu.c` is the central SMB2/SMB3 client protocol implementation for constructing, sending, replaying, and decoding command PDUs. It owns the command workers for negotiate, session setup, tree connect/disconnect, create/open, ioctl, close, query/set info, change notify, echo, flush, read/write, directory enumeration, lock, oplock/lease acknowledgement, and filesystem information queries. It also contains SMB3.1.1 negotiate context construction/parsing, POSIX extension handling, DFS path prefixing, durable/persistent handle create contexts, multichannel reconnect coordination, and RDMA offload integration points.

## Important APIs, Types, And Functions
The command entry points exported through `smb2proto.h` include `SMB2_negotiate`, `SMB2_sess_setup`, `SMB2_logoff`, `SMB2_tcon`, `SMB2_tdis`, `SMB2_open`/`SMB2_open_init`/`SMB2_open_free`, `SMB2_ioctl`/`SMB2_ioctl_init`, `SMB2_close`, `SMB2_flush`, `SMB2_query_info`, `SMB2_query_acl`, `SMB2_get_srv_num`, `SMB2_read`, `SMB2_write`, async `smb2_async_readv`/`smb2_async_writev`, `SMB2_query_directory`, `SMB2_set_eof`, `SMB2_set_acl`, `SMB2_set_ea`, `SMB2_oplock_break`, `SMB2_lease_break`, `SMB311_posix_qfs_info`, `SMB2_QFS_attr`, and `smb2_lockv`/`SMB2_lock`.

Core helpers are `smb2_hdr_assemble`, `smb2_reconnect`, `smb2_plain_req_init`, `smb2_ioctl_req_init`, `smb2_parse_contexts`, `smb2_validate_iov`, `smb2_validate_and_copy_iov`, `posix_info_sid_size`, and `posix_info_parse`. `smb3_encryption_required` centralizes whether a request should be transformed based on session flags, share flags, mount `seal`, and global mandatory seal policy. `smb3_update_ses_channels` coordinates multichannel expansion or disablement after reconnect or capability changes.

## Control Flow
Most workers follow the same pattern: select a channel with `cifs_pick_channel`, determine transform/sign/replay flags, allocate a request with `smb2_plain_req_init` or a command-specific init function, fill fixed and variable PDU fields, optionally add create or IO context vectors, send through `cifs_send_recv` or `cifs_call_async`, validate server offsets/lengths, copy or retain response payloads, release request/response buffers, and retry through `smb2_should_replay` for replayable failures.

Negotiation builds dialect arrays for explicit/default/SMB3-any modes, sends SMB3.1.1 negotiate contexts for preauth, encryption, netname, POSIX, optional compression, and optional signing, then validates dialect/security/capabilities and updates server state. Session setup is a small state machine around Kerberos or RawNTLMSSP phases, storing session IDs, auth keys, and derived signing/encryption keys.

Create/open flow builds DFS-aware paths and a variable list of lease, durable/persistent, POSIX, snapshot, security descriptor, query-id, and EA contexts. Read/write paths have synchronous and async variants; async callbacks verify signatures, manage credits, update netfs subrequests, trace progress/errors, and deregister SMBDirect MRs.

## State And Persistence Behavior
The file mutates negotiated server state (`dialect`, `ops`, `vals`, capabilities, sizes, cipher, compression, preauth hash, AEAD handles), session state (`Suid`, flags, auth keys, derived keys, `session_estab`), tree state (`tid`, share flags/caps, maximal access, reconnect flags, copy chunk defaults), file state (FIDs, lease keys/epoch, remote open count), search buffers, filesystem attributes, IO stats, replay counters, and reconnect queues. It does not persist local files.

## Dependencies And Integration Points
It integrates with CIFS core structures/protocol helpers, SMB2 transport signing/MID setup, SMBDirect, compression, DFS, SPNEGO/key upcall, NTLMSSP, ACL/SID helpers, netfs IO completion, tracepoints, common SMB2 status/fsctl definitions, and lower send paths via `cifs_send_recv`/`cifs_call_async`.

## Risks
Highest risk areas are packed wire-buffer construction, variable-length context lists, and server-controlled offsets/lengths. Changes near `CreateContextsOffset`, `OutputBufferOffset`, `NextEntryOffset`, POSIX SID/name parsing, or DFS path rewriting can introduce memory corruption or malformed PDU acceptance. Replay/reconnect behavior is subtle for handle-based commands. Signing/encryption decisions must stay aligned with dialect rules. RDMA offload must deregister MRs on all completion paths to avoid IO deadlock.

## Test Signals
Useful signals include dialect negotiation, SMB3.1.1 context fuzzing, guest/null/Kerberos/NTLMSSP auth, mandatory signing/sealing, DFS create paths, durable/persistent reconnect, POSIX mkdir/open/query-dir, malformed offset/length injection, async read/write retry and credit accounting, SMBDirect offload, compression-enabled writes, change notify/query directory EOF, and tracepoint coverage.
