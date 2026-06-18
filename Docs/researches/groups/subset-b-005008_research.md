# subset-b-005008 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.c

## Purpose
Implements the Intel/Ziatech ZT5550 CompactPCI host-controller glue for the generic CompactPCI hotplug core. It probes the Ziatech controller PCI function, maps its MMIO registers, exposes ENUM# status and optional IRQ handling through `struct cpci_hp_controller_ops`, registers the CompactPCI bus segment, and starts/stops the shared `cpci_hotplug` machinery.

## Important APIs, Types, and Functions
Module parameters are `debug` and `poll`; `poll` suppresses IRQ ops and forces ENUM# polling. The key statics are `zt5550_hpc_ops`, `zt5550_hpc`, `bus0_dev`, `bus0`, `hc_dev`, `hc_registers`, and CSR pointers such as `csr_int_status` and `csr_int_mask`. Important routines are `zt5550_hc_config()`, `zt5550_hc_cleanup()`, `zt5550_hc_query_enum()`, `zt5550_hc_check_irq()`, `zt5550_hc_enable_irq()`, `zt5550_hc_disable_irq()`, `zt5550_hc_init_one()`, `zt5550_hc_remove_one()`, `zt5550_init()`, and `zt5550_exit()`. The PCI driver matches `PCI_VENDOR_ID_ZIATECH` and `PCI_DEVICE_ID_ZIATECH_5550_HC`.

## Control Flow
Module init reserves the legacy ENUM port and registers `zt5550_hc_driver`. Probe enables the HC PCI device, reserves and maps BAR 1, computes direct and indexed CSR pointers, masks indexed host/fault/serial interrupts and direct timer/ENUM interrupts, fills `zt5550_hpc` with query and optional IRQ callbacks, registers the controller with `cpci_hp_register_controller()`, finds the first DEC 21154 bridge as the CompactPCI bus, registers slots `0x0a` through `0x0f` with `cpci_hp_register_bus()`, then starts the generic core with `cpci_hp_start()`. Remove reverses this order by stopping the core, unregistering the bus/controller, and unmapping/disabling the HC.

## State and Persistence Behavior
State is module-global and in-memory only. The driver assumes a single HC chip: a second probe fails while `hc_dev` is set. The controller MMIO mapping and CSR pointer aliases persist from probe until remove. ENUM# is read from I/O port `0xe1` on every query. Interrupt enablement is persisted in the hardware direct interrupt mask register but no durable storage is used.

## Dependencies and Integration Points
Depends on Linux PCI, I/O port reservation, MMIO mapping, interrupt flags, and the generic `cpci_hotplug` controller/bus APIs. It relies on a DEC 21154 bridge being discoverable and on ZT5550-specific register definitions from `cpcihp_zt5550.h`. Its IRQ callbacks are consumed by the CompactPCI core, which owns the actual slot processing.

## Risks
The single-controller assumption and "first DEC 21154" bus discovery are hardware-topology specific. Cleanup does not clear `hc_dev`, so rebind behavior depends on module lifetime and PCI driver expectations. Direct pointer arithmetic on `void __iomem *` and hard-coded BAR/port/register choices are architecture and device specific. Interrupt handling treats any nonzero `CSR_INTSTAT` as this device's shared IRQ claim.

## Test Signals
Useful signals include successful module load with ENUM port reservation, probe of the ZT5550 PCI ID, BAR 1 reservation/ioremap, correct interrupt mask writes, controller registration, DEC 21154 subordinate bus discovery, cPCI slots `0x0a`-`0x0f` appearing in the hotplug core, IRQ mode versus `poll=1`, ENUM# event detection, remove/unload without leaked regions, and failure injection for missing bridge, duplicate HC, and registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.h

## Purpose
Defines the ZT5550 CompactPCI host-controller register offsets and bit masks used by `cpcihp_zt5550.c`. It is the hardware register contract for direct CSRs, indexed host-controller CSRs, interrupt masks, and the legacy ENUM# input port.

