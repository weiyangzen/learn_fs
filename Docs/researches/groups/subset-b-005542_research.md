# subset-b-005542 Research

Grouped source research for USB Type-C/UCSI and USB/IP files under `sources/distributed-fs/ceph-client/drivers/usb`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_glink.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_glink.c

## Purpose

`ucsi_glink.c` adapts Qualcomm PMIC GLINK USBC messages into the common UCSI core. It lets platforms where the PD controller is exposed through PMIC GLINK register a UCSI device, handle connector-change notifications, and optionally publish connector orientation from per-port GPIOs.

## Important APIs, Types, and Functions

`struct pmic_glink_ucsi` stores the GLINK client, UCSI handle, read/write completions, transaction mutex, PD service state, work items, and up to three orientation GPIOs. `pmic_glink_ucsi_read()` sends `UC_UCSI_READ_BUF_REQ`, waits up to five seconds for `read_ack`, and copies from the cached UCSI buffer. `pmic_glink_ucsi_locked_write()` builds a UCSI v1 or v2 write request based on `ucsi->version`. The `ucsi_operations` callbacks expose version, CCI, message-in, sync/async control, connector setup, and connector-status orientation. `pmic_glink_ucsi_callback()` dispatches GLINK read/write responses and notifications. `pmic_glink_ucsi_pdr_notify()` tracks PD service up/down and schedules registration work.

## Control Flow

Probe allocates the UCSI object, attaches Qualcomm SoC quirks from the parent compatible, reads optional child-node orientation GPIOs, creates the PMIC GLINK client, and registers it. Runtime UCSI reads/writes serialize through `lock` and complete from GLINK response callbacks. GLINK notify indications schedule work that rereads CCI and calls `ucsi_notify_common()`. PDR service state drives `ucsi_register()` when PD is up and `ucsi_unregister()` when PD goes down.

## State and Persistence Behavior

State is in memory only. `pd_running` and `ucsi_registered` gate UCSI lifetime; `read_buf` caches the last GLINK read response long enough to satisfy a UCSI core read. No device settings are persisted by this driver.

## Dependencies and Integration Points

It depends on the Qualcomm PMIC GLINK auxiliary device, service-registry/PDR notifications, UCSI core, Type-C orientation APIs, firmware child nodes, GPIO descriptors, and SoC-specific quirk flags such as `UCSI_NO_PARTNER_PDOS` and `UCSI_DELAY_DEVICE_PDOS`.

## Risks and Test Signals

Risks include response-length mismatches during unknown UCSI-version probing, timeouts leaving UCSI commands failed, races between GLINK callbacks and teardown, bad child `reg` values, and PD service flaps. Test signals include UCSI registration only after PDR up, v1/v2 buffer selection, read/write timeout behavior, orientation GPIO changes reflected on connector status, and clean unregister on auxiliary removal or PD down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_glink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_huawei_gaokun.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_huawei_gaokun.c

## Purpose

`ucsi_huawei_gaokun.c` supports the Huawei MateBook E Go EC UCSI interface. It forwards EC UCSI mailboxes to the UCSI core and supplements incomplete firmware reporting with EC-side Type-C orientation, mux, DisplayPort pin assignment, and HPD bridge notifications.

## Important APIs, Types, and Functions

`struct gaokun_ucsi` owns the EC pointer, UCSI device, delayed registration work, notifier block, version, and port array. `struct gaokun_ucsi_port` stores per-port completion, lock, DP bridge, orientation, mux, pin assignment, SVID, and HPD bits. UCSI callbacks call `gaokun_ec_ucsi_read()` and `gaokun_ec_ucsi_write()`. `gaokun_ucsi_port_update()` decodes two-byte EC port records into Type-C/DP state. `gaokun_ucsi_refresh()` reads the EC aggregate register and updates the changed port. `gaokun_ucsi_notify()` handles EC USB and UCSI event classes.

## Control Flow

Probe reads the EC-reported port count, allocates per-port state, creates optional DP HPD bridges from child nodes, creates the UCSI object, and schedules delayed registration because the EC is unreliable early. The worker registers EC notifications and UCSI. EC UCSI events read CCI, call `ucsi_notify_common()`, then wait briefly for a matching USB event before forcing altmode handling. EC USB events complete all port USB acknowledgements and handle pending DP/HPD updates.

## State and Persistence Behavior

All state is runtime-only. Per-port locks protect decoded EC state used by connector callbacks. The delayed work acts as a boot-time stabilization mechanism; no firmware state is stored persistently.

## Dependencies and Integration Points

Dependencies include the `huawei-gaokun-ec` platform API, UCSI core, Type-C orientation APIs, USB PD/DP altmode definitions, DRM AUX HPD bridge helpers, auxiliary bus, firmware child-node `reg` properties, and EC PAN acknowledgement calls.

## Risks and Test Signals

Risks include EC register checksum/format assumptions, `GET_IDX()` returning no update, delayed UCSI registration failure leaving notifications absent, races between UCSI connector allocation and altmode events, and forced altmode enable when USB events are missing. Test signals include delayed registration, EC UCSI CCI notification, USB-event completion path, DP HPD bridge status transitions, orientation changes under `port->lock`, and removal cancelling delayed work before unregistering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_huawei_gaokun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_stm32g0.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_stm32g0.c

## Purpose

`ucsi_stm32g0.c` drives STMicroelectronics STM32G0 Type-C PD controllers over I2C. It exposes the controller as a UCSI device and optionally updates or restores controller firmware through the STM32 I2C bootloader.

## Important APIs, Types, and Functions

