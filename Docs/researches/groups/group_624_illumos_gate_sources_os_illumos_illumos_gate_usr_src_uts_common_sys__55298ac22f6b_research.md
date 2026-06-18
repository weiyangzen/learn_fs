# Group Research: group_624_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_sys__55298ac22f6b

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/bos.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/bos.h

## Role

Defines illumos USB Binary Object Store (BOS) descriptor layouts and parsed capability records for USB 3.x hub/framework use.

## Key Interfaces

- Defines BOS device capability type constants: WUSB, USB 2.0 extension, SuperSpeed, container ID, platform, Power Delivery, SuperSpeedPlus, precision time, and related values.
- Defines packed-size constants for wire descriptors so parser code can validate descriptor lengths independent of compiler padding.
- Provides C layouts for BOS header, generic device capability descriptor, USB 2.0 extension, SuperSpeed USB, container ID, platform capability, SuperSpeedPlus capability, and precision-time capability.
- Provides bitfield extraction macros for USB 2.0 LPM, SuperSpeed speed support, SuperSpeedPlus attribute counts, lane/functionality fields, sublink-speed attributes, lane speed exponent/protocol/type, and link speed mantissa.
- Defines `usb_bos_t`, an internal parsed representation with length, type, and a union of known capability structures plus a 256-byte raw fallback.

## Design Notes

The comments explicitly state this is separated from primary USBAI headers because BOS handling is currently private to hub/framework functionality, not normal client drivers.

## Risk Notes

Descriptor length constants and bitfield macros must match the USB 3.1 specification. Incorrect sizes or masks can cause BOS parsing to misclassify capability data or overrun/underrun variable-length descriptors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/bos.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/genconsole.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/genconsole.h

## Role

Declares generic USB console input/output support used to hand USB keyboard/output state between HID/USBA and lower host-controller layers for OBP/polled console mode.

## Key Interfaces

- Defines opaque `usb_console_info_t` and lower-layer `usb_console_info_private_t`.
- Defines `usb_console_info_impl_t` with the target device `dev_info_t` and lower-layer private state pointer.
- Declares input lifecycle: `usb_console_input_init`, `usb_console_input_fini`, `usb_console_input_enter`, `usb_console_read`, and `usb_console_input_exit`.
- Declares output lifecycle: `usb_console_output_init`, `usb_console_output_fini`, `usb_console_output_enter`, `usb_console_write`, and `usb_console_output_exit`.

## Design Notes

Input/output enter and exit calls are responsible for preserving and restoring controller state when OBP takes control of the USB keyboard or console output path.

## Risk Notes

These interfaces are sensitive to polled-mode state transitions. Failure to save/restore lower controller state can leave normal interrupt-driven USB operation inconsistent after console/OBP use.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/genconsole.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi.h

## Role

Defines the Host Controller Driver Interface (HCDI): the operations vector and support routines used by USBA to call USB host controller drivers.

## Key Interfaces

- `usba_hcdi_ops_t` is the HCD operation vector registered at attach time. It includes PM support, pipe open/close/reset, data-toggle reset, control/bulk/interrupt/isochronous transfers, polling stop, frame-number queries, max isochronous packet queries, console input/output hooks, device initialization/finalization/addressing, and hub update support.
- Defines versioned HCD ops constants through `HCDI_OPS_VERSION_2`.
- `usba_hcdi_cb()` routes HCD transfer completion into synchronous waiters or asynchronous normal/exception callbacks.
- Provides request duplication helpers for interrupt and isochronous requests.
- Provides accessors for request private data, pipe data, endpoint data toggle state, and HCD device private storage.
- Provides allocation/registration/unregistration APIs for HCDI ops via `usba_alloc_hcdi_ops`, `usba_hcdi_register`, and `usba_hcdi_unregister`.
- Defines HCDI hotplug and error kstat structures and macros to access their kstat data.
- Defines `HCDI_DEFAULT_TIMEOUT` for non-periodic transfers when clients do not specify a timeout.

