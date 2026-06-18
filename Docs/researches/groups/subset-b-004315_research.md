# subset-b-004315 Research

Grouped research for USB SocketCAN drivers in `sources/distributed-fs/ceph-client/drivers/net/can/usb`. Each section is marker-bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/gs_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/gs_usb.c

Purpose: implements the SocketCAN USB driver for Geschwister Schneider USB/CAN, candleLight, CANtact-compatible, and related CAN/CAN FD adapters. It binds USB interfaces, discovers one or more CAN channels, exposes each channel as a `candev`, and translates between SocketCAN sk_buffs and the gs_usb firmware control/bulk protocol.

Important APIs/types/functions: `struct gs_usb` is the per-USB-interface parent with shared bulk pipes, RX URB anchor, channel array, and optional hardware timestamp `cyclecounter`/`timecounter`. `struct gs_can` is the per-channel netdev private state with `can_priv`, RX offload, TX echo contexts, feature flags, and active TX URB accounting. Protocol structs include `gs_host_config`, `gs_device_config`, `gs_device_bittiming`, `gs_device_bt_const`, `gs_device_bt_const_extended`, `gs_device_mode`, `gs_device_state`, `gs_host_frame`, and the classic/CAN FD payload variants. Key entry points are `gs_usb_probe`, `gs_make_candev`, `gs_can_open`, `gs_can_close`, `gs_can_start_xmit`, `gs_usb_receive_bulk_callback`, `gs_usb_set_bittiming`, `gs_usb_set_data_bittiming`, `gs_usb_get_state`, `gs_usb_set_termination`, and ethtool identify/timestamp helpers.

Control flow: probe finds common bulk endpoints, sends host byte-order configuration, reads device config, allocates one parent with a flexible channel array, and registers one CAN netdev per firmware-reported interface. Per-channel setup reads bit-timing constants, derives supported ctrlmodes from firmware features, applies CANtact Pro quirks when needed, optionally reads extended CAN FD bit-timing constants, attaches RX offload, and registers the CAN netdev. Open enables RX offload, starts shared RX URBs if this is the first active channel, configures nominal and optional data bit timing, maps SocketCAN ctrlmode bits to firmware flags, and sends `GS_USB_BREQ_MODE` start. TX allocates a local echo context, encodes a `gs_host_frame`, anchors a bulk OUT URB, stores echo skb, and stops the queue at `GS_MAX_TX_URBS`. RX validates frame length/channel, decodes received CAN/CAN FD frames or TX echoes, queues RX through `can_rx_offload`, completes echo skbs, reports overflow as CAN error frames, and resubmits the bulk IN URB.

State and persistence behavior: all state is in RAM and tied to USB/netdev lifetime. Shared RX URBs exist only while any channel is active; per-channel TX URBs and echo contexts are killed/reset on close. `active_channels` gates shared RX and timestamp worker lifetime. Hardware timestamp state uses a delayed worker to read the firmware 32-bit microsecond counter before wraparound and a spinlock-protected `timecounter`. No persistent storage is touched.

Dependencies/integration points: depends on Linux USB bulk/control APIs, SocketCAN `can_priv`, `alloc_candev`, CAN FD helpers, `can_rx_offload`, netdev/ethtool operations, hwtstamp APIs, and module USB ID matching. It integrates with users through SocketCAN netdevs, netlink CAN bittiming/ctrlmode, ethtool identify and timestamp info, and termination control.

Risks: firmware feature reporting drives most behavior, so bad feature bits can select wrong frame sizes or unsupported requests. Multi-channel sharing means RX URB setup/teardown and timestamp worker lifetime depend on correct `active_channels` updates. Length validation is careful but any mismatch in CAN FD/timestamp/quirk frame size can drop traffic. TX context handling must stay synchronized with echo IDs to avoid echo leaks or queue stalls. Hardware timestamps depend on periodic counter reads and can become inaccurate after USB read failures.

Test signals: useful tests are hotplug/probe for each USB ID family, multi-channel open/close sequencing, CAN classic and CAN FD loopback, queue stop/wake under TX saturation, overflow/error-frame reporting, termination get/set, identify LED support, CANtact Pro quirk behavior, bus-off/restart state changes, and timestamp monotonicity across firmware counter wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/gs_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/Makefile

Purpose: defines the Kbuild composition for the Kvaser USB CAN driver module. It builds `kvaser_usb.o` when `CONFIG_CAN_KVASER_USB` is enabled.

