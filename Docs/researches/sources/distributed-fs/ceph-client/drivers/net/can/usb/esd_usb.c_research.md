# sources/distributed-fs/ceph-client/drivers/net/can/usb/esd_usb.c

## Purpose
`esd_usb.c` is a SocketCAN USB driver for esd electronics CAN-USB/2, CAN-USB/Micro, and CAN-USB/3 adapters. It supports up to two CAN nets per USB device, classical CAN on older products, and CAN FD on CAN-USB/3. It translates esd USB command records to CAN/CAN FD skbs, configures bit timing, configures ID acceptance filters, and exposes firmware, hardware, and net count sysfs attributes.

## Important APIs, Types, And Functions
`struct esd_usb` is the USB-device-level object with the shared RX anchor, endpoints, device version, net count, disconnect flag, and RX buffers. `struct esd_usb_net_priv` is the per-channel SocketCAN private state with `struct can_priv`, TX job counter, TX echo contexts, net index, previous bus state, and cached berr counters. The packed protocol union `union esd_usb_msg` covers version, RX, TX, TX done, filter, and baudrate messages.

Core paths include `esd_usb_probe()`, `esd_usb_probe_one_net()`, `esd_usb_disconnect()`, `esd_usb_open()`, `esd_usb_close()`, `esd_usb_start_xmit()`, `esd_usb_read_bulk_callback()`, `esd_usb_tx_done_msg()`, `esd_usb_rx_can_msg()`, `esd_usb_rx_event()`, `esd_usb_2_set_bittiming()`, `esd_usb_3_set_bittiming()`, and `esd_usb_get_berr_counter()`.

## Control Flow
Probe finds bulk endpoints, allocates `struct esd_usb`, sends a version command synchronously, waits for the version reply, records the number of nets and version, creates sysfs attributes, and registers one CAN netdevice per reported net. Per-net probe selects clock, timing constants, ctrlmode support, and bit timing callbacks based on the USB product ID.

Open calls `open_candev()`, sends an IDADD filter enabling all 11-bit and 29-bit IDs, lazily sets up shared RX URBs once, marks the channel active, and starts the net queue. RX bulk callbacks iterate variable-sized messages using `hdr.len` in 32-bit words. CAN RX records route by `rx.net`, allocate either CAN or CAN FD skbs, apply EFF/RTR/BRS/ESI flags, copy payload, and update RX stats. Event records with `ESD_USB_EVENT` and ID `ESD_USB_EV_CAN_ERROR_EXT` update cached error counters, optionally suppress repeated events when berr reporting is disabled, call `can_change_state()` for state transitions, and emit protocol error skbs for repeated diagnostic errors.

TX allocates one coherent `union esd_usb_msg`, encodes CAN or CAN FD payload, sets a nonzero handle with the echo index, stores an echo skb, increments `active_tx_jobs`, stops the queue when all contexts are in flight, and submits a bulk URB. Completion of the USB write only frees the DMA buffer and updates the software trans timestamp; actual TX success/error accounting happens when a device TX_DONE message returns.

## State And Persistence
No state is persisted outside the kernel. Device-level runtime state includes RX URB initialization, USB disconnect status, version, endpoint pipes, and the per-net pointer table. Per-net state includes active TX jobs, echo context ownership, old controller state, and berr counters. Close disables ID filters, sends a no-baudrate/reset command unless in USB disconnect, sets CAN state stopped, stops the queue, and closes the CAN device. Full URB cleanup happens in disconnect.

## Dependencies And Integration Points
This file uses USB core synchronous bulk messages for setup and asynchronous bulk URBs for data, SocketCAN netdevice APIs, CAN FD helpers, CAN error frame helpers, ethtool timestamp fallback, and sysfs `DEVICE_ATTR_RO` attributes. Product IDs drive feature selection: CAN-USB/3 gets FD support, 80 MHz clock, canonical nominal/data timing, and automatic TDC mode; CAN-USB/Micro and CAN-USB/2 use older BTR encoding and 36/60 MHz clocks.

## Risks
The driver trusts the device-reported `net_count` when probing per-net devices; invalid values above `ESD_USB_MAX_NETS` would be hazardous if firmware misbehaves. RX parsing advances by `hdr.len * sizeof(u32)` and only checks for overflow after dispatch, so zero-length messages could stall if ever emitted. TX completion indexes use `hnd & (ESD_USB_MAX_TX_URBS - 1)`, so handle integrity matters. Sysfs attribute creation failures are logged but not fatal and are not unwound individually. `unlink_all_urbs()` frees all RX coherent slots even if only a subset was allocated.

## Test Signals
Test with all three product families where possible: net count and sysfs values after probe, classical CAN standard/extended/RTR traffic, CAN FD with and without BRS on CAN-USB/3, listen-only and triple-sampling modes, ID filter enable/disable on open/close, TX_DONE success and error accounting, berr-counter reads, state transitions through warning/passive/bus-off, USB unplug during open channels, and repeated open/close across both channels sharing the same RX URB pool.