`struct ucsi_stm32g0` stores the normal I2C client, optional bootloader dummy client, bootloader state, firmware name, UCSI object, and suspend wakeup flags. Bootloader helpers implement ACK checking, command framing, address transfer, mass erase, flash read/write, and bootloader version probing. UCSI callbacks perform register-addressed I2C reads and write the `UCSI_CONTROL` register. `ucsi_stm32g0_fw_cb()` is the asynchronous firmware callback that compares embedded firmware metadata, switches to bootloader, erases, writes flash in 256-byte chunks, sets option bytes to boot main flash, and registers UCSI.

## Control Flow

Probe creates the UCSI object, checks for an optional `firmware-name`, creates the bootloader-address dummy client when needed, and first probes the normal UCSI version. If normal UCSI is unavailable and firmware is configured, it probes bootloader version and marks `in_bootloader`. Non-bootloader devices request the alert IRQ and register UCSI immediately. Firmware loading runs asynchronously to avoid blocking boot. IRQ handling reads CCI and calls `ucsi_notify_common()`.

## State and Persistence Behavior

Runtime state tracks whether the controller is in bootloader mode and whether suspend saw a wake event. The firmware-update path persists new controller firmware and option bytes in STM32 flash; normal UCSI operation has no file-backed persistence.

## Dependencies and Integration Points

The driver depends on I2C transfers, threaded IRQs, Linux firmware loading, device properties, UCSI core, PM sleep callbacks, and STM32 bootloader protocol constants from AN2606/AN4221 behavior.

## Risks and Test Signals

Risks include interrupted firmware flashing, malformed firmware footer keyword/version, bootloader ACK/NACK/BUSY handling, endian/alignment assumptions in option-byte access, IRQs during suspend, and cleanup when firmware request fails after UCSI registration. Test signals include normal UCSI probe, bootloader-only recovery, firmware no-op when versions match, mass-erase/write failure paths, IRQ CCI notification, suspend wake IRQ accounting, and remove behavior in both bootloader and normal states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_stm32g0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c

## Purpose

`ucsi_yoga_c630.c` adapts the Lenovo Yoga C630 EC UCSI implementation to Linux. It compensates for firmware quirks around DisplayPort alternate modes, duplicate partner altmodes, current CAM reporting, orientation, and HPD events.

## Important APIs, Types, and Functions

`struct yoga_c630_ucsi` holds the Lenovo EC, UCSI object, optional DP HPD bridge, notifier block, and UCSI version. Read callbacks use `yoga_c630_ec_ucsi_read()` to fetch CCI and message-in data; control writes pass commands to `yoga_c630_ec_ucsi_write()`. `yoga_c630_ucsi_sync_control()` fakes connector-1 DP altmode data, suppresses connector-2 altmode results, and fixes off-by-one current CAM responses. `yoga_c630_ucsi_read_port0_status()` reads the EC USB mux register, updates orientation, and notifies the HPD bridge.

## Control Flow

Probe allocates state, creates a DP HPD bridge only for child port 0, creates the UCSI object, reads EC UCSI version, registers an EC notifier, registers UCSI, and then adds the bridge. EC USB or HPD events update port-0 mux state and signal connector change. EC UCSI events read CCI and call `ucsi_notify_common()`.

## State and Persistence Behavior

The driver stores only runtime pointers and the reported UCSI version. Orientation and HPD are recomputed from the EC mux register on notifications. There is no persistent configuration.

## Dependencies and Integration Points

It integrates with `lenovo-yoga-c630` EC platform data, UCSI core, Type-C class, USB Type-C DP definitions, DRM AUX HPD bridge helpers, auxiliary bus, and firmware child-node `reg` properties.

## Risks and Test Signals

Risks include hard-coded assumptions that only connector 1 supports DP, EC altmode duplication hiding real data, off-by-one CAM adjustment underflow, and notification ordering between HPD and UCSI. Test signals include fake DP altmode query on connector 1, ignored altmode query on connector 2, duplicate SOP altmode trimming, mux register orientation mapping, HPD bridge notifications, and unwind after UCSI or bridge registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_yoga_c630.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/wusb3801.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/wusb3801.c

## Purpose

`wusb3801.c` is an I2C Type-C port-controller driver for the Willsemi WUSB3801. It programs the controller role/current policy, registers a Type-C port, reports partner/orientation/current state, and controls VBUS when acting as a source.

## Important APIs, Types, and Functions

`struct wusb3801` stores Type-C capability, current partner, regmap, VBUS regulator, port type, power mode, and VBUS state. Mapping helpers convert Type-C roles, preferred try roles, and power modes to WUSB3801 control bits and convert status bits back to Type-C orientation and current modes. `wusb3801_hw_init()` writes `CTRL0`; `wusb3801_hw_update()` reads `STAT`, manages VBUS, registers/unregisters partners, and updates Type-C role/orientation/opmode. Type-C operations implement `try_role` and `port_type_set`.

## Control Flow

Probe initializes regmap and VBUS regulator, reads the `connector` child node, parses Type-C firmware capability and `typec-power-opmode`, programs hardware, registers the Type-C port, mirrors initial status, and requests a threaded IRQ. IRQs clear the interrupt register and refresh status. Removal frees the IRQ, unregisters any partner, unregisters the port, and disables VBUS if needed.

## State and Persistence Behavior

The driver keeps runtime partner and VBUS state to avoid duplicate registrations and regulator toggles. Hardware registers hold current role policy while powered; no kernel persistence is provided.

## Dependencies and Integration Points

It depends on I2C, regmap, regulator framework, Type-C class, firmware Type-C connector bindings, IRQ delivery, and the `willsemi,wusb3801` OF compatible.

## Risks and Test Signals

