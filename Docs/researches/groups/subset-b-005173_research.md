# subset-b-005173 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-scan.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/rio-scan.c

## Purpose
Implements the basic RapidIO fabric enumeration and discovery method. In enumeration mode it claims the host lock, assigns destination IDs and component tags, creates `rio_dev`/`rio_net` objects, programs switch route tables, initializes error management, and enables port-write handling. In discovery mode it waits for a remote enumerator to set the discovered bit, reads already-assigned IDs/routes, and reconstructs the kernel device topology.

## Important APIs, types, and functions
`struct rio_id_table` is per-network enumeration state: a spinlocked bitmap plus a logical start ID. `rio_destid_alloc/reserve/free/first/next()` manage destination IDs. `rio_setup_device()` reads RapidIO config space, allocates `struct rio_dev` plus embedded switch storage, assigns component tags and destIDs, initializes route-table cache state, sets device names, attaches sysfs/device model state, and calls `rio_add_device()`. `rio_enum_peer()` and `rio_disc_peer()` are the recursive topology walkers. `rio_scan_alloc_net()` creates `struct rio_net` and optional enumeration state. `rio_enum_mport()` and `rio_disc_mport()` are exported through the local `struct rio_scan` registered by `rio_basic_attach()`.

## Control flow
Enumeration begins from `rio_enum_mport()`: reject repeated scans, set the local host lock and device ID, verify link activity, allocate a net, reserve the host destID, enable the local port, write the host component tag, allocate the next destID, then call `rio_enum_peer()`. Each peer access checks config-read reachability, arbitrates host locks against other enumerators, creates a device, and if it is a switch, programs routes back to the host and all previously allocated endpoints, walks active switch ports, recurses through them, and patches routes for newly found destIDs. After recursion it frees the last unused destID, updates missing routes across switches, releases locks, marks devices discovered/master, and enables port-write handling. Discovery begins from `rio_disc_mport()`, optionally waits up to `CONFIG_RAPIDIO_DISC_TIMEOUT`, allocates a net, reads the host destID, recursively follows switch route entries, and builds in-memory route caches.

## State and persistence
State is volatile kernel/device-model state. Persistent hardware-visible state is in RapidIO config CSRs: destination IDs, host locks, component tags, switch route tables, port lockout bits, port discovered/master bits, and port-write target CSRs. The file uses static counters `next_destid` and `next_comptag`; they are process/module global and assume one scan sequence at a time. `net->enum_data` owns the ID bitmap until `rio_scan_release_net()`.

## Dependencies and integration
Depends on RapidIO core helpers from `rio.c`/`rio.h`, Linux device model, config-space accessors from mport drivers, route ops supplied by switch drivers, and standard RapidIO register definitions. It is registered with `rio_register_scan(RIO_MPORT_ANY, &rio_scan_ops)` at `late_initcall`; the `scan` module parameter can trigger `rio_init_mports()`.

## Risks
Recursive enumeration has little recovery granularity: failed recursion returns `-1` and can leave partially discovered devices/routes until higher-level cleanup. Global counters are not protected by a top-level scan lock. Route discovery assumes route-table contents identify the next device and may silently skip ports with no matching route. Several config reads ignore return values. Switch `port_ok` is bitmask-based and would be fragile if port counts exceed the bit width.

## Test signals
Exercise enumerator and discoverer roles, multi-host lock contention, inactive links, empty switches, redundant paths, mixed endpoint/switch fabrics, 8-bit versus 16-bit destID system sizes, route-table cache contents, port-write target programming, and sysfs/device-model registration/teardown after failed mid-scan paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/rio-sysfs.c

## Purpose
Provides RapidIO bus, device, and mport sysfs exposure. It publishes identity/topology attributes, a binary config-space accessor, a bus-level scan trigger, and master-port attributes.

## Important APIs, types, and functions
The `rio_config_attr()` macro defines read-only device attributes for DID/VID/revision/assembly/destID/hopcount fields. `routes_show()`, `lprev_show()`, and `lnext_show()` expose switch route cache and topology links. `modalias_show()` emits RapidIO modalias strings for driver matching. `rio_read_config()` and `rio_write_config()` implement the `config` bin_attribute using aligned 8/16/32-bit RapidIO config accesses. `scan_store()` parses a bus attribute write and calls `rio_init_mports()` or `rio_mport_scan()`. Exported arrays `rio_dev_groups`, `rio_bus_groups`, and `rio_mport_groups` plug into the RapidIO device model.

## Control flow
When a RapidIO device is registered, its attribute group is attached. `rio_dev_is_attr_visible()` hides switch-only attributes from endpoints. Config reads cap non-admin callers at 0x100 bytes because some chips lock up on undefined maintenance-space reads; CAP_SYS_ADMIN may read the full `RIO_MAINT_SPACE_SZ`. Both read and write paths trim requests to maintenance-space limits, consume unaligned leading bytes, then handle aligned words, tails, and return the adjusted byte count. Writing the bus `scan` attribute with `-1` scans all mports; otherwise a validated mport number scans one port.

