# subset-b-005010 research

This grouped report covers the requested Linux PCI hotplug, PCI IDE, iomap/mmap, SR-IOV, IRQ, and MSI API files under `sources/distributed-fs/ceph-client`. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_hpc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_hpc.c

## Purpose
Implements the hardware-facing half of the PCI Express hotplug controller driver. It owns Slot Control/Status command sequencing, link and presence checks, attention/power indicator control, power on/off commands, interrupt or polling notification setup, reset/link-flap suppression, and `struct controller` initialization for a PCIe hotplug port.

## Important APIs, Types, and Functions
Public entry points include `pcie_init()`, `pciehp_release_ctrl()`, `pcie_init_notification()`, `pcie_shutdown_notification()`, `pciehp_power_on_slot()`, `pciehp_power_off_slot()`, `pciehp_check_link_status()`, `pciehp_check_link_active()`, `pciehp_card_present()`, `pciehp_card_present_or_link_active()`, `pciehp_reset_slot()`, and indicator/status helpers used by the core hotplug slot operations. Internal command helpers are `pcie_do_write_cmd()`, `pcie_wait_cmd()`, and `pcie_poll_cmd()`. Notification handlers are `pciehp_isr()`, `pciehp_ist()`, and `pciehp_poll()`. The file also declares DMI and PCI fixups for broken presence and command-complete behavior.

## Control Flow
`pcie_init()` allocates and initializes the controller, reads slot capabilities, sets state from the subordinate bus contents, applies in-band presence disable and command-completion quirks, clears stale Slot Status event bits, and powers off empty slots when possible. Runtime commands serialize under `ctrl_lock`, wait for any outstanding command completion unless `NO_CMD_CMPL`, write Slot Control, and optionally wait again. IRQ mode installs a shared threaded IRQ; polling mode starts a kthread that repeatedly runs the same ISR/IST paths. The hard IRQ clears Slot Status bits, wakes waiters for Command Completed immediately, and records hotplug events for the thread. The IRQ thread handles attention buttons, power faults, DPC/spurious link changes, disable requests, and presence/link changes under `reset_lock`.

## State and Persistence Behavior
Persistent controller state lives in `struct controller`: cached slot capabilities/control, command busy/start time, pending event bits, wait queues, state locks, `reset_lock`, current ON/OFF state, notification-enabled flag, in-band presence disable flag, stored downstream device serial number, and power-fault suppression flag. Hardware state is PCIe Slot Control, Slot Status, Link Control, and Link Status. Runtime PM references keep the port parent accessible during interrupt handling.

## Dependencies and Integration Points
Depends on PCIe capability accessors, PCI hotplug core data from `pciehp.h`, runtime PM, DMI matching, IRQ threading, kthreads, DPC/AER helpers, secondary bus reset helpers, and global PCI bus locking semantics in callers. It integrates with `pciehp_pci.c` enumeration/removal and higher-level pciehp state-machine functions such as `pciehp_handle_presence_or_link_change()`, `pciehp_handle_button_press()`, and `pciehp_request()`.

## Risks
Command completion handling is hardware-quirk sensitive; clearing `cmd_busy` too early or waiting when completions never arrive can wedge hotplug. Slot Status bits are write-1-to-clear and can race with MSI reassertion, so the reread loop matters. Link and presence events may be intentionally ignored during DPC recovery, secondary bus reset, suspend, or firmware reconfiguration; missing the synthetic follow-up can hide removal. Runtime PM and reset locking are interleaved with IRQ handling, so lock ordering changes can deadlock hotplug, reset, and driver bind/unbind paths.

## Test Signals
Exercise module probe/remove on real or emulated PCIe hotplug ports, interrupt and polling modes, attention-button workflows, surprise removal, safe removal, DPC recovery, secondary bus reset, runtime suspend/resume, broken Command Completed controllers, Dell/in-band presence disable systems, link training failure, empty-slot power-off, indicator sysfs reads/writes, and repeated hotplug under MSI and INTx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_hpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_pci.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_pci.c

## Purpose
Provides PCI enumeration and removal helpers for pciehp once the hardware controller has determined that a slot should be added or removed.

## Important APIs, Types, and Functions
The file exports `pciehp_configure_device()` and `pciehp_unconfigure_device()`. Both operate on a pciehp `struct controller`, its PCIe port bridge, and the bridge subordinate bus.

## Control Flow
Hot-add locks PCI rescan/remove, rejects already-enumerated function 0, scans slot `00.0`, adds hotplug bridge metadata below any newly found bridges, assigns unassigned bridge resources, configures PCIe bus settings, temporarily drops `reset_lock` while binding drivers through `pci_bus_add_devices()`, then caches the downstream device serial number. Hot-remove optionally marks devices disconnected for surprise removal, locks rescan/remove, iterates the subordinate device list in reverse so VFs are removed before PFs, temporarily drops `reset_lock` around driver unbind/removal, and for safe removals disables bus mastering/SERR and masks INTx on each removed device.

## State and Persistence Behavior
The code mutates the PCI device tree under the hotplug bridge and updates `ctrl->dsn`. It relies on core PCI resource assignment to persist BAR/window programming and on `pci_dev_set_disconnected()` to prevent config accesses after surprise removal.

## Dependencies and Integration Points
Depends on the PCI core scanning, bridge resource assignment, bus settings, driver binding, and removal APIs. It is invoked by the pciehp state machine after `pciehp_hpc.c` has validated link/presence and controlled slot power.

## Risks
Dropping and reacquiring `reset_lock` around device bind/unbind is required to avoid AB-BA deadlocks; changing this ordering is risky. Reverse removal protects SR-IOV list iteration. Function-0-only scanning follows PCIe hotplug's one-device-per-slot model and is not suitable for arbitrary conventional PCI slots.

## Test Signals
Validate hot-add of endpoints and downstream bridges, resource assignment, driver autoload, SR-IOV PF/VF hot-remove, surprise removal disconnect marking, safe removal command-bit masking, and repeated add/remove under concurrent reset or driver probe activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/pciehp_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/pnv_php.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/pnv_php.c

## Purpose
Implements PowerPC PowerNV PCI hotplug. It registers firmware-described hotplug slots, controls slot power via OPAL, imports/removes device-tree fragments for newly powered slots, scans/removes PCI devices, manages nested hotplug slot registration, and handles surprise hotplug interrupts.

## Important APIs, Types, and Functions
Important state is `struct pnv_php_slot` from platform headers and local `struct pnv_php_event`. Exported APIs are `pnv_php_find_slot()` and `pnv_php_set_slot_power_state()`. Major helpers include `pnv_php_add_devtree()`, `pnv_php_rmv_devtree()`, `pnv_php_enable()`, `pnv_php_disable_slot()`, `pnv_php_activate_slot()`, `pnv_php_register_slot()`, `pnv_php_enable_irq()`, `pnv_php_interrupt()`, `pnv_php_event_handler()`, `pnv_php_register()`, and `pnv_php_unregister()`.

