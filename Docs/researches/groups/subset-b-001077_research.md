<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_msghandler.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_msghandler.c

Purpose: This is the IPMI core message router. It registers lower-level system-management interfaces, exposes BMC devices through the kernel driver model, creates upper-layer IPMI users, formats outbound local/IPMB/LAN/direct messages, demultiplexes inbound responses, commands, events, watchdog pretimeouts, and panic-time messages, and owns the retry/timeout machinery for remote IPMI traffic.

Important APIs, types, and functions: Exported APIs include `ipmi_smi_watcher_register`, `ipmi_smi_watcher_unregister`, `ipmi_validate_addr`, `ipmi_addr_length`, `ipmi_create_user`, `ipmi_destroy_user`, `ipmi_get_smi_info`, `ipmi_get_version`, `ipmi_set_my_address`, `ipmi_get_my_address`, `ipmi_set_my_LUN`, `ipmi_get_my_LUN`, `ipmi_get_maintenance_mode`, `ipmi_set_maintenance_mode`, `ipmi_set_gets_events`, `ipmi_register_for_cmd`, `ipmi_unregister_for_cmd`, `ipmb_checksum`, `ipmi_request_settime`, `ipmi_request_supply_msgs`, `ipmi_poll_interface`, `ipmi_add_smi`, `ipmi_unregister_smi`, `ipmi_smi_msg_received`, `ipmi_smi_watchdog_pretimeout`, `ipmi_alloc_smi_msg`, `ipmi_free_smi_msg`, `ipmi_free_recv_msg`, and `ipmi_panic_request_and_wait`. Core state lives in `struct ipmi_smi`, `struct ipmi_user`, `struct seq_table`, `struct cmd_rcvr`, `struct bmc_device`, channel/address tables, global watcher/interface lists, and the `ipmi_timer` timeout worker.

Control flow: Lower drivers call `ipmi_add_smi`, which initializes an `ipmi_smi`, starts the hardware handler, fetches device ID/GUID, registers or links a `ipmi_bmc` platform device, scans IPMI channels, adds sysfs attributes, inserts the interface in numeric order, and notifies watchers. Upper users call `ipmi_create_user`, then issue requests through `ipmi_request_settime` or `ipmi_request_supply_msgs`; `i_ipmi_request` allocates or consumes supplied message objects, validates address family, delegates formatting to system-interface/IPMB/IPMB-direct/LAN helpers, optionally allocates a sequence-table entry, and queues or sends the SMI message through the lower handler. Incoming lower-level completions enter `ipmi_smi_msg_received`, which appends to `waiting_rcv_msgs`, clears `curr_msg` when appropriate, and schedules `smi_work`. `smi_work` starts queued transmissions, calls `handle_new_recv_msgs`, delivers user callbacks, and dispatches watchdog pretimeout notifications.

Receive demux and retry behavior: `handle_one_recv_msg` distinguishes send-message acks, GET_MSG responses, READ_EVENT responses, direct-IPMB messages, and local BMC responses. Remote responses are matched through `intf_find_seq`; remote commands are delivered to users registered by `ipmi_register_for_cmd`; unclaimed IPMB/LAN/direct commands get invalid-command replies where possible. Events are copied to every event-listening user or queued up to `MAX_EVENTS_IN_QUEUE` when no listener exists. `ipmi_timeout_work` periodically requests events for event waiters, decrements maintenance timers, retries sequence-table messages through `smi_from_recv_msg`, and emits timeout completion responses after retries are exhausted.

State and persistence behavior: Most state is volatile kernel runtime state: interface/user refcounts, outstanding sequence slots, queued events, command receiver registrations, BMC identity cache, scanned channel medium/protocol data, maintenance-mode state, statistics, and sysfs links. Persistent external effects are driver-model `ipmi_bmc` devices, sysfs attributes and symlinks, exported module parameters, panic notifier registration, and SEL/event records written to a BMC during panic handling. Dynamic BMC identity is cached for `IPMI_DYN_DEV_ID_EXPIRY`; if GUID/product/device identity changes, the BMC device is unregistered and re-registered.