## Important APIs, Types, and Functions
There are no functions or types. Direct register offsets include `CSR_HCINDEX`, `CSR_HCDATA`, `CSR_INTSTAT`, `CSR_INTMASK`, counter command/count registers, and direct interrupt masks such as `ENUM_INT_MASK` and `ALL_DIRECT_INTS_MASK`. Indexed-register selectors include `HC_INT_MASK_REG`, `HC_STATUS_REG`, `HC_CMD_REG`, arbiter/isolation/fault/watchdog/diagnostic/serial registers, and `ALL_INDEXED_INTS_MASK`. `ENUM_PORT` and `ENUM_MASK` define the digital I/O source for ENUM#.

## Control Flow
The header has no runtime control flow. The C file writes `HC_INT_MASK_REG` via the index/data pair to mask indexed interrupts, writes `CSR_INTMASK` to mask or unmask direct ENUM interrupts, reads `CSR_INTSTAT` in the shared IRQ checker, and reads `ENUM_PORT` via `inb_p()` to answer core ENUM queries.

## State and Persistence Behavior
These constants encode hardware state locations. Changing them changes which MMIO bytes and I/O port the driver reads/writes. The header itself stores no state and has no persistence.

## Dependencies and Integration Points
Integrated only by the ZT5550 driver and indirectly by the generic cPCI hotplug core through the driver's operations. Values are tied to the ZT5550 HC data sheet and to the Linux PCI/I/O accessors used in the C implementation.

## Risks
The register ABI is brittle: wrong offsets or masks can leave interrupts enabled, disable required events, or read the wrong ENUM# state. `ENUM_PORT` is a fixed legacy I/O port and can conflict with platform assumptions if reused outside the intended board.

## Test Signals
Compile coverage of `cpcihp_zt5550.c`, MMIO traces showing expected writes to `HC_INT_MASK_REG` and `CSR_INTMASK`, ENUM# reads changing with hardware events, IRQ masking/unmasking behavior, and no I/O port conflicts during module init are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpcihp_zt5550.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp.h

## Purpose
Provides the shared ABI, state structures, constants, prototypes, and MMIO helper routines for the Compaq/HP PCI hotplug controller driver. It binds `cpqphp_core.c`, `cpqphp_ctrl.c`, `cpqphp_pci.c`, `cpqphp_nvram.c`, and `cpqphp_sysfs.c` into one driver stack.

## Important APIs, Types, and Functions
Important packed hardware/firmware layouts include `struct smbios_system_slot`, `struct smbios_entry_point`, `struct ctrl_reg`, `struct hrt`, and `struct slot_rt`, with matching offset enums for direct byte/word access through `readb/readw/readl`. Runtime structures are `struct pci_func` for one PCI function and saved resources/config, `struct slot` for hotplug-core slot state, `struct pci_resource` for simple resource lists, `struct event_info`, `struct controller`, `struct irq_mapping`, and `struct resource_lists`. It declares cross-file entry points for debugfs, event handling, resource sorting, PCI configuration, board add/remove, NVRAM-assisted resource discovery, and device configure/unconfigure. Inline helpers control LEDs, slot enable/power bits, SOGO commits, speed detection, latch/presence/power status, and wait for controller completion.

## Control Flow
The header defines the shared control vocabulary. Core probe fills `struct controller`, registers `struct slot` instances with `cpqphp_hotplug_slot_ops`, and uses MMIO helpers to initialize slots. Interrupts in `cpqphp_ctrl.c` enqueue `event_info` records, and the kthread calls exported SI/SS functions. PCI helpers allocate and return `pci_resource` nodes through `resource_lists`. Hotplug-core callbacks use `to_slot()` and then route through `cpqhp_get_bus_dev()`, `cpqhp_slot_find()`, and controller operations.

## State and Persistence Behavior
The central persistent runtime state is the controller list `cpqhp_ctrl_list`, per-bus function lists `cpqhp_slot_list[256]`, IRQ routing table `cpqhp_routing_table`, per-controller resource pools, per-function saved config space and BAR length/type arrays, event queues, LED/slot state, and presence/switch snapshots. The header also exposes optional NVRAM persistence hooks through `cpqphp_nvram.h`, but durable storage is implemented elsewhere.

## Dependencies and Integration Points
Depends on Linux interrupt, MMIO, delay, mutex, signal, PCI, PCI hotplug, and x86 IRQ routing table definitions. It integrates with the PCI hotplug core through `struct hotplug_slot`, with debugfs through controller dentries, with Compaq ROM/HRT parsing through packed table definitions, and with x86 routing helpers for legacy IRQ programming.