## Control Flow
Module init walks PowerNV PHB compatible nodes and registers pluggable/reset-by-firmware slots. Allocation records slot id, PCI bus, bridge device, workqueue, kref, and hotplug ops. Enabling checks firmware presence and power, optionally asks OPAL to power on the slot, imports a fresh FDT blob through `pnv_pci_get_device_tree()`, applies an OF changeset, adds PCI device-node data, scans devices, and recursively registers child slots. Disabling turns off downstream IRQs, removes PCI devices, unregisters child slots, powers the slot off, and removes dynamic device-tree state. Surprise interrupts read/clear PCIe Slot Status, determine add/remove from DLL active or OPAL presence, optionally freezes a removed EEH PE, then queues work to enable or disable the slot.

## State and Persistence Behavior
Global slot topology is a locked tree rooted at `pnv_php_slot_list`, with krefs for parent/child ownership. Per-slot state includes OPAL id, device node, PCI bus/bridge, current populated/registered/offline state, dynamic FDT/change-set pointers, attention state, power-state-check flag, IRQ number, and broken-PDC flag. Power state and slot activation persist in OPAL firmware; device-tree changes persist in the live OF tree until removal.

## Dependencies and Integration Points
Depends on OPAL PCI calls, PowerNV PCI helpers, OF/FDT changesets, PCI hotplug core, PCI scanning/removal, MSI/MSI-X/INTx interrupt APIs, EEH PE freeze/thaw helpers, and PCIe capability registers. It integrates with platform firmware properties such as `ibm,slot-pluggable`, `ibm,reset-by-firmware`, `ibm,slot-surprise-pluggable`, `ibm,slot-label`, and `ibm,slot-broken-pdc`.

## Risks
Device-tree changeset ordering and cleanup are delicate because child nodes are attached in reverse and may come from one allocated FDT block. Interrupt resources must be disabled for downstream slots before removal or stale MSI/MSI-X state can block further events. OPAL slot activation may fail due to frozen PHBs, requiring reset retry logic. EEH freeze/thaw paths affect error recovery. Parent/child kref and list management must remain balanced across registration failure, nested unregister, and module exit.

## Test Signals
Use PowerNV systems with IODA2/IODA3/OpenCAPI slots: boot-time registration, manual enable/disable, OPAL power failures, FDT import/removal, nested slots, surprise add/remove interrupts with DLLSC and PDC, broken-PDC slots, MSI-X/MSI/INTx fallback, EEH frozen PE recovery, PHB reset retry, module unload, and repeated hotplug while child slots exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/pnv_php.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar.h

## Purpose
Declares the small public interface for RPA Dynamic Logical Partitioning of I/O slots on PPC64 pSeries systems.

## Important APIs, Types, and Functions
The header declares `dlpar_sysfs_init()`, `dlpar_sysfs_exit()`, `dlpar_add_slot()`, and `dlpar_remove_slot()`. It has only an include guard and no local types.

## Control Flow
There is no executable flow. `rpadlpar_core.c` implements add/remove operations and calls the sysfs init/exit helpers implemented by `rpadlpar_sysfs.c`.

## State and Persistence Behavior
No state is stored here. The declarations define the module-internal boundary for sysfs-triggered DLPAR operations.

## Dependencies and Integration Points
Consumed by `rpadlpar_core.c` and `rpadlpar_sysfs.c`; indirectly integrates with RTAS, VIO, PCI PHB, and rpaphp slot operations.

## Risks
Signature drift breaks the sysfs-to-core call boundary. Since DLPAR operations are string-keyed by DRC name, callers must honor `MAX_DRC_NAME_LEN` from `rpaphp.h` even though this header does not restate it.

## Test Signals
Compile coverage of `rpadlpar_core.c` and `rpadlpar_sysfs.c`, module load on DLPAR-capable partitions, and sysfs add/remove slot calls validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_core.c

## Purpose
Implements pSeries RPA DLPAR add/remove orchestration for PCI slots, PHBs, and VIO slots. It maps a user-provided DRC name to a device-tree node and then creates or removes kernel PCI/VIO/hotplug representations.

## Important APIs, Types, and Functions
Public functions are `dlpar_add_slot()` and `dlpar_remove_slot()`. Internal helpers include `find_dlpar_node()`, `find_php_slot()`, `dlpar_pci_add_bus()`, `dlpar_add_pci_slot()`, `dlpar_remove_pci_slot()`, `dlpar_add_phb()`, `dlpar_remove_phb()`, `dlpar_add_vio_slot()`, `dlpar_remove_vio_slot()`, and `is_dlpar_capable()`. `rpadlpar_mutex` serializes all DLPAR operations.

## Control Flow
Add/remove first acquire `rpadlpar_mutex`, find a VIO, PCI slot, or PHB node by DRC properties, dispatch by node type, put the OF node reference, and release the mutex. PCI slot add creates the PCI bus/device for the EADS bridge, scans below bridges, maps IO space, finishes PCI bus addition, confirms the bridge, and registers an rpaphp hotplug slot. PCI slot removal deregisters the hotplug slot, removes devices below the bus, unmaps IO space, and removes the bridge device. PHB add/remove use dynamic PHB platform helpers, while VIO add/remove register or unregister VIO device nodes. Module init rejects partitions lacking the RTAS `ibm,configure-connector` token and creates the sysfs control group.

## State and Persistence Behavior
The file mutates the live OF-derived PCI/VIO topology, PCI buses/devices, dynamic PHB state, rpaphp slot list, and VIO device registration. It calls `vm_unmap_aliases()` after removal to flush stale vmalloc mappings. No on-disk persistence exists; partition firmware remains authoritative for DRC topology.

## Dependencies and Integration Points
Depends on RTAS token discovery, Open Firmware node traversal, pSeries PCI bridge APIs (`init_phb_dynamic`, `remove_phb_dynamic`, `of_create_pci_dev`, `of_scan_pci_bridge`), EEH initialization, VIO registration, rpaphp DRC property parsing/slot registration, and PCI rescan/remove locking.

## Risks
DLPAR add/remove is topology-sensitive: built-in DLPAR-capable nodes may not be hotpluggable, and `find_php_slot()` only sees rpaphp-registered slots. PCI removal assumes the located bus has a bridge device and uses `BUG_ON` in that path. Failure after creating a dynamic PHB or bus can leave partial topology if not unwound by callers. The mutex serializes user operations but does not by itself protect against all firmware or hotplug event races.

## Test Signals
Exercise sysfs DRC add/remove for VIO slots, PCI slots, and PHBs; duplicate add/remove; missing DRC names; EEH initialization; IO-space map/unmap failures; hotplug slot deregistration failures; dynamic PHB creation/removal; and concurrent add/remove attempts interrupted by signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_sysfs.c

## Purpose
Exposes pSeries RPA DLPAR control through sysfs files under the PCI slots kset, allowing userspace to request slot add or remove by DRC name.