## Design Notes

This is the main contract boundary between framework code and controller-specific drivers. The operation vector is versioned so USBA can support old and new host-controller implementations.

## Risk Notes

Callback behavior depends on `USB_FLAGS_SLEEP`, completion reason, and request wrapper state. Incorrect HCD callback or ops-version handling can break synchronous waits, async callback ordering, transfer error reporting, or polled console support.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi_impl.h

## Role

Defines private per-host-controller USBA state for HCDI instances.

## Key Interfaces

- `usba_hcdi_t` stores the HCD devinfo pointer, DMA attributes, HCD ops, flags, soft interrupt handle, callback queue, transfer/burst constraints, root hub `usba_device_t`, USB address allocation bitmap, logging handle, interrupt cookies, mutex, hotplug counters, device count, kstat handles, and default ugen binding mode.
- Declares `usba_hcdi_set_hcdi()` and `usba_hcdi_get_hcdi()` for associating HCDI state with a devinfo node.
- Declares subsystem lifecycle functions `usba_hcdi_initialization()` and `usba_hcdi_destroy()`.

## Design Notes

The USB address bitmap is protected by `hcdi_mutex`; several stable fields are explicitly marked readable without locks for framework access patterns.

## Risk Notes

This structure is shared between HCD registration, address assignment, callback processing, root-hub management, kstats, and ugen policy. Layout or locking mistakes can affect all devices under a controller.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hcdi_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hubdi.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hubdi.h

## Role

Declares USBA hub-driver nexus interfaces used for root hubs, hub child devices, hub bus operations, reset, and power-budget accounting.

## Key Interfaces

- Declares hub subsystem initialization/destruction hooks.
- Defines `HUBDI_OPS_VERSION_0` and `HUBD_IS_ROOT_HUB`.
- Exposes hub character-device style entry points: open, close, ioctl, and root-hub power.
- Exports `usba_hubdi_busops`.
- Declares DDI autoconfiguration entry points: info, attach, probe, detach, and quiesce.
- Declares root-hub bind/unbind, device reset, and power budget increment/decrement/check helpers.

## Risk Notes

Hub reset and power budget functions sit in the enumeration path. Incorrect accounting can allow over-budget bus power usage or reject valid devices; reset errors can leave child devinfo nodes stale.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/hubdi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba10.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba10.h

## Role

Declares legacy USBA 1.0 wrapper entry points and compatibility functions exported to older USB client drivers.

## Key Interfaces

- Exposes internal helpers needed by the `usba10_calls` module, including descriptor endpoint lookup, endpoint number, clear-feature, bulk transfer-size, max isochronous packet count, PM-enabled query, descriptor-tree logging, client registration, and log-handle allocation.
- Declares `usba10_` wrappers for client register/unregister, descriptor tree free/print/log, data parsing, endpoint lookup, string descriptor retrieval, address/interface queries, device ownership, and pipe state/open/close/drain/reset/private-data operations.
- Declares wrapper allocation/free and transfer calls for control, bulk, interrupt, and isochronous requests.
- Declares wrapper calls for configuration, alternate interface, feature/status, current frame, maximum isochronous packets, power changes, remote wakeup, PM component creation, device power-level no-ops, async requests, event callbacks, checkpoint failure, logging, same-device checks, status-string helpers, rval-to-errno, and serialization helpers.

## Design Notes

This file preserves old driver source/binary expectations by forwarding legacy API names to newer USBA functionality.

## Risk Notes

Compatibility wrappers must keep old semantics while calling newer internals. Subtle differences in blocking, callback, PM, or request allocation behavior can break legacy USB drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba10.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb.h

## Role

Defines the public USBA device database record used to map USB device identity/preferences to configuration and driver choices.

## Key Interfaces

