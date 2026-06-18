<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ecc.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/ecc.h

## Purpose
This header defines sun4m external cache/memory-controller ECC register offsets and bit fields.

## Important APIs, Types, and Functions
It defines ECC register offsets (`ECC_ENABLE`, `ECC_FSTATUS`, `ECC_FADDR`, `ECC_DIGNOSTIC`, `ECC_MBAENAB`, `ECC_DMESG`) and masks for MBus arbiter enable, fault control, fault address, and fault status fields.

## Control Flow
ECC handling code reads status/address registers after memory errors, decodes syndrome/type/address fields, and enables checking/interrupts through control bits.

## State and Persistence Behavior
State is in the ECC controller registers. Fault bits persist until cleared by controller-specific handling.

## Dependencies and Integration Points
It integrates with SPARC32 sun4m memory error handling, SRMMU passthrough ASI access, and platform diagnostics.

## Risks
Wrong decoding can misreport faulting CPUs/addresses or mishandle correctable versus uncorrectable errors.

## Test Signals
Use platform error injection/logs where available, verify syndrome/address decode, and boot with ECC interrupt handling enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/ecc.h -->
