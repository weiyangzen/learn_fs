# subset-b-005538 Research

Grouped source research for USB Type-C, USB Power Delivery, TCPM, TCPCI, and selected controller drivers under `sources/distributed-fs/ceph-client/drivers/usb/typec`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/wcd939x-usbss.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/wcd939x-usbss.c

## Purpose

`wcd939x-usbss.c` is the Qualcomm WCD939x USBSS Type-C mux/switch driver. It programs an I2C regmap in the audio codec sideband switch block so SBU/USB/DP/audio accessory routes match Type-C orientation and mux mode, then forwards the same switch and mux events to the downstream codec mux objects.

## Important APIs, Types, and Functions

`struct wcd939x_usbss` stores the I2C client, reset GPIO, optional `vdd` regulator, typec switch/mux registrations, codec mux handles, current orientation, mode, SVID, and a mutex for serializing updates. `wcd939x_usbss_set()` is the central hardware programming routine for safe, USB, DisplayPort, mixed DP+USB, and audio accessory states. `wcd939x_usbss_switch_set()` updates orientation and then calls `typec_switch_set()` on the codec switch. `wcd939x_usbss_mux_set()` updates mode/SVID and then calls `typec_mux_set()` on the codec mux. Probe initializes regmap paging, power/reset sequencing, fixed analog tuning bits, safe-mode routing, and the Type-C switch/mux devices.

## Control Flow

Probe allocates state, gets regmap/reset/regulator resources, acquires peer codec mux and switch by fwnode, powers and resets the chip, applies default manual/boost/RCO/device-enable programming, calls `wcd939x_usbss_set()` in safe mode, and registers Type-C switch then mux. Runtime changes enter through Type-C switch or mux callbacks, take the mutex, update cached orientation/mode/SVID, reprogram the local USBSS routes, release the mutex, and forward the event to the codec-facing object. Remove unregisters mux/switch, disables the regulator, and drops codec references.

## State and Persistence Behavior

The driver persists only runtime cached orientation, mux mode, and SVID plus device handles. Hardware state is register-resident and reset/power-cycle volatile. The mutex protects against concurrent switch and mux callbacks producing interleaved route programming.

## Dependencies and Integration Points

It depends on I2C regmap with range paging, regulators, optional reset GPIO, `linux/usb/typec_mux.h`, DisplayPort altmode constants, and fwnode-discovered codec Type-C mux/switch providers. It integrates in the Type-C mux graph as both a local hardware controller and a forwarding shim to the codec path.

## Risks and Test Signals

Risks include optional regulator handling that treats every `devm_regulator_get_optional()` error as fatal, long manual register sequences that can leave partially switched routes on I/O failure, ignoring return values while writing audio linearizer coefficients, and mode/SVID combinations returning `-EOPNOTSUPP`. Test signals include probe power/reset timing, safe-mode setup, normal/reverse USB routing, DP C/E and D/F routing, audio accessory orientation swaps, forwarded codec events, and remove/unwind reference cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/wcd939x-usbss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/pd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/pd.c

## Purpose

`pd.c` implements the USB Power Delivery class sysfs model. It creates `/sys/class/usb_power_delivery/pdN` devices, optional capability subdevices, and child PDO devices exposing decoded fixed, variable, battery, PPS, and SPR AVS PDO fields.

## Important APIs, Types, and Functions

`struct pdo` wraps each PDO as a device with `object_position` and raw `u32 pdo`. Exported APIs are `usb_power_delivery_register()`, `usb_power_delivery_unregister()`, `usb_power_delivery_find()`, `usb_power_delivery_register_capabilities()`, `usb_power_delivery_unregister_capabilities()`, `usb_power_delivery_link_device()`, and `usb_power_delivery_unlink_device()`. Attribute groups decode PD bitfields via helpers from `<linux/usb/pd.h>`, with separate device types for source/sink fixed, variable, battery, PPS APDO, and SPR AVS APDO.

## Control Flow

Class init registers the `usb_power_delivery` class and exit destroys the IDA then unregisters the class. Registering a PD object allocates an ID, stores revision/version, initializes the class device, and publishes revision/version attributes. Capability registration creates a `source-capabilities` or `sink-capabilities` child, then iterates `desc->pdo[]` until `PDO_MAX_OBJECTS` or zero and calls `add_pdo()` for each supported PDO. Unregister walks child PDO devices before unregistering the capability device. Link/unlink add or remove a `usb_power_delivery` sysfs symlink and hold paired references while the link exists.

## State and Persistence Behavior

The class keeps a global `IDA` for stable runtime names. All PD/capability/PDO objects are device-model allocations released through `.release` callbacks; no negotiated values are persisted across unregister. PDO content is immutable after device registration.

## Dependencies and Integration Points

It depends on Linux device/class/sysfs APIs, USB PD encoding helpers, and Type-C role helpers. TCPM and UCSI use it to expose local and partner PD support, while Type-C class code links PD devices to ports and partners.

## Risks and Test Signals

Risks include only supporting PPS and SPR AVS APDO types, silently skipping unknown APDOs, requiring zero-terminated PDO arrays, link reference leaks if callers do not unlink, and sysfs ABI correctness for units and first-fixed-PDO visibility rules. Test signals include class init/exit, PD object registration with and without version, source and sink capability trees, each PDO type's attributes, unknown APDO warnings, unregister cleanup of children, and symlink reference balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/pd.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/pd.h

## Purpose

`pd.h` is the private header for the USB Power Delivery class implementation. It defines the internal device wrappers that back `pd.c` and declares class lifecycle and lookup helpers.

## Important APIs, Types, and Functions

