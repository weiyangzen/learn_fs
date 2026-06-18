# Research Report: subset-b-005017

This grouped report covers PCI VPD support, Xen PCI frontend support, and the PCMCIA/CardBus core, CIS, resource, and selected socket-controller files. Each section is delimited for reconciliation into its source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/vpd.c -->
# sources/distributed-fs/ceph-client/drivers/pci/vpd.c

Purpose: Implements Linux PCI Vital Product Data access. It discovers the VPD capability, probes usable VPD size, exposes binary sysfs access, exports read/write helpers, allocates whole VPD buffers, parses VPD resource tags and keywords, checks checksums, and applies quirks for devices with shared or unsafe VPD storage.

Important APIs and functions: Public entry points are `pci_vpd_init()`, `pci_read_vpd()`, `pci_read_vpd_any()`, `pci_write_vpd()`, `pci_write_vpd_any()`, `pci_vpd_alloc()`, `pci_vpd_find_id_string()`, `pci_vpd_find_ro_info_keyword()`, and `pci_vpd_check_csum()`. The `pci_dev_vpd_attr_group` exposes the `vpd` bin attribute. Internal helpers include tag-size decoding, `pci_vpd_size()`, `pci_vpd_available()`, `pci_vpd_wait()`, and function-0 redirection helpers.

Control flow: Initialization caches the VPD capability offset and initializes the per-device mutex. Reads optionally compute `vpd->len` by walking large and short resource data tags until an end tag or invalid tag. VPD reads issue aligned 32-bit transactions by writing the address register, waiting for `PCI_VPD_ADDR_F`, and reading data; writes require 4-byte alignment, write data first, set address plus flag, and wait for the flag to clear. Sysfs access wraps runtime PM get/put and honors `PCI_DEV_FLAGS_VPD_REF_F0`.

State and persistence: Mutable state is in `dev->vpd`: `cap`, lazily discovered `len`, and `lock`. VPD content is device EEPROM or firmware-backed persistent data, so writes may persist across reboot. Quirks can permanently disable access by setting `PCI_VPD_SZ_INVALID`, extend reported length, or route nonzero functions through function 0.

Dependencies and integration points: Depends on PCI config-space accessors, runtime PM config protection, unaligned helpers, exported PCI symbols, sysfs bin attributes, and PCI fixup infrastructure. Consumers include PCI drivers that read asset fields or serials from VPD.

Risks: VPD hardware has no interrupt completion path and may hang or time out; timeout handling must avoid wedging config access. Size probing trusts VPD format enough to bound future sysfs accesses, so malformed devices require quirks. Writes are especially risky because the backing store may be EEPROM. Function-0 sharing must only apply to genuinely identical multifunction devices.

Test signals: Build with PCI VPD and quirks, read `/sys/bus/pci/devices/.../vpd`, verify reads at odd offsets and truncated EOF behavior, check 4-byte write alignment rejection, exercise `pci_vpd_alloc()` and checksum helpers, and confirm blacklisted or function-0-linked devices behave as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/vpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/xen-pcifront.c -->
# sources/distributed-fs/ceph-client/drivers/pci/xen-pcifront.c

Purpose: Provides the Xen PV PCI frontend for passthrough PCI devices in non-initial Xen domains. It registers a XenBus frontend named `pcifront`, creates guest PCI root buses backed by pciback operations, mediates config-space and MSI/MSI-X operations through a shared page and event channel, and handles backend-driven reconfiguration and AER callbacks.

Important APIs and types: Core state is `struct pcifront_device`, containing the xenbus device, root bus list, event channel, grant reference, IRQ, shared info page, work item, and flags. `struct pcifront_sd` extends `pci_sysdata` with a frontend pointer. Key functions are `do_pci_op()`, `pcifront_bus_read()`, `pcifront_bus_write()`, MSI/MSI-X frontend ops, `pcifront_scan_root()`, `pcifront_rescan_root()`, `pcifront_free_roots()`, `pcifront_do_aer()`, `alloc_pdev()`, `pcifront_publish_info()`, and XenBus state handlers.

Control flow: Module init refuses non-PV, dom0, or no-PV-device environments, registers MSI frontend ops, then registers with XenBus. Probe allocates a shared info ring, grants it to the backend, binds an event-channel IRQ, publishes `pci-op-ref`, `event-channel`, and magic in XenStore, and switches to Initialised. When the backend reaches Connected, the frontend scans roots from XenStore or defaults to `0000:00`, creates PCI root buses with `pcifront_bus_ops`, scans all devfns, claims backend-owned resources, and adds devices. Config access serializes via `sh_info_lock`, copies a `xen_pci_op`, marks it active, notifies the backend, polls for completion with a two-second guest timeout, and maps Xen PCI errors to PCIBIOS errors.

State and persistence: State is runtime-only: a global `pcifront_dev`, root bus list, XenBus state, shared op page, event channel/IRQ, AER work flag, and per-root `pcifront_sd`. Device enumeration persists in Linux PCI core until backend detach, frontend removal, or reconfiguration. Backend-provided PCI resources are claimed as-is rather than rebalanced.

Dependencies and integration points: Integrates with XenBus, grant tables, event channels, Xen shared PCI ABI, Linux PCI scanning/resource APIs, MSI frontend hooks, PCI AER error handlers, and Xen SWIOTLB/platform support. It is explicitly a frontend for a Xen pciback-style backend.

