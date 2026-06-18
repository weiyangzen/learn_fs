## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/goya_packets.h

### Purpose
`goya_packets.h` describes Goya command packet IDs, shared packet header fields, control-bit masks, and packed little-endian packet payload layouts understood by the command processor.

### Important APIs, Types, And Functions
`enum packet_id` enumerates `PACKET_WREG_32`, `PACKET_WREG_BULK`, message packets, DMA packets, `PACKET_FENCE`, `PACKET_NOP`, and `PACKET_STOP`. `struct goya_packet` provides the common 64-bit header plus flexible contents. Specific layouts include `packet_wreg32`, `packet_wreg_bulk`, `packet_msg_long`, `packet_msg_short`, `packet_msg_prot`, `packet_fence`, `packet_lin_dma`, and `packet_cp_dma`. Header/control macros expose packet ID, opcode, EB/RB/MB, register offset, and linear-DMA mode bits.

### Control Flow
The file has no executable flow. Submission validation reads `goya_packet.header`, extracts `packet_id`, casts the following bytes to the matching packet struct, validates command size and control bits, and then passes the packet buffer to hardware.

### State, Persistence, And Dependencies
The persistent state is the command buffer submitted to the device and any resulting hardware register or DMA side effect. The header depends on Linux fixed-width and little-endian types, and on firmware/hardware matching this ABI exactly.

### Integration Points
It is part of the Goya command submission ABI between userspace, the kernel driver, and the command processor. DMA packet fields integrate with memory manager address validation, while message packets integrate with firmware doorbells/queues.

### Risks
Packet structs are hardware ABI: changing field size, endian type, or control masks breaks existing command buffers. Flexible arrays require separate size validation. DMA direction, memset, completion, and write-only bits are security-sensitive because malformed packets can target unintended memory or registers.

### Test Signals
Tests should validate every packet ID, malformed headers, short command buffers, register-offset bounds, DMA address ranges, fence behavior, stop/nop handling, and endian-correct decoding on little-endian command streams.
