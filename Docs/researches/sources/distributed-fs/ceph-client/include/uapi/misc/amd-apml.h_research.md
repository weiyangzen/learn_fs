<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/amd-apml.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/amd-apml.h

Purpose: defines AMD APML sideband userspace ioctls and message payloads for mailbox, CPUID, MCA/MSR, and register-transfer protocols.

Important APIs and types: `struct apml_mbox_msg` carries mailbox command, data word, and firmware return code. `apml_cpuid_msg` and `apml_mcamsr_msg` carry packed 64-bit request/response values plus status. `apml_reg_xfer_msg` carries register address, byte data, and read/write flag. Ioctls under `SB_BASE_IOCTL_NR` are `SBRMI_IOCTL_MBOX_CMD`, `CPUID_CMD`, `MCAMSR_CMD`, and `REG_XFER_CMD`.

Control flow, state, and persistence: userspace sends ioctl messages to the APML/SBRMI device; firmware/hardware returns data and soft error codes. Register writes may alter platform state depending on address.

Dependencies and integration points: integrates AMD sideband management drivers, platform firmware, monitoring tools, and RMI/SBI mailbox protocols.

Risks and test signals: risks include packed bitfield interpretation in 64-bit messages, firmware error translation, register access authorization, and ioctl number compatibility. Test valid and invalid commands, per-thread CPUID/MSR reads, register read/write, and firmware soft-error returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/amd-apml.h -->