## State and persistence
The sysfs files are views over live `struct rio_dev` and `struct rio_mport` state plus hardware config space. Writes to the `config` bin file persist only in target device CSRs/registers; this file keeps no private persistent state.

## Dependencies and integration
Depends on Linux sysfs/device APIs, capability checks, RapidIO object conversion helpers, and core scan functions declared in `rio.h`. The config bin attribute depends on mport-specific maintenance read/write methods underneath `rio_read_config_*` and `rio_write_config_*`.

## Risks
Config writes are privileged only by sysfs mode (`S_IWUSR`) and can change hardware state broadly. The route/topology text attributes assume `rdev->rswitch` and route cache validity when visible. `sprintf()` is used for attribute formatting, so unusually large route output relies on sysfs buffer size constraints rather than explicit bounds.

## Test signals
Check endpoint versus switch visibility, modalias content, admin/non-admin config read size behavior, unaligned config reads and writes, out-of-range scan requests, successful scan return count semantics, and mport `port_destid`/`sys_size` output after enumeration and discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio-sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/rio.c

## Purpose
Implements RapidIO core services: global device/net/mport registries, resource allocation for mailboxes and doorbells, port-write handling, memory window mapping, extended-feature discovery, route-table operations, optional DMA wrappers, scan registration, mport scanning, and mport lifecycle.

## Important APIs, types, and functions
Global state includes `rio_devices`, `rio_nets`, `rio_mports`, `rio_scans`, `rio_global_list_lock`, `rio_mport_list_lock`, and `rio_mmap_lock`. Public APIs include `rio_alloc_net/add_net/free_net`, `rio_add_device/del_device`, `rio_request/release_inb_mbox`, `rio_request/release_outb_mbox`, `rio_request/release_inb_dbell`, `rio_request/release_outb_dbell`, `rio_add/del_mport_pw_handler`, `rio_request/release_inb_pwrite`, `rio_pw_enable`, `rio_map/unmap_inb_region`, `rio_map/unmap_outb_region`, `rio_mport_get_physefb`, `rio_mport_get_efb`, `rio_mport_get_feature`, `rio_lock/unlock_device`, `rio_route_add/get/clr_table`, optional `rio_request_mport_dma`, `rio_dma_prep_xfer`, `rio_register_scan`, `rio_mport_scan`, `rio_init_mports`, `rio_mport_initialize`, `rio_register_mport`, and `rio_unregister_mport`.

## Control flow
Mport drivers initialize and register master ports; scan ops attach by exact mport ID or `RIO_MPORT_ANY`. Scans run enumeration if `host_deviceid >= 0`, otherwise discovery. Device and network add/remove paths register Linux devices and maintain global/per-net lists under spinlocks. Mailbox/doorbell request paths allocate `struct resource`, reserve the corresponding resource tree, attach callbacks, and call mport driver open/close hooks. Route operations optionally take the RapidIO host lock, then serialize on the switch lock, prefer switch-specific `rio_switch_ops`, and fall back to standard RapidIO route CSRs. Port-write handling resolves component tags, invokes per-device and per-mport callbacks, traces failed routes if the sender is inaccessible, performs switch error handling, toggles lockout on insertion/removal, clears ack/error status, and clears EM detect registers. Mport unregister transitions state, removes child devices, frees the net, removes the mport from the registry, and unregisters the device.

## State and persistence
Core state is in kernel lists, Linux resources, callbacks, refcounts, mport state, switch route caches, and hardware CSRs. Module parameter `hdid[]` supplies host destID assignment. Hardware-persistent actions include mailbox/doorbell setup by mport drivers, port-write enablement, route table writes, lockout bits, ack status updates, and memory window mappings.

## Dependencies and integration
Integrates with `linux/rio.h`, `rio_drv.h`, mport operation tables, RapidIO bus/classes, switch drivers, DMAEngine when enabled, Linux resources, workqueues, and module reference management through `try_module_get()` around scan and switch ops.

## Risks
Some legacy APIs return generic `-1` instead of errno. Several hardware access paths assume successful config reads. Port-write recovery is partly generic and explicitly not universal for all switches. Resource callback arrays are indexed by caller-supplied mailbox IDs and rely on upper-layer validation. The scan workqueue holds the mport list mutex while flushing discovery work, which deserves deadlock scrutiny if callbacks re-enter mport registration paths.

## Test signals
Validate mailbox/doorbell resource conflicts and cleanup, mport scan registration precedence, enumeration/discovery dispatch, switch-specific and standard route ops, port-write insertion/removal/error-stopped recovery, mport unregister cleanup of child devices and nets, DMAEngine wrappers under `CONFIG_RAPIDIO_DMA_ENGINE`, and behavior with absent mport operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio.h -->
# sources/distributed-fs/ceph-client/drivers/rapidio/rio.h

## Purpose
Internal RapidIO core header shared by the core, scan, sysfs, and switch drivers. It declares non-public core helpers and exports the sysfs attribute group arrays used by bus/device registration.

