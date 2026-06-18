# Research Report: subset-b-004314

Work item `subset-b-004314` covers Linux SocketCAN USB drivers under `sources/distributed-fs/ceph-client/drivers/net/can/usb/`, with emphasis on EMS CPC-USB/ARM7, esd CAN-USB, ETAS ES58x, and Fintek F81604 adapters.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/ems_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/ems_usb.c

## Purpose
`ems_usb.c` is a SocketCAN USB network driver for the EMS Dr. Thomas Wuensche CPC-USB/ARM7 adapter. It binds USB vendor/product `0x12d6:0x0444`, exposes one CAN netdevice, translates CPC protocol messages to classical CAN frames and CAN error frames, and programs SJA1000-compatible timing parameters over USB bulk control messages. The device clock is modeled as 8 MHz because the firmware expects SJA1000 bit timing values based on that clock even though the device uses a 16 MHz source internally.

## Important APIs, Types, And Functions
The central state object is `struct ems_usb`, whose first member is `struct can_priv` for SocketCAN compatibility. It owns the USB device, netdevice, RX/TX anchors, interrupt URB, coherent RX buffers, a synchronous command buffer, TX echo contexts, the active SJA1000 parameter message, and a cached device `free_slots` count. CPC wire messages are represented by `struct ems_cpc_msg` and nested payload types such as `struct cpc_can_msg`, `struct cpc_can_params`, `struct cpc_can_error`, and `struct cpc_can_err_counter`.

Key entry points are `ems_usb_probe()`, `ems_usb_disconnect()`, `ems_usb_open()`, `ems_usb_close()`, and `ems_usb_start_xmit()`. Protocol helpers include `ems_usb_command_msg()`, `ems_usb_write_mode()`, `ems_usb_control_cmd()`, `ems_usb_set_bittiming()`, `init_params_sja1000()`, `ems_usb_rx_can_msg()`, and `ems_usb_rx_err()`. USB callbacks are `ems_usb_read_bulk_callback()`, `ems_usb_write_bulk_callback()`, and `ems_usb_read_interrupt_callback()`.

## Control Flow
Probe allocates a CAN netdevice with `MAX_TX_URBS` echo slots, allocates interrupt and synchronous TX command buffers, initializes open SJA1000 acceptance filters, sends initial CAN parameters to the device, and registers the CAN device. Open first writes reset mode, calls `open_candev()`, submits up to ten bulk RX URBs, starts the interrupt URB, enables device notifications for CAN frames, state changes, and bus errors, then switches the controller to normal mode and starts the net queue.

RX bulk URBs may contain multiple CPC messages behind a four-byte header. `ems_usb_read_bulk_callback()` walks the advertised message count, validates message boundaries, dispatches CAN/RTR frames to `ems_usb_rx_can_msg()`, and dispatches state, bus error, and overrun messages to `ems_usb_rx_err()`. TX allocates a coherent bulk URB per skb, encodes standard/extended and RTR/data frames into CPC command messages, reserves a free echo context, anchors and submits the URB, and stops the net queue if host TX URBs or device free slots fall below thresholds. The interrupt endpoint refreshes `free_slots` and wakes the queue once the device has recovered enough capacity.

## State And Persistence
There is no persistent disk state. Runtime state is in `struct ems_usb`: active URB anchors, echo skb slots, current SJA1000 mode/timing parameters, and `free_slots`. CAN state is updated from SJA1000 status bits and SocketCAN restart requests. `unlink_all_urbs()` kills RX, TX, and interrupt activity and resets echo context indices.

## Dependencies And Integration Points
The driver integrates with Linux USB core, SocketCAN (`alloc_candev()`, `open_candev()`, `register_candev()`, echo skb helpers, CAN error skb helpers), netdevice ops, ethtool timestamp info, and SJA1000-compatible bit timing. USB endpoint numbers are hard-coded to bulk endpoint 2 and interrupt endpoint 1, matching the CPC-USB firmware protocol.

## Risks
RX parsing depends on correct CPC message counts and lengths; malformed packets are logged and parsing stops for that URB. TX context selection is linear and assumes queue stopping prevents exhaustion. `ems_usb_control_cmd()` sets `cmd.length = CPC_MSG_HEADER_LEN + 1`, which is unusual because the lower command helper also adds the CPC header length; this matches existing protocol expectations but is a maintenance trap. Error-state handling maps a non-bus-off/non-warning state to `CAN_STATE_ERROR_ACTIVE` while incrementing `error_passive`, which looks suspicious and should be regression-tested before modification. Resource cleanup frees coherent RX buffers by slots even if fewer URBs were submitted, relying on zeroed private memory for unused entries.

## Test Signals
Useful tests include probe/remove with the device attached, `ip link set canX type can bitrate ... up/down`, standard, extended, and RTR frame loopback, TX queue stop/wake under high load, unplug during RX/TX, bus-off and restart behavior, bus error reporting with `berr-reporting`, malformed short RX URB injection if USB fault tooling is available, and suspend-like disconnect paths that exercise anchored URB cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/ems_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/esd_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/esd_usb.c

