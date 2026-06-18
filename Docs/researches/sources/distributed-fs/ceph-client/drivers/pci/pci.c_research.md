# sources/distributed-fs/ceph-client/drivers/pci/pci.c

## Purpose
`pci.c` is a central PCI core service file. It implements common helpers for capability discovery, PCI and platform power-state transitions, device enable/disable, config-state save/restore, PME wake handling, bridge D3 policy, Enhanced Allocation resource parsing, ARI/ACS/AtomicOp configuration, BAR resource reservation, I/O space mapping, bus mastering and MWI controls, function/slot/bus reset flows, PCI-X and PCIe tuning helpers, bandwidth reporting, VGA decode routing, DMA alias tracking, resource-alignment policy, PCI domain allocation, and `pci=` boot parameter parsing.

The file is not a device driver by itself. It exports infrastructure used by PCI enumeration, power management, hotplug, reset, IOMMU grouping, sysfs, architecture code, and individual PCI drivers.

## Important APIs, Types, and Functions
Global state includes `pci_power_names`, `pci_pci_problems`, hotplug resource-size defaults, `pcie_bus_config`, cache-line settings, `pcie_ari_disabled`, `pcie_ats_disabled`, `pci_early_dump`, bridge D3 controls, the PME polling list and delayed work, resource-alignment parameter state, and PCI domain IDAs.

Capability helpers include `pci_find_capability()`, `pci_bus_find_capability()`, `pci_find_next_capability()`, `pci_find_ext_capability()`, `pci_find_next_ext_capability()`, `pci_get_dsn()`, HyperTransport search helpers, `pci_find_vsec_capability()`, and `pci_find_dvsec_capability()`. Device string matching for boot parameters is implemented by `pci_dev_str_match_path()` and `pci_dev_str_match()`.

Power-management APIs include `pci_update_current_state()`, `pci_refresh_power_state()`, `pci_platform_power_transition()`, `pci_power_up()`, `pci_set_power_state()`, `pci_set_power_state_locked()`, `pci_save_state()`, `pci_restore_state()`, `pci_store_saved_state()`, `pci_load_saved_state()`, `pci_enable_wake()`, `pci_wake_from_d3()`, `pci_prepare_to_sleep()`, `pci_back_from_sleep()`, `pci_finish_runtime_suspend()`, `pci_dev_run_wake()`, `pci_choose_state()`, `pci_config_pm_runtime_get()`, `pci_config_pm_runtime_put()`, and `pci_pm_init()`.

Enable/resource APIs include `pci_ioremap_bar()`, `pci_ioremap_wc_bar()`, `pci_enable_device()`, `pci_enable_device_mem()`, `pci_reenable_device()`, `pci_disable_device()`, region request/release helpers, `pci_select_bars()`, I/O range helpers, `pci_set_master()`, `pci_clear_master()`, `pci_set_mwi()`, `pci_try_set_mwi()`, `pci_clear_mwi()`, `pci_intx()`, and weak architecture hooks such as `pcibios_enable_device()`, `pcibios_disable_device()`, `pcibios_set_master()`, `pci_resource_to_user()`, and `pci_ext_cfg_avail()`.

Reset APIs include `pcie_flr()`, `pcie_reset_flr()`, AF FLR, PM reset, CXL and bus reset helpers, `pci_dev_lock()`, `pci_dev_trylock()`, `pci_dev_unlock()`, `pci_init_reset_methods()`, `__pci_reset_function_locked()`, `pci_reset_function()`, `pci_reset_function_locked()`, `pci_try_reset_function()`, `pci_probe_reset_slot()`, `pci_probe_reset_bus()`, `pci_reset_bus()`, `pci_try_reset_bridge()`, and `pci_bus_error_reset()`. Reset ordering is described by `pci_reset_fn_methods[]`.

PCIe/PCI-X tuning and topology APIs include `pcix_get_max_mmrbc()`, `pcix_get_mmrbc()`, `pcix_set_mmrbc()`, `pcie_get_readrq()`, `pcie_set_readrq()`, `pcie_get_mps()`, `pcie_set_mps()`, `pcie_link_speed_mbps()`, `pcie_bandwidth_available()`, `pcie_get_supported_speeds()`, `pcie_get_speed_cap()`, `pcie_get_width_cap()`, `__pcie_print_link_status()`, `pcie_print_link_status()`, `pcie_retrain_link()`, `pcie_wait_for_link()`, `pci_enable_atomic_ops_to_root()`, ACS helpers, and ARI setup.

