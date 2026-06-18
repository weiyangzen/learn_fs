<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.c

## Purpose
This file is the USB transport, probe, runtime, and power/reset layer for the pureLiFi plfxlc driver. It matches supported USB IDs, allocates mac80211 hardware, uploads metadata, downloads firmware, configures radio and MAC address, manages RX URBs, schedules per-station TX queues, handles device FIFO/status messages, and implements disconnect, reset, suspend, and resume.

## Important APIs, Types, And Functions
The USB ID table matches pureLiFi X, XC, and XL devices. Public transport functions are `plfxlc_usb_init()`, `plfxlc_usb_release()`, `plfxlc_usb_init_hw()`, `plfxlc_usb_enable_rx()`, `plfxlc_usb_disable_rx()`, `plfxlc_usb_enable_tx()`, `plfxlc_usb_disable_tx()`, `plfxlc_usb_wreq()`, `plfxlc_usb_wreq_async()`, `plfxlc_send_packet_from_data_queue()`, `plfxlc_tx_urb_complete()`, and `plfxlc_speed()`.

Important internal functions include `rx_urb_complete()`, `alloc_rx_urb()`, `free_rx_urb()`, `__lf_x_usb_enable_rx()`, `__lf_x_usb_disable_rx()`, `get_usb_req()`, `slif_data_plane_sap_timer_callb()`, `sta_queue_cleanup_timer_callb()`, `probe()`, `disconnect()`, `pre_reset()`, `post_reset()`, `suspend()`, and `resume()`.

## Control Flow
Probe allocates `ieee80211_hw`, records `ez_usb`, reads MAC and serial, sets unit type to station, preinitializes permanent MAC, registers mac80211 hardware, downloads XL firmware or FPGA image based on USB ID, resets USB configuration, turns the radio on, sets rate 8, writes the MAC to firmware, enables RX/TX, initializes per-station queues and broadcast station, starts the retry and station-cleanup timers, initializes chip/mac hardware, and marks USB initialized.

RX enable allocates five coherent bulk-IN URBs and submits them. Completion validates device/initialization state, handles terminal URB errors, retries transient errors up to a counter, passes normal RX frames to `plfxlc_mac_rx()` when link is up, and interprets short status messages as FIFO-full, FIFO-not-full, connect, or disconnect events. RX URBs are resubmitted from the completion path.

TX scheduling is per station. `plfxlc_send_packet_from_data_queue()` scans station queues round-robin, skips disconnected or FIFO-full stations, dequeues one SKB, submits an async bulk OUT URB, and wakes mac80211 queues when backlog falls below the low threshold. TX completion hands status to `plfxlc_mac_tx_to_dev()`, sends another queued packet, and frees the URB.

Synchronous write requests build a `struct plf_usb_req` envelope, append FCS zeros and alignment padding, and send it over bulk OUT. Async writes send the caller's buffer directly over bulk OUT. Disconnect deletes timers, unregisters mac80211, disables RX/TX, resets the USB device to allow later firmware upload, and releases hardware. Reset and PM paths stop USB transport, remember running state, and optionally resume/restores settings.

## State And Persistence
`struct plfxlc_usb` persists interface pointers, RX/TX state, per-station queues, timers, current round-robin station index, RX enabled flag, initialized flag, previous running state, and link-up status. RX URBs own coherent buffers while enabled. TX station flags track connected, FIFO-full, and heartbeat state. Firmware and USB configuration persist until reset or disconnect.

## Dependencies And Integration Points
This file integrates Linux USB core, mac80211 registration/unregistration, firmware helpers, chip control, and MAC TX/RX helpers. It is the module init/exit owner through `usb_register()`/`usb_deregister()`.

## Risks
`rx_urb_complete()` increments `submitted_urbs` twice in the retry log path, which can shorten retry allowance. `get_plfxlc_usb()` dereferences the result of `plfxlc_intf_to_hw()` through `plfxlc_usb_to_mac(pl)` after checking `pl`, but `pl` is derived from `hw`; PM suspend calls `plfxlc_usb_to_mac(pl)` before verifying `pl` is non-NULL, creating a NULL-risk path if no hw is attached. Async TX URBs use SKB data buffers without anchoring the URB in `tx->submitted`, so lifetime correctness depends on completion and mac80211 teardown ordering. FIFO status names appear inverted in logs versus flag behavior. Probe registers hw before firmware download; failed firmware download must unregister/release cleanly.

## Test Signals
Test probe/disconnect for X, XC, and XL IDs, missing firmware, USB reset, suspend/resume, bulk IN/OUT error injection, RX URB allocation failure, FIFO full/not-full status, connect/disconnect status, station queue cleanup timer, TX retry timer, queue stop/wake, and module unload/reload. KASAN and USB fault injection are especially useful for URB/SKB lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/purelifi/plfxlc/usb.c -->
