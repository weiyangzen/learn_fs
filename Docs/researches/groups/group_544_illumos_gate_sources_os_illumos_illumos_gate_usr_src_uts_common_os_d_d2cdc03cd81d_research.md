# Group Research: group_544_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_d_d2cdc03cd81d

Scope: `Docs/research_subset_a.md`  
Source tree: `sources/os/illumos/illumos-gate`  
Files researched: 1

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devcfg.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devcfg.c

## Purpose

`devcfg.c` is the illumos kernel device-tree configuration engine. It owns `dev_info_t` node lifecycle management, driver binding, child enumeration, attach/detach transitions, devfs event generation, path resolution, device retirement/offline handling, and multithreaded subtree configuration.

Read completely: 9,374 lines.

## Main Responsibilities

- Allocates, initializes, links, unlinks, and frees `dev_info_t` nodes.
- Drives device node state transitions:
  `DS_PROTO -> DS_LINKED -> DS_BOUND -> DS_INITIALIZED -> DS_PROBED -> DS_ATTACHED -> DS_READY`, and the reverse path.
- Binds nodes to drivers using compatible properties, node names, path aliases, and driver.conf data.
- Handles `.conf` child enumeration and property merging into hardware nodes.
- Provides public/private DDI/NDI entry points such as `ddi_initchild`, `ddi_remove_child`, `ndi_devi_config`, `ndi_devi_config_one`, `ndi_devi_unconfig`, `ndi_devi_online`, and `ndi_devi_offline`.
- Coordinates devfs sysevents and branch add/remove events.
- Implements tree walking, path-to-device resolution, and pre-root block-device scanning used by ZFS.
- Handles quiesce/reset paths for reboot and shutdown.
- Maintains device retirement, unretirement, fencing, and hotplug removed/inserted state.
- Provides alias redirect support for platform device path aliases.
- Maintains the devinfo snapshot cache invalidation path.

## Important Data Structures And Globals

- `top_devinfo`, `options_dip`, `pseudo_dip`, `clone_dip`, `scsi_vhci_dip`: well-known root and special device tree nodes.
- `devtree_gen`: generation counter used to signal zone `/dev` refresh needs and devinfo cache changes.
- `devinfo_freeze`: blocks future devinfo state changes during shutdown/panic-adjacent paths.
- `devinfo_attach_detach`: counts attach/detach operations in progress.
- `di_cache`: global devinfo snapshot cache metadata.
- `devi_nodeid_list` / `devimap`: maps persistent PROM/SID node IDs to held `dev_info_t` nodes.
- `brevq_node`: queues branch-remove event paths during subtree unconfiguration.
- `mt_config_handle` and `mt_config_data`: coordinate parallel recursive config/unconfig.
- `ddi_aliases`: platform alias path table and lookup caches.

## Node Lifecycle

Allocation starts in `i_ddi_alloc_node()`, which creates a zeroed `struct dev_info`, duplicates the node name and system properties, assigns node class/attributes, initializes locks/CVs/lists/contracts, and starts the node in `DS_PROTO`.

Persistent nodes are tracked in `devimap`; pseudo/SID nodes may get auto-assigned node IDs. Freeing in `i_ddi_free_node()` asserts the node is back in `DS_PROTO`, has no children or active refs, removes properties/minors/devid data, tears down contract and unbind callback state, and returns the object to `ddi_node_cache`.

`link_node()` inserts a node into the parent's child list, with special root-child ordering for `scsi_vhci` and IB VHCI nodes. `unlink_node()` removes it after checking references and removing it from the nodeid map.

## State Transition Engine

`i_ndi_config_node()` is the central promotion loop:

- `DS_PROTO`: link into parent.
- `DS_LINKED`: bind to a driver.
- `DS_BOUND`: call parent `DDI_CTLOPS_INITCHILD`, assign instance, detect duplicate nodes, handle path-alias rebind, optimize bus-op dispatch.
- `DS_INITIALIZED`: call driver probe.
- `DS_PROBED`: enforce retire policy, call attach.
- `DS_ATTACHED`: run DACF postattach, reach `DS_READY`.

`i_ndi_unconfig_node()` reverses the same ladder:

- pre-detach DACF from `DS_READY`.
- detach driver from `DS_ATTACHED`.
- unprobe, uninitchild, unbind, unlink.
- handles `DEVI_DETACHING`, driver release, minor/property cleanup, and autodetach restrictions.

Wrappers include `ddi_initchild()`, `ddi_uninitchild()`, `i_ddi_attachchild()`, and `i_ddi_detachchild()`.

## Configuration And Unconfiguration

The main recursive configuration path is:

- `ndi_devi_config()` / `ndi_devi_config_driver()`
- `devi_config_common()`
- bus nexus `bus_config` if provided, else framework fallback
- `config_immediate_children()`
- `config_grand_children()` via multithreaded child nexus traversal

Single-child lookup/configuration is handled by `ndi_devi_config_one()` and `devi_config_one()`. These parse `name@addr[:minor]`, account for PROM/generic names, pHCI/vHCI relationships, asynchronous enumeration waits, `.conf` child creation, and alias redirect fallback.

Unconfiguration mirrors this through:

- `ndi_devi_unconfig()`
- `ndi_devi_unconfig_driver()`
- `ndi_devi_unconfig_one()`
- `devi_unconfig_common()`
- `devi_unconfig_branch()`
- `devi_detach_node()`

The unconfig path integrates PM hooks, devfs cache cleaning, branch remove event queues, pHCI/vHCI lock ordering, offline notifications, and optional physical removal.

## Locking And Concurrency