## Control Flow
Boot-time setup starts with `early_param("pci", pci_setup)`, which parses comma-separated `pci=` options and delegates architecture-specific handling through `pcibios_setup()`. Recognized options disable MSI, ATS, AER, ARI, or TPH, configure PCIe bus tuning, resource reallocation and alignment, hotplug resource windows, ECRC policy, ACS redirection/configuration, early config dumping, domain support, and PCIe scanning. Because some parsed strings initially point into `__initdata`, `pure_initcall(pci_realloc_setup_params)` duplicates them after early init. `pcie_port_pm_setup()` separately handles `pcie_port_pm=off|force`.

Capability search flows read standard or extended config-space linked lists and return config offsets. The VSEC/DVSEC helpers iterate vendor-specific extended capability instances and match vendor/capability IDs. These offsets feed later PM, reset, ACS, ARI, EA, and sysfs behavior.

Power-state transitions use a layered policy. Platform hooks are tried through ACPI or MID helpers. `pci_update_current_state()` queries platform D3cold first, then PMCSR when accessible, and otherwise falls back to the supplied state. `pci_set_power_state()` normalizes the target, rejects invalid D1/D2 paths, powers up through `pci_power_up()` and BAR restore when needed, or enters low power through `pci_set_low_power_state()` and optional platform D3cold. When a bridge reaches D3cold, subordinate devices are marked D3cold too.

Suspend/wake flows choose target states with `pci_target_state()`, configure PME and platform wake in the correct order, and unwind wake settings if power transition fails. Runtime config access helpers raise runtime-PM references on parent and device, wait for barriers, and resume devices only when D3cold would make config space inaccessible.

Device enable increments `enable_cnt` and only programs hardware on the first enable. The first enable resumes the device, enables upstream bridges recursively, calls host-bridge and arch enable hooks, applies enable fixups, and clears INTx disable if a legacy interrupt pin exists and MSI/MSI-X is not active. Disable decrements the reference count and only disables bus mastering and arch resources when the count reaches zero.

State save reads the first 64 bytes of config space, saves PCIe and PCI-X state plus other optional capability state managed by companion files, and marks `state_saved`. Restore replays PCIe/PASID/PRI/ATS/VC/ReBAR/DPC/PTM/TPH/AER/config/MSI/ACS/IOV state in an order that restores dependencies before enabling dependent features. Opaque saved states are copied to and from dynamically allocated `struct pci_saved_state`.

Reset flows probe available reset methods into `dev->reset_methods[]`, then execute the first supported method that succeeds. Function reset paths lock the device, call driver reset-prepare handlers when present, force D0, save state, clear command decoding and bus mastering, perform the reset, restore state, notify reset-done, and unlock. Slot and bus reset paths lock entire subtrees from top down, save and disable all affected devices, issue hotplug slot reset or secondary bus reset, wait for downstream accessibility, restore devices top down, and unlock bottom up.

Resource and PCIe policy flows are mostly direct helpers. EA parsing discovers enabled Enhanced Allocation entries and fills `struct resource`s. Region request functions reserve I/O or memory resources and unwind partial failures. ACS and ARI initialization read capabilities, apply device-specific quirks and administrator `pci=` overrides, and program control registers. Link retrain and secondary-bus wait helpers enforce PCIe timing, link-active checks, RRS polling, and D3cold delay requirements.

## State and Persistence Behavior
All state is kernel runtime state. Persistent external effects are hardware register changes and exported sysfs/boot-parameter policy, not on-disk storage.

Per-device state touched here includes `current_state`, `pm_cap`, PME support fields, wakeup flags, D1/D2 support, D3cold delays and policy flags, `bridge_d3`, `state_saved`, `saved_config_space`, `saved_cap_space`, `enable_cnt`, `is_busmaster`, reset-method arrays, ACS capability offsets and masks, ARI bridge state, BAR `struct resource`s, DMA alias bitmaps, `ignore_hotplug`, and subordinate bus state. Global mutable policy includes bridge D3 disable/force, PCIe ATS/ARI disable, `pcie_bus_config`, hotplug sizing, resource-alignment strings, ACS override strings, and domain IDA allocation state.

