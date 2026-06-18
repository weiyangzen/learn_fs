# subset-b-001278 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon.c -->
## sources/distributed-fs/ceph-client/drivers/extcon/extcon.c

### Purpose
`extcon.c` implements the external connector provider core. It registers `/sys/class/extcon` devices, tracks per-cable attach state, exposes cable and mutual-exclusion metadata through sysfs, stores typed connector properties, and notifies consumers through raw notifier chains plus `KOBJ_CHANGE` uevents.

### Important APIs, Types, And Functions
The file centers on `struct extcon_cable`, the static `extcon_info[]` id/type/name table, global `extcon_class`, `extcon_dev_ids`, and `extcon_dev_list`. Exported APIs include `extcon_dev_allocate()`, `extcon_dev_register()`, `extcon_dev_unregister()`, `extcon_set_state()`, `extcon_get_state()`, `extcon_set_state_sync()`, `extcon_sync()`, property get/set/capability helpers, notifier registration helpers, `extcon_get_extcon_dev()`, OF lookup helpers, and `extcon_get_edev_name()`.

### Control Flow, State, And Persistence
Registration creates the class if needed, counts `supported_cable[]` entries, allocates an IDA id, allocates per-cable sysfs groups, optional mutual-exclusion attributes, per-device notifier heads, then `device_register()`s `extconN` and adds it to the global list. State is a `u32` bitmask protected by `edev->lock`. `extcon_set_state()` validates the cable id, checks mutual-exclusion masks, clears properties on detach, and updates the bit. `extcon_sync()` reads state under the spinlock, calls the per-cable and all-cable raw notifiers, builds `NAME=` and `STATE=` environment variables from sysfs renderers using an atomic page allocation, then sends a uevent outside the lock. Unregister removes the device from the global list, unregisters the device, frees IDA/sysfs/notifier allocations, and drops the device reference.

