<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/typec.h

## Purpose
This header is the main USB Type-C class interface. It models ports, partners, cables, plugs, alternate modes, power/data/VCONN roles, orientation, USB modes, PD identity, and firmware-derived Type-C capabilities for port controller and connector-aware drivers.

## Important APIs, types, and functions
Important enums include `typec_port_type`, `typec_port_data`, `typec_role`, `typec_data_role`, `typec_pwr_opmode`, `typec_orientation`, `usb_mode`, and `usb_pd_svdm_ver`. Core types are `usb_pd_identity`, `typec_altmode_desc`, `typec_cable_desc`, `typec_partner_desc`, `typec_operations`, `typec_capability`, and `typec_connector`. APIs register/unregister ports, partners, cables, plugs, and alternate modes, update roles/orientation/mode, parse firmware capabilities, attach PD objects, and expose connector attach/deattach callbacks.

## Control flow, state, and persistence
Port drivers describe static capabilities, register a `typec_port`, then report cable/partner/plug discovery and live role changes through setter APIs. The Type-C core owns device-model objects and sysfs-visible state; callbacks in `typec_operations` route user or policy requests back to hardware drivers. Persistent state is limited to firmware/device-tree properties read through `typec_get_fw_cap()`; attachment, role, and altmode state is runtime only.

## Dependencies and integration points
It depends on Linux core types, the Type-C bus, firmware nodes, USB Power Delivery descriptors, and the device model. Integration points include TCPM/UCSI/EC port drivers, alternate-mode drivers, mux/switch/retimer users, USB/DisplayPort/Thunderbolt consumers, and sysfs userspace policy.

## Risks and test signals
Risks include stale partner/cable lifetimes, role/orientation updates racing with disconnect, wrong SVDM/PD revision propagation, and mismatched firmware capability parsing. Tests should cover port registration cleanup, role swap callbacks, altmode enumeration, active cable identity, Enter_USB mode changes, sysfs state, and disabled or missing callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_altmode.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/typec_altmode.h

## Purpose
This header defines USB Type-C Alternate Mode devices and drivers. It lets the Type-C core expose port, plug, and partner altmodes as device-model objects and lets SVID-specific drivers enter, exit, notify, and exchange VDMs.

## Important APIs, types, and functions
Key items are `typec_altmode`, `typec_altmode_ops`, `typec_cable_ops`, `typec_altmode_driver`, `typec_altmode_enter()`, `typec_altmode_exit()`, `typec_altmode_attention()`, `typec_altmode_vdm()`, cable altmode helpers, plug lookup helpers, `typec_match_altmode()`, and driver registration macros. It also defines modal connector states and special Type-C modes for USB2, USB3, USB4, audio, and debug accessories.

## Control flow, state, and persistence
Port discovery creates altmode devices with SVID/mode/VDO metadata. Matching altmode drivers bind through the Type-C bus, then invoke operation callbacks to send Enter/Exit/Attention/vendor VDMs and report asynchronous mode-selection results. Active state, priority, selected mode, and driver data are runtime device state; no persistent storage is defined.

## Dependencies and integration points
It depends on `mod_devicetable.h`, `device.h`, and `typec.h`. It integrates with DisplayPort, Thunderbolt, USB4 mode selection, Type-C muxes, cable plug SOP prime operations, and userspace-visible device binding.

## Risks and test signals
Risks are entering modes while not DFP, mixing partner and plug SVDM versions, missing async state updates, and dangling driver data after disconnect. Tests should bind/unbind a fake altmode driver, exercise enter/exit/attention/VDM callbacks, verify mode-selection timeout/reporting, and check plug altmode reference handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_altmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_dp.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/typec_dp.h

## Purpose
This header captures DisplayPort Alternate Mode constants, connector states, command IDs, and VDO bit helpers used by DP altmode drivers and Type-C mux consumers.

## Important APIs, types, and functions
Important definitions include `USB_TYPEC_DP_SID`, `USB_TYPEC_DP_MODE`, `TYPEC_DP_STATE_*`, `DP_PIN_ASSIGN_*`, `typec_displayport_data`, `DP_CMD_STATUS_UPDATE`, `DP_CMD_CONFIGURE`, and helpers for DP capabilities, status, HPD, pin assignments, UHBR signaling, cable type, and DPAM version fields.

## Control flow, state, and persistence
The header has no executable flow. Drivers parse Discover Modes capability VDOs, issue Status Update and Configure commands, then pass `typec_displayport_data` and `TYPEC_DP_STATE_*` values through altmode notify/mux paths. All state is negotiated runtime state; capabilities come from USB PD VDOs rather than local persistence.

## Dependencies and integration points
It depends on `typec_altmode.h` and bitfield helpers. Integration points are DP altmode policy, Type-C mux routing, HPD notification, GPU/DRM bridge logic, and USB/DP pin assignment selection.

## Risks and test signals
Risks include reversed DFP/UFP pin assignment interpretation for plugs versus receptacles, accepting deprecated A/B/F assignments unexpectedly, and misparsing UHBR/cable type bits. Tests should feed known capability/status/configuration VDOs and verify selected pin assignment, HPD handling, and mux state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_mux.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/typec_mux.h

## Purpose
This header defines Type-C orientation switches and mode muxes. It abstracts devices that flip connector orientation or route pins between USB, accessory, USB4, and alternate-mode states.

## Important APIs, types, and functions
Important types are `typec_switch_desc`, `typec_switch_set_fn_t`, `typec_mux_state`, `typec_mux_desc`, and `typec_mux_set_fn_t`. APIs include fwnode and device lookup helpers, `typec_switch_set()`, `typec_switch_register()`, `typec_mux_set()`, `typec_mux_register()`, drvdata accessors, and unregister/put helpers. Disabled `CONFIG_TYPEC` stubs return success for no-op sets and `-EOPNOTSUPP` for registration.

## Control flow, state, and persistence
Provider drivers register switch or mux devices with firmware-node identity and set callbacks. Type-C policy obtains handles from the connector fwnode, sends orientation or mode state updates, and releases references on disconnect or teardown. Mux state carries the active altmode pointer, numeric mode, and mode-specific data. State is hardware runtime state only.

## Dependencies and integration points
It depends on firmware property APIs, error pointers, and Type-C core types. It integrates with board firmware descriptions, retimers, PHYs, DP/TBT/USB4 altmode drivers, and controller drivers that need routing updates.

## Risks and test signals
Risks include missing fwnode links, ignoring error-pointer drvdata stubs, stale altmode pointers in mux state, and ordering orientation before mode changes incorrectly. Tests should cover provider registration, consumer lookup, orientation flips, mode transitions, disabled-config stubs, and cleanup on disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_mux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_retimer.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/typec_retimer.h

## Purpose
This header defines the Type-C retimer interface for components that condition or re-drive high-speed lanes according to orientation, USB mode, and active alternate mode.

## Important APIs, types, and functions
Key types are `typec_retimer_state`, `typec_retimer_desc`, and `typec_retimer_set_fn_t`. APIs include `fwnode_typec_retimer_get()`, `typec_retimer_get()`, `typec_retimer_put()`, `typec_retimer_set()`, `typec_retimer_register()`, `typec_retimer_unregister()`, and `typec_retimer_get_drvdata()`.

## Control flow, state, and persistence
Providers register a retimer with a firmware node and set callback. Consumers look up the retimer through the connector fwnode and send state changes containing altmode, mode, and orientation. Runtime state lives in provider hardware and private data; this header defines no persistent state.

## Dependencies and integration points
It depends on firmware properties and `typec.h`. It integrates with Type-C mux policy, USB4/DP/TBT altmode handling, PHY power management, and board-specific retimer drivers.

## Risks and test signals
Risks include lookup failure on bad firmware graph links, applying retimer state after disconnect, and mode/orientation mismatches causing link training failure. Tests should validate fwnode lookup, callback invocation order, unregister cleanup, and lane-mode transitions for USB3, USB4, and DP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_retimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_tbt.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/typec_tbt.h

## Purpose
This header defines Intel Thunderbolt Alternate Mode SVID values, state identifiers, cable/device data, and VDO bit helpers for Type-C Thunderbolt mode negotiation.

## Important APIs, types, and functions
Important items are `USB_TYPEC_VENDOR_INTEL`, `USB_TYPEC_TBT_SID`, `TYPEC_TBT_MODE`, `TYPEC_TBT_STATE`, `typec_thunderbolt_data`, `TBT_MODE`, `TBT_ADAPTER()`, `TBT_CABLE_SPEED()`, rounded/optical/retimer/link-training bits, and Enter Mode VDO construction helpers.

## Control flow, state, and persistence
The header provides constants used by TBT altmode code when parsing Discover Modes VDOs and constructing Enter Mode VDOs. The negotiated status/configuration data is carried in `typec_thunderbolt_data` notifications. State is runtime PD/altmode state, not persistent storage.

## Dependencies and integration points
It depends on `typec_altmode.h` and bitfield helpers. Integration points include Thunderbolt/USB4 lane policy, Type-C muxes, active cable handling, and Intel SVID-specific altmode drivers.