- `usba_configrec_t` stores selection string, vendor ID, product ID, configuration index, serial number, pathname, and preferred driver.
- Declares `usba_devdb_get_user_preferences()` to look up a matching user preference record.
- Declares `usba_devdb_refresh()` to reload or refresh the database.

## Risk Notes

This database can influence driver binding/configuration. Matching fields such as serial number and pathname must be interpreted consistently with parser and enumeration code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb_impl.h

## Role

Provides private implementation definitions for parsing and storing the USBA USB device configuration map.

## Key Interfaces

- Defines `USBCONF_FILE` as `/etc/usb/config_map.conf` and a static `usbconf_file` variable.
- `usba_devdb_info_t` wraps a `usba_configrec_t` with an AVL tree link.
- `config_field_t` enumerates parser fields for selection, vendor, product, configuration index, serial number, pathname, driver, and none.
- `usba_cfg_varlist[]` maps textual config-file variable names to parser field identifiers.

## Design Notes

The header includes kernel object lexer/parser support and AVL support, indicating the config map is parsed in-kernel and stored for lookup.

## Risk Notes

Because this header defines static data, inclusion discipline matters. Field names must remain synchronized with `/etc/usb/config_map.conf` syntax and lookup code.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_devdb_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_impl.h

## Role

Central private USBA implementation header tying together HCDI, hubdi, request wrappers, logging, enumeration, BOS handling, hotplug stats, and pipe/device utility functions.

## Key Interfaces

- Defines ugen binding modes for HCD `.conf` files and USB address allocation limits.
- `usba_pipe_async_req_t` describes asynchronous pipe management calls with callback and synchronous worker function.
- `usba_pm_req_t` describes asynchronous/nonblocking PM power-change requests.
- `usba_req_wrapper_t` is the private allocation wrapper around control/bulk/interrupt/isoc requests. It provides callback queue links, allocated-request tracking, synchronous completion CV, request owner, HCD private data, pipe pointer, completion reason, callback flags, request attributes, and allocation length.
- Provides macros converting between wrapper, request, request queues, allocated queues, and per-request pipe data.
- Declares HCD private accessors for control requests and USB address set/unset helpers.
- Defines private `usba_hubdi_t` and declares major subsystem init/destroy functions.
- Declares allocation/free, pipe state, async setup, callback drain, default pipe, pipe handle refcount, persistent pipe, leak checking, child device creation/destruction, BOS retrieval/property/free, hotplug stats, callback dispatch, and logging helpers.
- Defines debug print masks and `usba_log_handle_impl_t`.
- Defines node-name matching entries and node kind flags for device/interface/interface-association naming.
- Defines `usb_dev_cap_t` for USB device capture callback registration.

## Design Notes

The wrapper layout intentionally allocates USBA metadata immediately before the public request structure. Macros use pointer arithmetic to move between them.

## Risk Notes

Request wrapper pointer arithmetic, per-pipe task queues, callback queues, and sync CVs are core transfer machinery. Any mismatch in allocation layout or callback state handling can corrupt requests, leak allocations, or deadlock synchronous transfers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_private.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_private.h

## Role

Defines private USBA functions and structures shared inside the USB framework but not intended for client drivers.

## Key Interfaces

- Defines legacy DDK version support constants `USBA_LEG_MAJOR_VER` and `USBA_LEG_MINOR_VER`.
- Declares descriptor parsing helpers for device, configuration, interface association, interface, endpoint, class/vendor descriptors, arbitrary little-endian descriptor data, raw configuration data, and device descriptor retrieval.
- Defines private list type `usba_list_entry_t` plus list initialization, destruction, add/remove, move, leak-check, count, and pop helpers.
- Defines private USBA event tags and suspend/resume event strings.
- Declares DMA attribute lookup, driver binding, ownership, device/interface/interface-association node readiness, bus control, parent notification, usba_device get/set, event data lookup, pipe policy lookup, interrupt-context callback flag adjustment, and interface-number lookup.
- Defines packed standard descriptor sizes and legacy USB 1.1 power descriptor type values.
- Defines configuration and interface power descriptor structures plus parsers.
- Declares ASCII string descriptor conversion.
- Defines `usb_common_power_t` and common PM/event registration helpers for simple USB nexus drivers.

