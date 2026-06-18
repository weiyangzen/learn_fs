# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bfusb.c

## Purpose

`bfusb.c` is the HCI USB transport driver for AVM BlueFRITZ! USB Bluetooth devices. It loads device firmware, registers an HCI device, fragments outgoing HCI frames into the device block format, reassembles incoming block streams, and manages USB bulk URBs.

## Important APIs, Types, And Functions

`struct bfusb_data` stores the HCI device, state bits, USB device and endpoint addresses, bulk packet size, an rwlock, TX queue, RX reassembly skb, and pending/completed URB skb queues. `bfusb_data_scb` stores an URB pointer in skb control data. TX flow is handled by `bfusb_send_frame`, `bfusb_tx_wakeup`, `bfusb_send_bulk`, and `bfusb_tx_complete`. RX flow is handled by `bfusb_rx_submit`, `bfusb_rx_complete`, and `bfusb_recv_block`. Firmware loading is in `bfusb_load_firmware`; USB binding and HCI registration are in `bfusb_probe` and `bfusb_disconnect`.

## Control Flow

Probe checks for at least two endpoints, records endpoint addresses, initializes queues and locks, requests `bfubase.frm`, and calls `bfusb_load_firmware`. Firmware loading switches the device to loading configuration 1, streams firmware blocks over bulk OUT, sends a zero-length bulk request, then switches to running configuration 2 and resets toggles. After firmware load, the driver allocates an HCI device with `HCI_USB` bus, installs callbacks, sets `HCI_QUIRK_BROKEN_LOCAL_COMMANDS`, and registers it.

Opening the HCI device submits two bulk RX URBs. Incoming URBs are parsed as BFUSB blocks with headers, start/continuation/end flags, and payload lengths; valid completed HCI frames are handed to `hci_recv_frame`. Sending prepends the HCI packet type, wraps data into up to 256-byte BFUSB blocks, adds a short terminator block if the resulting transfer is a multiple of bulk max packet size, queues it, and pumps up to two concurrent bulk TX URBs.

## State And Persistence

Runtime state is queue-based and volatile. `pending_tx` limits concurrent TX URBs. `pending_q` and `completed_q` recycle URBs using skb control blocks. `reassembly` holds partially received HCI frames across URB completions. Firmware load changes device configuration but the driver stores no persistent firmware state after probe.

## Dependencies And Integration Points

The driver depends on USB, firmware loader, skbuff APIs, Bluetooth HCI core, and module USB-driver registration. It is enabled by `BT_HCIBFUSB` and declares `bfubase.frm` as required firmware. HCI integration is through `hci_alloc_dev`, `hci_register_dev`, `hci_recv_frame`, stats counters, and callback hooks.

## Risks

The custom block parser is a high-risk area: malformed headers, payload lengths extending past the URB buffer, unexpected start/continuation flags, and missing packet-type handling can corrupt reassembly or leak skbs if changed carelessly. Locking uses an rwlock around queue and URB state; callbacks can run in atomic context. `bfusb_disconnect` assumes `usb_get_intfdata` returns valid data, so probe failure paths must not leave partial interface data. Firmware loading uses fixed configuration numbers and endpoint assumptions.

## Test Signals

Signals include successful firmware load, HCI registration, open/close cycles without URB leaks, TX stats increasing for command/ACL/SCO frames, RX reassembly of split frames, error counters on malformed blocks, clean unplug during active RX/TX, and correct behavior when firmware is missing.
