<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pasemi_dma.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pasemi_dma.h

## Purpose
This header defines the PA Semi DMA engine register and descriptor bitfield interface used by network, copy, and platform DMA code.

## Important APIs, Types, And Functions
It defines `struct pasdma_status`, channel/interface enum values, capability masks, common TX/RX command/status bits, RX interface registers, TX/RX channel register offsets, descriptor ring base/size/increment fields, status/control fields, descriptor flags, and bitfield constructor macros for packet length, interface, channel, checksum, LRO, and buffer metadata.

## Control Flow
Drivers program capability-derived channel counts, configure rings and interfaces by writing the offset macros, enable channels, then poll or interrupt on command/status and descriptor completion bits.

## State And Persistence Behavior
State lives in memory-mapped DMA registers and descriptor rings. Ring base, size, counters, active/stop bits, drop counters, and descriptor ownership persist until driver reset or device reset.

## Dependencies And Integration Points
It integrates with PA Semi Ethernet and DMA drivers, PCI/platform device setup, DMA mapping, and interrupt handling.

## Risks And Edge Cases
This is raw hardware ABI. Incorrect bit shifts can corrupt DMA rings or packet metadata. Ring base alignment and size encodings are constrained. Register status bits may be clear-on-write or hardware-updated.

## Test Signals
Run PA Semi network transmit/receive, checksum offload, interrupt moderation, ring wrap, stop/start, drop counter, and DMA mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/pasemi_dma.h -->