## Risks and test signals
Risks are misinterpreting active cable properties, missing link-training requirements, and treating legacy and TBT3 adapters the same. Tests should validate VDO parsing for passive, active, optical, retimer, and rounded cable combinations and verify mux state notification payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/typec_tbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/uas.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/uas.h

## Purpose
This header defines USB Attached SCSI protocol wire structures, information unit IDs, task management codes, response codes, and pipe usage descriptors.

## Important APIs, types, and functions
Important packed structures are `iu`, `command_iu`, `task_mgmt_iu`, `sense_iu`, `response_iu`, and `usb_pipe_usage_descriptor`. Enums define IU identifiers, task management functions, service response values, and endpoint usage values.

## Control flow, state, and persistence
UAS host drivers build command and task-management IUs from SCSI commands, submit them over bulk streams, and parse sense/response IUs when devices complete work. The header only describes USB wire layout; queueing state is in the UAS driver and SCSI midlayer.

## Dependencies and integration points
It depends on SCSI command and SCSI constants. It integrates USB storage transports with the Linux SCSI midlayer and endpoint/stream selection during probe.

## Risks and test signals
Risks include packed layout drift, wrong big-endian fields, tag/task attribute mismatches, and incorrect endpoint usage discovery. Tests should cover structure sizes, command IU encoding, sense parsing, task management response handling, and malformed descriptor rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/uas.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ulpi.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/ulpi.h

## Purpose
This header exposes ULPI OTG transceiver creation and capability flags for USB PHY drivers using the ULPI viewport/register model.

## Important APIs, types, and functions
Key definitions are `ULPI_OTG_*`, `ULPI_IC_*`, and `ULPI_FC_*` flag bits, `devm_otg_ulpi_create()`, and the exported `ulpi_viewport_access_ops`. Disabled-config stubs return `NULL` for transceiver creation.

## Control flow, state, and persistence
Controller drivers call `devm_otg_ulpi_create()` with access ops and capability flags to instantiate a managed `usb_phy`. Register IO is delegated through ULPI viewport ops. State is the transceiver's runtime register configuration and devres-managed lifetime; no persistence is defined.

## Dependencies and integration points
It depends on USB OTG and ULPI register definitions. It integrates host/device controller drivers, OTG role logic, and PHY creation for platforms with external ULPI transceivers.

## Risks and test signals
Risks include wrong capability flags, viewport read/write ordering bugs, and assuming the helper exists when `CONFIG_USB_ULPI` is disabled. Tests should cover creation/removal, register access ops, OTG flag programming, and disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/ulpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usb338x.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/usb338x.h

## Purpose
This header defines the USB3380/USB338x device-controller register layout and bit positions used by the NetChip/PLX USB gadget driver family.

## Important APIs, types, and functions
Important register layout types are `usb338x_usb_ext_regs`, `usb338x_fifo_regs`, `usb338x_ll_regs`, and `usb338x_pl_regs`. Macros describe scratch, endpoint configuration, FIFO layout, link power management, USB2/USB3 core enablement, LFPS timing, physical-layer endpoint control, sequence reset, and status fields.

## Control flow, state, and persistence
The header is a register map only. The gadget driver maps hardware registers, programs endpoint/FIFO/link/PHY fields, handles workarounds, and observes endpoint status bits. State is hardware register state plus driver bookkeeping outside this header.

## Dependencies and integration points
It depends on `usb/net2280.h` and integrates with the USB gadget controller implementation, endpoint allocation, DMA setup, SuperSpeed link management, and controller-specific errata handling.

## Risks and test signals
Risks include incorrect bit positions corrupting endpoint enable/type, FIFO sizing, or power-state transitions. Tests should include register-offset assertions, endpoint configuration traces, SuperSpeed link recovery, LPM settings, and regression tests for documented hardware workarounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usb338x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usb_phy_generic.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/usb_phy_generic.h

## Purpose
This header declares helpers for registering the generic no-op USB PHY platform device used by controllers that need a simple PHY object.

## Important APIs, types, and functions
The exported APIs are `usb_phy_generic_register()` and `usb_phy_generic_unregister()`. When `CONFIG_NOP_USB_XCEIV` is disabled, registration returns `NULL` and unregister is a no-op.

## Control flow, state, and persistence
Callers register a generic PHY during platform setup and unregister it during teardown. Runtime state belongs to the created platform device and USB PHY framework; no persistent data is represented.

## Dependencies and integration points
It depends on USB OTG PHY declarations and platform-device infrastructure. It integrates with controller drivers expecting an OTG/PHY provider even when hardware has no programmable transceiver.

## Risks and test signals
Risks are mishandling a `NULL` return from disabled stubs and unregistering an invalid pointer. Tests should cover enabled probe/remove and disabled-config behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usb_phy_generic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usbio.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/usbio.h

## Purpose
This header defines Intel USBIO packet formats, client names, quirks, GPIO/I2C commands, descriptors, and auxiliary-bus helper APIs for USB-attached GPIO and I2C functions.

## Important APIs, types, and functions
Key constants are `USBIO_GPIO_CLIENT`, `USBIO_I2C_CLIENT`, `USBIO_QUIRK_*`, packet type IDs, GPIO/I2C commands, bank/bus limits, and pin/config bit helpers. Important packed types are `usbio_packet_header`, `usbio_ctrl_packet`, `usbio_bulk_packet`, GPIO bank/init/rw descriptors, and I2C bus/init/rw descriptors. APIs include `usbio_control_msg()`, `usbio_bulk_msg()`, acquire/release, buffer-length/quirk queries, and ACPI binding.

## Control flow, state, and persistence
Auxiliary child drivers acquire the shared USBIO parent, send typed control or bulk command packets, then release it. GPIO/I2C operations encode bank, pin, bus, config, speed, and payload lengths into packed little-endian messages. Quirks alter transfer lengths, initialization ACK behavior, and speed limits. State is runtime device arbitration and controller configuration; ACPI IDs provide firmware binding.

## Dependencies and integration points
It depends on auxiliary bus, endian types, list/types, and ACPI identifiers. It integrates USBIO parent drivers with GPIO and I2C auxiliary clients.

## Risks and test signals
Risks include counted flexible-array length mismatches, quirk-dependent transfer splitting, concurrent client access without acquire/release, and endian mistakes in I2C/GPIO payloads. Tests should cover control and bulk packets, max buffer limits, every quirk flag, ACPI matching, and invalid bus/bank/pin values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usbio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usbnet.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/usbnet.h

## Purpose
This header defines the shared USB networking core contract used by many USB Ethernet, RNDIS, CDC, WLAN, WWAN, and vendor minidrivers.

## Important APIs, types, and functions
Key types are `usbnet`, `driver_info`, `cdc_state`, `skb_state`, and `skb_data`. APIs include probe/suspend/resume/disconnect, control command helpers, CDC bind/status helpers, netdev operations, RX/TX queue control, power management, link settings, status URB control, and `usbnet_set_skb_tx_stats()`. Flags describe framing, naming, ARP, multi-packet, runtime PM, and link interrupt behavior.

## Control flow, state, and persistence
Minidrivers provide `driver_info` callbacks for bind, reset, stop, power, status, link reset, RX/TX fixups, recovery, indication, and multicast filtering. The core owns URBs, skb queues, work items, status interrupt URB, MII state, link state, and event bits. State is runtime network/USB state; no persistent storage is defined.

## Dependencies and integration points
It depends on USB, netdevice, skbuff, MII, workqueue, mutex, spinlock, and CDC descriptors. It integrates the USB driver model with netdev/ethtool, runtime PM, CDC Ethernet/RNDIS-like protocols, and minidriver framing.

## Risks and test signals
Risks include queue/work races during unplug, malformed framing in fixups, runtime PM misuse, multi-packet accounting errors, and deadlocks around interrupt/status URBs. Tests should cover probe/bind failure cleanup, suspend/resume, RX pause/resume, TX timeout, CDC descriptors, link changes, and unplug while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/usbnet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/uvc.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/uvc.h

## Purpose
This header provides internal UVC/V4L2 GUID constants and extension-unit control IDs shared by USB video drivers.

## Important APIs, types, and functions
Important definitions are UVC entity GUIDs, ChromeOS and Microsoft extension-unit GUIDs, MSXU control IDs, ChromeOS IQ profile control, and pixel-format GUIDs for MJPEG, YUY2, NV12, YV12, and I420 variants.

## Control flow, state, and persistence
The header has no executable flow. UVC parsers compare descriptor GUIDs against these constants to identify terminals, processing/selector/extension units, controls, and frame formats. State is descriptor-derived runtime metadata cached by the UVC driver.

## Dependencies and integration points
It is a lightweight internal API for USB video class drivers and V4L2 format/control mapping.

## Risks and test signals
Risks are GUID byte-order mistakes and assigning vendor extension controls to the wrong unit. Tests should parse descriptors for each known GUID, map formats to V4L2 fourcc values, and validate MSXU/ChromeOS control lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/uvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/webusb.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/webusb.h

