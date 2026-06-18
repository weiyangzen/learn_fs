# Research: subset-b-004049

This grouped report covers Siano common media driver files plus TTPCI/Hauppauge EEPROM helpers, UVC format mapping, and the v4l2 test-pattern-generator build hooks. Each section preserves the original source path and is bounded by reconciliation markers for per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.c

## Purpose
`smscoreapi.c` implements the shared Siano MDTV core used by bus-specific transports and higher-level clients such as `smsdvb-main.c`. It owns core device registration, hotplug notification, firmware and mode management, common DMA/buffer pools, client message routing, board setup hooks, IR startup, GPIO control, and module-global device/mode registries.

## Important APIs, Types, and Functions
The file defines private `smscore_device_notifyee_t`, `smscore_idlist_t`, `smscore_client_t`, and `smscore_registry_entry_t` objects around the public types from `smscoreapi.h`. Exported entry points include `smscore_register_device()`, `smscore_unregister_device()`, `smscore_start_device()`, `smscore_register_hotplug()`, `smscore_unregister_hotplug()`, `smscore_register_client()`, `smscore_unregister_client()`, `smsclient_sendrequest()`, `smscore_onresponse()`, `smscore_getbuffer()`, `smscore_putbuffer()`, `smscore_set_device_mode()`, `smscore_get_device_mode()`, `smscore_registry_getmode()`, board-id helpers, LED state, and old/new GPIO helpers.

Message support is centered on `smscore_translate_msg()`, the large `siano_msgs[]` table, `SMS_INIT_MSG()`, and completions embedded in `struct smscore_device_t`. Firmware mode lookup uses `smscore_fw_lkup`, `smscore_get_fw_filename()`, `smscore_load_firmware_from_file()`, and `smscore_load_firmware_family2()`.

## Control Flow
Transport drivers call `smscore_register_device()` with `smsdevice_params_t`; this allocates a `smscore_device_t`, initializes lists, locks, completions, and waitqueues, allocates either `kzalloc()` USB buffers or DMA-coherent buffers, wraps them in `smscore_buffer_t`, stores transport callbacks, records the devpath/type in the registry, and puts the device on `g_smscore_devices`.

`smscore_start_device()` chooses the persisted/default mode, calls `smscore_set_device_mode()`, applies board MTU/crystal configuration, notifies registered hotplug callbacks under `g_smscore_deviceslock`, and initializes IR if the board advertises an IR port. DVB registration is reached through this hotplug path.

Mode setting detects the current firmware mode with `MSG_SMS_GET_VERSION_EX_REQ`, optionally loads firmware with request-firmware and download chunks, initializes the device with `MSG_SMS_INIT_DEVICE_REQ`, updates `coredev->mode`, and clears `SMS_DEVICE_NOT_READY`. Family 2 firmware download sends reload/data/validity/trigger or reload-exec messages and waits on completions handled by `smscore_onresponse()`.

Incoming transport data arrives as a `smscore_buffer_t` in `smscore_onresponse()`. The header at `cb->p + cb->offset` is used to find a registered client by message type and destination id. If no client handles the buffer, core control responses complete the relevant core completion, IR sample indications are forwarded to `sms_ir_event()`, known harmless indications are ignored, and the buffer is returned to the pool.

## State and Persistence Behavior
Global state includes hotplug notifyees, live devices, and a registry keyed by `devpath`. The registry persists selected mode and type across re-registration within the module lifetime. Per-device state includes current mode, supported mode bitmask, firmware version, board id, LED state, IR state, common buffer pool, waitqueue, and completion objects.

Buffers are pooled in `coredev->buffers`; `smscore_getbuffer()` waits until a descriptor is available, while `smscore_putbuffer()` wakes the waitqueue and returns it to the list. Client routing state is a per-client id/type list protected by `clientslock`.

