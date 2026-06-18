# Research: subset-b-004842

Grouped research for Marvell Libertas and Libertas thinfirm wireless driver files under `sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/host.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/host.h

## Purpose
Defines the full-firmware Libertas host/firmware ABI: command ids, return-command conventions, action constants, event codes, packet descriptors, TLV structures, and packed command payloads. It is the common contract used by the core command path, mesh support, and SDIO/SPI/USB transports when building requests and parsing firmware responses.

## Important APIs, Types, And Constants
Important constants include `CMD_RET()`, `CMD_*` command ids, `CMD_ACT_*` actions, power-save actions, SNMP MIB oids, mesh access/config enums, and firmware event ids such as `MACREG_INT_CODE_FIRMWARE_READY`. `struct txpd` and `struct rxpd` are the data-plane descriptors placed before transmitted and received payloads. `struct cmd_header` is the common command header used by all command payloads. The many `cmd_ds_*` packed structs represent firmware commands for scan, association, MAC control, multicast, sleep, power, radio, EEPROM, key material, mesh, forwarding table, wake-on-LAN, and hardware specification.

## Control Flow And State
This header has no executable control flow, but it drives runtime dispatch: transport drivers identify command/data/event packets, core code fills `cmd_header` and command-specific structs, and response paths validate return ids against `CMD_RET(command)`. Fields are explicitly little-endian or big-endian where the firmware ABI requires it.

## Dependencies And Integration
Includes `types.h` and `defs.h`, and depends on Linux 802.11/Ethernet definitions through those headers. It is consumed by `main.c`, `cmd.c`, `rx.c`, `tx.c`, `mesh.c`, and bus-specific files. The packed layout is firmware-visible and should be treated as a binary interface.

## Risks And Test Signals
Primary risks are ABI drift, endian mistakes, variable-length array misuse, and accidental changes to packed structs such as `adhoc_bssdesc`, which explicitly forbids adding fields. Test signals include successful firmware `GET_HW_SPEC`, association/scan command responses, valid RX/TX descriptor parsing, mesh start/stop behavior, and suspend/resume power commands across firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.c

## Purpose
Implements the SDIO transport for full-firmware Libertas devices, including model detection, firmware/helper download, SDIO register access, command/data/event upload handling, host-to-card queuing, runtime power handling, system suspend/resume, and registration as an `sdio_driver`.

## Important APIs And Functions
`if_sdio_probe()` identifies 8385/8686/8688 models from card info, allocates `struct if_sdio_card`, wires Libertas callbacks into `lbs_private`, and powers on the device. `if_sdio_power_on()`, `if_sdio_prog_firmware()`, `if_sdio_prog_helper()`, `if_sdio_prog_real()`, and `if_sdio_finish_power_on()` perform enablement, firmware status detection, async firmware request, and post-firmware Libertas startup. `if_sdio_interrupt()` handles download acknowledgements and upload interrupts. `if_sdio_card_to_host()` dispatches uploaded packets to `if_sdio_handle_cmd()`, `if_sdio_handle_data()`, or `if_sdio_handle_event()`. `if_sdio_host_to_card()` queues outbound packets for `if_sdio_host_to_card_worker()`.

## Control Flow And State
The driver serializes outbound SDIO writes through a private workqueue and `card->packets`, protected by `card->lock`. IRQ handling reads/clears interrupt cause bits, signals `lbs_host_to_card_done()` on download completion, and pulls one uploaded packet. Power state flows through `priv->fw_ready`, `card->started`, runtime PM reference counts, and `pwron_waitq`. SD8688 removal is special-cased with `user_rmmod` so module unload sends `CMD_FUNC_SHUTDOWN` while surprise card removal does not.

## Dependencies And Integration
Depends on MMC/SDIO core, Linux firmware loading, runtime PM, and Libertas core APIs such as `lbs_add_card()`, `lbs_start_card()`, `lbs_process_rxed_packet()`, command helpers, and power hooks. Firmware names are declared through `MODULE_FIRMWARE` and selected from `fw_table`.

## Risks And Test Signals
Risks include one-transaction transfer requirements, block-size alignment bugs in host controllers, races between IRQ, reset work, and removal, and wait loops around firmware status. Tests should exercise cold firmware load, already-loaded firmware, RX command/data/event paths, SD8688 FUNC_INIT/FUNC_SHUTDOWN, runtime PM power-save/restore, suspend with and without Wake-on-WLAN, and reset-card recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.h

## Purpose
Defines SDIO register offsets, interrupt bit masks, status bits, firmware status values, RX length/unit registers, event register location, block size, and deep-sleep wake register bits used by `if_sdio.c`.

## Important Definitions
Key registers include `IF_SDIO_IOPORT`, host interrupt mask/status registers, `IF_SDIO_RD_BASE`, `IF_SDIO_STATUS`, scratch/status registers, `IF_SDIO_RX_LEN`, `IF_SDIO_RX_UNIT`, and `IF_SDIO_EVENT`. Important status bits are `IF_SDIO_IO_RDY`, `IF_SDIO_DL_RDY`, and `IF_SDIO_FIRMWARE_OK`. `IF_SDIO_BLOCK_SIZE` is the normal post-firmware transfer block size. `CONFIGURATION_REG` and `HOST_POWER_UP` support deep-sleep wake.

## Control Flow And State
No runtime code is present. The constants drive state polling in firmware download, packet-length discovery, interrupt masking/clearing, and deep-sleep transitions.

## Dependencies And Integration
Included only by the SDIO transport. It encodes hardware ABI values and must remain consistent with Marvell SDIO firmware expectations.

## Risks And Test Signals
Risks are incorrect register offsets or bit masks causing firmware load hangs, missed interrupts, or invalid packet lengths. Test signals include successful `IF_SDIO_FIRMWARE_OK` polling, upload/download interrupts, RX length decoding for old and newer models, and wake from deep sleep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.c

## Purpose
Implements the SPI transport for Marvell Libertas WLAN cards. It initializes the SPI interface unit, loads helper and main firmware, handles firmware command/data/event movement through SPU registers, provides Libertas host-to-card callbacks, and registers a `spi_driver`.

## Important APIs And Functions
Low-level SPU helpers are `spu_write()`, `spu_read()`, `spu_read_u16()`, `spu_read_u32()`, `spu_wait_for_u16()`, `spu_wait_for_u32()`, `spu_set_interrupt_mode()`, `spu_get_chip_revision()`, and `spu_init()`. Firmware loading is split across `if_spi_prog_helper_firmware()`, `if_spi_prog_main_firmware_check_len()`, and `if_spi_prog_main_firmware()`. Runtime transfer handlers include `if_spi_c2h_cmd()`, `if_spi_c2h_data()`, `if_spi_h2c()`, `if_spi_e2h()`, `if_spi_host_to_card_worker()`, and `if_spi_host_to_card()`. Probe/remove and PM are handled by `if_spi_probe()`, `libertas_spi_remove()`, `if_spi_suspend()`, and `if_spi_resume_worker()`.

## Control Flow And State
All SPI bus access after firmware load is serialized through `card->workqueue`; IRQ context only queues work. Commands and data have separate packet lists protected by `buffer_lock`. `priv->dnld_sent` is updated when Libertas enqueues a command or data frame, while the worker calls `lbs_host_to_card_done()` when the card reports download readiness. Firmware load uses scratch registers, CRC retry handling, and a magic value in scratch 4 for success. Suspend disables IRQ, tears down platform resources, and resume re-runs platform setup and card init in worker context.

## Dependencies And Integration
Depends on Linux SPI, `linux/spi/libertas_spi.h` platform data, firmware loader, and full Libertas core callbacks. It uses `lbs_get_firmware()`, `lbs_add_card()`, `lbs_start_card()`, `lbs_process_rxed_packet()`, `lbs_queue_event()`, and command response notification.

## Risks And Test Signals
Risks include strict even-byte/word alignment, timing delays between SPU transactions, dummy-clock versus timed-delay platform behavior, command/data queue races, and firmware CRC retry exhaustion. Test signals include chip id/revision detection, helper/main firmware download, interrupt-driven command response and data RX, event delivery, TX wake after command/data ready bits, suspend/resume, and platform setup/teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.h

## Purpose
Defines SPI transport constants for Libertas cards: firmware load sizes and retry limits, SPU register offsets, read/write operation masks, interrupt cause/status bits, device id extraction, and bus mode fields.

## Important Definitions
`IF_SPI_CMD_BUF_SIZE` bounds command/upload buffers. `HELPER_FW_LOAD_CHUNK_SZ`, `FIRMWARE_DNLD_OK`, `MAX_MAIN_FW_LOAD_CRC_ERR`, and `SUCCESSFUL_FW_DOWNLOAD_MAGIC` drive firmware loading. Register constants cover command/data/io ports, scratch registers, interrupt control/status/mask registers, delay read, and bus mode. `IF_SPI_HIST_*`, `IF_SPI_HISM_*`, and `IF_SPI_CIC_*` map interrupt state between host and card.

## Control Flow And State
This header has no executable code. Its constants drive SPU reads/writes, readiness polling, interrupt-mode setup, packet movement, and firmware-success detection in `if_spi.c`.

## Dependencies And Integration
Included by `if_spi.c`; the values are hardware ABI and are also coupled to platform data choices such as dummy clock delay support.

## Risks And Test Signals
Risks are off-by-one buffer assumptions, wrong interrupt masks, or invalid bus mode bit composition. Test signals include stable SPU initialization, correct device id/revision extraction, successful command/data port transfers, and firmware success magic detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_usb.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_usb.h

## Purpose
Defines the full-firmware Libertas USB transport ABI and per-device USB state structure used by `if_usb.c`.

## Important Types And Constants
Message types are `CMD_TYPE_REQUEST`, `CMD_TYPE_DATA`, and `CMD_TYPE_INDICATION`. Boot commands include USB firmware download, EEPROM boot, Boot2 update, and firmware update, identified by `BOOT_CMD_MAGIC_NUMBER`. `struct if_usb_card` stores the USB device, URBs, anchors, endpoints, RX skb, output buffer, firmware download state, timeout, waitqueue, surprise-removal flag, and Boot2 version. `struct fwheader`, `struct fwdata`, and `struct fwsyncheader` describe firmware block transport.

## Control Flow And State
The header has no executable code but defines persistent per-device state for both firmware loading and normal runtime. `bootcmdresp`, `CRC_OK`, `fwdnldover`, `fwfinalblk`, and sequence counters are mutated by firmware-load callbacks.

## Dependencies And Integration
Depends on Linux wait queues and timers plus USB/skb types through the implementation. It is tightly coupled to `if_usb.c` and to firmware image layout.

## Risks And Test Signals
Risks include structure layout mismatch with Boot2, insufficient output buffer size for firmware blocks, and stale URB/skb pointers after disconnect. Test signals are valid boot response parsing, firmware block sequencing, and clean URB anchor teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/if_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/main.c

## Purpose
Provides the shared full-firmware Libertas driver core: netdev lifecycle, main service thread, command/event/TX scheduling, multicast programming, firmware setup, suspend/resume helpers, adapter allocation/free, debugfs/cfg80211 registration, and exported bus-driver entry points.

## Important APIs And Functions
Public/exported functions include `lbs_fw_index_to_data_rate()`, `lbs_set_iface_type()`, `lbs_start_iface()`, `lbs_stop_iface()`, `lbs_host_to_card_done()`, `lbs_set_mac_address()`, `lbs_suspend()`, `lbs_resume()`, `lbs_add_card()`, `lbs_remove_card()`, `lbs_start_card()`, `lbs_stop_card()`, `lbs_queue_event()`, and `lbs_notify_command_response()`. Netdev operations are open, stop, xmit, MAC address, and multicast update. `lbs_thread()` is the central scheduler.

## Control Flow And State
Transports call into this core through `hw_host_to_card` and response/event callbacks. `lbs_thread()` sleeps until work appears, then processes command responses, firmware events, command timeouts, sleep confirmation, queued commands, and pending TX in that order. State is held in `lbs_private`: `fw_ready`, `dnld_sent`, `cur_cmd`, command queues, response buffers, event FIFO, power-save/deep-sleep flags, `tx_pending_len`, timers, netdev pointers, and mesh pointers. `driver_lock`, waitqueues, timers, and workqueues coordinate access.

## Dependencies And Integration
Depends on cfg80211 setup, debugfs, command helpers, mesh support, Linux netdev APIs, kthreads, kfifo, and bus-specific drivers. Bus drivers call `lbs_add_card()` then assign transport callbacks before calling `lbs_start_card()`.

## Risks And Test Signals
Risks include serialization bugs around `dnld_sent`, response buffer flipping, command timeout recovery, TX lockup reset, teardown while work or commands are pending, and multicast updates across station and mesh devices. Test signals include card add/start/stop/remove, netdev open/close, command timeout reset, TX queue wake, multicast mode programming, suspend/resume, and mesh-disabled module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.c

## Purpose
Implements Libertas full-firmware mesh support. It detects mesh-capable firmware, starts/stops firmware mesh mode, creates a virtual `msh%d` netdev, exposes mesh sysfs controls, maps RX/TX packets to the mesh interface, and provides mesh ethtool statistics.

## Important APIs And Functions
Command helpers are `lbs_mesh_access()`, `__lbs_mesh_config_send()`, `lbs_mesh_config_send()`, and `lbs_mesh_config()`. Runtime APIs include `lbs_init_mesh()`, `lbs_start_mesh()`, `lbs_deinit_mesh()`, `lbs_remove_mesh()`, `lbs_mesh_set_channel()`, `lbs_mesh_set_dev()`, and `lbs_mesh_set_txpd()`. Sysfs handlers cover `lbs_mesh`, `anycast_mask`, `prb_rsp_limit`, persistent boot options, and mesh IE fields. Mesh netdev operations are open, stop, xmit, MAC address, and multicast update.

## Control Flow And State
`lbs_init_mesh()` probes firmware version/capability and chooses old or new mesh TLV ids, then stops mesh until the interface opens. `lbs_start_mesh()` registers the virtual mesh interface and `lbs_mesh_dev_open()` starts firmware mesh on the selected channel. Persistent config sysfs paths read defaults with `CMD_TYPE_MESH_GET_DEFAULTS`, modify one field, and send `CMD_ACT_MESH_CONFIG_SET`. RX selection checks old `RxPD_MESH_FRAME` or new BSS interface id; TX marks the descriptor similarly.

## Dependencies And Integration
Depends on cfg80211, netdev, ethtool, command helpers, `host.h` mesh command structs, `types.h` mesh IE structures, and `main.c` lifecycle. It integrates with `rx.c`, `tx.c`, and multicast handling.

## Risks And Test Signals
Risks include firmware-version probing false positives, persistent config writes that are difficult to revert, sysfs input bounds, mesh netdev teardown ordering, and dual-interface TX contention. Test signals include mesh TLV detection on v5/v10 firmware, `msh%d` registration, sysfs read/write results, mesh frame RX routing, TX descriptor marking, ethtool stat retrieval, and behavior when `CONFIG_LIBERTAS_MESH` is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.h

## Purpose
Declares the full-firmware mesh interface between `main.c`, `rx.c`, `tx.c`, ethtool, and `mesh.c`, and provides no-op stubs when `CONFIG_LIBERTAS_MESH` is disabled.

## Important APIs
When mesh is enabled, it declares lifecycle functions `lbs_init_mesh()`, `lbs_start_mesh()`, `lbs_deinit_mesh()`, `lbs_remove_mesh()`, status helper `lbs_mesh_activated()`, channel setter `lbs_mesh_set_channel()`, RX/TX descriptor helpers, and mesh ethtool callbacks. When disabled, macros preserve buildability while returning default behavior.

## Control Flow And State
No direct runtime state is stored here. Compile-time configuration selects either real functions or stubs, which determines whether `main.c` registers mesh support and whether RX/TX helpers alter device selection or descriptors.

## Dependencies And Integration
Includes `host.h` and `dev.h`, and forward-declares netdev, descriptor, command, and ethtool types. It is included by the core RX/TX/main paths.

## Risks And Test Signals
Risks include stub return types drifting from real functions and callers assuming mesh side effects when disabled. Test signals are successful builds with and without `CONFIG_LIBERTAS_MESH`, normal station RX/TX when disabled, and mesh device creation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/mesh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/radiotap.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/radiotap.h

## Purpose
Defines minimal radiotap headers and 802.11 frame-control masks used by Libertas monitor-mode TX and RX paths.

## Important Types And Constants
`struct tx_radiotap_hdr` carries the fixed radiotap header plus rate, tx power, RTS retries, and data retries. `TX_RADIOTAP_PRESENT` marks those fields. Frame-control masks and values define version, type, subtype, ToDS/FromDS combinations, and data/control/management types. `struct rx_radiotap_hdr` carries flags, rate, and antenna signal, with `RX_RADIOTAP_PRESENT`.

## Control Flow And State
No executable code. `tx.c` reads the TX radiotap rate and later fills retry count for TX feedback. `rx.c` prepends an RX radiotap header before delivering monitor-mode frames.

## Dependencies And Integration
Includes `<net/ieee80211_radiotap.h>` and is used by `rx.c` and `tx.c`.

## Risks And Test Signals
Risks include mismatched `it_present` bitmaps, missing alignment/padding handling, and invalid rate conversion. Test signals include monitor-mode packet injection with radiotap rate, radiotap RX visibility in packet capture, and TX feedback retry count updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/radiotap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/rx.c

## Purpose
Processes full-firmware Libertas RX packets delivered by transports. It strips firmware descriptors, converts firmware SNAP/802.2 framing to Ethernet II when appropriate, routes mesh frames to the mesh netdev, constructs radiotap headers in monitor mode, updates stats, and submits packets to the network stack.

## Important APIs And Functions
`lbs_process_rxed_packet()` is exported to transports. `process_rxed_802_11_packet()` handles monitor-mode RX. `convert_mv_rate_to_radiotap()` maps firmware rate indices to radiotap 500 Kb/s units. Local packed header structs model firmware 802.3/SNAP and 802.11 layouts.

## Control Flow And State
Normal RX reads `struct rxpd`, finds the payload via `pkt_ptr`, chooses `priv->dev` or `priv->mesh_dev` via `lbs_mesh_set_dev()`, validates length, optionally rewrites SNAP to Ethernet II, pulls descriptor/header bytes, updates `priv->cur_rate` and netdev stats, then calls `netif_rx()`. Monitor RX validates length, builds `struct rx_radiotap_hdr`, pulls `rxpd`, expands headroom if needed, prepends radiotap, and submits the skb.

## Dependencies And Integration
Called by SDIO/SPI/USB transports after they allocate/fill skb data. Uses `host.h` descriptors, `radiotap.h`, mesh helpers, cfg80211 iftype, and Linux skb/netdev APIs.

## Risks And Test Signals
Risks include trusting firmware `pkt_ptr`, insufficient length checks for malformed frames, radiotap headroom allocation failure, SNAP conversion pointer arithmetic, and stats on the selected device. Test signals include Ethernet RX, non-SNAP LLC RX, mesh RX routing, monitor-mode capture, invalid length drops, and rate reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/tx.c

## Purpose
Builds Libertas firmware TX descriptors from netdev skbs, queues one pending data frame for the main thread to send through the active transport, and handles monitor-mode TX feedback.

## Important APIs And Functions
`lbs_hard_start_xmit()` is the netdev transmit entry point for station and mesh devices. `lbs_send_tx_feedback()` is exported to transports/event paths to echo monitor-mode TX packets back with retry status. `convert_radiotap_rate_to_mv()` maps radiotap rates into firmware TX-control format.

## Control Flow And State
TX holds `driver_lock`, rejects surprise removal and invalid sizes, stops both station and mesh queues, and enforces a single `priv->tx_pending_len` slot. It fills `struct txpd` in `priv->tx_pending_buf`, copies destination address from Ethernet or 802.11 header, applies mesh descriptor markings, copies payload after the descriptor, updates stats, and wakes `lbs_thread()`. Monitor mode keeps `currenttxskb` until an event calls `lbs_send_tx_feedback()`, which sets retry count and injects the skb back through `netif_rx()`.

## Dependencies And Integration
Used by `main.c` netdev ops and `mesh.c` mesh netdev ops. Depends on `host.h`, `radiotap.h`, mesh helpers, `lbs_thread()` draining `tx_pending_buf`, and transport `hw_host_to_card`.

## Risks And Test Signals
Risks include contention between station and mesh hard-start paths, queue wake rules when waiting for monitor feedback, invalid radiotap header assumptions, and descriptor length mismatch. Test signals include ordinary TX, mesh TX descriptor marking, oversize/zero-length drops, queue stop/wake behavior, transport send failures, and monitor TX feedback injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/types.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/types.h

## Purpose
Defines IEEE and Marvell TLV structures shared by Libertas command construction and parsing, including scan/channel TLVs, domain/power/auth TLVs, LED TLVs, and proprietary mesh information elements.

## Important Types And Constants
Core types include `struct ieee_ie_header`, CF/IBSS/FH/DS parameter sets, `struct mrvl_ie_header`, flexible-array TLV payload structs, channel scan parameter sets, RSSI/SNR threshold TLVs, beacon/probe TLVs, LED GPIO/behavior TLVs, `struct mrvl_meshie_val`, `struct mrvl_meshie`, and `struct mrvl_mesh_defaults`. Constants define standard and proprietary TLV ids, including `TLV_TYPE_MESH_ID` and `TLV_TYPE_OLD_MESH_ID`.

## Control Flow And State
No executable code. These packed structs shape variable-length command buffers for scan, 11d, authentication, events, LED configuration, and mesh persistent configuration.

## Dependencies And Integration
Included by `host.h` and other Libertas files. Depends on Linux Ethernet and IEEE 802.11 definitions and explicit endian annotations.

## Risks And Test Signals
Risks include flexible-array sizing mistakes, endian mistakes, mesh IE length mismatch, and inconsistent TLV ids across firmware revisions. Test signals include scan request/response parsing, country/domain programming, event subscription TLVs, LED commands, and mesh persistent IE reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Kconfig

## Purpose
Declares Kconfig options for the Libertas thinfirm driver family.

## Important Options
`LIBERTAS_THINFIRM` is the main tristate library and depends on `MAC80211`, selecting `FW_LOADER`. `LIBERTAS_THINFIRM_DEBUG` enables full thinfirm debugging output when the library is enabled. `LIBERTAS_THINFIRM_USB` builds USB support for 8388 devices and depends on both thinfirm and USB.

## Control Flow And State
No runtime control flow. The selected symbols determine whether the thinfirm core, debug macros, and USB module are compiled.

## Dependencies And Integration
Integrates with kernel build configuration and the `libertas_tf/Makefile`. Thinfirm differs from the full Libertas stack by integrating with mac80211 rather than the full-firmware cfg80211/netdev core.

## Risks And Test Signals
Risks include missing dependency selections for firmware loading or mac80211 APIs, and debug code compiled unexpectedly. Test signals are successful builds for module/built-in combinations and correct object inclusion for USB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Makefile

## Purpose
Defines object composition for the Libertas thinfirm kernel modules.

## Important Rules
`libertas_tf-objs := main.o cmd.o` builds the thinfirm core. `libertas_tf_usb-objs += if_usb.o` builds USB transport support. `obj-$(CONFIG_LIBERTAS_THINFIRM)` and `obj-$(CONFIG_LIBERTAS_THINFIRM_USB)` connect those modules to Kconfig symbols.

## Control Flow And State
No runtime behavior. Build state is controlled entirely by Kconfig symbol expansion.

## Dependencies And Integration
Integrates with `Kconfig` and the kernel kbuild system. The USB object depends on exported/visible thinfirm core symbols and headers.

## Risks And Test Signals
Risks include object list drift when adding source files and missing core linkage for USB. Test signals are successful builds for `libertas_tf.ko` and `libertas_tf_usb.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/cmd.c

