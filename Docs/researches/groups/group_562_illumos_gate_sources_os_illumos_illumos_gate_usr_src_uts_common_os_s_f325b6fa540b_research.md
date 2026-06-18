# Group Research: group_562_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_s_f325b6fa540b

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunmdi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunmdi.c

## Overview

`sunmdi.c` is the illumos kernel implementation of the Multipath Driver Interface (MDI), the framework that lets a virtual HCI (vHCI) present one client device through multiple physical HCI (pHCI) paths. It manages vHCI class registration, pHCI registration, client devinfo nodes, pathinfo nodes, path selection, failover coordination, power management, devfs bus configuration, persistent vHCI cache storage, kstats, sysevents, and retire/hotplug handling.

The file is large and central: 9,755 lines, read completely for this report.

## Major Responsibilities

- Registers and unregisters vHCI class drivers with `mdi_vhci_register()` / `mdi_vhci_unregister()`.
- Registers and unregisters pHCI instances with `mdi_phci_register()` / `mdi_phci_unregister()`.
- Creates, links, unlinks, and frees `mdi_client_t`, `mdi_phci_t`, and `mdi_pathinfo_t` objects.
- Maintains per-vHCI client hash tables and pHCI/client path lists.
- Implements path allocation, lookup, state transitions, online/offline/standby/fault states, enable/disable flags, and per-path properties.
- Selects paths for I/O using no-balancing, round-robin, preferred-path, and LBA-region policies.
- Coordinates failover through vHCI callback vectors.
- Integrates MDI components with NDI attach, detach, online, offline, suspend, resume, and power-management flows.
- Persists and rebuilds vHCI bus-configuration cache data in `/etc/devices/mdi_<class>_cache`.
- Drives pHCI bus configuration, including multithreaded configuration of all pHCIs and async configuration of cached paths.
- Supports device removal/insertion, retire/unretire, per-path kstats, sysevent logging, and devctl state reporting.

## Core State And Data Structures

Global state includes:

- `mdi_mutex`: protects the global vHCI list.
- `mdi_vhci_head`, `mdi_vhci_tail`, `mdi_vhci_count`: registered vHCI classes.
- `mdi_taskq`: CPR-safe taskq used for asynchronous failover.
- `mdi_pathmap_*`: hash maps between persistent in-memory path strings, path instances, and short path names.
- vHCI cache tunables: flush delay, async idle time, path discovery retry counts, cache hash size, and `mdi_mtc_off`.

Main object relationships:

- A vHCI owns a class, ops vector, pHCI list, client hash table, and vHCI cache/config object.
- A pHCI points back to its vHCI and owns a list of pathinfo nodes.
- A client points back to its vHCI and owns a list of pathinfo nodes.
- A pathinfo joins exactly one client to one pHCI while active, carries path state, address, path instance, properties, private pointers, reference count, power hold state, kstats, and preferred/disable/remove flags.

## Registration And Topology Management

`i_mdi_init()` lazily initializes the framework mutex, taskq, and path-instance hash maps.

`mdi_vhci_register()` enforces one vHCI driver per class, initializes per-vHCI locks and client hash table, reads load-balancing properties, installs the vHCI ops vector, sets up the vHCI cache, and marks the devinfo node as an MDI vHCI component.

`mdi_phci_register()` checks `mpxio-disable`, finds the class vHCI, allocates a pHCI object, initializes pHCI state and locks, marks the pHCI devinfo, links it into the vHCI pHCI list, adds it to the cache, and logs a registration sysevent.

`mdi_phci_unregister()` removes the pHCI from the vHCI list, nulls back-pointers from remaining pathinfo nodes, removes the pHCI from the cache, logs unregister, and destroys pHCI resources.

## Client And Path Lifecycle

Client allocation is handled by `i_mdi_client_alloc()`, which initializes client state as failed/offline/detached/power-up, sets inherited load balancing, creates condition variables, and enlists the client in the vHCI hash table.

`mdi_pi_alloc_compatible()` is the main path allocation API. It validates pHCI readiness, creates or finds the client, creates the client devinfo node if needed, then finds or allocates the pathinfo node. `i_mdi_pi_alloc()` initializes the pathinfo, computes or reuses a persistent path instance, creates its nvlist property store, and links it into both the pHCI and client path lists under devinfo enters.

`mdi_pi_free()` only frees paths in offline/init states after pending references drain. It serializes against failover, calls the vHCI `vo_pi_uninit` callback when appropriate, releases power holds, removes the path from cache and lists, destroys kstats/properties/locks, and frees the client if this was its last path.

## Path States And Selection

Path state changes flow through `i_mdi_pi_state_change()`. It performs initial `vo_pi_init`, checks pHCI readiness, waits for transient states, serializes against failover, marks transient state, calls the vHCI `vo_pi_state_change` callback, updates client aggregate state, and brings the client devinfo online or offline as needed.

Public wrappers:

- `mdi_pi_online()`
- `mdi_pi_standby()`
- `mdi_pi_fault()`
- `mdi_pi_offline()`

Path selection is implemented by `mdi_select_path()`. It rejects failed, detached, or failover-busy clients for normal I/O, supports selection by path instance, and implements:

- `LOAD_BALANCE_NONE`: reuse or find a usable online path.
- `LOAD_BALANCE_RR`: round-robin online/standby selection with preferred-path pass before non-preferred paths.
- `LOAD_BALANCE_LBA`: selects a path by block region, falling back to round-robin if no matching online path is available.

Transient or driver-disable states cause `MDI_BUSY`; no usable paths cause `MDI_NOPATH`.