## Purpose
`esd_usb.c` is a SocketCAN USB driver for esd electronics CAN-USB/2, CAN-USB/Micro, and CAN-USB/3 adapters. It supports up to two CAN nets per USB device, classical CAN on older products, and CAN FD on CAN-USB/3. It translates esd USB command records to CAN/CAN FD skbs, configures bit timing, configures ID acceptance filters, and exposes firmware, hardware, and net count sysfs attributes.

## Important APIs, Types, And Functions
`struct esd_usb` is the USB-device-level object with the shared RX anchor, endpoints, device version, net count, disconnect flag, and RX buffers. `struct esd_usb_net_priv` is the per-channel SocketCAN private state with `struct can_priv`, TX job counter, TX echo contexts, net index, previous bus state, and cached berr counters. The packed protocol union `union esd_usb_msg` covers version, RX, TX, TX done, filter, and baudrate messages.

Core paths include `esd_usb_probe()`, `esd_usb_probe_one_net()`, `esd_usb_disconnect()`, `esd_usb_open()`, `esd_usb_close()`, `esd_usb_start_xmit()`, `esd_usb_read_bulk_callback()`, `esd_usb_tx_done_msg()`, `esd_usb_rx_can_msg()`, `esd_usb_rx_event()`, `esd_usb_2_set_bittiming()`, `esd_usb_3_set_bittiming()`, and `esd_usb_get_berr_counter()`.

## Control Flow
Probe finds bulk endpoints, allocates `struct esd_usb`, sends a version command synchronously, waits for the version reply, records the number of nets and version, creates sysfs attributes, and registers one CAN netdevice per reported net. Per-net probe selects clock, timing constants, ctrlmode support, and bit timing callbacks based on the USB product ID.

Open calls `open_candev()`, sends an IDADD filter enabling all 11-bit and 29-bit IDs, lazily sets up shared RX URBs once, marks the channel active, and starts the net queue. RX bulk callbacks iterate variable-sized messages using `hdr.len` in 32-bit words. CAN RX records route by `rx.net`, allocate either CAN or CAN FD skbs, apply EFF/RTR/BRS/ESI flags, copy payload, and update RX stats. Event records with `ESD_USB_EVENT` and ID `ESD_USB_EV_CAN_ERROR_EXT` update cached error counters, optionally suppress repeated events when berr reporting is disabled, call `can_change_state()` for state transitions, and emit protocol error skbs for repeated diagnostic errors.

TX allocates one coherent `union esd_usb_msg`, encodes CAN or CAN FD payload, sets a nonzero handle with the echo index, stores an echo skb, increments `active_tx_jobs`, stops the queue when all contexts are in flight, and submits a bulk URB. Completion of the USB write only frees the DMA buffer and updates the software trans timestamp; actual TX success/error accounting happens when a device TX_DONE message returns.

## State And Persistence
No state is persisted outside the kernel. Device-level runtime state includes RX URB initialization, USB disconnect status, version, endpoint pipes, and the per-net pointer table. Per-net state includes active TX jobs, echo context ownership, old controller state, and berr counters. Close disables ID filters, sends a no-baudrate/reset command unless in USB disconnect, sets CAN state stopped, stops the queue, and closes the CAN device. Full URB cleanup happens in disconnect.

## Dependencies And Integration Points
This file uses USB core synchronous bulk messages for setup and asynchronous bulk URBs for data, SocketCAN netdevice APIs, CAN FD helpers, CAN error frame helpers, ethtool timestamp fallback, and sysfs `DEVICE_ATTR_RO` attributes. Product IDs drive feature selection: CAN-USB/3 gets FD support, 80 MHz clock, canonical nominal/data timing, and automatic TDC mode; CAN-USB/Micro and CAN-USB/2 use older BTR encoding and 36/60 MHz clocks.

## Risks
The driver trusts the device-reported `net_count` when probing per-net devices; invalid values above `ESD_USB_MAX_NETS` would be hazardous if firmware misbehaves. RX parsing advances by `hdr.len * sizeof(u32)` and only checks for overflow after dispatch, so zero-length messages could stall if ever emitted. TX completion indexes use `hnd & (ESD_USB_MAX_TX_URBS - 1)`, so handle integrity matters. Sysfs attribute creation failures are logged but not fatal and are not unwound individually. `unlink_all_urbs()` frees all RX coherent slots even if only a subset was allocated.

## Test Signals
Test with all three product families where possible: net count and sysfs values after probe, classical CAN standard/extended/RTR traffic, CAN FD with and without BRS on CAN-USB/3, listen-only and triple-sampling modes, ID filter enable/disable on open/close, TX_DONE success and error accounting, berr-counter reads, state transitions through warning/passive/bus-off, USB unplug during open channels, and repeated open/close across both channels sharing the same RX URB pool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/esd_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/Makefile

## Purpose
This Makefile wires the ETAS ES58x driver directory into Kbuild. When `CONFIG_CAN_ETAS_ES58X` is enabled, it builds the composite module object `etas_es58x.o` from the common core, devlink information support, ES581.4 adapter code, and ES58x FD adapter code.

## Important APIs, Types, And Functions
There are no functions or types in this file. Its important symbols are the Kbuild variables `obj-$(CONFIG_CAN_ETAS_ES58X)` and `etas_es58x-y`. The object list is `es58x_core.o es58x_devlink.o es581_4.o es58x_fd.o`.

