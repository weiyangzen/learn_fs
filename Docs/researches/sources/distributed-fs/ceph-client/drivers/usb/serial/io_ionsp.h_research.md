# sources/distributed-fs/ceph-client/drivers/usb/serial/io_ionsp.h

## Purpose

This header defines the I/O Networks Serial Protocol, or IOSP, used by Edgeport devices to multiplex data, commands, status, and flow-control information for multiple serial ports over a single USB bulk endpoint pair plus an interrupt endpoint. It is a shared host/firmware protocol contract and must stay synchronized with peripheral firmware.

## Important APIs, Types, And Constants

`struct int_status_pkt` describes interrupt-pipe status: a little-endian `RxBytesAvail` count and per-port `TxCredits` array sized by `MAX_RS232_PORTS`. `GET_INT_STATUS_SIZE` computes the active packet size for a port count.

Header constants include `IOSP_DATA_HDR_SIZE`, `IOSP_CMD_HDR_SIZE`, `IOSP_MAX_DATA_LENGTH`, `IOSP_PORT_MASK`, and `IOSP_CMD_STAT_BIT`. Parsing macros distinguish data and command/status headers, extract port numbers, data lengths, and status codes. Builder macros create data and command header bytes.

Command constants include direct UART-register writes through `IOSP_WRITE_UART_REG`, the extended-command selector `IOSP_EXT_CMD`, and extended commands such as `IOSP_CMD_OPEN_PORT`, `IOSP_CMD_CLOSE_PORT`, `IOSP_CMD_CHASE_PORT`, RX/TX flow setup, XON/XOFF character setup, RX checkpoint requests, and break set/clear. `MAKE_CMD_WRITE_REG` and `MAKE_CMD_EXT_CMD` append encoded commands to a caller-provided command buffer while advancing pointer and length variables.

Flow-control masks define how the device stops incoming UART data (`IOSP_RX_FLOW_RTS`, `IOSP_RX_FLOW_DTR`, `IOSP_RX_FLOW_DSR_SENSITIVITY`, `IOSP_RX_FLOW_XON_XOFF`) and what prevents device transmission (`IOSP_TX_FLOW_CTS`, `IOSP_TX_FLOW_DSR`, `IOSP_TX_FLOW_DCD`, `IOSP_TX_FLOW_XON_XOFF`, and related optional behaviors). Status constants define LSR, MSR, LSR-with-data, extended status, chase response, RX-check response, and open response formats. `IOSP_GET_STATUS_LEN` and related macros classify status message length.

## Control Flow

The file has no executable functions, but it defines the state machine consumed by `io_edgeport.c`. Host TX data is framed as a two-byte data header followed by payload for a port. Host commands are command/status headers followed by one or more parameters. Device bulk-IN streams alternate data headers and status headers. The interrupt pipe reports how many bytes are waiting on bulk IN and how many TX credits are available per port, which drives the driver's read scheduling and write backpressure.

## State And Persistence

No local state exists. IOSP messages mutate state in device firmware and in the driver's cached port state. Open responses initialize `txCredits` and modem status. Interrupt packets add credits and pending-read byte counts. LSR/MSR status packets update `icount` counters and shadow registers. Flow-control and UART-register commands update hardware state until changed, closed, reset, or disconnected.

## Dependencies And Integration Points

This header depends on `MAX_RS232_PORTS` from `io_edgeport.h` and on Linux integer types. It integrates directly with `io_edgeport.c` command builders, receive parser, open/close/chase flow, termios programming, throttle/unthrottle, break control, and status handling. It also relies on UART register constants from `io_16654.h` for direct register write commands.

## Risks

The macros write into caller-managed buffers without bounds checking, so callers must allocate sufficient command space and pass valid pointer variables. Header length encoding is 12-bit and must match device credit accounting; sending more bytes than credits allow can overflow peripheral buffering. Status length classification must match firmware or the receive parser will desynchronize. Some documented flow-control bits are not implemented by firmware, so setting them may produce no effect. Because this protocol multiplexes all ports, a wrong port number or malformed header can deliver data or status to the wrong tty.

## Test Signals

Signals include open responses for every port, interrupt packets with RX byte counts and per-port credits, data headers at minimum and maximum lengths, payloads split across bulk URBs, status headers split across URBs, LSR/MSR and LSR-data handling, chase response wakeups, RX-check responses, termios-triggered flow-control commands, XON/XOFF character programming, break set/clear commands, and malformed status-code handling without parser lockup.
