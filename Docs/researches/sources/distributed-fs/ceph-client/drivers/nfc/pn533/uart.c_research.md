# sources/distributed-fs/ceph-client/drivers/nfc/pn533/uart.c

Purpose: Implements the PN532 UART/serdev transport for the shared PN533 core.

Important APIs and functions: `struct pn532_uart_phy` stores serdev, receive SKB, common PN533 pointer, wakeup state, command timeout timer, and current TX buffer. PHY ops are `pn532_uart_send_frame()`, `pn532_uart_send_ack()`, `pn532_uart_abort_cmd()`, `pn532_dev_up()`, and `pn532_dev_down()`. Receive parsing is handled by `pn532_uart_rx_is_frame()` and `pn532_receive_buf()`.

Control flow: Probe allocates PHY state and RX buffer, opens serdev, sets 115200 baud/no flow control, initializes common PN533 as a PN532 autopoll request/ACK/response device, finalizes setup, closes serdev for idle power, and registers NFC. `dev_up` opens serdev and sends a final wakeup; `dev_down` closes it and marks future sends to wake. Send may prepend a wakeup sequence, writes the framed SKB, and arms a short timeout that resends the current buffer. Receive accumulates bytes until it finds a PN533 frame or ACK/error frame, then passes the SKB to `pn533_recv_frame()`.

State and persistence: Runtime state includes `recv_skb`, `send_wakeup`, `cmd_timeout`, and `cur_out_buf`. No durable persistence.

Dependencies and integration points: Uses serdev bus, OF compatible `nxp,pn532`, common PN533 core, and NFC registration.

Risks: The resend timer reuses `cur_out_buf`, so lifetime depends on PN533 command completion not freeing it before timeout handling. Frame scanning tolerates garbage but can discard accumulated data when tailroom fills. Wakeup state intentionally has no mutex. Test signals include wakeup sequence, timeout resend, malformed leading bytes, ACK/error/extended frame detection, serdev open/close, remove with active timer, and autopoll behavior.