## Risks
Packed layout and offset enums are hardware ABI. Inline MMIO helpers assume slot indexes and bit placements that match Compaq/Intel HPC registers. Global lists are manually managed and shared across interrupt, kthread, timer, hotplug-core, and teardown paths. `wait_for_ctrl_irq()` sleeps a fixed interval and only reports signals, so hardware completion semantics are weak. Resource nodes are raw singly linked lists, making ownership bugs easy.

## Test Signals
Build all `cpqphp` translation units together, probe supported Compaq/Intel controllers, verify slot registration/status callbacks, LED and power bit changes, event queue processing, resource list sorting/combining, IRQ routing table discovery, NVRAM enabled/disabled builds, debugfs creation/removal, and teardown of all global lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_core.c

## Purpose
Implements Compaq PCI hotplug module and PCI-driver lifecycle: controller discovery, SMBIOS and routing-table setup, MMIO/IRQ initialization, hotplug slot registration, initial slot power policy, debugfs registration, and module teardown.

## Important APIs, Types, and Functions
Exports global driver state `cpqhp_debug`, `cpqhp_legacy_mode`, `cpqhp_ctrl_list`, `cpqhp_slot_list`, and `cpqhp_routing_table`. Important helpers include `detect_SMBIOS_pointer()`, `init_SERR()`, `init_cpqhp_routing_table()`, `get_SMBIOS_entry()`, `ctrl_slot_cleanup()`, `get_slot_mapping()`, `cpqhp_set_attention_status()`, hotplug callbacks `process_SI()` and `process_SS()`, `ctrl_slot_setup()`, `one_time_init()`, `cpqhpc_probe()`, `unload_cpqphpd()`, `cpqhpc_init()`, and `cpqhpc_cleanup()`.

## Control Flow
Module init sets `cpqhp_debug`, creates the `cpqhp` debugfs root, and registers a PCI driver matching PCI hotplug-controller class devices. Probe enables a controller bridge, validates vendor/revision/subsystem capability bits, allocates a controller, duplicates the parent bus object for config-space probing, starts one-time global services, reserves and maps BAR 0, discovers bus speed, maps the first physical slot through the IRQ routing table, saves existing PCI config, discovers add resources from ROM/HRT/NVRAM, registers every physical slot with the PCI hotplug core, masks/clears interrupts, requests the shared controller IRQ, enables SOGO and SERR behavior, saves initial presence/switch snapshots, optionally powers off empty slots, initializes SERR, and creates a debugfs file. Teardown stores NVRAM, disables interrupts/SERR, deregisters slots, frees IRQ/MMIO/resources/function lists, stops the event thread, unmaps ROM/SMBIOS, unregisters the PCI driver, and removes debugfs.

## State and Persistence Behavior
Global one-time state includes ROM and SMBIOS mappings, routing table, event thread, and initialized flag. Per-controller state includes capability flags, resource pools, slot linked list, event queue, current interrupt comparison word, copied bus, MMIO base, IRQ, and debugfs dentry. Per-function state saved by `cpqhp_save_config()` persists original config space and resource ownership for replace/remove flows. If NVRAM support is built, resource-list state can be loaded and stored across module lifetimes.

## Dependencies and Integration Points
Depends on PCI core driver binding, x86 routing table APIs, ioremap of legacy ROM and SMBIOS table addresses, PCI hotplug core registration, controller IRQ handling from `cpqphp_ctrl.c`, resource discovery/configuration from `cpqphp_pci.c`, NVRAM hooks, and debugfs helpers.

## Risks
Probe is tightly coupled to old Compaq/Intel subsystem IDs and x86 firmware tables. Error paths after slot registration can leak already registered slots because `ctrl_slot_setup()` only returns the failing allocation path. The PCI driver has no `.remove` callback; cleanup is module-wide. It copies and mutates a `struct pci_bus`, which is fragile against PCI-core changes. One-time global initialization is shared across all controllers and only partially rolled back on later probe failures.