Important APIs/types/functions: no C APIs are declared here. The build variables are `obj-$(CONFIG_CAN_KVASER_USB) += kvaser_usb.o` and `kvaser_usb-y = kvaser_usb_core.o kvaser_usb_devlink.o kvaser_usb_leaf.o kvaser_usb_hydra.o`.

Control flow: Kbuild compiles the common core, devlink support, Leaf/Usbcan protocol implementation, and Hydra protocol implementation into one module. Product ID dispatch in `kvaser_usb_core.c` selects the appropriate ops table at runtime.

State and persistence behavior: no runtime state or persistence. Its only effect is compile-time object inclusion.

Dependencies/integration points: integrates with the kernel CAN USB driver menu through `CONFIG_CAN_KVASER_USB`. The object list is an important integration point because `kvaser_usb_core.c` references `kvaser_usb_leaf_dev_ops`, `kvaser_usb_hydra_dev_ops`, and `kvaser_usb_devlink_ops` defined in the companion objects.

Risks: omitting one object would cause link failures or remove support for a Kvaser device family. Adding a new Kvaser protocol family requires updating this file as well as the core ID/ops mapping.

Test signals: build coverage with `CONFIG_CAN_KVASER_USB=m` or `=y` is the main signal; runtime tests should confirm both Leaf/Usbcan and Hydra devices still bind from the single module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb.h

Purpose: provides the shared internal contract for the Kvaser USB driver, covering common device/netdev state, protocol-operation callbacks, device configuration, capabilities, quirks, and helper declarations used by the core plus Leaf and Hydra subdrivers.

Important APIs/types/functions: `struct kvaser_usb` stores the USB device/interface, endpoint descriptors, RX anchors/buffers, per-channel netdev private pointers, driver info, card metadata, firmware/hardware identifiers, max outstanding TX count, and card-specific data. `struct kvaser_usb_net_priv` embeds `can_priv`, `devlink_port`, error counters, channel state, completions, TX anchor, cached busparams, and variable-length TX contexts. `struct kvaser_usb_dev_ops` is the subdriver vtable for mode changes, bit timing, busparams readback, endpoint setup, card/channel init, firmware/card/capability discovery, LED control, chip start/stop/reset/flush, bulk RX decode, and skb-to-command translation. Other central types are `kvaser_usb_driver_info`, `kvaser_usb_dev_cfg`, `kvaser_usb_busparams`, and `kvaser_usb_tx_urb_context`.

Control flow: the core selects a `kvaser_usb_driver_info` from the USB ID table, then drives the selected `kvaser_usb_dev_ops` through probe, open, close, bit timing, TX, and RX paths. Subdrivers use the exported helpers for synchronous/asynchronous USB commands, overflow error injection, TX URB unlinking, devlink port registration, and timestamp conversion.

State and persistence behavior: the header defines only in-memory kernel state. `completion` objects synchronize command replies; spinlocks protect TX contexts, Hydra transaction IDs, and partial RX buffers; anchors own URB lifetimes. No persistent state is represented.

Dependencies/integration points: includes Linux USB, netdev/devlink, SocketCAN, completion, ktime, math64, spinlock, and type headers. It is the integration seam between `kvaser_usb_core.c`, `kvaser_usb_devlink.c`, `kvaser_usb_leaf.c`, and `kvaser_usb_hydra.c`.

Risks: the vtable makes callback contracts critical: subdrivers must complete expected completions, provide matching frame encoders/decoders, and maintain busparam caches. `max_tx_urbs` doubles as the free-context sentinel, so inconsistent values can corrupt TX flow control. Timestamp conversion depends on each device config reporting the correct `timestamp_freq`.

Test signals: compile coverage across all four Kvaser objects catches signature drift. Runtime tests should exercise every ops callback for Leaf/Usbcan and Hydra families, including TX echo, command timeouts, devlink metadata, and timestamp conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_core.c

Purpose: implements the common Kvaser USB driver module: USB product matching, shared command transport, RX URB management, SocketCAN netdev operations, TX flow control, devlink allocation, probe/disconnect, and per-channel CAN device registration. Device-family-specific protocol work is delegated to Leaf or Hydra ops.