Dependencies and integration points: This file depends on `linux/ipmi.h` and `linux/ipmi_smi.h` for user and lower-handler contracts, platform bus registration for BMC devices, workqueues and timers for deferred processing, RCU for command receiver lookup, panic notifiers, sysfs/device attributes, IPMI protocol helpers such as `ipmi_demangle_device_id`, and lower-level handlers supplied by SI, PowerNV, SSIF, or other transports. The soft dependency on `ipmi_devintf` helps user-space character-device access load after the core router.

Risks and edge cases: The code is concurrency-sensitive across lower-driver callbacks, workqueues, timers, panic context, user destruction, SMI unregister, and RCU command receiver lookup. Sequence table reuse is guarded with sequence IDs, but wrong address/channel/netfn/cmd matching drops late responses. Memory pressure can defer inbound processing, event queues can overflow, and supplied panic/poweroff messages avoid allocation but require single-threaded run-to-completion assumptions. Maintenance and reset modes intentionally block or slow traffic. BMC registration unlocks around platform registration to avoid recursive sysfs callbacks, which makes its locking order important.

Test signals: Useful validation includes SMI add/remove with watcher callbacks, BMC sysfs identity refresh and GUID/product matching, user create/destroy with outstanding messages, local BMC command routing, IPMB/LAN/direct command and response paths, unclaimed command error replies, event listener and event-queue overflow behavior, retry and timeout completion paths, maintenance-mode command behavior, panic notifier run-to-completion sends, and leak warnings for SMI/receive message counters on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_msghandler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.c

Purpose: This helper creates software-described IPMI platform devices for discovery sources that do not already have a native device instance, especially hardcoded and hot-added SI devices and SSIF descriptors.

Important APIs, types, and functions: The exported `ipmi_platform_add` takes a platform device name, instance number, and `struct ipmi_plat_data`. It constructs `struct resource` entries for SI register windows and IRQs, constructs software-node properties such as `ipmi-type`, `i2c-addr`, `slave-addr`, `addr-source`, `reg-shift`, and `reg-size`, allocates a `platform_device`, attaches resources/properties, and adds it to the platform bus.

Control flow: SI platform data derives a resource count from the SI type: KCS/SMIC use two register resources, BT uses three, and invalid SI uses no register resource. Default register size and spacing are filled when missing. SSIF data emits an I2C address property and no SI register resources. If an IRQ is present, an IRQ resource is appended. Any failure after allocation drops the platform device with `platform_device_put`.

State and persistence behavior: The function creates runtime platform devices with managed software-node properties and optional resources. There is no filesystem persistence; state persists until the platform device is unregistered, usually by the hardcode/hotmod cleanup paths or by platform device removal.

Dependencies and integration points: It depends on `ipmi_plat_data.h` for the data contract, `ipmi_si.h` for SI type defaults and constants, the platform-device API, and the property-entry software-node API. Consumers include `ipmi_si_hardcode.c`, `ipmi_si_hotmod.c`, and firmware/platform discovery glue that wants the normal platform driver probe path.

Risks and edge cases: Invalid SI and SSIF devices intentionally have no resources, so consumers must rely on properties. `regspacing` is not emitted directly; it is represented by separated register resources, so callers must provide coherent `regsize`, `regspacing`, and address data. The property array is fixed-size and relies on the last zeroed entry for termination.

Test signals: Exercise KCS/SMIC/BT resource counts, invalid SI with no resources, SSIF property creation, IRQ appending, default register values, property visibility in platform probe, and error unwinding for resource/property/add failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.h

Purpose: This header defines the small platform-data contract used to synthesize IPMI platform devices from hardcoded, hotmod, and discovery paths.

Important APIs, types, and functions: `enum ipmi_plat_interface_type` distinguishes SI and SSIF platform devices. `struct ipmi_plat_data` carries interface type, SI type or SSIF marker, address space or SSIF interface number, base address, register spacing/size/shift, IRQ, slave address, and address-source metadata. `ipmi_platform_add` is declared as the constructor for such platform devices.