## Important APIs, Types, and Functions
Public functions are `dlpar_sysfs_init()` and `dlpar_sysfs_exit()`. Store handlers are `add_slot_store()` and `remove_slot_store()`, with simple show handlers returning `0`. The file defines `add_slot` and `remove_slot` `kobj_attribute`s in `dlpar_attr_group`.

## Control Flow
Initialization creates a `control` kobject under `pci_slots_kset` and adds the attribute group. A write to `add_slot` or `remove_slot` copies the DRC name into a fixed buffer, strips one trailing newline, and calls `dlpar_add_slot()` or `dlpar_remove_slot()`. Exit removes the group and drops the kobject.

## State and Persistence Behavior
The only local persistent state is `dlpar_kobj`. User writes trigger live topology mutations in `rpadlpar_core.c`; the sysfs file contents themselves are not persistent and reads always return `0`.

## Dependencies and Integration Points
Depends on kobject/sysfs APIs, `pci_slots_kset`, `MAX_DRC_NAME_LEN`, and the core DLPAR add/remove functions. It is the user-facing entry point for the `rpadlpar_io` module.

## Risks
Inputs with length `>= MAX_DRC_NAME_LEN` return `0` rather than an errno, which can look like a short no-op success to userspace. The handler accepts arbitrary strings and relies on core DRC lookup for validation. `dlpar_sysfs_exit()` assumes initialization succeeded and `dlpar_kobj` is valid.

## Test Signals
Validate sysfs group creation/removal, newline stripping, overlong input behavior, successful and failed add/remove writes, module unload after failed init paths, and DRC names containing spaces or unusual characters accepted by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpadlpar_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp.h

## Purpose
Defines the shared contract for the pSeries RPA PCI hotplug driver: RTAS constants, LED/power/sensor/state values, debug macros, `struct slot`, and cross-file prototypes.

## Important APIs, Types, and Functions
Key constants include `DR_INDICATOR`, `DR_ENTITY_SENSE`, `POWER_ON`, `POWER_OFF`, `LED_*`, `PRESENT`, `EMPTY`, `CONFIGURED`, `NOT_CONFIGURED`, `NOT_VALID`, and `MAX_DRC_NAME_LEN`. `struct slot` stores DRC index/type/power domain/name, OF node, PCI bus/device list, hotplug slot, attention state, and list linkage. Prototypes cover rpaphp PCI, core, and slot allocation/registration functions.

## Control Flow
The header has no execution, but its `to_slot()` helper maps generic `struct hotplug_slot` callbacks back to rpaphp `struct slot`. The hotplug ops object declared here is supplied by `rpaphp_core.c` and installed by `rpaphp_slot.c`.

## State and Persistence Behavior
The header describes per-physical-slot runtime state and declares the global `rpaphp_slot_head` list plus `rpaphp_debug`. Slot objects hold references to OF nodes and PCI buses but no external persistence.

## Dependencies and Integration Points
Includes Linux PCI and PCI hotplug headers. It is shared by `rpaphp_core.c`, `rpaphp_pci.c`, `rpaphp_slot.c`, and the DLPAR core.

## Risks
Several state names overlap semantically (`EMPTY` is both sensor and slot state), so call sites must distinguish sensor values from hotplug slot states. Changes to `struct slot` affect all rpaphp files and DLPAR lookup. DRC constants are RTAS ABI values and must not drift.

## Test Signals
Compile all rpaphp/rpadlpar objects, register/deregister slots, use attention/power/sensor callbacks, and verify debug macro/module parameter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_core.c

## Purpose
Implements the core pSeries RPA PCI hotplug driver. It discovers hotpluggable DRC entries in the device tree, allocates/enables/registers slots, exposes hotplug callbacks for enable/disable/status/attention, and cleans up registered slots at module exit.

## Important APIs, Types, and Functions
Exports `rpaphp_slot_head`, `rpaphp_check_drc_props()`, and `rpaphp_add_slot()`. Important helpers include `get_children_props()`, `rpaphp_check_drc_props_v1()`, `rpaphp_check_drc_props_v2()`, `is_php_type()`, `is_php_dn()`, `rpaphp_drc_info_add_slot()`, `rpaphp_drc_add_slot()`, `enable_slot()`, `disable_slot()`, and status callbacks. `rpaphp_hotplug_slot_ops` is the hotplug-core operation table.

## Control Flow
Module init walks all `pci` OF nodes and calls `rpaphp_add_slot()`. Discovery supports both legacy `ibm,drc-*` arrays and newer `ibm,drc-info` cells. For each hotpluggable PCI DRC entry, it allocates a slot, records type/power domain/name/index, calls `rpaphp_enable_slot()` to initialize state and add present devices, then registers it with the PCI hotplug core. The enable callback checks the RTAS sensor; present devices trigger EEH init and `pci_hp_add_devices()`, while empty slots become `EMPTY`. Disable removes devices below the slot bus and marks the slot not configured.

## State and Persistence Behavior
Global state is the `rpaphp_slot_head` list and `rpaphp_debug` module parameter. Per-slot state tracks attention LED, power domain, DRC metadata, bus pointer, and configured/empty/not-valid status. Hardware/firmware state is RTAS power, sensor, and indicator state; PCI devices are added/removed from kernel memory only.

## Dependencies and Integration Points
Depends on Open Firmware DRC properties, RTAS indicator/power/sensor services, EEH initialization, pSeries PCI bridge data, PCI hotplug core, PCI rescan/remove locking, and `rpaphp_pci.c` sensor/enable helper. DLPAR add/remove calls `rpaphp_add_slot()` and `rpaphp_deregister_slot()`.

## Risks
Legacy DRC parsing walks packed string arrays and must stay aligned with index counts. The `ibm,drc-info` path currently handles a single first cell for slot creation, so assumptions about multiple cells need audit. The loop in `rpaphp_drc_add_slot()` returns the last slot's result only. Enable/disable state updates depend on RTAS sensor values, and a powered-off slot may need power-on just to read presence.

## Test Signals
Test legacy and `ibm,drc-info` device trees, boot-time slot discovery, attention LED set/get, power get, adapter get, enable/disable of empty and populated slots, EEH initialization, duplicate slot names, DLPAR-added slots, and module exit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_pci.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_pci.c

## Purpose
Provides rpaphp PCI-slot sensor and initial enable/configuration logic around RTAS and pSeries EEH/PCI bus integration.

## Important APIs, Types, and Functions
Public functions are `rpaphp_get_sensor_state()` and `rpaphp_enable_slot()`. Internal helpers are `rtas_get_sensor_errno()` and `__rpaphp_get_sensor_state()`. The file defines PAPR-specific RTAS sensor error constants for unisolated/not-unisolated/unusable slots.