### Dependencies, Integration Points, Risks, And Test Signals
The implementation integrates the driver core class/device model, sysfs attribute groups, IDA allocation, OF phandle lookup, raw notifier chains, spinlocks usable from IRQ context, and provider definitions from `<linux/extcon-provider.h>`. Risks include the `SUPPORTED_CABLE_MAX` 32-bit state limit, raw notifier callbacks executing with no blocking-chain serialization, property capability bits being modified without the same lock used by get/set paths, malformed supported-cable IDs indexing `extcon_info[]`, and careful lifetime requirements around device unregister and global list lookup. Test signals include attach/detach uevents, per-cable `name` and `state` files, mutual-exclusion rejection with `-EPERM`, property reset on detach, notifier ordering, OF phandle deferral, registration failure unwind, and duplicate/late consumer lookup returning `-EPROBE_DEFER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon.h -->
## sources/distributed-fs/ceph-client/drivers/extcon/extcon.h

### Purpose
`extcon.h` is the private extcon core header. It defines the internal layout of `struct extcon_dev` used by the provider implementation while exposing only the fields that provider drivers may initialize before registration.

### Important APIs, Types, And Functions
The only concrete type is `struct extcon_dev`. User-initialized fields are `name`, `supported_cable`, and `mutually_exclusive`. Internal fields include embedded `struct device dev`, numeric `id`, global list `entry`, per-cable and all-cable raw notifier heads, `max_supported`, IRQ-safe `lock`, state bitmask, dynamic `device_type`/cable sysfs group storage, and mutual-exclusion sysfs attribute storage.

### Control Flow, State, And Persistence
The header has no executable code, but it documents the lifecycle contract enforced by `extcon.c`: provider drivers allocate/fill the public fields, `extcon_dev_register()` overwrites internal fields, and consumers should not mutate runtime state directly. The persisted runtime state is in-memory only: attached cable bits in `state`, notifiers registered in `nh`/`nh_all`, global list membership, and sysfs group allocations. `mutually_exclusive` uses bit masks over supported-cable indexes and must be 0-terminated.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on `<linux/extcon-provider.h>` for public extcon IDs and property definitions. It couples tightly to `extcon.c` allocation and free paths because the struct embeds dynamic sysfs group pointers rather than opaque private data. Risks include drivers treating internal fields as stable ABI, setting too many supported cables for the 32-bit mask, or misunderstanding `name` fallback semantics. Test signals are mainly build-time and provider registration behavior: initialized public fields survive registration, internal fields are reset, mutual-exclusion arrays terminate correctly, and unregister frees the dynamic members described here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/extcon/extcon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/firewire/Kconfig

### Purpose
This Kconfig file defines the Linux IEEE 1394 FireWire driver stack build options: core bus support, OHCI host controllers, SBP-2 storage, IP networking over 1394, the Nosy sniffer, and several KUnit suites for UAPI, packet, self-ID, OHCI, and device-attribute validation.

### Important APIs, Types, And Functions
The important symbols are `FIREWIRE`, `FIREWIRE_OHCI`, `FIREWIRE_SBP2`, `FIREWIRE_NET`, `FIREWIRE_NOSY`, and test symbols `FIREWIRE_KUNIT_UAPI_TEST`, `FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST`, `FIREWIRE_KUNIT_PACKET_SERDES_TEST`, `FIREWIRE_KUNIT_SELF_ID_SEQUENCE_HELPER_TEST`, and `FIREWIRE_KUNIT_OHCI_SERDES_TEST`. `FIREWIRE` selects `CRC_ITU_T`; protocol drivers depend on `FIREWIRE` plus their subsystem dependencies such as `SCSI` or `INET`.

### Control Flow, State, And Persistence
There is no runtime control flow, but these options decide which objects and test inclusions exist. The top menu depends on `PCI || COMPILE_TEST` because the core is not useful without a PCI controller in normal configurations. KUnit tests default to `KUNIT_ALL_TESTS` and build as tristate options tied to `FIREWIRE && KUNIT`.

### Dependencies, Integration Points, Risks, And Test Signals
This file integrates with the kernel configuration system and the local Makefile. Risks are build-matrix gaps: tests can be omitted if their symbols are not added to the Makefile, and protocol drivers can select impossible combinations if dependencies drift. Test signals include `FIREWIRE=m/y` builds, OHCI plus protocol modules, KUnit all-tests builds, COMPILE_TEST coverage, and absence of production-only dependencies from test options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/Makefile -->
## sources/distributed-fs/ceph-client/drivers/firewire/Makefile

### Purpose
The FireWire Makefile composes the kernel objects for the IEEE 1394 stack and wires Kconfig symbols to their built modules or built-in objects.

### Important APIs, Types, And Functions
`firewire-core-y` is built from `core-trace.o`, `core-card.o`, `core-cdev.o`, `core-device.o`, `core-iso.o`, `core-topology.o`, and `core-transaction.o`. Optional targets include `firewire-ohci.o`, `firewire-sbp2.o`, `firewire-net.o`, `nosy.o`, `init_ohci1394_dma.o`, and KUnit objects `uapi-test.o`, `packet-serdes-test.o`, `self-id-sequence-helper-test.o`, and `ohci-serdes-test.o`.

### Control Flow, State, And Persistence
There is no runtime state. Build-time control flows from `obj-$(CONFIG_...)` selections. The core module is a composite object, while protocol/controller modules are separate objects.

### Dependencies, Integration Points, Risks, And Test Signals
The Makefile must stay aligned with `Kconfig` and source-level conditional includes. One notable integration point is that `FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST` is not listed as a separate object because `device-attribute-test.c` is included directly by `core-device.c` under `#ifdef CONFIG_FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST`. Risks include missing an object in the composite core, stale KUnit wiring, or unresolved symbols if cross-file exports change. Test signals are successful modular and built-in links for each Kconfig combination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-card.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/core-card.c

### Purpose
`core-card.c` manages FireWire controller card lifetime and bus-management duties. It builds and updates local config ROMs, maintains the global card and descriptor lists, schedules bus resets, performs bus-manager contention and gap-count/root optimization, initializes controller state, and tears cards down through a dummy driver facade.

### Important APIs, Types, And Functions
Exports include `fw_compute_block_crc()`, `fw_core_add_descriptor()`, `fw_core_remove_descriptor()`, `fw_schedule_bus_reset()`, `fw_schedule_bm_work()`, `fw_card_initialize()`, `fw_card_add()`, `fw_core_remove_card()`, and `fw_card_read_cycle_time()`. Major state includes `card_mutex`, `card_list`, `descriptor_list`, `descriptor_count`, `tmp_config_rom`, global `config_rom_length`, delayed `br_work` and `bm_work`, card workqueues, card generation/node/gap/broadcast fields, and the dummy `fw_card_driver` template.

