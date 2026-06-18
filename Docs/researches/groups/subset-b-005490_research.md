# Research: subset-b-005490

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/composite.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/composite.c

## Purpose
`composite.c` is the core Linux USB gadget composite framework implementation. It lets one gadget driver expose a USB device made from one or more configurations and one or more function drivers, then mediates descriptor generation, endpoint setup, EP0 request dispatch, configuration selection, string IDs, OS descriptors, WebUSB BOS data, suspend/resume, disconnect/reset, and registration with the UDC layer.

## Important APIs, Types, and Functions
Key exported APIs are `usb_composite_probe()`, `usb_composite_unregister()`, `usb_add_config()`, `usb_add_config_only()`, `usb_add_function()`, `usb_remove_function()`, `usb_interface_id()`, `usb_string_id()`, `usb_string_ids_tab()`, `usb_string_ids_n()`, `usb_gstrings_attach()`, `config_ep_by_speed()`, `config_ep_by_speed_and_alt()`, `usb_function_deactivate()`, `usb_function_activate()`, `usb_func_wakeup()`, `usb_composite_setup_continue()`, and `usb_composite_overwrite_options()`. Internally, `struct usb_os_string` models Microsoft OS string descriptor 0xee. `function_descriptors()` selects the descriptor vector for the negotiated speed with fallback. `config_buf()`, `config_desc()`, `count_configs()`, `bos_desc()`, and `device_qual()` assemble standard descriptors. `set_config()` activates a selected configuration and calls each function's `set_alt()`. `composite_setup()` is the main EP0 dispatcher.

## Control Flow
Registration starts in `usb_composite_probe()`, which copies `composite_driver_template` into the caller's driver and registers with `usb_gadget_register_driver()`. UDC bind calls `composite_bind()`: allocate `usb_composite_dev`, initialize locks/lists, prepare EP0 request buffers, call the gadget driver's `bind()`, optionally allocate OS descriptor request state, then finalize unchanged device descriptor fields. Configurations are added through `usb_add_config()`, which calls the supplied config bind routine and validates endpoint allocation with `usb_gadget_check_config()`. Functions are added via `usb_add_function()`, which links the function, optionally deactivates enumeration, calls `function->bind()`, and records speed support.

At enumeration, `composite_setup()` handles standard requests directly. GET_DESCRIPTOR routes to device/config/string/BOS/OTG/qualifier builders. SET_CONFIGURATION calls `set_config()` under `cdev->lock`; SET_INTERFACE calls the relevant function's `set_alt()`; GET_INTERFACE calls `get_alt()` if present. Non-standard requests first check Microsoft OS and WebUSB vendor requests, then dispatch to `req_match()` functions, interface recipients, endpoint recipients, the configuration `setup()`, or the lone function fallback. Responses are queued with `composite_ep0_queue()`, and delayed status is completed later through `usb_composite_setup_continue()`.

## State and Persistence
Runtime state lives in `struct usb_composite_dev`: active `config`, `configs` list, gadget pointer, descriptor copy, string ID cursor, `gstrings`, deactivation count, delayed status count, suspend flag, pending EP0 requests, OS/WebUSB flags, and OS descriptor buffers. Functions store speed-specific descriptor copies, endpoint usage bitmaps, suspend/wakeup flags, and callbacks. State is in-memory only and reset on disconnect, reset, unbind, or unregister. `deactivations` gates pullup activation; `delayed_status` counts outstanding deferred status stages; endpoint bitmaps are rebuilt when setting a config so endpoint-recipient control requests can be routed to owning functions.

## Dependencies and Integration Points
This file depends on USB gadget core (`struct usb_gadget`, `usb_ep_queue()`, `usb_gadget_register_driver()`), composite API declarations from `<linux/usb/composite.h>`, descriptor helpers from `config.c`, endpoint assignment from `epautoconf.c`, Microsoft OS descriptor helpers in `u_os_desc.h`, and WebUSB constants. It integrates directly with function drivers through the `struct usb_function` callback surface: `bind`, `unbind`, `set_alt`, `get_alt`, `setup`, `disable`, `suspend`, `resume`, `get_status`, `func_suspend`, and `req_match`.