## Control Flow
`rpaphp_get_sensor_state()` tries to read `DR_ENTITY_SENSE`; if firmware reports that the slot must be powered/unisolated, it powers the slot on with `rtas_set_power_level()` and retries. During EEH recovery, `__rpaphp_get_sensor_state()` bypasses `rtas_get_sensor()` and calls `rtas_call()` directly so extended-delay return codes become `-EBUSY` instead of blocking recovery. `rpaphp_enable_slot()` reads slot power, reads presence, locates the PCI bus by OF node, records bus/device-list pointers, and if an adapter is present, initializes EEH and adds devices on an empty bus.

## State and Persistence Behavior
The code initializes `slot->state`, `slot->bus`, and `slot->pci_devs`. It may change RTAS slot power just to make sensor reads work. PCI devices added to the bus persist until hotplug disable or DLPAR removal.

## Dependencies and Integration Points
Depends on RTAS `get-sensor-state`, RTAS power-level calls, pSeries PCI DN/PHB structures, EEH PE state, PCI bus lookup by OF node, and `pci_hp_add_devices()`. Called by rpaphp discovery and hotplug enable paths.

## Risks
The EEH fast path only inspects the first child PDN under the PHB, so unusual topologies may not reflect the target slot's recovery state. Powering on a slot for sensor reads has side effects. `rpaphp_enable_slot()` requires present slots to have child OF nodes and fails otherwise. It only adds devices if the bus list is empty, assuming firmware/kernel topology consistency.

## Test Signals
Validate sensor reads for powered-on/off slots, RTAS busy/extended-delay behavior during EEH recovery, unusable slots, present slots without children, empty slots, PCI bus lookup failures, EEH init plus device add, and debug listing of configured devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_slot.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_slot.c

## Purpose
Owns allocation, deallocation, registration, and deregistration of rpaphp `struct slot` objects with the PCI hotplug core.

## Important APIs, Types, and Functions
Public functions are `alloc_slot_struct()`, `dealloc_slot_struct()`, `rpaphp_register_slot()`, and `rpaphp_deregister_slot()`. The private `is_registered()` helper detects duplicate slot names in `rpaphp_slot_head`.

## Control Flow
Allocation zeroes a slot, duplicates the DRC name, takes an OF node reference, stores DRC index/power-domain metadata, and attaches `rpaphp_hotplug_slot_ops`. Registration rejects duplicate names, searches child OF nodes for matching `ibm,my-drc-index` to derive a PCI slot number, registers with `pci_hp_register()`, then links the slot into the global rpaphp list. Deregistration removes the slot from the list, deregisters the hotplug slot, drops the OF node, and frees memory.

## State and Persistence Behavior
This file manages heap lifetime and OF node references for slot objects. The global list is updated without a local lock, relying on rpaphp/DLPAR call serialization and module init/exit context.

## Dependencies and Integration Points
Depends on OF node reference counting, PCI DN metadata for child devfn lookup, PCI hotplug registration, and `rpaphp_hotplug_slot_ops` from `rpaphp_core.c`.

## Risks
The `retval` variable in child-node lookup is not initialized before the loop but is assigned before use if matching logic behaves normally; malformed children can make slot number fallback subtle. Lack of explicit locking around `rpaphp_slot_head` is safe only if callers serialize. Duplicate detection is name-based, not DRC-index-based.

## Test Signals
Exercise allocation failures, duplicate slot registration, missing child DRC index, successful register/deregister, OF node refcount balance, and DLPAR add/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/rpaphp_slot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/s390_pci_hpc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/s390_pci_hpc.c

## Purpose
Implements PCI hotplug slot operations for IBM Z `zpci` functions. It maps generic PCI hotplug actions to s390 configure, deconfigure, reset, and status operations.

## Important APIs, Types, and Functions
Public functions are `zpci_init_slot()` and `zpci_exit_slot()`. Hotplug callbacks are `enable_slot()`, `disable_slot()`, `reset_slot()`, `get_power_status()`, and `get_adapter_status()` in `s390_hotplug_slot_ops`.

## Control Flow
Enabling requires the zPCI function to be in `STANDBY`, calls `sclp_pci_configure()`, marks it configured, and scans the configured device. Disabling requires `CONFIGURED`, rejects PFs with enabled VFs by checking `pci_num_vf()`, then calls `zpci_deconfigure_device()`. Reset uses `mutex_trylock()` to avoid waiting during state transitions, supports probe queries, and calls `zpci_hot_reset_device()` only for configured functions. Registration names the hotplug slot by FID.

## State and Persistence Behavior
State is held in `struct zpci_dev`: function state, FID/FH, devfn, zbus, state lock, and embedded hotplug slot. Firmware/hardware configured state changes through SCLP and zPCI reset/deconfigure calls.

## Dependencies and Integration Points
Depends on s390 SCLP PCI configure, zPCI scan/deconfigure/reset helpers, PCI hotplug core, zPCI debug, and SR-IOV helper `pci_num_vf()`.

## Risks
State transitions are serialized by `zdev->state_lock`; reset intentionally fails if the lock is busy. Disabling a PF with active VFs returns `-EBUSY`, so callers must quiesce SR-IOV first. Adapter status always reports present because a zPCI slot represents an existing function.

## Test Signals
Configure/deconfigure a standby/configured function, reset configured and unconfigured functions, disable PFs with and without VFs, hotplug slot registration naming, concurrent state transitions, and power/adapter sysfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/s390_pci_hpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp.h

## Purpose
Defines the shared data structures, constants, register layout, helper functions, and prototypes for the Standard Hot Plug Controller PCI/PCI-X driver.

## Important APIs, Types, and Functions
Important types are `struct slot`, `struct event_info`, `struct controller`, packed `struct ctrl_reg`, and `enum ctrl_offsets`. The header defines event constants (`INT_*`), state constants (`STATIC_STATE`, `BLINKING*`, `POWER*`), user-facing error codes, SHPC/AMD errata register masks, and prototypes for core, control, hardware, PCI, and sysfs helpers. Inline helpers include `get_slot()`, `shpchp_find_slot()`, and AMD POGO errata save/restore functions.

## Control Flow
No standalone code runs, but the header defines the controller/slot state machine used by `shpchp_core.c` and `shpchp_ctrl.c`. AMD errata helpers temporarily mask SERR/PERR enables and clear bridge error status around slot enable.

## State and Persistence Behavior
`struct controller` persists per-HPC locks, slot list, wait queue, PCI device, MMIO mapping, SHPC offsets, bus speed metadata, and polling timer. `struct slot` persists per-slot state, cached power/presence/latch/attention status, workqueue, delayed button work, and hotplug slot object.

## Dependencies and Integration Points
Includes PCI, PCI hotplug, delay, signal, mutex, and workqueue APIs. It is consumed by all `shpchp_*` implementation files and couples them to SHPC MMIO register layout.

## Risks
Register layout and bit definitions mirror the SHPC spec and are ABI-sensitive. Slot state values drive button debounce and sysfs behavior. AMD errata helpers touch vendor-specific PCI-X bridge registers and must remain scoped to affected devices. `shpchp_find_slot()` assumes device numbers uniquely identify slots.

