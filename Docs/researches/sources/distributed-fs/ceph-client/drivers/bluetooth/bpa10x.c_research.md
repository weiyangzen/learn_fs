# Research: sources/distributed-fs/ceph-client/drivers/bluetooth/bpa10x.c

## Purpose

`bpa10x.c` is the USB HCI driver for Digianswer/Tektronix BPA 100/105 Bluetooth sniffer devices. It registers a USB-backed HCI device, submits interrupt and bulk RX URBs, sends HCI packets over vendor control or bulk transfers, and supports a diagnostic/sniffer mode command.

## Important APIs, Types, And Functions

`struct bpa10x_data` stores the HCI device, USB device, TX/RX URB anchors, two receive reassembly skbs, and an embedded `struct hci_uart` used with H4 receive parsing helpers. `bpa10x_recv_pkts` declares H4 packet descriptors for ACL, SCO, events, and vendor diagnostic packets. `bpa10x_open`, `bpa10x_close`, `bpa10x_flush`, `bpa10x_setup`, `bpa10x_send_frame`, and `bpa10x_set_diag` are HCI callbacks. USB binding is handled by `bpa10x_probe` and `bpa10x_disconnect`.

## Control Flow

Probe accepts only interface 0, allocates state and an HCI device, initializes USB anchors, attaches HCI callbacks, sets `HCI_QUIRK_RESET_ON_CLOSE`, registers the device, and stores interface data. Opening submits one interrupt RX URB on endpoint `0x81` and one bulk RX URB on endpoint `0x82`. RX completion selects one of two reassembly slots based on pipe type, feeds bytes into `h4_recv_buf`, handles corrupted packets by incrementing `err_rx`, then reanchors and resubmits the URB.

Sending prepends the HCI packet type. Command packets are sent as vendor control requests on endpoint zero with a dynamically allocated setup packet. ACL and SCO packets go over bulk OUT endpoint `0x02`. Completion updates TX stats, frees the setup packet, and frees the skb. Setup sends vendor command `0xfc0e` with request byte `0x07` to read a revision string and stores it as firmware info. Diagnostic mode sends the same opcode with enable state.

## State And Persistence

Runtime state is anchored URBs plus RX reassembly skbs. `tx_anchor` and `rx_anchor` allow close/flush to kill outstanding URBs. No firmware is loaded and no persistent state is stored by the driver; diagnostic mode is a controller runtime setting.

## Dependencies And Integration Points

The driver depends on USB core, Bluetooth HCI core, `hci_uart.h` H4 parsing helpers, and skbuff APIs. Kconfig requires `BT_HCIUART` and USB and selects `BT_HCIUART_H4`, reflecting its use of H4 receive parsing despite being a USB transport.

## Risks

URB lifetime is central. Completion frees skbs and setup packets, while anchors control cancellation; changes must avoid use-after-free during disconnect. RX resubmission occurs from completion context with `GFP_ATOMIC`, so allocation and error paths must stay nonblocking. Command send failure frees setup packets only in the error path; completion handles the successful path. The driver uses fixed endpoint addresses and a vendor command contract specific to these sniffer devices.

## Test Signals

Signals include successful HCI registration, open submitting both RX URBs, revision string logging from setup, command/ACL/SCO TX stats, diagnostic mode toggling while running, clean close/flush/unplug behavior, and corrupted H4 packet error handling.