## Purpose
Implements thinfirm command management and selected firmware commands for the mac80211-based Libertas thinfirm stack. It allocates command buffers, queues async/sync commands, submits commands through transport ops, processes command responses, and updates hardware/channel/radio state.

## Important APIs And Functions
Public helpers include `lbtf_cmd_copyback()`, `lbtf_update_hw_spec()`, `lbtf_set_channel()`, `lbtf_beacon_set()`, `lbtf_beacon_ctrl()`, `lbtf_cmd_set_mac_multicast_addr()`, `lbtf_set_mode()`, `lbtf_set_bssid()`, `lbtf_set_mac_address()`, `lbtf_set_radio_control()`, `lbtf_set_mac_control()`, `lbtf_allocate_cmd_buffer()`, `lbtf_free_cmd_buffer()`, `lbtf_execute_next_command()`, `lbtf_cmd_async()`, `__lbtf_cmd()`, `lbtf_cmd_response_rx()`, and `lbtf_process_rx_command()`.

## Control Flow And State
Command buffers live in `priv->cmd_array` and are cycled through `cmdfreeq`, `cmdpendingq`, and `cur_cmd` under `driver_lock`. `__lbtf_cmd_async()` fills command header fields, increments `seqnum`, queues the command, and schedules `priv->cmd_work` on `lbtf_wq`. `lbtf_submit_command()` calls `priv->ops->hw_host_to_card()` and starts `command_timer`. Synchronous `__lbtf_cmd()` waits on the command node waitqueue. Response processing checks sequence and `CMD_RET(curcmd)`, handles firmware `0x0004` retry responses by letting timeout logic retry, invokes optional callbacks, completes waiters, and recycles nodes.