Risks include enabling `vbus_on` even if regulator enable fails, missing IRQ support, unsupported PD power mode, partner registration failures leaving `partner_type` advanced, and ambiguous orientation status `BOTH`. Test signals include probe with every port type/current mode, IRQ attach/detach transitions, source VBUS enable/disable, role/type sysfs operations, audio/debug accessory registration, and remove while VBUS is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/wusb3801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usb-skeleton.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usb-skeleton.c

## Purpose

`usb-skeleton.c` is a sample USB bulk device driver that demonstrates matching a USB device, exposing a minor-backed character device, and safely performing bulk IN/OUT I/O with URBs, autosuspend, disconnect handling, and reset handling.

## Important APIs, Types, and Functions

`struct usb_skel` stores USB device/interface references, a write limit semaphore, submitted-URB anchor, one reusable bulk-in URB/buffer, endpoint addresses, error state, read waitqueue, kref, and I/O mutex. File operations are `skel_open()`, `skel_release()`, `skel_flush()`, `skel_read()`, and `skel_write()`. `skel_do_read_io()` submits the bulk-in URB; callbacks record errors or completion length. `skel_probe()` discovers endpoints and registers `skel%d`; `skel_disconnect()` deregisters and kills URBs.

## Control Flow

Open resolves the USB interface from the minor, resumes the device via autosuspend, and increments the kref. Reads serialize through `io_mutex`, wait for any ongoing read, consume cached bulk-in bytes, or submit a new read. Writes throttle concurrent URBs with `limit_sem`, allocate coherent buffers, anchor the URB, and submit bulk OUT. Flush and suspend call `skel_draw_down()` to wait for or kill outstanding writes and the read URB.

## State and Persistence Behavior

State is per connected interface and reference-counted. Errors are latched and reported once to userspace; `disconnected` prevents new submissions after unplug. No data persists beyond runtime buffers.

## Dependencies and Integration Points

It integrates with USB core device matching, USB class minor registration, userspace char-device I/O, autosuspend PM, URB anchoring, wait queues, krefs, and reset callbacks.

## Risks and Test Signals

Risks include single-reader design, partial read caching edge cases, user-triggered memory pressure despite `WRITES_IN_FLIGHT`, disconnect races, and using placeholder vendor/product IDs. Test signals include probe endpoint validation, blocking and nonblocking read/write behavior, error propagation from URB callbacks, unplug during active I/O, suspend/reset drawdown, and kref release after last close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usb-skeleton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/Kconfig

## Purpose

`usbip/Kconfig` defines the selectable kernel configuration surface for USB/IP core, virtual host controller, host-side exported-device driver, virtual USB device controller, and optional debug output.

## Important APIs, Types, and Functions

The entries are `USBIP_CORE`, `USBIP_VHCI_HCD`, `USBIP_VHCI_HC_PORTS`, `USBIP_VHCI_NR_HCS`, `USBIP_HOST`, `USBIP_VUDC`, and `USBIP_DEBUG`. `USBIP_CORE` depends on `NET` and selects `USB_COMMON` and `SGL_ALLOC`. VHCI and host depend on `USBIP_CORE && USB`; VUDC depends on `USBIP_CORE && USB_GADGET`.

## Control Flow

There is no runtime flow. Build-time selection determines which modules and helper objects are compiled and whether debug macros expand with `-DDEBUG`.

## State and Persistence Behavior

Kconfig values persist in the kernel configuration. `USBIP_VHCI_HC_PORTS` and `USBIP_VHCI_NR_HCS` shape compiled-in port/controller counts and therefore the sysfs attach surface.

## Dependencies and Integration Points

This file integrates USB/IP with kernel networking, USB host, USB gadget, scatterlist allocation, and debug build infrastructure. Userspace USB/IP tools depend on the selected kernel pieces being present.

## Risks and Test Signals

Risks include invalid assumptions about high port/controller counts, missing core selection for dependent drivers, and debug builds exposing verbose logs. Test signals are allmodconfig/build coverage, module names matching help text, valid Kconfig ranges, and sysfs port count matching configured VHCI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/Makefile

## Purpose

`usbip/Makefile` maps USB/IP Kconfig symbols to kernel modules and object lists. It defines the build composition for the core, virtual host controller, host export driver, and virtual USB device controller.

## Important APIs, Types, and Functions

`ccflags-$(CONFIG_USBIP_DEBUG)` adds `-DDEBUG`. `usbip-core-y` contains `usbip_common.o` and `usbip_event.o`. `vhci-hcd-y` contains `vhci_sysfs.o`, `vhci_tx.o`, `vhci_rx.o`, and `vhci_hcd.o`. `usbip-host-y` contains `stub_dev.o`, `stub_main.o`, `stub_rx.o`, and `stub_tx.o`. `usbip-vudc-y` includes VUDC device, sysfs, tx, rx, transfer, and main objects.

## Control Flow

There is no runtime flow. The object order links shared logic with driver-specific entry points and controls which modules are emitted for selected configuration symbols.

## State and Persistence Behavior

Build artifacts reflect Kconfig state. No runtime state is defined here.

## Dependencies and Integration Points

It integrates Kbuild with the Kconfig symbols and keeps source files grouped by module boundary. It is the point where common USB/IP symbols become exported from `usbip-core` for `vhci-hcd`, `usbip-host`, and `usbip-vudc`.

## Risks and Test Signals

Risks include missing object files causing unresolved symbols, debug flag mismatch, or module composition drift when adding new files. Test signals are module build success for each symbol combination and `modinfo` showing expected module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub.h -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub.h

## Purpose

`stub.h` declares the host-side USB/IP private state shared by `stub_dev.c`, `stub_main.c`, `stub_rx.c`, and `stub_tx.c`. It models exported physical USB devices, in-flight remote URBs, unlink replies, and bus-id selection state.

