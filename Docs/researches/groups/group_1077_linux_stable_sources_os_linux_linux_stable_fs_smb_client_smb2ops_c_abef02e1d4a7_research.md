# Group Research: group_1077_linux_stable_sources_os_linux_linux_stable_fs_smb_client_smb2ops_c_abef02e1d4a7

Scope: `Docs/research_subset_a.md`; the listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2ops.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/client/smb2ops.c

## Summary
Implements the SMB2/SMB3 version-operation layer for the Linux CIFS/SMB client. The file supplies the protocol-specific `smb_version_operations` and `smb_version_values` tables for SMB2.0, SMB2.1, SMB3.0, SMB3.0.2, SMB3.1.1, and default/any dialect negotiation, and backs those tables with helpers for credits, request IDs, compounding, leases/oplocks, xattrs, ACLs, DFS referrals, multichannel interface discovery, server-side copy/clone, fallocate-style range operations, encrypted transform handling, large read receive handling, and dialect-specific capability values.

## Main Responsibilities
- Manage SMB2/3 credit accounting, including echo/oplock credit reservation, MTU-credit waits, reconnect-instance protection, in-flight tracking, and read/write credit adjustment.
- Provide MID allocation, MID lookup/dequeue, compound response walking, message-detail dumping, and reconnect-sensitive status checks.
- Negotiate read/write sizes for SMB2 and SMB3, including large-MTU limits and SMB Direct RDMA fragment/read-write limits.
- Query and maintain SMB3 multichannel server interface lists from `FSCTL_QUERY_NETWORK_INTERFACE_INFO`.
- Probe share and path accessibility, query filesystem attributes, query file info by path or open file, and expose server inode numbers.
- Convert SMB2 extended attributes to Linux xattr list/get semantics and set EAs through compounded open/set-info/close requests.
- Provide passthrough ioctl/query/set-info support for privileged callers via compounded SMB2 create, ioctl/query/set-info, and close operations.
- Implement server-side copy and clone paths through resume keys, `FSCTL_SRV_COPYCHUNK_WRITE`, and `FSCTL_DUPLICATE_EXTENTS_TO_FILE`.
- Implement sparse/compression/integrity/snapshot/change-notify helpers through SMB2/3 FSCTLs.
- Implement directory enumeration open/query and query-next/close hooks.
- Translate leases and oplocks between SMB wire states and CIFS cache flags, including SMB3 epoch-based cache purge decisions.
- Build SMB2 and SMB3 lease create contexts and parse lease response contexts.
- Implement ACL get/set by path or FID using SMB2 security descriptor queries.
- Implement SMB3 fallocate behaviors: punch hole, zero range, simple preallocation, collapse range, insert range, `SEEK_DATA`/`SEEK_HOLE`, and fiemap using allocated-range queries and copychunk.
- Build, encrypt, decrypt, receive, and split SMB3 transform/encrypted messages, including large encrypted read handling and optional decrypt offload.
- Create special files through SFU emulation or reparse-point support.
- Publish final dialect operation and value tables that plug these helpers into the rest of the CIFS client.