### Control Flow, State, And Persistence
Descriptor add/remove validates descriptor block lengths, adjusts global config ROM length, then regenerates ROMs for all live cards under `card_mutex`. `fw_card_add()` creates per-card high-priority freezable isochronous and async workqueues, generates a config ROM, calls the hardware driver's `enable()`, and links the card globally. `fw_schedule_bus_reset()` takes a card reference and queues `br_work`, which delays resets until two seconds after the last reset, sends a PHY config packet using the current gap count, then requests a short or long reset. `bm_work()` runs after topology changes, contends for bus-manager ownership through a compare-swap transaction to the IRM, chooses whether local node should become root, computes expected gap count from topology, requests PHY config plus reset when needed, enables cycle master, and allocates broadcast channel when local node is IRM. Removal disables link/contender bits, schedules reset, removes from `card_list`, swaps most driver callbacks to dummy fail-fast operations, drains workqueues, disables hardware, cancels transactions, destroys topology nodes under `card->lock`, waits for references, and destroys workqueues.

### Dependencies, Integration Points, Risks, And Test Signals
This file integrates controller drivers through `struct fw_card_driver`, topology state from `core-topology.c`, transactions from `core-transaction.c`, device broadcast updates from `core-device.c`, ISO resource management from `core-iso.c`, tracepoints, CRC-ITU-T, krefs, completions, and workqueues. Risks include lock ordering between `card_mutex`, `card->lock`, and transaction calls that temporarily drop locks; config ROM length overflow; delayed work reference leaks; races when switching to the dummy driver; repeated reset storms; and quirks around non-1394a IRMs. Test signals include descriptor add/remove updating live ROMs, bus reset coalescing and postponement, bus-manager election outcomes, gap mismatch forcing long reset, broadcast channel allocation, remove with pending async/iso work, and `fw_card_read_cycle_time()` returning `-ENODEV` after dummy driver switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-cdev.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/core-cdev.c

### Purpose
`core-cdev.c` implements the `/dev/fw*` character-device ABI for raw FireWire access. It lets userspace discover device/card state, read event records, submit asynchronous transactions, allocate inbound address regions, respond to requests, add local config-ROM descriptors, manage isochronous contexts and bus resources, mmap ISO buffers, send broadcast/stream/PHY packets, and receive PHY packets.

### Important APIs, Types, And Functions
The public integration point is `const struct file_operations fw_device_ops`. Core private types are `struct client`, `struct client_resource`, and resource wrappers for address handlers, outbound transactions, inbound transactions, descriptors, and ISO resources. Event wrappers cover bus resets, outbound responses, inbound requests, ISO interrupts, ISO-resource notifications, outbound PHY completions, and inbound PHY packets. Important functions include `fw_device_op_open/read/ioctl/mmap/release/poll()`, `ioctl_get_info()`, `ioctl_send_request()`, `ioctl_allocate()`, `ioctl_send_response()`, ISO ioctls, `ioctl_send_phy_packet()`, `fw_cdev_handle_phy_packet()`, and `fw_device_cdev_update/remove()`.

### Control Flow, State, And Persistence
Open resolves a `fw_device` by device number, rejects shutdown devices, initializes a client with event list, waitqueues, xarray resources, one optional ISO context, one optional mmap buffer, and list links. `GET_INFO` negotiates ABI version, copies config ROM under `fw_device_rwsem`, registers for bus reset events, and returns the initial reset snapshot. Resource-creating ioctls allocate a typed resource, register with core subsystems when needed, then store a handle in `resource_xa` under `client->lock`; release paths remove by handle and call the matching resource-specific cleanup. Outbound transactions allocate an event/resource object, copy user payload, send through `fw_send_request_with_tstamp()`, then completion removes the resource and queues a version-specific response event. Address allocations install `fw_address_handler`s; inbound requests become queued request events with handles, and userspace later sends responses or deallocating the handle sends conflict for non-FCP requests. ISO setup creates one context, maps pages either during `mmap()` or context creation, queues packet descriptors from userspace, starts/stops/flushes callbacks, and uses delayed `iso_resource_work()` to allocate/reallocate/deallocate IRM resources across bus generations. Release unregisters PHY/client-list links, destroys ISO context and buffer, freezes event/resource mutation with `in_shutdown`, waits for outbound transactions to flush, releases remaining resources, destroys xarray, drops queued events, and releases the client reference.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on UAPI layout in `<linux/firewire-cdev.h>`, `fw_device_xa`, `fw_device_rwsem`, core transaction/address/descriptor APIs, ISO buffer/context APIs, bus-reset updates from `core-device.c`, PHY packet routing from `core-transaction.c`, DMA mapping, compat pointer handling, xarrays, waitqueues, and poll semantics. Risks include userspace ABI compatibility across event versions, short-read response compatibility, copy_from_user/copy_to_user validation, xarray handle lifetime while completions race release, shutdown deadlocks if outbound transaction flushing misses a resource, only one ISO context/buffer per client, DMA direction chosen before or after mmap, FCP request fan-out with partial allocation failures, and local-node-only security checks for descriptor/PHY access. Test signals include open after unplug returning `-ENODEV`, event read/poll behavior, ABI version negotiation, send request completion with timestamps, inbound address allocation and response, FCP multi-handler delivery, bus reset events rescheduling ISO resources, mmap plus ISO queue boundary checks, release with pending resources, broadcast security boundary, and PHY packet send/receive on local nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-cdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-device.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/core-device.c