Control flow: The header has no executable flow. Its fields are consumed by `ipmi_platform_add`, then by platform probe paths that parse resources and software-node properties.

State and persistence behavior: The structure is caller-owned transient data. The long-lived state is created only after `ipmi_platform_add` copies fields into platform resources and device properties.

Dependencies and integration points: It includes `linux/ipmi.h` for `enum ipmi_addr_src`. It is shared by `ipmi_plat_data.c`, SI hardcode/hotmod helpers, and any platform-discovery code that fabricates IPMI devices.

Risks and edge cases: The comment-level field overloading is important: `type` and `space` mean different things for SI versus SSIF. Callers must zero-initialize the structure when leaving optional fields unset, because defaulting is done by the implementation. Bad address-source or register metadata can propagate into sysfs and duplicate-detection decisions.

Test signals: Compile-time users should cover both `IPMI_PLAT_IF_SI` and `IPMI_PLAT_IF_SSIF`, zero/defaulted register metadata, slave address propagation, and address-source propagation into created device properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_plat_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_powernv.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_powernv.c

Purpose: This is the PowerNV OPAL-backed IPMI SMI transport. It registers an IPMI system interface for device-tree nodes compatible with `ibm,opal-ipmi` and translates the generic IPMI SMI handler calls into OPAL `opal_ipmi_send` and `opal_ipmi_recv` operations.

Important APIs, types, and functions: `struct ipmi_smi_powernv` stores the OPAL interface ID, registered `ipmi_smi`, IRQ, spinlock, one outstanding `ipmi_smi_msg`, and reusable `opal_ipmi_msg` buffer. The SMI handler table supplies `start_processing`, `sender`, `request_events`, `set_run_to_completion`, and `poll`. Driver entry points are `ipmi_powernv_probe`, `ipmi_powernv_remove`, and the platform driver declared by `module_platform_driver`.

Control flow: Probe reads `ibm,ipmi-interface-id` and interrupt data from device tree, maps or requests an OPAL event IRQ, allocates an OPAL message buffer, and registers the SMI with `ipmi_register_smi`. Sends validate message size and minimum netfn/cmd bytes, reject concurrent outstanding requests with `IPMI_NODE_BUSY_ERR`, format the OPAL message, call `opal_ipmi_send`, and retain the generic message as `cur_msg`. Interrupts or polling call `ipmi_powernv_recv`, which reads OPAL response data, validates size and format version, fills `msg->rsp`, clears `cur_msg`, and hands the message to `ipmi_smi_msg_received`.

State and persistence behavior: The driver keeps exactly one in-flight request per interface and one reusable OPAL buffer protected by `msg_lock`. There is no persistent storage. Device state exists for the lifetime of the platform device and registered SMI.

Dependencies and integration points: It integrates with the IPMI message handler via `ipmi_register_smi`/`ipmi_unregister_smi`, with the PowerNV OPAL firmware ABI via `opal_ipmi_send`, `opal_ipmi_recv`, and `opal_event_request`, with OF matching, and with Linux IRQ mapping/request/free APIs.

Risks and edge cases: The one-request model means upper layers can observe node-busy when a second message arrives before OPAL completion. Receive errors synthesize generic IPMI error replies, while `OPAL_EMPTY` is treated as a non-event for polling. If OPAL returns an undersized or unknown-version message, the current message is not completed in those branches, so future sends can remain blocked until another successful/error receive path clears it. Remove unregisters the SMI then frees IRQ/mapping; outstanding OPAL request handling during removal is a key integration risk.

Test signals: Validate OF probe with missing properties, IRQ map fallback to OPAL event request, send length validation, busy behavior with a pending request, successful OPAL response translation, `OPAL_EMPTY` polling behavior, OPAL error-to-completion-code synthesis, remove-time `ipmi_unregister_smi`, and recovery from malformed OPAL responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_powernv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_poweroff.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_poweroff.c

