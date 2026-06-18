# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bcm4908_enet.h

## Purpose
Provides the BCM4908 ENET register map and descriptor control/status bit definitions used by `bcm4908_enet.c`.

## Important APIs, Types, and Functions
This header is macro-only. It defines top-level ENET control, MIB, GMAC status, FIFO flush, flow control, DMA controller, DMA channel config, DMA channel state RAM, and DMA descriptor control/status fields. Key fields include `ENET_DMA_CTRL_CFG_MASTER_EN`, per-channel interrupt status/mask bits (`BUFF_DONE`, `DONE`, `NO_DESC`, `RX_ERROR`), descriptor `DMA_CTL_STATUS_OWN`, `SOP`, `EOP`, `WRAP`, `APPEND_CRC`, and the buffer length mask/shift.

## Control Flow
There is no executable control flow. The implementation uses these constants to select the RX and TX channel blocks, reset DMA state, program descriptor base pointers, mask/ack interrupts, force GMAC status, flush FIFOs, and encode/decode descriptors in the RX/TX NAPI paths.

## State and Persistence
The header describes persistent hardware state in MMIO registers and DMA descriptor words. Descriptor state is shared between software and hardware: software sets OWN, length, WRAP, SOP/EOP, and address fields; hardware clears OWN and writes completion length/status. Channel state RAM persists ring base and current descriptor information while DMA is active.

## Dependencies and Integration Points
Consumed directly by `bcm4908_enet.c` and indirectly tied to `unimac.h` for the UMAC sub-block. It must match the BCM4908 hardware manual and the driver's assumption that channel 0 is RX, channel 1 is TX, and descriptor addresses fit in 32 bits.

## Risks and Test Signals
Risks are incorrect offsets or descriptor bit definitions causing DMA stalls, lost interrupts, false link/speed status, or corrupt skb lengths. Test signals are compile coverage, descriptor dumps under RX/TX load, interrupt status/mask validation, DMA no-descriptor recovery, and comparing register values against known-good bootloader or vendor driver programming.