Risks: Shared-page operation ordering depends on barriers and flag discipline. Lost event-channel notifications are mitigated by polling but can still delay or fail config operations. Backend unresponsiveness is treated like device-not-found after timeout. Reconfiguration races with PCI device removal, AER work, and root-bus teardown need careful locking through PCI rescan/remove locks. Only one frontend is accepted globally.

Test signals: Boot a Xen PV guest with PCI passthrough, verify XenBus state transitions, config reads/writes, PCI device enumeration, resource claiming, MSI and MSI-X vector assignment, backend reconfiguration add/remove, AER callback propagation, and cleanup on backend Closing/Closed and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/xen-pcifront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/Kconfig

Purpose: Defines the Kconfig surface for the PCCard subsystem: core PCCard support, 16-bit PCMCIA, CardBus, CIS firmware loading, resource probing, bridge/socket drivers, and embedded CompactFlash/PCMCIA controller drivers.

Important APIs and symbols: Top-level `PCCARD` builds `pcmcia_core`. `PCMCIA` builds 16-bit services and selects `CRC32`; `PCMCIA_LOAD_CIS` selects `FW_LOADER`; `CARDBUS` depends on PCI. Socket/controller symbols include `YENTA`, `PD6729`, `PCMCIA_ALCHEMY_DEVBOARD`, `PCMCIA_BCM63XX`, `OMAP_CF`, `ELECTRA_CF`, SoC families, `PCMCIA_MAX1600`, and `PCCARD_NONSTATIC`.

Control flow: This file has no runtime logic. Its dependency graph controls which source files in the directory are compiled, whether CardBus code is included in `pcmcia_core`, whether CIS replacement firmware can be loaded, and whether non-static resource managers are available.

State and persistence: Persistent state is the kernel configuration. Defaults such as `PCMCIA=y`, `CARDBUS=y`, Yenta quirks, and `PCMCIA_LOAD_CIS=y` influence built kernels and modules.

Dependencies and integration points: Ties the PCMCIA directory to architecture symbols (`ARM`, `MIPS_DB1XXX`, `BCM63XX`, `PPC_PASEMI`, `ARCH_OMAP16XX`), bus facilities (`PCI`, `HAS_IOMEM`, `HAS_IOPORT`), and firmware/resource subsystems.

Risks: Wrong dependencies can expose drivers on unsupported architectures, omit helper objects selected by board drivers, or build CardBus without required PCI support. Defaults also matter because PCMCIA is legacy hardware and often only tested on niche platforms.

Test signals: Kconfig coverage includes `allyesconfig`, targeted builds for Yenta, BCM63XX, Alchemy, OMAP, Electra, and SA/PXA sockets, plus checks that selected helper modules appear in the linked objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/Makefile

Purpose: Describes how the PCMCIA subsystem objects are assembled into kernel modules and built-in objects. It groups core socket services, 16-bit driver services, resource managers, and board/socket controller drivers.

Important APIs and targets: `pcmcia_core-y` includes `cs.o` and `socket_sysfs.o`; `pcmcia_core-$(CONFIG_CARDBUS)` adds `cardbus.o`. The `pcmcia` module includes `ds.o`, `pcmcia_resource.o`, `cistpl.o`, and `pcmcia_cis.o`. `pcmcia_rsrc` combines `rsrc_mgr.o` and optional `rsrc_nonstatic.o`. Driver objects are selected by symbols such as `CONFIG_YENTA`, `CONFIG_PCMCIA_BCM63XX`, `CONFIG_OMAP_CF`, `CONFIG_ELECTRA_CF`, and `CONFIG_PCMCIA_MAX1600`.

Control flow: Build-time only. Kconfig selects symbols, kbuild links matching objects into modules or built-ins, and composite `*-y` variables define internal module composition.

State and persistence: The Makefile persists the binary/module boundaries. These boundaries affect exported symbols and load order: `pcmcia_core`, `pcmcia`, and `pcmcia_rsrc` are separate logical units.

Dependencies and integration points: Integrates with Kbuild and with the Kconfig symbols in this folder. The split mirrors runtime layering: socket core, driver services, resource manager, and host socket drivers.

Risks: Missing an object from a composite module can cause unresolved symbols only under specific configs. Moving files between modules must account for exported symbols between `pcmcia_core` and `pcmcia`.

Test signals: Build all major configurations as modules and built-in, verify `modpost` has no unresolved symbols or section mismatch warnings, and confirm selected socket drivers produce expected `.ko` names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.c

Purpose: Implements Broadcom BCM63xx PCMCIA/CardBus socket services. It registers either a platform socket driver or, with CardBus enabled, a PCI CardBus bridge shim that then registers the platform driver. It handles register programming, card detection, card type/voltage inference, static memory mapping, and polling-based event delivery.

Important APIs and functions: The socket ops are `bcm63xx_pcmcia_sock_init()`, `bcm63xx_pcmcia_suspend()`, `bcm63xx_pcmcia_get_status()`, `bcm63xx_pcmcia_set_socket()`, `bcm63xx_pcmcia_set_io_map()`, and `bcm63xx_pcmcia_set_mem_map()`. Probe/remove are `bcm63xx_drv_pcmcia_probe()` and `bcm63xx_drv_pcmcia_remove()`. CardBus-specific registration uses `bcm63xx_cb_probe()`, `bcm63xx_cb_exit()`, and a Broadcom PCI id table.