Important APIs/types/functions: the large `kvaser_usb_table` maps Kvaser product IDs to `kvaser_usb_driver_info` entries for Hydra, Leaf, Leaf i.MX, and Usbcan families. Shared transport helpers are `kvaser_usb_send_cmd`, `kvaser_usb_recv_cmd`, and `kvaser_usb_send_cmd_async`. RX/TX helpers include `kvaser_usb_setup_rx_urbs`, `kvaser_usb_read_bulk_callback`, `kvaser_usb_start_xmit`, `kvaser_usb_write_bulk_callback`, `kvaser_usb_reset_tx_urb_contexts`, `kvaser_usb_unlink_tx_urbs`, and `kvaser_usb_unlink_all_urbs`. Netdev lifecycle functions are `kvaser_usb_open`, `kvaser_usb_close`, `kvaser_usb_set_bittiming`, `kvaser_usb_set_data_bittiming`, and `kvaser_usb_set_phys_id`. Probe/remove functions are `kvaser_usb_probe`, `kvaser_usb_init_one`, `kvaser_usb_remove_interfaces`, and `kvaser_usb_disconnect`.

Control flow: probe allocates a devlink instance with private `struct kvaser_usb`, selects subdriver ops from the USB ID, lets the subdriver find endpoints and initialize/discover the card, validates `dev->cfg`, reads card info and capabilities, then initializes one netdev per channel. `kvaser_usb_init_one` optionally resets the chip, allocates a variable-sized CAN device for TX contexts, configures SocketCAN capabilities from quirks/card capabilities, initializes subdriver channel state, registers a devlink port, and registers the CAN device. Open calls `open_candev`, sets optional driver mode, and starts the chip. Bit timing writes busparams via subdriver, ensures RX URBs are running, reads back busparams where supported, and compares readback. TX reserves a context under a spinlock, asks the subdriver to encode the skb into a firmware command, anchors/submits a bulk URB, and leaves final echo completion to subdriver RX handling. Disconnect unregisters netdevs, kills RX/TX URBs, frees coherent RX buffers, unregisters devlink, and releases devlink memory.

State and persistence behavior: runtime state is all in memory and anchored to USB/netdev lifetimes. RX URBs are allocated once lazily after first bit-timing setup and tracked by `rxinitdone`, `rxbuf`, and `rxbuf_dma`; TX contexts use `echo_index == dev->max_tx_urbs` as the free sentinel and `active_tx_contexts` for queue stop/wake. Completions in per-channel private state synchronize subdriver command replies. No disk persistence exists.

Dependencies/integration points: integrates Linux USB bulk APIs, SocketCAN netdev registration, CAN bittiming and CAN FD data bittiming, ethtool LED identify and timestamp info, devlink private data, and module USB registration. It depends on Leaf/Hydra ops and shared header helpers.

Risks: the common TX path assumes subdriver TX acknowledge events will free echo contexts and wake queues; missing or malformed firmware replies can stall TX. RX URB setup accepts partial allocation with a performance warning, so low-memory cases may work with reduced throughput. Probe error unwinding spans devlink, subdriver channel init, registered netdevs, URBs, and devlink ports, making ordering important. Busparam readback comparison can reject devices with firmware rounding differences unless subdriver returns `-EOPNOTSUPP`.

Test signals: build and module-load tests for all USB IDs, probe/unplug while interfaces are open, bit timing readback success/failure, TX queue saturation and recovery, subdriver command timeout behavior, devlink info/port visibility, CAN FD setup on Hydra, and error unwinding fault injection around URB allocation and register failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_devlink.c

Purpose: exposes Kvaser USB device metadata and per-channel physical ports through devlink.

Important APIs/types/functions: `kvaser_usb_devlink_info_get` publishes serial number, running firmware version, fixed board revision, and fixed board ID/EAN when present. `kvaser_usb_devlink_ops` installs `.info_get`. `kvaser_usb_devlink_port_register` sets physical port attributes and links a netdev to its `devlink_port`; `kvaser_usb_devlink_port_unregister` removes it.

Control flow: the core allocates devlink before probe initialization and registers it after all CAN channels are created. During each channel init, this file registers a devlink physical port with `phys.port_number = channel` and calls `SET_NETDEV_DEVLINK_PORT`. `devlink info` calls read metadata previously filled by Leaf/Hydra card and software-info discovery.