## Purpose
This header defines WebUSB platform capability and URL descriptor constants for USB gadget/device code exposing WebUSB metadata.

## Important APIs, types, and functions
Important items are `WEBUSB_UUID`, `usb_webusb_cap_data`, `WEBUSB_VERSION_1_00`, landing-page presence constants, `WEBUSB_GET_URL`, `webusb_url_descriptor`, URL scheme constants, header lengths, and `WEBUSB_URL_RAW_MAX_LENGTH`.

## Control flow, state, and persistence
Gadget code advertises the platform capability in BOS descriptors and answers vendor requests for URL descriptors. State is descriptor data configured by the gadget; the header only defines wire layout and limits.

## Dependencies and integration points
It depends on USB chapter 9 UAPI definitions and little-endian conversion. It integrates with USB gadget BOS descriptor construction and browser/user-agent WebUSB discovery.

## Risks and test signals
Risks include malformed descriptor lengths, invalid URL scheme values, landing-page index mismatches, and exceeding one-byte descriptor length limits. Tests should inspect generated BOS/URL descriptors and issue GET_URL requests with valid and invalid indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/webusb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/xhci-dbgp.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/xhci-dbgp.h

## Purpose
This header declares early xHCI debug capability console setup hooks used for early boot USB debugging.

## Important APIs, types, and functions
When `CONFIG_EARLY_PRINTK_USB_XDBC` is enabled it exports `early_xdbc_parse_parameter()`, `early_xdbc_setup_hardware()`, and `early_xdbc_register_console()`. Disabled stubs make setup return `-ENODEV` and console registration a no-op.

## Control flow, state, and persistence
Early boot parses parameters, initializes xDBC hardware, then registers an early console. State is early-console and controller hardware state only; no persistence is defined.

## Dependencies and integration points
It integrates with architecture early printk, xHCI debug capability support, and boot parameter parsing.

## Risks and test signals
Risks include using unavailable early MMIO resources, enabled/disabled config divergence, and failing gracefully before the normal USB stack exists. Tests should cover boot parameters, no-device fallback, early console output, and disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/xhci-dbgp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/xhci-sideband.h -->
# sources/distributed-fs/ceph-client/include/linux/usb/xhci-sideband.h

## Purpose
This header defines xHCI sideband support for clients that need direct endpoint/event ring buffers or secondary interrupters alongside the normal USB host driver.

## Important APIs, types, and functions
Key types are `xhci_sideband_type`, `xhci_sideband_notify_type`, `xhci_sideband_event`, and `xhci_sideband`. APIs register/unregister sideband clients, add/remove/stop endpoints, obtain endpoint/event buffers, check HCD support, create/remove interrupters, query interrupter IDs, and notify endpoint ring free events.

## Control flow, state, and persistence
Clients register against a USB interface with a notification callback. The sideband layer brokers selected endpoint rings and event buffers from xHCI, supports interrupter allocation, and sends lifecycle notifications. State is runtime xHCI/USB endpoint ownership and scatter-gather buffer metadata.

## Dependencies and integration points
It depends on scatterlists, USB core, and USB HCD structures. It integrates with xHCI internals and device-specific sideband consumers such as display or accelerator paths.

## Risks and test signals
Risks include endpoint ownership races, freeing rings while sideband users still hold buffers, mismatch between HCD support and client registration, and interrupt teardown ordering. Tests should cover register/unregister, endpoint add/remove/stop, interrupter allocation, buffer lifetime, and disabled-config no-op notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb/xhci-sideband.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb_usual.h -->
# sources/distributed-fs/ceph-client/include/linux/usb_usual.h

## Purpose
This header centralizes USB mass-storage unusual-device quirk flags and exposes shared device ID and ignore helpers.

## Important APIs, types, and functions
`US_DO_ALL_FLAGS` enumerates quirk flags such as single-LUN behavior, bad sense, capacity quirks, no report opcodes, ignore-residue, no UAS, and others by expanding `US_FLAG`. It exports `usb_usual_ignore_device()` and `usb_storage_usb_ids[]`.

## Control flow, state, and persistence
USB storage and UAS probing use the shared ID table and quirk flags to decide whether a device should bind and which protocol workarounds apply. There is no local runtime state; flags are static driver metadata.

## Dependencies and integration points
It includes USB storage definitions and integrates usb-storage, UAS, and device ID matching.

## Risks and test signals
Risks include conflicting quirk bits, misapplied ignore behavior, and duplicate device IDs across storage transports. Tests should probe devices with known unusual entries, verify selected flags, and ensure UAS is suppressed where required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usb_usual.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usbdevice_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/usbdevice_fs.h

## Purpose
This kernel header wraps the usbdevfs UAPI and defines 32-bit compatibility structures for usbfs ioctls.

## Important APIs, types, and functions
Under `CONFIG_COMPAT`, it defines `usbdevfs_ctrltransfer32`, `usbdevfs_bulktransfer32`, `usbdevfs_disconnectsignal32`, `usbdevfs_urb32`, and `usbdevfs_ioctl32`, mirroring pointer-bearing UAPI structs with `compat_caddr_t` and fixed-width fields.

## Control flow, state, and persistence
The usbfs ioctl layer copies compat user structures, translates pointers and sizes to native kernel forms, and dispatches to normal usbdevfs handling. The header describes ABI layout only; ioctl state and URB tracking live in usbfs implementation code.

## Dependencies and integration points
It depends on `uapi/linux/usbdevice_fs.h` and `linux/compat.h`. It integrates 32-bit userspace with 64-bit kernels for USB control, bulk, URB, disconnect-signal, and nested ioctl calls.

## Risks and test signals
Risks include ABI layout mismatch, pointer truncation, wrong padding, and unchecked user lengths. Tests should run 32-bit usbfs ioctl exercisers on 64-bit kernels and compare native versus compat behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/usbdevice_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user-return-notifier.h -->
# sources/distributed-fs/ceph-client/include/linux/user-return-notifier.h

## Purpose
This header defines a per-task notifier mechanism fired just before returning to user mode when `CONFIG_USER_RETURN_NOTIFIER` is enabled.

## Important APIs, types, and functions
Key type is `user_return_notifier` with an `on_user_return` callback and hlist link. APIs are `user_return_notifier_register()`, `user_return_notifier_unregister()`, `propagate_user_return_notify()`, `fire_user_return_notifiers()`, and `clear_user_return_notifier()`. Disabled builds provide empty stubs.

## Control flow, state, and persistence
Users register callbacks that set task thread flags. On context switch, `propagate_user_return_notify()` moves `TIF_USER_RETURN_NOTIFY` from previous to next task when needed; return-to-user code calls `fire_user_return_notifiers()`. State is task-local flags and notifier lists, not persistent.

## Dependencies and integration points
It depends on scheduler task flags and hlist support. It integrates with low-level context-switch and return-to-user paths.

## Risks and test signals
Risks include callback lifetime errors, missing flag propagation, and callbacks running in sensitive return-to-user context. Tests should register/unregister notifiers, switch tasks, clear flags, and verify disabled stubs compile away.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user-return-notifier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user.h -->
# sources/distributed-fs/ceph-client/include/linux/user.h

## Purpose
This compatibility header simply includes architecture-specific user register/core-dump definitions from `asm/user.h`.

## Important APIs, types, and functions
No Linux-generic APIs are defined here. The exported surface is whatever the target architecture provides through `asm/user.h`, typically user register and core-dump layout types.

## Control flow, state, and persistence
There is no control flow or state in this wrapper. It provides an include indirection for code that wants the generic `linux/user.h` path.

## Dependencies and integration points
It depends entirely on architecture headers and integrates with ptrace/core-dump and low-level user ABI code.

## Risks and test signals
Risks are architecture header divergence and accidental assumptions that this generic file defines common fields. Build coverage across architectures is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user_events.h -->
# sources/distributed-fs/ceph-client/include/linux/user_events.h

## Purpose
This header defines kernel bookkeeping for user_events tracing registrations attached to an `mm_struct` and task lifecycle hooks.

## Important APIs, types, and functions
With `CONFIG_USER_EVENTS`, key type `user_event_mm` tracks mm list links, enablers, refcounts for mm/tasks, and deferred RCU cleanup. APIs are `user_event_mm_dup()`, `user_event_mm_remove()`, and inline hooks `user_events_fork()`, `user_events_execve()`, and `user_events_exit()`. Disabled builds provide no-op hooks.

## Control flow, state, and persistence
On fork, tasks sharing the VM increment task refs; non-`CLONE_VM` forks duplicate user_event mm state. Exec and exit remove task/mm associations. State is runtime tracing enablement tied to process address spaces and protected by tracing internals; no persistent state is stored.

## Dependencies and integration points
It depends on list, refcount, mm types, RCU work, and the user_events UAPI. It integrates with task fork/exec/exit paths and tracing/eventfs user-event registration.

## Risks and test signals
Risks include refcount leaks, use-after-free across fork/exec/exit, and incorrect handling of shared VM tasks. Tests should exercise clone with and without `CLONE_VM`, exec cleanup, exit cleanup, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/user_namespace.h

