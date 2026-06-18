# Group Research: group_622_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__a18db0390f35

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidvar.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidvar.h

Internal HID driver state header. It defines boot-interface/protocol constants, fallback keyboard/mouse packet and report descriptor sizes, HID control request values, mctl return codes, stream-open flags, timeout/retry constants, and debug masks.

The central structures are `hid_power_t`, which tracks PM strategy, wakeup, busy accounting, supported/current power states, and pending power-up message state, and `hid_state_t`, which owns per-instance USBA registration, descriptors, default/interrupt pipe handles, parser handle, packet sizing, polled console state, STREAMS queues, logging, and ugen support.

Concurrency is documented with Warlock `_NOTE` annotations: `hid_mutex` protects `hid_state_t` and `hid_power_t`, while several handles/descriptors are declared stable/readable without the lock. The file also records the driver's online/suspended/disconnected/powered-down/power-change state model.

Notable detail: there is a `_NOTE(DATA_READABLE_WITHOUT_LOCK(hid_state_t::hid_ep_intr_descr))` reference, while the actual struct field is `hid_ep_intr_xdescr`; this may be a stale annotation name.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hid_parser_driver.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hid_parser_driver.h

Private HID parser interface for the HID driver. It exposes parser lifecycle and driver-only query functions, not general HID STREAMS module APIs.

Exports `hidparser_parse_report_descriptor()`, `hidparser_free_report_descriptor_handle()`, `hidparser_get_top_level_collection_usage()`, and `hidparser_lookup_usage_collection()`. These let the HID driver parse a raw HID report descriptor, free the opaque handle, determine top-level collection usage for module selection, and test for a usage collection.

The API depends on `usb_hid_descr_t` and `hidparser_handle_t` defined elsewhere. Return comments use parser success/failure status names and make clear that parse failure is expected to be reported through `HID_PARSER_ERROR`-style values.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hid_parser_driver.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser.h

Public HID parser contract shared by the HID driver and HID STREAMS modules. It defines opaque `hidparser_handle_t`, usage/report description structures, report-id list structures, packet info, parser query functions, HID item tags, usage pages/usages, main-item descriptor bits, and parser status values.

Important query APIs include country code lookup, report packet size lookup, usage attribute lookup, main item data descriptor lookup, ordered usage list extraction, report-id list extraction, and max-packet-size discovery.

The ABI is intentionally descriptor-centric: consumers ask for report IDs, usage metadata, logical ranges, report size/count, and main item attributes rather than walking the raw parser tree. Limits include `USAGE_MAX` of 100 usages per report and `REPORT_ID_MAX` of 10 report IDs per type.

The header codifies common HID pages/usages used by keyboard, mouse, LED, button, generic desktop, and consumer-control modules.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser_impl.h

Implementation-private HID parser model. It defines linked-list entities for parser attributes and main items, the internal `hidparser_handle` containing the parse tree and HID descriptor pointer, scanner token state, attribute stacks for PUSH/POP handling, and additional parser tag/error constants.

The parser tree is built from `entity_item_t` nodes representing collection/input/output/feature/end-collection items. Each node can carry inherited attributes, child/data pointers, sibling links, and collection ancestry.

The scanner/token bridge `hidparser_tok_t` tracks token bytes, raw descriptor buffer, current descriptor index/token, current global/local item lists, and the global-item stack.

Constants include unexposed local/global items such as set delimiter, usage page, push/pop, end collection, raw item tags, error masks, extended-item marker, and token text buffer length.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hidparser/hidparser_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/mass_storage/usb_bulkonly.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/mass_storage/usb_bulkonly.h

USB Mass Storage Bulk-Only Transport definitions. It provides class request constants for reset and GET_MAX_LUN, CBW signature/direction/CDB length constants, byte extraction macros for CBW fields, and CSW layout/status constants.

The only structure is `usb_bulk_csw_t`, a byte-wise representation of the 13-byte Command Status Wrapper, including signature, tag, residue, and status fields.

It also defines `IOMEGA_CMD_CARTRIDGE_PROTECT` as a vendor-specific command needed for certain bulk-only devices.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/mass_storage/usb_bulkonly.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/mass_storage/usb_cbi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/mass_storage/usb_cbi.h

USB Mass Storage CBI transport constants. It defines class request type composition, command block reset values, 12-byte command block length, and command status bit values.