## Test Signals
Probe supported and unsupported subsystem IDs, failure injection through each probe stage, SMBIOS pointer/table mapping, slot name/number registration, IRQ request and interrupt completion wakeups, initial empty-slot power-off with `power_mode=0`, `power_mode=1` behavior, debugfs file creation, NVRAM store on unload, and module unload after multiple controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_ctrl.c

## Purpose
Contains the Compaq hotplug controller event engine and resource allocator. It handles hardware interrupts, switch/presence/power-fault events, pushbutton delay semantics, board add/replace/remove, bus speed changes, resource splitting/combining, recursive bridge configuration, and controller hardware tests.

## Important APIs, Types, and Functions
Public functions are `cpqhp_ctrl_intr()`, `cpqhp_slot_create()`, `cpqhp_slot_find()`, `cpqhp_resource_sort_and_combine()`, `cpqhp_event_start_thread()`, `cpqhp_event_stop_thread()`, `cpqhp_pushbutton_thread()`, `cpqhp_process_SI()`, `cpqhp_process_SS()`, and `cpqhp_hardware_test()`. Key internal routines include `handle_switch_change()`, `handle_presence_change()`, `handle_power_fault()`, resource selection helpers `get_io_resource()`, `get_resource()`, `get_max_resource()`, bridge split helpers, `set_controller_speed()`, `board_replaced()`, `board_added()`, `remove_board()`, `event_thread()`, `interrupt_event_handler()`, `configure_new_device()`, and `configure_new_function()`.

## Control Flow
The IRQ handler checks SOGO completion and general input interrupts, clears hardware bits, diffs `INT_INPUT_CLEAR` against `ctrl_int_comp`, converts switch/presence/power changes into `event_queue` entries, handles reset completion, and wakes the event kthread. The kthread either runs a pending pushbutton timer action or drains all controller event queues. Button releases blink the green LED and arm a five-second timer; cancellation restores LED state. Timer expiry calls SI for power-on/add or SS for power-off/remove. Board add powers the slot briefly to read adapter speed, may change segment speed, powers off, then enables the slot, configures resources and devices, saves slot config, and turns the green LED on. Remove unconfigures devices, saves or returns resources, powers down, and recreates an empty placeholder.

## State and Persistence Behavior
State is kept in `cpqhp_event_thread`, `pushbutton_pending`, each controller's circular ten-entry `event_queue`, slot timer/state fields, `pci_func` presence/switch/status/configured flags, resource lists, and PCI config-space snapshots. Resource allocation mutates controller free pools and function-owned lists; remove returns them when add support is available. No direct durable persistence is done here, but its resource-list mutations are the data later stored by NVRAM teardown.

## Dependencies and Integration Points
Depends on controller MMIO helpers from `cpqphp.h`, PCI config-space access, PCI hotplug-core callbacks from `cpqphp_core.c`, Linux kthreads/timers/wait queues, and PCI-core scan/remove helpers via `cpqphp_pci.c`. Legacy IRQ programming calls `cpqhp_set_irq()` for direct devices and bridge interrupt swizzling.

## Risks
The event queue has fixed length ten with overwrite-style modulo advancement and no locking in enqueue/dequeue paths. Resource allocation is hand-written and assumes 32-bit BARs, specific bridge windows, power-of-two sizes, and x86-era IRQ behavior. Several config writes ignore intermediate `rc` values. Pushbutton timer state is global, so concurrent button timers can collide. Bus speed changes temporarily disable slots and LEDs, so errors can leave hardware in surprising states.

## Test Signals
Interrupt diff handling, switch open/close, presence insert/remove, power-fault set/clear, button press/release/cancel timing, SI/SS sysfs operations, add of normal and multifunction devices, bridge add with subordinate devices, remove with resource return, replace validation, speed changes across 33/66/PCI-X modes, event thread stop on unload, resource sort/combine correctness, and ENOMEM/error-path rollback are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.c

## Purpose
Implements optional Compaq NVRAM persistence for hotplug resource lists. It reads and invalidates a BIOS environment variable at startup, overlays persisted free resource pools onto the active controller, and writes current free resources back on module unload through a Compaq INT15 ROM entry point.