## Purpose
This header defines user namespace identity mapping, per-namespace resource accounting, keyring/sysctl state, and APIs for creating, referencing, and querying user namespaces.

## Important APIs, types, and functions
Key types are `uid_gid_extent`, `uid_gid_map`, `user_namespace`, and `ucounts`. Enums define namespace and rlimit count classes. APIs include sysctl setup/retire, `inc_ucount()`/`dec_ucount()`, ucount allocation/refcounting, rlimit count helpers, `get_user_ns()`/`put_user_ns()`, `create_user_ns()`, `unshare_userns()`, `/proc/*_map` write helpers, setgroups checks, and namespace ancestry helpers.

## Control flow, state, and persistence
Namespace creation initializes UID/GID/projid maps, parent/owner/group, flags, counts, keyring/sysctl state, and resource limits. Proc map writes populate translation extents; resource helpers increment/decrement per-user counters and rlimit usage. State is kernel runtime namespace state; mappings and sysctls are observable through procfs but not persisted by this header.

## Dependencies and integration points
It depends on namespace common code, credentials, keyrings, sysctl, workqueues, RCU refs, and procfs sequence operations. It integrates with clone/unshare, capability checks, ID mapping, keyrings, binfmt_misc, and per-user resource enforcement.

## Risks and test signals
Risks include ID-map extent overflow, wrong parent/owner capability checks, ucount leaks, rlimit underflow/overflow, and disabled `CONFIG_USER_NS` behavior returning init namespace. Tests should cover nested namespace creation, uid/gid/projid map writes, setgroups policy, ucount limits, rlimit enforcement, and disabled-config fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/user_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/userfaultfd_k.h -->
# sources/distributed-fs/ceph-client/include/linux/userfaultfd_k.h

## Purpose
This header is the kernel-internal userfaultfd interface for registering VMAs, handling missing/minor/write-protect faults, atomic page fill/move/poison operations, and mm lifecycle notifications.

## Important APIs, types, and functions
Key items are `userfaultfd_ctx`, `vm_uffd_ops`, `uffd_flags_t`, `mfill_atomic_mode`, `handle_userfault()`, `mfill_atomic_copy()`, `mfill_atomic_zeropage()`, `mfill_atomic_continue()`, `mfill_atomic_poison()`, `mwriteprotect_range()`, `uffd_wp_range()`, `move_pages()`, registration/release helpers, VMA flag predicates, and fork/mremap/unmap preparation/completion hooks. Disabled builds return conservative no-op or `SIGBUS`/false results.

## Control flow, state, and persistence
Fault paths call `handle_userfault()` when VMA flags are armed. UFFD operations fill, continue, poison, write-protect, or move pages under context waitqueues and `map_changing_lock`. Fork, mremap, unmap, and release paths notify or clear contexts so userspace fault handlers see coherent events. State includes waitqueues, refcount, requested features, released flag, mmap-changing counter, mm pointer, and VMA `vm_userfaultfd_ctx`; no disk persistence is involved.

## Dependencies and integration points
It depends on mm, swap, page-table UFFD helpers, hugetlb, fcntl flags, and userfaultfd UAPI. It integrates deeply with page fault handling, VMA merge/split, filemap/pagecache operations, huge PMD sharing, swap PTE markers, and mm teardown.

## Risks and test signals
Risks include lock ordering violations among waitqueues, lost wakeups, PTE marker misuse, huge-PMD sharing with UFFD-WP/minor, fault-around installing mappings without notification, and feature mismatch with userspace. Tests should cover missing/minor/WP faults, fork/mremap/unmap events, atomic fill modes, async WP markers, hugetlb/file-backed VMAs, disabled config, and race stress around release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/userfaultfd_k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/util_macros.h -->
# sources/distributed-fs/ceph-client/include/linux/util_macros.h

## Purpose
This header provides small generic helper macros for conditional iteration, closest-value lookup in sorted arrays, and compile-time-dead-code-friendly pointer selection.

## Important APIs, types, and functions
Important macros are `for_each_if()`, `find_closest()`, `find_closest_descending()`, and `PTR_IF()`. They use `typeof`, type checking, arithmetic helpers, and compiler attributes to preserve expression types.

## Control flow, state, and persistence
The macros expand inline at call sites. `for_each_if()` gates loop bodies, closest-value macros scan sorted arrays, and `PTR_IF()` returns a pointer or `NULL` while allowing the compiler to drop disabled code. There is no runtime state beyond local temporaries and no persistence.

## Dependencies and integration points
It depends on compiler attributes, math helpers, type checking, and stddef. Integration is broad across drivers that need compact helper expressions.

## Risks and test signals
Risks include unsigned/signed surprises in closest calculations, descending-loop underflow if size is invalid, and misuse of `PTR_IF()` with non-pointers. Tests should compile macro users with signed/unsigned arrays, ascending/descending data, boundary sizes, and disabled config expressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/util_macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uts.h -->
# sources/distributed-fs/ceph-client/include/linux/uts.h

## Purpose
This header declares the global system UTS name object used for kernel release, version, machine, nodename, and domainname metadata.

## Important APIs, types, and functions
It includes UAPI `utsname.h`, defines `struct uts_namespace`, and exports `system_utsname`.

## Control flow, state, and persistence
There is no control flow. The exported `system_utsname` is global runtime identity state initialized during boot and referenced by uts namespace code and syscalls. Persistence comes from build-time/generated version data and administrator changes through namespace-aware interfaces.

## Dependencies and integration points
It integrates with UTS namespaces, uname-related syscalls, proc/sysctl views, and generated kernel version metadata.

## Risks and test signals
Risks are direct global access bypassing namespace-specific UTS state. Tests should verify uname output in init and non-init UTS namespaces and build-generated release/version strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uts_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/uts_namespace.h

## Purpose
This header defines the UTS namespace object and helpers for copying, referencing, and freeing namespace-specific host/domain name state.

## Important APIs, types, and functions
Key type is `uts_namespace` containing `new_utsname`, `user_namespace`, `ucounts`, namespace common header, and refcount. APIs include `copy_utsname()`, `free_uts_ns()`, `get_uts_ns()`, `put_uts_ns()`, `uts_ns_init()`, and `to_uts_ns()`. Disabled builds reuse `init_uts_ns` and reject `CLONE_NEWUTS`.

## Control flow, state, and persistence
Clone/unshare calls copy or share the namespace based on flags; ref helpers manage lifetime; namespace operations access `name` under UTS locks in implementation code. State is runtime namespace identity and ownership accounting; there is no filesystem persistence.

## Dependencies and integration points
It depends on namespace proxy/common code, user namespaces, ucounts, sched, and UAPI utsname layout. It integrates with clone/unshare, uname/sethostname/setdomainname syscalls, and proc namespace handles.

## Risks and test signals
Risks include refcount leaks, wrong user namespace ownership, ucount limit bypass, and disabled-config behavior. Tests should cover clone/unshare semantics, namespace lifetime via proc fd, hostname isolation, and init namespace fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uts_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/utsname.h -->
# sources/distributed-fs/ceph-client/include/linux/utsname.h

## Purpose
This header provides namespace-aware helpers for obtaining current UTS identity strings and defines default kernel nodename/domainname values.

## Important APIs, types, and functions
Key items are `init_uts_ns`, `init_utsname()`, `utsname()`, `INIT_UTS_NAME`, `INIT_UTS_DOMAIN`, and `get_uts()`.

## Control flow, state, and persistence
Callers use `utsname()` or `get_uts()` to retrieve the current task's UTS namespace name state through `current->nsproxy`. Init namespace data is built at boot. Host/domain changes are runtime namespace state.

## Dependencies and integration points
It depends on sched/current task state and `uts_namespace.h`. It integrates with uname and hostname/domainname syscalls and any kernel code formatting system identity.

## Risks and test signals
Risks include dereferencing namespace state outside valid task context and accidentally using init namespace in container contexts. Tests should compare init and cloned UTS namespaces and validate default strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/utsname.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uuid.h -->
# sources/distributed-fs/ceph-client/include/linux/uuid.h

## Purpose
This header defines Linux UUID/GUID types and helpers for parsing, formatting, comparing, copying, generating, and validating UUID values.

## Important APIs, types, and functions
Key types are `uuid_t` and `guid_t`; constants include null UUID/GUID values and string length definitions. APIs include equality/null checks, copy helpers, `generate_random_uuid()`, `uuid_gen()`, `guid_gen()`, parse helpers, UUID/GUID import/export helpers, and MEI-style conversion helpers.

## Control flow, state, and persistence
Helpers operate on fixed 16-byte values. Generation obtains random bytes in implementation code; parse/export helpers translate string or byte-array representations. Persistence is caller-owned when UUIDs are stored in firmware, filesystems, devices, or protocol descriptors.

## Dependencies and integration points
It depends on string and types helpers. It integrates broadly with filesystems, device identifiers, VFIO tokens, virtio dma-buf UUIDs, firmware tables, and protocol descriptors.