Control flow: Probe validates platform memory resources and IRQ/platform data, maps the controller registers and I/O window, fills `struct pcmcia_socket` with static resource ops and features, initializes control/timing registers, registers the socket, and starts a timer. The timer reads current status, computes changed bits masked by `requested_state.csc_mask`, calls `pcmcia_parse_events()`, and reschedules. New card detection toggles VS output-enable combinations, samples VS/CD pins, indexes `vscd_to_cardtype`, and enables PCMCIA or CardBus logic.

State and persistence: Runtime state lives in `struct bcm63xx_pcmcia_socket`: mapped registers, resources, card type, card-detected flag, previous status, requested socket state, timer, and static memory resources. Hardware state persists in BCM63xx PCMCIA control/timing registers while the driver is loaded.

Dependencies and integration points: Depends on BCM63xx register access, platform resources, GPIO ready line, Linux PCI if CardBus is enabled, `pccard_static_ops`, and the PCMCIA socket core.

Risks: Hardware cannot control socket power, so status always reports `SS_POWERON`; this can confuse generic power assumptions. Card-type inference depends on electrical settling and table coverage. Remove does not explicitly call `pcmcia_unregister_socket()` in the shown path, which is a lifecycle point to inspect against surrounding kernel version expectations. CardBus reset polarity is inverted for detected CardBus cards.

Test signals: Probe on BCM63xx with and without CardBus, insertion/removal polling, VS/CD card-type classification, ready GPIO behavior, reset assertion/deassertion, static common/attribute memory mapping, and module unload/removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.h

Purpose: Defines the private data model for the BCM63xx PCMCIA socket driver, including card-type bits and the per-socket state structure used by `bcm63xx_pcmcia.c`.

Important APIs and types: Defines `BCM63XX_PCMCIA_POLL_RATE`, card masks `CARD_CARDBUS`, `CARD_PCCARD`, `CARD_5V`, `CARD_3V`, `CARD_XV`, and `CARD_YV`, and `struct bcm63xx_pcmcia_socket`.

Control flow: No executable logic. The structure fields determine how the implementation tracks resources, mappings, polling, and socket state between callbacks.

State and persistence: `struct bcm63xx_pcmcia_socket` stores the embedded `pcmcia_socket`, platform data, spinlock, register and memory resources, mapped I/O base, detected card type, old status for change reporting, requested socket state, and polling timer.

Dependencies and integration points: Includes PCMCIA socket-service types and BCM63xx platform data. It is private to the BCM63xx socket implementation and must track the source file's register/mapping assumptions.

Risks: Field ownership is split between timer context, socket callbacks, and probe/remove; lock coverage must stay consistent. Card-type flags are electrical interpretations, so changing values requires auditing the status-reporting logic.

Test signals: Compile coverage with `CONFIG_PCMCIA_BCM63XX`, timer/status callback execution, and lockdep or race testing around insertion/removal validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/bcm63xx_pcmcia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cardbus.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/cardbus.c

Purpose: Bridges CardBus insertion/removal into the Linux PCI core. It scans devices below a CardBus bridge, sizes and assigns resources, sets shared IRQ/cacheline settings, invokes socket-specific bridge tuning, and removes downstream devices on eject.

Important APIs and functions: Public internal functions are `cb_alloc()` and `cb_free()`, declared through `cs_internal.h`. `cardbus_config_irq_and_cls()` recursively sets PCI interrupt lines and cacheline sizes for downstream devices.

Control flow: On CardBus insert, `cb_alloc()` locks PCI rescan/remove, scans slot 0, scans any bridges in two passes, sizes and assigns bridge resources, configures IRQ/cacheline values, calls optional `s->tune_bridge()`, adds devices to the PCI bus, and unlocks. On eject, `cb_free()` locates the subordinate bus of `s->cb_dev` and removes every child PCI device under the same PCI lock.

State and persistence: This file does not own long-lived state. It mutates PCI core bus/device/resource state and uses socket fields `cb_dev`, `pci_irq`, `functions`, and `tune_bridge`.

Dependencies and integration points: Depends on `CONFIG_CARDBUS`, Linux PCI bus scanning/resource APIs, and the PCMCIA socket core's CardBus state machine in `cs.c`.

Risks: CardBus has only one socket IRQ in this model, so all downstream devices are forced to the same IRQ line. Resource sizing/assignment is delegated to PCI and can fail if bridge windows are constrained. Removal must hold PCI locks to avoid racing driver bind/unbind or rescan paths.

Test signals: Insert a CardBus card, observe PCI device creation, IRQ line programming, cacheline setup, driver binding, bridge resource assignment, and clean removal on eject/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cardbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cirrus.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/cirrus.h

Purpose: Provides register and bit definitions for Cirrus Logic PD672x/PD6730/PD6832 PCMCIA/CardBus controllers, primarily for Yenta or legacy bridge tuning code.

Important APIs and types: Defines offsets such as `PD67_MISC_CTL_1`, `PD67_EXT_INDEX`, `PD67_TIME_SETUP()`, `PD67_TIME_CMD()`, `PD67_TIME_RECOV()`, and PD6832 extension registers. Bit masks cover voltage detection, speaker/IRQ/media enable, FIFO, suspend, DMA modes, timing scale/multiplier, extension controls, IRQ/power routing, PCI space, and bridge control.

Control flow: No executable logic. Consumers combine these constants with controller config/index register accessors.

State and persistence: The header names hardware registers whose values persist in the controller until reset, suspend/resume restore, or driver reprogramming.

