<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iosf_mbi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/iosf_mbi.h

## Purpose
Intel IOSF sideband Message Bus Interface API for register reads/writes, P-unit locking, PMIC bus access notifications, and SoC unit/opcode constants. The header is 246 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/notifier.h>`

Notable constants/macros: `#define IOSF_MBI_SYMS_H`; `#define MBI_MCR_OFFSET 0xD0`; `#define MBI_MDR_OFFSET 0xD4`; `#define MBI_MCRX_OFFSET 0xD8`; `#define MBI_RD_MASK 0xFEFFFFFF`; `#define MBI_WR_MASK 0X01000000`; `#define MBI_MASK_HI 0xFFFFFF00`; `#define MBI_MASK_LO 0x000000FF`; `#define MBI_ENABLE 0xF0`; `#define MBI_MMIO_READ 0x00`; `#define MBI_MMIO_WRITE 0x01`; `#define MBI_CFG_READ 0x04`; `#define MBI_CFG_WRITE 0x05`; `#define MBI_CR_READ 0x06`; `#define MBI_CR_WRITE 0x07`; `#define MBI_REG_READ 0x10`; `#define MBI_REG_WRITE 0x11`; `#define MBI_ESRAM_READ 0x12`

Notable declarations and inline helpers: `#define IOSF_MBI_SYMS_H`; `#define MBI_MCR_OFFSET 0xD0`; `#define MBI_MDR_OFFSET 0xD4`; `#define MBI_MCRX_OFFSET 0xD8`; `#define MBI_RD_MASK 0xFEFFFFFF`; `#define MBI_WR_MASK 0X01000000`; `#define MBI_MASK_HI 0xFFFFFF00`; `#define MBI_MASK_LO 0x000000FF`; `#define MBI_ENABLE 0xF0`; `#define MBI_MMIO_READ 0x00`; `#define MBI_MMIO_WRITE 0x01`; `#define MBI_CFG_READ 0x04`; `#define MBI_CFG_WRITE 0x05`; `#define MBI_CR_READ 0x06`; `#define MBI_CR_WRITE 0x07`; `#define MBI_REG_READ 0x10`; `#define MBI_REG_WRITE 0x11`; `#define MBI_ESRAM_READ 0x12`; `#define MBI_ESRAM_WRITE 0x13`; `#define BT_MBI_UNIT_AUNIT 0x00`; `#define BT_MBI_UNIT_SMC 0x01`; `#define BT_MBI_UNIT_CPU 0x02`; `#define BT_MBI_UNIT_BUNIT 0x03`; `#define BT_MBI_UNIT_PMC 0x04`

## Control Flow
Clients call iosf_mbi_read/write/modify with port/opcode/offset; PMIC and P-unit helpers serialize bus access and notify registered blockers around PMIC transactions.

## State and Persistence
State is IOSF hardware registers, P-unit lock ownership, and notifier-chain registration stored in implementation files.

## Dependencies and Integration Points
Depends on notifier chains, Intel SoC platform support, P-unit/PMIC drivers, and sideband PCI/MMIO accessors.

## Risks
Risks include deadlocks around P-unit acquisition, unbalanced PMIC bus blocking, unsupported port/opcode access, and silent -EPROBE_DEFER/-ENODEV behavior in stubs.

## Test Signals
Tests should cover read/write/modify on supported SoCs, notifier registration/unregistration, lock assertion, concurrent PMIC/P-unit users, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iosf_mbi.h -->