## Test Signals
Compile all SHPC objects, initialize controllers with multiple slot counts/orderings, exercise button/presence/latch/power-fault events, AMD POGO single-slot enable, and inspect cached status consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_core.c

## Purpose
Registers the SHPC PCI driver, probes SHPC-capable bridges, initializes controller and slot objects, exposes hotplug slot callbacks, and tears controllers down on remove.

## Important APIs, Types, and Functions
Key functions are `shpc_probe()`, `shpc_remove()`, `init_slots()`, `cleanup_slots()`, and hotplug callbacks for attention, enable, disable, power, attention, latch, and adapter status. Module parameters are `shpchp_poll_mode` and `shpchp_poll_time`.

## Control Flow
Probe filters for SHPC capability or AMD Golam, declines devices controlled by firmware/ACPI, allocates a controller, calls `shpc_init()` for hardware/MMIO/IRQ setup, registers per-slot hotplug entries, creates the controller sysfs resource file, and marks the PCI device SHPC-managed. Slot initialization allocates one `struct slot` per hardware slot, creates a per-slot workqueue, initializes delayed button work and locks, registers with the PCI hotplug core, caches initial status, and links the slot to the controller. Remove clears management state, removes sysfs, releases hardware resources, and frees the controller.

## State and Persistence Behavior
Persistent state includes module parameters, `pdev->shpc_managed`, controller MMIO/IRQ/timer resources, per-slot workqueues and cached status, and hotplug registration. Hardware state is initialized in `shpc_init()` and masked during release.

## Dependencies and Integration Points
Depends on PCI driver core, PCI hotplug registration, ACPI hotplug ownership checks, SHPC hardware setup in `shpchp_hpc.c`, slot operation logic in `shpchp_ctrl.c`, and resource reporting in `shpchp_sysfs.c`.

## Risks
Failure paths must avoid double cleanup because `shpchp_release_ctlr()` already calls `cleanup_slots()`. Per-slot workqueues and delayed work must be canceled before free. Capability detection includes device-specific exceptions. Firmware-controlled hotplug must not be claimed by this driver.

## Test Signals
Probe/remove SHPC and non-SHPC bridges, ACPI ownership refusal, polling and interrupt modes, multi-slot registration, sysfs file creation failure, status cache fallback, and module parameter changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_ctrl.c

## Purpose
Implements the SHPC policy/state machine for handling attention button, latch, presence, power-fault, sysfs enable/disable, board add, and board remove events.

## Important APIs, Types, and Functions
Event entry points are `shpchp_handle_attention_button()`, `shpchp_handle_switch_change()`, `shpchp_handle_presence_change()`, and `shpchp_handle_power_fault()`. User entry points are `shpchp_sysfs_enable_slot()` and `shpchp_sysfs_disable_slot()`. Core helpers include `board_added()`, `remove_board()`, `handle_button_press_event()`, `shpchp_queue_pushbutton_work()`, `interrupt_event_handler()`, `shpchp_enable_slot()`, and `shpchp_disable_slot()`.

## Control Flow
Hardware IRQ handlers queue compact event objects to per-slot workqueues. Button events enter a five-second blinking confirmation window; a second press cancels, while delayed work commits power on/off. Sysfs enable/disable bypasses the delay but still obeys the slot state machine. Add validates adapter present, latch closed, and power off, powers the slot, negotiates PCI/PCI-X bus speed if needed, enables the slot, waits for power fault, scans/configures PCI devices, updates state, and turns the green LED on. Remove unconfigures devices, disables the slot, clears attention, and updates cached state.

## State and Persistence Behavior
Per-slot state includes button state (`STATIC`, `BLINKING*`, `POWER*`), cached power/presence/latch/attention, `is_a_board`, fault status, and pending delayed work. Controller-level `crit_sect` serializes add/remove operations; per-slot `lock` serializes button/sysfs state transitions. Hardware slot power/LED/bus speed persists in SHPC registers.

## Dependencies and Integration Points
Depends on SHPC hardware commands/status from `shpchp_hpc.c`, PCI enumeration/removal in `shpchp_pci.c`, hotplug callbacks in `shpchp_core.c`, workqueues, timers, and PCI bus speed fields.

## Risks
State transitions are easy to break because the code unlocks around blocking enable/disable operations and relocks to update state. Bus speed changes are unsafe if other devices exist on the same bus and are guarded by `slots_not_empty`. Power-fault handling uses `p_slot->status == 0xFF` as an event flag. Button delayed work cancellation must be synchronized with sysfs actions and slot teardown.

## Test Signals
Exercise button press/commit/cancel, sysfs enable/disable in every state, presence/latch/power-fault interrupts, PCI-X bus speed mismatch, add failure rollback, AMD POGO errata path, and repeated rapid events on the same slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_hpc.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_hpc.c

## Purpose
Implements the hardware access layer for Standard Hot Plug Controllers. It maps SHPC working registers, serializes and issues SHPC commands, handles interrupts or polling, reads slot status, controls LEDs/power/bus speed, and initializes/releases controller resources.

## Important APIs, Types, and Functions
Public hardware APIs include `shpc_init()`, `shpchp_release_ctlr()`, `shpchp_power_on_slot()`, `shpchp_slot_enable()`, `shpchp_slot_disable()`, `shpchp_set_bus_speed_mode()`, `shpchp_get_*_status()`, `shpchp_get_adapter_speed()`, `shpchp_query_power_fault()`, LED helpers, and `shpchp_check_cmd_status()`. Internal helpers include MMIO accessors, indirect SHPC config reads, `shpc_write_cmd()`, `shpc_wait_cmd()`, `shpc_isr()`, and polling timer helpers.

## Control Flow
Initialization locates SHPC MMIO either through AMD special handling or SHPC capability indirect registers, enables the PCI device, reserves and maps MMIO, initializes locks/wait queues, reads slot configuration, masks controller and per-slot events, installs a polling timer or MSI/INTx IRQ, computes max/current bus speed, and unmasks slot events. Commands wait for controller not busy, write the command register, wait for command completion via IRQ waitqueue or polling, and decode command errors. ISR masks global interrupts, wakes command waiters, dispatches per-slot event bits to `shpchp_ctrl.c`, clears slot events, and unmasks global interrupts.

## State and Persistence Behavior
Controller state includes MMIO base/size/mapping, capability offset, slot counts/offsets, speed fields stored in the subordinate bus, polling timer, IRQ allocation, and cached AMD errata register values. Hardware state includes SHPC logical slot registers, SERR/interrupt enable register, command/status register, and secondary bus speed mode.

## Dependencies and Integration Points
Depends on PCI config/MMIO APIs, MSI/IRQ APIs, timers, wait queues, SHPC constants from the spec, `shpchp_ctrl.c` event handlers, and `shpchp_core.c` lifecycle management.