State and persistence behavior: no independent state is allocated here beyond `devlink_port` embedded in `kvaser_usb_net_priv`. Reported values come from in-memory probe-time fields (`serial_number`, `fw_version`, `hw_revision`, `ean`). No persistent data is written.

Dependencies/integration points: depends on netdev and devlink APIs and the shared Kvaser structs. It is integrated by `kvaser_usb_core.c` during channel registration/removal and by the module-level `devlink_alloc` call.

Risks: metadata is omitted when probe did not fill a value or the EAN MSB does not match the expected Kvaser prefix. Buffer formatting must remain large enough for decimal serials and concatenated EAN strings. Port unregister must mirror successful register to avoid devlink resource leaks.

Test signals: `devlink info` should show serial, firmware, board revision, and board ID for devices that report them; `devlink port` should show one physical port per CAN channel and removal should clean ports on unplug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_hydra.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_hydra.c

Purpose: implements the Minihydra/Kvaser Hydra firmware protocol backend for the shared Kvaser USB core. It handles Hydra command headers, entity-address mapping, capability discovery, CAN/CAN FD frame encoding/decoding, chip control, bit timing, LED control, timestamps, and error-state translation.

Important APIs/types/functions: command definitions cover standard commands such as `CMD_SET_BUSPARAMS_REQ`, `CMD_START_CHIP_REQ`, `CMD_TX_CAN_MESSAGE`, `CMD_RX_MESSAGE`, `CMD_GET_SOFTWARE_DETAILS_RESP`, `CMD_GET_CAPABILITIES_RESP`, and extended commands `CMD_TX_CAN_MESSAGE_FD`, `CMD_TX_ACKNOWLEDGE_FD`, `CMD_RX_MESSAGE_FD`. Protocol structures include `kvaser_cmd`, `kvaser_cmd_ext`, card/software/capability structs, RX/TX CAN structs, error-event structs, and KCAN FD packet fields. Key helpers are `kvaser_usb_hydra_get_next_transid`, `kvaser_usb_hydra_map_channel`, `kvaser_usb_hydra_wait_cmd`, `kvaser_usb_hydra_read_bulk_callback`, `kvaser_usb_hydra_frame_to_cmd_std`, `kvaser_usb_hydra_frame_to_cmd_ext`, `kvaser_usb_hydra_tx_acknowledge`, `kvaser_usb_hydra_rx_msg_std`, `kvaser_usb_hydra_rx_msg_ext`, and `kvaser_usb_hydra_error_frame`. The exported ops table is `kvaser_usb_hydra_dev_ops`.

Control flow: card init initializes transaction-ID and leftover-buffer locks, maps CAN0..CAN4 and SYSDBG names to Hydra entity addresses via router requests, and stores HE addresses. Software discovery reads max outstanding TX and software details, rejects bad firmware, records firmware version/capability flags, enables CAN FD/non-ISO/ext commands where advertised, and selects one of three device configs. Capability discovery queries listen mode, error reporting, and one-shot support. RX bulk handling reassembles partial extended commands into a leftover buffer, walks complete commands, and dispatches standard or extended command handlers. Start/stop/flush/get-busparams commands use completions. TX uses the common core context index as Hydra transid, encodes classic frames into standard commands or CAN FD/classic frames into extended KCAN commands, and later TX ACK frees echo state. RX decodes standard or extended frames, maps HE source to channel, attaches hardware timestamps, reports overrun and bus errors, and calls `netif_rx`.

State and persistence behavior: persistent device state is not stored. In-memory state includes `channel_to_he`, `sysdbg_he`, spinlock-protected rolling transid, `usb_rx_leftover` for split extended commands, cached busparams, per-channel `sub_priv` with pending busparam type, cached error counters, completions, and firmware/card metadata used by devlink. State resets on unplug/module removal.

Dependencies/integration points: plugs into `kvaser_usb_core.c` through `kvaser_usb_hydra_dev_ops`. Uses SocketCAN error helpers, netdev stats, USB bulk command helpers, completion timeouts, spinlocks, bitfield helpers, and common timestamp conversion in `kvaser_usb.h`.

Risks: Hydra routing depends on correct HE mapping; invalid transids or stale mappings can route events to the wrong channel. Extended command reassembly must bound lengths correctly to avoid format errors or dropped packets. Error-active versus error-warning is partly inferred from counters because firmware does not distinguish all states. TX ACK uses `transid % max_tx_urbs`, so transid/context alignment with the core is critical. CAN FD support depends on firmware flags and selected device config timestamp/clock frequencies.