## Control Flow
Kbuild evaluates the config-dependent `obj-*` assignment and links the four listed translation units into one loadable driver module. This causes the module metadata and `module_usb_driver()` registration from `es58x_core.c` to become the driver entry point while still allowing model-specific operator tables from `es581_4.c` and `es58x_fd.c` and devlink ops from `es58x_devlink.c` to resolve at link time.

## State And Persistence
The Makefile carries no runtime state. Its persistent effect is build composition: removing a file from `etas_es58x-y` would make exported `extern` symbols in `es58x_core.h` unresolved or silently remove feature families from the module if corresponding references were also changed.

## Dependencies And Integration Points
The file depends on the kernel Kbuild system and the `CONFIG_CAN_ETAS_ES58X` Kconfig symbol defined elsewhere. It integrates all ETAS ES58x source files into one module rather than building per-device modules.

## Risks
The main risk is accidental omission or ordering confusion during future refactors. `es58x_core.c` references `es58x_dl_ops`, `es581_4_param`, `es581_4_ops`, `es58x_fd_param`, and `es58x_fd_ops`, so all four objects are required. Adding a new hardware variant will require adding its object here and extending core device ID/operator selection.

## Test Signals
Build coverage is the primary signal: `CONFIG_CAN_ETAS_ES58X=m` or `=y` should compile and link all four objects. Runtime probe tests indirectly verify that the linked operator tables and devlink ops are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es581_4.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es581_4.c

## Purpose
`es581_4.c` is the ETAS ES581.4 model-specific adapter for the shared ES58x SocketCAN USB core. It implements the classic CAN-only wire format, command dispatch, channel enable/disable, timestamp request, echo handling, and TX message encoding for the dual-channel ES581.4 adapter.

## Important APIs, Types, And Functions
The file exports `const struct es58x_parameters es581_4_param` and `const struct es58x_operators es581_4_ops`, which are selected by `es58x_core.c` for non-FD ES581.4 devices. It uses protocol structures from `es581_4.h`, shared helpers from `es58x_core.h`, and unaligned little-endian accessors.

Important functions include `es581_4_get_msg_len()`, `es581_4_handle_urb_cmd()`, `es581_4_dispatch_rx_cmd()`, `es581_4_rx_can_msg()`, `es581_4_rx_err_msg()`, `es581_4_rx_event_msg()`, `es581_4_tx_ack_msg()`, `es581_4_echo_msg()`, `es581_4_tx_can_msg()`, `es581_4_set_bittiming()`, `es581_4_enable_channel()`, `es581_4_disable_channel()`, `es581_4_reset_device()`, and `es581_4_get_timestamp()`.

## Control Flow
Inbound URB commands are validated by the core before reaching `es581_4_handle_urb_cmd()`. This function checks the ES581.4 command type, then dispatches command IDs to command-return handlers, TX acknowledgments, RX CAN/error/event handlers, timestamp updates, echo processing, or device-error handling. RX CAN commands may contain an array of fixed maximum classic CAN records. The handler checks element count, validates that every record belongs to the same channel, drops packets if the netdevice is down, and forwards each frame to `es58x_rx_can_msg()`.

TX is bulk-oriented. On the first skb in a batch, `es581_4_tx_can_msg()` initializes a TX message header and the message count. Each skb appends a variable-sized `struct es581_4_tx_can_msg` based on DLC, stores raw CAN ID, packet index, flags, 1-based channel number, DLC, and payload, then updates URB length. ES581.4 rejects CAN FD skbs with `-EMSGSIZE`. Channel enable first sends bit timing/configuration with echo enabled and then sends the enable-channel command.

## State And Persistence
No persistent storage is used. Variant state is expressed through shared `struct es58x_priv` fields: packet indexes, TX batch count, CAN state, and channel index. ES581.4 uses 1-based device channel numbers, so all channel lookup and TX encode paths apply `ES581_4_CHANNEL_IDX_OFFSET`. Echo processing collects device timestamps, detects repeated or skipped packet indexes, increments TX drops for duplicates, and delegates echo skb completion to the core.

## Dependencies And Integration Points
This file depends on the ES58x core for USB submission, CRC/framing, netdevice lifecycle, SocketCAN skb creation, error handling, and timestamp conversion. It defines ES581.4 timing constants from the Stellaris LM3S5B91 CAN controller, a 50 MHz CAN clock, maximum 1 Mbps bitrate, classic CAN ctrlmode support with `CAN_CTRLMODE_CC_LEN8_DLC`, SOF values, FIFO mask, DQL limit, and bulk/URB sizing parameters.

## Risks
The ES581.4 wire protocol uses variable-length TX/RX classic CAN records, so length calculations around `es581_4_sizeof_rx_tx_msg()` are critical. Echo packet index recovery is strict: jumps return `-EBADMSG`, while duplicate previous indexes are dropped and counted. Command handlers rely on `rx_can_msg[0].rx_type` for RX dispatch, so malformed zero-length RX commands must be rejected by prior length checks. The comment in `es581_4_param` notes unresolved device CRC errors at larger FIFO values, so throughput tuning can affect stability.

