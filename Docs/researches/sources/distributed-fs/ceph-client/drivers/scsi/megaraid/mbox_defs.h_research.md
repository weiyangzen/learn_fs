# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/mbox_defs.h

## Purpose
`mbox_defs.h` is the firmware ABI definition file for mailbox-based MegaRAID controllers. It centralizes firmware opcodes, drive states, cache policies, topology limits, packed command layouts, inquiry/configuration structures, BIOS-private data, and SG descriptors.

## Important APIs, Types, and Constants
Mailbox commands cover logical read/write, passthrough, extended passthrough, adapter inquiry, product/enquiry3 configuration, cache flush, random logical-drive deletion, BIOS queries, channel class, and cluster reservations. Core command types include `mbox_t`, `mbox64_t`, `int_mbox_t`, `mraid_passthru_t`, `mega_passthru64_t`, and `mraid_epassthru_t`.

Firmware information and topology are represented by `mraid_pinfo_t`, `mraid_notify_t`, `mraid_inquiry3_t`, `mraid_adapinfo_t`, `mraid_ldrv_info_t`, `mraid_pdrv_info_t`, `mraid_inquiry_t`, `mraid_extinq_t`, `logdrv_param_t`, `logdrv_40ld_t`, `logdrv_8ld_span8_t`, `logdrv_8ld_span4_t`, `phys_drive_t`, and `disk_array_*` variants. `mbox_sgl64` and `mbox_sgl32` describe DMA SG elements.

## Control Flow, State, Dependencies, and Risks
The header has no execution, but it defines the runtime handshake: write a mailbox, mark busy, ring a doorbell, then read status, poll/ack, and completed command IDs. Inquiry/configuration structures persist as driver snapshots refreshed by explicit firmware commands. It depends only on `linux/types.h` but is consumed by mailbox driver, management ABI, and sysfs logic. Risks are packed ABI drift, 32-bit transfer address limits, fixed old-controller topology sizes, and array bounds. Test signals include successful inquiry, 64-bit read/write, passthrough sense data, LD map retrieval, cluster commands, and cache flush.