Test signals: tests should cover HE mapping, software-details flag combinations, capability status codes, start/stop/flush completion timeouts, standard and extended CAN/CAN FD RX/TX, one-shot failure ACKs, overrun and bus-error reporting, bus-off recovery, partial USB packet reassembly, LED control, and devlink metadata population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_hydra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_leaf.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_leaf.c

Purpose: implements the Kvaser Leaf and Usbcan-II firmware protocol backend for the shared Kvaser USB core. It covers fixed-size/variable-size command parsing, firmware/card/capability discovery, classic CAN frame encode/decode, chip control, bit timing, timestamps, LED control, and family-specific error reporting.

Important APIs/types/functions: protocol structures include `kvaser_cmd`, `kvaser_cmd_simple`, `kvaser_cmd_cardinfo`, Leaf and Usbcan software-info structs, busparams, RX/TX CAN structs, chip-state/error-event structs, log-message structs, capability request/response, and clock-overflow events. `kvaser_usb_leaf_cmd_sizes_leaf` and `kvaser_usb_leaf_cmd_sizes_usbcan` define receive validation. Important functions include `kvaser_usb_leaf_verify_size`, `kvaser_usb_leaf_wait_cmd`, `kvaser_usb_leaf_get_software_info`, `kvaser_usb_leaf_get_card_info`, `kvaser_usb_leaf_get_capabilities`, `kvaser_usb_leaf_frame_to_cmd`, `kvaser_usb_leaf_read_bulk_callback`, `kvaser_usb_leaf_handle_command`, `kvaser_usb_leaf_rx_can_msg`, `kvaser_usb_leaf_rx_error`, `kvaser_usb_leaf_tx_acknowledge`, `kvaser_usb_leaf_start_chip`, `kvaser_usb_leaf_stop_chip`, and `kvaser_usb_leaf_set_mode`. The exported ops table is `kvaser_usb_leaf_dev_ops`.

Control flow: software-info probing sends `CMD_GET_SOFTWARE_INFO`, retries timeouts, selects Leaf M32C/i.MX or Usbcan device config based on family, frequency options, and quirks, and records firmware version/max TX URBs. Card-info probing fills channel count, EAN, serial, and hardware revision, enforcing Usbcan's two-channel limit. Leaf extended capabilities may enable listen-only and bus-error reporting. RX bulk parsing skips zero-length padding commands inserted to avoid USB max-packet boundary crossing, validates command length, and dispatches by command ID. TX encodes SocketCAN classic frames into Leaf/Usbcan byte layout with standard/extended ID packing and RTR flags. RX decodes standard/extended/log-message frames, handles overrun/error flags, attaches family-specific timestamps, and submits skbs to the network stack. Error handling normalizes Leaf M16C error factors and Usbcan ambiguous channel reports into CAN error frames and state transitions; delayed chip-state polling fills firmware gaps when recovery notifications are not automatic.

State and persistence behavior: no persistent storage. In-memory state includes selected device config, firmware/card metadata, `usbcan_timestamp_msb` updated by clock-overflow events, cached busparams, per-channel error counters, completions, and `kvaser_usb_net_leaf_priv` with delayed chip-state work and `joining_bus` startup suppression. Delayed work is canceled on stop/remove.

Dependencies/integration points: used by `kvaser_usb_core.c` for all Leaf and Usbcan product IDs. Depends on USB command helpers, SocketCAN netdev/error APIs, delayed work, completions, bitfield helpers, and common timestamp conversion. It provides no CAN FD data-bit-timing callbacks; Hydra covers newer FD devices.

Risks: firmware padding/alignment behavior is unusual; parser regressions can silently drop events under heavy RX load. Usbcan error-channel attribution is inferred from counter deltas and peer-channel status, so some events may be advisory. Startup `joining_bus` suppresses stale bus-off events but must clear correctly. Timestamp high bits for Usbcan depend on overflow events. Max outstanding TX and command sizes come from firmware/family assumptions.

Test signals: validate command-size checks, zero-length padding alignment, software-info retry behavior, clock/frequency config selection, card-info channel limits, capability probing, TX/RX standard and extended classic frames, Usbcan timestamp overflow, delayed chip-state polling, bus-off/restart behavior, overrun and M16C error-factor mapping, LED identify, and hot unplug cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/kvaser_usb/kvaser_usb_leaf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/mcba_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/mcba_usb.c

