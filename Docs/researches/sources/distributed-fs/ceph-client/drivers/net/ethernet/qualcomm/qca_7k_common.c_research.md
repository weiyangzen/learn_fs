<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.c

## Purpose
`qca_7k_common.c` implements the QCA7K serial Ethernet framing format used by both SPI and UART transports. It creates frame headers/footers and decodes byte streams into Ethernet frames with a state machine.

## Important APIs, Types, and Functions
- `qcafrm_create_header()` writes four `0xAA` bytes, little-endian payload length, and two reserved bytes.
- `qcafrm_create_footer()` writes two `0x55` footer bytes.
- `qcafrm_fsm_decode()` consumes one byte at a time and returns gather/error/completed-frame status.
- All three functions are exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
The decoder starts either at SPI hardware-length states or UART header states, validates the four-byte header, reads two length bytes and two reserved bytes, rejects lengths larger than the supplied buffer or smaller than minimum Ethernet frame length, copies payload bytes while using the state value as remaining length, then validates both footer bytes and returns the completed frame length.

## State and Persistence
Decoder state lives in caller-owned `struct qcafrm_handle` and receive buffer. The file has no static mutable state. Frame decode progress persists across calls until a complete frame or error resets the state.

## Dependencies and Integration Points
Used by `qca_spi.c` and `qca_uart.c` for RX decode and by both TX paths for header/footer creation. It depends on Ethernet/VLAN length constants from the header.

## Risks and Edge Cases
- On `QCAFRM_NOHEAD`, callers generally ignore the error and keep scanning, which is expected for stream resynchronization.
- `QCAFRM_INVFRAME` is defined but not emitted by the current decoder.
- The function writes payload bytes directly to `buf[handle->offset]`; callers must pass a buffer with adequate tailroom.
- SPI mode consumes four hardware-length bytes before the Atheros frame header, while UART mode does not.

## Test Signals
Decoder unit tests should cover valid SPI/UART frames, split frames across calls, missing header/footer, invalid lengths, minimum Ethernet padding, VLAN-sized maximum frames, and resynchronization after noise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/qca_7k_common.c -->
