<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-usb.c

Purpose: implements DMTF DSP0283 MCTP-over-USB as a USB class driver that registers an ARPHRD_MCTP netdev for matching MCTP USB interfaces.

Important APIs/types/functions: `struct mctp_usb` stores the USB device/interface, endpoint addresses, netdev, one TX URB, one RX URB, stopped flag, and delayed RX retry work. Key functions are `mctp_usb_probe`, `mctp_usb_start_xmit`, `mctp_usb_out_complete`, `mctp_usb_rx_queue`, `mctp_usb_in_complete`, `mctp_usb_open`, `mctp_usb_stop`, and `mctp_usb_disconnect`.

Control flow: probe finds bulk IN/OUT endpoints, allocates netdev and URBs, initializes retry work, and registers the MCTP netdev. Opening starts TX and queues the first RX URB. TX prepends `struct mctp_usb_hdr`, stops the queue, submits the bulk OUT URB, and wakes the queue on successful completion. RX completion validates one or more DMTF packets in the USB transfer, clones/trims skbs for packed frames, injects MCTP packets, and requeues RX.

State and persistence: state is runtime-only in URBs, skbs, delayed work, and the stopped flag. Stop kills both URBs and cancels retry work; disconnect unregisters and frees objects. Per-CPU dynamic stats are enabled.

Dependencies/integration: depends on USB class matching via `USB_INTERFACE_INFO(USB_CLASS_MCTP, 0, 1)`, Linux USB bulk URBs, MCTP netdev registration with `MCTP_PHYS_BINDING_USB`, and `linux/usb/mctp-usb.h` constants.

Risks and test signals: risks include packed-frame parsing bugs, RX retry after stop/disconnect, TX queue stuck after URB errors, and header length truncation because packet length is stored in `u8`. Tests should cover short/invalid IDs, multiple packets per transfer, open/stop cycles, allocation failure retry, and unplug during active URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mctp/mctp-usb.c -->
