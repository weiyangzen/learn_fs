<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/amd_hsmp.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/amd_hsmp.h

Purpose: Defines the AMD Host System Management Port userspace ABI: message IDs, message descriptors, metrics table layout, protocol versions, and the ioctl used to exchange HSMP commands with the kernel driver.

Important APIs/types/functions: `HSMP_MAX_MSG_LEN`, `enum hsmp_message_ids`, `struct hsmp_message`, `enum hsmp_msg_type`, `enum hsmp_proto_versions`, `struct hsmp_msg_desc`, `hsmp_msg_desc_table`, `struct hsmp_metric_table`, `HSMP_BASE_IOCTL_NR`, and `HSMP_IOCTL_CMD`.

Control flow: Userspace fills `struct hsmp_message` with a socket index, message ID, argument count, expected response size, and up to eight arguments, then issues `HSMP_IOCTL_CMD`. Kernel driver validation can use the descriptor table to check supported GET/SET/SET_GET command shape before forwarding to platform firmware/SMU.

State and persistence behavior: No kernel state is owned by the header. The ABI conveys mutable platform state such as power limits, boost limits, link widths, P-states, telemetry counters, RAPL counters, and metrics table contents.

Dependencies and integration points: Depends on Linux UAPI integer and ioctl types. Integrates with AMD server firmware, the HSMP character device driver, telemetry agents, power-management tooling, and platform-specific PPR message definitions.

Risks and test signals: Risks include ioctl layout drift due to packing, mismatched descriptor counts, firmware protocol-version differences, and command IDs that are unsupported on a given family/model. Test ioctl round trips on supported AMD systems, descriptor validation for each message, 32-bit userspace compatibility, metrics table size/offset checks, and unsupported-message `-ENOMSG` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/amd_hsmp.h -->