Purpose: This module installs an IPMI-backed `pm_power_off` implementation. It watches for available IPMI SMIs, chooses a supported platform poweroff method, and sends the required IPMI command sequence during system powerdown or power-cycle requests.

Important APIs, types, and functions: The module registers an `ipmi_smi_watcher`, creates an IPMI user with `ipmi_create_user`, sends synchronous requests with `ipmi_request_wait_for_response`, sends run-to-completion shutdown requests with `ipmi_request_in_rc_mode`, and overrides/restores `pm_power_off`. Detection/poweroff pairs include ATCA, CPI1, vendor-specific chassis fallbacks, and standard chassis control. Parameters include `ifnum_to_use` and `poweroff_powercycle`; under procfs, `dev/ipmi/poweroff_powercycle` mirrors the latter.

Control flow: Initialization registers the power-cycle sysctl and watcher. When `ipmi_po_new_smi` sees a selected interface, it creates a user, sends Get Device ID, records manufacturer/product/capability/IPMI-version data, scans `poweroff_functions`, stores the selected callback, and replaces `pm_power_off`. `ipmi_poweroff_function` invokes the selected callback in run-to-completion mode. Removal or matching SMI disappearance destroys the user and restores the previous poweroff callback.

Poweroff behavior: ATCA detection uses PICMG address-info and can run an additional OEM graceful-restart hook for matching hardware. CPI1 uses slot and active-event-receiver queries, sends a hotswap-control request over IPMB, asserts reset, and sets power state. Chassis poweroff uses the IPMI chassis control command, optionally first trying power cycle and falling back to power down on error. Dell and HP compatibility detectors allow chassis control on older systems that do not advertise the chassis capability bit.

State and persistence behavior: Global module state records readiness, selected interface number, IPMI user pointer, previous `pm_power_off`, selected function, and cached Get Device ID fields. No data is persisted to disk. The externally visible persistent effect is the platform power state transition requested from the BMC.

Dependencies and integration points: It depends on the core IPMI user API, SMI watcher API, kernel PM `pm_power_off`, module parameters, optional proc sysctl registration, completions for normal synchronous requests, and polling/run-to-completion behavior for shutdown contexts where interrupts may be disabled.

Risks and edge cases: Global state is single-interface and not heavily locked, relying on watcher/module-parameter sequencing. The static halt message objects make shutdown requests intentionally single-threaded. If `ifnum_to_use` changes while ready, the code tears down the current user and attempts the requested interface. Overriding `pm_power_off` must be restored correctly on removal or SMI loss. Power-cycle requests may not be supported and fall back to power down. Shutdown-time polling assumes the lower driver can make progress without interrupts.

Test signals: Cover watcher registration with existing and later SMIs, interface filtering and parameter changes, Get Device ID short/error responses, each detector path, chassis power-cycle fallback, completion-based request waits, run-to-completion polling sends, `pm_power_off` replacement/restoration, SMI removal cleanup, and proc sysctl registration failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_poweroff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si.h

Purpose: This header is the internal contract between IPMI SI discovery/probe code and the base SI transport engine. It describes SI types, address spaces, register I/O callbacks, IRQ setup hooks, and add/remove/init/shutdown entry points for KCS, SMIC, BT, and platform-specific SI providers.

Important APIs, types, and functions: `enum si_type` names invalid, KCS, SMIC, and BT state-machine types. `enum ipmi_addr_space` distinguishes I/O port and memory-mapped register spaces. `struct ipmi_match_info` carries SI type matches. `struct si_sm_io` provides `inputb`/`outputb` callbacks, register mapping metadata, address source/info, setup/cleanup callbacks, IRQ callbacks, slave address, match info, and backing device. Externs include `ipmi_si_add_smi`, `ipmi_si_irq_handler`, IRQ helper functions, removal helpers, hardcode/hotmod/platform init and shutdown functions, optional PCI/LS2K/PARISC hooks, and generic port/memory setup.

Control flow: Discovery modules fill a `struct si_sm_io`, then call `ipmi_si_add_smi`. The SI engine chooses low-level KCS/SMIC/BT handlers, calls `io_setup`, probes the BMC, registers the SMI with the core message handler, and uses the callbacks in this structure for every state-machine byte access and IRQ lifecycle operation.