## Important APIs, types, and functions
Defines `RIO_MAX_CHK_RETRY`, `RIO_MPORT_ANY`, `RIO_GET_DID(size, x)`, and `RIO_SET_DID(size, x)` for base versus extended destID encoding. Declares feature-walk helpers, device access checking, host lock/unlock, route add/get/clear, port lockout, component-tag lookup, net/device add/remove, RX/TX port enabling, scan registration, device attachment, and mport scan. Also declares `rio_dev_groups`, `rio_bus_groups`, and `rio_mport_groups`.

## Control flow
This file has no executable control flow. Its declarations define the private call graph used by `rio-scan.c`, `rio-sysfs.c`, `rio.c`, and `switches/*.c`. The destID macros centralize the conditional 8-bit or 16-bit packing used whenever code reads or writes `RIO_DID_CSR`.

## State and persistence
No state is stored here. The macros affect how hardware destination ID state is interpreted and written.

## Dependencies and integration
Includes `linux/device.h`, `linux/list.h`, and `linux/rio.h`. It is intentionally not a public userspace ABI; it links internal compilation units in the RapidIO subsystem.

## Risks
The prototypes must stay synchronized with implementations in `rio.c`; mismatches can cause build failures or subtle ABI changes for in-tree callers. Incorrect `RIO_GET_DID`/`RIO_SET_DID` use would corrupt destID programming in mixed 8-bit/16-bit systems.

## Test signals
Build coverage across RapidIO core and switch drivers, plus enumeration tests on both `sys_size` modes, are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio_cm.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/rio_cm.c

## Purpose
Provides the RapidIO Channelized Messaging character device (`/dev/rio_cm`). It maps userspace ioctl operations onto RapidIO data-message mailboxes, with connection-oriented channel IDs, accept/connect handshakes, send/receive queues, endpoint discovery lists, mport lists, and teardown on device/mport removal or reboot.

## Important APIs, types, and functions
Core types are `struct cm_dev` for one local mport, `struct rio_channel` for each local channel, `struct chan_rx_ring` for queued/in-use receive buffers, `struct cm_peer` for reachable endpoints, and packet headers `rio_ch_base_bhdr`/`rio_ch_chan_hdr`. Global state includes `ch_idr`, `idr_lock`, `cm_dev_list`, `rdev_sem`, the cdev/class objects, and module parameters `cmbox` and `chstart`. Main operations include `riocm_ch_alloc/create/free/close`, `riocm_ch_bind/listen/accept/connect/send/receive`, `riocm_post_send`, `riocm_queue_req`, inbound work handler `rio_ibmsg_handler`, outbound completion `rio_txcq_handler`, ioctl dispatcher `riocm_cdev_ioctl`, RapidIO bus interface add/remove hooks, mport class interface add/remove hooks, and reboot notifier `rio_cm_shutdown()`.

## Control flow
Module init registers a class, chrdev region, mport class interface, RapidIO bus subsystem interface, reboot notifier, and cdev. Adding an mport allocates `cm_dev`, reserves inbound/outbound mailbox `cmbox`, creates an RX workqueue, pre-posts 128 inbound buffers, and publishes it. Adding a capable endpoint records it as a peer for the matching mport. Userspace creates a channel, binds it to an mport, listens or connects, and then sends/receives. Connect sends `CM_CONN_REQ`, waits up to `RIOCM_CONNECT_TO`, and transitions to connected on `CM_CONN_ACK`. Accept waits on the listening channel completion, allocates a new channel, matches the peer, sends ACK, and returns the new channel ID. Inbound mailbox callbacks queue work; the work handler drains messages, dispatches control packets or enqueues data to the channel RX ring. TX completions advance ring accounting and flush queued request packets.

## State and persistence
All state is volatile. Channel IDs live in an IDR and are file-descriptor-owned. RX buffers are tracked in both mport-level inbound rings and per-channel queued/in-use arrays. Removal paths close affected channels and free peers, mailboxes, workqueues, and buffers. The reboot notifier sends close packets for connected channels but does not persist metadata.

## Dependencies and integration
Depends on RapidIO mailbox APIs from `rio.c`, RapidIO bus and mport classes, `linux/rio_cm_cdev.h` ioctl ABI, IDR, krefs, completions, workqueues, cdev, reboot notifiers, and endian conversion helpers. Endpoint capability is determined by `RIO_SRC_OPS_DATA_MSG` and `RIO_DST_OPS_DATA_MSG`.

## Risks
The send path assumes mport `add_outb_message()` copies the buffer immediately; direct-buffer mport implementations could cause use-after-free. `cm_ep_get_list()` copies `info[0] + 2` entries even when only `nent + 2` were allocated, a notable bounds risk if user-requested count exceeds current peer count. Channel close/free uses `comp_close` and manual kfree after kref completion, making refcount sequencing important. The ioctl ABI trusts user-provided buffer sizes for receive truncation and does not return actual message length. TX accounting depends on hardware completion slot order.