## Dependencies and Integration Points
The code depends on Linux firmware loading, DMA mapping, completions, waitqueues, list/mutex/spinlock primitives, media-controller conditionals, `sms-cards` board helpers, and `smsir`. It is the central integration layer between bus transports, board database, IR rc-core setup, DVB clients, firmware files declared by `MODULE_FIRMWARE()`, and Siano firmware protocol message ids.

## Risks and Test Signals
High-risk paths are firmware download sequencing, timeout handling, and response routing. `smscore_gpio_get_level()` stores the response in a single `coredev->gpio_get_res`, and the source comment explicitly notes a race between concurrent callers. `smscore_putbuffer()` wakes before adding the buffer back to the list, which is unusual but protected by the wait condition. `sms_ir_exit()` is called during unregister even if IR may not have initialized, so rc-core null handling and config stubs matter.

Useful test signals include successful firmware request and mode transition logs, hotplug callback registration/removal under module load/unload, DVB adapter creation after `smscore_start_device()`, completion of version/init/download requests within `SMS_PROTOCOL_MAX_RAOUNDTRIP_MS`, balanced buffer counts during unregister, and no duplicate client id/type registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.h

## Purpose
`smscoreapi.h` is the public contract for the Siano core. It declares firmware names, device families, device modes, protocol message ids, message wire structures, statistics structures, GPIO configuration structures, callback typedefs, and exported APIs used by Siano transports and DVB/IR clients.

## Important APIs, Types, and Functions
Key public types include `smscore_device_t`, `smscore_client_t`, `smscore_buffer_t`, `smsdevice_params_t`, `smsclient_params_t`, `sms_msg_hdr`, `sms_msg_data`, `sms_data_download`, `sms_version_res`, `sms_firmware`, `sms_stats`, `sms_isdbt_stats`, `sms_isdbt_stats_ex`, DVB RX/TX statistics structures, and `smscore_config_gpio`.

The header defines callback typedefs for hotplug, mode switching, transport send, firmware preload/postload, response handling, and removal. It exports core lifecycle APIs, client APIs, message send/receive hooks, buffer pool APIs, GPIO APIs, board id helpers, LED state, and message translation.

## Control Flow
The header models a layered driver: a transport fills `smsdevice_params_t`, receives a `smscore_device_t`, and exposes transport-specific send/mode/preload callbacks. Higher-level protocol clients register `smsclient_params_t` callbacks with an initial message id and data type, then send Siano protocol messages through `smsclient_sendrequest()`. Incoming buffers are delivered to `smscore_onresponse()` and routed back by message type/destination id.

## State and Persistence Behavior
`struct smscore_device_t` is the main in-memory state container. It stores lists of clients and buffers, common DMA memory metadata, transport context, devpath, mode, supported modes, all request completions, GPIO result state, board id, firmware metadata, IR state, LED state, and optional media-controller device pointer. No disk persistence is defined; the implementation keeps module-lifetime registry state by devpath.

## Dependencies and Integration Points
The header integrates Linux device/list/mutex/wait/timer/scatterlist primitives, media-device support, page alignment, and `smsir.h`. Its firmware names must match `smscoreapi.c` module firmware declarations and board-specific firmware tables in `sms-cards`. The message id enum is shared with firmware and therefore has ABI-like constraints.

## Risks and Test Signals
Because this header defines protocol wire layouts, padding, field size, and endian assumptions are critical. Changes to `enum msg_types`, `sms_msg_hdr`, or statistics structures can break firmware communication and DVB statistics parsing. The `SMS_PROTOCOL_MAX_RAOUNDTRIP_MS` spelling is preserved in code and should not be casually renamed without updating all users.