## Important APIs, Types, and Functions

`struct stub_device` wraps the physical `usb_device`, common `usbip_device`, stable `devid`, URB lifecycle lists (`priv_init`, `priv_tx`, `priv_free`), unlink lists, locks, and TX waitqueue. `struct stub_priv` tracks one remote submit request, possibly split across multiple URBs, with SG state and unlinking status. `struct bus_id_priv` records user-selected bus IDs and binding status. Prototypes expose bus-id lookup, cleanup, RX/TX loops, completion, and unlink response enqueueing.

## Control Flow

The header defines list ownership: submit requests enter `priv_init`, completions move to `priv_tx`, sent completions move to `priv_free`, and cleanup can drain all lists. Unlink requests are queued separately for TX.

## State and Persistence Behavior

State is entirely in memory and tied to module/device lifetime. Bus-id names persist only while the module is loaded and are manipulated through driver sysfs files.

## Dependencies and Integration Points

It depends on USB core, common USB/IP transport definitions, spinlocks, lists, wait queues, and slab allocation. It is the internal ABI for the host export module.

## Risks and Test Signals

Risks include list-state invariants, lock ordering around `priv_lock`, refcount/lifetime bugs for physical devices, and bus-id status transitions. Test signals are compile coverage of all stub objects, export/import attach cycles, unlink races, SG splitting cleanup, and module unload rebind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_dev.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_dev.c

## Purpose

`stub_dev.c` binds selected physical USB devices for export through USB/IP. It exposes per-device sysfs controls, accepts a userspace-provided TCP socket, starts host RX/TX threads, and implements shutdown/reset/unusable event operations.

## Important APIs, Types, and Functions

Sysfs attributes are `usbip_status` and write-only `usbip_sockfd`. `stub_device_alloc()` initializes `struct stub_device`, common event-handler ops, URB/unlink lists, and stable `devid`. `stub_probe()` checks the bus-id table, rejects hubs and VHCI devices, sets driver data, and claims the hub port. `stub_shutdown_connection()`, `stub_device_reset()`, and `stub_device_unusable()` are common event callbacks. `stub_disconnect()` releases the hub port, shuts down active USB/IP state, and restores bus-id status.

## Control Flow

Userspace first adds a busid through driver sysfs, causing probe to claim matching devices. Writing a nonnegative socket fd to `usbip_sockfd` validates availability and socket type, creates `stub_rx` and `stub_tx` kthreads, stores socket/task state, and marks the device used. Writing `-1` queues a down event. Disconnect or removal queues a removed event and waits for event handling unless already inside the event handler.

## State and Persistence Behavior

Per-device state includes socket, task pointers, status, URB lists, and bus-id shutdown flags. It does not persist beyond module/device lifetime; userspace must re-add bus IDs after reload.

## Dependencies and Integration Points

It integrates with USB device-driver binding, hub port claiming, sysfs, sockets via `sockfd_lookup()`, kthreads, the common USB/IP event handler, and `stub_main` bus-id tables.

## Risks and Test Signals

Risks include socket/task setup races, leaving a claimed hub port on error, disconnect during reset, event-handler reentrancy, and bus-id status restoration. Test signals include export attach/detach, invalid fd/type handling, hub/VHCI rejection, physical disconnect during active export, remote reset event, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_main.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_main.c

## Purpose

`stub_main.c` owns the USB/IP host module lifecycle, bus-id matching table, driver sysfs controls for selecting/rebinding devices, and common cleanup of host-side URB private data.

## Important APIs, Types, and Functions

`busid_table` holds up to 16 `struct bus_id_priv` entries protected by a global table lock and per-entry locks. `match_busid_store()` parses `add ` and `del ` commands. `rebind_store()` releases an exported device back to normal driver matching. `stub_free_priv_and_urb()` frees setup packets, buffers, SG lists, URBs, and `stub_priv` cache entries. `stub_device_cleanup_urbs()` kills and frees all pending/completed/free URB state. Module init creates the `stub_priv` slab cache, registers `stub_driver`, and creates sysfs files.

## Control Flow

Userspace writes bus IDs into `match_busid`; later USB core probing consults this table in `stub_dev.c`. Deleting a busid either clears an idle entry or marks active entries for removal. During module exit, the USB device driver is deregistered, causing disconnect callbacks, then selected devices may be rebound to ordinary drivers.

## State and Persistence Behavior

Bus-id selections, shutdown flags, device pointers, and interface counts are module-resident only. The slab cache persists while the module is loaded and backs all remote submit state.

## Dependencies and Integration Points

It depends on USB device-driver registration, sysfs driver attributes, device attach/rebind, scatterlist freeing, the `stub.h` contract, and the common USB/IP core.

## Risks and Test Signals

Risks include fixed `MAX_BUSID` capacity, newline/termination handling in busid parsing, lock ordering between table and entry locks, rebind behavior differing for built-in versus module builds, and cleanup of split SG requests. Test signals include add/del/rebind sysfs operations, table full handling, module unload with active exports, and leak checks around `stub_priv_cache`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_rx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_rx.c

## Purpose

`stub_rx.c` is the host-side USB/IP receive path. It receives remote submit/unlink PDUs, validates them against the exported device, reconstructs local URBs, handles control requests requiring local USB core APIs, receives payloads/iso descriptors, and submits or unlinks URBs on the physical device.

## Important APIs, Types, and Functions

Special-request detectors/tweakers handle `CLEAR_FEATURE(ENDPOINT_HALT)`, `SET_INTERFACE`, `SET_CONFIGURATION`, and port reset. `stub_recv_cmd_unlink()` finds pending submits, marks them unlinking, and calls `usb_unlink_urb()`, or queues an immediate unlink reply. `stub_priv_alloc()` creates request state in `priv_init`. `get_pipe()` maps USB/IP endpoint/direction to a real pipe and validates isochronous packet count. `masking_bogus_flags()` constrains wire-provided URB flags. `stub_recv_cmd_submit()` allocates buffers or SG lists, optionally splits SG into multiple URBs, unpacks the PDU, receives data, and submits.

