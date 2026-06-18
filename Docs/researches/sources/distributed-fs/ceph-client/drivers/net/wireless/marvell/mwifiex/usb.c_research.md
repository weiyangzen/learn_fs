# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/usb.c

## Purpose
`usb.c` is the mwifiex USB bus driver. It binds supported Marvell/NXP USB Wi-Fi IDs, discovers endpoints, downloads firmware when needed, allocates and submits RX/TX URBs, demultiplexes command/event/data packets, implements suspend/resume/disconnect/coredump hooks, supports multi-channel USB port resync, provides bus `if_ops`, and optionally aggregates TX data packets for USB efficiency.

## Important APIs, Types, and Functions
Important local functions include `mwifiex_usb_probe`, `mwifiex_usb_suspend`, `mwifiex_usb_resume`, `mwifiex_usb_disconnect`, `mwifiex_usb_recv`, `mwifiex_usb_rx_complete`, `mwifiex_usb_tx_complete`, `mwifiex_usb_submit_rx_urb`, `mwifiex_usb_host_to_card`, TX aggregation helpers, `mwifiex_usb_rx_init`, `mwifiex_usb_tx_init`, `mwifiex_register_dev`, `mwifiex_unregister_dev`, `mwifiex_prog_fw_w_helper`, and `mwifiex_usb_dnld_fw`. The exported integration object is `usb_ops`, a `struct mwifiex_if_ops` installed via `mwifiex_add_card`.

## Control Flow and Integration
Probe allocates `struct usb_card_rec`, determines boot state from PID, scans endpoint descriptors for command/event and data IN/OUT endpoints, validates minimal firmware-download endpoints, stores interface data, and calls `mwifiex_add_card`. Firmware download uses synchronous bulk messages on the command endpoint, sends a winner probe, streams firmware blocks with sequence numbers, retries on transfer/CRC failures, and expects the device to re-enumerate or change boot state before RX/TX init proceeds.

RX URBs complete in `mwifiex_usb_rx_complete`. Successful command/event endpoint packets are passed to `mwifiex_usb_recv`, which strips the interface header, attaches command responses to `adapter->curr_cmd`, stores event cause/body/SKB, or queues data SKBs on `adapter->rx_data_q`. It schedules main work and resubmits command URBs only after command/event completion; data URBs are resubmitted immediately unless `rx_pending` is high.

TX goes through `mwifiex_usb_host_to_card`. Command packets use the single command URB. Data packets select a `usb_tx_data_port`, respect `tx_data_urb_pending`, optionally aggregate packets into an aligned aggregate SKB with MWIFIEX_TYPE_AGGR_DATA_V2 headers and a timer-bound hold window, and submit URBs. TX completion clears command/data sent flags, completes data SKBs, unblocks ports, handles multi-channel resync, and schedules main work.

Suspend waits for firmware load, enables host sleep, sets `MWIFIEX_IS_SUSPENDED`, and kills URBs. Resume clears suspension, resubmits RX URBs, and cancels host sleep asynchronously. Disconnect deauthenticates, sends firmware shutdown when appropriate, and removes the card.

## State and Persistence Behavior
State lives in `usb_card_rec`: endpoint numbers/types, boot state, URB contexts, pending URB atomics, command/data SKBs, multi-channel port state, aggregation queues/timers, and firmware completion. Adapter-level persistent effects include `fw_name`, `tx_buf_size`, `ext_scan`, `usb_mc_status`, `usb_mc_setup`, `data_sent`, `cmd_sent`, event/command flags, `rx_pending`, work flags, and power-save flags.

## Dependencies and Risks
Dependencies include Linux USB core, firmware loader via common mwifiex core, `mwifiex_if_ops`, SKB queue APIs, timers, and power-management helpers in station ioctl/TX. Risks include asynchronous URB lifetime and SKB ownership, endpoint descriptor assumptions for ready devices, aggregation counter/timer races, suspend/disconnect completion ordering, high RX pending leaving data URB contexts without SKBs until resubmission, and firmware-download retry/boot-state ambiguity.

## Test Signals
Test probe on each PID, firmware download and re-enumeration, command/event/data RX demux, high RX pending throttling and `submit_rem_rx_urbs`, data TX with and without aggregation, URB submit failure, port blocking/resync for multi-channel, suspend/resume host sleep, disconnect during in-flight URBs, coredump trigger, and module firmware declarations.