Purpose: implements the SocketCAN USB driver for the Microchip CAN BUS Analyzer Tool. It exposes the adapter as one classic CAN netdev, sends firmware commands for bitrate/termination/version reads, and converts Microchip USB messages to and from SocketCAN frames.

Important APIs/types/functions: `struct mcba_priv` embeds `can_priv` and stores echo skbs, TX contexts, USB device/netdev pointers, RX/TX anchors, error counters, keepalive/version flags, speed-check state, coherent RX buffers, and pipe addresses. Protocol structs include `mcba_usb_msg_can`, generic `mcba_usb_msg`, USB/CAN keepalive messages, bitrate command, termination command, and firmware-version command. Key functions are `mcba_usb_probe`, `mcba_usb_start`, `mcba_usb_open`, `mcba_usb_close`, `mcba_usb_start_xmit`, `mcba_usb_xmit`, `mcba_usb_xmit_cmd`, `mcba_usb_read_bulk_callback`, `mcba_usb_process_rx`, `mcba_usb_process_can`, `mcba_usb_process_ka_usb`, `mcba_usb_process_ka_can`, `mcba_net_set_bittiming`, `mcba_set_termination`, and `mcba_usb_disconnect`.

Control flow: probe finds bulk endpoints, allocates/registers one CAN netdev, initializes termination and bitrate constants, stores pipes, then starts the USB side immediately by submitting RX URBs and requesting USB/CAN PIC firmware versions. Open only opens the CAN device, sets `can_speed_check`, marks error-active, and starts the queue. TX gets a free context, packs standard or extended CAN IDs into Microchip SID/EID fields, stores an echo skb, and submits a coherent bulk OUT URB. TX completion frees coherent memory, accounts echo skb for CAN frames, frees the context, and wakes the queue. RX completion parses stacked fixed-size messages, dispatches keepalive, received CAN, no-op, and transmit-response commands, then resubmits the URB. Keepalive from the CAN PIC updates error counters/state and verifies reported bitrate after a bittiming change; keepalive from the USB PIC updates termination state.

State and persistence behavior: state is in memory only. RX URBs are started at probe rather than netdev open and killed on close/disconnect. TX contexts use `MCBA_CTX_FREE` plus an atomic free count for queue flow control. Firmware version logging happens only on first keepalive from each PIC. Termination and error counters are continuously refreshed from keepalive packets; no disk state exists.

Dependencies/integration points: depends on Linux USB coherent/bulk APIs, SocketCAN classic CAN helpers, netdev/ethtool, unaligned big-endian helpers, and module USB ID matching. Integrates with SocketCAN via fixed bitrate constants, termination control, `do_get_berr_counter`, local echo, and netdev operations.

Risks: command TX and CAN TX share the same context pool, so heavy command traffic can temporarily block CAN frames. RX messages are fixed-size and stacked; format errors drop the remainder of an URB. Netdev open does not start hardware because RX URBs are already running from probe, so close/open sequencing must not leave URBs unexpectedly killed without restart. State changes are inferred from keepalive counters and thresholds, not explicit CAN error frames. The bitrate command sends kbps with special rounding expectations for 33.333/83.333 kbps.

Test signals: probe/disconnect, repeated open/close after probe-started RX, standard/extended/RTR TX and RX ID packing, TX context exhaustion/wake, bitrate set plus keepalive verification, termination set and keepalive readback, bus-warning/passive/off threshold behavior, malformed stacked RX buffers, and hot unplug during active URBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/mcba_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/nct6694_canfd.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/nct6694_canfd.c

Purpose: implements the Nuvoton NCT6694 CAN FD controller driver exposed through an NCT6694 USB MFD transport. Unlike the pure USB drivers in this folder, it is a platform driver that communicates with the parent MFD via `nct6694_read_msg`/`nct6694_write_msg`, maps parent IRQs, and registers one CAN FD netdev per allocated port.