## Control Flow

`stub_rx_loop()` repeatedly calls `stub_rx_pdu()` until stopped or an event appears. Each PDU header is read exactly, endian-corrected, validated by stable `devid` and `SDEV_ST_USED`, and dispatched by command. Submit handling allocates state before payload receive so event cleanup can free it. Completion flows later through `stub_tx.c`.

## State and Persistence Behavior

Remote submit state lives in `stub_priv` lists. For HCDs without SG support, one remote request is split into several URBs and reassembled by TX. There is no persistent state.

## Dependencies and Integration Points

It depends on common USB/IP wire helpers, USB core URB submission/unlink/control APIs, SG allocation, physical endpoint descriptors, and host TX completion queues.

## Risks and Test Signals

Risks include malformed remote headers, negative or oversized lengths, SG zero-length cases, special-control requests changing device configuration mid-stream, unlink completion races, and wire-supplied isochronous metadata. Test signals include valid/invalid endpoint submit, OUT payload receive, IN submit completion, unlink before and after completion, SG split path, special control requests, and TCP/error event generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_tx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_tx.c

## Purpose

`stub_tx.c` is the host-side transmit path. It converts completed physical URBs and unlink outcomes into USB/IP return PDUs and sends them to the remote VHCI client.

## Important APIs, Types, and Functions

`stub_complete()` is the USB completion callback. It records final status, waits for all split SG URBs when needed, converts unlinking requests into unlink replies, or moves normal completions to `priv_tx`. `setup_ret_submit_pdu()` and `setup_ret_unlink_pdu()` build return headers. `stub_send_ret_submit()` sends RET_SUBMIT headers, IN payload data, packed isochronous descriptors, and reassembled split-SG data. `stub_send_ret_unlink()` sends RET_UNLINK headers. `stub_tx_loop()` drains submit replies before unlink replies and waits on `tx_waitq`.

## Control Flow

Completions enqueue work under `priv_lock` and wake the TX thread. The TX loop drains all normal completions, freeing `priv_free` entries after successful send, then drains unlink completions. Send failures queue TCP error events. The ordering intentionally lets late unlink requests see the already completed submit result before the unlink reply.

## State and Persistence Behavior

The file moves `stub_priv` through `priv_tx` and `priv_free`, and `stub_unlink` through `unlink_tx` and `unlink_free`. State is transient per connection.

## Dependencies and Integration Points

It depends on kernel sockets, common PDU packing/endian helpers, isochronous descriptor packing, scatterlist iteration, stub RX list conventions, and USB completion context rules.

## Risks and Test Signals

Risks include partial `kernel_sendmsg()` writes, inconsistent isochronous actual-length sums, freeing URB state while a connection closes, split-SG status aggregation, and allocating `kvec` arrays in response to hostile URBs. Test signals include IN/OUT completions, isochronous IN returns, split-SG reassembly, unlink races, TCP send failure, and cleanup after device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.c

## Purpose

`usbip_common.c` implements USB/IP core helpers shared by VHCI, host stub, and VUDC modules: debugging, reliable socket receive, URB/PDU packing, endian conversion, isochronous descriptor handling, and transfer-buffer receive.

## Important APIs, Types, and Functions

Exports include `usbip_debug_flag`, `dev_attr_usbip_debug`, `usbip_dump_urb()`, `usbip_dump_header()`, `usbip_recv()`, `usbip_pack_pdu()`, `usbip_header_correct_endian()`, `usbip_alloc_iso_desc_pdu()`, `usbip_recv_iso()`, `usbip_pad_iso()`, and `usbip_recv_xbuff()`. Internal flag mapping translates unstable kernel `URB_*` flags to stable UAPI `USBIP_URB_*` bits. `usbip_pack_ret_submit()` clamps response packet counts to the originally allocated URB descriptor count.

## Control Flow

Transmit paths pack URB fields into PDUs, map flags, append payload/iso descriptors, and endian-correct before send. Receive paths read exact socket payload sizes with `MSG_WAITALL`, endian-correct headers/descriptors, unpack URB fields, receive payload into flat buffers or SG entries, validate isochronous packet counts/length sums, and restore padding for isochronous transfers.

## State and Persistence Behavior

Only debug flag state persists at module runtime via module parameter/sysfs. Transfer helpers are stateless, except for mutating URB fields from wire data and raising USB/IP events on TCP/protocol failures.

## Dependencies and Integration Points

It depends on kernel sockets, USB core URBs, scatterlist helpers, byteorder helpers, module parameters, UAPI USB/IP definitions, and `usbip_event.c` for error propagation.

## Risks and Test Signals

Risks include accepting malicious remote lengths, integer overflow in descriptor sizing, partial socket reads, SG copy mismatch, isochronous OOB access, and kernel flag/UAPI drift. Test signals include endian round trips, all four PDU commands, IN/OUT payload receive, SG payload receive, invalid iso packet counts, mismatched iso total length, debug sysfs read/write, and error events by side.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.h -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.h

## Purpose

`usbip_common.h` defines the shared USB/IP protocol structures, debug flags, event bits, common device state, exported helper prototypes, and small inline helpers used by all USB/IP kernel modules.

## Important APIs, Types, and Functions

