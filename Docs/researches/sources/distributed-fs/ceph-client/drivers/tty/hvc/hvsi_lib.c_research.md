# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvsi_lib.c

## Purpose
`hvsi_lib.c` is a reusable HVSI packet helper used by HVC backends such as VIO and OPAL. It encapsulates HVSI handshaking, packet parsing, data packet extraction, DTR/carrier modem-control handling, and open/close behavior around backend-supplied character I/O functions.

## Important APIs, Types, and Functions
Public functions are `hvsilib_get_chars()`, `hvsilib_put_chars()`, `hvsilib_read_mctrl()`, `hvsilib_write_mctrl()`, `hvsilib_establish()`, `hvsilib_open()`, `hvsilib_close()`, and `hvsilib_init()`. Internal helpers include `hvsi_send_packet()`, `hvsi_start_handshake()`, `hvsi_send_close()`, `hvsi_cd_change()`, `hvsi_got_control()`, `hvsi_got_query()`, `hvsi_got_response()`, `hvsi_check_packet()`, and `hvsi_get_packet()`.

## Control Flow
Backends initialize an embedded `struct hvsi_priv` with get/put callbacks and terminal number. Open stores a tty kref and calls `hvsilib_establish()`. Establish first consumes any already-arrived packets, then sends close/restart handshake if needed, waits for version negotiation, reads modem control, asserts DTR, and finally sets `opened` so HVC reads may consume data.

Reads consume any buffered data packet, compact the input buffer, fetch and parse more packets, and return `-EPIPE` when the protocol is no longer established. Writes wrap up to `HVSI_MAX_OUTGOING_DATA` bytes into a VS_DATA packet and send it with an incremented sequence number. Close clears `opened` under the HVC lock for non-console ports, optionally lowers DTR on HUPCL, sends close, and drops the tty kref.

## State and Persistence Behavior
State lives in caller-owned `struct hvsi_priv`: packet buffers/cursors, sequence number, `established`, `opened`, `is_console`, modem-control bits, tty pointer, and backend callbacks. There is no global state in this file.

## Dependencies and Integration Points
It depends on `asm/hvsi.h`, HVC `struct hvc_struct`, tty krefs, timing helpers, and backend character functions such as OPAL or VIO raw put/get calls. It is designed to run both in early boot contexts with IRQs disabled and normal sleeping contexts.

## Risks and Edge Cases
The parser discards the entire input buffer when the first byte is not a valid HVSI header, trading data loss for resynchronization. The `for (tries = 1; count && tries < 2; tries++)` loop in `hvsilib_get_chars()` effectively permits one fetch cycle and should be checked against expected throughput. Carrier drop closes non-console opened sessions. `hvsilib_put_chars()` returns adjusted payload count rather than packet length on success.

## Test Signals
Signals include OPAL/VIO HVSI handshake, close/restart handshake recovery, data packet split reads, DTR set/clear, carrier-drop hangup via `-EPIPE`, early boot operation while IRQs are disabled, and tty kref balance across open/close.