## Test Signals
Exercise classic CAN standard, extended, RTR, and len8_dlc traffic; bulk TX with `xmit_more`; echo ordering under load; channel numbering for both ports; enable/disable and reset commands; timestamp request/response; malformed command length and unknown command IDs; bus error/event translation through the shared error path; and bus-off recovery via SocketCAN restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es581_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es581_4.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es581_4.h

## Purpose
`es581_4.h` defines the ES581.4 USB protocol ABI used by `es581_4.c` and the shared ES58x core. It contains channel counts, bulk limits, command IDs, RX record types, packed command payload layouts, and maximum URB command sizes for the classic CAN-only ES581.4 adapter.

## Important APIs, Types, And Functions
This header has no functions. Its key constants are `ES581_4_NUM_CAN_CH`, `ES581_4_CHANNEL_IDX_OFFSET`, `ES581_4_TX_BULK_MAX`, `ES581_4_RX_BULK_MAX`, and `ES581_4_ECHO_BULK_MAX`. It defines `enum es581_4_cmd_type`, `enum es581_4_cmd_id`, and `enum es581_4_rx_type`.

Important packed structures include `struct es581_4_tx_conf_msg`, `struct es581_4_tx_can_msg`, `struct es581_4_bulk_tx_can_msg`, `struct es581_4_echo_msg`, `struct es581_4_bulk_echo_msg`, `struct es581_4_rx_can_msg`, `struct es581_4_rx_err_msg`, `struct es581_4_rx_event_msg`, `struct es581_4_tx_ack_msg`, `struct es581_4_rx_cmd_ret`, and `struct es581_4_urb_cmd`. The sizing macros `ES581_4_URB_CMD_HEADER_LEN`, `ES581_4_TX_URB_CMD_MAX_LEN`, and `ES581_4_RX_URB_CMD_MAX_LEN` feed `struct es58x_parameters`.

## Control Flow
The header controls how `es581_4.c` parses inbound commands and encodes outbound ones. The top-level `struct es581_4_urb_cmd` starts with SOF, command type, command ID, and message length, followed by a packed union whose active member depends on command ID. The final CRC field is intentionally not addressed directly because command payloads are variable-length; the core uses offset/length helpers to place and verify CRC16.

## State And Persistence
No runtime state is stored here. The header defines wire-state fields such as packet indexes, timestamps, channel numbers, command return codes, TX free-entry counts, and error/event codes. These fields become runtime state only when copied into core `struct es58x_device` or per-channel `struct es58x_priv` logic.

## Dependencies And Integration Points
The structures depend on Linux fixed-width types, CAN payload constants, and ES58x shared enums declared in `es58x_core.h` even though this header is also included by that core header. It is tightly coupled to `ES58X_SIZEOF_URB_CMD()` and the core's CRC/header-length logic.

## Risks
The file defines packed USB ABI structures; field reordering, type widening, or alignment changes would break hardware communication. Some payload buffers are byte arrays rather than typed flexible arrays because individual CAN records are variable-sized; code using these fields must compute offsets carefully. The channel index offset is 1 for ES581.4, unlike ES58x FD devices, so mixing the two conventions is a common integration risk.

## Test Signals
Compile-time structure size checks are implicit through max URB size calculations. Runtime signals include correct parsing of RX message, RX error, RX event, echo, timestamp, and command-return frames; successful dual-channel traffic using 1-based device channel numbers; and CRC success for all encoded commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es581_4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.c

## Purpose
`es58x_core.c` is the shared SocketCAN USB implementation for ETAS ES581.4, ES582.1, and ES584.1 adapters. It owns USB probe/disconnect, devlink allocation, netdevice registration, URB allocation and resubmission, command CRC and framing, split-URB reassembly, timestamp calibration, TX batching, echo skb accounting, CAN/CAN FD RX conversion, and common CAN error handling. Variant files provide protocol-specific operators and parameters.

## Important APIs, Types, And Functions
The core binds USB IDs for ES581.4, ES582.1, and ES584.1 and selects `es581_4_param/es581_4_ops` or `es58x_fd_param/es58x_fd_ops` from `id->driver_info`. Exported helpers used by variants include `es58x_can_get_echo_skb()`, `es58x_tx_ack_msg()`, `es58x_rx_can_msg()`, `es58x_rx_err_msg()`, `es58x_rx_timestamp()`, `es58x_rx_cmd_ret_u8()`, `es58x_rx_cmd_ret_u32()`, and `es58x_send_msg()`.

Important internal functions include CRC helpers, `es58x_check_rx_urb()`, `es58x_split_urb()`, `es58x_handle_incomplete_cmd()`, `es58x_split_urb_try_recovery()`, USB callbacks, `es58x_get_tx_urb()`, `es58x_submit_urb()`, `es58x_alloc_rx_urbs()`, `es58x_free_urbs()`, `es58x_open()`, `es58x_stop()`, `es58x_start_xmit()`, `es58x_set_mode()`, `es58x_init_netdev()`, `es58x_init_es58x_dev()`, `es58x_probe()`, and `es58x_disconnect()`.