It declares wire PDUs: `usbip_header_basic`, `usbip_header_cmd_submit`, `usbip_header_ret_submit`, `usbip_header_cmd_unlink`, `usbip_header_ret_unlink`, and `usbip_header`. It defines `usbip_iso_packet_descriptor`, side enum values for VHCI/STUB/VUDC, event masks, side-specific event combinations, and `struct usbip_device` with status, locks, sysfs mutex, socket, RX/TX tasks, event bits, event ops, and optional KCOV handle. It also provides debug macros and prototypes for common receive/pack/event helpers.

## Control Flow

The header has no standalone runtime flow, but it establishes the state machine used by all modules: connection state lives in `usbip_device`, transport threads observe `event`, and event operations perform shutdown/reset/unusable handling.

## State and Persistence Behavior

`struct usbip_device` is per exported/virtual device and runtime-only. Kconfig-dependent KCOV handle state permits remote coverage attribution during socket-driven processing.

## Dependencies and Integration Points

It integrates Linux USB, networking, device, waitqueue, task, spinlock, KCOV, and UAPI USB/IP definitions. It is the central internal ABI between core, host stub, VHCI, and VUDC.

## Risks and Test Signals

Risks include changing packed wire structs, event-mask semantics, status lock rules, debug flag bit overlap, and task/socket lifetime contracts. Test signals are cross-module compile coverage, UAPI compatibility tests, attach/detach event behavior across all sides, and KCOV-enabled/disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_event.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_event.c

## Purpose

`usbip_event.c` provides the shared USB/IP event handler. It coalesces shutdown/reset/unusable events per `usbip_device`, serializes handling through a single workqueue, and lets connection threads and sysfs paths wait for teardown completion.

## Important APIs, Types, and Functions

`struct usbip_event` links devices into `event_list`. `set_event()` and `unset_event()` update `ud->event` under the device lock. `event_handler()` drains pending devices, locks `ud->sysfs_lock`, runs `eh_ops.shutdown`, `eh_ops.reset`, and `eh_ops.unusable` in order, clears bits, and wakes `eh_waitq`. Exported APIs are `usbip_start_eh()`, `usbip_stop_eh()`, `usbip_init_eh()`, `usbip_finish_eh()`, `usbip_event_add()`, `usbip_event_happened()`, and `usbip_in_eh()`.

## Control Flow

Core module init creates a singlethread workqueue. Device setup initializes waitqueue and event bits. Any side queues an event with `usbip_event_add()`, which sets bits, avoids duplicate queued nodes for the same device, and schedules work. Stop waits until all non-`BYE` bits are cleared.

## State and Persistence Behavior

Global state is the workqueue, event list, event lock, and `worker_context` pointer. Per-device event bits are runtime-only. No persistent state exists.

## Dependencies and Integration Points

It depends on workqueues, spinlocks, waitqueues, exported symbols, and `usbip_device.eh_ops` implementations from stub, VHCI, and VUDC.

## Risks and Test Signals

Risks include allocation failure dropping queued work after setting bits, waiting interruptibly in stop, `worker_context` assumptions, event coalescing obscuring repeated events, and lock ordering with sysfs paths. Test signals include concurrent event_add calls, duplicate-device coalescing, shutdown-before-reset ordering, wait completion in stop, and module unload with active events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/usbip_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci.h -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci.h

## Purpose

`vhci.h` declares internal state and helper contracts for the USB/IP virtual host controller. It models virtual root-hub ports, in-flight local URBs, pending unlink requests, and high-speed/superspeed paired HCDs.

## Important APIs, Types, and Functions

`struct vhci_device` stores the remote device ID, speed, root-hub port, common `usbip_device`, transmit/receive submit lists, unlink lists, and TX waitqueue. `struct vhci_priv` is attached to `urb->hcpriv` and maps local URBs to USB/IP sequence numbers. `struct vhci_unlink` tracks unlink request sequence and target submit sequence. `struct vhci` stores platform device and paired HS/SS HCDs; `struct vhci_hcd` stores per-HCD port status, resume timeout, sequence counter, and virtual devices.

## Control Flow

The header defines how VHCI maps global port IDs to platform devices and root-hub ports, how HCD private memory is interpreted, and how RX/TX/sysfs/HCD files call each other.

## State and Persistence Behavior

All state is runtime-only and initialized per virtual controller during HCD start. Configured port/controller counts are compile-time constants from Kconfig.

## Dependencies and Integration Points

It depends on USB HCD structures, common USB/IP definitions, sysfs attributes, and list/spinlock/waitqueue primitives. It is the internal ABI for VHCI module objects.

## Risks and Test Signals

Risks include pointer arithmetic in `vdev_to_vhci_hcd()`, Kconfig port count assumptions, list ownership invariants, and sequence number wrap behavior. Test signals include multi-controller attach/detach, HS versus SS routing, unlink list cleanup, and compile coverage with varied Kconfig counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_hcd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_hcd.c

## Purpose

`vhci_hcd.c` implements the USB/IP virtual host controller. It registers paired USB2/USB3 HCDs, emulates root-hub status/control, queues local URBs for remote submission, handles local unlink requests, and owns virtual-device teardown/reset state.

## Important APIs, Types, and Functions

Root-hub functions are `rh_port_connect()`, `rh_port_disconnect()`, `vhci_hub_status()`, and `vhci_hub_control()`. HCD operations include `vhci_urb_enqueue()`, `vhci_urb_dequeue()`, `vhci_setup()`, `vhci_start()`, `vhci_stop()`, suspend/resume callbacks, and stream stubs. Connection event callbacks are `vhci_shutdown_connection()`, `vhci_device_reset()`, and `vhci_device_unusable()`. Platform lifecycle is managed by `vhci_hcd_probe()`, `vhci_hcd_remove()`, `vhci_hcd_init()`, and `vhci_hcd_exit()`.

