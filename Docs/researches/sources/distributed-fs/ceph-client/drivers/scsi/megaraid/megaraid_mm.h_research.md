# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/megaraid_mm.h

## Purpose
`megaraid_mm.h` is the private header for the common management module. It includes kernel/local ABI headers, defines module version strings and debug binding, declares the initial DMA buffer size, and defines `mimd_t`, the deprecated legacy ioctl packet consumed by `megaraid_mm.c`.

## Important APIs, Types, and Constants
`LSI_COMMON_MOD_VERSION` and `LSI_COMMON_MOD_EXT_VERSION` are printed at module load. `LSI_DBGLVL` maps shared logging to `dbglevel`. `MRAID_MM_INIT_BUFF_SIZE` sets the first DMA pool to 4096 bytes. `mimd_t` carries `inlen`, `outlen`, opcode/subopcode/adapter/buffer/length fields, an 18-byte mailbox image, embedded `mraid_passthru_t`, and a user data pointer, with conditional 32-bit/64-bit pointer padding.

## Control Flow, State, Dependencies, and Risks
The header has no execution, but every supported management ioctl starts as `mimd_t`. The implementation copies it from userspace, classifies local versus firmware commands, converts it into `uioc_t` plus DMA buffers, then copies status/data back. Dependencies are Linux spinlock, fs, uaccess, module, PCI, list, miscdevice, `mbox_defs.h`, and `megaraid_ioctl.h`. Risks are packed legacy pointer layout, compat ioctl behavior, newer packet rejection, and structure-size drift. Test signals include 32-bit and 64-bit builds, old MIMD adapter queries, mailbox commands, direction from `inlen`/`outlen`, and userspace tool compatibility.