`struct usb_power_delivery` contains the class `struct device`, allocated ID, PD revision, and optional version. `struct usb_power_delivery_capabilities` contains the capabilities device, parent PD pointer, and source/sink role. Container macros convert devices to those wrappers. Prototypes expose `usb_power_delivery_find()`, `usb_power_delivery_init()`, and `usb_power_delivery_exit()`.

## Control Flow

The header has no executable control flow. It defines the device layout and local helper contract consumed by `pd.c` and the Type-C class initialization path.

## State and Persistence Behavior

The structures describe runtime-only device-model state. IDs, revision/version, and role are retained while the corresponding devices exist and are freed by device release callbacks.

## Dependencies and Integration Points

It includes `linux/device.h` and `linux/usb/typec.h`, tying the private PD class state to the Linux device core and Type-C role enums. It is intentionally narrower than the public `<linux/usb/pd.h>` API.

## Risks and Test Signals

Risks are local ABI coupling with `pd.c`: changing structure fields or macros affects every release path and sysfs callback. Test signals are compile coverage of PD class init, registration, sysfs attribute access, and lookup by class device name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/pd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/port-mapper.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/port-mapper.c

## Purpose

`port-mapper.c` links ACPI-described USB and USB4 ports with a Type-C connector using the component framework. It lets devices sharing the connector's ACPI physical location data bind as components of the Type-C port.

## Important APIs, Types, and Functions

`typec_link_ports()` scans ACPI devices for matching `_PLD` CRCs and builds a `component_match` list. `typec_unlink_ports()` removes the component master. `typec_aggregate_bind()` and `typec_aggregate_unbind()` call `component_bind_all()` and `component_unbind_all()` with the connector object. `typec_port_match()` compares ACPI companion devices and optionally adds a USB4 host-interface match using `usb4_usb3_port_match()`.

## Control Flow

Linking exits early for non-ACPI ports. For ACPI ports, it walks all ACPI devices, skips the connector's own companion, adds devices whose `_PLD` CRC matches, and adds USB4 matches when the matching fwnode advertises `usb4-host-interface`. If any match exists, the Type-C port becomes a component master. Unlink removes the master only for ACPI-backed ports.

## State and Persistence Behavior

The file stores no long-lived global state. Component framework registrations persist until unlink and bind/unbind the connector's `port->con` aggregate as matched devices appear or disappear.

## Dependencies and Integration Points

Dependencies are ACPI device enumeration, firmware nodes, component framework, Thunderbolt/USB4 matching, USB core, and Type-C class internals from `class.h`. It is a firmware topology bridge between Type-C connectors and USB/USB4 port devices.

## Risks and Test Signals

Risks include `_PLD` CRC collisions, the documented limitation that a connector can have only one component master, incorrect assumptions about USB4 fwnode properties, and no work on non-ACPI systems. Test signals include ACPI systems with shared `_PLD`, USB3 port matching, USB4 host-interface links, component bind/unbind order, and unlink on connector teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/port-mapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/retimer.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/retimer.c

## Purpose

`retimer.c` implements the Type-C retimer class. It lets retimer drivers register device-model objects and lets Type-C mux/port code discover retimers through firmware graph connections named `retimer-switch`.

## Important APIs, Types, and Functions

Exports are `fwnode_typec_retimer_get()`, `typec_retimer_put()`, `typec_retimer_set()`, `typec_retimer_register()`, `typec_retimer_unregister()`, and `typec_retimer_get_drvdata()`. `typec_retimer_match()` uses `fwnode_connection_find_match()` and `class_find_device()` with `retimer_fwnode_match()`. `struct typec_retimer_desc` from the public header supplies name, fwnode, drvdata, and the required set callback.

## Control Flow

Registration validates a `set` callback, allocates a retimer, initializes its device under `retimer_class`, binds parent/fwnode/type/driver data, names it, and calls `device_add()`. Discovery searches firmware connections and returns `NULL` for no connection, `-EPROBE_DEFER` when a connection exists but the device is not registered, or a referenced retimer after pinning the parent driver's module. `typec_retimer_set()` is a no-op for NULL/error handles and otherwise invokes the provider callback. Put releases the module and device references.

## State and Persistence Behavior

Retimer objects are runtime device-model state with lifecycle managed by device registration and `.release`. No hardware state is cached here beyond the callback pointer and driver data; actual retimer state lives in provider drivers.

## Dependencies and Integration Points

It depends on firmware-node connection APIs, Linux class/device core, module reference management, and Type-C retimer public definitions. Retimer-capable mux drivers such as PS883x, NB7VPQ904M, and PTN36502 register through this class.

## Risks and Test Signals

Risks include module owner assumptions through `retimer->dev.parent->driver->owner`, discovery deferral behavior when firmware declares a retimer not yet probed, and provider callbacks being responsible for all hardware validation. Test signals include registration failure on missing callback, fwnode lookup success/defer/no-match cases, module refcount balancing, `typec_retimer_set()` passthrough, and unregister release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/retimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/retimer.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/retimer.h

## Purpose

`retimer.h` is the private header for the Type-C retimer class implementation. It defines the internal retimer object layout and type-check helper.

## Important APIs, Types, and Functions

`struct typec_retimer` embeds a `struct device` and stores the provider `typec_retimer_set_fn_t set` callback. `to_typec_retimer()` converts a device pointer to the wrapper. `typec_retimer_dev_type` and `is_typec_retimer()` identify retimer devices in class searches.

## Control Flow

There is no runtime flow in the header. It provides the object contract used by `retimer.c` and retimer provider/consumer code.

## State and Persistence Behavior

The structure holds runtime device-model state only. The callback remains valid while the provider device and module are referenced.

## Dependencies and Integration Points