## Test signals
Run ioctl create/bind/listen/accept/connect/send/receive/close flows, nonblocking and timeout waits, peer and mport hot-remove, reboot notifier, mailbox full and queued control-packet behavior, TX completion wraparound, invalid destIDs/mport IDs/channel ownership, receive ring full/in-use full cases, and memory-safety tests around endpoint-list copy sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/rio_cm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/rapidio/switches/Kconfig

## Purpose
Defines Kconfig symbols for optional RapidIO switch-family drivers under the RapidIO subsystem.

## Important APIs, types, and functions
Symbols are `RAPIDIO_CPS_XX` for IDT CPS-16/12/10/8 Gen1 switches, `RAPIDIO_CPS_GEN2` for IDT CPS Gen2 switches, and `RAPIDIO_RXS_GEN3` for IDT RXS Gen3 switches. All are `tristate`, allowing built-in, module, or disabled builds.

## Control flow
Kconfig has no runtime control flow. The selected symbols drive object inclusion through the sibling Makefile and decide whether the corresponding `rio_driver` registration code is compiled.

## State and persistence
No runtime state. The configuration persists in the kernel `.config`.

## Dependencies and integration
This file is normally sourced from a higher-level RapidIO Kconfig. The symbols integrate with `drivers/rapidio/switches/Makefile`.

## Risks
The help text contains vendor/product spelling issues (`ITD`) but no functional risk. There are no explicit `depends on RAPIDIO` guards here, so correct sourcing context matters.

## Test signals
Build matrix for each symbol as module and built-in; confirm only the expected object is compiled and the switch driver registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/Makefile -->
# sources/distributed-fs/ceph-client/drivers/rapidio/switches/Makefile

## Purpose
Maps RapidIO switch Kconfig symbols to their driver objects.

## Important APIs, types, and functions
`obj-$(CONFIG_RAPIDIO_CPS_XX) += idtcps.o`, `obj-$(CONFIG_RAPIDIO_CPS_GEN2) += idt_gen2.o`, and `obj-$(CONFIG_RAPIDIO_RXS_GEN3) += idt_gen3.o`.

## Control flow
No runtime flow. Kbuild includes objects based on `.config`.

## State and persistence
No runtime state; build output depends on configuration.

## Dependencies and integration
Integrates directly with `switches/Kconfig` and the RapidIO core symbols used by each object.

## Risks
Misaligned symbol names would silently omit a driver; current names match Kconfig.

## Test signals
Kernel build with each switch option toggled and module alias/probe availability for the selected object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen2.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen2.c

## Purpose
RapidIO switch driver for IDT CPS Gen2 devices. It supplies switch-specific route-table operations, domain configuration, error-management initialization/handling, and an `errlog` sysfs attribute.

## Important APIs, types, and functions
`idtg2_route_add_entry/get_entry/clr_table()` implement route programming using local route-table select and standard route CSRs, translating `RIO_INVALID_ROUTE` to device default/no-route values. `idtg2_set_domain/get_domain()` access `IDT_RIO_DOMAIN`. `idtg2_em_init()` configures port-write based error reporting across LT, port, lane, auxiliary, and config-block facilities. `idtg2_em_handler()` clears implementation-specific L/T and port error records. `idtg2_show_errlog()` drains `IDT_ERR_RD` into sysfs. `idtg2_probe/remove()` attach/detach `idtg2_switch_ops` and create/remove sysfs state.

## Control flow
The driver registers a `rio_driver` at `device_initcall`. Probe takes the switch lock, refuses to replace existing ops, stores `idtg2_switch_ops`, disables default routing during enumeration, releases the lock, and creates `errlog`. Core enumeration and route APIs call these ops through `rio_route_*()` and `rio_init_em()`. Removal verifies the ops pointer before clearing it and removing sysfs.

## State and persistence
Persistent hardware state includes route tables, default route behavior, switch domain, port-write/error-reporting enable bits, log-overwrite policy, TVAL, and cleared error capture registers. Kernel state is limited to the ops pointer and sysfs attribute.

## Dependencies and integration
Depends on RapidIO core switch ops, IDT device IDs, config-space accessors, delay helpers, and the Linux device attribute API. It is selected by `CONFIG_RAPIDIO_CPS_GEN2`.

## Risks
Sysfs `errlog` reads consume the hardware log. Error init writes many broadcast and per-port/per-lane implementation-specific registers and assumes Gen2 layout and lane count by DID. Route clear only covers 8-bit extended config entries. Probe creates sysfs after releasing the switch lock and does not unwind ops if sysfs creation fails.

## Test signals
Probe/remove on all IDs, route add/get/clear including invalid routes and per-port tables, domain set/get, enumeration default-route disable, EM initialization register writes, implementation-specific error clearing, and `errlog` behavior with empty and full logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen3.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen3.c

## Purpose
RapidIO switch driver for IDT RXS Gen3 devices. It provides Gen3 route-table operations, hot-swap/error port-write setup, Gen3-specific error handling, and shutdown mitigation for repeated port-write generation.

