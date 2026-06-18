<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/byteorder.h

## Purpose
Declares OpenRISC userspace byte order as big endian.

## Important APIs, Types, And Functions
Includes `linux/byteorder/big_endian.h`.

## Control Flow
No control flow; it is a compile-time UAPI selection.

## State And Persistence
No state.

## Dependencies And Integration Points
Consumed by exported headers and userspace code compiling against OpenRISC ABI.

## Risks
This is an ABI statement. Changing it would break structure layout, ELF data expectations, networking conversions, and userspace compatibility.

## Test Signals
Headers-install builds and userspace endian macro checks for OpenRISC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/byteorder.h -->