It includes the public `linux/usb/typec_retimer.h` definitions and is included by `retimer.c`. It is the private bridge between public Type-C retimer APIs and the Linux device core representation.

## Risks and Test Signals

Risks are local coupling around `dev.type` checks and callback lifetime. Test signals are compile coverage of `is_typec_retimer()`, class lookup matching, set callback invocation, and release through `typec_retimer_dev_type`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/retimer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/rt1719.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/rt1719.c

## Purpose

`rt1719.c` is the Richtek RT1719 sink-only USB-PD controller driver. It exposes a Type-C sink port, USB role switch, and USB power-supply interface while interpreting RT1719 autonomous PD policy/register events.

## Important APIs, Types, and Functions

`struct rt1719_data` holds regmap, Type-C port/partner, role switch, power-supply descriptor, partner identity, completion for requests, attach/PD flags, current volt/current data, source PDOs, generated sink capabilities, and cached connection registers. Key helpers are `rt1719_attach()`, `rt1719_detach()`, `rt1719_update_source_pdos()`, `rt1719_update_pwr_opmode()`, `rt1719_usbpd_request_voltage()`, `rt1719_dr_set()`, `rt1719_irq_handler()`, `rt1719_get_caps()`, and `rt1719_init_attach_state()`.

## Control Flow

Probe builds regmap, verifies the unique PID, reads power selection and USB-role capability registers, gets the connector child and USB role switch, registers a power supply, registers a Type-C sink/DRD-data port with debug accessory support, initializes existing attach/contract state, and requests the IRQ. The IRQ reads events, policy info, and stats, updates cached state, handles data-role swap acceptance, attach, detach, source capability reception, and policy-engine-ready completion, then clears handled events. Voltage requests and data-role swaps write request bits and wait up to 400 ms for `PE_SNK_RDY`.

## State and Persistence Behavior

Runtime state tracks whether attached, PD capable, selected source PDO, advertised USB type, voltage/current in micro-units, and partner object lifetime. The chip autonomously negotiates PD; the driver mirrors register state into Linux Type-C and power-supply objects. No file-backed persistence exists.

## Dependencies and Integration Points

It depends on I2C regmap, Type-C class, USB role-switch, USB PD PDO helpers, completions, and power-supply core. It integrates autonomous RT1719 policy decisions with Linux userspace through `POWER_SUPPLY_PROP_USB_TYPE`, `VOLTAGE_NOW`, `CURRENT_MAX`, and `CURRENT_NOW`.

## Risks and Test Signals

Risks include indexing `spdos[spdo_sel - 1]` from hardware fields, fixed-voltage-only request logic, no explicit locking around power-supply writes versus IRQ updates, possible partner registration failure not handled beyond storing an error pointer, and probe error paths that do not unregister the Type-C port after late failures. Test signals include PID mismatch, attach/detach IRQs, source PDO count bounds, PD-ready completion timeout, voltage selection for 5/9/12/15/20 V, data-role swap with and without partner support, and power-supply change notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/rt1719.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/stusb160x.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/stusb160x.c

## Purpose

`stusb160x.c` is the STUSB160x Type-C controller driver. It configures port mode/current advertisement, registers a Type-C port, manages VBUS/VCONN regulators, handles attach/detach interrupts, and updates USB role-switch state.

## Important APIs, Types, and Functions

`struct stusb160x` stores regmap, regulators (`vdd`, `vsys`, `vconn`, selected main supply), Type-C port/capabilities/partner, port type, power opmode, VBUS state, and USB role switch. Important functions are `stusb160x_get_caps()`, `stusb160x_get_fw_caps()`, `stusb160x_chip_init()`, `stusb160x_attach()`, `stusb160x_detach()`, `stusb160x_irq_handler()`, `stusb160x_irq_init()`, suspend/resume handlers, and regmap readable/writeable/volatile/precious callbacks.

## Control Flow

Probe initializes regmap and supplies, gets the `connector` fwnode, purges fw_devlink links for legacy DT connector nodes, selects main supply, reads chip capabilities, applies optional firmware overrides, initializes chip mode and interrupt masks, registers the Type-C port, sets the initial power opmode, and either requests an IRQ plus role switch or enables source VBUS permanently when no IRQ exists. IRQ handling checks alert/status registers and calls attach or detach on CC attach transitions. Resume synchronizes regcache, reconciles missed attach/detach state, and unmasks CC interrupts.

## State and Persistence Behavior

Driver state tracks registered partner pointer, selected port type/opmode, whether VBUS is currently enabled, and regulator handles. Hardware registers are cached via maple regcache for nonvolatile register state. Attach state is not persisted and is resynchronized from status on init/resume.

## Dependencies and Integration Points

It depends on I2C regmap, regulators, Type-C class, USB role-switch, firmware connector properties, PM callbacks, and STUSB160x register semantics. It integrates VBUS sourcing/sinking and partner/accessory information into Linux Type-C objects.

## Risks and Test Signals

Risks include limited PD support (`usb_pd = false`), duplicate or missing partner handling if attach transitions are noisy, optional regulator combinations, role-switch only acquired when IRQ exists, VCONN disable paths depending on register reads, and wake/resume attach changes. Test signals include source/sink/DRP firmware overrides, current advertisement programming, attach/detach IRQs for normal/debug/audio accessories, VBUS/VCONN regulator enable and unwind, no-IRQ source behavior, suspend/resume attach reconciliation, and regcache synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/stusb160x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Kconfig

## Purpose

`tcpm/Kconfig` declares build-time options for the USB Type-C Port Controller Manager and its TCPCI/FUSB302/WCOVE/Qualcomm PMIC controller drivers.

## Important APIs, Types, and Functions

