# sources/distributed-fs/ceph-client/fs/dlm/rcom.c

## Purpose
`rcom.c` implements DLM recovery communication messages. These RCOM packets coordinate recovery status barriers, slot/config exchange, directory-name transfer, new-master lookup, and lock-copy recovery between nodes.

## Important APIs, Types, And Functions
Exports include `dlm_rcom_status()`, `dlm_rcom_names()`, `dlm_send_rcom_lookup()`, `dlm_send_rcom_lock()`, `dlm_receive_rcom()`, and `dlm_send_ls_not_ready()`. Internal helpers include `create_rcom()`, `create_rcom_stateless()`, `allow_sync_reply()`, `receive_sync_reply()`, `check_rcom_config()`, `receive_rcom_status()`, `receive_rcom_names()`, `receive_rcom_lookup()`, `receive_rcom_lock()`, and `pack_rcom_lock()`.

## Control Flow
Synchronous recovery queries set `LSFL_RCOM_WAIT`, increment `ls_rcom_seq`, clear `ls_recover_buf`, send a request, and wait through `dlm_wait_function()` until `receive_sync_reply()` copies the matching reply into `ls_recover_buf`. Status requests are sent stateless through lowcomms for backward-compatible early version detection; name/lookup/lock recovery messages use midcomms handles.

Status replies include recovery status and configuration (`lvblen`, lockspace flags, slots, generation). The low node gathers per-node slot values; non-low nodes can request the full slot table by setting `DLM_RSF_NEED_SLOTS`. Names requests ask a peer to copy master resource names that hash to this node. Lookup requests ask a directory node to assign/return a new master. Lock requests send process-copy lock details to a new master and receive the new remote id/result.

`dlm_receive_rcom()` gates messages by recovery stop state, recovery sequence, and status-stage ordering. It ignores names/lookup/lock before `DLM_RS_NODES`, and lookup/lock before `DLM_RS_DIR`, then dispatches by RCOM type.

## State And Persistence
State lives in the lockspace: `ls_recover_buf`, `ls_rcom_seq`, `ls_flags` wait/ready bits, recovery status, slots, and generation. RCOM packets are transient but can drive persistent in-memory recovery changes such as new master ids and recovered lock copies.

## Dependencies And Integration Points
RCOM integrates with midcomms/lowcomms, recovery wait helpers, directory recovery, member slot helpers, lock recovery (`dlm_recover_master_reply`, `dlm_recover_master_copy`, `dlm_recover_process_copy`), and errno/config compatibility checks.

## Risks
Recovery depends on strict sequence matching and stage gating. Config mismatches return `-EPROTO`. Timeouts retry status/name calls, so repeated communication failure can delay recovery. Length checks exist for lock messages, but correctness also depends on sender/receiver struct compatibility.

## Test Signals
Test recovery barriers, slot-table exchange, remote lockspace-not-ready replies, config mismatch, stale sequence replies, short lock messages, directory rebuild, new-master lookup, and lock copy reconstruction across node failure.