The status constants cover pass, failed, phase error, persistent failure, and a status mask. No structures or functions are declared.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/mass_storage/usb_cbi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/printer/usb_printer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/printer/usb_printer.h

Generic USB printer class specification constants. It defines the printer descriptor type, class-specific requests for IEEE-1284 device ID, port status, soft reset, and clear-feature handling.

It also maps USB printer port status bits to driver/application error-state flags for no-error, select, and paper-empty conditions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/printer/usb_printer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/printer/usbprn.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/printer/usbprn.h

Internal USB printer driver state header. It defines transfer timeouts, per-pipe state flags, max transfer size, per-pipe state `usbprn_ps_t`, PM state `usbprn_power_t`, and per-instance `usbprn_state_t`.

`usbprn_state_t` holds USBA registration, descriptors, device ID buffer, default/bulk pipes, serialization objects, pending bulk message/buf state, port status, power state, ECPP/printer timeout settings, logging, and ugen support.

Macros cover device-access checks, pipe busy checks, debug masks, device ID maximum, and minor-number extraction for ugen-style minors.

Notable detail: `USBPRN_PIPES_BUSY()` references `usbprn_default.ps_flags`, but the state structure has `usbprn_def_ph` rather than a `usbprn_default` pipe-state member. This looks like stale macro code unless supplied by another compatibility definition.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/printer/usbprn.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/ugend.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/ugend.h

Internal USB generic driver support skeleton header. It defines a small `ugen_skel_state_t` containing device info, instance, and `usb_ugen_hdl_t`.

Constants cover soft-state instance count and minor-number packing: 9 bits reserved for ugen minor data, with remaining bits mapped back to instance via `UGEN_MINOR_TO_INSTANCE()`.

The state is marked readable without lock by Warlock annotations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/ugend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/usb_ugen.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/usb_ugen.h

User-facing UGEN status and isochronous request ABI definitions. It enumerates endpoint last-command status values, including USB link errors, stalls, underruns/overruns, timeout, no bandwidth, disconnect/suspend, invalid/interrupted/no-resource requests, and isochronous polling failures.

It defines endpoint control flag `USB_EP_INTR_ONE_XFER`, device status values exposed through device-status minors, and isochronous packet/request header structures used between applications and ugen.

The isochronous ABI uses `ugen_isoc_pkt_descr_t` for per-packet requested length, actual length, and status, plus `ugen_isoc_req_head_t` with a flexible one-entry descriptor array pattern.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/usb_ugen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbcdc/usb_cdc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbcdc/usb_cdc.h

USB Communications Device Class definitions. It declares descriptor type/subtype constants and C structures for CDC header, call management, ACM, union, ECM, line coding, and notification descriptors.

The header defines capabilities for call management and ACM, class-specific request codes for encapsulated commands, line coding, control line state, and break, plus stop-bit/parity/control-line constants.

It also defines notification constants for network connection, response available, serial state, and speed change, along with serial-state bits for DCD/DSR/break/ring/framing/parity/overrun.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbcdc/usb_cdc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbecm/usbecm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbecm/usbecm.h

Internal USB CDC ECM Ethernet driver state header. It defines PM state, MAC statistics, device-specific operation callbacks, and the main `usbecm_state` structure.

`usbecm_state` owns USBA handles, MAC handle, serialization object, control/data interface numbers, endpoint data, ECM descriptor compatibility data, MAC address and packet filter state, pipe handles/states, receive queue, TX count, statistics, initialization flags, MAC state, private device data, and device-specific ops.

Constants cover pipe states, MAC states, bulk timeouts, class request type composition, init flags, ECM statistics selectors/capability bits, ECM class-specific request codes, packet filter bits, debug masks, and byte-order helpers.

The file redefines simple `isdigit` and `toupper` macros locally, so consumers must be aware of macro namespace effects.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbecm/usbecm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbinput/usbwcm/usbwcm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbinput/usbwcm/usbwcm.h

USB Wacom tablet event ABI and kernel driver definitions. The file includes Sun, FreeBSD, and NetBSD-derived licensing/copyright material.

The user-visible portion defines event ioctl commands, `event_dev_id`, `event_abs_axis`, and `event_input`, plus event type/code spaces for sync, buttons, relative axes, absolute axes, and miscellaneous serial data.

The `_KERNEL` portion defines Wacom vendor/product IDs, tool IDs, pad serial constants, ioctl command numbers, protocol/model structs, protocol table, softc state, USBWCM STREAMS state, transparent ioctl copyin state, supported Wacom device table with dimensions/pressure ranges, packet extraction macros, bitmap helpers, bitmap sizes, and debug mask.