The key symbols are `TYPEC_TCPM`, `TYPEC_TCPCI`, `TYPEC_RT1711H`, `TYPEC_MT6360`, `TYPEC_TCPCI_MT6370`, `TYPEC_TCPCI_MAXIM`, `TYPEC_FUSB302`, `TYPEC_WCOVE`, and `TYPEC_QCOM_PMIC`. Dependencies and selects wire in USB, I2C, regmap-I2C, power-supply, USB role-switch, ACPI, MFD support, DRM HPD bridge support, and Qualcomm architecture/compile-test coverage.

## Control Flow

There is no runtime control flow. Kconfig gates which modules are available, nests vendor TCPCI drivers under `TYPEC_TCPCI`, and restricts all controller options to the `TYPEC_TCPM` block.

## State and Persistence Behavior

Configuration state is persisted in the kernel `.config`, affecting which object files are built in or modular. It does not create runtime state directly.

## Dependencies and Integration Points

It integrates TCPM drivers with the kernel build system and dependency graph. `TYPEC_FUSB302` and `TYPEC_QCOM_PMIC` select `DRM_AUX_HPD_BRIDGE` when the DRM bridge and OF dependencies are available, matching their runtime HPD bridge allocation.

## Risks and Test Signals

Risks include missing dependency/select updates when drivers gain new subsystems, vendor drivers hidden by parent symbols, and compile-test gaps for platform-specific options. Test signals include `allyesconfig`, `allmodconfig`, `COMPILE_TEST` for Qualcomm PMIC, and building each module combination with parent symbols enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Makefile

## Purpose

`tcpm/Makefile` maps TCPM-related Kconfig symbols to object files and composite modules.

## Important APIs, Types, and Functions

`tcpm.o`, `fusb302.o`, `typec_wcove.o`, `tcpci.o`, `tcpci_rt1711h.o`, `tcpci_mt6360.o`, `tcpci_mt6370.o`, `tcpci_maxim.o`, and the `qcom/` subdirectory are selected by their matching config symbols. Composite definitions map `typec_wcove-y := wcove.o` and `tcpci_maxim-y += tcpci_maxim_core.o maxim_contaminant.o`.

## Control Flow

There is no runtime flow. Kbuild uses these object lists to decide module names and link composition.

## State and Persistence Behavior

The file controls build artifacts only. It has no runtime persistence.

## Dependencies and Integration Points

It integrates the generic TCPM core, TCPCI framework, vendor TCPCI helpers, FUSB302, WCOVE, Maxim contaminant helper, and Qualcomm PMIC subdirectory into the kernel build.

## Risks and Test Signals

Risks include stale object lists when files move or composite modules gain dependencies, especially Maxim contaminant coupling to `tcpci_maxim_core.o`. Test signals are module builds for each config and verifying expected module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302.c

## Purpose

`fusb302.c` is the Fairchild/FCS FUSB302 Type-C port-controller driver for TCPM. It uses SMBus/I2C register access to implement the `tcpc_dev` callbacks for CC detection, DRP toggling, VBUS/VCONN control, PD RX/TX, and interrupt-driven state changes.

## Important APIs, Types, and Functions

`struct fusb302_chip` holds device/I2C/TCPM state, regulator, GPIO/IRQ/workqueue state, optional extcon, mutex-protected Type-C/PD state, current CC polarity/status, and debugfs log buffers. Key TCPM callbacks are `tcpm_init()`, `tcpm_get_vbus()`, `tcpm_get_current_limit()`, `tcpm_set_cc()`, `tcpm_get_cc()`, `tcpm_set_vconn()`, `tcpm_set_vbus()`, `tcpm_set_pd_rx()`, `tcpm_set_roles()`, `tcpm_start_toggling()`, and `tcpm_pd_transmit()`. Internal control paths include `fusb302_set_toggling()`, `fusb302_handle_togdone_snk()`, `fusb302_handle_togdone_src()`, `fusb302_pd_send_message()`, `fusb302_pd_read_message()`, and `fusb302_irq_work()`.

## Control Flow

Probe checks SMBus block support, allocates state, optionally looks up ACPI extcon, gets the VBUS regulator, creates a single-thread workqueue, initializes IRQ work and BC-level delayed work, creates debugfs, gets IRQ or GPIO interrupt, obtains connector fwnode or software defaults, allocates a DRM DP HPD bridge, registers with TCPM, requests the low-level IRQ, enables wake, and adds the bridge. TCPM calls initialize the chip via reset, auto-retry, interrupt masks, power mode, VBUS sampling, and device ID logging. The interrupt handler disables the level IRQ and schedules work; the worker reads interrupt/status snapshots, updates VBUS, handles TOGDONE CC resolution, schedules delayed sink current measurement, handles source detach comparator changes, maps PD collision/retry/hard-reset/TX/RX events into TCPM callbacks, then re-enables the IRQ.

## State and Persistence Behavior

The driver caches VBUS, VCONN, charge, PD RX, toggling mode, interrupt enable intentions, CC polarity/status, and sink PDO fallback data in memory. Hardware register state is volatile and reinitialized by TCPM init. Debugfs keeps a circular in-memory log only. Suspend marks IRQs as deferred, flushes current work before bus suspend, and resume schedules work if an IRQ arrived while suspended.

## Dependencies and Integration Points

It depends on I2C SMBus block operations, GPIO IRQ or client IRQ, regulator core, TCPM, USB PD helpers, Type-C class enums, optional extcon charger detection, workqueues, debugfs, software fwnodes, and DRM AUX HPD bridge. It is one of the main TCPM hardware adapters.

## Risks and Test Signals

