# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.c

## Purpose
`es58x_core.c` is the shared SocketCAN USB implementation for ETAS ES581.4, ES582.1, and ES584.1 adapters. It owns USB probe/disconnect, devlink allocation, netdevice registration, URB allocation and resubmission, command CRC and framing, split-URB reassembly, timestamp calibration, TX batching, echo skb accounting, CAN/CAN FD RX conversion, and common CAN error handling. Variant files provide protocol-specific operators and parameters.

## Important APIs, Types, And Functions
The core binds USB IDs for ES581.4, ES582.1, and ES584.1 and selects `es581_4_param/es581_4_ops` or `es58x_fd_param/es58x_fd_ops` from `id->driver_info`. Exported helpers used by variants include `es58x_can_get_echo_skb()`, `es58x_tx_ack_msg()`, `es58x_rx_can_msg()`, `es58x_rx_err_msg()`, `es58x_rx_timestamp()`, `es58x_rx_cmd_ret_u8()`, `es58x_rx_cmd_ret_u32()`, and `es58x_send_msg()`.

Important internal functions include CRC helpers, `es58x_check_rx_urb()`, `es58x_split_urb()`, `es58x_handle_incomplete_cmd()`, `es58x_split_urb_try_recovery()`, USB callbacks, `es58x_get_tx_urb()`, `es58x_submit_urb()`, `es58x_alloc_rx_urbs()`, `es58x_free_urbs()`, `es58x_open()`, `es58x_stop()`, `es58x_start_xmit()`, `es58x_set_mode()`, `es58x_init_netdev()`, `es58x_init_es58x_dev()`, `es58x_probe()`, and `es58x_disconnect()`.

## Control Flow
Probe initializes a devlink-backed `struct es58x_device`, parses product information, registers devlink, and creates one or two CAN netdevices. Opening the first channel allocates RX URBs and requests a device timestamp to calibrate hardware timestamps to kernel real time. Each open channel calls `open_candev()`, sends a variant enable command, increments `opened_channel_cnt`, and starts the queue. Closing disables the channel, resets echo FIFO state, closes the CAN device, flushes pending TX batches, decrements the open count, and frees URBs when the last channel closes.

RX callbacks validate USB status, split arbitrary URB payloads into one or more ES58x commands, buffer incomplete commands across URBs, skip ES581.4 heartbeat bytes, verify SOF, length, maximum command size, and CRC, then call the variant `handle_urb_cmd()`. Severe parse or handler errors increment RX errors on all channels and may detach netdevices and reset the device.

TX uses Byte Queue Limits and `netdev_xmit_more()` to batch multiple skbs into one URB. `es58x_start_xmit()` obtains or reuses a TX URB, prevents mixed classical CAN and CAN FD batches, delegates encoding to the variant `tx_can_msg()`, stores an echo skb at `tx_head & fifo_mask`, and commits the URB when batching should stop. Completion of echo messages later advances `tx_tail`, applies hardware timestamps, completes BQL bytes, updates stats, and wakes the queue when echo FIFO pressure falls.

## State And Persistence
There is no disk persistence. Device runtime state includes devlink private memory, USB endpoints, RX/TX anchors, idle TX URB count, product versions, timestamp calibration fields, a temporary timestamp array, open channel count, and a reassembly buffer. Per-net state in `struct es58x_priv` tracks CAN state, devlink port, pending TX URB, TX head/tail counters, batch count, batch CAN FD type, passive-error repetition count, and channel index.

## Dependencies And Integration Points
The core depends on Linux USB, SocketCAN, netdevice, BQL/DQL, CRC16, devlink, CAN hardware timestamping ops, ethtool timestamp reporting, and variant operator tables. It delegates protocol layout to `es581_4.c` and `es58x_fd.c`, and product metadata to `es58x_devlink.c`.

## Risks
The RX reassembly path is complex and must remain robust against split, concatenated, stale, malformed, and CRC-bad URBs. `es58x_split_urb_try_recovery()` intentionally scans for the next SOF after corruption, which can recover traffic but risks false-positive resynchronization if payload bytes mimic SOF. TX batching requires strict echo FIFO invariants; packet index recovery drops stale echo skbs to resynchronize. Bus-off handling avoids self-recovery to prevent races with SocketCAN restart, so changes here can easily introduce echo skb races. URB idle-count accounting must stay matched with anchor operations.

## Test Signals
Run probe/remove for all supported products, open/close one and multiple channels, RX split and concatenated command scenarios, CRC failure and recovery paths, timestamp calibration and hardware timestamp visibility, BQL behavior under bulk TX, mixed CAN/CAN FD batching on FD hardware, echo packet loss/reordering recovery, bus-off and restart, USB unplug during active TX/RX, devlink info visibility, and KASAN/KCSAN-style stress around URB anchor cleanup.