## Risks
EP0 handling is concurrency-sensitive: setup requests, delayed status, OS descriptor requests, and unbind cleanup all share request objects and flags. Descriptor fallback can hide missing speed descriptors with warnings but may still fail endpoint lookup. `config_ep_by_speed_and_alt()` assumes companion descriptors immediately follow SuperSpeed endpoints. `set_config()` must unwind all previously enabled functions if any later `set_alt()` fails. OS descriptor and WebUSB paths are bounded by EP0 buffer sizes, but malformed lengths and interface indexes are important fuzzing targets. Function suspend/wakeup state must stay consistent with configuration wakeup capability or hosts may see incorrect USB 3 function wake status.

## Test Signals
Useful signals include enumeration at full/high/super/super-plus speeds; descriptor dumps for device/config/other-speed/BOS/WebUSB/OS descriptors; SET_CONFIGURATION and SET_INTERFACE failure unwinds; multiple-function endpoint-recipient control dispatch; delayed-status functions; deactivation/activation reference counting; suspend/resume and reset/disconnect behavior; remote wakeup capability clearing; and configfs/legacy gadgets using ACM/ECM/EEM to verify real function callback integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/composite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/config.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/config.c

## Purpose
`config.c` provides small but central descriptor utilities used by USB gadget function and composite drivers. It copies null-terminated descriptor vectors, marshals descriptor arrays into EP0/configuration buffers, assigns per-speed descriptor copies to a `usb_function`, frees them, and builds OTG descriptors based on gadget OTG capabilities.

## Important APIs, Types, and Functions
Exports are `usb_descriptor_fillbuf()`, `usb_copy_descriptors()`, `usb_assign_descriptors()`, `usb_free_all_descriptors()`, `usb_otg_descriptor_alloc()`, and `usb_otg_descriptor_init()`. The code operates on `struct usb_descriptor_header **` vectors, `struct usb_function` descriptor slots (`fs_descriptors`, `hs_descriptors`, `ss_descriptors`, `ssp_descriptors`), and OTG descriptor types `struct usb_otg_descriptor` and `struct usb_otg20_descriptor`.

## Control Flow
`usb_descriptor_fillbuf()` walks a descriptor pointer array until NULL, copying each descriptor length into the destination if it fits. `usb_copy_descriptors()` first counts descriptors and total bytes, allocates one contiguous block for pointer vector plus descriptor bytes, then rewrites vector entries to point inside that block. `usb_assign_descriptors()` copies supplied FS/HS/SS/SSP vectors into the function; absent SSP falls back to SS. On any allocation failure it calls `usb_free_all_descriptors()` to leave no partial descriptor state. OTG allocation chooses descriptor size by `gadget->otg_caps->otg_rev`; initialization fills SRP/HNP/ADP capability bits and bcdOTG where applicable.

## State and Persistence
All descriptor state is heap allocated and owned by the function after assignment. The vectors are per-function copies so bind routines can patch static templates before assignment without later mutations affecting already-bound functions. OTG descriptors are separately allocated and typically hung off configuration descriptor arrays by callers. Nothing persists across unbind; callers must free through `usb_free_all_descriptors()` and `kfree()` for OTG allocations.

## Dependencies and Integration Points
The composite framework uses `usb_descriptor_fillbuf()` when building configuration descriptors and function drivers use `usb_assign_descriptors()` after endpoint/interface/string IDs are assigned. The file depends on USB chapter 9 descriptor definitions, gadget OTG capability structures, and `usb_free_descriptors()` from the gadget API.