Dependencies and integration points: Integrated by bridge drivers that know `struct yenta_socket` or ExCA register access. It intentionally contains only hardware constants and no Linux object ownership.

Risks: Register definitions encode vendor-specific behavior. A wrong mask or offset can silently corrupt bridge power, timing, or IRQ routing. Licensing header is dual MPL/GPL historical text and should be preserved if copied.

Test signals: Compile the drivers that include it, inspect bridge config dumps before/after tuning, and validate Cirrus-based socket power, timing, DMA, and IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cirrus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cistpl.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/cistpl.c

Purpose: Implements low-level and high-level parsing of 16-bit PCMCIA Card Information Structure tuples. It maps CIS memory, caches tuple reads, supports fake CIS replacement, follows long-link and multifunction chains, parses individual tuple formats, validates CIS sanity, and exposes a socket `cis` binary sysfs attribute.

Important APIs and functions: Exported/internal entry points include `pcmcia_read_cis_mem()`, `pcmcia_write_cis_mem()`, `release_cis_mem()`, `destroy_cis_cache()`, `verify_cis_cache()`, `pcmcia_replace_cis()`, `pccard_get_first_tuple()`, `pccard_get_next_tuple()`, `pccard_get_tuple_data()`, `pcmcia_parse_tuple()`, and `pccard_validate_cis()`. `pccard_cis_attr` exposes read/write sysfs access.

Control flow: CIS reads map either attribute/common space or indirect CIS registers, respecting `cis_width` and socket map size. `read_cis_cache()` serves fake CIS data first, then exact cache hits, then reads hardware and records cache entries. Tuple iteration starts with an assumed common long link, follows link tuples and MFC links using `follow_link()`, skips NULL tuples, bounds traversal by `MAX_TUPLES`, and returns requested tuple data. Parsing dispatches by tuple code to routines for device, checksum, longlink, strings, MANFID, FUNCID/FUNCE, config, power, timing, IO, memory, IRQ, geometry, version, organization, and format tuples.

State and persistence: State lives on `struct pcmcia_socket`: `cis_mem`, `cis_virt`, `cis_cache`, `fake_cis`, `fake_cis_len`, `functions`, and socket flags. Fake CIS persists only while the socket/card state lives; hardware CIS is card ROM/attribute memory. The `cis_width` module parameter changes access width behavior.

Dependencies and integration points: Used by `ds.c`, `pcmcia_cis.c`, and `pcmcia_resource.c` to identify devices, choose configurations, and access configuration registers. It depends on socket `set_mem_map`, PCMCIA resource allocation, Linux I/O mapping, unaligned helpers, and lockdown security for sysfs CIS writes.

Risks: CIS parsing is inherently hostile-input parsing from removable hardware. Bounds checks, tuple count limits, and cache invalidation are critical. Long-link fallback handles common bad offsets but can mask malformed cards. Writable CIS override is powerful and therefore guarded by `security_locked_down(LOCKDOWN_PCMCIA_CIS)`. Mapping lifetime must be balanced to avoid stale `cis_virt` access.