Test signals include compile coverage across `CONFIG_MEDIA_CONTROLLER_DVB`, `CONFIG_SMS_SIANO_RC`, and `CONFIG_SMS_SIANO_DEBUGFS`, successful structure use by `smscoreapi.c` and `smsdvb-main.c`, and compatibility with big-endian conversion helpers in `smsendian.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smscoreapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-debugfs.c

## Purpose
`smsdvb-debugfs.c` provides optional debugfs visibility into Siano DVB statistics. It creates a debugfs directory for USB Siano DVB devices and exposes a `stats` file that blocks or polls until the next statistics update is captured from the DVB response path.

## Important APIs, Types, and Functions
The private `struct smsdvb_debugfs` holds a kref, spinlock, one `PAGE_SIZE` text buffer, byte count, read-state flag, and waitqueue. Formatting functions are `smsdvb_print_dvb_stats()`, `smsdvb_print_isdb_stats()`, and `smsdvb_print_isdb_stats_ex()`. File operations are `smsdvb_stats_open()`, `smsdvb_stats_poll()`, `smsdvb_stats_read()`, and `smsdvb_stats_release()`. Public integration functions are `smsdvb_debugfs_create()`, `smsdvb_debugfs_release()`, `smsdvb_debugfs_register()`, and `smsdvb_debugfs_unregister()`.

## Control Flow
Module init in `smsdvb-main.c` calls `smsdvb_debugfs_register()`, creating `<debugfs>/usb/smsdvb`. On each DVB client creation, `smsdvb_debugfs_create()` checks that the root exists and the core device is USB, allocates debug state, creates a per-device directory named by `coredev->devpath`, creates the `stats` file, and installs print callbacks into `smsdvb_client_t`.

When the DVB response path updates statistics, it invokes the relevant print callback. The callback locks the debug state, refuses to overwrite an unread snapshot, emits key/value lines with `sysfs_emit_at()`, stores `stats_count`, unlocks, and wakes the waitqueue. A reader opening `stats` resets the snapshot state; `read()` blocks unless nonblocking, returns the buffered snapshot, and then marks EOF for the open instance.

## State and Persistence Behavior
State is per DVB client and transient. It stores only the latest unread formatted statistics page for the current open/read cycle. `kref` prevents freeing while file operations are active. There is no persistence beyond the debugfs lifetime.

## Dependencies and Integration Points
This file depends on debugfs, usb debug root, DVB headers, `smscoreapi.h`, and `smsdvb.h`. It is compiled only when enabled by config and otherwise replaced by no-op inline functions in `smsdvb.h`. It is tightly coupled to statistics structures from `smscoreapi.h` and callback slots in `smsdvb_client_t`.

## Risks and Test Signals
The one-page buffer and `sysfs_emit_at()` limit output size, but additions should watch for truncation. The design intentionally drops new stats if a previous snapshot is unread. `smsdvb_debugfs_create()` creates the file without checking `debugfs_create_*` errors, which is common for debugfs but worth noting. It only supports USB-root placement; comments flag missing SDIO-style support.

Test signals include successful creation/removal of `<debugfs>/usb/smsdvb/<devpath>/stats`, blocking reads that wake after statistics requests, poll returning readable once `stats_count` is set, no use-after-free during concurrent remove/read, and callbacks being cleared on release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-main.c

## Purpose
`smsdvb-main.c` adapts a Siano core device into Linux DVB devices. It registers a core hotplug callback, creates a DVB adapter/demux/dmxdev/frontend per arriving Siano device, maps DVB frontend operations into Siano firmware control messages, feeds transport-stream packets into the DVB demux, and converts firmware statistics into DVB property-cache metrics and legacy frontend reads.

## Important APIs, Types, and Functions
The file uses `struct smsdvb_client_t` from `smsdvb.h` as the per-adapter state. Important functions include `smsdvb_hotplug()`, `smsdvb_unregister_client()`, `smsdvb_onresponse()`, feed control (`smsdvb_start_feed()`, `smsdvb_stop_feed()`), statistics request/read helpers, frontend tuning (`smsdvb_dvbt_set_frontend()`, `smsdvb_isdbt_set_frontend()`, `smsdvb_set_frontend()`), frontend power callbacks, statistics translators, and module init/exit.

`smsdvb_fe_ops` advertises a "Siano Mobile Digital MDTV Receiver" frontend with DVB-T-like capabilities; delivery system is set to DVB-T or ISDB-T at registration based on the core mode.

## Control Flow
At module load, `smsdvb_module_init()` registers debugfs and the `smsdvb_hotplug()` callback with the core. For each arriving device, `smsdvb_hotplug()` allocates a client, registers a DVB adapter, initializes demux and dmxdev, copies frontend ops, registers the frontend, registers a Siano core client for `MSG_SMS_DVBT_BDA_DATA`, initializes completions, inserts the client in a global list, emits board hotplug/setup events, creates debugfs, and creates a media graph.

Frontend tuning clears status and stats, then dispatches to DVB-T or ISDB-T tuning based on core mode. DVB-T sends `MSG_SMS_RF_TUNE_REQ` with frequency, bandwidth enum, and 12 MHz crystal. ISDB-T sends `MSG_SMS_ISDBT_TUNE_REQ` with frequency, segment bandwidth, crystal, and segment index. Both paths try tuning with board LNA off first, read status, and retry with LNA enabled if needed.

Incoming messages are handled by `smsdvb_onresponse()`. TS data is passed to `dvb_dmx_swfilter()` only when feeds exist and the frontend has tuned. Tune responses complete `tune_done`. Signal/statistics indications update status/property caches, trigger board LED/event state, complete `stats_done`, and mark `has_tuned`.

## State and Persistence Behavior
Per-client state includes DVB adapter/demux/frontend objects, tune/stat completions, current `fe_status`, legacy BER/PER, frontend/uncorrected event state, throttling jiffies for statistics requests, feed user count, and `has_tuned`. Global state is a list of live DVB clients protected by `g_smsdvb_clientslock`. There is no disk persistence; state is rebuilt on hotplug.

## Dependencies and Integration Points
The file integrates the Siano core client API, board control helpers from `sms-cards`, Linux DVB adapter/demux/frontend APIs, media-controller graph creation, and optional debugfs callbacks. It depends on firmware message ids and statistics layouts from `smscoreapi.h`.

## Risks and Test Signals
Risk areas include concurrent feed start/stop updating `feed_users` without a local lock, statistics request throttling returning cached state, timeout behavior of `smsdvb_sendrequest_and_wait()`, and the LNA retune sequence changing board state. `smsdvb_read_signal_strength()` reads `power` before requesting fresh statistics, so the returned value may reflect the previous cached sample.

Test signals include successful DVB adapter/frontend registration after Siano hotplug, PID add/remove messages on demux feed changes, TS demux activity only after tune lock, frontend status transitions through board events, statistics properties using FE_SCALE_COUNTER/DECIBEL as expected, module unload releasing clients cleanly, and media graph creation success under media-controller builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb.h

## Purpose
`smsdvb.h` defines the per-DVB-client state and debugfs callback interface for the Siano DVB adaptation layer. It also documents the special per-slice reception-statistics structure used by firmware indications.

## Important APIs, Types, and Functions
The main type is `struct smsdvb_client_t`, which embeds DVB adapter, demux, dmxdev, and frontend objects alongside Siano core client pointers, frontend status, completions, legacy statistics, board-event state, statistics throttling, feed counters, tune state, and optional debugfs fields.

It defines callback typedefs for DVB, ISDB-T, and extended ISDB-T stats printers. `struct RECEPTION_STATISTICS_PER_SLICES_S` models the payload of `MSG_SMS_HO_PER_SLICES_IND` and combines fields from older Siano statistics types. The header declares debugfs functions when `CONFIG_SMS_SIANO_DEBUGFS` is enabled and provides no-op stubs otherwise.

## Control Flow
`smsdvb-main.c` allocates and fills `smsdvb_client_t` during hotplug. Incoming firmware statistics are converted and optionally passed through the callback pointers declared here. Debugfs creation installs these callback pointers; debugfs release clears them before removing files.

## State and Persistence Behavior
The header describes volatile runtime state only. `feed_users` and `has_tuned` gate TS demux delivery. `get_stats_jiffies` throttles statistics polling. `event_fe_state` and `event_unc_state` suppress repeated board notifications. Debugfs pointers are valid only while the optional debugfs node exists.

## Dependencies and Integration Points
This header relies on DVB types, `smscore_device_t`, `smscore_client_t`, and Siano statistics structures from `smscoreapi.h`. Its config stubs let `smsdvb-main.c` call debugfs hooks unconditionally while keeping debugfs optional.

## Risks and Test Signals
Because this header owns embedded DVB objects, lifetime order in `smsdvb-main.c` must match allocation and registration order. The stats callback pointers must be null-checked by callers before use, as the debugfs module can be disabled or released. Test signals include successful builds with and without `CONFIG_SMS_SIANO_DEBUGFS` and correct initialization of completions and event state before frontend use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsdvb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.c

## Purpose
`smsendian.c` provides Siano message byte-order fixups for big-endian hosts. On little-endian builds all functions compile to no-op bodies except for symbol export.

## Important APIs, Types, and Functions
The exported functions are `smsendian_handle_tx_message()`, `smsendian_handle_rx_message()`, and `smsendian_handle_message_header()`. They operate on `sms_msg_hdr`, `sms_msg_data`, and `sms_version_res` from `smscoreapi.h`.

## Control Flow
For transmit messages on big-endian builds, the helper inspects message type and converts 32-bit payload words from little-endian representation into CPU order before transport handling. `MSG_SMS_DATA_DOWNLOAD_REQ` receives special handling for its first data word. For receive messages, it converts `MSG_SMS_GET_VERSION_EX_RES` chip model as a 16-bit value, skips raw stream/data message payloads, and converts remaining 32-bit payload words. Header conversion adjusts message type, length, and flags from little-endian.

## State and Persistence Behavior
There is no persistent state. The functions mutate caller-provided message buffers in place.

## Dependencies and Integration Points
The file depends on architecture byteorder macros and the Siano message definitions. It is intended to be called by bus-specific transport code before sending and after receiving Siano firmware messages.

## Risks and Test Signals
Risks are concentrated in message-specific exceptions: raw TS/data messages must not be word-swapped, while structured control messages must be. The download request special case only converts `msg_data`, leaving payload bytes unchanged. Test signals require big-endian compile/runtime coverage, correct version response parsing, valid TS demux data on big-endian systems, and no double-swapping by transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.h

## Purpose
`smsendian.h` is the small public declaration header for Siano endian conversion helpers.

## Important APIs, Types, and Functions
It declares `smsendian_handle_tx_message()`, `smsendian_handle_rx_message()`, and `smsendian_handle_message_header()`, all taking raw message-buffer pointers.

## Control Flow
Transport code includes this header and invokes the helpers around firmware message transmission/reception. The implementation controls whether any actual work is done through `__BIG_ENDIAN`.

## State and Persistence Behavior
No state is declared. All behavior is in-place transformation of supplied buffers.

## Dependencies and Integration Points
The header includes `<asm/byteorder.h>` and is paired with `smsendian.c`. It deliberately avoids pulling in all Siano core types, because callers only need function prototypes.

## Risks and Test Signals
The primary risk is missing integration in a transport driver, which would make Siano firmware protocol messages fail on big-endian architectures. Test signals include successful builds on endian-diverse configurations and transport tests that exercise both control responses and raw payload messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsendian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.c

## Purpose
`smsir.c` integrates Siano firmware IR sample indications with the Linux rc-core raw IR stack. It allocates an rc device per Siano core device, configures the keymap from board data, and forwards raw pulse/space durations from firmware into rc-core.

## Important APIs, Types, and Functions
The public functions are `sms_ir_init()`, `sms_ir_exit()`, and `sms_ir_event()`. `sms_ir_init()` allocates `RC_DRIVER_IR_RAW`, sets names/physical path/parent, allowed protocols, map name, driver name, and registers the rc device. `sms_ir_event()` interprets the payload as signed 32-bit samples and stores `ir_raw_event` entries. `sms_ir_exit()` unregisters and frees the rc device.

## Control Flow
`smscore_start_device()` calls IR initialization when board configuration advertises an IR port, then sends `MSG_SMS_START_IR_REQ`. Later, `smscore_onresponse()` routes `MSG_SMS_IR_SAMPLES_IND` to `sms_ir_event()`, which converts each sample into duration plus pulse flag and calls `ir_raw_event_handle()`.

## State and Persistence Behavior
State lives in `coredev->ir`: rc device pointer, human-readable name, physical path, timeout, controller, and keymap. There is no persistence; rc-core owns runtime input-device registration after `rc_register_device()`.

## Dependencies and Integration Points
The file depends on `smscoreapi.h`, `sms-cards` for board names and rc maps, and Linux input/rc-core. It is conditionally exposed by `smsir.h` through `CONFIG_SMS_SIANO_RC`.

## Risks and Test Signals
`sms_ir_exit()` calls both `rc_unregister_device()` and `rc_free_device()` on `coredev->ir.dev`; rc-core ownership conventions should be checked for the target kernel version to avoid double-free concerns. `sms_ir_event()` assumes payload length is a multiple of four bytes and that negative samples represent pulses. Test signals include rc device creation with the expected name/path, decoded remote events from firmware samples, safe unload when IR was not initialized, and no events after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.h

## Purpose
`smsir.h` declares the Siano IR state and public hooks used by the core module. It also supplies stubs when rc-core support for Siano is disabled.

## Important APIs, Types, and Functions
`struct ir_t` stores the rc device pointer, name, physical path, optional rc keymap string, timeout, and controller id. The declared APIs are `sms_ir_init()`, `sms_ir_exit()`, and `sms_ir_event()`.

## Control Flow
`smscoreapi.c` embeds `struct ir_t` inside `smscore_device_t` and calls these hooks at device startup, message reception, and unregister. With `CONFIG_SMS_SIANO_RC` disabled, inline stubs make those calls compile away behaviorally.

## State and Persistence Behavior
The header defines per-device transient IR state. It does not own persistence or global lists.

## Dependencies and Integration Points
The header depends on Linux input and media rc-core types and forward-declares `smscore_device_t`. It is included by `smscoreapi.h`, so changes here affect the central Siano core type.

## Risks and Test Signals
The stubs must remain behaviorally safe for builds without RC support. The `phys` buffer is 32 bytes and receives `devpath` plus `/ir0`, so long devpaths can be truncated by safe string helpers. Test signals include builds with `CONFIG_SMS_SIANO_RC=y/m/n` and correct board keymap propagation when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/siano/smsir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.c

## Purpose
`ttpci-eeprom.c` reads and decodes encoded MAC addresses from 24C16-style EEPROMs on Siemens/Technotrend/Hauppauge PCI DVB cards so dvb_net can use a stable Ethernet address.

## Important APIs, Types, and Functions
Exported functions are `ttpci_eeprom_decode_mac()` and `ttpci_eeprom_parse_mac()`. Internal helpers are `check_mac_tt()`, `getmac_tt()`, and `ttpci_eeprom_read_encodedMAC()`. The decode algorithm uses a fixed 20-byte XOR mask, bit shifts derived from encoded bytes, and a checksum over the decoded intermediate data.

## Control Flow
`ttpci_eeprom_parse_mac()` reads 20 encoded bytes from I2C EEPROM address `0x50`, starting at offset `0xcc`, using a two-message `i2c_transfer()`. On read failure it zeroes the proposed MAC and returns the error. On successful read it decodes with `getmac_tt()`, validates the signature checksum, copies six decoded bytes into the caller's buffer, and logs the MAC.

`ttpci_eeprom_decode_mac()` exposes the same decode/validate logic for callers that already have the 20 encoded bytes.

## State and Persistence Behavior
The EEPROM provides persistent hardware state, but this file only reads it. It does not cache decoded addresses. On failure, caller-provided MAC storage is explicitly zeroed in the parse path.

## Dependencies and Integration Points
The file depends on Linux I2C, module infrastructure, string helpers, and `eth_zero_addr()`. It exports symbols for DVB PCI card drivers. The companion header declares the two public helpers.

## Risks and Test Signals
The debug macro is hardwired on via `#if 1`, so parse operations can print more than expected. The decode algorithm is format-specific; invalid EEPROM data returns `-ENODEV` and zeros the output in `parse_mac()`. The header parameter name typo does not affect ABI but is visible to readers.