## Key Interfaces
- Credit and MID operations: `smb2_add_credits()`, `smb2_set_credits()`, `smb2_get_credits_field()`, `smb2_wait_mtu_credits()`, `smb2_adjust_credits()`, `smb2_get_next_mid()`, `smb2_find_mid()`, and `smb2_find_dequeue_mid()`.
- Negotiation and sizing: `smb2_negotiate()`, `smb2_need_neg()`, `smb2_negotiate_wsize()`, `smb3_negotiate_wsize()`, `smb2_negotiate_rsize()`, and `smb3_negotiate_rsize()`.
- Share/path/query operations: `SMB3_request_interfaces()`, `smb3_qfs_tcon()`, `smb2_qfs_tcon()`, `smb2_is_path_accessible()`, `smb2_query_file_info()`, `smb2_query_info_compound()`, `smb2_queryfs()`, and `smb311_queryfs()`.
- File and range operations: `smb2_close_file()`, `smb2_close_getattr()`, `smb2_flush_file()`, `smb2_sync_read()`, `smb2_sync_write()`, `smb2_set_file_size()`, `smb2_copychunk_range()`, `smb2_duplicate_extents()`, and `smb3_fallocate()`.
- Metadata/control surfaces: `smb2_ioctl_query_info()`, `smb2_query_eas()`, `smb2_set_ea()`, `get_smb2_acl()`, `set_smb2_acl()`, `smb3_enum_snapshots()`, `smb3_notify()`, and `smb2_get_dfs_refer()`.
- Lease/oplock operations: `smb2_oplock_response()`, `smb2_downgrade_oplock()`, `smb3_downgrade_oplock()`, `smb2_set_oplock_level()`, `smb21_set_oplock_level()`, `smb3_set_oplock_level()`, `smb2_create_lease_buf()`, `smb3_create_lease_buf()`, `smb2_parse_lease_buf()`, and `smb3_parse_lease_buf()`.
- Encryption/transform receive: `smb3_init_transform_rq()`, `crypt_message()`, `decrypt_raw_data()`, `smb3_receive_transform()`, `receive_encrypted_read()`, `receive_encrypted_standard()`, and `smb3_handle_read_data()`.
- Dialect tables: `smb20_operations`, `smb21_operations`, `smb30_operations`, `smb311_operations`, plus `smb20_values`, `smb21_values`, `smb3any_values`, `smbdefault_values`, `smb30_values`, `smb302_values`, and `smb311_values`.

## Control Flow And Behavior
Credit handling separates normal, echo, and oplock credits. When responses return credits, `smb2_add_credits()` checks reconnect instances before returning credits, prevents credit overflow near 64K, tracks invalid in-flight states, rebalances reserved echo/oplock credits when operations drain, and wakes waiters. Large I/O uses `smb2_wait_mtu_credits()` to reserve enough credits for the transfer while deliberately leaving credits available for reopen and other control operations. `smb2_adjust_credits()` can return excess credits after partial read/write progress but refuses to adjust upward and rejects stale reconnect instances.

MID handling is SMB2-specific: message IDs are taken from `server->current_mid`, responses are matched by MID and command, and encrypted transform frames are not matched until decrypted. Compound request helpers set `NextCommand`, `SMB2_FLAGS_RELATED_OPERATIONS`, and replay flags. For encrypted compounds, `smb2_set_next_command()` flattens request iovecs into the first buffer because the encryption layer cannot consume padding iovecs.

Mount and share setup uses query-filesystem helpers to open the root directory, optionally reuse a cached root directory handle, request multichannel interfaces on SMB3, and then query attribute/device/volume/sector-size information. Path accessibility opens the target for attributes and maps invalid-name DFS-link cases into remote-link semantics, while respecting `CIFS_MOUNT_NO_DFS`.

Extended attribute support maps SMB2 `FILE_FULL_EA_INFORMATION` lists to Linux `user.*` xattr names. Listing computes or copies null-separated names with `user.` prefixes, named gets return only the matching value, and malformed EA chains are rejected on length/offset overruns. EA setting first optionally checks existing EA space, applies a conservative buffer-size guard, then sends a replayable open/set-info/close compound.

The passthrough ioctl/query-info path accepts a bounded user `struct smb_query_info`, opens the target, sends either an FSCTL, set-info EOF request, or query-info request, closes the handle, and copies bounded output back to userspace. FSCTL and set-info passthroughs require `CAP_SYS_ADMIN`, and response offsets/lengths are checked against the returned iovec before copying.

Server-side copy first obtains a source resume key with `FSCTL_SRV_REQUEST_RESUME_KEY`, then sends copychunk batches bounded by `tcon->max_chunks`, `tcon->max_bytes_copy`, and `tcon->max_bytes_chunk`. It validates that the server did not report more bytes or chunks than requested, handles partial successful copies by rewinding offsets, and adapts copy limits after server `-EINVAL` responses before retrying. Clone/duplicate-extents checks share block-refcount support, extends destination EOF when needed, updates local/netfs size state, and sends `FSCTL_DUPLICATE_EXTENTS_TO_FILE`.

