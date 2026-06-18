# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_dev.c

## Purpose
`card_dev.c` implements the GenWQE character device. It tracks open files, mmap-created coherent DMA buffers, pinned user pages, DDCB address fixups, flash update/read commands, ioctl register access, async notification, and device-node creation/removal.

## Important APIs, Types, and Functions
The file operations are `genwqe_open()`, `genwqe_release()`, `genwqe_fasync()`, `genwqe_mmap()`, and `genwqe_ioctl()`. Public device lifecycle functions are `genwqe_device_create()` and `genwqe_device_remove()`. Important helpers include mapping/pinning functions `genwqe_search_pin()`, `__genwqe_search_mapping()`, `genwqe_pin_mem()`, `genwqe_unpin_mem()`, `genwqe_remove_mappings()`, `genwqe_remove_pinnings()`, DDCB fixup helpers `ddcb_cmd_fixups()` and `ddcb_cmd_cleanup()`, command dispatch `genwqe_execute_ddcb()`/`do_execute_ddcb()`, and flash helpers `do_flash_update()`/`do_flash_read()`.

## Control Flow
Open allocates a per-file `genwqe_file`, initializes raw-mapping and pinned-memory lists, records the opener PID, and stores it in `filp->private_data`. `mmap()` allocates coherent DMA memory, maps it into user space, records the user/kernel/DMA tuple, and frees it from `genwqe_vma_close()`. DDCB ioctls copy a command from user space, optionally replace ASIV user addresses with DMA addresses or generated SGL pointers, execute the raw DDCB through `card_ddcb.c`, clean temporary mappings, and copy result fields back. Flash update/read chunk user buffers into 256 KiB coherent buffers and send `SLCMD_MOVE_FLASH` DDCBs. Device removal first signals async users, escalates to SIGKILL if descriptors remain, then refuses to continue if the cdev still has unexpected references.

## State and Persistence
Per-open state contains raw DMA mappings, pinned mappings, async queue, opener PID, and client pointer. Kernel state persists only while the device/file is open; flash operations persist data on the accelerator card. The driver writes a DMA address into the first bytes of mmap memory for `CAP_SYS_ADMIN` users when the allocation is larger than a DMA address.

## Dependencies and Integration Points
This file bridges user ABI definitions from `linux/genwqe/genwqe_card.h`, GenWQE DDCB execution, DMA/SGL helpers from `card_utils.c`, sysfs groups from `card_sysfs.c`, debugfs setup, cdev/device core, PCI state, and capabilities checks.

## Risks and Edge Cases
The user ABI allows raw register writes and raw DDCBs to privileged callers, so capability and read-only checks matter. Mapping lookups use user virtual address ranges and must handle overflow and partial ranges correctly. Temporary SGL mappings are cleaned after execution, while explicit pins survive until unpinned or file close. `genwqe_device_remove()` panics on unexpected references, which is severe during hot-unplug or stuck user processes. Flash size and page alignment restrictions are strict, and older SLU versions follow different ASIV layouts.

## Test Signals
Exercise all ioctls for success and permission failures, mmap/unmap cleanup, pin/unpin including killed processes, DDCB flat and SGL ATS fixups, raw DDCB privileged-only behavior, flash read/update errors, PCI offline `-EIO`, nonblocking queue busy paths, and device removal with open descriptors.