PME polling uses `pci_pme_list`, `pci_pme_list_mutex`, and delayed work on `system_freezable_wq`. Entries are allocated when PME polling is enabled and removed when disabled or when scan observes `pme_poll` cleared.

## Dependencies and Integration Points
This file depends on core PCI config accessors, PCIe capability helpers, ACPI and OF firmware interfaces, DMI quirks, runtime PM, hotplug slot operations, IOMMU reset prepare/done hooks, AER/DPC/PTM/TPH/VC/ReBAR/ASPM/MSI/SR-IOV companion helpers, logic PIO, resource management APIs, VGA arbitration architecture callbacks, IDA allocation, and architecture weak hooks.

It integrates upward with drivers through exported symbols such as `pci_enable_device()`, `pci_request_regions()`, `pci_set_master()`, `pci_save_state()`, `pci_restore_state()`, `pci_enable_wake()`, and reset helpers. It integrates sideways with `pci-sysfs.c` through reset support, reset method names, runtime-PM config access helpers, resource-user translation, link-speed helpers, resource resizing, and power-state names. It integrates downward with firmware and platform code for power, domain numbering, resource windows, and architecture-specific setup.

## Risks
Power management is highly hardware- and firmware-sensitive. Incorrect platform D3cold reporting, bad DMI policy, unsupported D1/D2 transitions, or missing PME wiring can make devices inaccessible or prevent wake. The code includes many fallbacks, delays, and blacklist/force knobs, but changes in this area require hardware coverage.

Reset paths are high risk because they intentionally disrupt devices and subordinate hierarchies. Reset methods must stop DMA through IOMMU prepare hooks, block config access, avoid resetting unrelated multifunction or sibling devices when inappropriate, and restore state in dependency order. CXL SBR masking and hotplug slot semantics add topology-specific failure modes.

Config restore and enable/disable order are fragile contracts. BARs must be restored before command decoding, bridges before children, MSI after config restore, and ACS/IOV after base state. Enable/disable reference counting means unbalanced callers can leave devices disabled or unexpectedly enabled.

Administrator boot parameters and sysfs policies can override ACS, resource alignment, bridge D3, and PCIe tuning. Parsing errors, stale initdata pointers, or over-broad device matches can affect unrelated devices. Resource alignment may resize BAR resources beyond hardware size, which can break drivers that infer register layout from resource length.

Concurrency risks are managed through `pci_bus_sem`, device locks, config access locks, PM locks, `pci_slot_mutex`, spinlocks around resource-alignment policy, and PME mutexes. New code must respect these lock orders, especially top-down locking and bottom-up unlocking for bus and slot reset.

## Test Signals
Capability tests should cover standard, extended, HT, VSEC, DVSEC, DSN, ACS, ARI, and EA discovery on devices with and without each capability. Boot-parameter tests should validate parsing of `pci=` options, copied lifetime after init, ACS/resource-alignment matching by ID and path, and sysfs `resource_alignment` updates.

PM tests should cover D0/D1/D2/D3hot/D3cold transitions, PMCSR error handling, platform-only devices, bridge D3 policy on DMI-blacklisted and Thunderbolt/native-hotplug systems, PME wake enable/disable ordering, PME polling, runtime-suspended config access, and resume decisions around D3cold. Logs such as "Refused to change power state", "PME# supported", and bridge D3 changes are useful signals.

Enable/resource tests should verify `enable_cnt` reference behavior, recursive bridge enable, host-bridge hooks, INTx disable clearing, BAR reservation and unwind, exclusive region behavior, I/O range registration/remapping, MWI/cacheline programming, and bus mastering state. Sysfs resource tests in `pci-sysfs.c` exercise several of these helpers indirectly.

Reset tests should probe and execute each reset method where hardware supports it: device-specific, ACPI, PCIe FLR, AF FLR, PM reset, bus reset, and CXL bus reset. They should validate IOMMU prepare/done pairing, driver `reset_prepare`/`reset_done` callbacks, state restoration, lock contention `-EAGAIN`, hierarchy save/restore, secondary-bus wait timing, and correct refusal for no-reset quirks, multifunction devices, CXL masked SBR, or inaccessible devices.

PCIe tuning tests should validate MPS/MRRS bounds, host bridge `no_inc_mrrs`, PCI-X MMRBC behavior, AtomicOp enablement across upstream topology, link retrain completion and LBMS clearing, speed/width capability reporting, bandwidth limiting-device calculation, and VGA decode propagation through bridges.