## Risks
Resource failure paths in `shpc_init()` can leak memory regions if future changes add exits after `request_mem_region()`. Command completion waits are limited to one second and can return interrupted by signals. MMIO register masks must preserve reserved-zero bits. Polling and IRQ paths share `shpc_isr()`, so assumptions about IRQ numbers must remain minimal. Bus speed encoding depends on programming interface version.

## Test Signals
Probe with capability and AMD Golam paths, MMIO reservation/map failure injection, MSI success/fallback to INTx, polling mode, command timeout/interruption, every slot event bit, LED/power commands, bus speed set/get across PI 1 and 2, release masking, and controller remove during pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_hpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_pci.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_pci.c

## Purpose
Provides SHPC PCI device enumeration and removal for a specific conventional PCI slot device number below an SHPC-managed bridge.

## Important APIs, Types, and Functions
Public functions are `shpchp_configure_device()` and `shpchp_unconfigure_device()`, both operating on `struct slot` and its controller bridge/subordinate bus.

## Control Flow
Configure locks PCI rescan/remove, rejects an already existing device at the slot devfn, scans that slot, adds hotplug bridge metadata only for bridges in the target slot, assigns unassigned bridge resources, configures PCIe bus settings, and adds devices. Unconfigure locks rescan/remove, iterates subordinate devices, removes those whose PCI slot matches `p_slot->device`, and unlocks.

## State and Persistence Behavior
The code mutates the PCI device tree under the SHPC bridge and causes resource assignment/device binding through PCI core calls. It does not manage SHPC hardware state directly.

## Dependencies and Integration Points
Depends on PCI scanning/removal/resource assignment and is called by `board_added()` and `remove_board()` in `shpchp_ctrl.c`.

## Risks
It scans/removes by PCI slot number, which matches SHPC conventional PCI semantics but differs from pciehp's fixed function-0 model. It does not explicitly mark devices disconnected for surprise removal; higher-level SHPC handling must decide when removal is safe. Resource assignment affects the whole bridge.

## Test Signals
Hot-add endpoints and bridges at SHPC slot device numbers, duplicate device detection, no-device scan failure, resource assignment, driver binding, and removal of only devices in the target slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_sysfs.c

## Purpose
Adds a controller-level SHPC sysfs attribute that reports free subordinate bus resources for debugging and management.

## Important APIs, Types, and Functions
Public functions are `shpchp_create_ctrl_files()` and `shpchp_remove_ctrl_files()`. The `ctrl` device attribute is read-only and implemented by `show_ctrl()`.

## Control Flow
`show_ctrl()` obtains the bridge subordinate bus, emits free non-prefetchable memory, prefetchable memory, I/O resources, and a simple free bus-number range by scanning for the first unused bus number.

## State and Persistence Behavior
No persistent state is stored beyond the device attribute registration. Output reflects current PCI bus resource lists at read time.

## Dependencies and Integration Points
Depends on PCI device/sysfs APIs and resource iteration. It is created after SHPC probe and removed before controller release.

## Risks
The bus-number reporting only shows the first contiguous gap discovered by `pci_find_bus()`. The output is diagnostic and not synchronized against concurrent resource changes beyond normal sysfs/device lifetime assumptions.

## Test Signals
Read the `ctrl` attribute on SHPC bridges with free memory, prefetchable memory, I/O, and bus-number resources; validate removal on driver unbind and behavior with no subordinate resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/shpchp_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/ide.c -->
# sources/distributed-fs/ceph-client/drivers/pci/ide.c

## Purpose
Implements PCIe Integrity and Data Encryption (IDE) stream discovery, allocation, registration, register programming, enable/disable, teardown, and host-bridge stream accounting.

## Important APIs, Types, and Functions
Public APIs include `pci_ide_init()`, `pci_ide_stream_alloc()`, `pci_ide_stream_free()`, `pci_ide_stream_release()`, `pci_ide_stream_register()`, `pci_ide_stream_unregister()`, `pci_ide_to_settings()`, `pci_ide_stream_setup()`, `pci_ide_stream_teardown()`, `pci_ide_stream_enable()`, `pci_ide_stream_disable()`, `pci_ide_init_host_bridge()`, `pci_ide_set_nr_streams()`, and `pci_ide_destroy()`. Important helper types are `struct stream_index`, `struct pci_ide_stream_id`, `struct pci_ide`, `struct pci_ide_partner`, and `struct pci_ide_regs`.

## Control Flow
Device init finds the IDE extended capability, requires Selective IDE, requires endpoints to have an IDE-capable root port, discovers link/selective stream counts and address-association block counts, claims any streams already active, and programs inactive stream IDs to the reserved ID. Stream allocation reserves a host-bridge stream, root-port selective stream index, and endpoint selective stream index, computes RID ranges including enabled VFs, and records downstream memory/prefetchable windows. Registration reserves the requested stream ID and creates a host-bridge sysfs link. Setup converts RID and address associations into config register writes for endpoint or root-port partner blocks, then writes control disabled but with stream ID/config fields. Enable sets the enable bit and requires the status state to become secure.

## State and Persistence Behavior
Per-device state includes `pdev->ide_cap`, stream counts, TEE/config limits, per-device IDA for stream indexes, and hardware selective/link stream registers. Host-bridge state includes stream count and IDAs for stream resources and stream IDs. `struct pci_ide` tracks partner setup/enable flags and a sysfs link name so `pci_ide_stream_release()` can unwind in reverse setup order.

## Dependencies and Integration Points
Depends on PCIe extended capability definitions, root-port lookup, SR-IOV helpers for VF RID ranges, bridge resource windows, IDA allocators, sysfs links, PCI config space writes, and host-bridge sysfs attribute groups.

## Risks
IDE setup is asymmetric between endpoint and root port and requires both sides to be programmed consistently. The code assumes a constant number of address-association blocks across selective streams and skips the rest otherwise. Active firmware-configured stream IDs are reserved opportunistically; failure aborts IDE initialization. `pci_ide_stream_enable()` leaves cleanup of failed secure-state entry to the caller. `pci_ide_stream_free()` appears to free `hb->ide_stream_ida` for `host_bridge_stream`, while allocation uses `hb->ide_stream_ida`; stream ID reservations separately use `ide_stream_ids_ida`.

## Test Signals
Validate IDE capability discovery on endpoints/root ports, pre-active stream reservation, host-bridge stream count override, stream alloc/register/setup/enable/disable/teardown/release, sysfs link creation/removal, SR-IOV RID range coverage, memory/prefetch window associations, secure-state failure, and cleanup under partial setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/ide.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/iomap.c -->
# sources/distributed-fs/ceph-client/drivers/pci/iomap.c

## Purpose
Provides default PCI BAR mapping helpers that return `__iomem` cookies for MMIO or I/O port BARs, plus an architecture-gated default `pci_iounmap()`.