It embeds a static `uwacom_devs[]` device table covering Graphire, Bamboo, Cintiq, Volito, PenPartner, Intuos3, and Intuos4 variants.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbinput/usbwcm/usbwcm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbkbm/usbkbm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbkbm/usbkbm.h

USB keyboard module state and translation constants. It defines LED masks, modifier masks/keycodes, rollover constant, boot keyboard report size, open/qwait flags, polled key state, max packet size, and report format metadata.

`usbkbm_state_t` owns kbtrans state, STREAMS queues, report format, HID parser handle, layout, LED ioctl sequencing, previous/pending USB packets, HID polled callback, pending ioctl/link messages, bufcall ID, console polled I/O state, virtual keyboard type, vid/pid, polled scancode ring, and boot/report protocol selection.

The file also defines Sun Japanese keyboard layout/vendor/product constants, USB keymap sizing, saved global keyboard state, debug masks, and index conversion constants for PC/USB key tables.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbkbm/usbkbm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbms/usbms.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbms/usbms.h

USB mouse STREAMS module state header. It defines mouse sample/buffer structures, parsed HID input descriptor metadata, full per-instance state, button mapping constants, jitter/speed filtering settings, transparent ioctl state, and debug masks.

`usbms_state_t` includes read/write queues, open/qwait flags, pending ioctl message, `ms_softc`, previous button state, HID parser handle, jitter threshold/timeouts, speed limit/law counters, button/wheel counts, report ID and logical maxima, screen resolution, absolute-report flag, parsed input descriptor, and mouse sample buffer.

Macros include absolute value, byte clipping to signed 7-bit mouse deltas, default/max button counts, input parser states, default screen resolution, USB-to-Type-5 button encodings, and default jitter/speed/buffer tunables.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbms/usbms.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_reg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_reg.h

FTDI USB serial protocol/register constants, derived from NetBSD/FreeBSD lineage and FTDI protocol documentation. It defines vendor request numbers, port identifiers, FTDI chip types, reset commands, baud divisor values for SIO and 8U232AM-style chips, data format bitfields, modem-control commands, flow-control values, and status decoding.

The comments document each vendor request format in detail: reset, set baud rate, set data, modem control, flow control, event char, error char, modem status, and endpoint data framing.

Status macros decode FTDI IN endpoint leading modem/line status bytes and OUT endpoint tag construction. Line-status bits mirror 16550-style overrun, parity, framing, break, THRE, and TEMT semantics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_reg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_var.h

Internal FTDI device-specific serial driver state. It includes USB serial DSDI support and defines PM state, soft register cache, and per-device `uftdi_state_t`.

`uftdi_state_t` tracks DDI/USBA handles, device and port flags/states, hardware port number, callbacks into the generic serial driver, default/bulk pipe handles and states, buffer sizes, PM state, RX/TX mblk ownership, TX completion CV, cached baud/data/flow registers, modem control, modem status, and line status.

Constants define port states, TX-stopped flag, pipe states, bulk timeouts, max transfer size, cleanup level, and debug masks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsacm/usbsacm.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsacm/usbsacm.h

USB CDC ACM serial driver private state. It defines PM state, per-port `usbsacm_port`, per-device `usbsacm_state`, pipe/port state enums, timeouts, class request type constants, and debug masks.

Each ACM port owns bulk-in, bulk-out, and interrupt pipes, endpoint descriptor, control/data interface numbers, data-port number, generic serial callbacks, RX/TX messages, TX completion CV, modem controls in/out, capability bits, line coding, port state, and bulk-in transfer size.

The device state owns DDI/USBA handles, USB events, default pipe, logging, device state, transfer size, compatibility flag, port array/count, and PM state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsacm/usbsacm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser.h

Generic USB-to-serial driver public entry-point header for device-specific serial drivers. It includes `usbser_dsdi.h` and declares soft-state sizing, attach/detach/getinfo/power entry points, and STREAMS open/close/wput/wsrv/rsrv functions.

It also defines default STREAMS packet size and queue watermarks: unlimited max packet size, 128 KiB high water, and 4 KiB low water.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_dsdi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_dsdi.h

USB serial Device-Specific Driver Interface. This is the core contract between the generic serial driver and concrete USB serial chip drivers.