State and persistence behavior: The header itself is stateless. Runtime state is carried by each `si_sm_io` instance and copied into `struct smi_info` in `ipmi_si_intf.c`. Address source and address info become visible through sysfs and `ipmi_get_smi_info`.

Dependencies and integration points: It includes IPMI public headers, interrupt support, and platform-device support. It is consumed by SI core, hardcode/hotmod/platform discovery, LS2K, PCI, PARISC, and low-level I/O setup code.

Risks and edge cases: The state machine assumes `inputb`/`outputb` implement IPMI register semantics correctly, including regspacing/regsize/regshift handling. Optional setup functions must fill cleanup callbacks to avoid leaks. Conditional hooks compile to no-ops when platform support is disabled, so callers depend on the header's stubs for init/shutdown ordering.

Test signals: Compile configurations with and without PCI, LS2K, and PARISC; add SMIs using I/O and memory spaces; IRQ setup and cleanup; removal by device and by address/type; and `get_smi_info` propagation of source metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hardcode.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hardcode.c

Purpose: This module converts boot/module parameters into synthetic SI platform devices for systems where firmware discovery is absent or intentionally overridden.

Important APIs, types, and functions: Parameters include `type`, `addrs`, `ports`, `irqs`, `regspacings`, `regsizes`, `regshifts`, and `slave_addrs`, each capped by `SI_MAX_PARMS`. `ipmi_hardcode_init_one` builds `struct ipmi_plat_data` and calls `ipmi_platform_add`. `ipmi_hardcode_init` parses comma-separated SI type strings and creates one platform device per configured port or memory address. `ipmi_si_hardcode_exit` removes hardcoded devices by name, and `ipmi_si_hardcode_match` reports whether an address is already user-hardcoded.

Control flow: During SI init, `ipmi_hardcode_init` splits the `type` string in-place, then iterates over the four possible entries. Nonzero I/O ports generate `IPMI_IO_ADDR_SPACE` devices; nonzero memory addresses generate `IPMI_MEM_ADDR_SPACE` devices. Missing type defaults to KCS; invalid type logs a warning and skips that entry.

State and persistence behavior: Parameter arrays are static module state, some init-only. Created platform devices persist until `ipmi_si_hardcode_exit` removes all devices named `hardcode-ipmi-si`. There is no disk persistence.

Dependencies and integration points: It depends on module parameter parsing, `ipmi_plat_data` construction, `ipmi_platform_add`, and SI duplicate suppression in `ipmi_si_add_smi`, which gives hardcoded devices priority over firmware-specified devices at the same address.

Risks and edge cases: Arrays are independently counted, so partial parameter sets can leave default zero values for optional IRQ/register/slave fields. A single index can create both port and memory devices if both arrays contain entries. Type parsing mutates the initdata string. Duplicate hardcoded addresses are not filtered here; later SI add logic handles conflicts.

Test signals: Boot with KCS/BT/SMIC types, invalid type strings, port-only and memory-only entries, mixed register spacing/size/shift, IRQ and slave address propagation, hardcoded address matching, and cleanup removing only `hardcode-ipmi-si` platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hardcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hotmod.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hotmod.c

Purpose: This module implements the writable `hotmod` module parameter used to dynamically add or remove IPMI SI platform devices after module load.

Important APIs, types, and functions: `module_param_call(hotmod, hotmod_handler, ...)` binds writes to `hotmod_handler`. Parsing helpers are `parse_str`, `check_hotmod_int_op`, and `parse_hotmod_str`. Operations are `add` and `remove`; interface types are `kcs`, `smic`, and `bt`; address spaces are `mem` and `i/o`; options include `rsp`, `rsi`, `rsh`, `irq`, and `ipmb`. `hotmod_nr` generates add instance IDs.

