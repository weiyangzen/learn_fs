# sources/distributed-fs/ceph-client/drivers/net/can/usb/ems_usb.c

## Purpose
`ems_usb.c` is a SocketCAN USB network driver for the EMS Dr. Thomas Wuensche CPC-USB/ARM7 adapter. It binds USB vendor/product `0x12d6:0x0444`, exposes one CAN netdevice, translates CPC protocol messages to classical CAN frames and CAN error frames, and programs SJA1000-compatible timing parameters over USB bulk control messages. The device clock is modeled as 8 MHz because the firmware expects SJA1000 bit timing values based on that clock even though the device uses a 16 MHz source internally.

## Important APIs, Types, And Functions
The central state object is `struct ems_usb`, whose first member is `struct can_priv` for SocketCAN compatibility. It owns the USB device, netdevice, RX/TX anchors, interrupt URB, coherent RX buffers, a synchronous command buffer, TX echo contexts, the active SJA1000 parameter message, and a cached device `free_slots` count. CPC wire messages are represented by `struct ems_cpc_msg` and nested payload types such as `struct cpc_can_msg`, `struct cpc_can_params`, `struct cpc_can_error`, and `struct cpc_can_err_counter`.

Key entry points are `ems_usb_probe()`, `ems_usb_disconnect()`, `ems_usb_open()`, `ems_usb_close()`, and `ems_usb_start_xmit()`. Protocol helpers include `ems_usb_command_msg()`, `ems_usb_write_mode()`, `ems_usb_control_cmd()`, `ems_usb_set_bittiming()`, `init_params_sja1000()`, `ems_usb_rx_can_msg()`, and `ems_usb_rx_err()`. USB callbacks are `ems_usb_read_bulk_callback()`, `ems_usb_write_bulk_callback()`, and `ems_usb_read_interrupt_callback()`.

## Control Flow
Probe allocates a CAN netdevice with `MAX_TX_URBS` echo slots, allocates interrupt and synchronous TX command buffers, initializes open SJA1000 acceptance filters, sends initial CAN parameters to the device, and registers the CAN device. Open first writes reset mode, calls `open_candev()`, submits up to ten bulk RX URBs, starts the interrupt URB, enables device notifications for CAN frames, state changes, and bus errors, then switches the controller to normal mode and starts the net queue.

RX bulk URBs may contain multiple CPC messages behind a four-byte header. `ems_usb_read_bulk_callback()` walks the advertised message count, validates message boundaries, dispatches CAN/RTR frames to `ems_usb_rx_can_msg()`, and dispatches state, bus error, and overrun messages to `ems_usb_rx_err()`. TX allocates a coherent bulk URB per skb, encodes standard/extended and RTR/data frames into CPC command messages, reserves a free echo context, anchors and submits the URB, and stops the net queue if host TX URBs or device free slots fall below thresholds. The interrupt endpoint refreshes `free_slots` and wakes the queue once the device has recovered enough capacity.

## State And Persistence
There is no persistent disk state. Runtime state is in `struct ems_usb`: active URB anchors, echo skb slots, current SJA1000 mode/timing parameters, and `free_slots`. CAN state is updated from SJA1000 status bits and SocketCAN restart requests. `unlink_all_urbs()` kills RX, TX, and interrupt activity and resets echo context indices.

## Dependencies And Integration Points
The driver integrates with Linux USB core, SocketCAN (`alloc_candev()`, `open_candev()`, `register_candev()`, echo skb helpers, CAN error skb helpers), netdevice ops, ethtool timestamp info, and SJA1000-compatible bit timing. USB endpoint numbers are hard-coded to bulk endpoint 2 and interrupt endpoint 1, matching the CPC-USB firmware protocol.

## Risks
RX parsing depends on correct CPC message counts and lengths; malformed packets are logged and parsing stops for that URB. TX context selection is linear and assumes queue stopping prevents exhaustion. `ems_usb_control_cmd()` sets `cmd.length = CPC_MSG_HEADER_LEN + 1`, which is unusual because the lower command helper also adds the CPC header length; this matches existing protocol expectations but is a maintenance trap. Error-state handling maps a non-bus-off/non-warning state to `CAN_STATE_ERROR_ACTIVE` while incrementing `error_passive`, which looks suspicious and should be regression-tested before modification. Resource cleanup frees coherent RX buffers by slots even if fewer URBs were submitted, relying on zeroed private memory for unused entries.

## Test Signals
Useful tests include probe/remove with the device attached, `ip link set canX type can bitrate ... up/down`, standard, extended, and RTR frame loopback, TX queue stop/wake under high load, unplug during RX/TX, bus-off and restart behavior, bus error reporting with `berr-reporting`, malformed short RX URB injection if USB fault tooling is available, and suspend-like disconnect paths that exercise anchored URB cleanup.
