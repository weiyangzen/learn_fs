# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_ioctl.h

## Purpose
`megaraid_ioctl.h` defines the user and low-level-driver ABI for the MegaRAID common management module. It provides debug levels, ioctl command numbers, packet format constants, management opcodes, the aligned `uioc_t` command packet, HBA information structures, DMA-pool metadata, and exported adapter registration APIs.

## Important APIs, Types, and Constants
The external ioctl command is `MEGAIOCCMD`. Important management opcodes include `MBOX_CMD`, `GET_DRIVER_VER`, `GET_N_ADAP`, `GET_ADAP_INFO`, `GET_CAP`, `GET_STATS`, and `GET_IOCTL_VERSION`. Packet/action constants include `EXT_IOCTL_SIGN`, `MBOX_LEGACY`, `MBOX_HPE`, `APPTYPE_MIMD`, `APPTYPE_UIOC`, `IOCTL_ISSUE`, and `IOCTL_ABORT`.

`uioc_t` is the normalized kernel management packet, containing user-visible command metadata plus kernel-only user pointers, passthrough DMA state, callback, attached DMA buffer, pool index, and timeout marker. `mraid_hba_info_t` is a packed 256-byte HBA response, `mcontroller_t` is the older app-facing adapter info, `mm_dmapool_t` describes per-adapter DMA pools, and `mraid_mmadp_t` is the low-level driver registration object. Exported APIs are `mraid_mm_register_adp`, `mraid_mm_unregister_adp`, and `mraid_mm_adapter_app_handle`.

## Control Flow, State, Dependencies, and Risks
Userspace packets enter the common management module, become `uioc_t`, receive DMA buffers, are sent through `mraid_mmadp_t.issue_uioc`, and complete through `uioc_t.done`. The header depends on Linux type/semaphore/timer APIs and `mbox_defs.h`; it integrates `megaraid_mm.c` with `megaraid_mbox.c`. Risks are ABI alignment, packed 32-bit/64-bit compatibility, retained user pointers, late completion after timeout, and drift between the defined newer packet format and the implementation that accepts only legacy MIMD. Test signals include adapter info/version/count ioctls, mailbox commands, passthrough SCSI status copyback, timeout handling, and sysfs app-handle matching.
