<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mce.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mce.h

Purpose: Defines the userspace-visible machine-check event record and ioctls for querying mcelog record and buffer properties.

Important APIs/types/functions: `struct mce`, `MCE_GET_RECORD_LEN`, `MCE_GET_LOG_LEN`, and `MCE_GETCLEAR_FLAGS`.

Control flow: Kernel machine-check handlers fill records; userspace reads them and uses ioctls to determine record length, log length, and clear flags. Fields must remain stable for mcelog and other consumers.

State and persistence behavior: `struct mce` instances persist in kernel logs/ring buffers and userspace crash telemetry. Header comments explicitly require adding shared fields only at the end and avoiding vendor-specific field insertion.

Dependencies and integration points: Depends on Linux UAPI types and ioctl. Integrates with x86 MCE handling, EDAC/rasdaemon/mcelog, SMCA, protected processor inventory, microcode reporting, and APEI/MCE reporting paths.

Risks and test signals: Risks include structure offset changes, vendor-specific ABI pollution, missing SMCA field handling, and 32-bit consumers misreading 64-bit fields. Test mcelog/rasdaemon ingestion, MCE injection, SMCA systems, ioctl record-length checks, and ABI offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mce.h -->
