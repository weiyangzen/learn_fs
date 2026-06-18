<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-vcp-mailbox.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-vcp-mailbox.h

## Purpose
This header defines the client-visible payload contract for the MediaTek VCP mailbox controller. It is a compact IPC descriptor used between VCP IPC code and the mailbox driver, pairing a shared buffer with mailbox signal metadata.

## Important APIs, types, and functions
`MTK_VCP_MBOX_SLOT_MAX_SIZE` fixes the maximum mailbox slot payload at `0x100` bytes. `struct mtk_ipi_info` carries `msg`, `len`, logical `id`, hardware signal `index`, shared-memory `slot_ofs`, and latched `irq_status`. There are no functions; consumers pass the structure to mailbox send/receive paths.

## Control flow
Client code fills the descriptor with a message buffer, length, identifier, slot offset, and signal index before handing it to the mailbox controller. RX-side code can use `irq_status` to communicate captured interrupt bits back to higher IPC layers.

## State and persistence
The header owns no persistent state. All fields are per-message or per-channel runtime metadata, and `msg` points at externally owned shared memory.

## Dependencies and integration points
It depends on Linux integer types being visible to includers and integrates with the `mtk-vcp-mailbox` driver and VCP IPC users that know the shared-buffer layout.

## Risks and test signals
The key risks are length overruns beyond `MTK_VCP_MBOX_SLOT_MAX_SIZE`, stale or invalid shared-buffer pointers, mismatched `slot_ofs`, and confusion between logical `id` and hardware `index`. Test by sending boundary-size messages, validating RX interrupt status propagation, and exercising multiple signal indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-vcp-mailbox.h -->