## Important APIs, Types, and Functions
Exported functions are `pci_iomap_range()`, `pci_iomap_wc_range()`, `pci_iomap()`, `pci_iomap_wc()`, and conditionally `pci_iounmap()`.

## Control Flow
Mapping validates the BAR index, reads BAR start/length/flags, rejects zero or out-of-range offsets, clamps to `maxlen`, then maps I/O resources through `__pci_ioport_map()` or memory resources through `ioremap()`/`ioremap_wc()`. WC mapping rejects I/O port BARs. The default unmap treats generic fixed I/O-port mappings under `PCI_IOBASE` as no-op and otherwise calls `iounmap()`.

## State and Persistence Behavior
The file creates virtual mappings but stores no state itself. Mapping lifetime is owned by callers and must be released with the appropriate unmap helper.

## Dependencies and Integration Points
Depends on PCI resource helpers, `pci_bar_index_is_valid()`, architecture I/O mapping support, and core I/O remap APIs. It is used broadly by PCI drivers and subsystems that map BARs.

## Risks
Callers must not request invalid offsets or forget unmap. WC mapping on device memory can change ordering semantics and must match device requirements. The default `pci_iounmap()` intentionally preserves legacy architecture behavior and may not fit architectures with unusual I/O-port mapping rules.

## Test Signals
Map MMIO, WC MMIO, and I/O BARs; reject invalid BARs, zero starts, and offsets beyond BAR length; clamp max length; unmap on generic and non-generic I/O mapping architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/iomap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/iov.c -->
# sources/distributed-fs/ceph-client/drivers/pci/iov.c

## Purpose
Implements PCI SR-IOV support: capability initialization, VF BAR sizing/resource management, enabling/disabling VFs, creating/removing VF `pci_dev` objects, sysfs controls, VF MSI-X count hooks, state restore, and exported PF/VF helper APIs.

## Important APIs, Types, and Functions
Exported helpers include `pci_iov_virtfn_bus()`, `pci_iov_virtfn_devfn()`, `pci_iov_vf_id()`, `pci_iov_get_pf_drvdata()`, `pci_enable_sriov()`, `pci_disable_sriov()`, `pci_num_vf()`, `pci_vfs_assigned()`, `pci_sriov_set_totalvfs()`, `pci_sriov_get_totalvfs()`, `pci_sriov_configure_simple()`, `pci_iov_vf_bar_set_size()`, and `pci_iov_vf_bar_get_sizes()`. Core internal helpers are `sriov_init()`, `sriov_enable()`, `sriov_disable()`, `pci_iov_add_virtfn()`, `pci_iov_remove_virtfn()`, `pci_iov_update_resource()`, and restore helpers.

## Control Flow
Initialization finds the SR-IOV extended capability, disables any firmware-left VF Enable, sets ARI if needed, validates total VFs and page size, sizes VF BARs with VF Enable clear, scales PF VF BAR resources by total VFs, records offsets/stride/capabilities/link/VF ReBAR, marks the device as a PF, and computes maximum bus range. Enabling validates requested VF count/resources/bus range, enables VF BAR resources, creates dependency links when needed, calls arch enable hook, writes NumVFs and SR-IOV Control VF Enable/MSE, waits, creates VF devices and sysfs links, and records `num_VFs`. Disabling removes VFs, clears control bits, waits, calls arch disable hook, removes links, and resets NumVFs. Sysfs `sriov_numvfs` delegates to the PF driver's `sriov_configure()` under device and rescan/remove locks.

## State and Persistence Behavior
`struct pci_sriov` persists capability position, control word, total/driver-max/initial/current VF counts, offset/stride, VF BAR sizes, page size, VF device ID, dependency link, VF ReBAR capability, resource count, and autoprobe flag. VF `pci_dev`s hold `is_virtfn`, `physfn`, inherited resource slices, and sysfs `physfn`/`virtfnN` links. Hardware state includes SR-IOV control, NumVFs, system page size, VF BARs, and VF ReBAR size fields.

## Dependencies and Integration Points
Depends on PCI extended capability/resource sizing, bus creation/removal, sysfs attribute groups, MSI-related VF vector hooks, PCI driver callbacks (`sriov_configure`, `sriov_get_vf_total_msix`, `sriov_set_msix_vec_count`), arch hooks `pcibios_sriov_enable/disable`, ReBAR helpers, IOMMU assignment checks, and global PCI rescan/remove locking.

## Risks
SR-IOV enablement is resource- and topology-sensitive: VF BAR resources must be assigned for every implemented VF BAR and bus numbers must cover the highest VF. Partial VF creation must unwind already-created VFs. Sysfs vector count changes are blocked when a VF driver is bound, but PF driver callbacks still need strong validation. Restore order matters: ARI must be restored before NumVFs because offset/stride can depend on it. Drivers that remove with VFs still enabled are warned but can leave cleanup to later paths.

## Test Signals
Initialize PFs with varied total VFs, ARI, VF BAR sizes, page sizes, VF ReBAR; enable/disable via driver API and sysfs; resource/bus exhaustion failures; no-VF-scan mode; VF sysfs link creation/removal; VF driver autoprobe toggling; assigned VF refusal in `pci_sriov_configure_simple()`; suspend/resume restore; PF remove with VFs enabled; VF MSI-X count attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/iov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/irq.c -->
# sources/distributed-fs/ceph-client/drivers/pci/irq.c

## Purpose
Provides generic PCI IRQ utility functions: request/free wrappers around PCI interrupt vectors, INTx swizzling/mapping, runtime IRQ assignment, and shared INTx mask/unmask helpers.

## Important APIs, Types, and Functions
Exported APIs are `pci_request_irq()`, `pci_free_irq()`, `pci_common_swizzle()`, `pci_check_and_mask_intx()`, and `pci_check_and_unmask_intx()`. Other core functions include `pci_swizzle_interrupt_pin()`, `pci_get_interrupt_pin()`, `pci_assign_irq()`, and weak arch hooks `pcibios_penalize_isa_irq()`, `pcibios_alloc_irq()`, and `pcibios_free_irq()`.

## Control Flow
`pci_request_irq()` formats a device IRQ name, gets the Linux IRQ through `pci_irq_vector()`, and installs a shared threaded IRQ, adding `IRQF_ONESHOT` when only a thread handler is supplied. `pci_free_irq()` frees the IRQ and the allocated name. Swizzling walks bridges to root, applying slot-based INTx rotation unless ARI forces slot zero. `pci_assign_irq()` asks the host bridge's swizzle/map callbacks for a platform IRQ and writes it to `PCI_INTERRUPT_LINE`. INTx masking does one locked config dword read of Command+Status, checks pending state, and only toggles `PCI_COMMAND_INTX_DISABLE` when pending state matches the requested mask/unmask operation.

## State and Persistence Behavior
IRQ assignment writes `dev->irq` and the device's Interrupt Line config byte. `pci_request_irq()` allocates a persistent handler name freed by `pci_free_irq()`. INTx mask state persists in PCI Command until changed again.