### Purpose
`core-device.c` implements FireWire device discovery, config-ROM parsing, sysfs attributes, driver matching, uevents, device/unit registration, rediscovery after bus resets, and shutdown. It bridges topology nodes into Linux `struct device` objects and child `fw_unit` devices bound by `fw_driver` ID tables.

### Important APIs, Types, And Functions
Exports include `fw_csr_iterator_init()`, `fw_csr_iterator_next()`, `fw_csr_string()`, `fw_bus_type`, `fw_device_enable_phys_dma()`, `fw_device_get_by_devt()`, `fw_device_set_broadcast_channel()`, `fw_node_event()`, `fw_device_rwsem`, `fw_device_xa`, `fw_cdev_major`, and `fw_workqueue`. Important helpers are `search_directory()`, `search_leaf()`, `get_modalias_ids()`, `unit_match()`, config-ROM attribute show functions, `read_config_rom()`, `create_units()`, `fw_device_init()`, `fw_device_refresh()`, and `fw_device_shutdown()`.

### Control Flow, State, And Persistence
`fw_node_event()` is called from topology handling under the card lock. Created or link-on nodes allocate a minimal `fw_device`, attach it to the node, and schedule delayed config-ROM reading. `read_config_rom()` reads the bus information block, recursively walks config-ROM directory/leaf references with generation-stable transactions, filters invalid out-of-ROM references, detects quirks, probes max speed, and publishes the copied ROM under `fw_device_rwsem`. `fw_device_init()` can revive a recently gone device if the new ROM matches the previous bus info/root header; otherwise it allocates an xarray minor, initializes `/dev/fw*`, installs dynamic sysfs attribute groups based on present ROM entries, registers the device, creates `fw_unit` children, transitions state from initializing to running, sets broadcast channel when applicable, and seeds randomness with GUID data. Refresh rereads the header, updates units and uevents if the ROM changed, or calls driver update callbacks if it did not. Destroy/link-off transitions running devices to gone and delayed shutdown, which removes cdev clients, unregisters units and the device, erases the xarray entry, and drops references.

### Dependencies, Integration Points, Risks, And Test Signals
The file integrates Linux driver core bus matching/probe/remove, FireWire transaction reads/writes, topology events, cdev update/remove hooks, bus manager broadcast channel setup, random pool seeding, sysfs binary/config attributes, xarray minors, and KUnit test inclusion. Risks include config-ROM parser bounds, device reuse based on partial ROM comparison, memory barriers around `node_id` and `generation`, delayed work racing unplug, sysfs attribute presence detection calling show methods with `buf == NULL`, and firmware quirks changing bus-manager behavior before full probing. Test signals include modalias generation for standard and legacy AV/C layouts, ROM text leaf trimming, unit creation/removal, config-ROM retry exhaustion, rediscovery after unplug/replug, root-node bus-manager rescheduling, broadcast channel read-test/write, and shutdown waking cdev readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-iso.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/core-iso.c

### Purpose
`core-iso.c` provides FireWire isochronous support: page-backed DMA buffers, driver-backed ISO context lifecycle and queueing, completion flushing, stop handling, and client-side IRM channel/bandwidth allocation.