## Dependencies And Integration
Depends on `libertas_tf.h`, thinfirm main workqueue/timers, mac80211 hardware state, firmware command ABI, and transport ops supplied by USB or other bus drivers.

## Risks And Test Signals
Risks include command node leaks on interrupted waits, response/sequence mismatch, holding locks around callbacks, timeout retry behavior, region-code clamping, and async command completion without callbacks. Test signals include `GET_HW_SPEC`, channel changes, beacon programming, MAC/radio control, multicast list updates, command timeout/retry, and valid response sequence checking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/deb_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/deb_defs.h

## Purpose
Provides debug category flags and logging macros for the Libertas thinfirm driver.

## Important APIs And Constants
Defines `DRV_NAME` defaulting to `libertas_tf`, maps `CONFIG_LIBERTAS_THINFIRM_DEBUG` to `DEBUG`, declares `extern unsigned int lbtf_debug`, and defines `LBTF_DEB_*` bitmasks for main, net, mesh, scan, association, command, RX/TX, USB, firmware, thread, SDIO, MAC ops, and hex dump categories. Macros such as `lbtf_deb_enter()`, `lbtf_deb_leave()`, `lbtf_deb_cmd()`, `lbtf_deb_usb()`, and `lbtf_deb_usbd()` compile to conditional `printk()` when debugging is enabled and no-ops otherwise. `lbtf_deb_hex()` conditionally dumps buffers.