## Risks
Descriptor vectors must be NULL-terminated and each descriptor's `bLength` must be correct; malformed templates can cause incorrect allocation size or EP0 copy failure. `usb_descriptor_fillbuf()` returns `-EINVAL` if a descriptor does not fit, so callers must propagate that to avoid truncated descriptors. SSP fallback to SS is intentional but can mask lack of true SuperSpeedPlus descriptors. OTG initialization assumes `otg_caps` is coherent when `otg_rev >= 0x0200`.

## Test Signals
Check descriptor copy/free under allocation fault injection, configuration descriptor building with too-small buffers, FS/HS/SS/SSP enumeration with functions that omit SSP descriptors, and OTG 1.x versus 2.0 descriptor generation for gadgets with different `otg_caps` combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/configfs.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/configfs.c

## Purpose
`configfs.c` implements the configfs-backed USB gadget composition interface at `usb_gadget`. It lets userspace create gadget objects, set device descriptor attributes, create strings/configurations/functions, link functions into configurations, configure Microsoft OS descriptors and WebUSB metadata, then bind the constructed composite gadget to a UDC by writing the `UDC` attribute.

## Important APIs, Types, and Functions
The central container is `struct gadget_info`, which embeds configfs groups, a mutex, available function list, string list, `usb_composite_driver`, and `usb_composite_dev`. `struct config_usb_cfg` wraps a configfs config group plus `struct usb_configuration` and staged function list. `struct gadget_language` and `struct gadget_config_name` hold device/config strings. Major paths include `gadgets_make()`, `gadget_dev_desc_UDC_store()`, `unregister_gadget()`, `function_make()/function_drop()`, `config_desc_make()`, `config_usb_cfg_link()/unlink()`, string make/drop/store helpers, WebUSB attribute stores, OS descriptor link/unlink, `usb_os_desc_prepare_interf_dir()`, `configfs_composite_bind()`, `purge_configs_funcs()`, and wrapper callbacks for setup/disconnect/reset/suspend/resume.

## Control Flow
Module init registers a `configfs_subsystem` named `usb_gadget`. Creating a gadget allocates `gadget_info`, default groups (`functions`, `configs`, `strings`, `os_desc`, `webusb`), initializes the embedded composite device, creates a configfs gadget driver name, and defaults `max_speed` to SuperSpeedPlus. Creating `functions/FUNC.INSTANCE` calls `usb_get_function_instance()` and stores the instance in `available_func`. Creating `configs/name.N` allocates a `config_usb_cfg`, initializes strings, defaults power/attributes, and calls `usb_add_config_only()` on the embedded cdev. Symlinking a function into a config verifies the instance belongs to the same gadget, rejects links while bound, gets a concrete `usb_function`, and stages it in `cfg->func_list`.

Binding happens when userspace writes a non-empty UDC name. `gadget_dev_desc_UDC_store()` sets `udc_name` then calls `usb_gadget_register_driver()`, whose bind callback is `configfs_composite_bind()`. That prepares the cdev, validates at least one config and one function per config, attaches gadget and config strings, copies OS/WebUSB settings, optionally allocates OTG descriptors, links each staged function into the real config with `usb_add_function()`, validates config endpoint resources, prepares OS descriptor request storage, and resets endpoint autoconfig state. Unbind purges bound functions back to configfs staging lists, frees composite resources, clears gadget data, and resets deactivation state.

## State and Persistence
Configfs directory objects persist while their configfs items exist. Live UDC binding state is `gi->composite.gadget_driver.udc_name`; writing an empty UDC unregisters. `gi->lock` serializes configfs mutations and bind/unbind decisions. `gi->spinlock` and `gi->unbind` protect UDC callbacks racing with unbind by making wrappers re-check gadget data under the spinlock. Function instances live in `available_func`; concrete function objects move between `cfg->func_list` before bind and `c->functions` while bound. Strings are stored as allocated C strings in configfs objects and attached as gadget string containers at bind time.