Control flow: `hotmod_handler` duplicates and strips the input string, processes colon-separated operations, parses each comma-separated operation into `struct ipmi_plat_data`, then either creates a `hotmod-ipmi-si` platform device through `ipmi_platform_add` or removes a matching SI with `ipmi_si_remove_by_data`. On removal, it unregisters the platform device only if the returned device is a platform device named `hotmod-ipmi-si`.

State and persistence behavior: Dynamic devices persist in the platform bus until explicitly removed or until `ipmi_si_hotmod_exit` removes all hotmod devices by name. The atomic instance counter persists for the module lifetime. No disk state is stored.

Dependencies and integration points: It depends on kernel parameter writes, IPMI platform-data synthesis, SI remove-by-address/type, platform-device unregister, and normal SI probe/cleanup paths. It is designed as a runtime companion to hardcoded and firmware discovery.

Risks and edge cases: The parser mutates a duplicated input buffer and returns the original input length on success, as module parameter setters expect. Bad option syntax fails the whole write at the first invalid operation. Remove can target an SI by address/type even if the matching device was not hotmod-created, but it only unregisters platform devices with the hotmod name. `put_device(dev)` is called even when no device is found, relying on NULL-safe behavior.

Test signals: Write single and multiple colon-separated add/remove operations, invalid operations/types/address spaces/options, decimal and hex addresses, each optional register/IRQ/slave field, removal of existing hotmod devices, attempted removal of non-hotmod devices, and cleanup removing all remaining hotmod devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_hotmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_intf.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_intf.c

Purpose: This is the base IPMI System Interface transport driver for KCS, SMIC, and BT hardware. It owns SI discovery aggregation, low-level state-machine selection, timers, optional interrupts, optional `kipmi` polling threads, event/message flag handling, BMC global enable programming, OEM workarounds, sysfs statistics, and registration with the core IPMI message handler.

Important APIs, types, and functions: Exported or externally used entry points include `ipmi_si_add_smi`, `ipmi_si_irq_handler`, `ipmi_irq_finish_setup`, `ipmi_irq_start_cleanup`, `ipmi_std_irq_setup`, `ipmi_si_remove_by_dev`, and `ipmi_si_remove_by_data`. The main state is `struct smi_info`, which holds the generic `ipmi_smi`, selected low-level `si_sm_handlers`, `si_sm_io`, current/waiting messages, `si_intf_state`, flags, timers, IRQ status, event-buffer support, maintenance mode, stats, and optional thread. The IPMI core handler table is `handlers`, with sender, poll, request-events, run-to-completion, maintenance-mode, and shutdown callbacks.

Control flow: Discovery code calls `ipmi_si_add_smi` with a filled `si_sm_io`; duplicates are rejected or ACPI replaces SMBIOS where preferred. During module init, hardcode, platform, PCI, LS2K, and PARISC discovery hooks populate `smi_infos`, then interfaces with IRQs are initialized before polled ones. `try_smi_init` chooses KCS/SMIC/BT handlers, allocates state-machine data, sets up I/O, detects the interface, sends Get Device ID, applies OEM quirks, checks broken IRQ behavior, enables event buffers where possible, clears flags, adds sysfs attributes, and registers the SMI with `ipmi_register_smi`.

Runtime state-machine behavior: Upper-layer sends enter `sender`, which stores a single waiting message and starts processing unless run-to-completion mode is active. `smi_event_handler` drives the low-level state machine, handles completed transactions, starts queued messages, prioritizes ATTN flag fetches, fetches message queues and event buffers, clears watchdog pretimeout flags, and enters `SI_HOSED` on state-machine failure. Timer, IRQ, thread, poll, and flush paths all call this handler with appropriate locking and elapsed-time values.

Interrupts, events, and maintenance: `current_global_enables`, `start_check_enables`, and related helpers maintain receive/event interrupt and event-buffer bits, compensating for BMCs that cannot set or clear receive IRQ enables. When flags show receive-message, event-buffer, or watchdog data, the driver allocates SMI messages and fetches data for the core handler. In maintenance mode, the polling thread avoids long busy waits and event requests are suppressed.