## Risk Notes

These APIs are inside-framework contracts. Descriptor parsers must tolerate extended descriptors while preserving truncation behavior; list and devinfo helpers are used during attach/detach/enumeration and must observe locking expectations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_types.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_types.h

## Role

Defines the core private USBA data model for pipe handles, USB devices, event registrations, endpoint indexing, speeds, and serialization.

## Key Interfaces

- `usba_ph_impl_t` backs opaque pipe handles and stores mutex, pipe data pointer, owner dip, endpoint descriptor, pipe policy, flags, refcount, pipe state, and state-changing flag.
- `usba_pipe_handle_data_t` stores per-open-pipe state: request queue, shared device pointer, pipe policy, standard and extended endpoint descriptors, owner dip, mutex, HCD/client private pointers, request count, task queue, callback queue, soft interrupt count, and special flags.
- Defines default pipe index, pipe-closing checks, default-pipe detection, endpoint count, PM component count, speed constants, port types, and data-toggle/persistent flags.
- `usba_evdata_t` stores per-devinfo event callback IDs for removal, insertion, suspend, and resume.
- `usb_client_dev_data_list_t` links multiple client registration data instances for one device.
- `usba_device_t` represents a USB device shared by multiple devinfo/client nodes. It stores device pipe list, mutex, dip, HCD ops, hub pointer, USB address, root hub fields, descriptors, raw/current/all configuration data, strings, preferred driver, port status, high-speed hub transaction state, hub bandwidth data, power draw, refcount, allocated request tracking, event cookies, client cleanup lists, shared task queues, parent hub pointer, HCD private pointer, and parsed BOS data.
- Defines client cleanup flags.
- `usba_serialization_impl_t` backs the public USB serialization handle.

## Design Notes

The comments emphasize that `usba_device_t` can be shared by multiple clients or devinfo nodes for composite devices. Pipe handles are unique even when underlying pipes can be shared.

## Risk Notes

This is high-risk shared state. Endpoint indexing assumes 32 endpoints and bitmask-sized exclusive tracking. Incorrect locking or lifetime handling can break composite devices, event callbacks, shared task queues, or HCD private state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugen.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugen.h

## Role

Declares the shared USBA-facing interface to the generic USB driver (ugen).

## Key Interfaces

- `usb_ugen_info_t` carries ugen flags and minor-node bit masks for ugen index and instance encoding.
- Defines opaque `usb_ugen_hdl_t`.
- Defines flags `USB_UGEN_ENABLE_PM` and `USB_UGEN_REMOVE_CHILDREN`.
- Declares ugen handle acquisition/release and driver entry wrappers for attach, detach, open, close, power, read, write, poll, disconnect event, and reconnect event.

## Risk Notes

Minor-node mask configuration controls how user-visible ugen device nodes map to endpoints/status nodes. Incorrect masks can alias devices or endpoints.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugen.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugend.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugend.h

## Role

Defines private data structures and macros for the USB generic driver implementation.

## Key Interfaces