## Important APIs, types, and functions
`idtg3_route_add_entry/get_entry/clr_table()` program broadcast or per-port L2 route table entries and translate invalid routes to `RIO_RT_ENTRY_DROP_PKT`. `idtg3_em_init()` disables interrupts, suppresses port writes during setup, enables OK-to-uninitialized and link-init notifications on usable ports, routes port writes to the ingress port, re-enables port writes, and sets TVAL. `idtg3_em_handler()` soft-resets a port to clear error-stopped bits on insertion. `idtg3_shutdown()` disables port-write transmission if this enumerator is the configured target. Probe attaches ops and disables hierarchical routing during enumeration.

## Control flow
The driver registers a `rio_driver` at device init. Route ops validate 8-bit destination IDs and table bounds. Global route writes use broadcast registers because the hardware lacks a dedicated global table; global reads use the ingress port table. Core port-write handling invokes `em_handle()` before generic error processing. Shutdown runs from the RapidIO driver shutdown callback and only affects enumerator-owned devices.

## State and persistence
Hardware state includes L2 route table entries, hierarchical routing control, EM port-write TX control, per-port event enables, port-write route, soft reset bits, and optional shutdown disabling of port-write TX. Kernel state is the switch ops pointer.

## Dependencies and integration
Depends on RapidIO core switch ops and error-management flow, IDT RXS device IDs, and Gen3 register layout. Selected by `CONFIG_RAPIDIO_RXS_GEN3`.

## Risks
Only route destIDs up to 0xff are supported despite wider RapidIO systems. The error handler intentionally treats link-up error-stopped as insertion and uses soft reset; comments note this is not sufficient for all cable-down/up cases requiring full ackID realignment. Shutdown parses 8-bit/16-bit destID target fields and must match hardware encoding.

## Test signals
Route add/get/clear for global and per-port tables, invalid destID/table rejection, probe disabling hierarchical routing, EM init on ports with and without `PORT_UA`, soft reset on error-stopped insertion, no-op on removal, and shutdown disabling port-write TX only when the host destID matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/idt_gen3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/idtcps.c -->
# sources/distributed-fs/ceph-client/drivers/rapidio/switches/idtcps.c

## Purpose
RapidIO switch driver for IDT CPS Gen1/CPS-xx switches. It supplies route-table and switch-domain operations for older IDT devices.

## Important APIs, types, and functions
`idtcps_route_add_entry/get_entry/clr_table()` access standard route destination/port select CSRs, while preserving upper bits of the port-select register on add. `CPS_DEFAULT_ROUTE` and `CPS_NO_ROUTE` are translated to `RIO_INVALID_ROUTE` for core route caches. `idtcps_set_domain/get_domain()` access `IDTCPS_RIO_DOMAIN`. `idtcps_probe/remove()` attach/detach `idtcps_switch_ops`.

## Control flow
Probe registers `idtcps_switch_ops` under the switch lock if no ops are already attached. During enumeration, it sets link timeout TVAL and disables default routing by writing `CPS_NO_ROUTE`. Core route APIs and enumeration then invoke the driver-specific ops. Removal clears the ops pointer only if it still points to this driver.

## State and persistence
Hardware state includes route table entries, default route configuration, switch domain, and TVAL. Kernel state is the switch ops pointer.

## Dependencies and integration
Depends on RapidIO core switch ops, IDT Gen1 device IDs, and config-space access helpers. Selected by `CONFIG_RAPIDIO_CPS_XX`.

## Risks
Route clear is fixed to 8-bit entries `0x80000000..0x800000ff`, so it is not a full 16-bit route-table clear. There is no device-specific EM support. Probe assumes `phys_efptr` is valid when setting TVAL.

## Test signals
Probe/remove on every ID, route add/get/clear default/no-route translation, domain set/get, enumeration startup default-route disable, and route behavior in fabrics using Gen1 switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rapidio/switches/idtcps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ras/Kconfig

## Purpose
Top-level Kconfig menu for Reliability, Availability, and Serviceability features.

## Important APIs, types, and functions
Defines `menuconfig RAS` with explanatory help text. When enabled, it sources `arch/x86/ras/Kconfig` and `drivers/ras/amd/atl/Kconfig`, and defines `RAS_FMPM`, a tristate FRU Memory Poison Manager depending on `AMD_ATL && ACPI_APEI` and defaulting to module.

## Control flow
No runtime control flow. The `if RAS` block gates submenus and the FMPM symbol.

## State and persistence
Configuration persists in the kernel `.config`. Runtime persistence described here belongs to FMPM, which stores memory poison information through ACPI ERST in UEFI CPER FRU Memory Poison section format.

## Dependencies and integration
Integrates architecture RAS options, AMD ATL, ACPI APEI, and the RAS Makefile. `RAS_FMPM` depends on AMD address translation because poison records need platform-specific address conversion.

## Risks
Disabling `RAS` hides all nested features, including AMD ATL and FMPM. Defaulting FMPM to module when dependencies are met may surprise minimal builds.

