<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c` is the main Thunderbolt/USB4 router and port utility implementation. It manages router allocation/configuration/add/remove, port initialization and adapter control, HopID allocation, link width/bonding/asymmetric links, NVM sysfs/authentication, authorization sysfs, DROM/UUID identity, PM resume/suspend, wake programming, DP resources, retimer removal integration, lookup helpers, and selected generation-specific PCIe/xHCI flows. The source was read as a complete 4038-line file.

## Important APIs, Types, and Functions

Switch lifecycle APIs include `tb_switch_alloc()`, `tb_switch_alloc_safe_mode()`, `tb_switch_configure()`, `tb_switch_configuration_valid()`, `tb_switch_add()`, `tb_switch_remove()`, `tb_sw_set_unplugged()`, `tb_switch_resume()`, and `tb_switch_suspend()`. Port APIs include `tb_port_state()`, `tb_wait_for_port()`, `tb_port_add_nfc_credits()`, `tb_port_clear_counter()`, `tb_port_unlock()`, `tb_port_enable()`, `tb_port_disable()`, HopID alloc/release helpers, `tb_next_port_on_path()`, link speed/generation/width helpers, adapter enable helpers for USB3/PCIe/DP, and DP HPD/hop helpers. Link APIs include `tb_switch_set_link_width()`, `tb_switch_configure_link()`, and `tb_switch_unconfigure_link()`. NVM APIs include `tb_switch_nvm_read()` plus internal authentication/status helpers. Lookup/special APIs include `tb_switch_find_by_link_depth()`, `tb_switch_find_by_uuid()`, `tb_switch_find_by_route()`, `tb_switch_find_port()`, `tb_switch_query_dp_resource()`, `tb_switch_alloc_dp_resource()`, `tb_switch_dealloc_dp_resource()`, `tb_switch_pcie_l1_enable()`, `tb_switch_xhci_connect()`, and `tb_switch_xhci_disconnect()`.

## Control Flow

Allocation unlocks the downstream port for non-root routes, reads switch config space, determines generation, fills route/depth/upstream fields, checks topology depth, allocates and minimally initializes ports/IDAs, discovers VSE capabilities, initializes the device object, and leaves hardware programming to `tb_switch_configure()`. Configuration marks the router enabled, writes USB4 or legacy switch config fields, runs USB4 setup when needed, and enables plug events for legacy routers. Adding a switch first creates any DMA/NVM access path, initializes USB4 credits, reads DROM, sets UUID, initializes all ports, applies quirks, links default dual-lane ports, updates link attributes, initializes CLx/TMU, enables USB4 hotplug, registers the device, adds USB4 child ports and nvmem devices, enables wake/runtime PM, and initializes debugfs.

Removal walks downstream switches and XDomain children, removes retimers for every port, disables plug events if still present, removes NVM and USB4 ports, logs disconnects, and unregisters the device. Resume verifies non-root identity by reading config and UID, reconfigures the switch, handles wake notifications, disables wakes, reinitializes TMU, then recursively resumes surviving downstream routers or marks lost children unplugged. Suspend disables CLx, disables plug events, recursively suspends children, programs wake flags according to runtime/system suspend, and sets USB4 or LC sleep.

Port control reads/writes adapter config space for lane state, NFC credits, USB3/PCIe/DP enable bits, DP HPD, and DP HopIDs. Link width control handles pre-Gen4 bonding, Gen4 dual/asymmetric widths, credit refresh, and userspace change notification. NVM sysfs stages writes through `tb_nvm_write_buf()`, validates/writes flash on authentication, handles USB4 vs DMA-port flashing, and caches authentication status across switch power cycles by UUID.

## State and Persistence Behavior

`struct tb_switch` owns router config, identity, UUID, DROM data, ports, quirks, NVM, DMA port, link attributes, authorization/key state, runtime PM flags, and unplug state. Each port owns config snapshots, capabilities, HopID IDAs, remote/XDomain pointers, dual-link metadata, credits, and bandwidth limits. Hardware-persistent state includes router config space, path registers, link width/bonding state, wake/sleep settings, NVM flash, and authorization side effects mediated by the connection manager. The static `nvm_auth_status_cache` persists authentication failure status by switch UUID beyond switch power cycles while the module remains loaded.

## Dependencies and Integration Points

The file depends on `tb.h`, Linux device/sysfs/runtime PM/nvmem/IDA APIs, DMA-port helpers, DROM code, USB4 router/port helpers, LC helpers, CLx/TMU/debugfs helpers, retimer management, path deactivation, domain approval/disapproval APIs, and connection-manager PM callbacks. It is the central integration point for most higher-level Thunderbolt tunnel managers.

## Risks and Edge Cases

This file has many hardware-ordering risks: NVM authentication can intentionally make routers disappear; host NVM update keeps the PCIe root port in D0; switch add may return `-ESHUTDOWN` after power cycling; safe-mode switches expose only limited NVM paths; plug events differ for ICM/USB4/legacy; UID mismatch on resume means a different device is present; recursive remove/resume must handle already unplugged children; link width changes must keep both ends and credits consistent; Gen4 cannot switch to single lane; sysfs uses `mutex_trylock()` and `restart_syscall()` to avoid domain-lock deadlocks; `switch_attr_is_visible()` hides attributes depending on security, safe mode, route, NVM support, and quirks.

## Test Signals

Validation should cover root and device router add/remove, safe mode, DROM failures, UUID generation from UID/LC, USB4 and legacy config, authorization/key sysfs, NVM active/non-active sysfs and authentication statuses, hotplug plug-event behavior, runtime/system suspend with child routers and XDomain, wake flag programming, link bonding/asymmetric transitions, DP resource allocation, retimer removal, lookup helpers, Titan Ridge PCIe L1 writes, Alpine/Titan Ridge xHCI connect flows, and fault injection around config-space reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/switch.c -->