### Important APIs, Types, And Functions
Exports include `fw_iso_buffer_init()`, `fw_iso_buffer_destroy()`, `__fw_iso_context_create()`, `fw_iso_context_destroy()`, `fw_iso_context_start()`, `fw_iso_context_queue()`, `fw_iso_context_queue_flush()`, `fw_iso_context_flush_completions()`, `fw_iso_context_stop()`, and `fw_iso_resource_manage()`. Internal helpers include `fw_iso_buffer_alloc()`, `fw_iso_buffer_map_dma()`, `fw_iso_buffer_lookup()`, `manage_bandwidth()`, `manage_channel()`, and `deallocate_channel()`.

### Control Flow, State, And Persistence
Buffer allocation bulk-allocates zeroed DMA32 pages and stores a page array; mapping creates one DMA mapping per page and records direction. Destroy unmaps all DMA addresses and releases pages. Context creation delegates to the card driver, then fills common metadata and emits tracepoints for outbound/single-receive/multichannel possibilities. Start, set-channels, queue, flush-queue, flush-completions, and stop are thin traced wrappers around card driver methods. Completion flush disables the context work item around the driver's flush callback; stop calls the driver then cancels work. Resource management uses compare-swap transactions to the IRM's bandwidth and channel registers, handling generation changes, 1394-1995 retry behavior, channel bit ordering, and rollback if bandwidth allocation fails after channel allocation.

### Dependencies, Integration Points, Risks, And Test Signals
This file depends on DMA mapping, page allocation, `struct fw_card_driver` ISO methods, transaction helpers, CSR register constants, tracepoints, and cdev mmap/ISO ioctls. Risks include DMA mapping unwind using the intended direction, noncontiguous buffer offset lookup edge cases, deadlock if flush/stop is called from the context work itself, generation-stale resource semantics, and IRM compare-swap contention. Test signals include buffer allocation failure unwind, mmap DMA map/unmap, transmit/receive/multichannel context creation, queue validation from cdev, completion flush from process context, stop canceling work, allocation/deallocation of high and low channel registers, bandwidth rollback, and `-EAGAIN` on stale generation allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-iso.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-topology.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/core-topology.c

### Purpose
`core-topology.c` turns self-ID packets from each bus reset into an in-memory FireWire node tree, compares new and old topologies, reports node lifecycle events, updates bus-manager inputs, and maintains the local topology map CSR payload.

### Important APIs, Types, And Functions
Exports are `fw_core_handle_bus_reset()` and `fw_destroy_nodes()`. Important helpers include `fw_node_create()`, `update_hop_count()`, `build_tree()`, `for_each_fw_node()`, `report_lost_node()`, `report_found_node()`, `move_tree()`, `update_tree()`, and `update_topology_map()`. The file operates on `struct fw_node` from `core.h` and card fields such as `local_node`, `root_node`, `irm_node`, `gap_count`, `beta_repeaters_present`, `color`, and `topology_map`.

### Control Flow, State, And Persistence
On bus reset, `fw_core_handle_bus_reset()` verifies generation continuity, destroys old nodes if needed, updates card generation/node/reset/bus-manager fields, then calls `build_tree()` under `card->lock`. `build_tree()` enumerates self-ID sequences, validates PHY IDs, parent/child counts, extended self-ID consistency, constructs nodes bottom-up from a stack, identifies local/root/IRM nodes, detects beta repeaters and gap-count mismatch, and computes max depth/hops. For first topology, `for_each_fw_node()` reports every node as created. For subsequent compatible topologies, `update_tree()` walks old and new trees in parallel, emits updated/link on/link off/initiated reset events, moves newly found subtrees into the persistent tree, and reports lost subtrees. After releasing the card lock, bus-manager work is scheduled and the topology map buffer is regenerated under its own lock.

### Dependencies, Integration Points, Risks, And Test Signals
The topology layer depends on PHY/self-ID decoding helpers, `fw_node_event()` from `core-device.c`, bus-manager work from `core-card.c`, transaction CSR topology map reads, krefs, and tracepoints. Risks include malformed self-ID sequences causing NULL topology, stack underflow, parent-count inconsistencies, color reuse bugs during graph traversal, generation discontinuity requiring full destruction, and `card->root_node` assumptions after a failed build. Test signals include self-ID sequence helper KUnit coverage, bus reset traces, create/update/destroy event ordering, link-on/link-off transitions, root and IRM detection, gap mismatch forcing bus-manager reset logic, beta repeater detection, and topology map CRC/generation changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-trace.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/core-trace.c

