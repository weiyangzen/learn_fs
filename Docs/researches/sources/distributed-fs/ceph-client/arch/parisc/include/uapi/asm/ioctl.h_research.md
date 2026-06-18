<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctl.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctl.h

Source read size: 45 lines, 1710 bytes.

Purpose: defines PA-RISC ioctl command encoding direction bits and includes generic ioctl helpers. Important APIs: `_IOC_NONE`, `_IOC_WRITE`, `_IOC_READ`, and generic `_IOC` macros. Control flow: ioctl numbers encode command, size, and access direction; kernel ioctl handlers and compat layers decode them. State and persistence: ioctl numbers are permanent userspace ABI. Dependencies and integration points: tty, serial, block, network, and driver UAPI headers. Risks: PA-RISC direction-bit ordering differs from common expectations; wrong encoding causes compat failures or user-buffer size mismatches. Test signals: ioctl-number compile tests, tty ioctl tests, strace decode, and 32/64-bit compat ioctl smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/ioctl.h -->