## Dependencies and Integration Points
This file integrates configfs core, the composite framework (`composite_dev_prepare()`, `composite_setup()`, `usb_add_config_only()`, `usb_add_function()`), function registry APIs (`usb_get_function_instance()`, `usb_get_function()`, put counterparts), descriptor helpers, `u_os_desc.h`, WebUSB constants, and function-specific configfs helpers. `usb_os_desc_prepare_interf_dir()` is exported so function drivers can expose per-interface OS descriptor configfs groups.

## Risks
The highest-risk areas are lifecycle and locking. Userspace can unlink functions or OS descriptor configs while bound, so the code forces unregister and must restore staged lists correctly. The static `otg_desc` array is shared module state and is allocated/freed around binds. String language tables require every language to contain the same number of strings; mismatch aborts bind. Attribute stores mostly mutate fields even while unbound and some WebUSB/OS flags can change while bound, so tests should confirm whether host-visible state changes only after rebind. Extended property stores adjust length accounting when switching binary/unicode types; off-by-one and empty-write cases are important because `page[len - 1]` is accessed.

## Test Signals
Exercise configfs creation/removal order, duplicate languages/configuration values, function links from other gadgets, double links, writes to `UDC` bind/unbind, unlinking while bound, OS descriptor symlink behavior, WebUSB BOS and landing-page descriptor responses, multi-language string consistency, MaxPower/bmAttributes validation, max_speed changes before versus after bind, and concurrent control requests during unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/configfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/configfs.h -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/configfs.h

## Purpose
`configfs.h` is the local header that exposes configfs gadget helpers shared between `configfs.c` and USB function implementations. It declares gadget unregistration through a config item, declares OS descriptor interface directory creation, and provides a typed conversion helper for OS descriptor config groups.

## Important APIs, Types, and Functions
The exported declarations are `unregister_gadget_item(struct config_item *item)` and `usb_os_desc_prepare_interf_dir(struct config_group *parent, int n_interf, struct usb_os_desc **desc, char **names, struct module *owner)`. The inline `to_usb_os_desc()` converts a config item for an interface OS descriptor group back to `struct usb_os_desc` using `container_of()`.

## Control Flow
Function drivers that need OS descriptor configfs support call `usb_os_desc_prepare_interf_dir()` with their parent function group, number of interfaces, descriptor objects, names, and module owner. Configfs release or external helper paths can call `unregister_gadget_item()` to unbind a gadget represented by a root config item. `to_usb_os_desc()` is used by attribute handlers in `configfs.c` for compatible IDs and extended properties.

## State and Persistence
The header owns no state. It defines access to state allocated and managed by `configfs.c`: gadget root objects and per-interface `usb_os_desc` groups.

## Dependencies and Integration Points
It depends on `<linux/configfs.h>` and assumes `struct usb_os_desc` is visible to includers through surrounding USB gadget headers. It is a narrow integration point between configfs gadget infrastructure and function drivers that expose Microsoft OS descriptor metadata.

## Risks
The conversion helper assumes the item is a config group embedded in `struct usb_os_desc`; using it on the wrong item type will corrupt type interpretation. Callers of `usb_os_desc_prepare_interf_dir()` must provide descriptor and name arrays that remain valid for the created groups.

## Test Signals
Compile coverage from OS-descriptor-capable functions, configfs creation of `os_desc/interface.*` groups, compatible/sub-compatible ID stores, extended property make/drop, and gadget unregistration through a config item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/configfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/epautoconf.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/epautoconf.c

## Purpose
`epautoconf.c` provides endpoint autoconfiguration helpers so gadget function drivers can request endpoints by descriptor requirements instead of hard-coding controller endpoint names or numbers. It assigns endpoint addresses, sets initial max packet values, marks endpoints claimed, and resets/releases autoconfig state.

