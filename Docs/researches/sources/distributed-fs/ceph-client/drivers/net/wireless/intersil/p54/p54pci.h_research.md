# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54pci.h

## Purpose
This header defines Prism54 PCI register bits, CSR layout, DMA descriptor/ring-control formats, MMIO access macros, and PCI-private driver state.

## Important APIs, Types, and Functions
- Interrupt bits cover device interrupt commands, interrupt identification/ack/enable, and PCI UART bits.
- Control/status bits include sleep mode, CLKRUN, reset, RAM boot, start halted, and host override.
- `struct p54p_csr` maps MMIO registers, CardBus CIS, and direct memory window.
- `struct p54p_desc` and `struct p54p_ring_control` define RX/TX data and management DMA rings.
- `P54P_READ()` and `P54P_WRITE()` wrap raw MMIO access.
- `struct p54p_priv` embeds `p54_common` and stores PCI device, map, tasklet, firmware, lock, ring control, indexes, SKB arrays, and completions.

## Control Flow
No direct control flow exists. `p54pci.c` uses these definitions to reset/upload firmware, program rings, and process interrupts.

## State and Persistence Behavior
The header defines the in-memory and MMIO-backed state. Coherent ring control is shared with the device; SKB arrays and indexes mirror descriptor ownership in the driver.

## Dependencies and Integration Points
It depends on Linux interrupt types and p54 common structures. Some register definitions are shared with the USB backend under the `P54USB_H` guard.

## Risks and Edge Cases
The CSR struct is a hardware register layout and must match the device BAR. Raw MMIO access bypasses endian/accessor niceties except explicit little-endian casts. The ring sizes are fixed ABI values; mismatches with firmware expectations would break RX/TX.

## Test Signals
Successful PCI firmware boot, ring DMA traffic, and interrupts validate the register and descriptor definitions.