## Control Flow And State
Runtime logging is controlled by the global `lbtf_debug` mask. When debugging is disabled, most macros compile out, leaving no runtime logging state.

## Dependencies And Integration
Included by thinfirm headers and source files. Depends on kernel logging, spinlock include, and `print_hex_dump_bytes()` in debug builds.

## Risks And Test Signals
Risks include format-string mismatches hidden in disabled builds, category names that do not match code paths, and excessive logging in debug builds. Test signals include debug module parameter behavior, category-filtered logs, and clean non-debug compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/deb_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.c

## Purpose
Implements USB transport and firmware loading for the mac80211/thinfirm Libertas 8388 driver. It mirrors much of the full Libertas USB Boot2 protocol but routes normal data, command responses, and events into `lbtf_*` thinfirm core callbacks.

## Important APIs And Functions
`if_usb_probe()` finds endpoints, allocates RX/TX/CMD URBs and output buffer, then calls `lbtf_add_card()` with `if_usb_ops`. `if_usb_ops` provides `hw_host_to_card`, `hw_prog_firmware`, and `hw_reset_device`. Firmware paths include `if_usb_prog_firmware()`, `if_usb_receive_fwload()`, `if_usb_send_fw_pkt()`, `if_usb_issue_boot_command()`, `check_fwfile_format()`, and `if_usb_fw_timeo()`. Runtime paths include `if_usb_receive()`, `process_cmdtypedata()`, `process_cmdrequest()`, `if_usb_host_to_card()`, `usb_tx_block()`, and `if_usb_submit_rx_urb()`.

