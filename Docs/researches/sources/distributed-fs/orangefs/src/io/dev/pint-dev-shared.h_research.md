# sources/distributed-fs/orangefs/src/io/dev/pint-dev-shared.h

Purpose: defines user/kernel shared constants and ioctl ABI types for the OrangeFS request device.

Important APIs/types: `PVFS_KERNEL_PROTO_VERSION` encodes OrangeFS version for device messages. Buffer-map defaults define descriptor count, descriptor size/shift, total size, and max total size. `LOG2()` validates and computes power-of-two shifts. `PVFS_dev_map_desc` is the ioctl-visible mapping descriptor. Linux-only ioctl numbers include magic, max up/down sizes, mapping, remount, debug, upstream-module, client mask, and client string commands. `dev_mask2_info_t` carries two debug mask words.

State and persistence: no runtime state; this is ABI surface shared with the kernel module, so field layout and ioctl values are persistent compatibility contracts.

Dependencies/integration: includes `ioctl.h` from kernel or user space. `pint-dev.c` uses these constants to negotiate magic/protocol, map shared buffers, push debug masks, and request remounts. Kernel code must agree with the struct layout, especially for 32-bit compatibility notes.

Risks: ABI changes break kernel/user interoperability. `PVFS2_BUFMAP_MAX_TOTAL_SIZE` is exclusive in `pint-dev.c` (`>=` rejected), while comments call it a maximum. `LOG2()` returns `-1` for non-power-of-two values and must be checked by callers. Test signals include ioctl compatibility tests, 32-bit compat mapping, power-of-two descriptor sizes, and version mismatch handling.
