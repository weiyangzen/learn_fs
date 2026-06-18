<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.h -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.h

## Purpose
Defines TI UMP address spaces, UART register offsets, command numbers, UART configuration constants, DMA descriptor layout, interrupt packet layout, and helper macros used by the Edgeport TI usb-serial driver in `io_ti.c`.

## Important APIs, Types, And Functions
The header exports address-space constants `DTK_ADDR_SPACE_XDATA`, `DTK_ADDR_SPACE_I2C_TYPE_II`, and `DTK_ADDR_SPACE_I2C_TYPE_III`; UART memory bases `UMPMEM_BASE_UART1`, `UMPMEM_BASE_UART2`, and `UMPMEM_OFFS_UART_LSR`; UART character, parity, stop-bit, and LSR masks; UMP port-configuration flag masks; purge direction masks; and command IDs such as `UMPC_SET_CONFIG`, `UMPC_OPEN_PORT`, `UMPC_START_PORT`, `UMPC_PURGE_PORT`, `UMPC_MEMORY_READ`, and `UMPC_MEMORY_WRITE`. `struct out_endpoint_desc_block` models the UMP DMA output endpoint descriptor read by `tx_active()`. `struct ump_uart_config` is the packed command payload built from tty termios. `struct ump_interrupt` models two-byte interrupt messages. `TIUMP_GET_PORT_FROM_CODE()` and `TIUMP_GET_FUNC_FROM_CODE()` decode interrupt code bytes.

## Control Flow
This file has no executable control flow. Its definitions shape control flow in `io_ti.c`: port open/close/start/purge operations use the command IDs; termios changes fill `struct ump_uart_config`; interrupt callbacks decode function and port fields; and TX-empty checks read DMA count and line-status bits at the fixed UMP memory offsets.

## State And Persistence
The header does not own state. It defines the binary wire and memory layouts that become persistent only when passed to device firmware or read from device memory. Incorrect constants would affect device-side UART mode, flow-control behavior, DMA state interpretation, and line-status mapping.

## Dependencies And Integration Points
It depends on UART flag definitions from the surrounding Edgeport driver stack, especially line status values included before this header. It is consumed by `io_ti.c` and must remain synchronized with TI UMP firmware semantics.

## Risks And Edge Cases
These values are ABI-like hardware contracts. Any mismatch in endian expectation, struct layout, or command number can break firmware communication. `struct ump_uart_config` contains 16-bit fields that the C file converts to big endian before sending, so callers must preserve that convention. The interrupt port macro only extracts one port bit, matching the two-port implementation; using it for devices with more direct UMP ports would be insufficient.

## Test Signals
Compile-time integration with `io_ti.c`, successful port configuration after termios changes, correct interrupt routing by port number, accurate TX-empty detection, and hardware-level validation of purge/open/start commands are the primary signals that these definitions match firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/io_ti.h -->