Test signals include I2C transfer returning exactly two messages, known encoded vectors decoding to expected MACs, checksum failure paths zeroing output, and downstream dvb_net receiving nonzero valid MAC addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.h

## Purpose
`ttpci-eeprom.h` declares the exported TTPCI EEPROM MAC helpers for DVB card drivers.

## Important APIs, Types, and Functions
It declares `ttpci_eeprom_decode_mac(u8 *decodedMAC, u8 *encodedMAC)` and `ttpci_eeprom_parse_mac(struct i2c_adapter *adapter, u8 *propsed_mac)`. The latter parameter name contains a spelling error but the type and function name are correct.

## Control Flow
Callers either pass raw encoded EEPROM bytes to the decode helper or pass an I2C adapter to have the implementation read and decode the EEPROM.

## State and Persistence Behavior
The header defines no state. The implementation reads persistent EEPROM contents and writes caller-supplied buffers.

## Dependencies and Integration Points
It includes Linux types and I2C declarations and pairs with `ttpci-eeprom.c`. It is intended for media/DVB board drivers that need a MAC address for network-over-DVB support.

## Risks and Test Signals
The misspelled `propsed_mac` parameter can cause confusion but not compile failure. Test signals are compile users including this header and successful link resolution of exported symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/ttpci-eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/tveeprom.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/tveeprom.c

