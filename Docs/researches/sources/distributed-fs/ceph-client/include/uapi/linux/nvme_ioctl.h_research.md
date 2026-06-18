# sources/distributed-fs/ceph-client/include/uapi/linux/nvme_ioctl.h

Purpose: Defines the userspace ioctl and io_uring command ABI for NVM Express namespace, controller, admin, and passthrough operations.

Important APIs/types/functions: Exports `struct nvme_user_io`, `struct nvme_passthru_cmd`, `struct nvme_passthru_cmd64`, `struct nvme_uring_cmd`, `nvme_admin_cmd`, and ioctl numbers `NVME_IOCTL_ID`, `NVME_IOCTL_ADMIN_CMD`, `NVME_IOCTL_SUBMIT_IO`, `NVME_IOCTL_IO_CMD`, reset/rescan ioctls, 64-bit passthrough ioctls, vectored IO variants, and `NVME_URING_CMD_*` async commands.

Control flow: Userspace opens an NVMe character or block device and either submits structured namespace I/O through `nvme_user_io`, sends arbitrary admin or I/O command dwords via passthrough structures, or issues async io_uring commands. The kernel translates the ABI structure to NVMe SQEs, DMA maps data and metadata buffers, waits or completes asynchronously, and returns command result fields.

State and persistence behavior: The header carries transient command parameters, user buffer addresses, data lengths, metadata pointers, timeouts, namespace IDs, and completion results. Durable state changes may occur on the device for admin commands, format, firmware, namespace management, reset, or writes, but the header itself owns no state.

Dependencies and integration points: Depends on `<linux/types.h>`. Integrates with nvme-cli, libnvme, io_uring, block devices, controller char devices, and kernel NVMe core passthrough validation.

Risks: Raw passthrough exposes powerful device operations; capability checks, namespace/controller targeting, buffer length validation, metadata handling, and 32/64-bit layout compatibility are critical. Vectored commands overload `data_len` with `vec_cnt`, so callers and kernel paths must select the correct ioctl.

Test signals: Run nvme-cli identify/get-log/admin passthrough, read/write namespace I/O, invalid opcode and timeout cases, 64-bit result propagation, vectored io_uring commands, reset/rescan behavior, and compat userspace structure tests.