## Important APIs, Types, and Functions
Important constants are `ROM_INT15_PHY_ADDR`, `READ_EV`, and `WRITE_EV`. Persistent formats are `struct ev_hrt_header` and `struct ev_hrt_ctrl`; `struct register_foo` and `struct all_reg` describe the low-level BIOS call register model but are not used by the inline assembly wrapper. Global state includes `evbuffer_init`, `evbuffer_length`, `evbuffer[1024]`, `compaq_int15_entry_point`, and `int15_lock`. Public functions are `compaq_nvram_init()`, `compaq_nvram_load()`, and `compaq_nvram_store()`. Internal helpers are `add_byte()`, `add_dword()`, `check_for_compaq_ROM()`, `access_EV()`, `load_HRT()`, and `store_HRT()`.

## Control Flow
Core probe calls `compaq_nvram_init()` after ROM mapping to compute the INT15 entry pointer. Resource discovery calls `compaq_nvram_load()` once globally; it reads `CQTHPS`, invalidates the old variable by writing `0xff`, validates version/controller identity, and appends persisted memory, prefetchable memory, I/O, and bus nodes to the matching controller's free lists. Module unload calls `compaq_nvram_store()`, which serializes each controller identity and resource-list counts/data into `evbuffer` and writes `CQTHPS` back through `access_EV()`.

## State and Persistence Behavior
This is the only Compaq file in the set that intentionally persists driver state beyond runtime. The persisted state is not slot config, but free resource pools per controller. `evbuffer_init` prevents repeated ROM reads. `evbuffer_length` bounds parsing, and the 1024-byte buffer caps serialized state. `access_EV()` serializes firmware calls with a spinlock and disables interrupts around the far call-like ROM entry invocation.

## Dependencies and Integration Points
Depends on `cpqphp.h` global controller/resource structures, the legacy ROM mapping from `cpqphp_core.c`, Compaq ROM OEM string at `0xffea`, x86 inline assembly, and BIOS support for `READ_EV`/`WRITE_EV` environment variable operations. It is compiled only when `CONFIG_HOTPLUG_PCI_COMPAQ_NVRAM` enables the real declarations from `cpqphp_nvram.h`.

## Risks
Calling BIOS code from the kernel is architecture- and firmware-sensitive. The parser casts unaligned bytes to `u32 *`, depends on a small fixed buffer, and trusts count fields except for length checks. `evbuffer_length` is `u8`, so a 1024-byte transfer length truncates. Persisted stale or corrupt resources can affect future hot-add allocation. Firmware call failures fall back to ROM/HRT resources but can silently lose previous resource state.

## Test Signals
Build with and without `CONFIG_HOTPLUG_PCI_COMPAQ_NVRAM`, Compaq ROM detection, INT15 READ/WRITE success and failure, invalid/corrupt/truncated `CQTHPS`, version 1 versus version 2 data, matching and nonmatching controller identities, resource-list sort after load, unload store with multiple controllers, and behavior when serialized data exceeds 1024 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.h

## Purpose
Provides the compile-time interface for optional Compaq NVRAM support. It either declares the real NVRAM load/store functions or supplies no-op inline stubs when NVRAM support is disabled.

## Important APIs, Types, and Functions
The API is `compaq_nvram_init(void __iomem *rom_start)`, `compaq_nvram_load(void __iomem *rom_start, struct controller *ctrl)`, and `compaq_nvram_store(void __iomem *rom_start)`. Without `CONFIG_HOTPLUG_PCI_COMPAQ_NVRAM`, init is empty and load/store return success.

## Control Flow
`cpqphp_core.c` calls these hooks unconditionally. The header makes that code independent of the Kconfig option: disabled builds proceed with ROM/HRT resource discovery and skip persistent resource overlay/store, while enabled builds link to `cpqphp_nvram.c`.

## State and Persistence Behavior
The header itself has no state. Its build-time branch determines whether resource-list persistence exists at all. In disabled builds, no durable state is read or written and store reports success.

## Dependencies and Integration Points
Depends on `struct controller` from `cpqphp.h` being visible to callers and on `void __iomem *` ROM mappings supplied by the core. It is included by both `cpqphp_core.c` and `cpqphp_pci.c`, though persistence is implemented only in the C file.

