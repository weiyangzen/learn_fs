# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.c

## Purpose
Implements the shared rtlwifi USB transport layer. It provides synchronous vendor control-message register I/O, discovers endpoints, initializes USB TX/RX queues and URBs, moves received bulk data into mac80211, submits transmitted skbs as bulk OUT URBs, and provides generic probe/disconnect glue for USB rtlwifi chip drivers.

## Important APIs, Types, And Functions
Exported entry points are `rtl_usb_probe` and `rtl_usb_disconnect`. Core helpers include `_usbctrl_vendorreq_sync`, `_usb_read_sync`, `_usb_write_sync`, `_usb_write_chunk_sync`, `_rtl_usb_io_handler_init`, `_rtl_usb_init`, `rtl_usb_init_sw`, `_rtl_prep_rx_urb`, `_rtl_rx_completed`, `_rtl_rx_work`, `_rtl_usb_rx_process_noagg`, `_rtl_usb_receive`, `rtl_usb_start`, `rtl_usb_stop`, `_rtl_usb_cleanup_rx`, `_rtl_usb_cleanup_tx`, `_rtl_usb_tx_preprocess`, `_rtl_usb_transmit`, `_rtl_tx_complete`, `_usb_tx_post`, and `rtl_fill_h2c_cmd_work_callback`.

## Control Flow
Probe allocates `ieee80211_hw` with USB private space, allocates a small synchronized control-transfer data ring, initializes locks/work items/completions, binds `rtl_hal_cfg` and `rtl_usb_ops`, installs USB register I/O callbacks, reads chip/eeprom data, discovers endpoints, initializes TX/RX transport state, initializes mac80211 core and chip software variables, then registers the hardware. Adapter start calls chip `hw_init`, initializes RX config, marks USB started, marks HAL started, and submits RX URBs. RX completion validates length and queue depth, allocates an skb with radiotap/alignment reserve, copies the coherent buffer, queues it, schedules a tasklet, and resubmits the URB. The tasklet parses descriptors through chip `query_rx_desc`, updates stats/LED/beacon state, and passes valid frames to mac80211. TX maps mac80211 queues to hardware queues, applies power-save/action/stat preprocessing, asks the chip to fill a TX descriptor, builds a bulk URB, and reports completion status back to mac80211. Disconnect waits for firmware loading, unregisters mac80211 if needed, stops/deinitializes transport/core/chip state, releases I/O, and frees `ieee80211_hw`.

## State And Persistence
State lives in `struct rtl_usb`, `struct rtl_usb_priv`, `rtlpriv->usb_data`, USB anchors for submitted and cleanup URBs, TX skb queues, RX skb queue, tasklets, work items, endpoint maps, interrupt masks, and USB/HAL start-stop flags. No durable persistence exists.

## Dependencies And Integration Points
Depends on the Linux USB core, mac80211, skbuff APIs, rtlwifi core/base/power-save code, chip-specific `rtl_hal_cfg`, chip `usb_interface_cfg`, firmware common address ranges, and shared LED/action/beacon/stat helpers. USB chip drivers such as rtl8192cu and rtl8192du call `rtl_usb_probe` and `rtl_usb_disconnect`.

## Risks And Edge Cases
Vendor register I/O uses a shared rotating `usb_data` buffer protected only for allocation of the slot; the USB control transfer then occurs after unlocking, so concurrent accesses rely on enough ring slots and no immediate reuse. Firmware download writes are not retried in the firmware address range. RX aggregation path logs unsupported after processing, and `_rtl_usb_rx_process_agg` does not itself submit to mac80211. `_rtl_tx_complete` returns without freeing/reporting the skb if USB is stopped, relying on broader teardown to own cleanup. Cleanup reports queued TX skbs as ACKed even though they were never transmitted. Endpoint discovery assumes the first bulk-IN endpoint is the main RX endpoint.

## Test Signals
USB probe/disconnect loops, firmware load/unload races, suspend-like stop/start, high-speed and full-speed devices, endpoint map validation, control transfer timeout injection, RX queue saturation, short RX packet handling, TX URB submission failures, unplug during active traffic, and mac80211 registration failures are key tests. Runtime signals include no leaked URBs/skbs, stable register I/O, correct RX status delivery, and TX status completion under load.