Test signals: Validate known good and malformed CIS images, multi-function cards, fake CIS loading through firmware/sysfs, suspend/resume cache verification, tuple extraction from `/sys/class/pcmcia_socket/.../cis`, and lockdep around `ops_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cistpl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cs.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/cs.c

Purpose: Implements the PCMCIA socket core and Card Services event engine. It registers socket devices, starts the per-socket `pccardd` thread, handles insertion/ejection, power/reset sequencing, suspend/resume, CardBus dispatch, callback registration for the PCMCIA bus layer, socket sysfs event handling, and socket class registration.

Important APIs and functions: Exported functions include `pcmcia_register_socket()`, `pcmcia_unregister_socket()`, `pcmcia_get_socket()`, `pcmcia_put_socket()`, `pcmcia_parse_events()`, `pcmcia_parse_uevents()`, `pccard_register_pcmcia()`, and `pcmcia_reset_card()`. Important internals are `socket_setup()`, `socket_shutdown()`, `socket_insert()`, `socket_suspend()`, resume stages, `socket_detect_change()`, and `pccardd()`.

Control flow: Socket registration assigns a socket number, initializes locks/completions, runs resource init, starts `pccardd`, queues an initial detect event, and asynchronously requests the `pcmcia` module. `pccardd` registers the socket device/sysfs, waits for userspace, then loops over hardware and sysfs events under `skt_mutex`. Insert powers and resets the card through socket ops, distinguishes CardBus from 16-bit PCMCIA, calls `cb_alloc()` for CardBus or bus callback `add()` for PCMCIA. Remove calls bus callback `remove()`, powers down, clears fake CIS and function count, and frees CardBus devices.

State and persistence: Maintains global `pcmcia_socket_list` protected by `pcmcia_socket_list_rwsem`, socket state bits, lock counts, socket voltage/reset fields, callback pointer, event bitmasks, thread pointer, CIS cache, fake CIS, and per-socket completions. State is volatile and rebuilt across insertion/removal.

Dependencies and integration points: Depends on socket controller `pccard_operations`, resource ops, socket sysfs helpers, `cardbus.c`, `ds.c` callback registration, kernel kthreads/freezer, device class PM, and module parameters controlling reset and delay timings.

Risks: The core is concurrency-heavy: socket ops, sysfs events, PM callbacks, card interrupts, and kthread shutdown converge on the same state. Timing parameters affect real hardware stability. CardBus and 16-bit flows diverge, so state bits must stay coherent. Cleanup waits for device references via completions.

Test signals: Register/unregister socket drivers, insert/eject PCMCIA and CardBus cards, sysfs insert/eject/suspend/resume/requery, system suspend/resume with card replacement, reset requests, and lockdep/kthread teardown coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cs_internal.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/cs_internal.h

Purpose: Defines private contracts shared inside the PCMCIA core modules. It separates internal state flags, resource operation hooks, callback types, and cross-module prototypes from public PCMCIA driver headers.

Important APIs and types: Defines `config_t`, `struct cis_cache_entry`, `struct pccard_resource_ops`, `struct pcmcia_callback`, `BIND_FN_ALL`, client/window/socket state flags, sysfs event masks, and prototypes for socket sysfs, CardBus, resource, CIS, and bus-core functions.

Control flow: No direct execution. The function pointer types determine how resource managers, socket core, and bus services call each other.

State and persistence: `config_t` and `cis_cache_entry` describe runtime state embedded or referenced from `struct pcmcia_device` and `struct pcmcia_socket`. State flags such as `CONFIG_LOCKED`, `CONFIG_IO_REQ`, `SOCKET_PRESENT`, `SOCKET_CARDBUS`, and `SOCKET_WIN_REQ()` gate lifecycle transitions.

Dependencies and integration points: Included by `cs.c`, `ds.c`, `cistpl.c`, `pcmcia_cis.c`, `pcmcia_resource.c`, and `cardbus.c`, but explicitly not by socket or device drivers. It binds module layering between `pcmcia_core`, `pcmcia`, and `pcmcia_rsrc`.

Risks: Because this header is a private ABI between separately linked PCMCIA modules, signature or flag changes can create subtle cross-module breakage. Public driver behavior can still be affected indirectly by these private state definitions.

Test signals: Full PCMCIA modular build, symbol resolution between `pcmcia_core` and `pcmcia`, and lifecycle tests that exercise every callback in `struct pcmcia_callback`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/cs_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/db1xxx_ss.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/db1xxx_ss.c

Purpose: Provides PCMCIA socket services for Alchemy Db/Pb1xxx development boards. It handles board-specific card detect, voltage/status interpretation, IRQ setup, reset and buffer control through BCSR registers, and static I/O/attribute/common memory mapping.

Important APIs and functions: Main socket ops are `db1x_pcmcia_configure()`, `db1x_pcmcia_get_status()`, `au1x00_pcmcia_set_io_map()`, and `au1x00_pcmcia_set_mem_map()`. Probe/remove are `db1x_pcmcia_socket_probe()` and `db1x_pcmcia_socket_remove()`. IRQ paths include `db1000_pcmcia_cdirq()`, `db1000_pcmcia_stschgirq()`, `db1200_pcmcia_cdirq()`, and threaded `db1200_pcmcia_cdirq_fn()`.

Control flow: Probe determines board type from BCSR, collects card/insert/status/eject IRQs and physical memory resources, remaps I/O with MIPS port-base adjustment, initializes socket fields, registers IRQs, disables status-change IRQ, and registers the socket. Card detect IRQs queue `SS_DETECT`; DB1200/DB1300 use paired insert/eject interrupts where the active one is disabled and the opposite one enabled after debounce. `set_socket` validates Vcc/Vpp, writes BCSR power/reset/buffer bits, disables STSCHG during reset, waits after reset deassertion, then re-enables STSCHG.

State and persistence: `struct db1x_pcmcia_sock` stores socket number, physical mappings, previous flags, IRQ numbers, insert GPIO, and board type. Hardware state persists in board BCSR PCMCIA registers and interrupt enable state.

Dependencies and integration points: Depends on Alchemy/Db1x00 BCSR APIs, MIPS I/O mapping, GPIO/IRQ APIs, `pccard_static_ops`, and PCMCIA socket core. It integrates with board platform devices that provide named resources.

Risks: Board variants have different voltage-key bit positions and interrupt semantics. IRQ polarity/disable rules are hardware-specific, especially DB1200 level-like insert/eject lines. Vpp/Vcc validation must prevent illegal combinations. I/O mapping subtracts `mips_io_port_base`, which is easy to break if MIPS I/O assumptions change.

Test signals: Probe each supported board variant, insert/eject debounce, STSCHG after reset, Vcc/Vpp programming, reset/buffer enable, static memory and I/O access, suspend/resume no-op behavior, and cleanup on platform remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/db1xxx_ss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/ds.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/ds.c

Purpose: Implements the 16-bit PCMCIA bus and driver services layer. It registers PCMCIA drivers, creates `pcmcia_device` instances from socket CIS data, performs device/driver matching, handles dynamic IDs and firmware CIS overrides, exposes device sysfs attributes, coordinates per-device PM, and registers as a class interface for sockets.

Important APIs and functions: Exported APIs are `pcmcia_register_driver()`, `pcmcia_unregister_driver()`, and `pcmcia_dev_present()`. Major internals include `pcmcia_device_probe()`, `pcmcia_device_remove()`, `pcmcia_device_query()`, `pcmcia_device_add()`, `pcmcia_card_add()`, `pcmcia_requery()`, `pcmcia_load_firmware()`, `pcmcia_devmatch()`, `pcmcia_bus_match()`, PM helpers, and socket callbacks in `pcmcia_bus_callback`.

Control flow: Driver registration fills a `device_driver`, checks product-string hashes, registers on `pcmcia_bus_type`, and creates a `new_id` sysfs file. Socket class-interface add creates the socket CIS bin file, initializes device lists/counts, and registers callbacks with `cs.c`. On card add, the layer waits for resource setup, validates memory and CIS, detects multifunction chains, allocates devices per function, queries MANFID/FUNCID/VERS data, sets up IRQ/config resources, and registers devices. Driver matching tries dynamic IDs first, then static ID tables, with guarded FUNCID fallback and optional fake CIS firmware loading.

State and persistence: Runtime state includes driver dynamic ID lists, socket device lists, `device_count`, `pcmcia_pfc`, `present`, per-device identity fields, product strings, config resources, suspend flags, and function shared `config_t`. CIS firmware overrides persist only in the socket's fake CIS memory until card/socket removal.

Dependencies and integration points: Uses Linux device model bus/class interfaces, firmware loader, CRC32 modalias hashing, DMA mask setup, CIS tuple helpers, resource APIs, socket callbacks, sysfs attributes, and runtime/system PM.

Risks: Matching behavior is intentionally conservative: FUNCID matching requires userspace acknowledgement to avoid binding wrong drivers. Pseudo multifunction cards share configuration state and can trigger requery/removal cascades. Firmware CIS loading can change function count and force re-enumeration. Device removal checks for unreleased IRQ/I/O/window resources but cannot fully protect against buggy drivers.

Test signals: Register legacy PCMCIA drivers, dynamic `new_id`, modalias generation, udev autoload, fake CIS firmware, pseudo multifunction cards, sysfs attributes, suspend/resume via `pm_state`, card requery after CIS changes, and driver cleanup warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/electra_cf.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/electra_cf.c

Purpose: Implements a CompactFlash socket driver for the PA Semi Electra evaluation board. It uses device-tree resources and GPIO registers to provide static PCMCIA mappings, card-detect events, power selection, and IRQ delivery to the PCMCIA core.

Important APIs and functions: Socket ops are `electra_cf_ss_init()`, `electra_cf_get_status()`, `electra_cf_set_socket()`, `electra_cf_set_io_map()`, and `electra_cf_set_mem_map()`. Runtime event functions are `electra_cf_timer()` and `electra_cf_irq()`. Probe/remove are `electra_cf_probe()` and `electra_cf_remove()`.

Control flow: Probe reads two address resources, maps memory and I/O, maps a fixed GPIO controller base, parses card-detect/voltage/power GPIO properties, requests IRQ and address regions, fills static socket fields, registers the socket, marks it active, and starts polling. IRQ and timer both call the timer routine; when presence changes, it queues `SS_DETECT`. `set_socket` treats reset as power-off, maps Vcc to 3.3V or 5V GPIO outputs, and writes GPIO enable/write bits.

State and persistence: `struct electra_cf_socket` stores mapped bases, resource sizes, GPIO numbers, present/active flags, timer, IRQ, and embedded socket. Hardware state persists in GPIO output registers and static mappings.

Dependencies and integration points: Depends on Open Firmware address/IRQ/property parsing, PA Semi/PowerPC I/O helpers, PCMCIA static resource ops, and the generic socket core.

Risks: The GPIO base is hard-coded, and property values are consumed as raw GPIO bit numbers rather than gpiod descriptors. The Vcc switch accepts `5` rather than the core's common `50` decivolt convention, which is a compatibility point to verify. Polling and IRQ both drive the same event path.

Test signals: Device-tree probe, GPIO property validation, card detect IRQ and poll changes, 3.3V/5V power writes, static attribute/common memory offsets, I/O region reservation, and module/platform removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/electra_cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/i82365.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/i82365.h

Purpose: Defines register offsets and bit masks for Intel 82365SL-compatible PCMCIA controllers and ExCA-style socket windows.

Important APIs and types: Defines controller registers `I365_IDENT`, `I365_STATUS`, `I365_POWER`, `I365_INTCTL`, `I365_CSC`, `I365_CSCINT`, `I365_ADDRWIN`, `I365_IOCTL`, `I365_GENCTL`, `I365_GBLCTL`, macros `I365_IO()`, `I365_MEM()`, and `I365_REG()`, plus masks for status, power, interrupts, address windows, I/O control, general/global control, and memory window flags.

Control flow: No executable code. These constants are consumed by bridge/socket drivers that perform indexed ExCA register access.

State and persistence: The header identifies controller register state: Vcc/Vpp, RESETDRV, interrupt routing, card status change bits, I/O and memory window settings, and global control fields.

Dependencies and integration points: Used by low-level PCMCIA bridge code such as Yenta or PD6729-style controllers. It is hardware-definition-only and independent from the generic PCMCIA object model.

Risks: The Intel-compatible register model has chip-step differences, especially Vpp/Vcc bit layouts. Incorrect constants can affect physical power delivery or IRQ behavior.

Test signals: Bridge-driver compile coverage and real socket tests for status, reset, window programming, IRQ delivery, and suspend/resume restore on i82365-compatible hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/i82365.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/max1600.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/max1600.c

Purpose: Provides a small library for controlling MAX1600 PCMCIA power-switch GPIOs. It abstracts channel-specific GPIO names and voltage-to-pin encoding for socket drivers.

Important APIs and functions: Exports `max1600_init()` and `max1600_configure()`. `max1600_init()` validates channel/code mode, allocates `struct max1600`, and acquires managed GPIO descriptors. `max1600_configure()` maps Vcc/Vpp requests to GPIO values and writes them as an array.

Control flow: Initialization chooses channel A or B GPIO-name rows, validates code polarity mode, gets Vcc GPIOs and optional `0VPP`, and returns a managed handle. Configure validates Vpp first, supporting 0V, 12V, or Vcc when VPP control exists, then validates Vcc as off, 3.3V, or 5.0V. In `MAX1600_CODE_HIGH` mode it inverts Vcc pins before writing.

State and persistence: `struct max1600` stores GPIO descriptors, parent device, and code polarity. Hardware output state persists on GPIO pins until reconfigured or device teardown.

Dependencies and integration points: Depends on gpiod consumer APIs and is selected by socket drivers that need external MAX1600 power control, especially older SA1111/board combinations.

Risks: Voltage values use PCMCIA decivolt conventions (`33`, `50`, `120`). Missing optional VPP control restricts legal Vpp to Vcc or off. Wrong code polarity can invert Vcc selection and risk incorrect socket voltage.

Test signals: Probe with channel A/B GPIO names, optional VPP-present and absent variants, configure off/3.3V/5V/12V combinations, verify gpiod array writes, and check error returns for illegal voltages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/max1600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/max1600.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/max1600.h

Purpose: Declares the MAX1600 PCMCIA power-switch helper interface and its state object for socket drivers.

Important APIs and types: Defines GPIO indices, channel selectors `MAX1600_CHAN_A/B`, polarity modes `MAX1600_CODE_LOW/HIGH`, `struct max1600`, and prototypes for `max1600_init()` and `max1600_configure()`.

Control flow: No executable logic; it establishes the API used by board/socket drivers.

State and persistence: `struct max1600` holds GPIO descriptor pointers, parent device, and polarity code. The actual persistent state is external GPIO pin level.

Dependencies and integration points: Forward-declares `struct gpio_desc` and expects consumers to include it alongside socket controller code that owns a `struct device`.

Risks: The enum combines GPIO indices, channels, and code modes in one namespace; callers must pass the correct subset to each function. Signature changes break exported GPL users.

Test signals: Build all `CONFIG_PCMCIA_MAX1600` consumers and run voltage-switch tests through `max1600_configure()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/max1600.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/o2micro.h -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/o2micro.h