## Control Flow
Probe initializes a devlink-backed `struct es58x_device`, parses product information, registers devlink, and creates one or two CAN netdevices. Opening the first channel allocates RX URBs and requests a device timestamp to calibrate hardware timestamps to kernel real time. Each open channel calls `open_candev()`, sends a variant enable command, increments `opened_channel_cnt`, and starts the queue. Closing disables the channel, resets echo FIFO state, closes the CAN device, flushes pending TX batches, decrements the open count, and frees URBs when the last channel closes.

RX callbacks validate USB status, split arbitrary URB payloads into one or more ES58x commands, buffer incomplete commands across URBs, skip ES581.4 heartbeat bytes, verify SOF, length, maximum command size, and CRC, then call the variant `handle_urb_cmd()`. Severe parse or handler errors increment RX errors on all channels and may detach netdevices and reset the device.

TX uses Byte Queue Limits and `netdev_xmit_more()` to batch multiple skbs into one URB. `es58x_start_xmit()` obtains or reuses a TX URB, prevents mixed classical CAN and CAN FD batches, delegates encoding to the variant `tx_can_msg()`, stores an echo skb at `tx_head & fifo_mask`, and commits the URB when batching should stop. Completion of echo messages later advances `tx_tail`, applies hardware timestamps, completes BQL bytes, updates stats, and wakes the queue when echo FIFO pressure falls.

## State And Persistence
There is no disk persistence. Device runtime state includes devlink private memory, USB endpoints, RX/TX anchors, idle TX URB count, product versions, timestamp calibration fields, a temporary timestamp array, open channel count, and a reassembly buffer. Per-net state in `struct es58x_priv` tracks CAN state, devlink port, pending TX URB, TX head/tail counters, batch count, batch CAN FD type, passive-error repetition count, and channel index.

## Dependencies And Integration Points
The core depends on Linux USB, SocketCAN, netdevice, BQL/DQL, CRC16, devlink, CAN hardware timestamping ops, ethtool timestamp reporting, and variant operator tables. It delegates protocol layout to `es581_4.c` and `es58x_fd.c`, and product metadata to `es58x_devlink.c`.

## Risks
The RX reassembly path is complex and must remain robust against split, concatenated, stale, malformed, and CRC-bad URBs. `es58x_split_urb_try_recovery()` intentionally scans for the next SOF after corruption, which can recover traffic but risks false-positive resynchronization if payload bytes mimic SOF. TX batching requires strict echo FIFO invariants; packet index recovery drops stale echo skbs to resynchronize. Bus-off handling avoids self-recovery to prevent races with SocketCAN restart, so changes here can easily introduce echo skb races. URB idle-count accounting must stay matched with anchor operations.

## Test Signals
Run probe/remove for all supported products, open/close one and multiple channels, RX split and concatenated command scenarios, CRC failure and recovery paths, timestamp calibration and hardware timestamp visibility, BQL behavior under bulk TX, mixed CAN/CAN FD batching on FD hardware, echo packet loss/reordering recovery, bus-off and restart, USB unplug during active TX/RX, devlink info visibility, and KASAN/KCSAN-style stress around URB anchor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.h

## Purpose
`es58x_core.h` is the common contract for the ETAS ES58x driver. It declares hardware-independent enums, shared state structures, variant parameter/operator tables, command-size helpers, channel lookup helpers, CAN ID/flag conversion helpers, and cross-file function prototypes.

## Important APIs, Types, And Functions
Important constants include `ES58X_RX_URBS_MAX`, `ES58X_TX_URBS_MAX`, `ES58X_NUM_CAN_CH_MAX`, `ES58X_CHANNEL_IDX_NA`, `ES58X_CONSECUTIVE_ERR_PASSIVE_MAX`, and `ES58X_HEARTBEAT`. Shared enums cover device quirks (`enum es58x_driver_info`), echo mode, physical layer, samples per bit, sync edge, CAN frame flags, protocol errors, bus events, u8/u32 command return codes, and return-code categories.

The main structures are `union es58x_urb_cmd`, `struct es58x_priv`, `struct es58x_parameters`, `struct es58x_operators`, `struct es58x_sw_version`, `struct es58x_hw_revision`, and `struct es58x_device`. Inline/macros include `es58x_sizeof_es58x_device()`, `es58x_check_msg_len()`, `es58x_check_msg_max_len()`, `es58x_msg_num_element()`, `es58x_priv()`, `ES58X_SIZEOF_URB_CMD()`, `es58x_get_urb_cmd_len()`, `es58x_get_netdev()`, `es58x_get_raw_can_id()`, and `es58x_get_flags()`.

## Control Flow
The header shapes how the core and variants interact. `struct es58x_parameters` supplies static hardware limits and CAN capabilities. `struct es58x_operators` is the variant vtable used by the core for message length, command dispatch, header fill, TX encoding, channel enable/disable, reset, and timestamp request. Size-check macros are used by variant receive paths before they interpret packed USB payloads.

## State And Persistence
The header declares runtime state but does not allocate it. `struct es58x_device` persists for the USB interface lifetime and contains endpoint/anchor state, product version fields, timestamp calibration, temporary echo timestamp storage, open channel count, and the flexible RX reassembly buffer. `struct es58x_priv` persists per netdevice and tracks TX FIFO counters, pending TX URB, CAN state, and channel index.