Range mutation helpers coordinate server FSCTLs with local cache state. Zero range and punch hole invalidate page cache, wait for outstanding netfs I/O, use `FSCTL_SET_ZERO_DATA`, and update EOF/netfs/fscache size when extending. Simple fallocate either extends EOF, writes zeroes into small sparse holes, or clears the sparse flag for near-whole-file allocation. Collapse and insert range use writeback, page-cache invalidation, copychunk within the same file, EOF updates, zeroing, and netfs zero-point adjustments. `llseek()` and `fiemap()` use `FSCTL_QUERY_ALLOCATED_RANGES`, flushing writable handles first so server allocation state reflects recent writes.

Lease and oplock logic maps SMB2 oplock levels and SMB2/3 lease states into CIFS cache flags. SMB3 downgrade and set-level paths use lease epochs to decide when cached data must be purged after breaks or stale lease-state transitions. Lease create contexts differ between SMB2 lease v1 and SMB3 lease v2, with SMB3 supporting parent lease keys, lease flags, and epochs.

Encryption support builds SMB3 transform headers, selects the session encryption/decryption key by session id, configures AES-CCM or AES-GCM AEAD parameters, builds scatterlists over request iovecs and iter data, and encrypts or decrypts in place. Large encrypted reads are received into folio queues, decrypted either inline or on `decrypt_wq`, and then passed through read-response validation and iterator copying. Standard encrypted responses are decrypted, split by `NextCommand`, associated with mids, and handled as normal or custom MID callbacks.

## State And Synchronization
The file coordinates several shared CIFS state domains: `server->req_lock` protects credits and in-flight counts; `server->srv_lock` protects TCP status checks; `server->mid_counter_lock` protects MID allocation; `server->mid_queue_lock` protects pending MID lists; `ses->iface_lock` and `ses->chan_lock` protect multichannel interface/channel state; `cifs_tcp_ses_lock` protects session/tcon list walks; inode `i_lock` protects local timestamp/size/netfs updates; and mapping invalidate locks serialize range mutations with page-cache state.

Correctness depends on matching reference and buffer ownership across compounded request setup/free, response buffer transfer to callers, cached-directory handle use, tcon/tlink acquisition, MID dequeue/requeue during decrypt offload, and folio-queue allocation/free. Replay paths reinitialize mutable local state, select a channel again, mark compound requests as replay operations for SMB3+, and back off exponentially through `smb2_should_replay()`.

## Cross-File Interactions
This file is the glue between generic CIFS client logic and SMB2/3 wire helpers. It calls request builders and protocol operations from `smb2pdu.c`, prototypes from `smb2proto.h`, global types from `cifsglob.h`, path and inode helpers from the broader SMB client, DFS parsing and invalid-name handling, cached directory helpers from `cached_dir.h`, fscache helpers from `fscache.h`, reparse helpers from `reparse.h`, SMB Direct parameters from `smbdirect.h`, and mount-context flags/options from `fs_context.h`.

The exported operation tables are consumed through `server->ops` and `server->vals` throughout files such as open/reopen, file I/O, directory enumeration, inode refresh, xattr handling, ACL handling, mount setup, and reconnect paths. Dialect differences are centralized here: SMB2.0 lacks newer SMB3 transform/signing/capability hooks, SMB2.1 adds leases and MTU credit waits, SMB3 adds encryption, multichannel, persistent handles, copy/clone/fallocate improvements, and SMB3.1.1 swaps in POSIX qfs/mkdir and SMB3.1.1 signing-key generation.

## Risks
The highest-risk areas are credit accounting across reconnects, compound request replay, encrypted compound splitting, and large encrypted read offload, because each combines shared state, async callbacks, and buffer ownership. Range operations are also sensitive: zeroing, punching, collapse, insert, copychunk, and fiemap must keep server state, page cache, netfs remote size, zero point, and fscache coherency aligned. EA, ACL, snapshot, notify, and passthrough ioctl paths expose server metadata/control operations to userspace and depend on strict length, offset, capability, and privilege checks.

Multichannel interface parsing must reject malformed `Next` offsets and keep interface references stable while replacing inactive entries. Lease epoch handling controls cache invalidation; mistakes can either discard useful cache unnecessarily or retain stale data. The dialect operation tables are broad and easy to miswire: adding or changing a helper must be checked against each dialect table and its value table so protocol capabilities, signing/encryption, POSIX support, and create-context sizes remain consistent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/client/smb2ops.c -->