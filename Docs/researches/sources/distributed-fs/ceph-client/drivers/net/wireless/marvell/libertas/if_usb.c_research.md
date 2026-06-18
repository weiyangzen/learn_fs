# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_usb.c

## Purpose
Implements the USB transport for full-firmware Libertas USB devices. It enumerates endpoints, downloads firmware over bulk endpoints, translates USB message types into Libertas command/data/event handling, manages URBs, and supplies suspend/resume hooks.

## Important APIs And Functions
`if_usb_probe()` allocates `struct if_usb_card`, discovers bulk endpoints, allocates URBs and output buffer, creates the Libertas card, and starts async firmware loading through `lbs_get_firmware_async()`. `if_usb_prog_firmware()` validates firmware format, issues boot commands, drives block download, waits on `fw_wq`, then starts the card and configures wake support. `if_usb_receive_fwload()` handles boot responses, CRC acknowledgements, and firmware-ready indications. Normal runtime uses `if_usb_receive()`, `process_cmdtypedata()`, `process_cmdrequest()`, `if_usb_host_to_card()`, `usb_tx_block()`, and `if_usb_submit_rx_urb()`.

## Control Flow And State
Firmware loading is a staged URB state machine using `bootcmdresp`, `CRC_OK`, `fwseqnum`, `totalbytes`, `fwlastblksent`, `fwfinalblk`, `fwdnldover`, `fw_timeout`, and `fw_wq`. Normal receive URBs parse a 4-byte message header: data goes to `lbs_process_rxed_packet()`, requests become command responses, and indications become events or TX feedback. TX is limited by the `tx_submitted` anchor so only one pending bulk TX is allowed. `surprise_removed` gates TX and wakes firmware waits on disconnect.

## Dependencies And Integration
Depends on Linux USB, firmware loader, optional OLPC EC reset/wakeup hooks, and Libertas core APIs. It sets `priv->hw_host_to_card`, optionally `priv->reset_card`, configures Boot2 version, wake GPIO/gap, host sleep, and firmware wake method.

## Risks And Test Signals
Risks include firmware download retry loops, static `reset_count`, shared `ep_out_buf` reuse, URB lifetime during disconnect, invalid length handling, and unsupported wake methods disabling power save. Test signals include endpoint discovery, firmware format validation, boot command response handling, CRC retry, firmware-ready event, command response delivery, data RX, indication/TX feedback, disconnect cleanup, and suspend/resume URB re-submission.
