# sources/distributed-fs/ceph-client/drivers/net/wan/wanxl.h

## Purpose
`wanxl.h` defines the shared host/firmware ABI for the wanXL driver. It contains board configuration flags, cable/personality status bits, buffer and descriptor constants, PLX register offsets, doorbell bit assignments, status-memory offsets, and C structures used by the host driver.

## Important APIs, Types, And Functions
There are no functions. Important constants include `TX_BUFFERS`, `RX_BUFFERS`, `RX_QUEUE_LENGTH`, `BUFFER_LENGTH`, `BUFFERS_ADDR`, packet states (`PACKET_EMPTY`, `PACKET_FULL`, `PACKET_SENT`, `PACKET_UNDERRUN`), doorbell bits from card and to card, PLX mailbox/doorbell/control offsets, DMA register offsets for assembler, and status offsets. `desc_t` is the shared packet descriptor with volatile status and length. `port_status_t` is the per-port shared status block containing open/cable/error fields, parity/encoding/clocking fields, and TX descriptors.

## Control Flow
The host driver uses these constants to populate shared memory, ring PLX doorbells, and interpret card interrupts. The firmware uses the same values to service open/close/TX commands, fill RX descriptors, and notify cable/TX/RX events.

## State And Persistence
The header declares the layout of volatile shared state; it does not own state itself. `volatile` fields in `desc_t` and `port_status_t` mark locations updated asynchronously by firmware or host.

## Dependencies And Integration Points
The file is included by both `wanxl.c` and `wanxlfw.S`. It includes `HDLC_MAX_MRU` indirectly in `BUFFER_LENGTH` and uses `__ASSEMBLER__` guards to expose different PLX offsets and DMA register definitions for firmware assembly versus host C.

## Risks
Any change to descriptor sizes, offsets, or doorbell bit numbers requires synchronized host and firmware rebuilds. Comments explicitly note that some flags require rebuilding firmware. The ABI uses raw offsets and packed assumptions rather than generated structure validation, so compile-time cross-checks would be valuable.

## Test Signals
Build both host and firmware include paths, verify `sizeof(desc_t)` matches `DESC_LENGTH`, validate status offsets against `port_status_t`, confirm doorbell bit compatibility with firmware event loops, and run hardware tests after any buffer-count or RAM-layout change.
