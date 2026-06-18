# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.h

## Purpose
`es58x_core.h` is the common contract for the ETAS ES58x driver. It declares hardware-independent enums, shared state structures, variant parameter/operator tables, command-size helpers, channel lookup helpers, CAN ID/flag conversion helpers, and cross-file function prototypes.

## Important APIs, Types, And Functions
Important constants include `ES58X_RX_URBS_MAX`, `ES58X_TX_URBS_MAX`, `ES58X_NUM_CAN_CH_MAX`, `ES58X_CHANNEL_IDX_NA`, `ES58X_CONSECUTIVE_ERR_PASSIVE_MAX`, and `ES58X_HEARTBEAT`. Shared enums cover device quirks (`enum es58x_driver_info`), echo mode, physical layer, samples per bit, sync edge, CAN frame flags, protocol errors, bus events, u8/u32 command return codes, and return-code categories.

The main structures are `union es58x_urb_cmd`, `struct es58x_priv`, `struct es58x_parameters`, `struct es58x_operators`, `struct es58x_sw_version`, `struct es58x_hw_revision`, and `struct es58x_device`. Inline/macros include `es58x_sizeof_es58x_device()`, `es58x_check_msg_len()`, `es58x_check_msg_max_len()`, `es58x_msg_num_element()`, `es58x_priv()`, `ES58X_SIZEOF_URB_CMD()`, `es58x_get_urb_cmd_len()`, `es58x_get_netdev()`, `es58x_get_raw_can_id()`, and `es58x_get_flags()`.

## Control Flow
The header shapes how the core and variants interact. `struct es58x_parameters` supplies static hardware limits and CAN capabilities. `struct es58x_operators` is the variant vtable used by the core for message length, command dispatch, header fill, TX encoding, channel enable/disable, reset, and timestamp request. Size-check macros are used by variant receive paths before they interpret packed USB payloads.

## State And Persistence
The header declares runtime state but does not allocate it. `struct es58x_device` persists for the USB interface lifetime and contains endpoint/anchor state, product version fields, timestamp calibration, temporary echo timestamp storage, open channel count, and the flexible RX reassembly buffer. `struct es58x_priv` persists per netdevice and tracks TX FIFO counters, pending TX URB, CAN state, and channel index.

## Dependencies And Integration Points
The header bridges Linux CAN, CAN dev, netdevice, USB, and devlink APIs. It includes both variant headers, which makes the shared `union es58x_urb_cmd` able to represent all supported hardware commands. Function prototypes connect `es58x_core.c`, `es58x_devlink.c`, `es581_4.c`, and `es58x_fd.c`.

## Risks
This header is ABI-sensitive inside the driver: changes to packed command unions, max sizes, FIFO masks, or helper semantics affect all variants. The mutual inclusion pattern between the core and variant headers requires care to avoid circular type assumptions. `es58x_get_flags()` casts skb data to `struct canfd_frame` for both CAN and CAN FD paths, relying on SocketCAN layout compatibility. `es58x_get_netdev()` silently applies variant-specific channel offsets supplied by callers; wrong offsets misroute channels.

## Test Signals
Compile all ETAS objects together, run sparse/endian checks around packed and unaligned fields, exercise both variant operator tables, verify command size checks reject short/oversized payloads, and test CAN/CAN FD flag conversion for EFF, RTR, BRS, ESI, and FD data frames.
