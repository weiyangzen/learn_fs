<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/byteorder.h

Purpose: Selects little-endian byte order definitions for RISC-V UAPI.

Important APIs/types/functions: Includes Linux little-endian byteorder helpers.

Control flow: Compile-time only.

State and persistence: No state.

Dependencies and integration points: Used by exported structs/protocols that need endian annotations.

Risks: Wrong byteorder breaks all userspace ABI interpretation.

Test signals: headers_install and endian conversion build tests.

Source read size: 12 lines, 327 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/byteorder.h -->