## Risks and test signals
Risks include GUID versus UUID byte-order confusion, accepting malformed strings, and comparing uninitialized values. Tests should cover parse/format round trips, null detection, random generation uniqueness smoke tests, and byte-order conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/uuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vbox_utils.h -->
# sources/distributed-fs/ceph-client/include/linux/vbox_utils.h

## Purpose
This header declares VirtualBox guest utility logging, HGCM call helpers, status conversion, and guest-device reference helpers.

## Important APIs, types, and functions
Important APIs are `vbg_info()`, `vbg_warn()`, `vbg_err()`, `vbg_err_ratelimited()`, `vbg_debug`, `vbg_hgcm_connect()`, `vbg_hgcm_disconnect()`, `vbg_hgcm_call()`, `vbg_status_code_to_errno()`, `vbg_get_gdev()`, and `vbg_put_gdev()`.

## Control flow, state, and persistence
VirtualBox guest clients get the shared guest device, connect to an HGCM service, perform calls with requestor/client IDs and parameters, then disconnect and drop references. Logging goes both to VirtualBox backdoor channels and kernel printk variants depending on build/debug configuration. State is runtime guest-device and HGCM session state.

## Dependencies and integration points
It depends on printk and VirtualBox VMMDev type definitions. It integrates vboxguest core with vboxsf and other guest service clients.

## Risks and test signals
Risks include leaked guest-device references, untranslated VirtualBox status codes, logging from inappropriate contexts, and HGCM parameter count/timeout mistakes. Tests should cover connect/call/disconnect success and failure, errno mapping, ratelimited logging, and reference balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vbox_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vdpa.h -->
# sources/distributed-fs/ceph-client/include/linux/vdpa.h

## Purpose
This header defines the vDPA bus/device contract for exposing virtio data-path accelerators to vhost, virtio, and management users.

## Important APIs, types, and functions
Key types are `vdpa_callback`, `vdpa_notification_area`, split/packed `vdpa_vq_state`, `vdpa_device`, `vdpa_iova_range`, `vdpa_dev_set_config`, `vdpa_map_file`, `vdpa_config_ops`, `vdpa_driver`, `vdpa_mgmtdev_ops`, and `vdpa_mgmt_dev`. APIs allocate/register/unregister devices and drivers, reset devices, set features/status/config, manage drvdata, and register management devices.

## Control flow, state, and persistence
Parent drivers allocate a `vdpa_device` with config/map ops, register it with a virtqueue count, and expose callbacks for queue addresses, readiness, state, notifications, features, status, config space, DMA/IOTLB maps, ASIDs, reset/suspend/resume, and optional VA binding. The framework serializes config access with `cf_lock`, tracks `features_valid`, queue/address-space counts, and management-device ownership. Persistence is not defined; configuration is runtime and driven by userspace/vhost/virtio negotiation.

## Dependencies and integration points
It depends on device core, interrupts, virtio, virtio-net/blk IDs, vhost IOTLB, Ethernet constants, eventfd, cpumasks, and mm structs. It integrates with vhost-vDPA, vdpa netlink management, virtio feature negotiation, IOMMU/IOTLB mapping, and hardware/software accelerator drivers.

## Risks and test signals
Risks include reset/map ordering mistakes, feature negotiation before status transitions, queue state mismatch for packed versus split rings, ASID/group errors, and failure to lock config changes. Tests should cover device/driver registration, management add/del/set_attr, feature set/reset, queue ready/state/callback paths, IOTLB map/unmap/reset, suspend/resume, and concurrent config access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vdpa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vdso_datastore.h -->
# sources/distributed-fs/ceph-client/include/linux/vdso_datastore.h

## Purpose
This header declares generic vDSO data-page setup and VVAR mapping helpers.

## Important APIs, types, and functions
When `CONFIG_HAVE_GENERIC_VDSO` is enabled it exports `vdso_vvar_mapping`, `vdso_install_vvar_mapping()`, and `vdso_setup_data_pages()`. Disabled builds provide a no-op setup helper.

## Control flow, state, and persistence
Architecture or mm setup initializes vDSO data pages at boot and maps the VVAR special mapping into process address spaces. State is runtime memory mapping and vDSO data; no persistent storage is involved.

## Dependencies and integration points
It depends on mm types and integrates with architecture vDSO setup, mmap layout, timekeeping data exposure, and process exec/mmap paths.

## Risks and test signals
Risks include incorrect special mapping permissions, wrong address selection, and disabled-config differences. Tests should validate VVAR mapping presence, page permissions, vDSO time reads, and no-op setup on unsupported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vdso_datastore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/verification.h -->
# sources/distributed-fs/ceph-client/include/linux/verification.h

## Purpose
This header defines kernel data/signature verification interfaces for PKCS#7 and PE signatures and enumerates key usage contexts.

## Important APIs, types, and functions
Important items are sentinel keyring selectors `VERIFY_USE_SECONDARY_KEYRING` and `VERIFY_USE_PLATFORM_KEYRING`, `system_keyring_id_check()`, `enum key_being_used_for`, `verify_pkcs7_signature()`, `verify_pkcs7_message_sig()`, and optional `verify_pefile_signature()`.

## Control flow, state, and persistence
Callers pass data, signature or parsed PKCS#7 message, selected trusted keyring, usage context, and optional content-view callback. Verification code checks signatures against builtin/secondary/platform trust roots. This header stores no state; trust keyrings and parsed messages are external runtime objects.

## Dependencies and integration points
It depends on errno/types and, when enabled, key and PKCS#7 subsystems. It integrates module loading, firmware loading, kexec PE verification, key signing, and BPF signature verification.

## Risks and test signals
Risks include invalid sentinel keyring IDs, wrong usage context policy, accepting malformed PKCS#7 data, and disabled verification config. Tests should cover trusted/untrusted signatures, secondary/platform keyring selectors, PE verification, callback data views, and malformed signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/verification.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vermagic.h -->
# sources/distributed-fs/ceph-client/include/linux/vermagic.h

## Purpose
This header constructs the module version-magic string used to reject modules built for incompatible kernel configurations.

## Important APIs, types, and functions
Important macros are `MODULE_VERMAGIC_SMP`, `MODULE_VERMAGIC_PREEMPT`, `MODULE_VERMAGIC_MODULE_UNLOAD`, `MODULE_VERMAGIC_MODVERSIONS`, `MODULE_RANDSTRUCT`, and `VERMAGIC_STRING`. It requires `INCLUDE_VERMAGIC` and includes generated release and architecture vermagic data.

## Control flow, state, and persistence
There is no runtime flow. Build-time module code includes this header to embed a string containing release, SMP/preempt/module-unload/modversions, architecture, and randomization seed markers. The string persists in module metadata.

## Dependencies and integration points
It depends on generated `utsrelease.h` and `asm/vermagic.h`. It integrates with module build, modpost, and module loader compatibility checks.

## Risks and test signals
Risks include accidental inclusion outside allowed build contexts, missing architecture marker changes, and false module compatibility. Tests should compare built module vermagic against running kernel and cover config toggles for SMP, PREEMPT_RT, MODVERSIONS, MODULE_UNLOAD, and RANDSTRUCT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vexpress.h -->
# sources/distributed-fs/ceph-client/include/linux/vexpress.h

## Purpose
This header declares the ARM Versatile Express configuration regmap initializer.

## Important APIs, types, and functions
The exported API is `devm_regmap_init_vexpress_config(struct device *dev)`, returning a managed `regmap`.

## Control flow, state, and persistence
Platform drivers call the helper during probe to obtain a device-managed regmap for VExpress configuration registers. State is regmap/device runtime state managed by devres; no persistence is defined.

## Dependencies and integration points
It depends on device and regmap APIs. It integrates with ARM VExpress platform drivers that access system configuration registers.

## Risks and test signals
Risks include probe deferral or wrong firmware description causing regmap initialization failure. Tests should cover successful regmap creation, devres cleanup, and read/write operations through platform fixtures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vexpress.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfio.h -->
# sources/distributed-fs/ceph-client/include/linux/vfio.h

## Purpose
This header defines the VFIO kernel driver framework for safely exposing devices to userspace with IOMMU isolation, migration, dirty logging, IRQFD, and device cdev/group support.

## Important APIs, types, and functions
Key types are `vfio_device_set`, `vfio_device`, `vfio_device_ops`, `vfio_migration_ops`, `vfio_log_ops`, `vfio_info_cap`, and `virqfd`. APIs cover device allocation/registration/unregistration, iommufd binding/attach/detach, feature validation, precopy ioctl validation, device-set management, migration FSM transitions, IOVA range combination, file validation/KVM association, page pin/unpin, DMA read/write, capability construction, IRQ set validation, and virqfd enable/disable/flush.

## Control flow, state, and persistence
Bus drivers embed `vfio_device`, set static ops/migration/logging properties, register with the VFIO core, and serve file operations through callbacks. Open/close are serialized by device sets; iommufd/group state controls DMA address spaces; migration/log callbacks implement userspace-requested state transitions. State is runtime references, open counts, cdev/group/iommufd attachments, KVM pointer, PASIDs, IRQFD work, and debug roots; persistent state belongs to hardware or userspace migration streams.