Purpose: Provides O2Micro-specific PCI/ExCA register definitions and inline Yenta override helpers for read prefetch/write burst tuning.

Important APIs and functions: Defines O2Micro config registers such as `O2_MUX_CONTROL`, `O2_MODE_A` through `O2_MODE_E`, `O2_RESERVED1`, and `O2_RESERVED2`. `o2micro_override()` reads/writes reserved performance bits based on bridge device id and the `o2_speedup` parameter. `o2micro_restore_state()` reapplies the override after restore.

Control flow: For function 0, override reads 0x94 and 0xD4, defaults older bridge ids to speedup off and newer bridges on, allows `o2_speedup=on/off/default`, then sets or clears read-prefetch/write-burst bits in both registers.

State and persistence: State is in O2Micro bridge PCI config/ExCA registers. The helper has no owned data beyond using `struct yenta_socket` and the global parameter supplied by the including driver.

Dependencies and integration points: Depends on Yenta socket helpers such as `config_readb()` and `config_writeb()`, PCI device IDs, `o2_speedup`, and Linux device logging. It is included directly into the Yenta bridge implementation.

Risks: It writes reserved registers intentionally based on vendor guidance. Some old bridge/card combinations fail with speedups enabled, while others need them for performance or correctness. The global parameter parsing must remain compatible with module options.

