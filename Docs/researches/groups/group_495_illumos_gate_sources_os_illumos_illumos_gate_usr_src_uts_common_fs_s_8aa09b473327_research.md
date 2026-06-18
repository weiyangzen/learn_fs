# Group Research: group_495_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_8aa09b473327

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_create.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_create.c

Read completely. This file implements the SMB2 `CREATE` command, including request decoding, path extraction, create-context parsing, common open execution, lease/oplock acquisition, durable handle setup or reconnect, and final SMB2 create response encoding.

The main entry point is `smb2_create()`. It decodes the fixed SMB2 create request, validates name offsets and path rules, builds a shadow mbuf for create contexts, then dispatches `smb_common_open()` unless the request is a durable-handle reconnect. It handles protocol-specific validation for impersonation level, oplock level, leases, durable handle v1/v2 contexts, persistent handle flags, delete-on-close, backup intent credentials, query maximal access, on-disk ID responses, and Apple `AAPL` create context replies.

Create-context handling is split into `smb2_decode_create_ctx()`, `smb2_encode_create_ctx()`, `smb2_encode_create_ctx_elem()`, and `smb2_free_create_ctx()`. Supported incoming contexts include EA, security descriptor, durable request/reconnect v1/v2, allocation size, maximal access, timewarp, on-disk ID, leases, and Apple extensions. Unsupported or unknown context IDs are ignored after structural validation. Responses may include maximal access, on-disk ID, Apple extension data, lease state, and durable handle acknowledgements.

Important dependencies are `smb_common_open()`, `smb2_dh_reconnect()`, `smb2_dh_make_persistent()`, `smb2_lease_create()`, `smb2_lease_acquire()`, `smb2_oplock_acquire()`, `smb2_aapl_crctx()`, and SMB mbuf encode/decode helpers. Durable and lease state is stored through `sr->arg.open`, `sr->fid_ofile`, and create-context flags.

Notable behavior: durable reconnect intentionally ignores most create parameters and several context types; persistent durable handles require continuous-availability tree support; EA create contexts are rejected as unsupported; leases are restricted to valid cache-state combinations; non-disk trees and non-regular files suppress oplocks/leases.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_create.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_dispatch.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_dispatch.c

Read completely. This file is the SMB2/SMB3 dispatch core. It maps SMB2 command codes to handlers, accepts new requests from the session reader, decrypts SMB3 transform messages, validates and dispatches compound commands, manages credits, signing, encryption, async interim responses, error responses, FID lookup, statistics, and postwork.

`smb2_disp_table` binds commands such as negotiate, session setup, logoff, tree connect, create, close, flush, read/write, lock, ioctl, cancel, echo, query/set info, change notify, and oplock break. `smb2sr_newrq()` validates SMB2 magic, decrypts encrypted SMB3 messages with `smb3_decrypt_msg()`, scans compound headers to validate message-ID ranges and credit charges, special-cases cancel requests, and queues normal work on the server taskq.

`smb2sr_work()` is the central compound-command loop. It decodes headers, writes tentative reply headers, shadows each command payload, enforces related-operation inheritance for user/tree/file state, verifies sessions and tree connects, enforces session/tree encryption policies, checks SMB2 signatures, adjusts credits, invokes the command handler, encodes final headers, signs or encrypts replies, flushes durable handle nvlist updates, sends the reply, runs postwork, and frees the request.

Async handling is implemented by `smb2sr_go_async()`, `smb2sr_go_async_indefinite()`, and `smb2sr_send_interim()`. These send SMB2 `STATUS_PENDING` interim responses, update credits at interim time, and preserve or reset compound reply state depending on bounded vs indefinite blocking behavior.

Important exported utilities include `smb2_decode_header()`, `smb2_encode_header()`, `smb2_send_reply()`, `smb2sr_put_error*()`, `smb2sr_lookup_fid()`, dispatch stats init/fini/update, and postwork queue helpers. The file is a high-risk integration point because most SMB2 security, credit, async, encryption, and compound semantics converge here.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_dispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_durable.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_durable.c

Read completely. This file implements SMB2 durable, resilient, and persistent handle support, including persistent-handle import for continuous-availability shares, nvlist-backed on-disk state, durable reconnect validation, timeout expiration, orphan cleanup, and the resiliency FSCTL.

Durable-handle policy starts with `smb_dh_create_allowed()` and `smb_dh_should_save()`. Durable creation is allowed for files with batch oplocks, handle-caching leases, or persistent v2 requests, and optionally for directories when persistent. Save decisions depend on server/session/user/tree shutdown state, explicit logoff preservation mode, resilient state, persistent state, and whether the open still has suitable batch or handle-caching state.