## Dependencies and Integration Points
Depends on IRQ core, MSI/vector helper `pci_irq_vector()`, PCI host bridge `map_irq`/`swizzle_irq`, config-space bus ops, and the global raw `pci_lock`.

## Risks
`dev_id` must be unique and non-NULL for shared IRQs. The INTx check/mask helper assumes Command and Status can be read atomically as one dword at aligned offsets, enforced by build checks. Swizzling correctness depends on bridge topology and ARI state. Drivers must disable device interrupt generation before `pci_free_irq()`.

## Test Signals
Request/free MSI, MSI-X, and INTx vectors; threaded-only handlers; IRQ name allocation failure; INTx swizzle behind multiple bridges with and without ARI; platform IRQ assignment; shared INTx mask/unmask with pending and non-pending status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/mmap.c -->
# sources/distributed-fs/ceph-client/drivers/pci/mmap.c

## Purpose
Implements generic PCI resource mmap support for sysfs/procfs paths on architectures that use the generic PCI mmap helpers.

## Important APIs, Types, and Functions
The file conditionally defines `pci_mmap_resource_range()` and `pci_mmap_fits()`. It also defines `pci_phys_vm_ops` with optional `generic_access_phys`.

## Control Flow
`pci_mmap_resource_range()` validates that the requested VMA page range fits inside the BAR, chooses device or write-combining page protection, converts I/O BAR offsets through `pci_iobar_pfn()` or memory BAR offsets by adding the BAR start PFN, attaches physical VM ops, and calls `io_remap_pfn_range()`. `pci_mmap_fits()` checks whether a requested sysfs/procfs mmap page range lies within the PCI resource, using `pci_resource_to_user()` for procfs address semantics.

## State and Persistence Behavior
The file stores no persistent state. It modifies VMA page offset, page protection, and VM ops for the mapping lifetime.

## Dependencies and Integration Points
Depends on architecture config symbols, mm/VMA APIs, PCI resource helpers, `pci_iobar_pfn()`, and optional sysfs/procfs mmap interfaces.

## Risks
Incorrect page-range validation could expose memory outside a BAR. I/O BAR and memory BAR offset semantics differ between sysfs and procfs. Write-combining mappings change ordering and must be requested intentionally.

## Test Signals
Mmap memory and I/O BARs through sysfs/procfs, reject over-length VMAs, validate write-combine protection, test `generic_access_phys` if enabled, and verify procfs address conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pci/msi/Makefile

## Purpose
Defines which PCI MSI implementation objects are built for each kernel configuration.

## Important APIs, Types, and Functions
The Makefile adds `pcidev_msi.o` whenever `CONFIG_PCI` is enabled, adds `api.o`, `msi.o`, and `irqdomain.o` for `CONFIG_PCI_MSI`, and adds `legacy.o` for `CONFIG_PCI_MSI_ARCH_FALLBACKS`.

## Control Flow
There is no runtime control flow. Kbuild uses these object lists to decide which MSI core and exported APIs are linked.

## State and Persistence Behavior
No runtime state exists. Build configuration determines which symbols are available in the resulting kernel.

## Dependencies and Integration Points
Integrates with Kbuild and the PCI/MSI source files in the same directory. `api.o` contains the driver-facing exported APIs, while `msi.o`, `irqdomain.o`, and `legacy.o` provide implementation backends.

## Risks
Incorrect object gating can expose APIs without backends or omit required fallback support. `pcidev_msi.o` being tied to `CONFIG_PCI` rather than `CONFIG_PCI_MSI` indicates some per-device MSI scaffolding is needed even when full MSI support is disabled.

## Test Signals
Build kernels with `CONFIG_PCI`, with and without `CONFIG_PCI_MSI`, and with/without architecture fallback support; check link symbols for MSI APIs and fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/api.c -->
# sources/distributed-fs/ceph-client/drivers/pci/msi/api.c

## Purpose
Exports the driver-facing PCI MSI/MSI-X interrupt APIs. It wraps internal MSI allocation/shutdown logic, supports legacy and modern vector allocation interfaces, dynamic MSI-X vector allocation, affinity queries, cleanup, restore, and global MSI-enabled reporting.

## Important APIs, Types, and Functions
Exported APIs include `pci_enable_msi()`, `pci_disable_msi()`, `pci_msix_vec_count()`, `pci_enable_msix_range()`, `pci_msix_can_alloc_dyn()`, `pci_msix_alloc_irq_at()`, `pci_msix_free_irq()`, `pci_disable_msix()`, `pci_alloc_irq_vectors()`, `pci_alloc_irq_vectors_affinity()`, `pci_irq_vector()`, `pci_irq_get_affinity()`, `pci_free_irq_vectors()`, `pci_restore_msi_state()`, and `pci_msi_enabled()`.

## Control Flow
Legacy MSI enables exactly one vector through `__pci_enable_msi_range()` and stores the Linux IRQ at `dev->irq`; disable shuts down MSI under the MSI descriptor lock and frees MSI IRQs. Legacy MSI-X range allocation validates entries through internal helpers and returns vector counts. Modern vector allocation tries MSI-X first, then MSI, then INTx if allowed and only one vector is required; affinity setup is passed to MSI backends or used to create a single INTx affinity mask. Dynamic MSI-X allocation first verifies MSI-X is enabled and the MSI domain supports dynamic allocation, then allocates or frees one table index. Vector lookup returns `dev->irq` for INTx or MSI descriptor IRQs for MSI/MSI-X.

## State and Persistence Behavior
The APIs mutate `dev->msi_enabled`, `dev->msix_enabled`, MSI descriptors, MSI/MSI-X hardware state, and sometimes `dev->irq`. `pci_restore_msi_state()` writes cached MSI/MSI-X state back after resume or reset. `pci_msi_enabled()` reflects global `pci_msi_enable`.

## Dependencies and Integration Points
Depends on internal `msi.h` helpers, Linux IRQ/MSI domains, IRQ affinity descriptors, MSI descriptor locking, PCI INTx control, and device MSI domain feature flags. It is the main exported surface used by PCI drivers and hotplug code such as PowerNV/SHPC interrupt setup.

## Risks
Legacy MSI/MSI-X APIs coexist with `pci_alloc_irq_vectors()`; drivers must not mix cleanup paths. `pci_free_irq_vectors()` warns against use after `pcim_enable_device()` because managed cleanup can double-free. Dynamic MSI-X is domain-feature-dependent and returns errors in `msi_map.index`. Affinity can be NULL for MSI vectors allocated without affinity descriptors. INTx fallback only works for `min_vecs == 1`.

## Test Signals
Enable/disable legacy MSI, legacy MSI-X range, modern MSI-X/MSI/INTx allocation with and without affinity, vector lookup bounds, affinity query for MSI/MSI-X/INTx, dynamic MSI-X allocate/free, global `pci=nomsi`, resume/reset restore, and managed-device cleanup interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/msi/api.c -->
