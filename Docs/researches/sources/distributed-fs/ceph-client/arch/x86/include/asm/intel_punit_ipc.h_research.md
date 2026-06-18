<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_punit_ipc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_punit_ipc.h

## Purpose
Intel P-unit IPC interface declarations for SoC power/clock/thermal register messaging. The header is 95 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INTEL_PUNIT_IPC_H_`; `#define IPC_TYPE_OFFSET 6`; `#define IPC_PUNIT_BIOS_CMD_BASE (BIOS_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_GTD_CMD_BASE (GTDDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_ISPD_CMD_BASE (ISPDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_CMD_TYPE_MASK (RESERVED_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_BIOS_ZERO (IPC_PUNIT_BIOS_CMD_BASE | 0x00)`; `#define IPC_PUNIT_BIOS_VR_INTERFACE (IPC_PUNIT_BIOS_CMD_BASE | 0x01)`; `#define IPC_PUNIT_BIOS_READ_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x02)`; `#define IPC_PUNIT_BIOS_WRITE_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x03)`; `#define IPC_PUNIT_BIOS_READ_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x04)`; `#define IPC_PUNIT_BIOS_WRITE_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x05)`; `#define IPC_PUNIT_BIOS_READ_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x06)`; `#define IPC_PUNIT_BIOS_WRITE_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x07)`; `#define IPC_PUNIT_BIOS_TRIGGER_VDD_RAM (IPC_PUNIT_BIOS_CMD_BASE | 0x08)`; `#define IPC_PUNIT_BIOS_READ_TELE_INFO (IPC_PUNIT_BIOS_CMD_BASE | 0x09)`; `#define IPC_PUNIT_BIOS_READ_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0a)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0b)`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_PUNIT_IPC_H_`; `typedef enum {`; `#define IPC_TYPE_OFFSET 6`; `#define IPC_PUNIT_BIOS_CMD_BASE (BIOS_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_GTD_CMD_BASE (GTDDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_ISPD_CMD_BASE (ISPDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_CMD_TYPE_MASK (RESERVED_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_BIOS_ZERO (IPC_PUNIT_BIOS_CMD_BASE | 0x00)`; `#define IPC_PUNIT_BIOS_VR_INTERFACE (IPC_PUNIT_BIOS_CMD_BASE | 0x01)`; `#define IPC_PUNIT_BIOS_READ_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x02)`; `#define IPC_PUNIT_BIOS_WRITE_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x03)`; `#define IPC_PUNIT_BIOS_READ_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x04)`; `#define IPC_PUNIT_BIOS_WRITE_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x05)`; `#define IPC_PUNIT_BIOS_READ_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x06)`; `#define IPC_PUNIT_BIOS_WRITE_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x07)`; `#define IPC_PUNIT_BIOS_TRIGGER_VDD_RAM (IPC_PUNIT_BIOS_CMD_BASE | 0x08)`; `#define IPC_PUNIT_BIOS_READ_TELE_INFO (IPC_PUNIT_BIOS_CMD_BASE | 0x09)`; `#define IPC_PUNIT_BIOS_READ_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0a)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0b)`; `#define IPC_PUNIT_BIOS_READ_TELE_EVENT_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0c)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_EVENT_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0d)`; `#define IPC_PUNIT_BIOS_READ_TELE_TRACE (IPC_PUNIT_BIOS_CMD_BASE | 0x0e)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_TRACE (IPC_PUNIT_BIOS_CMD_BASE | 0x0f)`; `#define IPC_PUNIT_BIOS_READ_TELE_EVENT (IPC_PUNIT_BIOS_CMD_BASE | 0x10)`

## Control Flow
Clients acquire the IPC path and issue read/write/command operations to P-unit firmware-controlled registers.

## State and Persistence
State is serialized through P-unit IPC hardware/mailbox and driver locks in the implementation, with no local state here.

## Dependencies and Integration Points
Depends on platform devices, IOSF/PMIC coordination, Intel SoC power drivers, and firmware mailbox semantics.

## Risks
Risks include command timeouts, lock ordering with PMIC/IOSF users, and platform register differences.

## Test Signals
Tests should cover supported SoC probe, read/write commands, timeout/error paths, concurrent clients, suspend/resume, and missing-device stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_punit_ipc.h -->