Risks include complex interrupt ordering between TX success and GoodCRC, delayed BC-level measurement during PD activity, level-triggered IRQ re-enable on error paths, manual FIFO token framing, missing cleanup if HPD bridge add fails after IRQ request, and concurrency between TCPM callbacks and IRQ work. Test signals include TCPM registration, SW reset and register init, source/sink/DRP toggling outcomes, CC attach/detach and current-level changes, VBUS regulator transitions, PD send/receive/hard-reset/retry/collision IRQs, suspend/resume IRQ deferral, debugfs log operation, and software-node fallback connector properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302_reg.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302_reg.h

## Purpose

`fusb302_reg.h` defines the FUSB302 register map, bit masks, status values, and TX FIFO token constants used by `fusb302.c`.

## Important APIs, Types, and Functions

The header defines register addresses for device ID, switches, measure, controls, masks, power, reset, status, interrupts, and FIFOs. Bit masks describe CC pull-up/down, VCONN, measurement selection, PD auto-GoodCRC, power/data role bits, toggle modes, retry counts, interrupt masks/statuses, BC levels, and FIFO states. `enum fusb302_txfifo_tokens` defines SOP sync, reset, PACKSYM, JAMCRC, EOP, TXON, and TXOFF tokens for PD message serialization.

## Control Flow

There is no executable flow. The constants drive every register read/write and FIFO command sequence in the FUSB302 driver.

## State and Persistence Behavior

The header has no state. It names volatile hardware state and command encodings.

## Dependencies and Integration Points

It is included directly by `fusb302.c`. The definitions must match the FUSB302 data sheet and the TCPM driver's expectations for CC and PD state transitions.

## Risks and Test Signals

Risks include incorrect bit masks for multi-bit fields, token ordering assumptions in TX FIFO framing, and stale constants for silicon variants. Test signals are register-level driver tests for CC setup, toggling, interrupt masks, PD reset, FIFO TX/RX, and device ID reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/fusb302_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/maxim_contaminant.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/maxim_contaminant.c

## Purpose

`maxim_contaminant.c` implements Maxim TCPCI contaminant/water detection support. It reduces wakeups and false connects by measuring CC/SBU resistance and switching the controller between dry-detection and normal toggling states.

## Important APIs, Types, and Functions

The exported helper is `max_contaminant_is_contaminant()`, declared in `tcpci_maxim.h` and called by the Maxim TCPCI core. Internal helpers include `max_contaminant_read_adc_mv()`, `max_contaminant_read_resistance_kohm()`, `max_contaminant_read_comparators()`, `max_contaminant_detect_contaminant()`, `max_contaminant_enable_dry_detection()`, and `max_contaminant_enable_toggling()`. `enum fladc_select` selects ADC channels and `enum contamiant_state` in the header tracks not-detected, detected, and sink cases.

## Control Flow

When asked to evaluate a CC event, the helper reads CC status and power control, treats active toggling with a prior detected contaminant as contaminant, optionally delays for debounce, checks for both CC pins open, temporarily overrides role control, measures CC1/CC2/SBU1/SBU2 resistances using 1 uA sources and ADC channels, reads comparators with 80 uA source, infers sink or contaminant state, restores or adjusts role control, and either enables dry detection or resumes normal toggling. It returns whether TCPM should treat the event as contaminant and whether CC handling was already consumed.

## State and Persistence Behavior

Persistent runtime state is `chip->contaminant_state`, stored in the Maxim chip wrapper. Hardware state changes include ADC enable/channel selection, current-source configuration, OVP disable/enable, comparator enable, role control overrides, low-power dry detection, and Look4Connection commands.

## Dependencies and Integration Points

It depends on Maxim vendor registers from `tcpci_maxim.h`, generic TCPCI register definitions, regmap, bitfield helpers, TCPM/Type-C enums, and the Maxim TCPCI core's `max_tcpci_chip` object. It plugs into the TCPCI vendor hook path for contaminant checks.

## Risks and Test Signals

Risks include invasive temporary changes to `TCPC_ROLE_CTRL`, analog threshold sensitivity, cleanup on intermediate regmap failures, sleep delays inside event handling, and the misspelled `contamiant_state` enum being part of local API. Test signals include open-CC contaminant detection, sink inference through comparators, dry-to-normal transition after removal, disconnect-while-debounce path, regmap failure cleanup restoring role control, and ensuring `cc_handled` is correct for TCPM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/maxim_contaminant.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/Makefile

## Purpose

`tcpm/qcom/Makefile` builds the Qualcomm PMIC TCPM adapter as one composite module.

## Important APIs, Types, and Functions

`obj-$(CONFIG_TYPEC_QCOM_PMIC) += qcom_pmic_tcpm.o` selects the module. `qcom_pmic_tcpm-y` links `qcom_pmic_typec.o`, `qcom_pmic_typec_port.o`, `qcom_pmic_typec_pdphy.o`, and `qcom_pmic_typec_pdphy_stub.o`.

## Control Flow

There is no runtime control flow. Kbuild uses the composite object list to link the platform driver and both real/stub PD PHY providers into the same module.

## State and Persistence Behavior

The file controls build artifacts only. It has no runtime state.

## Dependencies and Integration Points

It integrates the Qualcomm PMIC platform driver, Type-C port block, PD PHY block, and no-PD-PHY stub under the `TYPEC_QCOM_PMIC` symbol.

## Risks and Test Signals

Risks include missing object updates when the driver split changes and ensuring the stub is always linked for PMI632-like devices without a PD PHY. Test signals are module link checks for `CONFIG_TYPEC_QCOM_PMIC=m/y` and compatible probing for both PM8150B and PMI632 resource sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.c

## Purpose

`qcom_pmic_typec.c` is the top-level Qualcomm PMIC Type-C/TCPM platform driver. It aggregates the PMIC Type-C port block and, when present, the PD PHY block into one `tcpc_dev` registered with TCPM.

