# sources/distributed-fs/ceph-client/arch/mips/include/asm/txx9/pci.h

## Purpose

`pci.h` defines board or SoC support interfaces for Toshiba TXx9/TX49xx MIPS platforms.

## Important APIs, Types, And Functions

The file exposes memory-mapped register layouts, clock/reset/interrupt constants, platform-data structs, or setup prototypes used by TXx9 board code. Includes: `linux/pci.h`. Macros/constants: `__ASM_TXX9_PCI_H`, `TXX9_PCI_OPT_PICMG`, `TXX9_PCI_OPT_CLK_33`, `TXX9_PCI_OPT_CLK_66`, `TXX9_PCI_OPT_CLK_MASK`, `TXX9_PCI_OPT_CLK_AUTO`. Types/enums/unions: `pci_controller`, `txx9_pci_err_action`. Functions/prototypes/helpers: `txx9_alloc_pci_controller`, `txx9_pci66_check`, `txx9_pcibios_setup`.

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
Static review signal: this source currently has 40 lines and 1147 bytes; major size or symbol-surface changes should trigger a fresh review of this report.
