# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.c

## Purpose
`es58x_fd.c` is the model-specific adapter for ETAS ES582.1 and ES584.1 CAN FD devices. It implements the CAN/CANFD command set, variable-length RX/TX record parsing, FD channel configuration, timestamp request, echo handling, and the exported operator/parameter tables consumed by the ES58x core.

## Important APIs, Types, And Functions
The file exports `const struct es58x_parameters es58x_fd_param` and `const struct es58x_operators es58x_fd_ops`. Key functions are `es58x_fd_cmd_type()`, `es58x_fd_get_msg_len()`, `es58x_fd_echo_msg()`, `es58x_fd_rx_can_msg()`, `es58x_fd_rx_event_msg()`, `es58x_fd_rx_cmd_ret_u32()`, `es58x_fd_tx_ack_msg()`, `es58x_fd_can_cmd_id()`, `es58x_fd_device_cmd_id()`, `es58x_fd_handle_urb_cmd()`, `es58x_fd_fill_urb_header()`, `es58x_fd_tx_can_msg()`, `es58x_fd_convert_bittiming()`, `es58x_fd_enable_channel()`, `es58x_fd_disable_channel()`, and `es58x_fd_get_timestamp()`.

## Control Flow
Inbound commands are dispatched first by command type: CAN, CANFD, or device. Channel commands look up the netdevice using 0-based channel indexes, then route enable/disable returns, TX acknowledgments, echo messages, RX messages, reset returns, and error/event messages. Device commands currently handle timestamp replies.

RX CAN payloads are concatenated variable-length records. `es58x_fd_rx_can_msg()` validates total buffer length, iterates until the message buffer is consumed, computes each record length from flags and DLC/len, checks for overrun and CAN FD max payload length, then calls the core `es58x_rx_can_msg()` when the netdevice is running. Echo messages validate consecutive 8-bit packet indexes reconstructed against the wider `tx_tail` counter and delegate echo skb completion to the core.

TX chooses CAN or CANFD command type based on the netdevice ctrlmode and skb type. Each encoded record stores an 8-bit packet index, raw CAN ID, ES58x flags, DLC or length, and payload. Channel enable converts nominal and data bit timings to hardware register-minus-one encoding, configures samples, physical layer, echo, listen-only/active mode, CAN FD or non-ISO FD mode, and optional automatic TDC fields, then sends an enable-channel command.

## State And Persistence
No persistent storage is used. The adapter reads and updates shared per-channel TX counters and CAN ctrlmode via `struct es58x_priv`. ES58x FD uses 0-based device channel numbering and supports one or two channels depending on product. Parameters define 80 MHz clock, 8 Mbps maximum bitrate, CAN FD and TDC auto support, FIFO mask 255, bulk max 100, and FD-specific SOF values.

## Dependencies And Integration Points
This file depends on the shared ES58x core for USB framing, CRC, URB submission, SocketCAN skb creation, echo management, state/error handling, and timestamp calibration. It depends on CAN FD helpers such as `canfd_sanitize_len()`, `can_fd_len2dlc()`, and `can_fd_tdc_is_enabled()`. Timing constants are based on Microchip SAM E70/S70/V70/V71 MCAN registers.

## Risks
Variable-length record parsing is the main risk: the code must distinguish CAN DLC and CAN FD length, reject oversized FD payloads, and advance by the computed structure length exactly. Echo indexes are only one byte on the wire, so reconstruction from `tx_tail` must remain correct across wraparound. FD devices cannot mix classic and FD frames in one bulk transmission, so core batching logic and `tx_can_msg_is_fd` must stay aligned with this adapter. Manual TDC is explicitly unsupported despite the hardware exposing fields.

## Test Signals
Exercise ES582.1 dual-channel and ES584.1 single-channel probe, classic CAN and CAN FD traffic, BRS/ESI flags, non-ISO FD ctrlmode, listen-only, triple sampling, automatic TDC configuration, variable-length RX batches, echo wraparound and ordering, bus error/event messages, timestamp replies, and reset command return handling.