## Test signals
Kconfig visibility and dependency tests for `RAS`, `AMD_ATL`, and `RAS_FMPM`, plus build coverage with RAS disabled, built-in, and module-capable configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ras/Makefile

## Purpose
Build rules for the RAS driver subtree.

## Important APIs, types, and functions
Includes `ras.o` for `CONFIG_RAS`, `debugfs.o` for `CONFIG_DEBUG_FS`, `cec.o` for `CONFIG_RAS_CEC`, `amd/fmpm.o` for `CONFIG_RAS_FMPM`, and always descends into `amd/atl/` through `obj-y`.

## Control flow
No runtime flow. Kbuild selects objects from configuration. The unconditional `obj-y += amd/atl/` lets the ATL subdirectory Makefile decide whether to emit `amd_atl.o`.

## State and persistence
No runtime state.

## Dependencies and integration
Follows symbols from `drivers/ras/Kconfig` and nested AMD ATL Kconfig. Integrates common RAS core, debugfs support, corrected-error collector, FMPM, and AMD ATL.

## Risks
The unconditional subdirectory descent is safe only if nested Makefiles are properly config-gated; current ATL Makefile is gated by `CONFIG_AMD_ATL`.

## Test signals
Build with `RAS=n`, `DEBUG_FS=y/n`, `RAS_CEC=y/m/n`, `RAS_FMPM=m/y`, and `AMD_ATL=m/y` to verify object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Kconfig

## Purpose
Kconfig entries for the AMD Address Translation Library.

## Important APIs, types, and functions
`AMD_ATL` is a tristate depending on `AMD_NB`, `X86_64`, `RAS`, `AMD_NODE`, and `MEMORY_FAILURE`, default `N`. Help text positions it as a library for implementation-specific address translation needed for DRAM ECC and OS-based error handling on Zen systems. `AMD_ATL_PRM` depends on `AMD_ATL && ACPI_PRMT` and defaults to yes.

## Control flow
No runtime control flow. Symbol values decide whether `amd_atl.o` and optional PRM support are built.

## State and persistence
No runtime state in Kconfig; configuration persists in `.config`.

## Dependencies and integration
Connects AMD northbridge/node support, memory failure handling, ACPI PRMT, and RAS consumers such as FMPM or machine-check decoding.

## Risks
`AMD_ATL_PRM` uses `def_bool y`, so enabling ACPI PRMT with ATL automatically builds PRM integration. ATL is unavailable without `MEMORY_FAILURE`, which may limit translation consumers in configs that otherwise want address decoding.

## Test signals
Kconfig dependency/visibility tests across x86_64, RAS, AMD_NB, AMD_NODE, MEMORY_FAILURE, and ACPI_PRMT combinations, plus module and built-in builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Makefile

## Purpose
Build composition for the AMD Address Translation Library module/object.

## Important APIs, types, and functions
`amd_atl-y` is composed from `access.o`, `core.o`, `dehash.o`, `denormalize.o`, `map.o`, `system.o`, and `umc.o`. `amd_atl-$(CONFIG_AMD_ATL_PRM)` adds `prm.o`. `obj-$(CONFIG_AMD_ATL) += amd_atl.o` gates final output.

## Control flow
No runtime flow. Link order places low-level access/core/dehash/denormalize before map/system/umc and optional PRM.

## State and persistence
No runtime state.

## Dependencies and integration
Works with `drivers/ras/amd/atl/Kconfig`. The object composition matches prototypes in `internal.h`, where these compilation units share `df_cfg` and translation helpers.

## Risks
Missing any object breaks cross-file symbols such as `get_df_system_info()`, `get_address_map()`, or `convert_umc_mca_addr_to_sys_addr()`. Optional PRM code must remain fully guarded by `CONFIG_AMD_ATL_PRM`.

## Test signals
Build ATL as module and built-in, with and without `CONFIG_AMD_ATL_PRM`, and verify all cross-object symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/access.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/access.c

## Purpose
Provides serialized Data Fabric indirect register reads for AMD ATL. It abstracts FICAA/FICAD access, including legacy offsets and heterogeneous-node remapping.

## Important APIs, types, and functions
`df_indirect_mutex` serializes writes to the shared FICAA address register and reads from FICAD. `get_accessible_node()` maps logical node IDs to software-visible nodes on heterogeneous DF3.5 and DF4.5 systems. `__df_indirect_read()` performs the common read. Public internal helpers are `df_indirect_read_instance()` for instance-specific reads and `df_indirect_read_broadcast()` using instance ID `0xff`.

## Control flow
Callers pass node, function, register, instance ID, and result pointer. The code adjusts node visibility, bounds-checks against `amd_nb_num()`, fetches DF function 4 PCI device from `node_to_amd_nb(node)->link`, builds FICAA with optional instance enable, shifts register offset by two, chooses legacy or current FICAA/FICAD offsets from `df_cfg.flags.legacy_ficaa`, writes FICAA under mutex, then reads FICAD low.

