# sources/distributed-fs/ceph-client/drivers/comedi/drivers/adl_pci7250.c

## Purpose

This driver supports ADLINK PCI-7250, LPCI-7250, and LPCIe-7250 relay output and isolated digital input boards. It exposes paired relay DO and DI subdevices with either 8 or 32 channels depending on the board variant.

## Important APIs, types, and functions

Key functions are `adl_pci7250_read8()`, `adl_pci7250_write8()`, `adl_pci7250_do_insn_bits()`, `adl_pci7250_di_insn_bits()`, and `pci7250_auto_attach()`. The access helpers abstract MMIO versus port I/O. PCI IDs distinguish older I/O-port variants and newer LPCIe MMIO subsystem ID `0x7000`.

## Control Flow

Auto-attach enables PCI, verifies BAR 2 length, maps BAR 2 as MMIO or records it as I/O port space, chooses `max_chans` as 8 for the newer LPCIe subsystem device and 32 for other variants, allocates two subdevices, initializes relay DO state by reading even offset registers, and initializes DI reads from odd offset registers. DO writes walk byte-wide banks and write only banks whose mask includes changed bits.

## State and Persistence

State is relay output state in `s->state` and hardware relay registers. Inputs are read directly. No persistent data is stored, and detach does not reset relays.

## Dependencies and Integration Points

The driver depends on COMEDI PCI helpers, optional `CONFIG_HAS_IOPORT`, MMIO byte accessors, and ADLINK/PLX PCI subsystem IDs. It integrates with both legacy port-I/O and newer MMIO board designs.

## Risks

Channel count depends on subsystem ID and an assumption that older boards may have PCI-7251 expansion modules. Missing modules simply make extra channels ineffective. The `insn_bits` callbacks return `2` rather than `insn->n`, matching the two-word bits instruction convention but worth preserving. MMIO and I/O-port paths must stay equivalent.

## Test Signals

Validation includes old and new subsystem IDs, 8-channel limit on newer LPCIe, 32-channel behavior on older variants, initial relay state readback, per-bank masked DO writes, DI reads from odd offsets, operation without I/O port support for MMIO boards, and clean unmap/release on detach.