## Important APIs, Types, and Functions
Exports are `usb_ep_autoconfig_ss()`, `usb_ep_autoconfig()`, `usb_ep_autoconfig_release()`, and `usb_ep_autoconfig_reset()`. The inputs are `struct usb_gadget`, `struct usb_endpoint_descriptor`, and optionally `struct usb_ss_ep_comp_descriptor`. The code relies on controller `gadget->ops->match_ep` when present and otherwise uses `usb_gadget_ep_match_desc()` over `gadget->ep_list`.

## Control Flow
`usb_ep_autoconfig_ss()` first lets the UDC choose an endpoint with `match_ep()`. If that fails, it scans unclaimed endpoints for descriptor compatibility. Once found, it fills `wMaxPacketSize` from `ep->maxpacket_limit` if the function left it zero, derives an endpoint address either from numeric endpoint names like `ep2...` or from gadget `in_epnum`/`out_epnum` counters, assigns `ep->address`, clears `ep->desc` and `ep->comp_desc`, and marks `ep->claimed`. `usb_ep_autoconfig()` wraps the SS helper and caps full-speed bulk maxpacket at 64 bytes. Release and reset clear `claimed`/`driver_data`; reset also zeros the address counters.

## State and Persistence
Autoconfig state is held on each `struct usb_ep` (`claimed`, `address`, `driver_data`) and on the gadget counters `in_epnum` and `out_epnum`. It persists during a bind/config construction pass and is reset between configurations or on cleanup by composite/configfs code.

## Dependencies and Integration Points
Function bind methods for ACM, ECM, EEM, and other functions call these helpers before `usb_assign_descriptors()`. Composite code calls `usb_ep_autoconfig_reset()` after adding configs and during cleanup. The UDC can override matching via `match_ep`, enabling hardware-specific constraints.

## Risks
Endpoint address derivation from `ep->name[2]` assumes common endpoint naming and falls back to counters with a 15 endpoint limit. A selected endpoint may not be optimal for controller-specific FIFO/transfer constraints. Releasing an endpoint invalidates it for the releasing function. Missing reset between alternate configuration construction could cause false endpoint exhaustion.

## Test Signals
Test UDCs with and without `match_ep`, named and unnamed endpoint patterns, bulk/interrupt/isoc descriptors, SuperSpeed companion descriptors, counter overflow beyond endpoint 15, release/rebind paths, and multi-configuration gadgets that need different endpoint assignments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/epautoconf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/Makefile -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/Makefile

## Purpose
The Makefile defines how USB gadget function drivers are built in the kernel tree. It maps Kconfig symbols such as `CONFIG_USB_F_ACM`, `CONFIG_USB_F_ECM`, and `CONFIG_USB_F_EEM` to object modules and adds include paths for gadget and UDC headers.

## Important APIs, Types, and Functions
This is kbuild metadata, not C code. Important variables are `ccflags-y`, per-module object lists like `usb_f_acm-y := f_acm.o`, `usb_f_ecm-y := f_ecm.o`, `usb_f_eem-y := f_eem.o`, and `obj-$(CONFIG_...) += ...`. Multi-object functions include RNDIS, mass storage, FunctionFS, UAC, UVC, and source/sink loopback.

## Control Flow
During kernel build, kbuild evaluates each `obj-$(CONFIG_*)` line. Built-in `y` links objects into the kernel; module `m` builds loadable modules. Composite object variables define the constituent `.o` files before the final module object is emitted. The UVC section conditionally adds `uvc_trace.o` and extra `CFLAGS_uvc_trace.o` when `CONFIG_TRACING` is enabled.

## State and Persistence
The file affects build products only. There is no runtime state. Its output determines which function drivers are available for legacy gadgets or configfs function instances.

## Dependencies and Integration Points
It integrates USB function implementation files with Kconfig. `ccflags-y` supplies include paths for local gadget headers and UDC headers. Network functions depend on shared `u_ether.o`, serial functions on `u_serial.o`, audio on `u_audio.o`, and so on through their selected config symbols.