## Important APIs, Types, and Functions

`struct pmic_typec_resources` maps compatible data to `pmic_typec_port_resources` and optional `pmic_typec_pdphy_resources`. `qcom_pmic_typec_probe()` creates `struct pmic_typec`, obtains the parent regmap and `reg` base offsets, calls `qcom_pmic_typec_port_probe()`, calls either `qcom_pmic_typec_pdphy_probe()` or `qcom_pmic_typec_pdphy_stub_probe()`, gets the connector fwnode, allocates a DRM DP HPD bridge, registers the TCPM port, starts port and PD PHY blocks, and adds the bridge. `qcom_pmic_typec_remove()` stops PD PHY and port, unregisters TCPM, and releases the fwnode.

## Control Flow

Probe is resource-data driven: PM8150B gets both port and PD PHY resources using `reg[0]` and `reg[1]`, while PMI632 gets only the port and the stub PD callbacks. After both sub-blocks install their `tcpc_dev` callbacks, the top-level driver registers TCPM and starts hardware in port-before-PD-PHY order. Error paths unwind PD PHY start, port start, TCPM registration, and fwnode reference.

## State and Persistence Behavior

`struct pmic_typec` holds all runtime state and callback pointers, with sub-block state owned by the port and PD PHY probe helpers. No persistent storage exists; hardware state is configured on start and reset by sub-blocks.

## Dependencies and Integration Points

It depends on platform device matching, OF compatible data, parent regmap, TCPM, Type-C mux/connector fwnodes, regulators used by sub-blocks, and DRM AUX HPD bridge. It integrates Qualcomm PMIC Type-C hardware with the generic TCPM state machine.

## Risks and Test Signals

Risks include strict `reg` index expectations, missing connector child, start-order assumptions, optional PD PHY stub semantics for no-PD devices, and HPD bridge failures after hardware start. Test signals include PM8150B and PMI632 probes, regmap absence, missing connector, TCPM registration failure, port/PD PHY start failure unwind, remove ordering, and HPD bridge registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.h

## Purpose

`qcom_pmic_typec.h` defines the shared top-level state object used by the Qualcomm PMIC Type-C port and PD PHY subdrivers.

## Important APIs, Types, and Functions

`struct pmic_typec` stores the device, TCPM port, embedded `struct tcpc_dev`, pointers to PD PHY and port sub-block state, and start/stop callbacks for each block. `tcpc_to_tcpm()` converts a `tcpc_dev` callback receiver back to the owning `pmic_typec`.

## Control Flow

The header has no executable flow. It defines how subdrivers install TCPM callbacks and lifecycle functions during probe.

## State and Persistence Behavior

The structure is runtime-only state allocated by the top-level platform driver and used until remove. Callback pointers are installed by port and PD PHY probe helpers.

## Dependencies and Integration Points

It assumes users include the TCPM declarations that define `struct tcpm_port` and `struct tcpc_dev`. It is the central integration contract between `qcom_pmic_typec.c`, `qcom_pmic_typec_port.c`, `qcom_pmic_typec_pdphy.c`, and the PD PHY stub.

## Risks and Test Signals

Risks include callback pointer ordering, incomplete callback installation when a sub-block probe fails, and tight container-of coupling. Test signals are compile coverage and probe paths for both real and stub PD PHY configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.c

## Purpose

`qcom_pmic_typec_pdphy.c` implements the Qualcomm PMIC USB PD PHY half of the TCPM adapter. It handles PD message TX/RX registers, hard reset signaling, PD role header configuration, IRQ mapping, regulator enablement, and PHY reset.

## Important APIs, Types, and Functions

`struct pmic_typec_pdphy` stores device, TCPM port, regmap/base, IRQ data, reset/receive work, `vdd-pdphy` regulator, and a spinlock for register atomicity. TCPM callbacks installed here are `qcom_pmic_typec_pdphy_set_pd_rx()`, `qcom_pmic_typec_pdphy_set_roles()`, and `qcom_pmic_typec_pdphy_pd_transmit()`. Internal helpers include reset on/off, TX control clear, signal/payload transmit, receive buffer handling, ISR dispatch, enable/disable/reset, start/stop, and `qcom_pmic_typec_pdphy_probe()`.

## Control Flow

Probe validates resource IRQ count, allocates IRQ data, gets `vdd-pdphy`, initializes state and work, requests named IRQs with `IRQF_NO_AUTOEN`, installs TCPM callbacks, and assigns start/stop functions. Start enables the regulator, stores the TCPM port, resets/enables the PHY, then enables all IRQs. Transmit either frames a payload into header/data/size registers and starts SEND_MSG, or clears TX control and starts a signal/hard reset command with retry count based on negotiated revision. IRQs translate message TX success/fail/discard to `tcpm_pd_transmit_complete()`, message RX to buffer read plus `tcpm_pd_receive()`, and signal RX to scheduled hard reset work.

## State and Persistence Behavior

PD PHY state is runtime-only. The spinlock protects multi-register sequences and RX ownership handoff. The regulator and hardware enable bit define whether the PHY is active. Stop disables IRQs, resets filtering/TX, and disables the regulator.

## Dependencies and Integration Points

It depends on platform named IRQs, regmap, regulator core, TCPM PD callbacks, USB PD helpers, workqueues, and `qcom_pmic_typec` shared state. It integrates as the PD message transport provider for Qualcomm PMIC TCPM ports.

## Risks and Test Signals