It defines opaque DSD handles, callback registration (`ds_cb_t` for TX/RX/status), attach information, the `ds_ops_t` operation vector, operation-vector versioning, port parameter types and arrays, direction flags, on/off values, and input error codes.

`ds_ops_t` covers attach/detach, callback registration, port open/close, USB power, suspend/resume, disconnect/reconnect, UART parameter setting, modem control get/set, break, loopback, transmit, receive, stop/start, FIFO flush/drain, and V1 polled I/O pipe accessors.

The data ownership rule for `ds_tx()` is explicit: a DSD that accepts the mblk and returns success owns it afterward.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_dsdi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_49fw.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_49fw.h

Placeholder header for Keyspan USA49WLC firmware support. It defines `KEYSPAN_NO_FIRMWARE_SOURCE` and documents that firmware is not included here.

The comments explain that users with firmware source can replace this header with `keyspan_usa49w_fw.h` and build the `usbs49_fw` module under the platform-specific uts directory.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_49fw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_pipe.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_pipe.h

Keyspan USB pipe management header. It defines `keyspan_pipe_t`, which wraps a mutex, parent state pointer, pipe handle, endpoint descriptor, pipe policy, state, and log handle.

Pipe states are not-initialized, closed, and open. Function prototypes cover device-specific pipe initialization/finalization, open/close/reopen flows for device and port pipes, shared close helpers, data receive/send paths, status receive, and polling startup.