## Risks
Incorrect object lists lead to unresolved symbols or missing configfs functions. Missing shared helper objects for selected functions break link. Conditional UVC tracing flags must stay aligned with source inclusion. Because configfs discovers functions registered by compiled modules, build configuration directly controls userspace-visible function names.

## Test Signals
Build all relevant `CONFIG_USB_F_*` permutations as built-in and module, especially ACM/ECM/EEM plus shared `USB_U_SERIAL` and `USB_U_ETHER`. Verify `modinfo`, module load, and configfs `functions/FUNC.INSTANCE` creation for each selected function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_acm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_acm.c

## Purpose
`f_acm.c` implements the USB CDC Abstract Control Model serial function. It wraps the generic gadget serial (`u_serial`) data path with CDC ACM descriptors, control requests for line coding and control line state, interrupt notifications for serial state, configfs attributes, and function registration under the name `acm`.

## Important APIs, Types, and Functions
`struct f_acm` embeds `struct gserial` and stores control/data interface IDs, port number, interface protocol, notification endpoint/request, line coding, handshake bits, serial state, and a spinlock protecting pending notifications. Descriptor tables cover FS/HS/SS, including IAD, control/data interfaces, CDC header/call-management/ACM/union descriptors, notify interrupt endpoint, and bulk data endpoints. Key functions are `acm_setup()`, `acm_complete_set_line_coding()`, `acm_set_alt()`, `acm_disable()`, `acm_cdc_notify()`, `acm_notify_serial_state()`, `acm_cdc_notify_complete()`, `acm_connect()`, `acm_disconnect()`, `acm_send_break()`, `acm_bind()`, `acm_unbind()`, `acm_alloc_instance()`, and `acm_alloc_func()`.

## Control Flow
Creating a configfs instance allocates `f_serial_opts`, reserves a `u_serial` line, and exposes `port_num`, `protocol`, and optional console attributes. Allocating a function creates `f_acm`, copies the selected port/protocol, and installs USB function callbacks. During bind, strings and interface IDs are assigned, endpoint addresses are autoconfigured for bulk IN/OUT and interrupt notify, a notification request is allocated, HS/SS descriptors inherit endpoint addresses, and descriptor copies are assigned. `set_alt()` enables the notify endpoint for the control interface and connects/disconnects the generic serial port on the data interface. `setup()` handles SET/GET_LINE_CODING, SET_CONTROL_LINE_STATE, and SEND_BREAK, queuing EP0 responses or OUT completions as needed.

## State and Persistence
Line coding defaults to the zeroed struct until the host sets it. `port_handshake_bits` records DTR/RTS-like state but data flow is not gated on DTR. `serial_state` is updated on connect/disconnect/break and sent through a single reusable notification request. If a serial-state change occurs while the request is in flight, `pending` causes the completion handler to send another notification. Instance state persists while the configfs function instance exists; concrete function state is freed by `free_func`.

## Dependencies and Integration Points
The file depends on `u_serial` for TTY allocation, connect/disconnect, suspend/resume, console helpers, and request allocation. It integrates with composite helpers for string IDs, interface IDs, endpoint autoconfig, speed-based endpoint configuration, and descriptor assignment. It registers with the function framework using `DECLARE_USB_FUNCTION_INIT(acm, ...)`.

## Risks
The notification path is interrupt/callback-sensitive and relies on `acm->lock` plus a single request. `SET_LINE_CODING` accepts and stores host data without semantic validation. Static descriptor templates are patched at bind time before per-instance copies; multi-instance behavior depends on prompt copying after patching. The SS descriptor table reuses the HS notify descriptor plus an SS companion descriptor, so endpoint companion ordering must match composite expectations. DTR is recorded but not enforced, which may surprise hosts or tests expecting no data before DTR.

