# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb.c

## Purpose
This file is the USB bus driver for RSI 9113/9116 WLAN devices. It probes USB IDs, discovers bulk endpoints, initializes common RSI state, supplies USB host-interface operations, receives packets through URBs and an RX worker thread, performs vendor-control register access, loads firmware when needed, and resets/deinitializes hardware on disconnect.

## Important APIs, Types, and Functions
Important functions include `rsi_usb_card_write`, `rsi_write_multiple`, `rsi_find_bulk_in_and_out_endpoints`, `rsi_usb_reg_read`, `rsi_usb_reg_write`, `rsi_rx_done_handler`, `rsi_rx_urb_submit`, `rsi_usb_read_register_multiple`, `rsi_usb_write_register_multiple`, `rsi_usb_host_intf_write_pkt`, `rsi_usb_master_reg_read`, `rsi_usb_master_reg_write`, `rsi_usb_load_data_master_write`, `rsi_deinit_usb_interface`, `rsi_usb_init_rx`, `rsi_init_usb_interface`, `usb_ulp_read_write`, `rsi_reset_card`, `rsi_probe`, and `rsi_disconnect`. `usb_host_intf_ops` is the transport callback table.

## Control Flow
Probe creates the common adapter, initializes USB-private state, discovers WLAN and optional BT bulk endpoints, allocates a TX staging buffer, creates URBs and an RX thread, sets queue-status/timeout callbacks, determines device model, reads firmware status, loads firmware if not already running, and submits WLAN/BT RX URBs. RX URB completion validates length, queues the SKB to `dev->rx_q`, wakes `rsi_usb_rx_thread`, and resubmits the URB. TX packets route by RSI queue number to WLAN or BT endpoint and are written with bulk messages after adding USB headroom. Register and firmware loading use vendor control transfers in chunks. Disconnect detaches rfkill/mac80211/BT, kills URBs, resets the card through watchdog registers, frees RX/TX resources, and deinitializes common state.

## State and Persistence Behavior
USB-private state includes endpoint addresses/sizes, RX control blocks and URBs, RX queue, TX buffer, USB device pointer, write-failure flag, TX block size, and RX thread event/completion. The adapter records USB host ops, `RSI_HOST_INTF_USB`, block size, and debugfs entry count. Device state changes through vendor register writes, firmware image writes, TA hold/reset registers, and watchdog timers. USB PM callbacks currently return `-ENOSYS`.

## Dependencies and Integration Points
It depends on Linux USB core, `rsi_91x_main.c`, `rsi_91x_usb_ops.c` RX thread and queue-status helpers, common HAL firmware loading, optional BT coex, mac80211 detach/rfkill, and reset constants from `rsi_hal.h`.

## Risks
URB resubmission happens from completion context and must not leak or double-free SKBs on error. `rsi_usb_reg_read` writes `*value` before checking transfer status, so failed reads can expose stale control-buffer data. `rsi_usb_load_data_master_write` uses a fixed 256-byte stack buffer and assumes `block_size <= 256`. USB suspend/resume is unimplemented. Endpoint discovery assumes endpoint ordering maps WLAN first and BT second. Bulk writes serialize through a single TX buffer, so callers must preserve bus-level locking.

## Test Signals
Probe/remove for both USB product IDs, endpoint layouts with/without coex, firmware-already-loaded and firmware-load paths, URB completion/resubmit errors, RX queue overflow, WLAN/BT endpoint routing, vendor register read/write chunking, disconnect during active RX/TX, watchdog reset success/failure, and PM callback behavior should be exercised.