## Dependencies And Integration Points
The header bridges Linux CAN, CAN dev, netdevice, USB, and devlink APIs. It includes both variant headers, which makes the shared `union es58x_urb_cmd` able to represent all supported hardware commands. Function prototypes connect `es58x_core.c`, `es58x_devlink.c`, `es581_4.c`, and `es58x_fd.c`.

## Risks
This header is ABI-sensitive inside the driver: changes to packed command unions, max sizes, FIFO masks, or helper semantics affect all variants. The mutual inclusion pattern between the core and variant headers requires care to avoid circular type assumptions. `es58x_get_flags()` casts skb data to `struct canfd_frame` for both CAN and CAN FD paths, relying on SocketCAN layout compatibility. `es58x_get_netdev()` silently applies variant-specific channel offsets supplied by callers; wrong offsets misroute channels.

## Test Signals
Compile all ETAS objects together, run sparse/endian checks around packed and unaligned fields, exercise both variant operator tables, verify command size checks reject short/oversized payloads, and test CAN/CAN FD flag conversion for EFF, RTR, BRS, ESI, and FD data frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_devlink.c

## Purpose
`es58x_devlink.c` provides product metadata parsing and devlink info reporting for ETAS ES58x adapters. It extracts firmware version, bootloader version, and hardware revision from a USB product information string, then exposes those values plus the USB serial number through devlink.

## Important APIs, Types, And Functions
The main exported items are `es58x_parse_product_info()` and `const struct devlink_ops es58x_dl_ops`. Internal helpers are `es58x_parse_sw_version()`, `es58x_parse_hw_rev()`, `es58x_sw_version_is_valid()`, `es58x_hw_revision_is_valid()`, and `es58x_devlink_info_get()`. The product info string index is `ES58X_PROD_INFO_IDX` with value 6.

## Control Flow
During probe, the core calls `es58x_parse_product_info()`. The function initializes version/revision fields to invalid sentinel values, retrieves USB string index 6 with `usb_cache_string()`, then attempts to parse firmware (`FW`), bootloader (`BL`), and hardware revision fields. Parsing is tolerant of two known software prefixes (`FW_Vxx.xx.xx`/`BL_Vxx.xx.xx` and `FW:xx.xx.xx`/`BL:xx.xx.xx`) by searching for the prefix and then the first digit. Hardware parsing searches for the only `H`, then the next colon, and scans an `axxx/xxx` revision. Failures log informational messages but do not abort device probe.

When users request devlink info, `es58x_devlink_info_get()` validates each parsed field. Valid firmware and bootloader versions are reported as running generic firmware and bootloader versions, valid board revision is reported as a fixed board revision, and the USB serial string is reported as the serial number.

## State And Persistence
No independent state is allocated here. The file mutates fields in `struct es58x_device`: `firmware_version`, `bootloader_version`, and `hardware_revision`. Those values live for the USB device lifetime and are not persisted beyond driver unload or unplug.

## Dependencies And Integration Points
This file depends on Linux USB string retrieval, character classification, devlink info APIs, and `struct es58x_device` from `es58x_core.h`. It is linked into the same module and its `es58x_dl_ops` pointer is passed to `devlink_alloc()` in the core.

## Risks
Parsing is based on vendor-specific free-form strings and is intentionally non-fatal. New firmware string formats may result in missing devlink version fields while the CAN driver still works. Sentinel values use unsigned fields assigned `-1`, and validity checks rely on them exceeding the maximum printable range. The hardware parser assumes the only relevant `H` belongs to the hardware revision prefix, which could fail for unexpected strings.

## Test Signals
Use devices or mocked USB descriptors with both known string formats, missing product info, malformed versions, malformed hardware revisions, and serial/no-serial cases. Verify `devlink dev info` shows firmware, bootloader, board revision, and serial only when parsed values are valid, and that probe continues when parsing fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.c

## Purpose
`es58x_fd.c` is the model-specific adapter for ETAS ES582.1 and ES584.1 CAN FD devices. It implements the CAN/CANFD command set, variable-length RX/TX record parsing, FD channel configuration, timestamp request, echo handling, and the exported operator/parameter tables consumed by the ES58x core.

## Important APIs, Types, And Functions
The file exports `const struct es58x_parameters es58x_fd_param` and `const struct es58x_operators es58x_fd_ops`. Key functions are `es58x_fd_cmd_type()`, `es58x_fd_get_msg_len()`, `es58x_fd_echo_msg()`, `es58x_fd_rx_can_msg()`, `es58x_fd_rx_event_msg()`, `es58x_fd_rx_cmd_ret_u32()`, `es58x_fd_tx_ack_msg()`, `es58x_fd_can_cmd_id()`, `es58x_fd_device_cmd_id()`, `es58x_fd_handle_urb_cmd()`, `es58x_fd_fill_urb_header()`, `es58x_fd_tx_can_msg()`, `es58x_fd_convert_bittiming()`, `es58x_fd_enable_channel()`, `es58x_fd_disable_channel()`, and `es58x_fd_get_timestamp()`.

## Control Flow
Inbound commands are dispatched first by command type: CAN, CANFD, or device. Channel commands look up the netdevice using 0-based channel indexes, then route enable/disable returns, TX acknowledgments, echo messages, RX messages, reset returns, and error/event messages. Device commands currently handle timestamp replies.