## Risks
The no-op stubs make persistence failures impossible to distinguish from intentionally disabled support. Callers must not assume persisted resources were loaded just because `compaq_nvram_load()` returns zero in disabled builds.

## Test Signals
Compile both Kconfig paths, verify no unresolved symbols when disabled, verify real symbols are linked when enabled, and check that resource discovery still works when persistence is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_nvram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_pci.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_pci.c

## Purpose
Implements Compaq PCI configuration and firmware-resource helpers. It scans devices, creates/removes Linux `pci_dev` objects, programs legacy IRQ routing, saves existing config space, validates replacement boards, discovers add resources from the Hot Plug Resource Table, and frees/returns resource nodes.

## Important APIs, Types, and Functions
Globals are `cpqhp_nic_irq`, `cpqhp_disk_irq`, and `unused_IRQ`. Public functions include `cpqhp_configure_device()`, `cpqhp_unconfigure_device()`, `cpqhp_set_irq()`, `cpqhp_get_bus_dev()`, `cpqhp_save_config()`, `cpqhp_save_slot_config()`, `cpqhp_save_base_addr_length()`, `cpqhp_save_used_resources()`, `cpqhp_configure_board()`, `cpqhp_valid_replace()`, `cpqhp_find_available_resources()`, `cpqhp_return_board_resources()`, `cpqhp_destroy_resource_list()`, and `cpqhp_destroy_board_resources()`. Internal helpers are `detect_HRT_floating_pointer()`, `PCI_ScanBusForNonBridge()`, and `PCI_GetBusDevHelper()`.

## Control Flow
`cpqhp_configure_device()` gets or scans a `pci_dev` under `pci_lock_rescan_remove()`, adds devices, and handles bridge children. `cpqhp_unconfigure_device()` stops/removes all functions for a device. During probe, `cpqhp_save_config()` recursively snapshots config space and creates `pci_func` entries. `cpqhp_find_available_resources()` locates `$HRT`, loads optional NVRAM, parses slot resource entries, assigns resource nodes either to controller free pools or occupied functions, and sorts pools. Add/remove paths use BAR probing in `cpqhp_save_used_resources()` and `cpqphp_ctrl.c` allocation to track ownership. Replace paths use `cpqhp_valid_replace()` and `cpqhp_configure_board()` to confirm and restore the same device tree.

## State and Persistence Behavior
This file builds the in-memory representation that NVRAM may persist: controller free resource lists and function-owned resource lists. It also stores `config_space[0x20]`, `base_length[]`, `base_type[]`, `pci_dev`, and legacy IRQ defaults. Resource return destroys ownership on function removal and merges nodes back into controller pools. Durable storage is delegated to `compaq_nvram_load/store()`.

## Dependencies and Integration Points
Depends on PCI core scan/remove APIs, PCI config-space accessors, x86 `pcibios_set_irq_routing()`, ELCR I/O ports, IRQ routing table from the core file, HRT/slot structures from `cpqphp.h`, and resource allocation logic in `cpqphp_ctrl.c`.

## Risks
Many routines directly write all-ones to BARs and restore values, which is disruptive if used on active devices without proper quiescing. The code assumes domain 0, 32-bit resource windows, specific HRT scaling, and incomplete bridge recursion in `PCI_ScanBusForNonBridge()`. `cpqhp_set_irq()` hand-allocates fake PCI objects and touches x86 ELCR ports. Several paths return generic `1` or ignore read/write failures, making diagnostics weak.

## Test Signals
HRT detection and parsing, NVRAM overlay, empty versus populated slot resource assignment, save config for bridges and multifunction devices, add/remove Linux `pci_dev` objects, legacy IRQ programming, replacement mismatch cases, BAR length probing, resource return/merge, bridge subordinate resource handling, and module unload leak checks are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_sysfs.c

## Purpose
Despite its filename, implements debugfs diagnostics for the Compaq hotplug driver. It exposes one read-only debugfs file per controller showing free controller resources and resources assigned to devices in each slot.

## Important APIs, Types, and Functions
Important pieces are `cpqphp_mutex`, `show_ctrl()`, `show_dev()`, `spew_debug_info()`, `struct ctrl_dbg`, `MAX_OUTPUT`, file operations `open()`, `lseek()`, `read()`, `release()`, `debug_ops`, and public lifecycle functions `cpqhp_initialize_debugfs()`, `cpqhp_shutdown_debugfs()`, `cpqhp_create_debugfs_files()`, and `cpqhp_remove_debugfs_files()`.