- `usb_ugen_hdl_impl_t` stores ugen client handle state, devinfo, minor-node bit masks/shifts/limits, ugen state pointer, and log name.
- Defines devt lookup list/cache entries and a 10-entry cache.
- Defines minor-node sizing and extraction macros for instance, endpoint index, type, config value/index, interface, and alternate setting.
- Defines `ugen_minor_t`, minor-node type constants for device status, endpoint transfer, endpoint status, and whole-device ownership.
- Defines endpoint count, setup packet size, packet-size macro, and interrupt buffer limit.
- `ugen_ep_t` stores endpoint state, standard/extended descriptors, config/interface/alt identifiers, completion/status fields, open flags, buffer limits, pipe handle/policy, mutex/CV, serialization cookie, data/buf pointers, pollhead, and isochronous state.
- Defines endpoint state flags for active/open, interrupt polling, and isochronous polling.
- `ugen_dev_stat_t` tracks device status open state, exported state, wait CV, and pollhead.
- `ugen_power_t` tracks PM states, busy accounting, wakeup, and current power.
- `ugen_state_t` stores instance state, locks, serialization, log handle, client dev data, endpoint array, minor-node table, device status, PM pointer, max bulk transfer size, and cleanup flags.
- Defines ugen-specific unavailable device states and debug masks.

## Risk Notes

This header controls userland-visible generic USB endpoint access. Minor-number encoding, endpoint state flags, poll wakeups, and serialization must stay coherent or ugen can expose the wrong endpoint, race transfers, or misreport hotplug state.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugend.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_private.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_private.h

## Role

Declares unstable/private USBAI-adjacent interfaces used by Solaris/illumos USB client drivers but not part of the stable public USBAI contract.

## Key Interfaces

- Provides current configuration index lookup and string conversion helpers for completion reasons, callback flags, pipe state, device state, return values, plus `usb_rval2errno`.
- Defines `USB_FLAGS_SERIALIZED_CB`, default control pipe timeout, and `usb_pipe_sync_ctrl_xfer()`.
- Defines `usb_event_t` with disconnect, reconnect, pre-suspend, and post-resume callbacks, plus register/unregister and checkpoint-failure APIs.
- Defines logging handle type, log levels, debug-print macros/functions, log-handle allocation/free, and `usb_log`.
- Defines same-device check masks and `usb_check_same_device()`.
- Declares async PM raise/lower helpers and legacy/no-op device power-level helpers.
- Defines opaque serialization handle and functions to initialize/finalize, acquire, try-acquire, and release serialized access, including wait modes and same-thread checking.
- Defines async request scheduling flag `USB_FLAGS_NOQUEUE` and `usb_async_req()`.
- Declares endpoint-index helper and `usba_mk_mctl()`.

## Design Notes

The header labels these interfaces as unstable and marks status classes for migration/removal. It intentionally retains legacy DDK/client compatibility behavior.

## Risk Notes

Although private, these routines are used by real drivers. Changes to callback serialization, PM async behavior, or logging/string helpers can break out-of-tree or legacy clients.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_private.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_register_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_register_impl.h

## Role

Defines private state used while building a USB client descriptor tree during registration.

## Key Interfaces

- Defines binary descriptor dump formatting constants.
- Defines `USBA_ALL` sentinel for building all configurations/interfaces.
- `usba_reg_state_t` tracks current devinfo, current config/interface/alternate/endpoint nodes, last processed descriptor type, selected interface/configuration, total configuration length, current raw descriptor pointer/type/length, current config string, requested parse level, descriptor-tree root, and number of configurations.

## Design Notes

Warlock annotations mark descriptor tree and client registration fields as changed only at attach time.

## Risk Notes

Descriptor tree construction depends on correct state-machine placement of class/vendor-specific descriptors and correct parse-level filtering. Mistakes affect every client using `usb_get_dev_data()`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_register_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_version.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_version.h

## Role

Defines USB driver interface version constants for client drivers.

## Key Interfaces

- Defines `USBDRV_MAJOR_VER` as `2`.
- Defines `USBDRV_MINOR_VER` as `0`.

## Risk Notes

These constants participate in USBA driver/header version checks. Changing them affects source compatibility for USB client drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usbai_version.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usbai.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usbai.h

## Role

Primary public USB Architecture Interface (USBAI) header for illumos USB client drivers.

## Key Interfaces