## Purpose
`tveeprom.c` decodes Hauppauge analog TV-card EEPROM contents into the generic `struct tveeprom` description used by V4L2/media drivers. It maps Hauppauge tuner ids, tuner format bitmasks, audio processors, decoder processors, model/revision/serial tags, optional MAC address, radio presence, and IR capability.

## Important APIs, Types, and Functions
The exported APIs are `tveeprom_hauppauge_analog()` and `tveeprom_read()`. Large static tables map Hauppauge tuner ids to Linux tuner constants and names, tuner-format bits to V4L2 standards, audio IC ids to `TVEEPROM_AUDPROC_*` values, and decoder IC ids to names. `hasRadioTuner()` overrides missing radio flags for known radio-capable tuners.

## Control Flow
`tveeprom_read()` resets the EEPROM offset by writing a zero byte to the I2C client, reads the requested byte count, and dumps the raw data at debug level.

`tveeprom_hauppauge_analog()` clears the output structure, detects known EEPROM start offsets for em28xx, cx2388x, and cx23418 layouts, then walks tagged packets until an end/checksum marker. It handles tags for comprehensive board info, serial ids, audio info, model/revision, video decoder, one or two tuners, radio, and IR. After parsing, it derives a revision string, corrects radio presence from tuner type when needed, maps tuner ids and format bits through static tables, stores Hauppauge model ids, and logs the decoded configuration.