## Control Flow
Module init creates `/sys/kernel/debug/cpqhp`. Controller probe calls `cpqhp_create_debugfs_files()` with a file named after the PCI device. On open, the file allocates a `ctrl_dbg` buffer, snapshots formatted controller and per-slot resource data under a mutex, and stores it in `file->private_data`. Read uses `simple_read_from_buffer()`, lseek uses `fixed_size_llseek()`, and release frees the snapshot. Controller cleanup removes the file; module cleanup removes the root dentry.

## State and Persistence Behavior
Debug output is generated as an open-time snapshot into a `4 * PAGE_SIZE` heap buffer. It does not persist resource state or update live while the file is held open. Each controller stores its created dentry in `ctrl->dentry`; `root` is module-global.

## Dependencies and Integration Points
Depends on debugfs, file operations, controller/resource structures from `cpqphp.h`, `cpqhp_slot_find()` from the control file, and probe/cleanup calls from `cpqphp_core.c`.

## Risks
Formatting uses `sprintf()` into a fixed buffer and caps each list at eleven entries, so large resource lists can be truncated and the buffer relies on implicit size sufficiency. The global mutex protects snapshot allocation/formatting but does not lock controller resource mutation comprehensively. `debugfs_remove(root)` is nonrecursive compared with `debugfs_remove_recursive()`, so children must be removed first.

## Test Signals
Debugfs root creation/removal, per-controller file creation/removal, open/read/lseek/release behavior, output for free and assigned resources, truncation behavior with many resource nodes, concurrent hotplug while reading, and cleanup while files are not open are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/cpqphp_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp.h

## Purpose
Defines the shared contract for the IBM PCI hotplug driver: EBDA/RIO firmware table layouts, resource manager structures, HPC command/status constants, slot/controller runtime objects, and cross-file prototypes.

## Important APIs, Types, and Functions
Firmware structures include `rio_table_hdr`, `scal_detail`, `rio_detail`, `opt_rio`, `ebda_hpc_list`, `ebda_hpc_slot`, `ebda_hpc_bus`, controller access unions, `ebda_rsrc_list`, `ebda_pci_rsrc`, and `bus_info`. Resource structures are `range_node`, `bus_node`, `resource_node`, and `res_needed`. Runtime objects are IBM-specific `struct pci_func`, `struct slot`, and `struct controller`. It defines HPC write commands (`HPC_SLOT_ON`, `HPC_SLOT_OFF`, bus mode commands, attention LED commands), read commands, status bits, decode macros such as `SLOT_PRESENT()`, `SLOT_PWRGD()`, `CURRENT_BUS_SPEED()`, `CTLR_RESULT()`, and operation prototypes for EBDA, resources, HPC access, polling, PCI configure/unconfigure, and hotplug operations.

## Control Flow
The header has no standalone execution, but all IBM driver files use its state machine. EBDA parsing populates controller, slot, bus, and resource lists. Core validation reads slot status through `ibmphp_hpc_readslot()`, powers slots through `ibmphp_hpc_writeslot()`, allocates resources through `ibmphp_*rsrc*`, and registers `ibmphp_hotplug_slot_ops` with the hotplug core.

## State and Persistence Behavior
Runtime state is list-based: global `ibmphp_slot_head` and EBDA resource/controller lists, per-slot status/ext_status/busstatus, per-slot resource-owned `pci_func` chains, per-controller command/status/options, and per-bus speed/slot-limit data. The header models firmware-derived EBDA data but does not itself persist changes back to firmware.

## Dependencies and Integration Points
Depends on Linux PCI hotplug, PCI register constants, list heads, and x86-era firmware/IRQ concepts. It integrates `ibmphp_core.c` with other IBM hotplug implementation files for EBDA access, HPC I/O, resource management, and PCI card configuration.

## Risks
The header mixes firmware table ABI, controller command protocol, resource allocator internals, and hotplug-core state. Macro decoding must exactly match HPC status bit semantics; wrong interpretation can power unsafe slots or reject valid operations. Several structures assume domain 0, 32-bit resources, and old PCI/PCI-X speed models. The `HPC_CTLR_RESULE2` typo is part of the existing bit definitions and should be changed only with care.

