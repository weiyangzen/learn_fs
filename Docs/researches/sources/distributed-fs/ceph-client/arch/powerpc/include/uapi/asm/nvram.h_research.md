<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/nvram.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/nvram.h

Purpose: Defines PowerPC NVRAM partition signatures, PowerMac XPRAM identifiers, location structure, and `/dev/nvram` ioctls.

Important APIs/types/functions: `NVRAM_SIG_*`, `pmac_nvram_*` enum values, XPRAM offsets, `struct pmac_machine_location`, obsolete and current NVRAM ioctl numbers.

Control flow: Userspace tools identify partitions and issue ioctls to discover partition offsets or request NVRAM sync.

State and persistence: NVRAM contents persist across reboots; structures describe firmware/PowerMac state.

Dependencies and integration points: Depends on PowerPC ioctl encoding and nvram driver implementation.

Risks: Partition signatures and ioctl numbers are ABI. Writing wrong offsets can corrupt firmware environment or panic logs.

Test signals: NVRAM tool compile tests, ioctl smoke tests on PowerMac/PowerNV where available, and partition parsing validation.

Source read size: 63 lines, 2077 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/nvram.h -->
