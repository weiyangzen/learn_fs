<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/imr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/imr.h

## Purpose
Intel Isolated Memory Region declarations for firmware/platform memory protection windows. The header is 56 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`

Notable constants/macros: `#define _IMR_H`; `#define IMR_ESRAM_FLUSH BIT(31)`; `#define IMR_CPU_SNOOP BIT(30) /* Applicable only to write */`; `#define IMR_RMU BIT(29)`; `#define IMR_VC1_SAI_ID3 BIT(15)`; `#define IMR_VC1_SAI_ID2 BIT(14)`; `#define IMR_VC1_SAI_ID1 BIT(13)`; `#define IMR_VC1_SAI_ID0 BIT(12)`; `#define IMR_VC0_SAI_ID3 BIT(11)`; `#define IMR_VC0_SAI_ID2 BIT(10)`; `#define IMR_VC0_SAI_ID1 BIT(9)`; `#define IMR_VC0_SAI_ID0 BIT(8)`; `#define IMR_CPU_0 BIT(1) /* SMM mode */`; `#define IMR_CPU BIT(0) /* Non SMM mode */`; `#define IMR_ACCESS_NONE 0`; `#define IMR_READ_ACCESS_ALL 0xBFFFFFFF`; `#define IMR_WRITE_ACCESS_ALL 0xFFFFFFFF`; `#define QUARK_X1000_IMR_MAX 0x08`

Notable declarations and inline helpers: `#define _IMR_H`; `#define IMR_ESRAM_FLUSH BIT(31)`; `#define IMR_CPU_SNOOP BIT(30) /* Applicable only to write */`; `#define IMR_RMU BIT(29)`; `#define IMR_VC1_SAI_ID3 BIT(15)`; `#define IMR_VC1_SAI_ID2 BIT(14)`; `#define IMR_VC1_SAI_ID1 BIT(13)`; `#define IMR_VC1_SAI_ID0 BIT(12)`; `#define IMR_VC0_SAI_ID3 BIT(11)`; `#define IMR_VC0_SAI_ID2 BIT(10)`; `#define IMR_VC0_SAI_ID1 BIT(9)`; `#define IMR_VC0_SAI_ID0 BIT(8)`; `#define IMR_CPU_0 BIT(1) /* SMM mode */`; `#define IMR_CPU BIT(0) /* Non SMM mode */`; `#define IMR_ACCESS_NONE 0`; `#define IMR_READ_ACCESS_ALL 0xBFFFFFFF`; `#define IMR_WRITE_ACCESS_ALL 0xFFFFFFFF`; `#define QUARK_X1000_IMR_MAX 0x08`; `#define QUARK_X1000_IMR_REGBASE 0x40`; `#define IMR_ALIGN 0x400`; `#define IMR_MASK (IMR_ALIGN - 1)`; `int imr_add_range(phys_addr_t base, size_t size,`; `unsigned int rmask, unsigned int wmask);`; `int imr_remove_range(phys_addr_t base, size_t size);`

## Control Flow
The IMR implementation initializes region descriptors and programs hardware registers to protect selected physical memory ranges.

## State and Persistence
State is hardware IMR register configuration and any tracked reserved regions in implementation files.

## Dependencies and Integration Points
Depends on Intel platform support, resource reservations, firmware memory maps, and low-level MMIO/MSR access.

## Risks
Risks include overlapping protected ranges, locking out legitimate kernel/device access, and platform-specific register semantics.

## Test Signals
Tests should run on IMR-capable platforms, validate reserved/protected ranges, boot memory map interactions, and disabled-feature builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/imr.h -->