## Control Flow

Module init registers a platform driver and creates one platform device per configured controller. Probe creates a primary USB2 HCD and shared USB3 HCD. Sysfs attach later sets `vhci_device` state and calls `rh_port_connect()`, causing USB enumeration. Enqueued URBs are linked to the HCD endpoint, assigned a sequence in `vhci_tx_urb()`, and sent by `vhci_tx.c`. Local dequeue either gives back immediately if disconnected or queues a remote unlink request. Event shutdown kills transport threads, closes socket, cleans unlink lists, and disconnects the root-hub port.

## State and Persistence Behavior

Port status arrays emulate hardware root-hub registers. Each virtual device tracks remote ID, speed, socket/tasks, URB lists, and status. This is runtime-only; attach state is lost on module unload or detach.

## Dependencies and Integration Points

It integrates with USB HCD core, platform bus, USB/IP common/event helpers, VHCI sysfs/RX/TX files, PM callbacks, root-hub polling, and kernel sockets via event teardown.

## Risks and Test Signals

Risks include root-hub feature emulation gaps, invalid port indexes, set-address/get-descriptor enumeration assumptions, URB/unlink races, sequence wrap, suspend with active remote devices, and cleanup ordering between HCD removal and event work. Test signals include HS/SS attach enumeration, hub control requests, URB enqueue/dequeue, remote disconnect, local unlink races, suspend refusal with active ports, and multi-controller startup/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_hcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_rx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_rx.c

## Purpose

`vhci_rx.c` receives USB/IP responses from the remote host for the virtual host controller. It matches return PDUs to pending local URBs or unlink requests, receives payloads and isochronous descriptors, and gives URBs back to the USB core.

## Important APIs, Types, and Functions

`pickup_urb_and_free_priv()` searches `priv_rx` by sequence, removes the `vhci_priv`, clears `urb->hcpriv`, and returns the URB. `vhci_recv_ret_submit()` unpacks RET_SUBMIT, receives IN payload and iso descriptors, restores iso padding, unlinks the URB from HCD endpoint tracking, and calls `usb_hcd_giveback_urb()`. `vhci_recv_ret_unlink()` matches `unlink_rx`, finds the target submit URB if still pending, applies returned status, and gives it back. `vhci_rx_pdu()` handles socket receive and dispatch.

## Control Flow

`vhci_rx_loop()` runs until stopped or an event bit appears. Each response header is read, endian-corrected, and dispatched. Missing submit sequences or unknown commands are treated as TCP/protocol errors. Idle `-EAGAIN` is ignored only when no submitted URBs are awaiting replies.

## State and Persistence Behavior

The file consumes runtime `priv_rx` and `unlink_rx` entries created by VHCI TX/dequeue paths. It mutates URB status/length fields from remote responses and has no persistent state.

## Dependencies and Integration Points

It depends on USB/IP common receive/pack helpers, VHCI HCD endpoint unlinking, USB core giveback rules, kthreads, KCOV remote coverage hooks, and the common event handler.

## Risks and Test Signals

Risks include malicious response sequence numbers, remote lengths larger than URB buffers, iso descriptor corruption, giving back URBs after local unlink races, and treating transport EOF/timeouts correctly. Test signals include normal RET_SUBMIT, RET_UNLINK before and after submit return, invalid command handling, IN payload receive, isochronous receive/padding, SG flag cleanup, and TCP reset/down events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_sysfs.c

## Purpose

`vhci_sysfs.c` exposes the userspace control plane for the virtual host controller. It reports port status, number of ports, and accepts attach/detach requests that bind established sockets to virtual root-hub ports.

## Important APIs, Types, and Functions

`status_show_vhci()` prints HS and SS port rows with status, speed, remote device ID, socket fd, and local busid. `nports_show()` reports total configured ports. `detach_store()` parses a global port number and queues a down event. `attach_store()` parses `port sockfd devid speed`, validates port/speed, looks up a stream socket, creates VHCI RX/TX kthreads, sets `vhci_device` fields, initializes KCOV, wakes threads, and calls `rh_port_connect()`. `vhci_init_attr_group()` dynamically builds attributes for all controllers.

## Control Flow

VHCI start creates the sysfs group for controller 0. Userspace opens a TCP connection to a USB/IP server, then writes attach arguments. The driver chooses the HS or SS HCD by speed, rejects occupied ports, starts transport threads before publishing state, and triggers root-hub connect. Detach validates and queues event-driven teardown.

## State and Persistence Behavior

Sysfs state reflects runtime `vhci_device` fields. Attached sockets, task pointers, remote IDs, speeds, and port status are in memory only. Dynamic status attribute allocation is tied to module lifetime.

## Dependencies and Integration Points

It depends on platform devices, USB HCD private state, common USB/IP debug attribute, socket fd lookup, kthreads, Spectre-safe `array_index_nospec()`, root-hub connection helper, and VHCI RX/TX loops.

## Risks and Test Signals

Risks include invalid port calculations with multiple controllers, socket fd lifetime, failure after one kthread is created, status output consistency while state changes, and HS/SS port selection mismatch. Test signals include attach with every supported speed, invalid port/speed/fd handling, occupied-port `-EBUSY`, detach active and inactive ports, status output before/after attach, and multi-controller status attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_tx.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_tx.c

## Purpose

`vhci_tx.c` sends local USB core requests from the virtual host controller to the remote USB/IP server. It serializes pending URBs into CMD_SUBMIT PDUs and local unlink requests into CMD_UNLINK PDUs.

## Important APIs, Types, and Functions