- Defines USBAI version `2.1`, device states, return codes, callback flags, completion reasons, opaque pipe handles, opaque pointer type, and sleep/nosleep flags.
- Defines standard USB descriptor structures for device, qualifier, configuration, other-speed configuration, interface association, interface, endpoint, string, and SuperSpeed endpoint companion descriptors.
- Defines endpoint direction/type/synchronization/usage masks, packet-size masks, interval ranges, string length, and configuration attribute bits.
- Defines parsed descriptor-tree data structures: configuration, interface, alternate interface, endpoint, class/vendor-specific descriptor, parse levels, and `usb_client_dev_data_t`.
- Declares client registration, detach, descriptor tree free/print, descriptor parsing, endpoint lookup, string retrieval, address/interface/ownership utilities, and extended endpoint descriptor filling.
- Defines public pipe states and pipe policy, then declares pipe open/xopen/close/drain/reset/state/private-data APIs.
- Defines transfer request attributes and request structures/APIs for control, bulk, interrupt, and isochronous transfers.
- Defines setup/control request constants, descriptor type constants, standard request type/recipient masks, standard USB requests, feature selectors, and status bits.
- Declares wrapper helpers for synchronous control transfers, standard status/clear-feature/configuration/alternate-interface operations, max bulk size, current frame, and max isochronous packet count.
- Defines power management constants/masks/conversion macros, remote wakeup handling, PM component creation, hotplug callback registration, device reset levels, and `usb_reset_device()`.
- Defines project-private USB device capture registration callback types and APIs.
- Defines USB class, subclass, and protocol constants for audio, CDC, HID, printer, mass storage, hub, video, wireless, misc, application, and vendor-specific classes.

## Design Notes

This header is both a public driver contract and a detailed semantic specification. Its comments define legal state transitions, callback behavior, transfer queueing rules, polling rules, and blocking semantics.

## Risk Notes

This is ABI/API critical. Structure layouts, enum values, return codes, version checks, request semantics, and callback rules must remain compatible with existing USB drivers and HCD behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usbai.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/user.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/user.h

## Role

Defines process user-area data structures for kernel/kmem consumers and a reduced compatibility `struct user` for userland ptrace-style register access.

## Key Interfaces

- `struct exdata` records executable vnode, text/data/bss/library sizes, machine/magic values, file offsets, memory origins, and entry address.
- Kernel/kmem section defines file descriptor generation type `uf_entry_gen_t`.
- `uf_entry_t` is a per-file-descriptor entry with fd lock, file pointer, poll info, refcount, allocation/busy flags, close/set wait CVs, port association, assignment generation, and cache-line padding.
- `uf_rlist_t` tracks retired file lists.
- `uf_info_t` is per-process file descriptor table state with lock, bad-fd policy, table size, current fd list, and retired lists.
- `UF_ENTER`/`UF_EXIT` implement safe fd-entry locking against concurrent file-list growth.
- Defines `PSARGSZ`, `MAXCOMLEN`, `k_sysset_t`, and architecture-dependent `__KERN_NAUXV_IMPL`.
- Kernel `user_t` stores exec metadata, aux vector, start time/ticks, command/args, argv/envp/commpage pointers, cwd/root/current dir, memory/accounting/proc signal masks/handlers, saved rlimits, and open file info.
- Userland fallback `user_t` exposes saved registers, register pointer, ps args, signal dispositions, trap code, and fault address.

## Risk Notes

File descriptor locking rules are explicitly documented and subtle. `UF_ENTER` protects against `fi_list` replacement during `flist_grow()`. Any consumer bypassing these rules risks use-after-free or locking stale fd entries.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ustat.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ustat.h

## Role

Defines the obsolete SVR4 `ustat` filesystem statistics structure.

## Key Interfaces

- Emits a compile-time error for non-LP64 large-file compilation environments because `ustat` is incompatible there.
- `struct ustat` contains free-block count, free-inode count, filesystem name, and filesystem pack name.
- `_SYSCALL32` defines `struct ustat32` with 32-bit block and inode fields.