## State and Persistence Behavior
The persistent state is the card EEPROM content supplied by the caller. This file does not cache results. It writes all decoded state into the caller-owned `struct tveeprom`, including tuner types, standard masks, serial/model/revision, MAC, radio, IR, audio processor, and decoder processor.

## Dependencies and Integration Points
The file depends on Linux I2C, V4L2 standards, tuner constants, `<media/tveeprom.h>`, and V4L2 common logging helpers. It is a shared helper for multiple analog capture driver families that read Hauppauge EEPROMs.

## Risks and Test Signals
Parsing trusts packet lengths enough to index into `eeprom_data` while walking a 256-byte address space; corrupt lengths can cause early warnings or risk out-of-range reads if callers pass less than expected. The end tag notes checksum but does not validate it. Unknown tags are debug-logged and skipped. `tveeprom_read()` returns `-1` instead of a specific errno.

Test signals include known EEPROM dumps decoding to expected model/revision/serial/tuner/audio/decoder fields, start-offset detection for em28xx/cx2388x/cx23418 samples, radio override messages for known tuner ids, correct handling of dual-tuner tags, and I2C read failures returning errors without filling stale data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/tveeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/uvc.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/uvc.c

## Purpose
`uvc.c` provides common USB Video Class format GUID to V4L2 pixel-format mapping. It lets UVC drivers convert 16-byte UVC format GUIDs from descriptors into kernel fourcc values.

