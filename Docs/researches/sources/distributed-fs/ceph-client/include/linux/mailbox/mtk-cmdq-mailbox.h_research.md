<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-cmdq-mailbox.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-cmdq-mailbox.h

## Purpose
This header defines the MediaTek Command Queue mailbox client interface. It describes command packet layout, event/wait encodings, callback data, and helpers for extracting mailbox-private address-shift data.

## Important APIs, Types, and Functions
Constants include instruction size, subsystem shift, opcode shift, jump pass, WFE option bits, and `CMDQ_MAX_EVENT`. `enum cmdq_code` lists command opcodes. `struct cmdq_cb_data` carries completion status and packet data. `struct cmdq_mbox_priv` exposes thread and physical-address shift metadata. `struct cmdq_pkt` holds the command buffer, buffer size, command count, mailbox client, and completion callback. APIs include `cmdq_get_mbox_priv` and `cmdq_get_shift_pa`.

## Control Flow
Clients build a `cmdq_pkt` as a sequence of 64-bit instructions, submit it through a mailbox channel, and receive callback data on completion. Wait-for-event instructions use the WFE bit encodings and event IDs.

## State and Persistence Behavior
Packet buffers and callbacks are caller-managed runtime state. Hardware queue state and events live in the CMDQ controller; no persistence is provided.

## Dependencies and Integration Points
It depends on platform devices, slab/types, and mailbox channel structures. It integrates with MediaTek display, multimedia, and SoC drivers that offload register programming to CMDQ hardware.

## Risks and Test Signals
Risks include malformed instruction encoding, insufficient packet buffer sizing, wrong physical-address shift, event ID overflow, and callback lifetime bugs. Test signals are CMDQ packet submission tests, hardware completion interrupts, timeout/error status checks, and display/media pipeline smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-cmdq-mailbox.h -->