Persistent handles are stored as share-root named streams with names like `:<persistid>:$CA`. `smb2_dh_new_ca_share()` schedules import work for CA shares. `smb2_dh_import_share()` creates an internal tree connect, scans stream names, reads nvlist state, and calls `smb2_dh_import_handle()`. Import restores the original path, owner SID credential, access/share/options, create GUID, client UUID, lease or oplock state, byte-range locks, lock sequence table, pending sticky times, persistent ID, and orphan durable state.

`smb2_dh_make_persistent()` creates the state stream and initializes fixed nvlist fields. `smb2_dh_update_nvfile()` serializes the nvlist with XDR and writes it to the persistent stream. Update helpers persist oplock/lease state, locks, lock sequences, and sticky timestamps.

Reconnect is handled by `smb2_dh_reconnect()`, with validation in `smb2_dh_reconnect_checks()`: same user, matching lease/client/name rules, v2 persistent flag consistency, and create GUID match. Expiration and shutdown paths are handled by `smb2_durable_timers()`, `smb2_dh_close_my_orphans()`, `smb2_dh_shutdown()`, and internal expire/cleanup callbacks.

`smb2_fsctl_set_resilient()` implements `FSCTL_LMR_REQUEST_RESILIENCY`, setting resilient durable state and timeout for regular files.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_durable.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_echo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_echo.c

Read completely. This is the SMB2 `ECHO` command handler.

`smb2_echo()` decodes the request structure as `StructSize` plus reserved field, requires `StructSize == 4`, emits DTrace start/done probes, and encodes a minimal SMB2 Echo response with structure size 4 and reserved zero. It does not require user or tree context; that suppression is configured in `smb2_dispatch.c`.

The file has no filesystem dependencies and only includes `smbsrv/smb2_kproto.h`. Its primary purpose is connection liveness/protocol keepalive handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_echo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_flush.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_flush.c

Read completely. This file implements SMB2 `FLUSH`.

`smb2_flush()` decodes the request header fields and SMB2 file ID, requiring `StructSize == 24`. It resolves the file through `smb2sr_lookup_fid()` before DTrace start probing, then calls `smb_ofile_flush()` when lookup succeeds. On lookup or flush failure it writes an SMB2 error response; on success it encodes a structure-size-4 flush reply.