## State and persistence
Only global state is the mutex and reads of `df_cfg`. Hardware-visible state is the transient FICAA selector write in PCI config space.

## Dependencies and integration
Depends on AMD northbridge helpers, PCI config accessors, `df_cfg` initialized by system discovery, and register field macros. Used by ATL system/map/UMC discovery code to read Data Fabric registers.

## Risks
Incorrect heterogeneous node mapping reads the wrong DF instance. FICAA/FICAD are shared registers, so missing mutex coverage would race; current function covers the pair. Only FICAD low is read, so future high-register users need extension. Bad `df_cfg.rev` or shift values can make node adjustment invalid.

## Test signals
Unit or hardware tests for legacy and current FICAA offsets, broadcast and instance reads, out-of-range nodes, missing DF function 4, heterogeneous DF3.5/DF4.5 mapping, and concurrent callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/core.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/core.c

## Purpose
Owns AMD ATL module initialization and the central normalized-address to system-physical-address pipeline.

## Important APIs, types, and functions
Defines global `struct df_config df_cfg __read_mostly`. `norm_to_sys_addr()` is the main translation entry. `add_base_and_hole()` and `remove_base_and_hole()` apply DRAM base and legacy MMIO hole adjustments. Helpers include `addr_over_limit()`, `legacy_hole_en()`, `get_base_addr()`, `late_hole_remove()`, and `check_for_legacy_df_access()`. `amd_atl_init()` detects supported CPUs/northbridges, initializes DF info, pins the module refcount, and registers `convert_umc_mca_addr_to_sys_addr` as the decoder.

## Control flow
Init matches SMCA or Zen CPUs, requires at least one AMD northbridge, sets legacy FICAA access based on family/model, calls `get_df_system_info()`, pins the module, and registers the decoder. Translation rejects unknown DF revision, seeds `addr_ctx`, checks legacy-hole prerequisites, determines node ID, finds the DRAM address map, denormalizes interleave bits, conditionally adds base/hole before or after dehash based on revision/mode, dehashes, then validates against DRAM limit.

## State and persistence
`df_cfg` caches system-wide Data Fabric revision, masks, shifts, number of maps, DRAM hole base, and flags. The registered RAS decoder persists until module exit, though the module increments its own refcount to discourage unload. No on-disk persistence.

## Dependencies and integration
Depends on x86 CPU feature matching, AMD northbridge/node helpers, ATL map/system/UMC functions, RAS decoder registration, module APIs, and memory failure/RAS configuration.

## Risks
Returning `-EINVAL` as `unsigned long` relies on consumers recognizing error-valued addresses. Translation correctness depends on complete `df_cfg` and map discovery from other files. Late versus early hole/base ordering is revision-sensitive. Forced unload is possible despite the self-refcount comment and would unregister the decoder.

## Test signals
Boot/init on unsupported CPUs, missing northbridge, legacy Family 17h/19h models, supported DF2/DF3/DF3.5/DF4/DF4.5 systems, hole-enabled maps with and without hole base, address over limit, and known normalized-to-SPA vectors per interleave mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/dehash.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/dehash.c

## Purpose
Reverses Data Fabric address hash bits after denormalization so ATL can produce a system physical address.

## Important APIs, types, and functions
`dehash_address()` dispatches by `ctx->map.intlv_mode`. Family-specific helpers are `df2_dehash_addr()`, `df3_dehash_addr()`, `df3_6chan_dehash_addr()`, `df4_dehash_addr()`, `df4p5_dehash_addr()`, and `mi300_dehash_addr()`. They inspect hash-control fields in `ctx->map.ctl`, compute expected hashed bits from address bits, and toggle interleave bits when needed.

## Control flow
No-hash modes and modes where hashing was already handled during coherent-station ID calculation return immediately. DF2/DF3/DF4 paths progressively fix channel select bits depending on channel count. DF3 six-channel handles three interleave bits with 2M/1G hash controls. DF4.5 builds a rehash vector from total channels and stripe size to decide which address bits need recalculation. MI300 loops over channel and die interleave bits, including 4K/64K/2M/1G/1T hash controls and MI300’s stack bit placement.

## State and persistence
No persistent state. The function mutates `ctx->ret_addr` in place and reads `ctx->map` plus global `df_cfg`-derived map fields populated elsewhere.

## Dependencies and integration
Depends on `internal.h`, bitfield macros, interleave mode definitions, and prior `denormalize_address()` execution. Called from `norm_to_sys_addr()`.

## Risks
Address bit formulas are hardware-specific and difficult to review by inspection. Unsupported modes return `-EINVAL`; newly introduced hardware modes must be added here or explicitly classified. Boolean calculations sometimes use raw `BIT_ULL` truth values, which is intentional but sensitive to type changes. Incorrect total channel/die metadata causes wrong bit toggles.

## Test signals
Golden-vector tests for each interleave/hash-control combination, especially DF3 COD modes, DF3 six-channel, DF4 socket interleaving, DF4.5 1K/2K stripe modes, and MI300 8/16/32 channel plus die interleave cases. Include unknown-mode negative tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/dehash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/denormalize.c -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/denormalize.c