Risks include RX buffer ownership races, size validation around hardware's off-by-one length convention, ignored `receive_work` field, hard reset scheduling from IRQ work, transmit busy when RX pending, and all PMIC IRQ names matching DT resources. Test signals include PD RX enable/disable, role header writes, SOP payload TX, hard/cable reset TX, TX success/fail/discard IRQs, RX message parsing and acknowledge, hard reset receive, regulator failure unwind, and stop disabling IRQs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.h

## Purpose

`qcom_pmic_typec_pdphy.h` declares the Qualcomm PMIC PD PHY resource description and probe APIs.

## Important APIs, Types, and Functions

`PMIC_PDPHY_MAX_IRQS` bounds IRQ resources. `struct pmic_typec_pdphy_irq_params` maps a virtual IRQ ID to a named platform IRQ. `struct pmic_typec_pdphy_resources` stores the number of IRQs and the fixed-size parameter array. It declares `pm8150b_pdphy_res`, `qcom_pmic_typec_pdphy_probe()`, and `qcom_pmic_typec_pdphy_stub_probe()`.

## Control Flow

There is no executable control flow. The header supplies resource tables to the top-level compatible match and lets the top-level driver select real or stub PD PHY probing.

## State and Persistence Behavior

The resource structures are static configuration data. Runtime PD PHY state is opaque as `struct pmic_typec_pdphy`.

## Dependencies and Integration Points

It depends on platform devices and regmap and is shared by the top-level PMIC driver, real PD PHY implementation, and stub implementation.

## Risks and Test Signals

Risks include IRQ count/resource-name drift between DT and resource tables and the opaque type hiding lifetime constraints from callers. Test signals are compile coverage, PM8150B IRQ lookup, and PMI632 stub probe selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy_stub.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy_stub.c

## Purpose

`qcom_pmic_typec_pdphy_stub.c` provides no-op PD PHY callbacks for Qualcomm PMIC Type-C controllers that have a Type-C port block but no PD PHY hardware, such as the PMI632 resource path.

## Important APIs, Types, and Functions

`qcom_pmic_typec_pdphy_stub_probe()` installs stub `set_pd_rx`, `set_roles`, and `pd_transmit` callbacks plus no-op start/stop functions. `qcom_pmic_typec_pdphy_stub_pd_transmit()` logs the transmit type and immediately calls `tcpm_pd_transmit_complete(..., TCPC_TX_SUCCESS)`.

## Control Flow

Probe attaches stub callbacks to the shared `tcpc_dev`. TCPM can then call PD operations without NULL callbacks even though no hardware messages are sent. Start returns success and stop does nothing.

## State and Persistence Behavior

The stub stores no additional state and changes no hardware. Its only externally visible behavior is debug logging and immediate transmit completion.

## Dependencies and Integration Points

It depends on TCPM, USB PD types, and the shared Qualcomm PMIC container. It integrates no-PD-PHY PMIC variants into the same top-level driver as full PD-capable PMICs.

## Risks and Test Signals

Risks include reporting PD transmit success without actual PD transport if TCPM attempts PD negotiation on stub-only hardware, and relying on higher-level capabilities/configuration to avoid unsupported PD flows. Test signals include PMI632 probe, TCPM startup without PD PHY resources, stub callbacks invoked without crashes, and no regulator/IRQ side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_pdphy_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.c

## Purpose

`qcom_pmic_typec_port.c` implements the Qualcomm PMIC Type-C port-controller half of the TCPM adapter. It maps PMIC Type-C status/config registers to TCPM callbacks for CC, VBUS, VCONN, polarity, and DRP toggling.

## Important APIs, Types, and Functions

`struct pmic_typec_port` stores device, TCPM port, regmap/base, IRQ data, VBUS regulator and state, VBUS mutex, cached CC, debounce state and delayed work, and a spinlock for register atomicity. Installed TCPM callbacks are `qcom_pmic_typec_port_get_vbus()`, `set_vbus()`, `set_cc()`, `get_cc()`, `set_polarity()`, `set_vconn()`, and `start_toggling()`. Lifecycle functions are `qcom_pmic_typec_port_probe()`, `qcom_pmic_typec_port_start()`, and `qcom_pmic_typec_port_stop()`.

## Control Flow

Probe allocates state, validates IRQ resources, gets `vdd-vbus`, initializes locks/work, requests named IRQs with `IRQF_NO_AUTOEN`, installs TCPM callbacks, and assigns start/stop functions. Start enables PMIC interrupt masks, starts in Try.SNK mode, configures software VCONN control and exit thresholds, stores the TCPM port, and enables IRQs. IRQs read misc status and notify TCPM of VBUS or CC changes unless a software CC debounce window is active. VBUS set toggles the regulator and polls for vSafe5V/vSafe0V. CC get decodes source or sink status registers based on attach, orientation, and mode bits. CC set programs source current when sourcing and debounces before TCPM re-reads.

## State and Persistence Behavior

Runtime state tracks regulator-backed VBUS enablement, cached requested CC, and a short software debounce flag. PMIC hardware maintains attach/orientation/status registers. The VBUS mutex serializes regulator and state changes, while the spinlock protects register sequences and debounce flags.

## Dependencies and Integration Points

It depends on regmap, platform named IRQs, regulator core, delayed work, TCPM, Type-C mux-related orientation integration, and the shared Qualcomm PMIC container. Polarity is intentionally left to the Qualcomm QMP PHY.

## Risks and Test Signals

Risks include returning success even when vSafe polling warns on timeout, `set_cc()` not writing sink/source mode command directly except through toggling paths, 2 ms debounce hiding genuine quick CC changes, DT IRQ-name dependence, and VBUS notifications while under regulator transitions. Test signals include get/set VBUS with vSafe polling, CC decode for source/sink/audio/debug cases, Try.SNK/DRP toggling, VCONN orientation inversion, IRQ-driven TCPM notifications, debounce behavior, and start/stop IRQ enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.h

