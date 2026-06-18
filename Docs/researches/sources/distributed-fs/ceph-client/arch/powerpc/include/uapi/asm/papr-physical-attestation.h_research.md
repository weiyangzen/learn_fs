<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-physical-attestation.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-physical-attestation.h

Purpose: Defines the PAPR physical attestation command ioctl payload.

Important APIs/types/functions: `PAPR_PHYATTEST_MAX_INPUT`, `struct papr_phy_attest_io_block`, and `PAPR_PHY_ATTEST_IOC_HANDLE`.

Control flow: Userspace passes a versioned attestation command, TCG version, big-endian length/correlator, and payload; ioctl returns a handle for the attestation exchange.

State and persistence: Attestation state is firmware/driver-managed; the block carries command input and correlator state.

Dependencies and integration points: Depends on PAPR miscdev ioctl ID, PowerPC ioctl encoding, Linux types, and PAPR 2.13 attestation structures.

Risks: Maximum input is sized to 4K minus header; length endianness and bounds must be validated. Payload format is security-sensitive.

Test signals: Attestation ioctl size/bounds tests, firmware error mapping tests, and userspace structure layout checks.

Source read size: 31 lines, 854 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/papr-physical-attestation.h -->
