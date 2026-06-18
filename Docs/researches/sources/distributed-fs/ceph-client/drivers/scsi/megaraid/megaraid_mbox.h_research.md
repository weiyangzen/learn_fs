# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mbox.h

## Purpose
`megaraid_mbox.h` is the mailbox driver's private header. It defines driver versions, supported PCI IDs, command limits, timeout defaults, the driver-specific mailbox CCB, the mailbox-controller soft state, doorbell helpers, and bridge macros used by `megaraid_mbox.c`.

## Important APIs, Types, and Constants
Constants include `MEGARAID_VERSION`, controller PCI IDs, `MBOX_MAX_SCSI_CMDS`, `MBOX_MAX_USER_CMDS`, default command/SG/sector limits, reset and sync waits, busy-wait settings, and internal buffer size. `mbox_ccb_t` stores raw mailbox pointers, 32-bit and 64-bit mailbox views, mailbox DMA address, SG lists, passthrough objects, and DMA handles. `mraid_device_t` stores aligned shared mailbox memory, mailbox lock, BAR state, DMA pools, kernel and user CCB arrays, management mailboxes, physical drive states, display flags, `hw_error`, `fast_load`, channel class, sysfs resources, random-delete flag, and current LD map.

## Control Flow, State, Dependencies, and Risks
The header defines state consumed by the C file: initialization populates DMA pools and aligned mailbox pointers; command issue copies per-command mailboxes into the shared mailbox and rings doorbells; sysfs reads reuse one mutex-protected command buffer. It depends on `mega_common.h`, `mbox_defs.h`, and `megaraid_ioctl.h`. Risks include fixed-size command arrays, command ID separation between kernel and user SCBs, firmware-required mailbox alignment, hard-coded doorbell offsets, and resource cleanup on partial init. Test signals include no alignment warnings, successful pool allocation/free, correct user command IDs, sysfs serialization, doorbell completion, and clean rollback on probe failure.