## Important APIs, Types, and Functions
The static `uvc_fmts[]` table maps many `UVC_GUID_FORMAT_*` constants to `V4L2_PIX_FMT_*` values, including YUYV variants, NV12, MJPEG, planar YUV, greyscale/depth, Bayer patterns, RGB/BGR, H.264, HEVC, Intel RealSense formats, and compressed/confidence formats. The exported function is `uvc_format_by_guid(const u8 guid[16])`.

## Control Flow
Callers pass a 16-byte GUID. `uvc_format_by_guid()` linearly scans `uvc_fmts[]`, compares each GUID with `memcmp()`, and returns the matching descriptor pointer or `NULL` when unsupported.

## State and Persistence Behavior
The mapping table is static read-only module state. No runtime mutation or persistence exists.

## Dependencies and Integration Points
The file depends on Linux UVC GUID definitions, V4L2 pixel formats, and module/export infrastructure. It exports `uvc_format_by_guid()` GPL-only for UVC-related drivers.

## Risks and Test Signals
The search is linear but the table is small. Unsupported or vendor-new GUIDs return `NULL`; callers must handle that. Duplicate equivalent mappings, such as YUY2 variants and HEVC/H265 aliases, are intentional. Test signals include descriptor parsing tests for representative GUIDs, NULL behavior for unknown GUIDs, and build coverage when UVC GUID constants evolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/uvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Kconfig

