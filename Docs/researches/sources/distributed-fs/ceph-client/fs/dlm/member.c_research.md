# sources/distributed-fs/ceph-client/fs/dlm/member.c

## Purpose
`member.c` maintains lockspace membership, slot assignment, membership-related lockspace stop/start transitions, and callbacks to lockspace users during recovery. It is the bridge between configfs membership snapshots and DLM internal member lists.

## Important APIs, Types, And Functions
Important exports include `dlm_recover_members()`, `dlm_ls_stop()`, `dlm_ls_start()`, `dlm_clear_members()`, `dlm_clear_members_gone()`, `dlm_is_member()`, `dlm_is_removed()`, `dlm_slots_assign()`, `dlm_slots_copy_in()`, `dlm_slots_copy_out()`, `dlm_slot_save()`, `dlm_slots_version()`, and `dlm_lsop_recover_done()`.

The file uses `struct dlm_member`, `struct dlm_config_node`, `struct dlm_slot`, `rcom_config`, and `rcom_slot` structures. Membership lists live in `ls->ls_nodes` and `ls->ls_nodes_gone`.

## Control Flow
During recovery, `dlm_recover_members()` first counts prior gone members as negative changes, moves departed or re-added members from `ls_nodes` to `ls_nodes_gone`, notifies midcomms and lockspace ops of removals, adds new members from the config snapshot, recomputes the low node id and weighted node array, and pings members with `dlm_rcom_status()`.

Slot flow is led by the lowest node. It collects slot/generation data via status rcoms, runs `dlm_slots_assign()` to retain previous slots and allocate free offsets for new members, then distributes the sparse slot table through rcom status replies. Non-low nodes call `dlm_slots_copy_in()` to copy the low node's slot map.

`dlm_ls_stop()` stops normal receive processing, sets recovery-stop and locking-stopped flags, increments the recovery sequence, activates the requestqueue, waits for recovery lock acquisition when needed, suspends/resumes recoverd, clears old slot state, and invokes `recover_prep` once per stop. `dlm_ls_start()` obtains a new config snapshot, verifies the lockspace is stopped, installs a `dlm_recover` argument, and wakes recoverd.

## State And Persistence
Membership state is in lockspace lists, member slot fields, `ls_num_nodes`, `ls_low_nodeid`, `ls_node_array`, `ls_slots`, `ls_generation`, and recovery arguments. It persists while the lockspace lives and is regenerated on membership changes. Slot generation increases across successful slot assignment.

## Dependencies And Integration Points
This file integrates with `config.c` for node snapshots and communication sequence numbers, lowcomms/midcomms for connecting and member add/remove notifications, rcom for status pings, recoverd for stop/start synchronization, and lockspace ops (`recover_prep`, `recover_slot`, `recover_done`) used by filesystems.

## Risks
Incorrect membership transitions can leave midcomms user counts wrong or skip filesystem recovery callbacks. Slot assignment must preserve existing slots; slot changes are treated as errors. `dlm_ls_stop()` depends on precise lock ordering across recv, recover, requestqueue, and in-recovery locks.

## Test Signals
Test member add, remove, remove/re-add with changed `comm_seq`, slot assignment across mixed generations, low-node and non-low-node slot paths, and stop/start races with incoming messages. GFS2 mount/umount and node-failure tests should show recover_slot/recover_done callbacks in expected order.