It depends on forward-declared `keyspan_state_t` and `keyspan_port_t` from `keyspan_var.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_pipe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_var.h

Keyspan USB serial implementation state. It defines supported product IDs, max port count, pre-attach state, firmware record format, PM state, device endpoint specification, control/status message unions for USA19HS and USA49 variants, device state, and per-port state.

`keyspan_state` owns device/port data, a pipe-open semaphore, USBA event/registration handles, default/status/control pipes, logging, USB state, PM state, and USA49WG shared bulk-in pipe tracking. `keyspan_port` owns callbacks, RX/TX queues, TX CV, current control/status messages, baud/LCR/status flags, data pipes, and transfer sizing.

Constants cover port status flags, port states, TX-stopped flag, transfer timeouts and max lengths per model, firmware flag, vendor control requests, debug masks, and common helper prototypes.

Concurrency notes define lock ordering from device state to port to pipe.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa49msg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa49msg.h

Keyspan USA49W async firmware message format definitions. It defines port control/status messages plus global control/status/debug messages and RX data status bit meanings.

`keyspan_usa49_port_ctrl_msg` is a detailed host-to-device command structure covering baud clocking, LCR, flow control, RTS/DTR, forwarding behavior, ACK thresholds, loopback, TX/RX on/off/flush/break/forward, status return, data-toggle reset, port enable, and port disable.

`keyspan_usa49_port_status_msg` reports CTS/DCD/DSR/RI, TX-off and XOFF state, RX enable state, control response, TX ACK, and RS-232 validity.

The comments define raw USB IN/OUT data message framing, including status-byte interleaving for parity/framing/break reporting and overrun interpretation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa49msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa90msg.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa90msg.h

Keyspan USA19HS/USA90-style async firmware message format definitions. It defines port control and status structures plus LCR, flow-control, RX/TX mode, RX error, port-state, and modem-status bits.

`keyspan_usa19hs_port_ctrl_msg` controls baud, LCR, RX/TX modes, TX/RX flow control, immediate XON/XOFF/char sends, RTS/DTR, forwarding thresholds/timeouts, ACK behavior, port enable, flush, break, loopback, RX forward, cancel RX XOFF, and status return.

`keyspan_usa19hs_port_status_msg` reports MSR, CTS/DCD/DSR/RI, XOFF state, break, accumulated overrun/parity/frame errors, port state, message/char acknowledgements, and control response.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/usa90msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_rseq.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_rseq.h

Reusable reversible-sequence helper interface for multistep driver setup/teardown. It models paired do/undo steps so attach-like code can unwind completed steps in reverse order after failure.

Defines function and callback signatures, callback return values (`RSEQ_OK`, `RSEQ_UNDO`, `RSEQ_ABORT`), step and sequence structures, `rseq_do()`/`rseq_undo()`, debug variants, failure-injection scenarios, and convenience macros for declaring step pairs.

The design is explicitly aimed at replacing goto/bitfield cleanup patterns in attach/detach implementations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_rseq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_var.h

Internal generic USB serial driver state. It defines per-port worker-thread metadata, global device state, per-port tty state, port state machine, activities, flags, minor-number layout, timeouts, debug masks, and macros dispatching to DSD operations.

`usbser_state` tracks device list linkage, devinfo, mutex, soft-state anchor, instance, DSD ops/handle, port count/array, USB state, log handle, and taskq. `usbser_port` tracks port mutex, parent state, log handle, DSD copy, port number/state/activity/flags, state/activity/carrier CVs, write-queue byte count, read/write worker threads, `tty_common`, flow-control char, and delay/break timeout.

The port-state diagram documents tty vs dial-out open behavior, carrier-detect blocking, dial-out overtaking, suspended/disconnected handling, and close/open race avoidance.

Minor numbers reserve low bits for port, high bits for instance, and the top bit for dial-out (`OUTLINE`).
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsprl/pl2303_var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsprl/pl2303_var.h

Internal Prolific PL2303 USB serial state. It defines PM state, chip type enum, per-device `pl2303_state_t`, port/pipe states, tunables, debug masks, and `NELEM`.

`pl2303_state_t` tracks lock, devinfo, device flags, port state/flags, generic serial callbacks, USBA event/registration/default/bulk pipe handles and states, log handle, USB device state, transfer size, PM state, RX/TX mblks, TX completion CV, modem controls, and detected chip type.

Chip types distinguish PL-2303H, PL-2303X/HX chip A, PL-2303HX chip D, and unknown.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsprl/pl2303_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsprl/pl2303_vendor.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsprl/pl2303_vendor.h

Prolific PL2303 vendor/class request constants. It defines revision numbers for H, X, HX chip D, and revision 1 devices.

The header provides request type/code/length constants for set/get line coding, set control, break, vendor write/read, XON/XOFF symbol setup, DCR0/DCR1/DCR2 get/set/init values for H/X variants, and downstream/upstream data pipe reset commands.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsprl/pl2303_vendor.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbskel/usbskel.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbskel/usbskel.h

USB skeleton driver state header. It defines PM state and basic per-device skeleton state for a sample/teaching USB client driver.

`usbskel_power_t` tracks backpointer, supported power states, PM busy count, capabilities, raise-power flag, and current power. `usbskel_state_t` tracks devinfo, registration data, interrupt endpoint/pipe, device instance string, USB and driver state, mutex/CV serialization state, lock initialization, and PM pointer.

Constants cover open flag, max request size, device descriptor size, drain timeout, serialization modes, and logging destination flags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbskel/usbskel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc.h

USB Video Class descriptor and request definitions. It defines video class/subclass/protocol constants, class-specific descriptor types/subtypes, endpoint types, request codes, control selectors, terminal types, descriptor structures, probe/commit structure, format GUIDs, and stream payload flags.

The descriptor models cover video-control headers, units, terminals, streaming input/output headers, frames, still image frame patterns, color matching, MJPEG/uncompressed formats, and video streaming probe/commit controls.

The header uses raw byte arrays for many little-endian multi-byte UVC fields, leaving conversion to implementation helpers. It defines YUY2 and NV12 format GUID initializers and stream EOF/FID bit flags.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc_var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc_var.h

Internal USB video class driver state. It includes USBA private APIs, V4L2 types, and public UVC definitions, then layers PM, buffer management, stream-interface state, format grouping, V4L2 control mapping, and driver helper prototypes.

Important structures include `usbvc_buf_t` for raw camera buffers and mmap metadata, `usbvc_buf_grp_t` for free/done/filling lists, `usbvc_format_group_t` for format/frame/still/color plus V4L2 pixel metadata, `usbvc_stream_if_t` for streaming interface state and isochronous pipe/polling/buffer state, and `usbvc_state` for the whole device.

Macros cover copyin/copyout boilerplate, little-endian conversion, minimum descriptor lengths, high-speed packet size calculation, buffer status values, debug masks, buffer count limits, and UVC frame interval units.

Function prototypes expose isochronous pipe/polling, VC/VS controls, probe/commit negotiation, mmap buffer allocation/free, and V4L2 ioctl/color/GUID helpers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/video/usbvc/usbvc_var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci.h

Hardware-facing EHCI host controller header. It defines DMA alignment/attribute limits, EHCI capability and operational register layouts, register bitfields, root-hub port bits, extended capability/BIOS handoff bits, periodic frame list layout, queue heads, queue transfer descriptors, and isochronous transfer descriptors.

Core structures include `ehci_caps_t`, `ehci_regs_t`, `ehci_periodic_frame_list_t`, `ehci_qh_t`, `ehci_qtd_t`, and `ehci_itd_t`. The QH/QTD/iTD definitions include both hardware-visible fields and HCD-private software bookkeeping fields for ownership, active/reclaim lists, transfer wrappers, state, frame numbers, and offsets.

The file is central to EHCI transfer scheduling: it encodes async/periodic scheduler controls, root hub port control, QH endpoint/split controls, QTD status/PID/error fields, iTD high-speed isochronous controls, and siTD full/low-speed split isochronous bitfields.

It is not a standalone state header; it depends on broader EHCI state/pipe/wrapper types declared elsewhere.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_hub.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_hub.h

EHCI root hub state header. It defines `ehci_root_hub_t`, which stores the hub descriptor, companion controller count, per-port status/state arrays, control and interrupt pipe handles, current control/interrupt requests, saved client interrupt request, interrupt pending-status bitmap, and polling timer ID.

Port states cover uninitialized, powered off, disconnected, disabled, enabled, and suspended. Timing constants define root-hub polling interval, reset/suspend/resume waits, completion waits, and retry limits.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_hub.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_intr.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_intr.h

EHCI interrupt-handling prototypes. It declares handlers for USB errors, frame-list rollover, endpoint reclamation, active QTD traversal, QTD error checking, generic error handling, and per-transfer-type QTD completion handling for control, bulk, and interrupt transfers.

The prototypes show the interrupt layer operates over `ehci_state_t`, pipe-private state, transfer wrappers, QTDs, completion reasons, and opaque callback data.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_intr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_isoch.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_isoch.h

EHCI isochronous transfer interface header. It declares initialization/cleanup, per-pipe cleanup, isochronous resource allocation, request insertion, polling startup, active isochronous list traversal, and HCDI isochronous callback functions.

Constants define maximum siTD transfer size as 1023 bytes and maximum packets per isochronous transfer as 1024.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_isoch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_isoch_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_isoch_util.h

EHCI isochronous utility prototypes. It declares allocation of isochronous pools, ITW resources, iTD allocation/deallocation/list insertion/removal, iTD count calculation, periodic-frame-list insertion/removal, active-list helpers, done-list creation, isochronous IN resource management, CPU/IOMMU address conversion, error parsing, and iTD/siTD debug printing.

This header separates lower-level resource/list/address helpers from the higher-level isochronous API in `ehci_isoch.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_isoch_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_polled.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_polled.h