RX CAN payloads are concatenated variable-length records. `es58x_fd_rx_can_msg()` validates total buffer length, iterates until the message buffer is consumed, computes each record length from flags and DLC/len, checks for overrun and CAN FD max payload length, then calls the core `es58x_rx_can_msg()` when the netdevice is running. Echo messages validate consecutive 8-bit packet indexes reconstructed against the wider `tx_tail` counter and delegate echo skb completion to the core.

TX chooses CAN or CANFD command type based on the netdevice ctrlmode and skb type. Each encoded record stores an 8-bit packet index, raw CAN ID, ES58x flags, DLC or length, and payload. Channel enable converts nominal and data bit timings to hardware register-minus-one encoding, configures samples, physical layer, echo, listen-only/active mode, CAN FD or non-ISO FD mode, and optional automatic TDC fields, then sends an enable-channel command.

## State And Persistence
No persistent storage is used. The adapter reads and updates shared per-channel TX counters and CAN ctrlmode via `struct es58x_priv`. ES58x FD uses 0-based device channel numbering and supports one or two channels depending on product. Parameters define 80 MHz clock, 8 Mbps maximum bitrate, CAN FD and TDC auto support, FIFO mask 255, bulk max 100, and FD-specific SOF values.

## Dependencies And Integration Points
This file depends on the shared ES58x core for USB framing, CRC, URB submission, SocketCAN skb creation, echo management, state/error handling, and timestamp calibration. It depends on CAN FD helpers such as `canfd_sanitize_len()`, `can_fd_len2dlc()`, and `can_fd_tdc_is_enabled()`. Timing constants are based on Microchip SAM E70/S70/V70/V71 MCAN registers.

## Risks
Variable-length record parsing is the main risk: the code must distinguish CAN DLC and CAN FD length, reject oversized FD payloads, and advance by the computed structure length exactly. Echo indexes are only one byte on the wire, so reconstruction from `tx_tail` must remain correct across wraparound. FD devices cannot mix classic and FD frames in one bulk transmission, so core batching logic and `tx_can_msg_is_fd` must stay aligned with this adapter. Manual TDC is explicitly unsupported despite the hardware exposing fields.

## Test Signals
Exercise ES582.1 dual-channel and ES584.1 single-channel probe, classic CAN and CAN FD traffic, BRS/ESI flags, non-ISO FD ctrlmode, listen-only, triple sampling, automatic TDC configuration, variable-length RX batches, echo wraparound and ordering, bus error/event messages, timestamp replies, and reset command return handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.h

## Purpose
`es58x_fd.h` defines the USB wire protocol for ETAS ES582.1 and ES584.1 CAN FD devices. It provides channel counts, command type and command ID enums, controller mode bits, packed bit timing and channel configuration payloads, TX/RX/echo/error/ack payload layouts, and maximum URB command sizes.

## Important APIs, Types, And Functions
This header has no functions. Key constants include `ES582_1_NUM_CAN_CH`, `ES584_1_NUM_CAN_CH`, `ES58X_FD_NUM_CAN_CH`, `ES58X_FD_CHANNEL_IDX_OFFSET`, and bulk limits for TX, RX, and echo. Enums include `enum es58x_fd_cmd_type`, `enum es58x_fd_can_cmd_id`, `enum es58x_fd_dev_cmd_id`, and `enum es58x_fd_ctrlmode`.

Important packed structures are `struct es58x_fd_bittiming`, `struct es58x_fd_tx_conf_msg`, `struct es58x_fd_tx_can_msg`, `struct es58x_fd_rx_can_msg`, `struct es58x_fd_echo_msg`, `struct es58x_fd_rx_event_msg`, `struct es58x_fd_tx_ack_msg`, and `struct es58x_fd_urb_cmd`. Sizing macros include `ES58X_FD_CAN_CONF_LEN`, `ES58X_FD_CANFD_CONF_LEN`, `ES58X_FD_CAN_TX_LEN`, `ES58X_FD_CANFD_TX_LEN`, `ES58X_FD_CAN_RX_LEN`, `ES58X_FD_CANFD_RX_LEN`, `ES58X_FD_URB_CMD_HEADER_LEN`, `ES58X_FD_TX_URB_CMD_MAX_LEN`, and `ES58X_FD_RX_URB_CMD_MAX_LEN`.

## Control Flow
The command header includes SOF, command type, command ID, 0-based channel index, and message length. CAN and CANFD command types share many command IDs, while device-level commands carry timestamp replies. TX and RX CAN records are variable-sized because classic CAN uses DLC and up to eight bytes while CAN FD uses length and up to 64 bytes. The source adapter computes actual record lengths before appending or parsing records.

## State And Persistence
The header defines wire fields but stores no state. Runtime state includes packet indexes, timestamps, channel indexes, command return codes, TX free-entry counts, and CAN/CAN FD bit timing values after they are encoded into or decoded from these packed structures.

## Dependencies And Integration Points
It depends on Linux fixed-width types and CAN payload constants. The shared core includes this header in `union es58x_urb_cmd`, and `es58x_fd.c` uses its layouts to implement `es58x_fd_ops`. `ES58X_SIZEOF_URB_CMD()` from the core depends on the raw message and CRC field layout.

