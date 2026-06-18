# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/tx4927pcic.h

## Purpose

`tx4927pcic.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/pci.h`, `linux/irqreturn.h`. Macros/constants: `__ASM_TXX9_TX4927PCIC_H`, `TX4927_PCIC_G2PSTATUS_ALL`, `TX4927_PCIC_G2PSTATUS_TTOE`, `TX4927_PCIC_G2PSTATUS_RTOE`, `TX4927_PCIC_PCISTATUS_ALL`, `TX4927_PCIC_PBACFG_FIXPA`, `TX4927_PCIC_PBACFG_RPBA`, `TX4927_PCIC_PBACFG_PBAEN`, `TX4927_PCIC_PBACFG_BMCEN`, `TX4927_PCIC_PBASTATUS_ALL`, `TX4927_PCIC_PBASTATUS_BM`, `TX4927_PCIC_G2PMnGBASE_BSDIS`, `TX4927_PCIC_G2PMnGBASE_ECHG`, `TX4927_PCIC_G2PIOGBASE_BSDIS`, `TX4927_PCIC_G2PIOGBASE_ECHG`, `TX4927_PCIC_PCICSTATUS_ALL`, `TX4927_PCIC_PCICSTATUS_PME`, `TX4927_PCIC_PCICSTATUS_TLB`, `TX4927_PCIC_PCICSTATUS_NIB`, `TX4927_PCIC_PCICSTATUS_ZIB`, `TX4927_PCIC_PCICSTATUS_PERR`, `TX4927_PCIC_PCICSTATUS_SERR`, `TX4927_PCIC_PCICSTATUS_GBE`, `TX4927_PCIC_PCICSTATUS_IWB`, `TX4927_PCIC_PCICSTATUS_E2PDONE`, `TX4927_PCIC_PCICCFG_GBWC_MASK`, `TX4927_PCIC_PCICCFG_HRST`, `TX4927_PCIC_PCICCFG_SRST`, `TX4927_PCIC_PCICCFG_IRBER`, `TX4927_PCIC_PCICCFG_G2PMEN`, `TX4927_PCIC_PCICCFG_G2PM0EN`, `TX4927_PCIC_PCICCFG_G2PM1EN`, `TX4927_PCIC_PCICCFG_G2PM2EN`, `TX4927_PCIC_PCICCFG_G2PIOEN`, and 50 more. Types/enums/unions: `tx4927_pcic_reg`, `pci_controller`. Functions/prototypes/helpers: `tx4927_pcic_setup`, `tx4927_report_pcic_status`, `tx4927_dump_pcic_settings`, `get_tx4927_pcicptr`, `tx4927_pcibios_setup`, `tx4927_pcierr_interrupt`.

## Control Flow

Control flow is implemented in platform files; this header supplies addresses and declarations used during early board setup, interrupt routing, device registration, clock/timer setup, PCI, DMA, GPIO, and serial initialization.

## State And Persistence

State is hardware register state, platform-data passed to devices, IRQ numbering, and board global clock/pcode variables; no filesystem persistence exists.

## Dependencies And Integration Points

It depends on TXx9 common platform code, MIPS I/O mapping, PCI/IRQ/timer/gpio subsystems, and board-specific boot paths.

## Risks

Risks are wrong physical/MMIO addresses, stale IRQ numbers, bitfield mistakes in reset/clock control, and platform-data mismatch with drivers.

## Test Signals

Test signals are TXx9 defconfig builds, board boot logs, PCI enumeration, timer ticks, serial console, GPIO/LED behavior, DMA tests, and interrupt storm checks.
Static review signal: this source currently has 204 lines and 6534 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