## Control Flow And State
Probe creates transport state but the thinfirm core owns startup through `hw_prog_firmware`. Firmware download requests `lbtf_fw_name`, validates block format, submits an RX URB for Boot2 responses, retries boot commands, sends sequenced firmware blocks, handles CRC feedback, waits on `fw_wq`, kills the firmware RX URB, releases firmware, and then calls `if_usb_setup_firmware()`. Normal receive parses the 4-byte type header: data is passed to `lbtf_rx()`, command responses are copied into `priv->cmd_resp_buff` and signaled with `lbtf_cmd_response_rx()`, and indications become TX feedback or beacon-sent notifications. It uses separate `tx_urb` for data and `cmd_urb` for commands.

## Dependencies And Integration
Depends on Linux USB and firmware APIs plus `libertas_tf.h` command/mac80211 core. Exposes module parameter `fw_name` and declares `MODULE_FIRMWARE("lbtf_usb.bin")`.

## Risks And Test Signals
Risks include missing URB anchoring compared with full USB driver, static firmware reset retry count, command/data URB reuse while prior transfers are pending, firmware load error paths that still call setup after `release_fw`, and lack of suspend/resume support. Test signals include firmware request by parameter name, Boot2 response handling, CRC retry, firmware-ready wait, command response processing, data RX into mac80211, TX feedback/beacon events, disconnect reset, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.h

