# sources/distributed-fs/ceph-client/drivers/scsi/megaraid.h

## Purpose
This header is the private interface for the older MegaRAID SCSI driver path outside the `megaraid/` subdirectory. It defines firmware mailbox layouts, passthrough packets, scatter-gather elements, adapter soft state, command state flags, I/O port helpers, ioctl structures, and forward declarations for the legacy driver's implementation.

## Important APIs, Types, and Constants
Firmware-facing layouts include `struct mbox_out`, `struct mbox_in`, `mbox_t`, `mbox64_t`, `mega_passthru`, `mega_ext_passthru`, `mega_sglist`, and `mega_sgl64`. `scb_t` is the legacy command object with mailbox, DMA, SCSI command, SG, passthrough, and state ownership fields. `adapter_t` is the per-controller state with PCI/MMIO handles, aligned mailbox memory, command lists, SCSI host pointer, inquiry data, logical-drive metadata, internal-command synchronization, and clustering support.

The ioctl ABI is represented by `struct uioctl_t`, `nitioctl_t`, `megacmd_t`, `megastat_t`, and `struct mcontroller`. Declared implementation hooks include queue/build functions, interrupt handlers, abort/reset handlers, passthrough builders, random logical-drive deletion helpers, and internal firmware command helpers.

## Control Flow, State, Dependencies, and Risks
The expected runtime path is probe/init, mailbox setup, SCB pool initialization, firmware query, SCSI host registration, SCSI command translation, pending/issued/completed SCB movement, DMA unmap, and SCSI completion. State is guarded by adapter locks, command lists, internal command mutex/completion, and flags such as `IN_ABORT`, `IN_RESET`, `BOARD_MEMMAP`, `BOARD_IOMAP`, `BOARD_40LD`, and `BOARD_64BIT`.

Dependencies are Linux SCSI, PCI, DMA, procfs, user-copy, spinlock, mutex, and low-level port I/O APIs. Risks include packed firmware ABI drift, 32-bit versus 64-bit ioctl pointer compatibility, SCB ownership races, 64-bit DMA handling, and private ioctl bounds validation. Test signals include legacy driver build/probe, read/write I/O, passthrough commands, adapter info ioctls, interrupt completion, abort/reset recovery, and 64-bit DMA paths.