## Dependencies and integration points
It depends on IOMMU, iommufd, mm, poll, cdev, IOVA bitmaps, uaccess, workqueues, eventfd, and VFIO UAPI. It integrates PCI/platform/mdev VFIO drivers, KVM, userspace VMMs, IOMMUFD, dirty logging, and migration.

## Risks and test signals
Risks include lifetime/refcount races, incorrect iommufd detach, unsafe page pinning, bad user ioctl validation, migration stream state leaks, and IRQFD shutdown races. Tests should cover open/close sets, cdev/group paths, iommufd physical/emulated ops, feature/probe ioctls, migration FSM, dirty logging, DMA map/unmap callbacks, and IRQFD teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfio_pci_core.h -->
# sources/distributed-fs/ceph-client/include/linux/vfio_pci_core.h

## Purpose
This header defines shared VFIO PCI core structures and helpers used by VFIO PCI variant drivers to expose PCI BARs, config space, IRQs, reset, SR-IOV, DMA-buf, and region extensions.

## Important APIs, types, and functions
Key definitions include VFIO PCI offset/index macros, `vfio_pci_eventfd`, `vfio_pci_regops`, `vfio_pci_region`, `vfio_pci_device_ops`, and `vfio_pci_core_device`. APIs register device regions, set module parameters, initialize/release/register/unregister devices, handle ioctl/read/write/mmap/request/match, enable/disable PCI devices, setup BAR maps, handle AER, perform IO read/write with width helpers, test memory enablement, check range intersections, and map DMA-buf physical vectors.

## Control flow, state, and persistence
Variant drivers embed `vfio_pci_core_device`, initialize common state, register the VFIO device, and delegate user file operations to core helpers. The core tracks BAR mappings, config permission maps, IRQ/eventfd contexts, MSI/MSI-X state, reset/PM flags, SR-IOV token/PF state, memory locks, dynamic regions, and DMA-buf lists. State is runtime device and userspace attachment state; persistent PCI config is saved/restored through PCI core helpers.

## Dependencies and integration points
It depends on PCI, VFIO, IRQ bypass, RCU, UUIDs, notifiers, DMA-buf/P2PDMA, and UAPI VFIO region structures. It integrates VFIO PCI drivers with PCI reset/AER/PM, KVM irqbypass, SR-IOV, and userspace VMM memory mapping.

## Risks and test signals
Risks include BAR mmap permission errors, config-space access leakage, eventfd RCU lifetime mistakes, SR-IOV token misuse, reset/PM restore regressions, and width/alignment bugs in IO paths. Tests should cover BAR read/write/mmap, region capabilities, MSI/MSI-X and INTx, AER, reset, SR-IOV configure, DMA-buf paths, and range intersection edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfio_pci_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfs.h -->
# sources/distributed-fs/ceph-client/include/linux/vfs.h

## Purpose
This lightweight header includes filesystem statfs definitions under the traditional `linux/vfs.h` include path.

## Important APIs, types, and functions
No new APIs are defined directly. It re-exports `linux/statfs.h` types and constants to callers that include `linux/vfs.h`.

## Control flow, state, and persistence
There is no control flow or state. Filesystem behavior is entirely in the included statfs and VFS implementation headers/sources.

## Dependencies and integration points
It depends on `linux/statfs.h` and integrates with legacy include users in filesystem and VFS code.

## Risks and test signals
The main risk is assuming this wrapper contains broader VFS definitions. Build coverage for include users is the relevant signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfsdebug.h -->
# sources/distributed-fs/ceph-client/include/linux/vfsdebug.h

## Purpose
This header provides VFS-specific BUG/WARN wrappers that optionally dump inode context before triggering debug assertions.

## Important APIs, types, and functions
With `CONFIG_DEBUG_VFS`, it exports `dump_inode()` and macros `VFS_BUG_ON`, `VFS_WARN_ON`, `VFS_WARN_ON_ONCE`, `VFS_WARN_ONCE`, `VFS_WARN`, `VFS_BUG_ON_INODE`, and `VFS_WARN_ON_INODE`. Disabled builds use `BUILD_BUG_ON_INVALID()` to type-check conditions without runtime checks.

## Control flow, state, and persistence
Debug builds evaluate conditions at runtime; inode-specific forms call `dump_inode()` before BUG/WARN. Non-debug builds compile away runtime checks while preserving expression validation. There is no persistent state.

## Dependencies and integration points
It depends on bug/warn infrastructure and inode declarations. It integrates with VFS and filesystem invariant checks.

## Risks and test signals
Risks include side effects in conditions disappearing in non-debug builds and crashing debug kernels via BUG_ON. Tests should compile both configs, trigger warning paths with fake inodes, and verify no side-effect reliance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vfsdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vga_switcheroo.h -->
# sources/distributed-fs/ceph-client/include/linux/vga_switcheroo.h

## Purpose
This header defines the VGA switcheroo framework for laptops with integrated/discrete GPUs sharing outputs, including mux handler and client callback contracts.

## Important APIs, types, and functions
Key enums are handler flags, client power state, and client IDs. Important types are `vga_switcheroo_handler` and `vga_switcheroo_client_ops`. APIs register/unregister GPU and audio clients, set framebuffer association, register/unregister handlers, query flags, lock/unlock DDC, process delayed switches, defer probing, query client power state, and install/finalize PM domain ops. Disabled builds mostly return success/no-op or `-ENODEV` for DDC.

## Control flow, state, and persistence
GPU/audio clients register with callbacks for power state, reprobe, switch readiness, and audio binding. A platform handler supplies mux/DDC/power operations and client ID detection. The framework coordinates delayed switching and power-domain behavior based on client readiness. State is runtime client/handler registration and power/mux ownership.

## Dependencies and integration points
It depends on framebuffer and PCI declarations. It integrates DRM GPU drivers, HDA audio, platform mux handlers, DDC/EDID probing, and runtime power management.

## Risks and test signals
Risks include switching while device files are open, DDC/AUX ownership mismatches, audio/GPU ID mismatch, and disabled-config behavior hiding missing dependencies. Tests should cover dual-GPU registration, handler registration, delayed switch, DDC locking, audio binding, PM domain ops, and unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vga_switcheroo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vgaarb.h -->
# sources/distributed-fs/ceph-client/include/linux/vgaarb.h

## Purpose
This header declares the VGA arbiter interface for coordinating legacy VGA IO and memory decode among multiple PCI VGA devices.

## Important APIs, types, and functions
Important resource bits are `VGA_RSRC_LEGACY_IO`, `VGA_RSRC_LEGACY_MEM`, `VGA_RSRC_NORMAL_IO`, and `VGA_RSRC_NORMAL_MEM`. APIs include `vga_set_legacy_decoding()`, `vga_get()`, `vga_put()`, default-device getters/setters, `vga_remove_vgacon()`, `vga_client_register()`, and `vga_get_interruptible()`.

## Control flow, state, and persistence
Drivers acquire VGA resources before accessing legacy ranges and release them afterward; clients can register decode callbacks and default device selection. Runtime state is arbiter ownership and decode routing. Disabled builds return permissive no-ops.

## Dependencies and integration points
It depends on video VGA constants and PCI devices. It integrates DRM/fbdev/VGA console drivers and PCI resource arbitration.

## Risks and test signals
Risks include deadlocks if resources are not released, allowing simultaneous legacy decode, and disabled-config assumptions. Tests should cover multi-GPU arbitration, interruptible acquire, default-device changes, vgacon removal, and client decode callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vgaarb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vhost_iotlb.h -->
# sources/distributed-fs/ceph-client/include/linux/vhost_iotlb.h

## Purpose
This header defines the vhost IOTLB interval map used to track guest IOVA to host address mappings for vhost and vDPA devices.

## Important APIs, types, and functions
Key types are `vhost_iotlb_map`, `vhost_iotlb`, and the iterator helper macro. APIs allocate/free an IOTLB, add/delete mappings, reset, translate by address/size, and initialize an embedded IOTLB.

## Control flow, state, and persistence
Users add mapping intervals with permissions and opaque metadata, translate IOVAs during data path setup, delete intervals on unmap, and reset on device teardown. State is an in-memory interval tree/list of mappings; no persistence is defined.

## Dependencies and integration points
It depends on interval trees, lists, and vhost UAPI permission flags. It integrates with vhost, vDPA, IOMMU/IOTLB update handling, and device-specific DMA translation.

## Risks and test signals
Risks include overlapping interval handling, permission mismatches, stale opaque pointers, and leaks on reset/free. Tests should cover add/delete/lookup boundaries, overlapping updates, permission filtering, full reset, and iteration order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/vhost_iotlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/via-core.h -->
# sources/distributed-fs/ceph-client/include/linux/via-core.h

## Purpose
This header defines shared VIA framebuffer/core structures, port configuration, power-management hooks, interrupt helpers, and register/bit constants.