Test signals: Yenta probe on O2Micro bridges across listed old and newer IDs, verify parameter overrides, suspend/resume restore, and card stability/performance with RME Hammerfall-like CardBus devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/o2micro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/omap_cf.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/omap_cf.c

Purpose: Implements the OMAP16xx CompactFlash socket controller. It exposes CF as a static PCMCIA socket with fixed memory/attribute/I/O layout, basic reset control, IRQ/poll card detection, and OMAP1 pinmux/chipselect programming.

Important APIs and functions: Socket ops are `omap_cf_ss_init()`, `omap_cf_ss_suspend()`, `omap_cf_get_status()`, `omap_cf_set_socket()`, `omap_cf_set_io_map()`, and `omap_cf_set_mem_map()`. Runtime event functions are `omap_cf_timer()` and `omap_cf_irq()`. Probe/remove are `omap_cf_probe()` and `omap_cf_remove()`.

Control flow: Module init only registers on OMAP16xx. Probe reads platform chipselect from `platform_data`, gets IRQ and memory resource, requests a shared IRQ, remaps I/O space, reserves the CF memory region, configures OMAP CF pinmux, writes CF chipselect config, fills socket fields, and registers the socket. The timer polls card detect every two seconds while active; IRQ also calls the timer path. Socket status reports CF as ready, powered, detected, and 3.3V when present. Reset writes `CF_CONTROL_RESET`.

State and persistence: `struct omap_cf_socket` stores present/active bits, timer, platform device, physical CF base, IRQ, resource, and socket. OMAP CF controller registers and pinmux settings persist while configured.

Dependencies and integration points: Depends on OMAP1 I/O, OMAP16xx CPU detection, OMAP mux helpers, PCI I/O remap for PCMCIA-style port access, `pccard_static_ops`, and the PCMCIA socket core.