## Design Notes

The header warns applications to migrate to `statvfs(2)`.

## Risk Notes

This is legacy ABI. Structure sizes and large-file restrictions must remain compatible with old binaries and syscall32 translation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ustat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utime.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utime.h

## Role

Defines the `utime(2)` timestamp update structure.

## Key Interfaces

- `struct utimbuf` contains access time `actime` and modification time `modtime` as `time_t`.
- `_SYSCALL32` defines kernel view `struct utimbuf32` using `time32_t`.

## Risk Notes

This is public syscall ABI. 32-bit compatibility layout must stay synchronized with `utime` syscall copyin handling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utime.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utsname.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utsname.h

## Role

Defines the `uname(2)` system identity structure and namespace-dependent declarations.

## Key Interfaces

- Defines `_SYS_NMLN` as 257 and conditionally exposes `SYS_NMLN`.
- `struct utsname` contains `sysname`, `nodename`, `release`, `version`, and `machine` arrays.
- Conditionally exposes global `utsname` under non-strict/extension namespaces.
- Userland declares `uname()`, with special i386 compatibility handling for old SVID behavior through `_nuname`.
- Kernel declares `uts_nodename()` to retrieve the nodename as seen by the current process zone.

## Risk Notes

`struct utsname` element size is ABI-visible and must support Internet hostnames. i386 symbol remapping preserves historical behavior and should not be disturbed casually.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utsname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utssys.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utssys.h

## Role

Defines command numbers, flags, and result structures for the legacy `utssys()` syscall family.

## Key Interfaces

- Defines `UTS_UNAME`, `UTS_USTAT`, and `UTS_FUSERS` command codes.
- Defines `UTS_FUSERS` flags for file-only, contained, NBMAND-only, device-info, and kernel-info count modes.
- `f_user_t` reports either process user info (`pid`, `uid`) or kernel device consumer info (`modid`, `instance`, `minor`) with flags.
- `fu_data_t` is a variable-length result container with max/count and first `f_user_t`.
- Defines convenience aliases for union fields and `fu_data_size(x)`.
- Defines `fu_flags` values for cwd, root, text, mapped file, open file, trace, tty, NBMAND lock, and kernel consumer.

## Risk Notes

Variable-length sizing and user/kernel union interpretation must match syscall producer and consumer logic. Flag values are ABI visible to `fuser`-style tooling.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/utssys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uuid.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uuid.h

## Role

Defines UUID wire/storage types and endian conversion helper.

## Key Interfaces

- `uuid_node_t` stores a 6-byte node ID.
- `struct uuid` stores RFC-style UUID fields: time low/mid/high-version, clock sequence bytes, and 6-byte node address.
- Defines `UUID_LEN` as 16 and printable string length as 37.
- Defines `uuid_t` as a 16-byte `uchar_t` array.
- `UUID_LE_CONVERT(dest, src)` copies a UUID struct and converts time fields to little-endian using `LE_32`/`LE_16`.

## Risk Notes

UUID byte order is frequently confused between struct and byte-array forms. The conversion macro only adjusts the integer time fields, leaving sequence/node bytes unchanged.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va-sparc.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va-sparc.h

## Role

Provides SPARC-specific GNU/Sun-compatible variable argument implementation definitions for old compiler/header paths.

## Key Interfaces

- Defines `__gnuc_va_list` differently for SPARC v9 and non-v9/SVR4 compatibility cases.
- For SPARC v9, `__gnuc_va_list` is a struct tracking next integer output register, floating register, limits, and stack argument pointer.
- Defines `va_start` for stdarg and varargs styles using GCC builtins such as `__builtin_saveregs`, `__builtin_args_info`, and `__builtin_next_arg`.
- Defines `va_alist`/`va_dcl` for old varargs style.
- Defines `va_end` as no-op after optional libgcc declaration.
- Defines `enum __va_type_classes` mirroring GCC type classification.
- Defines `va_arg` for SPARC v9 register/stack ABI and for non-v9 rounded-size stack access, including aggregate and long-double handling.