## Purpose
Reconstructs address bits removed by AMD Data Fabric normalization, inserting coherent-station/channel/die/socket interleave information before dehashing.

## Important APIs, types, and functions
`denormalize_address()` is the dispatcher. Shared helpers compute destination fabric ID, make address gaps (`make_space_for_coh_st_id_*()`), derive coherent-station IDs (`get_coh_st_id_df2/df4/mi300()` and `calculate_coh_st_id()`), insert IDs, and translate physical-to-logical coherent station IDs including MI300 fixed mapping. Special algorithms are `denorm_addr_df3_6chan()`, `denorm_addr_df4_np2()`, and `denorm_addr_df4p5_np2()` with `struct df4p5_denorm_ctx`.

## Control flow
Power-of-two and common hashed modes convert physical to logical fabric ID, expand address bits to create gaps, calculate interleave/coherent-station ID, then insert it. DF3 six-channel computes high interleave bits and mod3 adjustments based on map size. DF4 non-power-of-two modes rebuild address groups for 3/5/6/10/12 channel interleaves and account for hash bit 8 locally. DF4.5 non-power-of-two modes initialize a context describing lost bits, modulo divisor, base denormalized address, divided high address, and target logical fabric ID; then `check_permutations()` enumerates all dropped remainders and lost-bit combinations, rehashes candidate SPAs, verifies logical fabric ID and re-normalized address, and keeps the highest valid SPA.

## State and persistence
No persistent state. Mutates `ctx->ret_addr` and sometimes `ctx->coh_st_fabric_id`. Temporary `df4p5_denorm_ctx` tracks candidate and resolved SPAs. Reads `df_cfg` masks/shifts and map remap arrays.

## Dependencies and integration
Depends on `internal.h` bit helpers, map metadata from `get_address_map()`, system masks in `df_cfg`, and `add_base_and_hole()`/`remove_base_and_hole()` from `core.c` for DF4.5 candidate verification. Called before `dehash_address()`.

## Risks
This is the highest-complexity ATL logic. DF4.5 permutation search can be expensive but bounded by small modulo/lost-bit counts. Selecting the highest valid SPA is a policy choice that should match hardware expectations. Physical-to-logical remap failures only debug-print and can feed an out-of-range value. Any mismatch in map fields, remap arrays, or hash controls produces silent wrong addresses unless golden vectors catch it.

## Test signals
Golden translations for every supported interleave mode, remap enabled/disabled, socket and die interleaving, MI300 fixed remap, DF3 six-channel edge cases, DF4 3/5/6/10/12 channel modes, DF4.5 1K/2K NP2 modes including multiple valid candidates, and unknown-mode error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/denormalize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/internal.h -->
# sources/distributed-fs/ceph-client/drivers/ras/amd/atl/internal.h

## Purpose
Private header for AMD ATL. It defines Data Fabric revision/mode enums, global configuration structures, address-map and translation context structures, cross-file prototypes, PRM hooks, bit manipulation helpers, debug helpers, and MI300 MCA address fields.

## Important APIs, types, and functions
Defines `enum df_revisions`, extensive `enum intlv_modes`, `struct df4p5_denorm_ctx`, `struct df_flags`, `struct df_config`, `struct dram_addr_map`, `struct addr_ctx_inputs`, and `struct addr_ctx`. Declares DF indirect access, system info, node determination, MI300 UMC info, address map lookup, denormalization, dehashing, UMC conversion, base/hole helpers, and optional `prm_umc_norm_to_sys_addr()`. Inline helpers `expand_bits()` and `remove_bits()` are central to address reconstruction.

## Control flow
No top-level runtime flow. Inline `expand_bits()` inserts a gap of `num_bits` at `bit_num`; `remove_bits()` removes an inclusive bit range. PRM fallback returns `-ENODEV` when `CONFIG_AMD_ATL_PRM` is disabled. Debug helpers standardize context-rich messages.

## State and persistence
Declares external global `df_cfg`, which persists for module lifetime and carries DF revision, masks, shifts, map count, hole base, and flags. Structures defined here hold per-map and per-translation transient state.

## Dependencies and integration
Includes Linux bitfield/bitops/RAS headers, AMD northbridge/node headers, and `reg_fields.h`. Used by every ATL compilation unit in the Makefile.

## Risks
Enums encode hardware-visible values and special software values; changes must preserve dispatch assumptions. `expand_bits()` and `remove_bits()` warn but do not fail on invalid bit ranges. Returning negative errno through unsigned address APIs appears in prototypes and must be handled consistently by callers. Cross-file prototypes need to track object composition in the Makefile.

## Test signals
Compile all ATL variants, unit-test `expand_bits()`/`remove_bits()` boundaries, validate enum dispatch coverage in denormalize/dehash/map code, test PRM disabled fallback, and verify structure fields are initialized before translation use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ras/amd/atl/internal.h -->
