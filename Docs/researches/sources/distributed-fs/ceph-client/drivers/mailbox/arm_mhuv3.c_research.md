<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv3.c -->
# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv3.c

## Purpose
`arm_mhuv3.c` implements the ARM Message Handling Unit v3 mailbox controller. It discovers whether the mapped frame is a PBX sender or MBX receiver, validates the architectural revision, discovers supported extensions, and currently exposes the Doorbell Extension (DBE) as Linux mailbox channels.

## Important APIs, Types, and Functions
The main private types are `struct mhuv3`, `struct mhuv3_extension`, `struct mhuv3_mbox_chan_priv`, and `struct mhuv3_protocol_ops`. Register layouts are represented with packed structs for the control page and PBX/MBX doorbell channel windows. Core entry points are `mhuv3_probe()`, `mhuv3_frame_init()`, `mhuv3_irqs_init()`, `mhuv3_initialize_channels()`, and `mhuv3_mbox_of_xlate()`. Doorbell behavior is implemented by `mhuv3_doorbell_send_data()`, `mhuv3_doorbell_last_tx_done()`, startup/shutdown helpers, and the combined IRQ lookup helpers.

## Control Flow
Probe maps the MMIO resource, reads `blk_id` to select PBX or MBX mode, verifies the MHU major version, optionally requests AutoOp full mode, initializes supported extensions, sets IRQ behavior, allocates mailbox channels, and registers the controller. DBE initialization creates one Linux channel for every hardware doorbell bit in every DB channel window. PBX frames send by setting a doorbell bit, then either poll or receive a combined transfer-ack interrupt. MBX frames require a combined IRQ, inspect combined DBCH status, deliver optional data, call `mbox_chan_received_data()`, and clear the doorbell to acknowledge.

## State and Persistence
State is devm-managed and lasts for the platform-device lifetime. `pending_db[]` tracks in-flight PBX doorbells and is protected by `pending_lock`; it is cleared on TX shutdown and when completions are observed. AutoOp full mode is undone by a devm cleanup action that clears `op_req`. There is no persistent storage across probe/remove.

## Dependencies and Integration Points
The driver integrates with platform devices, OF mailbox specifiers with three cells `(extension type, channel window, parameter)`, MMIO register access, Linux mailbox core, IRQ handling, spinlocks, and ARM MHUv3 hardware. It only implements DBE; FCE and FE support is detected but logged as unsupported by this driver.

## Risks and Edge Cases
The channel count can grow to `num_dbch * 32`, so DT specifier validation and channel allocation must stay consistent. PBX operation without a combined IRQ relies on polling and accurate `last_tx_done()`. MBX operation fails probe if the combined IRQ is missing. The source contains duplicated local declarations/comments in a few places, which should be caught by compile coverage. Interrupt lookup reports spurious status when pending doorbell state and hardware status disagree.

## Test Signals
Useful signals include OF probing for `arm,mhuv3`, compile coverage for packed register access, successful PBX polling and IRQ modes, MBX combined IRQ delivery, `mbox_chan_txdone()` on TX ack, `mbox_chan_received_data()` on RX doorbells, bad phandle-cell rejection, and suspend/remove cleanup that clears AutoOp state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhuv3.c -->