EHCI polled-mode state header for firmware/debugger console operation. It defines raw buffer size, input/output mode flags, in-use flags, keyboard packet limit, and `ehci_polled_t`.

`ehci_polled_t` stores controller state pointer, input pipe handle, dummy and interrupt QHs, raw scan-code buffer, flags, active interrupt QTD list, nested enter/exit reference count, saved USB device pointer, endpoint address, and a no-sync workaround flag.

The comments document nested polled entry/exit behavior through kmdb and firmware prompts so controller state is restored only after the final exit.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_polled.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_util.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_util.h

EHCI utility/init/deinit/bandwidth/miscellaneous function prototypes. It declares DMA attribute setup, pool allocation, DMA bind result decoding, register mapping, interrupt/mutex setup, controller initialization, HCDI ops allocation, cleanup, CPR suspend/resume, bandwidth allocation/deallocation, polling interval adjustment, state lookup, operational checks, soft reset, transfer attribute lookup, frame-number retrieval, SOF wait, scheduler toggling, debug printers, and kstat/stat helpers.

This header is the shared utility API used across EHCI attach/detach, scheduling, bandwidth management, and diagnostics.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_util.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_xfer.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_xfer.h

EHCI transfer-management prototypes. It declares QH allocation/insertion/removal/deallocation/address conversion, control/bulk/interrupt resource allocation and request insertion, periodic polling start/stop, QTD insertion/removal/deallocation/address conversion, transfer-wrapper TD allocation/timer/deallocation/free-DMA helpers, interrupt IN resource management, pipe cleanup, transfer completion checks, data-toggle restoration, outstanding-request handling, client periodic callback dispatch, generic HCDI callbacks, and clear-TT-buffer handling.

The API shows the transfer layer is organized around QHs, QTDs, transfer wrappers, pipe-private state, and USBA request types for control, bulk, interrupt, and periodic polling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_xfer.h -->