## Test Signals
Enumerate ACM at FS/HS/SS, open/close `/dev/ttyGS*`, issue CDC line coding/control line state/break requests, verify interrupt SerialState notifications and pending notification replay, suspend/resume serial traffic, create multiple ACM instances with different protocols, and test configfs protocol writes fail with `-EBUSY` while instances exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_acm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ecm.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ecm.c

## Purpose
`f_ecm.c` implements the USB CDC Ethernet Control Model function. It exposes a USB Ethernet network interface using a CDC control interface, a data interface with alternate settings, bulk data endpoints via `u_ether`, and an interrupt notification endpoint for network connection and speed changes. The configfs function name is `ecm`.

## Important APIs, Types, and Functions
`struct f_ecm` embeds `struct gether`, stores control/data interface IDs, CDC MAC string, notify endpoint/request, notification state/count, and open state. Descriptors include IAD, CDC header/union/ethernet descriptors, data altsetting 0 with no endpoints, data altsetting 1 with bulk endpoints, and FS/HS/SS notification descriptors. Important functions are `ecm_setup()`, `ecm_set_alt()`, `ecm_get_alt()`, `ecm_disable()`, `ecm_do_notify()`, `ecm_notify()`, `ecm_notify_complete()`, `ecm_open()`, `ecm_close()`, `ecm_bind()`, `ecm_unbind()`, `ecm_suspend()`, `ecm_resume()`, `ecm_get_status()`, `ecm_alloc_inst()`, and `ecm_alloc()`.

## Control Flow
Instance allocation creates `f_ecm_opts`, initializes a default Ethernet netdev with `gether_setup_default()`, and exposes dev/host address, qmult, and ifname attributes. Function allocation increments the option refcount, captures the host MAC in CDC string format, and sets callback pointers. Bind validates `can_support_ecm()`, registers or attaches the shared netdev to the gadget, attaches strings, assigns two interfaces, autoconfigures IN/OUT/notify endpoints, allocates a notify request buffer, mirrors endpoint addresses into HS/SS descriptors, assigns descriptors, and sets `port.open/close` callbacks. Runtime activation is through `SET_INTERFACE`: control alt 0 enables notify; data alt 1 configures data endpoints, sets ZLP/filter defaults, and calls `gether_connect()`. Alt 0 disconnects data traffic. Host packet filter control requests update `port.cdc_filter`.

## State and Persistence
The network device is owned by `f_ecm_opts` and may be shared across bound function instances through `bind_count`, `bound`, and `refcnt` conventions from `u_ether_configfs`. `notify_state` sequences CONNECT then SPEED notifications; `notify_count` prevents multiple in-flight notify requests. `is_open` reflects netdev open/close callbacks. `get_alt()` reports data interface alt 1 when the IN endpoint is enabled. State resets on disable/unbind, where notify requests are dequeued/freed and the gadget is detached from the netdev when no longer bound.

## Dependencies and Integration Points
ECM depends on `u_ether` for netdev setup, gadget attach/detach, connect/disconnect, bitrate, suspend/resume, and data transfer. Configfs attributes come from `u_ether_configfs.h`; ECM-specific shared declarations are in `u_ecm.h`. Composite integration uses string/interface ID allocation, endpoint autoconfig, speed-specific endpoint configuration, descriptor assignment, USB 3 function wake status, and function registration.

## Risks
The comments call out weak locking around `is_open` and packet filter updates. Notification sequencing allows connect notifications to overlap conceptually, guaranteeing speed notification but not strict ECM text ordering. Bind has several allocation/registration stages and relies on cleanup attributes (`__free`) plus unbind detach logic. Hosts that do not poll the notification endpoint can leave notifications in FIFO. ECM requires alternate settings and a valid `get_alt()`; errors in alt handling can expose endpoints at the wrong time.

