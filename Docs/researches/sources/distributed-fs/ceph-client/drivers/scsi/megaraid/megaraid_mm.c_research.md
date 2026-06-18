# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.c

## Purpose
`megaraid_mm.c` implements the LSI MegaRAID common management module. It registers `/dev/megadev0`, gates access to privileged users, translates legacy MIMD ioctl packets into `uioc_t`, allocates DMA-safe buffers, dispatches commands to registered low-level drivers, waits for completion or timeout, converts results back to userspace, and exports adapter registration helpers.

## Important APIs and Functions
The misc-device surface is `mraid_mm_open`, `mraid_mm_unlocked_ioctl`, and internal `mraid_mm_ioctl`. Local driver commands are handled by `handle_drvrcmd`. Adapter lookup and packet conversion use `mraid_mm_get_adapter`, `mimd_to_kioc`, and `kioc_to_mimd`. Dispatch and completion use `lld_ioctl`, `ioctl_done`, and `lld_timedout`. Resource management uses `mraid_mm_alloc_kioc`, `mraid_mm_dealloc_kioc`, `mraid_mm_attach_buf`, DMA pool setup/teardown, and adapter resource free. Exported APIs are `mraid_mm_register_adp`, `mraid_mm_unregister_adp`, and `mraid_mm_adapter_app_handle`.

## Control Flow and State
Open requires `CAP_SYS_ADMIN`. Ioctl entry validates command type, detects the extended signature, rejects the newer packet format, handles version/adapter count locally, or routes adapter-info/mailbox commands to a low-level driver. Legacy opcodes `0x80` and `0x81` drive transfer length and direction, attach a DMA buffer, copy user write data, translate mailbox state into `mbox64_t`, and handle 32-bit passthrough. `lld_ioctl` calls the low-level `issue_uioc`, arms a timeout timer when configured, waits until status changes from `-ENODATA`, and marks the management adapter unavailable on timeout.

Global state includes `adapters_list_g`, `adapters_count_g`, `wait_q`, and `drvr_ver`. Per registered adapter state includes kioc pool, mailbox array, passthrough DMA pool, five data DMA pools from 4 KiB to 64 KiB, a semaphore limiting concurrent ioctl packets, and a `quiescent` field where nonzero means the common management module can issue commands.

## Dependencies, Integration Points, Risks, and Test Signals
Dependencies include miscdevice, user-copy, DMA pools, timers, wait queues, semaphores, locks, PCI references, and local MegaRAID ABI headers. Low-level drivers register through `mraid_mm_register_adp`; userspace uses the legacy `/dev/megadev0` ABI and adapter handles.

Risks include legacy pointer compatibility, rejection of newer `uioc_t` applications, list-order adapter numbering, full-length data copyback, late completion after timeout, and resource retention if low-level callbacks never return. Test signals include device registration, non-admin denial, version/count/info ioctls, `0x80` and `0x81` mailbox commands, passthrough SCSI status, DMA pool selection, semaphore blocking, timeout marking offline, late timeout cleanup, and unregister with no pending commands.