## Important APIs, types, and functions
Key enums are `via_port_type`, `via_port_mode`, and `viafb_i2c_adap`. Important types are `via_port_cfg`, `viafb_pm_hooks`, and `viafb_dev`. APIs include `viafb_pm_register()`, `viafb_pm_unregister()`, `viafb_irq_enable()`, and `viafb_irq_disable()`. It also defines interrupt status/mask bits and MMIO helpers/state fields.

## Control flow, state, and persistence
VIA subdrivers share `viafb_dev` for PCI device, MMIO base, engine state, I2C adapters, port configuration, spinlocks, and PM hooks. Interrupt helpers modify video interrupt masks; PM hooks let subcomponents suspend/resume. State is runtime device and display configuration.

## Dependencies and integration points
It depends on types, IO, spinlocks, and PCI. It integrates VIA framebuffer, I2C, display output, capture, and power management code.

## Risks and test signals
Risks include shared MMIO lock misuse, stale PM hook pointers, wrong interrupt mask bits, and inconsistent port configuration. Tests should cover subdriver registration, IRQ enable/disable, suspend/resume callbacks, I2C adapter lookup, and register access under lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/via-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/via.h -->
# sources/distributed-fs/ceph-client/include/linux/via.h

## Purpose
This header defines VIA Super I/O parallel-port function and configuration register constants.

## Important APIs, types, and functions
It defines function values for SPP/ECP/EPP/disable/probe, parallel port capability bits, config index/data ports, and IRQ/DMA control register offsets.

## Control flow, state, and persistence
There is no executable flow. Platform or parport code writes these constants to VIA configuration ports to probe or set parallel-port mode and IRQ/DMA behavior. State is hardware register configuration.

## Dependencies and integration points
It integrates with VIA Super I/O and parallel-port setup code and has no header dependencies.

## Risks and test signals
Risks include writing the probe magic value to hardware as a real mode and using wrong config ports. Tests should validate probe/read/write sequences on supported chipsets or mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/via.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/via_i2c.h -->
# sources/distributed-fs/ceph-client/include/linux/via_i2c.h

## Purpose
This header declares VIA framebuffer I2C adapter state and helper APIs.

## Important APIs, types, and functions
Key type is `via_i2c_stuff` containing an `i2c_adapter`, bit-banged algo data, IO port, adapter type, and active flag. APIs include byte and multi-byte read/write helpers, adapter lookup, `viafb_i2c_init()`, and `viafb_i2c_exit()`.

## Control flow, state, and persistence
VIA framebuffer code initializes bit-banged I2C adapters, then callers perform indexed byte reads/writes to display devices such as DDC/EDID or panel controllers. State is runtime adapter registration and bit-bang GPIO/IO state.

## Dependencies and integration points
It depends on Linux I2C and i2c-algo-bit plus VIA core adapter enums. It integrates VIA display output code with EDID and peripheral control.

## Risks and test signals
Risks include bus selection mistakes, adapter lifetime issues, and bit-bang timing/port errors. Tests should cover init/exit, adapter lookup, read/write transactions, and invalid adapter IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/via_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/videodev2.h -->
# sources/distributed-fs/ceph-client/include/linux/videodev2.h

## Purpose
This kernel header wraps the V4L2 userspace API and supplies kernel-side dependencies needed by code including `linux/videodev2.h`.

## Important APIs, types, and functions
It includes `linux/time.h`, `linux/kernel.h`, and `uapi/linux/videodev2.h`. The API surface is the V4L2 UAPI structures, controls, formats, buffer types, and ioctls.

## Control flow, state, and persistence
There is no control flow in this wrapper. Runtime video state is handled by V4L2 core and drivers using the UAPI definitions.

## Dependencies and integration points
It integrates media/V4L2 kernel drivers with the stable userspace videodev2 ABI.

## Risks and test signals
Risks are ABI drift or including this wrapper when a stricter internal header is needed. Test signals are V4L2 UAPI compile checks and userspace ioctl compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/videodev2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio.h

## Purpose
This header defines the core virtio device and virtqueue API used by all Linux virtio drivers and transports.

## Important APIs, types, and functions
Key types are `virtqueue`, `virtio_map`, `virtio_admin_cmd`, `virtio_device`, and `virtio_driver`. APIs add in/out buffers and scatterlists, kick/notify queues, get completed buffers, manage callbacks, detach unused buffers, query/reset/resize vrings, register/unregister devices and drivers, signal config changes, freeze/restore/reset devices, iterate queues, map/unmap DMA buffers, and initialize optional debugfs filtering.

## Control flow, state, and persistence
Transports create `virtio_device` objects with config/map ops; drivers match by ID, negotiate features, find virtqueues, add buffers, kick devices, and handle callbacks/config changes. Core state includes device status flags, config-change locks, queue lists, negotiated feature arrays, mapping token, private driver data, and optional debug state. Persistence is not defined; virtio state is runtime and renegotiated after reset.

## Dependencies and integration points
It depends on scatterlists, device model, DMA mapping, completions, spinlocks, mod device tables, and virtio feature helpers. It integrates all virtio transports, virtio-net/block/scsi/console/etc. drivers, vDPA/VDUSE mapping, PM, and debugfs.

## Risks and test signals
Risks include queue callback races, broken-device state after reset, DMA mapping mismatches, feature-table omissions, and improper callback enable/disable loops. Tests should cover buffer enqueue/dequeue, notification suppression, reset/resize, DMA map/unmap, feature negotiation, PM freeze/restore, config change gating, and driver registration lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_anchor.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_anchor.h

## Purpose
This header provides an optional callback anchor for deciding whether a virtio device requires restricted memory access.

## Important APIs, types, and functions
With `CONFIG_VIRTIO_ANCHOR`, it declares `virtio_require_restricted_mem_acc()`, the function pointer `virtio_check_mem_acc_cb`, and `virtio_set_mem_acc_cb()`. Disabled builds make the setter a no-op.

## Control flow, state, and persistence
Platform/security code installs a callback; virtio code queries it to decide restricted memory access policy. State is a global callback pointer, not persistent storage.

## Dependencies and integration points
It integrates virtio with platform-specific memory-access policy such as confidential computing or restricted DMA environments.

## Risks and test signals
Risks include global callback lifetime/order, missing policy when disabled, and inconsistent decisions across devices. Tests should cover callback installation, policy query, module unload ordering, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_anchor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_byteorder.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_byteorder.h

## Purpose
This header provides virtio-specific endian conversion helpers for legacy and modern device fields.

## Important APIs, types, and functions
Important helpers are `virtio_legacy_is_little_endian()`, `__virtio16_to_cpu()`, `__cpu_to_virtio16()`, `__virtio32_to_cpu()`, `__cpu_to_virtio32()`, `__virtio64_to_cpu()`, and `__cpu_to_virtio64()`.

## Control flow, state, and persistence
Helpers branch on a runtime `little_endian` boolean or compile-time native endian for legacy devices. There is no state or persistence.

## Dependencies and integration points
It depends on virtio UAPI integer typedefs and CPU endian helpers. It integrates with virtio config-space and ring/data-structure accessors.

## Risks and test signals
Risks include using legacy host-endian rules for modern little-endian devices or vice versa. Tests should cover big-endian and little-endian builds, legacy and VERSION_1 devices, and 16/32/64-bit conversion round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_config.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_config.h

## Purpose
This header defines virtio transport configuration operations, DMA mapping operations, feature helpers, virtqueue discovery helpers, device-ready sequencing, endian-safe config accessors, and conditional feature reads.

## Important APIs, types, and functions
Key types are `virtio_shm_region`, `virtqueue_info`, `virtio_config_ops`, and `virtio_map_ops`. Important helpers include feature test/set/clear wrappers, `virtio_get_features()`, `virtio_has_dma_quirk()`, `virtio_find_vqs()`, `virtio_find_single_vq()`, `virtio_synchronize_cbs()`, `virtio_device_ready()`, bus name and affinity helpers, shared-memory lookup, endian conversions, `virtio_cread/cwrite` macros, little-endian config accessors, `__virtio_cread_many()`, byte/16/32/64 accessors, and feature-gated reads.

## Control flow, state, and persistence
Transports implement config ops for get/set/status/reset/find_vqs/features/shared memory/queue reset. Drivers use helpers to negotiate features, allocate queues, synchronize callbacks, set DRIVER_OK, and read/write config fields with generation-stable multi-byte reads. Runtime state is in `virtio_device`, transport config space, virtqueues, and mapping tokens. Nothing is persisted by this header.

## Dependencies and integration points
It depends on virtio core, byteorder helpers, compiler type checking, errno/bug helpers, and virtio UAPI config bits. It integrates every virtio transport and driver with feature negotiation, queue setup, DMA mapping, and config space access.

## Risks and test signals
Risks include sleeping config ops called from atomic context, missing generation retry for large fields, wrong endian accessor choice, feature checks for driver-unoffered bits, and queue reset callback synchronization. Tests should cover feature arrays, config read/write type checks, generation-change retry, DRIVER_OK sequencing, queue affinity, shared memory, DMA map ops, and feature-gated access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_dma_buf.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_dma_buf.h

