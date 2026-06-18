<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hpet.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hpet.h

## Purpose
HPET timer declarations, ID constants, and boot/runtime hooks for x86 high precision event timers. The header is 102 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/msi.h>`; `#include <linux/interrupt.h>`

Notable constants/macros: `#define _ASM_X86_HPET_H`; `#define HPET_MMAP_SIZE 1024`; `#define HPET_ID 0x000`; `#define HPET_PERIOD 0x004`; `#define HPET_CFG 0x010`; `#define HPET_STATUS 0x020`; `#define HPET_COUNTER 0x0f0`; `#define HPET_Tn_CFG(n) (0x100 + 0x20 * n)`; `#define HPET_Tn_CMP(n) (0x108 + 0x20 * n)`; `#define HPET_Tn_ROUTE(n) (0x110 + 0x20 * n)`; `#define HPET_T0_CFG 0x100`; `#define HPET_T0_CMP 0x108`; `#define HPET_T0_ROUTE 0x110`; `#define HPET_T1_CFG 0x120`; `#define HPET_T1_CMP 0x128`; `#define HPET_T1_ROUTE 0x130`; `#define HPET_T2_CFG 0x140`; `#define HPET_T2_CMP 0x148`

Notable declarations and inline helpers: `#define _ASM_X86_HPET_H`; `#define HPET_MMAP_SIZE 1024`; `#define HPET_ID 0x000`; `#define HPET_PERIOD 0x004`; `#define HPET_CFG 0x010`; `#define HPET_STATUS 0x020`; `#define HPET_COUNTER 0x0f0`; `#define HPET_Tn_CFG(n) (0x100 + 0x20 * n)`; `#define HPET_Tn_CMP(n) (0x108 + 0x20 * n)`; `#define HPET_Tn_ROUTE(n) (0x110 + 0x20 * n)`; `#define HPET_T0_CFG 0x100`; `#define HPET_T0_CMP 0x108`; `#define HPET_T0_ROUTE 0x110`; `#define HPET_T1_CFG 0x120`; `#define HPET_T1_CMP 0x128`; `#define HPET_T1_ROUTE 0x130`; `#define HPET_T2_CFG 0x140`; `#define HPET_T2_CMP 0x148`; `#define HPET_T2_ROUTE 0x150`; `#define HPET_ID_REV 0x000000ff`; `#define HPET_ID_NUMBER 0x00001f00`; `#define HPET_ID_64BIT 0x00002000`; `#define HPET_ID_LEGSUP 0x00008000`; `#define HPET_ID_VENDOR 0xffff0000`

## Control Flow
Boot code probes HPET address/configuration, initializes clockevent/clocksource paths, may force or disable HPET, and exposes MSI/remapping support where available.

## State and Persistence
State is global HPET enablement, memory-mapped HPET registers, legacy replacement mode, and per-channel timer allocation managed by implementation files.

## Dependencies and Integration Points
Depends on io mapping, APIC/IRQ routing, ACPI/platform timer discovery, clockevents, and x86 boot parameters.

## Risks
Risks include broken firmware tables, unsafe MMIO mapping, interrupt routing failures, and clocksource instability.

## Test Signals
Tests should boot with hpet=on/off/force, validate clocksource selection, periodic/oneshot timers, MSI HPET channels, suspend/resume, and systems without HPET.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hpet.h -->
