# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_hwdep.h

## Purpose
This header defines low-level miXart hardware access helpers and register layout. It provides endian-aware MMIO read/write macros, BAR address helpers, daughterboard type constants, BAR sizes, pseudo-register offsets for firmware loading and performance counters, mailbox FIFO addresses, message-frame layout constants, interrupt register offsets/masks, reset offset, and the firmware setup function prototype.

## Important APIs, types, and functions
`readl_be`, `writel_be`, `readl_le`, and `writel_le` normalize MMIO endianness where architecture helpers are absent. `MIXART_MEM(mgr, x)` addresses BAR0 memory and `MIXART_REG(mgr, x)` addresses BAR1 registers. Constants under `MIXART_PSEUDOREG_*` coordinate firmware status, base addresses, board type, daughterboard presence, flow-table pointer, and performance counters. `MSG_*` constants describe firmware mailbox FIFO pointers, stacks, frame sizes, and resource-protection words. `MIXART_PCI_*` constants describe interrupt mask/status/doorbell registers. The exported declaration is `snd_mixart_setup_firmware`.

## Control flow
The header has no executable control flow, but its offsets drive firmware loading, mailbox initialization, message send/receive, interrupt masking/unmasking, proc BAR reads, and board reset. `mixart_hwdep.c` uses pseudo-register constants during firmware staging; `mixart_core.c` uses mailbox and interrupt constants; `mixart.c` uses BAR sizes for proc entries.

## State and persistence behavior
The constants define hardware and firmware state locations. Firmware status pseudo-registers persist while the board is powered. Mailbox head/tail registers represent shared host/firmware queue state. The brutal reset offset is used during teardown when firmware had been loaded.

## Dependencies and integration points
It depends on ALSA hwdep declarations and Linux raw MMIO/endian helpers. All miXart implementation files include it either directly or indirectly for BAR and protocol access.

## Risks and edge cases
Incorrect offsets or endian accessors can break firmware loading or mailbox traffic immediately. Pointer arithmetic assumes valid `mgr->mem[0].virt` and `mgr->mem[1].virt` mappings. The mailbox stack and frame constants must match embedded firmware exactly. The daughterboard masks drive feature decisions; wrong values can expose unsupported digital devices or reject valid hardware.

## Test signals
Compile tests on little- and big-endian targets are useful for accessor coverage. Runtime signals include successful BAR proc reads, correct firmware stage status polling, mailbox message exchange, interrupt delivery through OIDI, and board reset during driver removal after firmware load.