Risks: The controller only supports CF memory-card-style timing; other I/O cards may not work without external logic. Platform data is cast to an integer chipselect. Remove is in exit text because `platform_driver_probe()` prevents runtime unbind. CF conflicts with MMC1 pinmux.

Test signals: OMAP16xx boot/probe, chipselect programming, card detect polling and IRQ, reset control, static memory/attribute/I/O mapping, CF storage driver bind, and unload path for module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/omap_cf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_cis.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_cis.c

Purpose: Provides higher-level CIS helper APIs used by PCMCIA client drivers and the bus layer. It reads and loops tuples, auto-selects configuration table entries, extracts tuple buffers, and optionally retrieves Ethernet MAC addresses from LAN function extension tuples.

Important APIs and functions: Public functions are `pccard_read_tuple()`, `pcmcia_loop_config()`, `pcmcia_loop_tuple()`, `pcmcia_get_tuple()`, and, under `CONFIG_NET`, `pcmcia_get_mac_from_cis()`. Internal helpers include `pccard_loop_tuple()`, `pcmcia_do_loop_config()`, `pcmcia_io_cfg_data_width()`, tuple-copy helpers, and LAN-node-id parsing.

Control flow: `pccard_read_tuple()` fetches the first matching tuple and parses it. `pccard_loop_tuple()` iterates tuples of a type, optionally parses each, and calls a callback until it returns success. `pcmcia_loop_config()` walks `CISTPL_CFTABLE_ENTRY` tuples, tracks defaults, applies automatic Vcc/Vpp/audio/I/O/IOMEM setup to `pcmcia_device`, and calls a driver-supplied `conf_check`. Tuple getters copy the first tuple payload into caller-owned memory.

State and persistence: The helpers mutate `struct pcmcia_device` configuration fields during auto-configuration: `config_index`, `vpp`, `config_flags`, resources, `io_lines`, and `card_addr`. They otherwise allocate transient buffers.

Dependencies and integration points: Sits on top of low-level tuple iteration and parsing in `cistpl.c`, and feeds resource setup in `pcmcia_resource.c` and PCMCIA client drivers. The MAC helper integrates with `struct net_device`.

Risks: Automatic configuration must interpret defaults correctly and avoid selecting unsupported Vcc, missing I/O windows, or undersized memory windows. Callback return convention is inverted from normal iteration: returning 0 stops with success. Tuple payload allocation makes callers responsible for freeing buffers.

Test signals: Client drivers using `pcmcia_loop_config()`, cards with default CFTABLE entries, multi-window I/O cards, memory-window cards, tuple-copy users, and network cards with `CISTPL_FUNCE_LAN_NODE_ID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_cis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_resource.c -->
# sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_resource.c

Purpose: Implements 16-bit PCMCIA resource management and driver-facing configuration APIs. It allocates/release I/O ports, memory windows, IRQs, maps card memory pages, accesses configuration registers, enables/disables devices, and offers post-enable Vpp/I/O-width fixups.

Important APIs and functions: Exports `pcmcia_validate_mem()`, `pcmcia_find_mem_region()`, `pcmcia_read_config_byte()`, `pcmcia_write_config_byte()`, `pcmcia_map_mem_page()`, `pcmcia_fixup_iowidth()`, `pcmcia_fixup_vpp()`, `pcmcia_enable_device()`, `pcmcia_request_io()`, `pcmcia_request_irq()`, `pcmcia_request_window()`, `pcmcia_release_window()`, and `pcmcia_disable_device()`. Internal helpers include `alloc_io_space()`, `release_io_space()`, `pcmcia_access_config()`, ISA IRQ probing, and `pcmcia_setup_irq()`.

Control flow: Drivers usually call `pcmcia_loop_config()`, request I/O/window/IRQ resources, then `pcmcia_enable_device()`. I/O allocation asks the socket resource manager for a parent range, requests it, and tracks shared socket windows. Enable sets Vpp, I/O-card/speaker/IRQ flags, writes CIS configuration registers, programs I/O maps, marks configuration locked, and increments socket lock count. Disable releases windows, configuration, I/O, and IRQ. Memory windows choose a free socket window, allocate or use static mapping, call `set_mem_map()`, then return a resource with encoded window id.

State and persistence: Mutates per-device private flags (`_io`, `_irq`, `_locked`, `_win`), shared `config_t` resource arrays/state, socket I/O/window state, `lock_count`, `pcmcia_irq`, and physical socket registers through socket ops. Hardware configuration persists until disabled, card removal, or socket reset.

Dependencies and integration points: Depends on socket resource ops from `pcmcia_rsrc`, low-level CIS memory access, Linux resource management, IRQ APIs, and PCMCIA device flags defined in public headers.

Risks: Resource accounting is shared between multifunction devices and scarce socket windows, making release ordering important. ISA IRQ probing can conflict with platform IRQ policy. Configuration register writes assume valid `config_base/config_regs`. A visible double `mutex_lock(&s->ops_mutex)` in `pcmcia_fixup_iowidth()` should be treated as a deadlock risk unless this source variant has external context explaining it.

Test signals: PCMCIA drivers requesting I/O, IRQ, and memory windows; multifunction cards sharing config; enable/disable cycles; bad resource requests; ISA and PCI IRQ fallback; Vpp and 8-bit I/O fixups; and lockdep around fixup and teardown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pcmcia/pcmcia_resource.c -->