### Purpose
`core-trace.c` instantiates FireWire tracepoints. It defines `CREATE_TRACE_POINTS` before including `<trace/events/firewire.h>` so the trace event storage and metadata are emitted in the core module.

### Important APIs, Types, And Functions
The file includes packet and PHY header definition helpers used by trace event field decoders. When `TRACEPOINTS_ENABLED` is defined, it exports GPL tracepoint symbols for isochronous inbound single completions, inbound multiple completions, and outbound completions.

### Control Flow, State, And Persistence
There is no ordinary runtime control flow beyond tracepoint registration through the kernel tracing infrastructure at module load. The persistent effect is that all `trace_*` calls in the FireWire core resolve to concrete tracepoints.

### Dependencies, Integration Points, Risks, And Test Signals
This file must be built exactly once in `firewire-core-y`; otherwise tracepoints are either undefined or multiply defined. It integrates with tracing users, ISO completion providers, and packet serialization helpers. Risks are mostly build/linkage issues and trace event field drift when packet header definitions change. Test signals include successful core link, availability of FireWire trace events in tracefs, and external ISO drivers resolving exported tracepoint symbols when tracing is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-transaction.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/core-transaction.c

### Purpose
`core-transaction.c` implements FireWire asynchronous transaction logic and core CSR request handling. It sends requests, matches responses by source/tlabel, manages split transaction timeouts, handles inbound requests through registered address handlers, sends responses, emits PHY config packets, exposes standard CSR regions, registers core descriptors, and initializes the FireWire bus/character-device core.

### Important APIs, Types, And Functions
Exports include `fw_cancel_pending_transactions()`, `fw_cancel_transaction()`, `__fw_send_request()`, `fw_run_transaction()`, `fw_send_phy_config()`, `fw_core_add_address_handler()`, `fw_core_remove_address_handler()`, `fw_request_get()`, `fw_request_put()`, `fw_get_response_length()`, `fw_fill_response()`, `fw_send_response()`, `fw_get_request_speed()`, `fw_request_get_timestamp()`, `fw_core_handle_request()`, `fw_core_handle_response()`, and `fw_rcode_string()`. Important static state includes the global `address_handler_list`, `address_handler_list_lock`, `phy_config_mutex`, `phy_config_done`, static `phy_config_packet`, standard handlers for topology map/registers/low memory, and built-in vendor/model descriptors.

### Control Flow, State, And Persistence
Outgoing requests allocate one of 64 transaction labels under `card->transactions.lock`, fill stream or async packet headers, add the transaction to the card list, trace initiation, and delegate to the card driver. Transmit completion either closes immediate transactions, starts a split-timeout timer on `ACK_PENDING`, or maps ACK errors to rcodes. Responses parse payload pointers by response tcode, find and pop the matching transaction by source and tlabel, cancel any request packet still pending, then invoke the caller callback with or without timestamps. Cancellation first asks the driver to cancel queued packets, then removes pending transactions and reports `RCODE_CANCELLED`. Inbound requests are allocated into `struct fw_request`, copied when needed, traced, and dispatched either to an exclusive enclosing address handler or to every FCP handler for FCP command/response writes. Response send suppresses unified/broadcast responses, fills headers, holds an in-flight reference, and releases after driver completion. Module init creates `fw_workqueue`, registers `fw_bus_type`, registers the character-device major, installs topology/register/low-memory address handlers, and adds default config-ROM descriptors.

### Dependencies, Integration Points, Risks, And Test Signals
The transaction core depends on card driver packet operations, packet header serializers, PHY packet serializers, timers, RCU list traversal for address handlers, split-timeout card state, `core-cdev.c` for PHY packet forwarding, `core-card.c` descriptors, `core-device.c` bus type and cdev ops, and tracepoints. Risks include tlabel exhaustion, callbacks running before send returns, timer/list races around split transactions, stale generation/node-id pairs, local request callbacks in initiator context, address-handler remove waiting for in-flight callbacks, FCP fan-out allocation failure causing partial delivery, low-memory policy returning type errors, and init unwind not removing already added address handlers/descriptors on later failures. Test signals include immediate and split transaction completion, busy/data/type ACK mappings, timeout cancellation timestamps, unsolicited response logging, address allocation overlap and FCP exception, register CSR reads/writes for split timeout and broadcast channel, topology map reads, PHY config serialization/completion timeout, and module init/exit with cdev major cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core-transaction.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core.h -->
## sources/distributed-fs/ceph-client/drivers/firewire/core.h