## Purpose
This header defines dma-buf integration for virtio exported objects identified by UUIDs.

## Important APIs, types, and functions
Key type is `virtio_dma_buf_ops`, embedding base `dma_buf_ops` plus optional `device_attach` and required `get_uuid`. APIs are `virtio_dma_buf_attach()`, `virtio_dma_buf_export()`, `is_virtio_dma_buf()`, and `virtio_dma_buf_get_uuid()`.

## Control flow, state, and persistence
Exporters provide virtio-aware dma-buf ops, export an object, and attach devices through `virtio_dma_buf_attach()` so virtio-specific attach validation can run. UUID lookup lets consumers identify shared objects. State is dma-buf lifetime and exporter private state.

## Dependencies and integration points
It depends on dma-buf, UUID, and virtio core APIs. It integrates virtio GPU or other virtio object exporters with generic dma-buf consumers.

## Risks and test signals
Risks include using the wrong attach op, missing UUID callbacks, and object identity collisions. Tests should cover export, attach success/failure, UUID retrieval, type detection, and dma-buf release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_dma_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_features.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_features.h

## Purpose
This header defines fixed-size virtio feature bit arrays and helper operations for testing, setting, clearing, copying, and comparing feature sets.

## Important APIs, types, and functions
Important definitions are `VIRTIO_FEATURES_U64S`, `VIRTIO_FEATURES_BITS`, `VIRTIO_BIT()`, `VIRTIO_U64()`, `VIRTIO_DECLARE_FEATURES()`, and helpers `virtio_features_chk_bit()`, test/set/clear/zero/from_u64/equal/copy/andnot.

## Control flow, state, and persistence
Helpers operate on two-u64 arrays representing the supported feature namespace. Constant out-of-range feature bits trigger build errors; dynamic out-of-range bits warn and return false/no-op. State belongs to caller feature arrays and is runtime negotiation state.

## Dependencies and integration points
It depends on bits, bug, and string helpers. It integrates virtio core, transports, vDPA, and any code manipulating feature sets beyond the lower 64 bits.

## Risks and test signals
Risks include assuming only one u64 of features, out-of-range feature indexes, and copying arrays with the wrong size. Tests should cover boundary bits, dynamic invalid bits, equality/copy/andnot, and `VIRTIO_DECLARE_FEATURES()` layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_net.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_net.h

## Purpose
This header provides kernel helpers for translating between virtio-net headers and Linux `sk_buff` checksum/GSO/tunnel metadata.

## Important APIs, types, and functions
Important helpers include `virtio_net_hdr_match_proto()`, `virtio_net_hdr_set_proto()`, `virtio_net_hdr_to_skb()`, internal `__virtio_net_hdr_to_skb()`, `virtio_net_hdr_from_skb()`, header-length setters, `virtio_l3min()`, tunnel-aware `virtio_net_hdr_tnl_to_skb()`, checksum validation `virtio_net_handle_csum_offload()`, and tunnel-aware `virtio_net_hdr_tnl_from_skb()`.

## Control flow, state, and persistence
RX paths parse virtio header flags, GSO type, checksum start/offset, optional tunnel offsets, and set skb protocol, transport headers, checksum state, GSO metadata, and encapsulation. TX paths derive virtio header fields from skb GSO/checksum/tunnel metadata and negotiated features. State is per-packet skb metadata and header contents; no persistence is involved.

## Dependencies and integration points
It depends on VLAN/IP/IPv6/UDP/TCP and virtio-net UAPI headers plus skbuff helpers. It integrates virtio-net, vhost-net, tap/macvtap-like paths, and packet validation for offloads.

## Risks and test signals
Risks include accepting invalid checksum offsets, GSO size zero or `GSO_BY_FRAGS`, unsupported tunnel metadata without negotiated features, protocol misclassification, and modifying skb GSO type during header creation. Tests should cover TCPv4/v6, UDP/UFO/USO, tunnel GSO with and without checksum, DATA_VALID handling, malformed offsets, endian variants, and VLAN header lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_pci_admin.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_pci_admin.h

## Purpose
This header declares virtio PCI admin command helpers for device parts and optional legacy IO access mediation.

## Important APIs, types, and functions
APIs include optional legacy helpers for probing legacy IO support, common/device IO read/write, and notify-info lookup, plus `virtio_pci_admin_has_dev_parts()`, `virtio_pci_admin_mode_set()`, object create/destroy, device-parts metadata get, parts get, and parts set.

## Control flow, state, and persistence
Virtio PCI code uses admin queues to change admin mode, create/destroy admin objects, fetch/set device partition metadata, and optionally access legacy fields. State is device-admin runtime state and objects managed by the device.

## Dependencies and integration points
It depends on PCI and scatterlists. It integrates virtio PCI transports with admin queue features for device partitioning and legacy access.

## Risks and test signals
Risks include unsupported admin command paths, scatterlist sizing errors, object ID leaks, and legacy IO access without negotiated support. Tests should cover capability detection, mode setting, object lifecycle, metadata get, parts get/set, and disabled legacy config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_pci_admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_pci_legacy.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_pci_legacy.h

## Purpose
This header defines the helper interface for legacy virtio PCI devices using IO BAR configuration space.

## Important APIs, types, and functions
Key type is `virtio_pci_legacy_device`, storing the PCI device, ISR mapping, and legacy IO config mapping. APIs include probe/remove, get/set features, generation/status access, queue selection/size/address/enable/notify, config vector, queue vector, config-space read/write, device reset, and deletion helpers.

## Control flow, state, and persistence
The legacy transport probes PCI IO resources, maps legacy config and ISR areas, negotiates 32/64-bit features as supported, programs queue PFNs/vectors, and tears down mappings on remove. State is PCI IO mapping and runtime queue/status/config values.

## Dependencies and integration points
It depends on PCI and virtio PCI UAPI definitions. It integrates legacy virtio PCI transport code with the generic virtio core.

## Risks and test signals
Risks include IO BAR mapping failure, legacy endian assumptions, queue PFN programming mistakes, and MSI-X vector handling. Tests should cover legacy probe/remove, feature negotiation, queue setup, config read/write, interrupt status, reset, and absent IO resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_pci_legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_pci_modern.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_pci_modern.h

## Purpose
This header defines the helper interface and mapped capability state for modern virtio PCI devices.

## Important APIs, types, and functions
Key type is `virtio_pci_modern_device`, storing PCI device, mapped common/notify/isr/device/shared/admin capabilities, notify geometry, device ID, and modern-only state. Helpers include endian-safe MMIO reads/writes, feature get/set, generation/status access, queue vector/address/enable/size/count/reset helpers, notify mapping, probe/remove, and admin virtqueue index/number helpers.

## Control flow, state, and persistence
Probe locates and maps modern PCI capabilities, drivers negotiate extended features through select registers, configure queues via common config, map notify regions, and read/write device config through mapped BARs. Runtime state is PCI capability mapping, queue configuration, status, generation, and notification offsets.

## Dependencies and integration points
It depends on PCI, virtio config, and virtio PCI UAPI headers. It integrates modern virtio PCI transport, admin queues, shared memory regions, and virtio core feature/config operations.

## Risks and test signals
Risks include wrong BAR/offset mapping, notify multiplier errors, feature select misuse, queue reset semantics, and non-atomic two-part 64-bit writes. Tests should cover capability discovery, feature banks, queue setup/reset, notify mapping, config generation, status transitions, and admin queue discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_pci_modern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_ring.h -->
# sources/distributed-fs/ceph-client/include/linux/virtio_ring.h

## Purpose
This header declares virtio ring construction, DMA policy, and vring interrupt APIs shared by virtio transports and vring implementations.

## Important APIs, types, and functions
Important APIs include `vring_create_virtqueue()`, `vring_create_virtqueue_dma()`, `vring_new_virtqueue()`, `vring_del_virtqueue()`, `vring_transport_features()`, `vring_interrupt()`, `vring_use_dma_api()`, `virtio_has_iommu_quirk()`, and weak barriers for virtqueue memory ordering. It connects generic `virtqueue` objects with UAPI `vring` layouts.

## Control flow, state, and persistence
Transports create or wrap vrings with callback/name/context metadata, DMA device information, queue index, ring size/alignment, and weak-barrier policy. Runtime data path enqueues descriptors through virtqueue APIs and receives interrupts through `vring_interrupt()`. State is allocated descriptor/avail/used ring memory, DMA mappings, callback suppression state, and queue private data.

## Dependencies and integration points
It depends on scatterlists, DMA mapping, virtio core, and virtio ring UAPI. It integrates PCI/MMIO/CCW/vDPA/VDUSE transports with the generic virtqueue API and platform DMA/IOMMU policy.

## Risks and test signals
Risks include wrong DMA API decision for legacy quirks, alignment/size mismatches, missing memory barriers, interrupt handling for broken queues, and teardown with outstanding buffers. Tests should cover split/packed ring creation where supported by implementation, DMA and non-DMA paths, notification interrupts, feature filtering, delete cleanup, and IOMMU quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/virtio_ring.h -->