## Risk Notes

This header encodes ABI-specific varargs mechanics. It depends on GCC builtins and SPARC calling conventions; incorrect alignment or register/stack transition handling breaks all variadic functions on affected builds.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va-sparc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_impl.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_impl.h

## Role

Common implementation layer for illumos variable argument support used by `stdarg.h`, `varargs.h`, ISO stdarg headers, and `sys/varargs.h`.

## Key Interfaces

- Documents common implementation macros: `__va_start`, `__va_arg`, `__va_copy`, and `__va_end`.
- Includes `sys/va_list.h` for `__va_list`, `__va_alist_type`, and ISA definitions.
- Provides lint protocol definitions.
- Provides protocol for compilers with `__BUILTIN_VA_STRUCT`, using `__builtin_va_start` and `__builtin_va_arg_incr`.
- Provides protocol for `__BUILTIN_VA_ARG_INCR`.
- Provides GCC 2.96+/3+ protocol using `__builtin_stdarg_start` or `__builtin_va_start`, `__builtin_va_arg`, `__builtin_va_end`, and `__builtin_va_copy`.
- Emits a compile-time error for unrecognized compiler protocols.

## Design Notes

The header centralizes compiler-specific handling while keeping user-facing namespace pollution out of standard headers.

## Risk Notes

Compiler feature detection is critical. Falling into the wrong protocol produces silent ABI corruption, so unknown compilers intentionally fail compilation.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_list.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_list.h

## Role

Defines internal variable-argument list types consumed by headers that need `va_list`-compatible declarations.

## Key Interfaces

- Defines `__va_alist_type` as `long` for LP64 and `int` otherwise.
- Defines `__va_void(expr)` and `__va_ptr_base`.
- For `__BUILTIN_VA_STRUCT` on amd64, defines `__va_list` as a one-element struct array with GP offset, FP offset, overflow area, and register save area pointer.
- For modern GCC, aliases `__gnuc_va_list` and `__va_list` to `__builtin_va_list`.
- Default fallback defines `__va_list` as `void *`.

## Design Notes

Applications are told not to include this directly; it exists so headers such as stdio, wchar, strlog, and syslog can mention va_list-related types safely.

## Risk Notes

The amd64 built-in structure fields must match compiler ABI expectations. The member name `__va_reg_sve_area` appears to be the register save area pointer used by this ABI definition.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_list.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/var.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/var.h

## Role

Defines legacy system configuration tunable structure `struct var`.

## Key Interfaces

- `struct var` contains counts/limits for I/O buffers, callouts, processes, user processes, scheduler priorities, clists, buffer hash state, physical I/O buffers, system virtual allocation map size, maximum physical memory, delayed-write age, and buffer cache high-water mark.
- Exports global `struct var v`.

## Risk Notes

This is historical system configuration ABI/state. Many fields may be obsolete or compatibility-only, but consumers still depend on names and layout.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/var.h -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/varargs.h -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/varargs.h

## Role

Defines Solaris system variable-argument macros in terms of the shared `sys/va_impl.h` implementation.

## Key Interfaces

- Includes `sys/va_impl.h`.
- Defines `va_list` as `__va_list` when `_VA_LIST` is not already defined.
- Maps `va_start`, `va_arg`, `va_copy`, and `va_end` directly to `__va_start`, `__va_arg`, `__va_copy`, and `__va_end`.

## Design Notes

Despite the file name, it explicitly provides stdarg-style semantics rather than old K&R varargs semantics.

## Risk Notes

This header is part of the compiler/standard-library ABI surface. Macro definitions must remain synchronized with `va_impl.h` and `va_list.h`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/varargs.h -->