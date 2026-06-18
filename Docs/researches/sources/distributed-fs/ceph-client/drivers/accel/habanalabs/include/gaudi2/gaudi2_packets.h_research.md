<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_packets.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_packets.h

## Purpose
Defines Gaudi2 command packet IDs, common header bit layout, control field masks, and packet payload structures used by command submission, internal DMA setup, synchronization, and firmware/queue-manager messaging.

## Important APIs, Types, And Functions
- `PACKET_HEADER_PACKET_ID_SHIFT` and `PACKET_HEADER_PACKET_ID_MASK` extract the 5-bit packet type from the 64-bit packet header.
- `enum packet_id` includes WREG, MSG long/short/protected, CP DMA, repeat, fence, linear DMA, NOP, STOP, wait, command-buffer list, load-and-execute, ARC stream, 64-bit WREG variants, and `MAX_PACKET_ID`.
- `GAUDI2_PKT_CTL_*` masks describe opcode, engine barrier, register barrier, and message barrier bits.
- `struct gaudi2_packet` is the generic 8-byte header plus flexible payload wrapper.
- Payload structs include `packet_wreg32`, `packet_wreg_bulk`, `packet_msg_long`, `packet_msg_short`, `packet_msg_prot`, `packet_fence`, `packet_lin_dma`, `packet_arb_point`, `packet_repeat`, `packet_wait`, `packet_cb_list`, `packet_load_and_exe`, and `packet_cp_dma`.
- Short-message, fence, and linear-DMA masks describe SOB/MON synchronization, fence target/decrement/id, endian, memset, write-completion, and context-id fields.

## Control Flow
Packet parsers and builders inspect the header to classify user or driver-generated packets, then cast to the matching payload struct. Gaudi2 driver code builds `packet_lin_dma`, `packet_msg_short`, and `packet_fence` instances for internal jobs, memory initialization, SOB/MON updates, and synchronization. Fields are populated with `FIELD_PREP` against the masks in this header before packets are submitted to hardware queues.

## State And Persistence Behavior
Packets are transient command-buffer data. They may live in user command buffers, kernel-generated command buffers, or DMA-accessible memory until consumed by hardware. The structs define little-endian wire layout; they are not persistent across boots.

## Dependencies And Integration Points
Depends on `<linux/types.h>` for `__le32`, `__le64`, and `u8`. Integrates with Gaudi2 command submission, parser validation, DMA packet generation, synchronization managers, queue managers, and firmware command execution. The packet ID namespace mirrors hardware packet encoding.

## Risks And Edge Cases
Mis-sized structs or wrong bit masks can make the driver accept malformed packets or emit packets that hardware interprets incorrectly. Flexible-array packet types require careful length validation. Endianness annotations must be honored. The header does not enforce alignment or bounds; packet parsers must check sizes, addresses, and packet IDs before casting.

## Test Signals
Signals include command parser tests for every packet ID, invalid-packet rejection, internal DMA/memset jobs completing, SOB/MON synchronization working, fences reaching expected values, and hardware command submissions running without queue hangs or packet sanity events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2_packets.h -->