## Purpose
Defines USB transport protocol constants and device state for the Libertas thinfirm USB driver.

## Important Types And Constants
Message constants match the full USB driver: `CMD_TYPE_REQUEST`, `CMD_TYPE_DATA`, and `CMD_TYPE_INDICATION`. Boot protocol constants define firmware download/update commands and `BOOT_CMD_MAGIC_NUMBER`. `struct if_usb_card` stores USB endpoints, RX/TX/CMD URBs, current RX skb, output buffer, firmware pointer, firmware timeout and waitqueue, firmware sequence/progress fields, CRC and final-block flags, Boot2 version, and the owning `lbtf_private`. Firmware block structs are `fwheader`, `fwdata`, and `fwsyncheader`.

## Control Flow And State
No executable code. The fields are mutated by `if_usb.c` during Boot2 command exchange, firmware block download, normal RX submission, and command/data TX.

## Dependencies And Integration
Includes Linux wait and timer headers and forward-declares `struct lbtf_private`. It is tightly coupled to `libertas_tf/if_usb.c` and the Boot2 firmware image format.

## Risks And Test Signals
Risks include layout drift from firmware expectations, lack of include guard in this header, stale URB pointers on cleanup, and shared `ep_out_buf` reuse. Test signals include successful thinfirm firmware sequencing, valid command/data/indication parsing, and clean USB disconnect after firmware or runtime traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/if_usb.h -->
