# sources/distributed-fs/ceph-client/drivers/nfc/s3fwrn5/uart.c

## Purpose
`uart.c` is the serdev UART transport for Samsung S3FWRN82 using the shared S3FWRN5 NCI core and common GPIO power helpers.

## Important APIs, types, and functions
- `struct s3fwrn82_uart_phy` embeds `phy_common`, the serdev device, and an accumulating receive skb.
- `s3fwrn82_uart_write()` writes complete sk_buffs using `serdev_device_write()`.
- `s3fwrn82_uart_read()` is the serdev receive callback; it accumulates bytes until the NCI header and declared payload length are present, then calls `s3fwrn5_recv_frame()`.
- `s3fwrn82_uart_probe()` opens/configures serdev at 115200 baud, disables flow control, obtains `en` and `wake` GPIOs, and calls `s3fwrn5_probe()`.
- `s3fwrn82_uart_remove()` removes the shared core, closes serdev, and frees the receive skb.

## Control flow
Probe allocates an initial receive skb and sets the device COLD. Incoming bytes are appended one by one. Once at least 3 NCI header bytes exist and `len - 3` reaches the payload length byte, the skb is delivered to the shared receive router and accumulation restarts with a new allocation on the next byte. TX is direct and blocking with an infinite schedule timeout.

## State and persistence
Runtime state is serdev open/configuration, common GPIO/mode state, and the partially filled receive skb. There is no persistent storage.

## Dependencies and integration points
The file depends on serdev, GPIO descriptors, NFC/NCI packet format, and the shared S3FWRN5 core. Device tree compatible is `samsung,s3fwrn82`.

## Risks
Receive parsing is NCI-header-specific and does not branch for firmware headers, so firmware-update receive over UART may not be supported even though the shared core has firmware mode. The receive buffer is fixed at 258 bytes; invalid length bytes could fill the skb to its limit without explicit overflow checks beyond skb behavior. Probe preallocates `recv_skb`, but `s3fwrn82_uart_read()` also allocates when it is NULL after delivery.

## Test signals
Test probe error unwinding for baud mismatch, missing GPIOs, and core probe failure; byte-by-byte frame assembly; multiple frames in one receive callback; short frames; maximum-length frames; and remove while a partial skb exists.