`setup_cmd_submit_pdu()` fills command, sequence, remote device ID, direction, endpoint, submit fields, and setup packet. `dequeue_from_priv_tx()` moves pending submits from `priv_tx` to `priv_rx` before send. `vhci_send_cmd_submit()` builds kvec arrays for headers, OUT payloads, SG payloads, and isochronous descriptors, then sends them with `kernel_sendmsg()`. `dequeue_from_unlink_tx()` moves pending unlink requests to `unlink_rx`. `vhci_send_cmd_unlink()` sends command headers for unlink target sequences. `vhci_tx_loop()` drains both queues and sleeps on `waitq_tx`.

## Control Flow

HCD enqueue adds `vhci_priv` to `priv_tx`; the TX loop moves it to `priv_rx` so RX can match the return. OUT transfers include payload; IN transfers send only command metadata. Isochronous URBs also send packed iso descriptors. Local dequeues add `vhci_unlink` to `unlink_tx`; TX moves it to `unlink_rx` before sending so RX can match RET_UNLINK.

## State and Persistence Behavior

The file advances transient list state from transmit-pending to receive-pending. It sets `URB_DMA_MAP_SG` for SG URBs before packing to the USB/IP UAPI flag space. No persistent state exists.

## Dependencies and Integration Points

It depends on common PDU packing/endian helpers, socket sendmsg, scatterlist iteration, VHCI list conventions, HCD enqueue/dequeue paths, and the common event handler for send failures.

## Risks and Test Signals

Risks include partial sends, SG lengths not matching transfer length, isochronous descriptor allocation failure, using wrong side event constants on allocation failure, and leaving items in receive-pending after send failure. Test signals include bulk/control/iso submit, SG OUT submit, unlink submit, send failure cleanup, and RX matching of moved list entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc.h -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc.h

## Purpose

`vudc.h` declares internal structures for the USB/IP virtual USB device controller. VUDC lets a machine act as a USB gadget whose USB traffic is transported over USB/IP.

## Important APIs, Types, and Functions

`struct vep` wraps a virtual endpoint, descriptor, request queue, halt/wedge flags, and ep0 setup flags. `struct vrequest` wraps gadget requests. `struct urbp` associates a USB/IP URB with a virtual endpoint and sequence. `struct tx_item` queues submit or unlink responses. `struct transfer_timer` tracks transfer pacing. `struct vudc` contains the gadget, gadget driver, platform device, cached device descriptor, common `usbip_device`, endpoint array, URB queue, TX queue/lock, main lock, address/status, and connection flags.

## Control Flow

The header defines the contracts among VUDC sysfs, RX, TX, transfer timer, and device/gadget files. Endpoint requests queued by gadget drivers are matched with USB/IP URBs by the RX/transfer code and returned by TX.

## State and Persistence Behavior

All state is runtime-only per virtual UDC platform device. Descriptor caching, pullup, connected, and endpoint request queues are reset by disconnect/reset paths.

## Dependencies and Integration Points

It depends on USB gadget APIs, USB/IP common core, platform devices, timers, sysfs groups, and list/spinlock primitives.

## Risks and Test Signals

Risks include endpoint/request queue invariants, address/status synchronization, timer state transitions, and consistency with VUDC files not in this work item. Test signals include gadget bind/unbind, endpoint enable/disable, request queue/dequeue, USB/IP attach, reset/disconnect, and transfer timer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_dev.c -->
# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_dev.c

## Purpose

`vudc_dev.c` implements the virtual USB gadget device side of USB/IP VUDC. It allocates virtual endpoints, registers a gadget UDC, handles gadget endpoint operations, and implements common USB/IP shutdown/reset/unusable behavior.

## Important APIs, Types, and Functions

URB helpers are `alloc_urbp()`, `free_urbp_and_urb()`, and `free_urb()`. `nuke()` completes queued endpoint requests with `-ESHUTDOWN`; `stop_activity()` resets address, nukes all endpoints, and frees queued URBs. Gadget ops are `vgadget_get_frame()`, `vgadget_set_selfpowered()`, `vgadget_pullup()`, `vgadget_udc_start()`, and `vgadget_udc_stop()`. Endpoint ops implement enable/disable, request alloc/free, queue/dequeue, halt, and wedge. Event callbacks are `vudc_shutdown()`, `vudc_device_reset()`, and `vudc_device_unusable()`. `init_vudc_hw()` creates ep0 plus 15 IN and 15 OUT endpoints and initializes common USB/IP state.

## Control Flow

Probe allocates `struct vudc`, initializes the gadget and virtual endpoints, then registers it with `usb_add_gadget_udc()`. A gadget driver bind calls UDC start; pullup-on sets speed, ep0 maxpacket, fetches gadget descriptors, and starts USB/IP event handling. Pullup-off invalidates descriptors and queues removal. Endpoint operations maintain request queues under `udc->lock`. Shutdown stops socket threads, closes sockets, clears activity, and calls gadget disconnect if needed.

## State and Persistence Behavior

Runtime state includes endpoint descriptors, queued gadget requests, queued USB/IP URBs, pullup/connected/descriptor-cache flags, address, device status, socket/tasks, and transfer timer. No persistent state exists.

## Dependencies and Integration Points

It integrates with USB gadget core, platform devices, USB/IP common/event code, VUDC sysfs descriptor retrieval, VUDC RX/TX/transfer modules, kthreads, sockets, and timer initialization.

## Risks and Test Signals

Risks include request `udc` pointer assumptions in dequeue, races between pullup changes and event shutdown, freeing URBs while RX/TX references remain, endpoint halt semantics for queued IN requests, descriptor cache failure, and reset while a gadget driver is active. Test signals include gadget registration, pullup on/off, descriptor retrieval failure, endpoint queue/dequeue/halt/wedge, USB/IP shutdown/reset events, active request nuke, and remove after gadget unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_dev.c -->