## Purpose

`qcom_pmic_typec_port.h` declares the Qualcomm PMIC Type-C port resource description and probe API.

## Important APIs, Types, and Functions

`PMIC_TYPEC_MAX_IRQS` bounds port IRQ resources. `struct pmic_typec_port_irq_params` maps virtual IRQ IDs to platform IRQ names. `struct pmic_typec_port_resources` stores the IRQ count and parameter table. It declares the PM8150B resource table and `qcom_pmic_typec_port_probe()`.

## Control Flow

There is no executable flow. The header defines static configuration consumed by the top-level compatible match and the port implementation.

## State and Persistence Behavior

Resource tables are static configuration. Runtime state is opaque as `struct pmic_typec_port`.

## Dependencies and Integration Points

It depends on platform devices and TCPM declarations and is shared by the top-level Qualcomm PMIC driver and port implementation.

## Risks and Test Signals

Risks include IRQ name/count drift from DT bindings and hidden lifetime assumptions for the opaque port state. Test signals are compile coverage and successful platform IRQ lookup for every PM8150B port IRQ resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/qcom/qcom_pmic_typec_port.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci.c

## Purpose

`tcpci.c` is the generic Type-C Port Controller Interface bridge for TCPM. It adapts TCPCI-compliant register maps to the `tcpc_dev` callback API and also provides a simple I2C TCPCI driver.

## Important APIs, Types, and Functions

`struct tcpci` stores device, TCPM port, regmap, alert mask, VBUS-control flag, embedded `tcpc_dev`, vendor `tcpci_data`, and optional orientation GPIO. Exported APIs are `tcpci_get_tcpm_port()`, `tcpci_register_port()`, `tcpci_unregister_port()`, and `tcpci_irq()`. TCPM callback implementations include CC set/get/apply, DRP toggling, polarity/orientation, VCONN, VBUS get/set, auto-discharge thresholds, FRS, BIST, role header, PD RX, PD transmit, cable-comm capability, and contaminant/vendor hooks.

## Control Flow

`tcpci_register_port()` allocates and fills the `tcpc_dev`, conditionally installs optional callbacks from `tcpci_data`, parses the connector fwnode, and registers with TCPM. The simple I2C probe enables optional `vdd`, creates a regmap, disables interrupts, detects orientation support or fallback GPIO, registers the TCPM port, requests the IRQ, then writes `TCPC_ALERT_MASK`. Runtime IRQ handling reads TCPC alerts, clears non-RX bits first, notifies TCPM of CC/VBUS/reset/extended-status changes, reads RX byte/header/data before clearing RX status, forwards PD messages and hard resets, completes TX status, and loops until no masked alerts remain.

## State and Persistence Behavior

The driver caches the computed alert mask, whether the controller handles VBUS, optional orientation GPIO, and vendor data. TCPCI hardware registers hold CC, VBUS, PD TX/RX, alert, and power state. Suspend either enables IRQ wake or masks alerts; resume disables wake or restores the alert mask.

## Dependencies and Integration Points

It depends on regmap, I2C, GPIO, regulators, TCPM, TCPCI public register definitions, USB PD helpers, Type-C class enums, and vendor `tcpci_data` hooks used by RT1711H, MT6360/MT6370, Maxim, and others. It is the main reusable TCPCI adapter layer under TCPM.

## Risks and Test Signals

Risks include endianness/raw regmap handling, alert loop livelock if hardware keeps reasserting, RX count validation, auto-discharge threshold math under unusual PPS voltages, orientation fallback detection, vendor hook return conventions for VBUS, and reset detection via mask value `0xff`. Test signals include registration/unregistration, connector fwnode absence, CC role programming, DRP toggling, polarity under DRP result, VBUS/VCONN control, PD TX/RX and alert clearing, extended vSafe0V, auto-discharge and FRS, vendor contaminant hooks, suspend/resume alert masking, and IRQ storm behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_maxim.h -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_maxim.h

## Purpose

`tcpci_maxim.h` defines Maxim TCPCI vendor register constants, contaminant-detection state, shared chip state, raw regmap helpers, and the contaminant helper API.

## Important APIs, Types, and Functions

Register and bit definitions cover vendor CC status, fast low-power ADC status/control, CC control, dry detection, low-power mode, OVP controls, source current settings, and water-detection timing. `enum contamiant_state` tracks contaminant detection state. `struct max_tcpci_chip` combines generic `tcpci_data`, the registered `tcpci` handle, device/I2C/TCPM handles, contaminant state, VCONN swap veto, and optional VBUS regulator. Inline helpers read/write 8-bit and 16-bit registers via raw regmap operations. `max_contaminant_is_contaminant()` is declared for the Maxim contaminant module.

## Control Flow

The header has no standalone runtime flow. Inline helpers provide direct raw register access used by Maxim core and contaminant code.

## State and Persistence Behavior

The shared chip structure stores runtime Maxim state, including contaminant tracking and VCONN swap policy. Vendor register state remains in hardware.

## Dependencies and Integration Points

It depends on `struct tcpci_data`, `struct tcpci`, regmap, regulators, TCPM, and TCPCI definitions included by users. It is the local contract between `tcpci_maxim_core.c` and `maxim_contaminant.c`.

## Risks and Test Signals

Risks include the misspelled enum name becoming part of local API, raw endianness assumptions for 16-bit register access, and tight coupling between contaminant helper and Maxim core state. Test signals include compile coverage of Maxim composite module, raw register read/write helpers, contaminant state transitions, VCONN swap veto users, and VBUS regulator handling in the Maxim core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_maxim.h -->
