# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_hw_mbox.c

## Purpose
Implements HINIC function-to-function mailbox transport used for VF-to-PF management proxying, PF-to-VF commands, mailbox responses, random-id validation for VF messages, and PF-side validation of common VF commands before forwarding to management firmware.

## Important APIs, Types, and Functions
Public APIs include callback registration/unregistration, `hinic_mbox_to_pf`, `hinic_mbox_to_vf`, `hinic_mbox_to_func`, `hinic_func_to_func_init/free`, `hinic_vf_mbox_random_id_init`, `hinic_mbox_check_func_id_8B`, and `hinic_mbox_check_cmd_valid`. Internal transport helpers include `recv_mbox_handler`, `send_mbox_to_func`, `send_mbox_seg`, `wait_for_mbox_seg_completion`, `resp_mbox_handler`, `recv_func_mbox_handler`, `response_for_recv_func_mbox`, and random-id helpers.

## Control Flow
Initialization allocates per-function receive and response buffers for up to 512 functions, allocates a coherent mailbox writeback status area, points the send mailbox at the CSR mailbox data area, registers AEQ callbacks for mailbox receive and send-result events, and registers a PF common mailbox callback for non-VF functions. Sending serializes under mailbox semaphores, segments messages into 48-byte chunks, writes header and segment data to mailbox CSRs, triggers the target AEQ, waits for writeback status, then waits for a response completion if ACK is requested. Receive AEQ handling validates source id and optional VF random id, reassembles segments by sequence id, dispatches responses to waiters or queues direct-send work, invokes PF/VF callbacks, and sends response mailboxes when requested.

## State and Persistence Behavior
State is in `hinic_mbox_func_to_func`: send/response semaphores, send mailbox CSR/writeback state, workqueue, per-function send/response assembly buffers, callback tables and bit states, send message id, event flag, mailbox lock, and VF random-id arrays. Hardware-visible state includes mailbox data CSRs, control/int registers, writeback status DMA address, AEQ delivery, and firmware-provisioned VF random ids.

## Dependencies and Integration Points
Depends on HWIF CSR access, AEQ callbacks, management messages, random number generation, workqueues, completions, and semaphores. `hinic_hw_mgmt.c` routes VF management requests through this file; PF handling forwards validated VF common commands to management firmware.

## Risks
Mailbox segmentation is concurrency-sensitive: sequence, length, message id, event flag, and response buffers must match under concurrent traffic. `hinic_func_to_func_free` always unregisters the PF common callback, so VF paths rely on callback state being harmless when not registered. Random-id checking reads from a fixed offset in the mailbox buffer and queues refresh work on mismatch. PF validation must reject forged function ids, invalid queue depths, invalid command queue contexts, and unsupported commands; gaps become VF isolation risks.

## Test Signals
VF-to-PF management commands, PF-to-VF commands, multi-segment messages, response timeout, mailbox writeback error codes, send-result AEQs, source function id mismatch, random-id unsupported/supported paths, random-id mismatch refresh, unsupported VF command rejection, FLR command handling, and teardown with queued mailbox work are key signals.