## Properties, Kstats, And Public Accessors

Pathinfo properties are stored in an nvlist. The file implements update, lookup, removal, size, and pack functions for bytes, integers, int64, arrays, strings, and string arrays. `i_map_nvlist_error_to_mdi()` maps nvlist errors into DDI property-style results.

Path kstats are created by `mdi_pi_kstat_create()` and destroyed by `i_mdi_pi_kstat_destroy()`. I/O accounting is updated by `mdi_pi_kstat_iosupdate()`. Error counters are represented by named kstats under the `iopath_errors` class.

Accessors expose client/pHCI devinfo pointers, node names, path addresses, path instances, path names, OBP paths, private pointers, preferred flags, hidden/device-removed flags, component type checks, vHCI/private storage, and devctl device state.

## Device Lifecycle, Hotplug, And Retire

`mdi_devi_online()` and `mdi_devi_offline()` are NDI notifications that update pHCI/client state and may offline affected paths or clients. pHCI offline handling checks unstable clients, failover, and last-path conditions before marking all child paths offlining and invoking offline callbacks.

Attach/detach integration is split across:

- `mdi_pre_attach()` / `mdi_post_attach()`
- `mdi_pre_detach()` / `mdi_post_detach()`
- `i_mdi_phci_pre_detach()`
- `i_mdi_client_pre_detach()`
- corresponding post-detach helpers

The file also supports pHCI retire flows:

- `mdi_phci_mark_retiring()`
- `mdi_phci_retire_notify()`
- `mdi_phci_retire_finalize()`
- `mdi_phci_unretire()`

Path hotplug removal/insertion is represented with `mdi_pi_device_remove()` and `mdi_pi_device_insert()`, which set hidden/device-removed flags and invalidate devinfo snapshots or mark the client removed if all paths are removed.

## Power Management

MDI keeps pHCIs powered while clients are configured or active. Key helpers:

- `i_mdi_pm_hold_pip()` / `i_mdi_pm_rele_pip()`
- `i_mdi_pm_hold_client()` / `i_mdi_pm_rele_client()`
- `i_mdi_power_one_phci()` / `i_mdi_power_all_phci()`
- `mdi_bus_power()`
- `mdi_power()`

Power operations serialize per client using `ct_powerchange_cv` and `MDI_CLIENT_IS_POWER_TRANSITION`. Config/unconfig paths temporarily hold all viable pHCIs, then release or reset counts depending on attach/detach and power-down results.

## Persistent vHCI Cache And Bus Configuration

The cache maps vHCI client addresses to pHCI paths and path addresses. It is stored as an nvlist with:

- `version`
- `phcis`
- `clientaddrmap`

`setup_vhci_cache()` initializes cache state, reads early boot cache nvlists, and installs a shutdown callback. `vhcache_dirty()` schedules a deferred flush through `vhcache_flush_thread()`, and `flush_vhcache()` writes the nvlist to disk with read-only filesystem/error handling.

`mdi_vhci_bus_config()` provides the generic vHCI bus config implementation for SCSI and IB classes. It builds the cache if needed, configures cached paths for `BUS_CONFIG_ONE`, drives all pHCIs for `BUS_CONFIG_DRIVER` and `BUS_CONFIG_ALL`, then delegates final child configuration to `ndi_busop_bus_config()`. If config-one fails, it can trigger full path discovery and retry.

The cache also supports cleanup through `mdi_clean_vhcache()`, called during `devfsadm -C`, removing stale pHCI/client/path entries.

## Concurrency And Locking Notes

The file explicitly documents lock ordering:

- global `mdi_mutex`
- vHCI pHCI/client locks
- pHCI/client locks
- pathinfo locks

Several helpers handle reverse-lock situations by dropping path locks, holding references, delaying, and reacquiring in safe order. State transitions rely on transient flags and condition variables (`pi_state_cv`, `ct_failover_cv`, `ct_unstable_cv`, `ph_unstable_cv`, `vhc_cv`) to serialize failover, path changes, power transitions, async config, and cache flush threads.

Important invariant: path list structure and devinfo snapshot consistency are protected by entering the involved devinfo nodes while linking/unlinking pathinfo nodes.

## Error Handling And Risks

Most public functions map internal or NDI failures to `MDI_SUCCESS`, `MDI_FAILURE`, `MDI_BUSY`, `MDI_NOPATH`, `MDI_ACCEPT`, or `MDI_DEVI_ONLINING`.

Notable risk areas for future changes:

- Lock ordering is delicate; reverse-lock helpers are intentional and should not be simplified casually.
- `mdi_select_path()` encodes subtle preferred/non-preferred traversal behavior.
- `mdi_pi_free()` and path state changes must remain serialized against failover and outstanding path references.
- vHCI cache updates are persistent; changing cache format requires versioning and boot compatibility.
- Power hold counts are distributed across path count, config/unconfig, attach/detach, and bus power callbacks.
- Some older compatibility paths remain, such as `mdi_pi_enable()` / `mdi_pi_disable()` wrappers and comments noting future removal.

## External Interfaces And Dependencies

This file depends heavily on illumos kernel subsystems:

- DDI/NDI devinfo and bus configuration
- devfs and `/etc/devices` cache handling
- nvlist packing/unpacking
- taskq, threads, callb/CPR callbacks
- kstat
- power management
- sysevent logging
- mod_hash
- dynamic reconfiguration and retire APIs

It is not filesystem code directly, but it is relevant to the storage substrate in subset A because it controls multipath discovery, path availability, failover, and I/O path selection for storage clients such as `scsi_vhci`.

<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunmdi.c -->