## Purpose
This Kconfig fragment declares the common V4L2 test pattern generator library symbol.

## Important APIs, Types, and Functions
It defines `config VIDEO_V4L2_TPG` as a `tristate` symbol with no prompt, making it an internal selectable dependency rather than a direct user-facing option.

## Control Flow
Other media drivers or Kconfig entries select or depend on `VIDEO_V4L2_TPG`; the Makefile then uses the symbol to build the common test pattern generator object.

## State and Persistence Behavior
Kconfig state persists in the kernel build configuration as built-in, module, or disabled. This file has no runtime state.

## Dependencies and Integration Points
The fragment integrates with the kernel media Kconfig tree and the sibling Makefile. It is intentionally minimal because dependencies are managed by selecting users.

## Risks and Test Signals
Because there is no prompt or dependency expression, incorrect external selects can enable the library in unsuitable contexts. Test signals are Kconfig resolution for drivers that use the test pattern generator and correct module/built-in propagation to `v4l2-tpg.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Makefile

## Purpose
The Makefile builds the common V4L2 test pattern generator composite object.

## Important APIs, Types, and Functions
It defines `v4l2-tpg-objs := v4l2-tpg-core.o v4l2-tpg-colors.o` and adds `v4l2-tpg.o` to `obj-*` based on `CONFIG_VIDEO_V4L2_TPG`.

## Control Flow
When Kconfig enables `VIDEO_V4L2_TPG`, kbuild compiles the core and colors objects and links them into the `v4l2-tpg` object, either built-in or as a module according to the symbol value.

## State and Persistence Behavior
There is no runtime state. Build output depends entirely on the kernel configuration.

## Dependencies and Integration Points
This file integrates with kbuild and the `v4l2-tpg` source files in the same directory. It is paired with the directory Kconfig symbol.

## Risks and Test Signals
Any source file rename or split must update `v4l2-tpg-objs`. Test signals include successful `make M=drivers/media/common/v4l2-tpg` style builds and correct link inclusion when drivers select `VIDEO_V4L2_TPG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/v4l2-tpg/Makefile -->