Important APIs/types/functions: protocol constants define NCT6694 CANFD module commands for setting, information, events, deliver, and receive. Packed structures are `nct6694_canfd_setting`, `nct6694_canfd_information`, `nct6694_canfd_event`, and `nct6694_canfd_frame`. `struct nct6694_canfd_priv` embeds `can_priv`, manual RX offload, parent `struct nct6694`, ordered TX workqueue, reusable TX/RX/event buffers, and cached error counters. Main functions include `nct6694_canfd_probe`, `nct6694_canfd_open`, `nct6694_canfd_close`, `nct6694_canfd_start`, `nct6694_canfd_stop`, `nct6694_canfd_start_xmit`, `nct6694_canfd_tx_work`, `nct6694_canfd_irq`, `nct6694_canfd_handle_rx`, `nct6694_canfd_handle_tx`, `nct6694_canfd_handle_state_change`, `nct6694_canfd_handle_bus_err`, and `nct6694_canfd_get_clock`.

Control flow: probe allocates a port ID from the parent IDA, maps the corresponding parent IRQ, allocates one-echo CAN device, reads the CAN clock via the information command, configures nominal/data bit-timing constants, forces static CAN FD mode, adds manual RX offload, and registers the netdev. Open enables RX offload, requests a threaded IRQ, creates an ordered/freezable workqueue, writes initial controller settings, and starts the queue. TX stops the queue, stores echo skb index 0, and queues work; work encodes classic or CAN FD frame flags/ID/data and sends a deliver command. IRQ reads both port event entries, handles RX data, lost RX, state changes, bus errors, and TX FIFO empty, then finishes threaded RX offload and updates cached counters. Close stops the queue, switches hardware into listen-only because it cannot be fully stopped, destroys workqueue, frees IRQ, disables RX offload, and closes the CAN device.

State and persistence behavior: all driver state is volatile. Port allocation persists only for device lifetime in the parent IDA. The hardware cannot be stopped, so close writes listen-only mode as a runtime safety state. The driver supports one outstanding TX echo skb and serializes TX through an ordered workqueue. Error counters are cached from event messages and returned by `do_get_berr_counter`.

Dependencies/integration points: depends on the NCT6694 MFD API, platform driver model, irqdomain mapping, SocketCAN CAN FD and RX offload APIs, netdev/ethtool, IDA allocation, and threaded IRQ handling. It integrates with users as a SocketCAN FD netdev with loopback, listen-only, bus-error reporting, FD, and FD non-ISO controls.

Risks: `nct6694_canfd_handle_state_change` currently derives state from cached counters before the IRQ updates `priv->bec` from the just-read event, so state transitions can lag by one event. Only one TX echo slot is used, so missed TX FIFO empty events can stall the queue. Close destroys the workqueue; pending TX work ordering around close must be correct. Since stop is implemented as listen-only, the controller may still observe bus traffic after netdev close. Event reads fetch both port events and index by `dev_port`, so port allocation and event layout must match hardware.

Test signals: validate clock read/probe, IRQ mapping per port, open/close resource unwind, setting register fields for nominal/data bit timing and ctrlmodes, classic/CAN FD/BRS/RTR TX encoding, RX frame decoding and offload delivery, lost-message error frame generation, bus error mappings, bus-off handling and restart, TX queue wake on FIFO-empty event, and behavior when write/read commands fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/nct6694_canfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/peak_usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/peak_usb/Makefile

Purpose: defines the Kbuild composition for the PEAK-System USB CAN driver module. It builds the aggregate `peak_usb.o` module when `CONFIG_CAN_PEAK_USB` is enabled.

Important APIs/types/functions: no runtime APIs are declared. The relevant Kbuild variables are `obj-$(CONFIG_CAN_PEAK_USB) += peak_usb.o` and `peak_usb-y = pcan_usb_core.o pcan_usb.o pcan_usb_pro.o pcan_usb_fd.o`.

Control flow: Kbuild links the PEAK common core and the protocol/device-family objects for classic PCAN-USB, PCAN-USB Pro, and PCAN-USB FD support into one module. Runtime device dispatch is handled by the C sources included here, not by this Makefile.

State and persistence behavior: no runtime state and no persistence. This file only controls object inclusion.

Dependencies/integration points: integrates with kernel configuration through `CONFIG_CAN_PEAK_USB`. The object list is the build-time integration point for all PEAK USB subdrivers.

Risks: stale object lists can create link failures or silently exclude support for a PEAK hardware family. Any new source added to the PEAK driver family must be reflected here.

Test signals: kernel build tests with `CONFIG_CAN_PEAK_USB` enabled are the primary signal; runtime smoke tests should verify devices from each included PEAK family bind to the aggregate module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/peak_usb/Makefile -->