### Purpose
`core.h` is the private cross-module header for the FireWire core. It declares card-driver operations, shared constants, internal function prototypes, topology node structures, helpers for tcode classification, and small inline utilities used across card, cdev, device, ISO, topology, and transaction files.

### Important APIs, Types, And Functions
The most important type is `struct fw_card_driver`, the controller-driver callback table for enable/disable, PHY register access, config ROM update, async packet send/cancel, physical DMA authorization, CSR access, and ISO context operations. The header also defines PHY/CSR constants, broadcast-channel defaults, `struct fw_node`, `fw_node_get/put()`, `fw_node_get_device/set_device()`, `fw_device_get/put()`, exported globals such as `fw_device_rwsem`, `fw_device_xa`, and `fw_cdev_major`, and prototypes for card, cdev, device, ISO, topology, and transaction entry points.

### Control Flow, State, And Persistence
There is little executable flow besides inline refcount helpers and classifiers. `fw_node` objects persist topology state across bus resets: node id, color, link/reset flags, beta path, speeds, hop/depth metrics, kref, tree/list links, optional associated `fw_device`, and flexible port pointers. Inline helpers establish conventions such as generation successor comparison with 8-bit wraparound, block/read/tlink-internal tcode classification, OHCI timestamp conversion, ping-packet detection, and FCP address range recognition.

### Dependencies, Integration Points, Risks, And Test Signals
This header couples all FireWire core compilation units and controller/protocol-facing internal APIs. Dependencies include Linux device, DMA, file operations, xarray, rwsem, refcount, slab, and FireWire public headers pulled by users. Risks include struct/callback contract drift between OHCI and core, inline `release_node()` being private but used by `fw_node_put()`, assumptions that `read_csr()` is not called after dummy driver replacement except best-effort checks, and generation wrap logic being central to stale-transaction handling. Test signals include full core build, OHCI implementing every required callback, topology refcounting under reset/removal, tcode helper behavior in packet tests, and correct cdev/device integration through declared globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/device-attribute-test.c -->
## sources/distributed-fs/ceph-client/drivers/firewire/device-attribute-test.c

### Purpose
`device-attribute-test.c` is a KUnit test file included directly by `core-device.c` when `CONFIG_FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST` is enabled. It validates FireWire device and unit sysfs attribute helpers and modalias ID extraction against simple and legacy AV/C configuration ROM layouts.

### Important APIs, Types, And Functions
The test data are `simple_avc_config_rom[]` and `legacy_avc_config_rom[]`. Test cases are `device_attr_simple_avc()` and `device_attr_legacy_avc()`, registered through `device_attr_test_cases` and `device_attr_test_suite`. The tests call internal static helpers from `core-device.c`, including `is_fw_device()`, `is_fw_unit()`, `fw_device()`, `fw_unit()`, `fw_parent_device()`, `show_immediate()`, `show_text_leaf()`, `config_rom_attributes[]`, and `get_modalias_ids()`.

### Control Flow, State, And Persistence
Each test builds static fake `fw_device` and `fw_unit` instances with the same device types used by production code and points them at an in-memory ROM. It allocates a page buffer, asserts type conversion helpers, checks immediate sysfs values and text leaf strings, frees the buffer, and verifies extracted modalias id arrays. The simple AV/C case expects root vendor/model text and unit specifier/version values. The legacy case checks a vendor directory layout where root/vendor/unit directories contribute different IDs and text leaf visibility.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on being textually included in `core-device.c` so it can access static functions and device types; it is intentionally not standalone. It integrates with KUnit and `FIREWIRE_KUNIT_DEVICE_ATTRIBUTE_TEST`. Risks include fragile coupling to `config_rom_attributes[]` ordering, static fake devices bypassing full device initialization, and ROM length comments using quadlets while production paths use byte lengths elsewhere. Test signals are direct: KUnit TAP output for `firewire-device-attribute`, expected sysfs strings, negative lookups for absent attributes, and modalias ID arrays for both AV/C layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/firewire/device-attribute-test.c -->