## Test Signals
Compile the whole IBM hotplug driver, EBDA table parsing, slot/controller list population, resource manager initialization, status macro decoding, bus speed/mode detection, HPC command completion result decoding, hotplug slot registration, and PCI/PCI-X capability reporting are key validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp_core.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp_core.c

## Purpose
Implements the IBM PCI hotplug core lifecycle and hotplug-slot operations. It initializes EBDA/resource/controller data, registers slots, reads and updates HPC status, powers slots on/off, sets bus speed/mode, configures/unconfigures PCI cards, handles attention/status callbacks, and cleans up on module exit.

## Important APIs, Types, and Functions
Exports `ibmphp_debug`, `ibmphp_pci_bus`, `ibmphp_init_devno()`, `ibmphp_update_slot_info()`, `ibmphp_do_disable_slot()`, and `ibmphp_hotplug_slot_ops`. Important internals include `get_cur_bus_info()`, `slot_update()`, `get_max_slots()`, `power_on()`, `power_off()`, status callbacks, `get_max_bus_speed()`, `init_ops()`, `validate()`, `ibm_slot_find()`, `free_slots()`, `ibm_unconfigure_device()`, `bus_structure_fixup()`, `ibm_configure_device()`, `is_bus_empty()`, `set_bus()`, `check_limitations()`, `enable_slot()`, `ibmphp_disable_slot()`, `ibmphp_unload()`, `ibmphp_init()`, and `ibmphp_exit()`.

## Control Flow
Module init copies root bus ops into `ibmphp_pci_bus`, sets debug, parses EBDA, initializes resources, computes `max_slots`, registers PCI hotplug slots, runs `init_ops()` to read controller revisions/options/status, update bus speeds, and power off empty powered slots, then starts the HPC polling thread. Enable validates that a present, latched, unpowered slot can be enabled; blinks attention, sets bus speed/mode if the segment is empty, checks bus electrical limits, powers on, validates power-good and speed/mode status, allocates a `pci_func`, configures card resources, scans Linux PCI devices, turns attention off, and updates PCI bus speed. Disable validates if requested by user, blinks attention, creates a boot-time function record if needed, removes Linux devices, unconfigures resources when allowed, powers off, clears attention, and updates slot/bus info. Exit stops polling and frees slots, resources, EBDA queues, and the copied bus.

## State and Persistence Behavior
State is in global `ibmphp_pci_bus`, `max_slots`, `irqs[16]`, and `init_flag`, plus slot/controller/resource lists populated by other IBM files. Slot status is refreshed from the HPC into `status`, `ext_status`, and `busstatus`. `slot_cur->func` owns configured card resources and PCI device references until disable or unload. No durable persistence is implemented here; EBDA is treated as firmware input.

## Dependencies and Integration Points
Depends on IBM EBDA parsing/resource/HPC/polling functions declared in `ibmphp.h`, PCI core scan/remove APIs, x86 IRQ routing and I/O APIC helpers, PCI hotplug core, and ServerWorks CIOBX detection for a 133 MHz PCI-X workaround. It shares the hotplug-core interface through `struct hotplug_slot_ops`.

## Risks
The driver serializes hotplug operations with `ibmphp_lock_operations()`, but also reacts to polling/latch/power-fault paths where `flag` changes disable behavior. It relies on firmware status to prevent unsafe operations; wrong status decoding can power cards at incompatible speeds. `bus_structure_fixup()` manually allocates temporary bus/device objects and scans buses to compensate for PCI-core limitations. Domain 0 assumptions, old PCI-X speed limits, and x86 routing APIs limit portability.

## Test Signals
Module init with valid and missing EBDA/root bus, slot registration, init-time empty-slot power-off, attention LED set/get/blink, enable on valid slot, enable rejection for latch/open/no card/bus limit/speed mismatch/power fault, bridge and multifunction card scan, disable of boot-time and hot-added cards, unexpected latch/power-fault disable path, polling thread start/stop, resource cleanup on failed init, and unload after active slots are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/ibmphp_core.c -->