## Test Signals
Run ECM on hosts with CDC ECM support at FS/HS/SS, verify interface alt 0/1 transitions, packet filter class request behavior, netdev open/close notification pairs, speed-change notifications, unplug/rmmod/SET_CONFIGURATION/SET_INTERFACE while open and closed, suspend/resume, function remote wake status bits, and configfs address/qmult/ifname attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_ecm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_eem.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_eem.c

## Purpose
`f_eem.c` implements the USB CDC Ethernet Emulation Model function. Unlike ECM, it uses one interface with bulk IN/OUT endpoints and wraps Ethernet frames in EEM packet headers/trailers. It integrates with `u_ether` for the network device and registers a configfs function named `eem`.

## Important APIs, Types, and Functions
`struct f_eem` embeds `struct gether` and stores one interface ID. `struct in_context` tracks dynamically allocated echo-response request context. Descriptor tables include a CDC EEM communication-class interface and FS/HS/SS bulk endpoints with SuperSpeed companion descriptors. Key functions are `eem_setup()`, `eem_set_alt()`, `eem_disable()`, `eem_bind()`, `eem_wrap()`, `eem_unwrap()`, `eem_cmd_complete()`, `eem_alloc_inst()`, `eem_alloc()`, `eem_unbind()`, and `eem_free()`.

## Control Flow
Instance allocation creates `f_eem_opts`, initializes a default `u_ether` netdev, and exposes standard Ethernet configfs attributes. Function allocation increments the option refcount, sets `gether` I/O state, and installs wrap/unwrap callbacks plus header length. Bind registers or attaches the netdev, assigns a string and interface ID, autoconfigures bulk endpoints, mirrors endpoint addresses to HS/SS descriptors, assigns descriptor copies, and increments bind count. `set_alt()` only accepts alt 0 on the single interface; it disconnects any old session, configures speed-appropriate endpoints if needed, sets `is_zlp_ok` and default filter, and calls `gether_connect()`.

`eem_wrap()` prepends a two-byte EEM data header and appends an Ethernet FCS. It uses the sentinel `0xdeadbeef` CRC form and appends a zero-length EEM packet when needed to avoid USB ZLP ambiguity. `eem_unwrap()` parses one or more EEM packets from a received USB transfer. Data packets are CRC-checked, stripped of FCS, copied with `NET_IP_ALIGN`, and queued to the network receive list. Command packets handle echo by cloning the payload and queueing an IN response; other command hints are ignored.

## State and Persistence
Per-instance persistent state is primarily the `u_ether` netdev/options and endpoint descriptors assigned during bind. Runtime RX parsing state is per-skb; echo responses allocate temporary USB requests, buffers, and `in_context` freed in `eem_cmd_complete()`. No class-specific control state is accepted via EP0; `eem_setup()` always stalls unsupported control requests.

## Dependencies and Integration Points
EEM depends on `u_ether` for netdev lifecycle and data path, `u_ether_configfs.h` for configfs attributes, CRC helpers for calculated EEM CRC validation, skb helpers for frame wrapping/unwrapping, and composite helpers for descriptor/string/interface/endpoint setup. Its wrap/unwrap callbacks are consumed by `u_ether` during USB network TX/RX.

## Risks
RX parsing handles multiple logical packets per USB transfer and must keep `skb_pull()` lengths exact after errors, echo commands, zero-length packets, and invalid CRCs. Echo response allocation occurs in atomic-ish receive context but uses `GFP_KERNEL` for `req->buf`, which is worth checking against call context expectations in surrounding `u_ether`. Sentinel CRC mode is used for transmitted packets; calculated CRC receive validation must accept both forms. ZLP avoidance depends on `in->maxpacket` being configured before wrapping.

## Test Signals
Test EEM frame TX/RX at FS/HS/SS, transfers containing multiple EEM packets, zero-length EEM padding, sentinel and calculated CRC packets, invalid headers/lengths/CRCs, echo command and completion cleanup, host disconnect while echo response is queued, suspend-like command hints, and configfs Ethernet attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/function/f_eem.c -->