`ndi_devi_enter()`, `ndi_devi_exit()`, and `ndi_devi_tryenter()` serialize modifications to a node’s children, pathinfo, and minor list using `DEVI_BUSY`. The file has explicit comments requiring hierarchical entry from root toward leaves to avoid deadlock.

Special handling exists for:

- recursive same-thread entry via `devi_circular`.
- panic context, where locking is skipped.
- pHCI/vHCI ordering, including `DEVI_PHCI_SIGNALS_VHCI`.
- root children protected by `global_vhci_lock`.
- per-driver lists protected by `devnames.dn_lock`.
- driver attach serialization through `DN_DRIVER_BUSY`.

Multithreaded config/unconfig uses per-child worker threads unless `mtc_off` or `NDI_MTC_OFF` disables it.

## Driver Binding And Properties

`bind_node()` selects a driver through `ddi_compatible_driver_major()`, which checks:

- `ddi-assigned` virtualization exclusion, forcing `nulldriver`.
- path-oriented aliases during rebind.
- `compatible` property strings.
- node name fallback.

`init_node()` also detects path-oriented aliases once `@addr` is known and may demote/rebind the node. `.conf` support includes:

- `i_ddi_load_drvconf()` / `i_ddi_unload_drvconf()`
- `i_ndi_make_spec_children()`
- `ndi_merge_node()`
- `ndi_merge_wildcard_node()`
- global driver property reference lists through `add_global_props()` and `remove_global_props()`.

## Devfs, Sysevents, And Cache

The file generates EC_DEVFS events for device add/remove and branch add/remove:

- `i_log_devfs_add_devinfo()`
- `i_log_devfs_remove_devinfo()`
- `i_log_devfs_branch_add()`
- `i_log_devfs_branch_remove()`

`brevq_node` queues subtree branch-remove events so failed or partial unconfiguration can still report correct paths.

`i_ddi_di_cache_invalidate()` increments `devtree_gen`, invalidates `di_cache`, and schedules asynchronous cache freeing. `i_ddi_di_cache_free()` also unlinks the persistent cache file when root is writable and the system is not shutting down.

## Path Resolution And Tree Walking

`resolve_pathname()` walks an absolute device path from `ddi_root_node()`, configuring each component as needed through `ndi_devi_config_one()`. It resolves minor names, OBP-style device args, iSCSI boot path syntax, and default/fallback minor-node selection.

Public consumers include:

- `ddi_pathname_to_dev_t()`
- `i_ddi_prompath_to_devfspath()`
- `e_ddi_hold_devi_by_path()`
- `e_ddi_hold_devi_by_dev()`
- `ddi_hold_devi_by_instance()`

`ddi_walk_devs()` performs breadth-style devinfo walks with pruning/termination controls. `e_ddi_walk_driver()` walks a per-driver instance list.

`preroot_walk_block_devices()` forces device attach and walks block minors for early ZFS label discovery.

## Hotplug, Offline, Retire, And Reinsert

`ndi_devi_online()` attaches a node, may configure descendants, and logs branch events. `ndi_devi_offline()` detaches and marks devices offline, optionally removing the node.

Offline and retire constraint handling integrates:

- device contracts via `contract_device_offline()`
- LDI notifications/finalizers
- `e_ddi_retire_device()`
- `e_ddi_unretire_device()`
- `i_ddi_check_retire()`
- snode fencing/unfencing through `spec_fence_snode()` and `spec_unfence_snode()`
- MDI pHCI retirement hooks

Open hotplug removal is represented independently of node destruction through:

- `ndi_devi_device_remove()`
- `ndi_devi_device_insert()`
- `ndi_devi_device_isremoved()`

These update hidden/removed state, invalidate snapshots, and log device events.

## Boot, Shutdown, And Special Nodes

Boot-time helpers include:

- `i_ddi_forceattach_drivers()`
- `i_ddi_attach_hw_nodes()`
- `i_ddi_attach_pseudo_node()`
- `ddi_hold_installed_driver()`
- `i_ddi_attach_node_hierarchy()`

`ndi_devi_config_vhci()` handcrafts VHCI nodes under root without normal parent busy locking to avoid deadlocks during attach/init paths.

Shutdown support includes:

- `devtree_freeze()`
- `quiesce_devices()`
- `check_driver_quiesce()`
- `reset_leaves()`

These prevent concurrent state transitions, call driver quiesce/reset hooks, and skip inappropriate pseudo/non-hardware nodes according to tunables.

## Platform Alias Support

`ddi_register_aliases()` installs platform alias mappings, sorted by alias/current path length, and creates two mod_hash lookup caches.

- `ddi_alias_redirect()` maps alias paths to current devinfo nodes.
- `ddi_curr_redirect()` maps current paths back to aliases.
- TSD `tsd_ddi_redirect` prevents recursive alias resolution.

## Notable Risks And Invariants

- Correctness relies heavily on external lock ownership assertions such as `DEVI_BUSY_OWNED(parent)`.
- pHCI/vHCI lock ordering is a repeated deadlock-sensitive concern.
- `e_ddi_hold_devi_by_dev()` contains a documented legacy race around `DDI_INFO_DEVT2DEVINFO`.
- Path-oriented alias rebind for driver.conf nodes deliberately preserves some system properties, with comments noting non-intuitive behavior.
- Many public functions return success despite sysevent logging failure to avoid blocking device configuration on devfs notification problems.
- `devinfo_freeze` blocks further state transitions but only waits briefly for active attach/detach operations.

## Research Relevance

For filesystem and storage research, this file is important because it defines how block devices become visible, attached, walked, resolved by path, exposed to devfs, retired/offlined, and quiesced. `preroot_walk_block_devices()`, `resolve_pathname()`, devfs event generation, and minor-node handling are the most directly relevant pieces for storage stack discovery and filesystem boot behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devcfg.c -->