Dependencies are `smb2sr_lookup_fid()` from dispatch, `smb_ofile_flush()`, SMB mbuf helpers, and filesystem operation support through `smbsrv/smb_fsops.h`. Related-compound inherited FIDs are supported indirectly by `smb2sr_lookup_fid()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_flush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_copychunk.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_copychunk.c

Read completely. This file implements `FSCTL_SRV_COPYCHUNK` and `FSCTL_SRV_COPYCHUNK_WRITE`, plus Apple server-side copy behavior.

`smb2_fsctl_copychunk()` validates the destination handle, access rights, output buffer size, resume key, source handle, source access, and chunk count. Resume keys are the opaque 24-byte blobs produced by `FSCTL_SRV_REQUEST_RESUME_KEY`, internally carrying SMB2 persistent and temporal file IDs. Limits are controlled by `smb2_copychunk_max_cnt`, `smb2_copychunk_max_seg`, and `smb2_copychunk_max_total`.

Chunk-array decoding is handled by `smb2_fsctl_copychunk_decode()`, which validates nonzero per-chunk lengths, maximum segment size, and total size. `smb2_fsctl_copychunk_array()` processes normal chunk lists and returns partial progress through `copychunk_resp`. `smb2_fsctl_copychunk_1()` checks source and destination byte-range locks, then delegates the copy to `smb2_sparse_copy()`.

Apple behavior is implemented in `smb2_fsctl_copychunk_aapl()`: when AAPL extensions are active, `chunk_cnt == 0` means copy the whole file. It loops until EOF, cancellation, timeout, or error, using a tunable timeout, and then calls `smb2_fsctl_copychunk_meta()` to copy attributes and DACL metadata. Metadata copying bypasses normal ofile WRITE_DAC checks but still relies on filesystem-level checks.

The IOCTL layer has special handling for this FSCTL because it may return an error status with a data payload containing server limits or partial-copy results.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_copychunk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_fs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_fs.c

Read completely. This file dispatches SMB2 IOCTL FSCTL subcodes for `FILE_DEVICE_FILE_SYSTEM` and `FILE_DEVICE_NETWORK_FILE_SYSTEM`.

For filesystem-device FSCTLs, `smb2_fsctl_fs()` maps compression, sparse, zero-data, allocated-ranges, ODX read/write, file-region query, and selected unsupported/invalid control codes. It requires the current FID to be a disk file before dispatching. Sparse and ODX work is delegated to sibling files.

For network-filesystem-device FSCTLs, `smb2_fsctl_netfs()` maps snapshot enumeration, resume-key creation, copychunk, resiliency, network-interface info, validate-negotiate, and unknown codes. Most require a disk file; `FSCTL_VALIDATE_NEGOTIATE_INFO` and network-interface info do not.

`smb2_fsctl_get_resume_key()` returns the server’s opaque copychunk resume key as persistent ID, temporal FID, and padding. This key is later consumed by `smb2_fsctl_copychunk()`.

Compression support is minimal: get returns compression state zero and set accepts only zero, returning `NT_STATUS_COMPRESSION_DISABLED` for nonzero compression state. Notable implementation detail: `smb2_fsctl_get_compression()` encodes to `fsctl->in_mbc`; because this is a getter, this is worth checking against expected output-buffer usage.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_odx.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_odx.c

Read completely. This file implements SMB2/FSCTL offloaded data transfer: `FSCTL_OFFLOAD_READ` and `FSCTL_OFFLOAD_WRITE`.

ODX read returns a 512-byte storage offload token representing a source range. The implementation supports a standard zero-data token and a server-native token carrying source SMB2 file ID, source offset, source EOF, and source tree ID. Tunables include `smb2_odx_enable`, `smb2_odx_read_max`, `smb2_odx_write_max`, and `smb2_odx_buf_size`.

`smb2_fsctl_odx_read()` validates read access, input/output sizes, block alignment, regular non-stream file constraints, delete state, locks, and EOF. It uses `smb_fsop_next_alloc_range()` to decide whether the requested range is entirely a hole. Hole ranges receive a zero-data token; data ranges receive a native token. It can set the all-zero-beyond flag when no more data exists.

`smb2_fsctl_odx_write()` validates write access, decodes write arguments and token, checks output size, block alignment, destination type, delete state, locks, and EOF. Zero tokens are handled by `smb2_fsctl_odx_write_zeros()`, which punches holes and extends the file when needed. Native tokens are handled by `smb2_fsctl_odx_write_native1()`, which locates the source ofile, possibly through another tree, validates source access, allocates a copy buffer, and uses `smb2_sparse_copy()`.

Token wire helpers `smb_odx_get_token()` and `smb_odx_put_token()` handle fixed 512-byte token framing and big-endian token metadata. EOF crossing and block-aligned transfer reporting are carefully handled so clients can continue copy loops correctly.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_odx.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_sparse.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_sparse.c

Read completely. This file implements sparse-file related FSCTLs and a sparse-preserving copy helper.

`smb2_fsctl_set_sparse()` toggles `FILE_ATTRIBUTE_SPARSE_FILE`, requiring a regular file and at least one of write attributes, write data, or append data access. It reads current DOS attributes and writes updated attributes only when a change is needed.

`smb2_fsctl_set_zero_data()` decodes a signed start/end range, validates ordering and regular-file status, requires write-data access, clamps zeroing to EOF, checks byte-range lock conflicts, and calls `smb_fsop_freesp()` to create holes or free space.

`smb2_fsctl_query_alloc_ranges()` validates the requested signed range, requires read-data access, clamps to EOF, and returns allocated regions. Non-sparse files return one allocated range. Sparse files use `smb_fsop_next_alloc_range()` to walk data/hole extents and encode ranges until output space is exhausted.

`smb2_sparse_copy()` is shared by copychunk and ODX. It walks source allocated ranges, punches holes in the destination for source gaps, then reads and writes allocated data with a caller-provided buffer. It preserves sparseness where possible and falls back to normal copying when allocation-range queries are unsupported.

`smb2_fsctl_query_file_regions()` implements Hyper-V-style valid-data/file-region reporting. It validates optional input, requires output space for the fixed header plus one region, reads file size and DOS attributes, and encodes hole/data region entries with total and returned counts. If output space is insufficient it returns buffer overflow after reporting partial region counts.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_fsctl_sparse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ioctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ioctl.c

Read completely. This file implements SMB2 `IOCTL` request handling and dispatch to FSCTL handlers.

`smb2_ioctl()` decodes the SMB2 IOCTL fixed request, extracts control code, file ID, input/output offsets and counts, max response sizes, and flags. It shadows the input buffer when present, bounds input and output by `smb2_max_trans`, and sets `sr->raw_data` as the FSCTL output buffer.

It enforces SMB2 IOCTL rules: non-FSCTL flags return not supported; selected control codes such as DFS referrals, network interface info, validate negotiate, and pipe wait must use all-ones file IDs; all other control codes require `smb2sr_lookup_fid()` and treat lookup failure as file closed.

Dispatch is by device type extracted from `CtlCode`: DFS goes to `smb_dfs_fsctl()`, filesystem controls to `smb2_fsctl_fs()`, named pipes to `smb_opipe_fsctl()`, and network filesystem controls to `smb2_fsctl_netfs()`. Unsupported device types return not supported.

Error handling is nuanced. Normal NT error severity responses are encoded as SMB2 errors without data, but copychunk FSCTLs are allowed to return error statuses with a data payload. Successful or data-bearing responses encode the SMB2 IOCTL reply with output offset/count and raw-data payload.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lease.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lease.c

Read completely. This file implements SMB2 lease support and lease-break handling, integrated with the existing oplock subsystem.

Lease lifecycle support includes `smb2_lease_init()`, `smb2_lease_fini()`, internal hold/release logic, lease hash computation, and `smb2_lease_create()`. Leases are stored in a server hash table keyed by lease key and client UUID. A lease is associated with one node, can be shared by multiple ofiles, and carries state, epoch, version, client UUID, and the ofile currently owning the underlying oplock.

`smb2_lease_break_ack()` decodes SMB2 lease break acknowledgements, looks up the lease, finds the ofile holding the lease oplock, validates the acknowledged state, clears breaking flags, calls `smb_oplock_ack_break()`, updates lease/ofile state, and persists durable state when needed.

Lease-break sending is handled by `smb2_lease_send_break()`. It builds an SMB2 lease-break notification, tries to send it on an active session associated with the lease, closes non-durable/nonpersistent handles when no connection is available, waits for ACKs when required, and performs local ACK downgrade on timeout or send failure.

`smb2_lease_acquire()` converts requested SMB2 lease caching bits into internal granular oplock state, respects tree oplock policy, attempts promotion in stages from write to handle to read caching, updates lease epoch and state on new grants, and may go async while waiting for oplock breaks.

`smb2_lease_ofile_close()` handles lease ownership transfer when the ofile owning the underlying oplock closes. It attempts to move the oplock to another open or durable/orphaned handle on the same lease, otherwise clears lease state and wakes ACK waiters.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lease.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lock.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lock.c

Read completely. This file implements SMB2 byte-range locking.

`smb2_lock()` decodes the SMB2 lock request, resolves the FID, validates lock count and node presence, applies dialect-specific lock-sequence replay handling, allocates and decodes the `SMB2_LOCK_ELEMENT` array, then dispatches either unlock processing or lock processing based on the first element’s flags. Persistent durable handles trigger `smb2_dh_update_locks()` after successful processing.

`smb2_unlock()` requires every element to be an unlock element and calls `smb_unlock_range()` for each range. `smb2_locks()` processes nonblocking lock arrays, validates flag combinations, maps shared/exclusive flags to internal lock types, rejects mixed invalid forms, and rolls back previously acquired locks if a later element fails.

`smb2_lock_blocking()` handles the special one-element blocking lock case. It first tries a zero-timeout lock to avoid async overhead. If the result means it would block, it sends an indefinite async interim response with `smb2sr_go_async_indefinite()` and then retries with an effectively infinite timeout.

Lock replay support uses SMB2 `LockSequenceIndex` and `LockSequenceNumber`. `smb2_lock_chk_lockseq()` detects repeated successful operations for durable/resilient reconnect scenarios, while `smb2_lock_set_lockseq()` records successful sequences in `ofile->f_lock_seq`. SMB2 ignores lock PIDs and uses PID zero internally.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_lock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_logoff.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_logoff.c

Read completely. This file implements SMB2 `LOGOFF`.

`smb2_logoff()` decodes the 4-byte request structure, validates `StructSize == 4`, requires an active `uid_user`, emits DTrace probes, sets `sr->uid_user->preserve_opens = SMB2_DH_PRESERVE_ALL`, and calls `smb_user_logoff()`. The preservation flag is important for durable handle policy in `smb_dh_should_save()`: protocol logoff requests preserve durable opens for reconnect instead of destroying them.

On success it encodes a minimal SMB2 Logoff reply with structure size 4 and reserved zero. The command suppresses tree requirements in the dispatch table but still requires a user session.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb2_logoff.c -->