## Risks
Packed ABI structures are sensitive to layout changes. The `dlc`/`len` union in TX/RX records must be interpreted according to command type and flags. Controller mode bits include features that SocketCAN may not expose directly; unsupported bits should not be set casually. ES58x FD channel numbering is 0-based, unlike ES581.4.

## Test Signals
Compile and sparse-check packed layout usage, then verify CAN and CANFD command encoding, max URB size boundaries for 100-record batches, channel indexes for ES582.1 and ES584.1, and correct parsing of echo, event/error, timestamp, and TX acknowledgment records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/etas_es58x/es58x_fd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/f81604.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/usb/f81604.c

## Purpose
`f81604.c` is a SocketCAN USB driver for the Fintek F81604 USB-to-2CAN controller. It exposes two classical CAN netdevices, programs SJA1000-compatible controller registers through vendor USB control transfers, receives CAN data through per-port bulk endpoints, receives TX/error/status events through interrupt endpoints, supports termination control, and handles SJA1000-style bus errors.

## Important APIs, Types, And Functions
Top-level state is `struct f81604_priv`, which stores the two netdevices. Per-port state is `struct f81604_port_priv`, with `struct can_priv`, netdevice, clear-register work item, USB device/interface pointers, and a shared URB anchor. USB/status payloads are `struct f81604_int_data` and `struct f81604_can_frame` with standard and extended frame sublayouts.

Important functions include register helpers `f81604_write()`, `f81604_read()`, `f81604_update_bits()`, `f81604_sja1000_write()`, `f81604_sja1000_read()`, mode/config helpers `f81604_set_reset_mode()`, `f81604_set_normal_mode()`, `f81604_chipset_init()`, `f81604_set_bittiming()`, `f81604_set_mode()`, RX/TX handlers `f81604_process_rx_packet()`, `f81604_read_bulk_callback()`, `f81604_read_int_callback()`, `f81604_handle_tx()`, `f81604_handle_can_bus_errors()`, `f81604_start_xmit()`, lifecycle functions `f81604_open()`, `f81604_close()`, `f81604_probe()`, `f81604_disconnect()`, and termination helpers.

## Control Flow
Probe allocates private USB interface state, disables termination on both channels, allocates/registers two CAN netdevices, initializes work and URB anchors, configures clock/timing/termination callbacks and ctrlmode support, and assigns endpoint indices by `dev_port`. Open calls `open_candev()`, configures device mode for normal or one-shot TX, enters reset mode, initializes SJA1000 registers and acceptance filters, clears error counters and capture registers, submits per-port bulk RX URBs plus one interrupt URB, switches to normal mode, and starts the queue.

Bulk RX callbacks require exactly one `struct f81604_can_frame`, decode standard or extended IDs from big-endian shifted fields, apply RTR/EFF flags, copy data for non-RTR frames, update stats, and resubmit the URB. Interrupt callbacks process error/status bits first and TX interrupt second. Error handling builds a CAN error skb, maps overrun, warning, bus error, passive, arbitration lost, and bus-off conditions, schedules deferred register-clear work for ALC/ECC/overrun, and uses `can_change_state()`/`can_bus_off()`.

TX is single-buffered per channel: `f81604_start_xmit()` stops the queue, allocates a bulk URB and frame, encodes ID/DLC/RTR/EFF/data, stores echo skb index 0, submits the URB, and relies on the interrupt endpoint's TX interrupt to complete or free the echo skb and wake the queue. Write URB errors also free echo skb and wake the queue.

## State And Persistence
No disk state is used. Runtime state includes per-port CAN state, one echo skb slot, clear flags for deferred register clearing, anchored RX/interrupt URBs, and device termination bits. The hardware termination setting is changed during probe and through SocketCAN termination callbacks but is not persisted by the driver.

## Dependencies And Integration Points
The driver integrates with Linux USB control, bulk, and interrupt APIs; SocketCAN classical CAN APIs; SJA1000 register definitions from `linux/can/platform/sja1000.h`; netdevice ops; ethtool timestamp fallback; workqueues; and CAN termination configuration. It supports listen-only, triple sampling, one-shot, berr reporting, and presume-ack/self-test mode.

## Risks
TX uses a single echo slot and stops the queue, so missed TX interrupts or write completion races can wedge throughput unless error paths wake the queue correctly. Register access uses synchronous control transfers and port-offset arithmetic; wrong port mapping would program the wrong SJA1000 instance. Error capture registers require deferred dummy reads/writes to clear, so work cancellation during close matters. Probe calls `f81604_disconnect()` on partial failure, which assumes the interface private pointer exists. Disconnect unregisters/free netdevices but does not explicitly kill URBs unless close has already run through unregister semantics.

## Test Signals
Test two-channel probe, per-channel open/close, termination get/set behavior, standard/extended/RTR TX and RX, high-rate RX with four URBs, one-shot TX failure, interrupt-driven TX completion, listen-only and presume-ack modes, SJA1000 bit timing values, berr counter reads, arbitration lost, data overrun, bus warning/passive/bus-off transitions, USB unplug while interfaces are up, and partial probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/usb/f81604.c -->