State and persistence behavior: State persists for the lifetime of each SI device: I/O mapping, IRQ registration, timer/thread, event-buffer and IRQ-broken flags, OEM handler choices, stats, current message pointers, and sysfs attributes. There is no disk persistence. Created sysfs attributes expose type, interrupt status, timing counters, transaction counters, event counts, incoming message counts, and register parameters.

Dependencies and integration points: It depends on the KCS/SMIC/BT state-machine handlers from `ipmi_si_sm.h`, I/O setup functions for port/memory mappings, discovery modules declared in `ipmi_si.h`, the core IPMI SMI registration API, kernel timers, interrupts, kthreads, module parameters, sysfs attributes, and IPMI protocol constants for global enables, message flags, and Get Device ID parsing.

Risks and edge cases: The implementation assumes one waiting and one current message per SI. Locking around `si_lock`, IRQ callbacks, timers, and the polling thread must prevent reentrant state-machine access. Memory allocation failure while fetching queued BMC messages triggers interrupt-disable/re-enable choreography. Broken BMC interrupt enable semantics are detected by live commands and can force degraded polling behavior. `SI_HOSED` returns synthetic bus errors and delays recovery. OEM handlers are global/notifier based and can affect matching hardware-specific transactions.

Test signals: Validate KCS/SMIC/BT probe success/failure, duplicate discovery priority, IRQ and no-IRQ init order, timer-only and `kipmi` thread operation, send/receive completion, ATTN flag handling, event-buffer enable failure, watchdog pretimeout delivery, broken IRQ detection, run-to-completion flush, maintenance-mode behavior, sysfs stat updates, hosed-state recovery, device removal by dev/address, and full cleanup of timer/thread/IRQ/I/O resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_intf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_ls2k.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_ls2k.c

Purpose: This platform driver adapts the Loongson-2K BMC KCS register block to the generic IPMI SI engine by providing custom memory-mapped byte input/output callbacks and registering a KCS SMI for `ls2k-ipmi-si` devices.

Important APIs, types, and functions: Register constants describe LS2K FIFO heads/tails, KCS status/data/cmd registers, version register, write request/ack registers, and status bits. Version-specific callbacks are `ls2k_mem_inb_v0`, `ls2k_mem_inb_v1`, `ls2k_mem_outb_v0`, and `ls2k_mem_outb_v1`. `ipmi_ls2k_mem_setup` maps the resource and selects callbacks based on `LS2K_KCS_VERSION`; `ipmi_ls2k_probe` fills `struct si_sm_io`; `ipmi_ls2k_remove` removes by device; init/shutdown register or unregister the platform driver.

Control flow: Probe creates an SI KCS descriptor with custom `io_setup`, base address from the first platform resource, register spacing equal to resource size, and backing device pointer, then calls `ipmi_si_add_smi`. Setup maps the register region and chooses v0 or v1 accessors. Reads and writes emulate the KCS status/data register layout expected by the generic KCS state machine.

State and persistence behavior: The module tracks whether the LS2K platform driver was registered. Per-device state is the mapped I/O address stored in `si_sm_io`, which is unmapped by `ls2k_mem_cleanup`. There is no persistent storage.

Dependencies and integration points: It depends on platform devices named `ls2k-ipmi-si`, MMIO accessors, `FIELD_PREP`, and the generic SI engine. It does not expose a separate IPMI transport; it feeds a customized KCS byte-access layer into `ipmi_si_add_smi`.

Risks and edge cases: The v0 and v1 hardware protocols differ in FIFO/status semantics, so version misdetection would break KCS handshaking. Output callbacks drop writes if input-buffer state says the BMC is busy. Mapping uses resource size as register spacing, so platform resources must be accurate. Shutdown unregisters only if init marked the driver registered.

Test signals: Probe with valid/invalid resources, v0 and v1 version selection, status/data reads reflecting OBF/IBF/CMD bits, write dropping while IBF is busy, write request counter updates, successful integration with generic KCS detect/Get Device ID, remove-time unmap via SI cleanup, and init/shutdown idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_ls2k.c -->
