# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.h

## Purpose
`es58x_fd.h` defines the USB wire protocol for ETAS ES582.1 and ES584.1 CAN FD devices. It provides channel counts, command type and command ID enums, controller mode bits, packed bit timing and channel configuration payloads, TX/RX/echo/error/ack payload layouts, and maximum URB command sizes.

## Important APIs, Types, And Functions
This header has no functions. Key constants include `ES582_1_NUM_CAN_CH`, `ES584_1_NUM_CAN_CH`, `ES58X_FD_NUM_CAN_CH`, `ES58X_FD_CHANNEL_IDX_OFFSET`, and bulk limits for TX, RX, and echo. Enums include `enum es58x_fd_cmd_type`, `enum es58x_fd_can_cmd_id`, `enum es58x_fd_dev_cmd_id`, and `enum es58x_fd_ctrlmode`.

Important packed structures are `struct es58x_fd_bittiming`, `struct es58x_fd_tx_conf_msg`, `struct es58x_fd_tx_can_msg`, `struct es58x_fd_rx_can_msg`, `struct es58x_fd_echo_msg`, `struct es58x_fd_rx_event_msg`, `struct es58x_fd_tx_ack_msg`, and `struct es58x_fd_urb_cmd`. Sizing macros include `ES58X_FD_CAN_CONF_LEN`, `ES58X_FD_CANFD_CONF_LEN`, `ES58X_FD_CAN_TX_LEN`, `ES58X_FD_CANFD_TX_LEN`, `ES58X_FD_CAN_RX_LEN`, `ES58X_FD_CANFD_RX_LEN`, `ES58X_FD_URB_CMD_HEADER_LEN`, `ES58X_FD_TX_URB_CMD_MAX_LEN`, and `ES58X_FD_RX_URB_CMD_MAX_LEN`.

## Control Flow
The command header includes SOF, command type, command ID, 0-based channel index, and message length. CAN and CANFD command types share many command IDs, while device-level commands carry timestamp replies. TX and RX CAN records are variable-sized because classic CAN uses DLC and up to eight bytes while CAN FD uses length and up to 64 bytes. The source adapter computes actual record lengths before appending or parsing records.

## State And Persistence
The header defines wire fields but stores no state. Runtime state includes packet indexes, timestamps, channel indexes, command return codes, TX free-entry counts, and CAN/CAN FD bit timing values after they are encoded into or decoded from these packed structures.

## Dependencies And Integration Points
It depends on Linux fixed-width types and CAN payload constants. The shared core includes this header in `union es58x_urb_cmd`, and `es58x_fd.c` uses its layouts to implement `es58x_fd_ops`. `ES58X_SIZEOF_URB_CMD()` from the core depends on the raw message and CRC field layout.

## Risks
Packed ABI structures are sensitive to layout changes. The `dlc`/`len` union in TX/RX records must be interpreted according to command type and flags. Controller mode bits include features that SocketCAN may not expose directly; unsupported bits should not be set casually. ES58x FD channel numbering is 0-based, unlike ES581.4.

## Test Signals
Compile and sparse-check packed layout usage, then verify CAN and CANFD command encoding, max URB size boundaries for 100-record batches, channel indexes for ES582.1 and ES584.1, and correct parsing of echo, event/error, timestamp, and TX acknowledgment records.
