# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/main.c

## Purpose

`main.c` is the core PCI, firmware, resource, devlink, SR-IOV, and lifecycle driver for Mellanox ConnectX mlx4 HCAs. It owns module parameters, PCI probe/remove, firmware boot, HCA context-memory setup, master/slave multifunction negotiation, port type switching, devlink reload, PCI error recovery, suspend/resume, default counter allocation, interrupt vector selection, and the handoff to mlx4 auxiliary/upper drivers. It is the central state machine that turns a `pci_dev` into a fully registered `mlx4_dev`.

## Important APIs, Types, And Functions

Module and devlink configuration is exposed through `msi_x`, `num_vfs`, `probe_vf`, `log_num_mgm_entry_size`, `enable_64b_cqe_eqe`, `enable_4k_uar`, `log_num_mac`, `log_num_vlan`, `log_mtts_per_seg`, and `port_type_array`. `mlx4_devlink_params` maps some of those knobs to devlink driverinit/runtime parameters, including internal-error reset, max MACs, crash-dump snapshots, 64-byte CQE/EQE enablement, and 4K UAR mode. `mlx4_devlink_param_load_driverinit_values()` applies driverinit devlink values during reload.

Firmware and capability setup is split across `mlx4_init_fw()`, `mlx4_load_fw()`, `mlx4_dev_cap()`, `mlx4_init_hca()`, `mlx4_init_icm()`, and `mlx4_setup_hca()`. `mlx4_dev_cap()` translates firmware capability fields into `dev->caps`, selects port defaults, bounds MAC/VLAN table sizes, handles CQE/EQE stride policy, stores physical port capability data, chooses reserved QP ranges, and disables unsupported combinations such as timestamping in slave mode. `choose_steering_mode()` chooses A0, B0, or device-managed flow steering and sets `dev->oper_log_mgm_entry_size` plus `dev->caps.num_qp_per_mgm`; `choose_tunnel_offload_mode()` enables VXLAN tunnel offload only when DMFS and firmware flags allow it.

PCI lifecycle is driven by `mlx4_init_one()`, `__mlx4_init_one()`, `mlx4_load_one()`, `mlx4_unload_one()`, and `mlx4_remove_one()`. The registered `pci_driver` also installs `mlx4_shutdown()`, `mlx4_suspend()`, `mlx4_resume()`, and AER handlers `mlx4_pci_err_detected()`, `mlx4_pci_slot_reset()`, and `mlx4_pci_resume()`. Devlink reload delegates to `mlx4_restart_one_down()` and `mlx4_restart_one_up()`.

Port and HA management centers on `mlx4_check_port_params()`, `mlx4_change_port_types()`, sysfs handlers for `mlx4_portN` and `mlx4_portN_mtu`, devlink port ops, `mlx4_bond()`, `mlx4_unbond()`, `mlx4_mf_bond()`, `mlx4_mf_unbond()`, and async `mlx4_queue_bond_work()`. Exported helper APIs include `mlx4_get_parav_qkey()`, `mlx4_sync_pkey_table()`, slave GUID helpers, `mlx4_is_slave_active()`, `mlx4_handle_eth_header_mcast_prio()`, `mlx4_read_clock()`, `mlx4_get_internal_clock_params()`, counter allocation/free helpers, and admin GUID helpers.

## Control Flow

Module init validates parameters in `mlx4_verify_params()`, creates the global single-threaded `mlx4_wq`, and registers the PCI driver. Probe allocates a devlink-backed `mlx4_priv`, creates persistent state, registers devlink parameters, enables the PCI device, requests BARs, sets DMA masks, initializes crash dump and catastrophic-error support, then calls `mlx4_load_one()`.

`mlx4_load_one()` initializes auxiliary-device support and core locks, detects PF versus VF, claims PF ownership, resets PF hardware, initializes the command interface, and enters either master, slave, or native flow. Slave mode initializes the multifunction communication channel and asks the PF for caps. Master mode may query device caps, enable SR-IOV through `mlx4_enable_sriov()`, reset, and restart command setup so firmware-visible resources match VF layout. After firmware/HCA init it initializes master multifunction resources, allocates EQ tables, chooses MSI-X or INTx, initializes software steering lists for PF/native devices, initializes quotas, calls `mlx4_setup_hca()`, arms the master communication channel, creates per-port devlink/sysfs state, registers the mlx4 device, starts link sensing, and clears the `pf_loading` probe-defer gate.

`mlx4_setup_hca()` has a strict resource ladder: UAR table and driver UAR, kernel access region mapping, PD/XRCD/MR tables, MCG table and MAD demux for non-slaves, EQ table, event-driven command mode and NOP interrupt test, CQ/SRQ/QP tables, counters, default counters, IB port default capabilities, and `SET_PORT`. Every failure path unwinds in reverse and switches commands back to polling before tearing down EQs.

Unload and error recovery reverse the same hierarchy. `mlx4_unload_one()` saves current port types, stops sensing, unregisters upper consumers, closes ports, frees resource trackers, default counters, QP/SRQ/CQ/EQ/MCG/MR/XRCD/PD/UAR resources, clears steering, disables MSI-X, releases ownership, destroys slave special-QP caps, frees VF metadata, cleans auxiliary devices, and preserves persistent fields through `mlx4_clean_dev()`. AER and suspend paths mark device state, unload under devlink/interface locks, and later reload through `mlx4_load_one()` with saved VF and port state.

## State And Persistence Behavior

The most important persistent anchor is `struct mlx4_dev_persistent`, stored in PCI drvdata. It survives `mlx4_clean_dev()` across reload/reset flows and carries the PCI device pointer, interface and PCI status mutexes, `num_vfs`, per-port VF distribution, saved current/possible port types, crash-dump state, and device state flags. `struct mlx4_priv` is zeroed during clean reloads, then rebuilt around that persistent pointer.

Runtime state is distributed across `dev->caps`, `dev->phys_caps`, `dev->quotas`, `dev->flags`, `dev->dev_vfs`, and many tables inside `mlx4_priv`: command context, firmware memory, UAR/MR/CQ/EQ/SRQ/QP/MCG tables, counters bitmap, port info, steering lists, bond map, slave state, and resource tracker. Port type changes persist for restart through `persist->curr_port_type` and `persist->curr_port_poss_type`. SR-IOV intent persists in `persist->num_vfs` and `persist->nvfs`; actual VF metadata is allocated per load. Devlink driverinit values persist in devlink until reload and are copied back into module-level globals before reload-up.

Synchronization is explicit: devlink lock guards load/unload/reload paths; `interface_state_mutex`, `device_state_mutex`, and `pci_status_mutex` guard persistent status; `port_mutex` guards port type and MTU reconfiguration; `bond_mutex` guards bond/remap state; `cmd.slave_cmd_mutex` serializes VF communication setup; `pf_loading` defers VF probe while the PF is enabling SR-IOV; table-specific locks protect resource allocators.

## Dependencies And Integration Points

The file depends on Linux PCI, DMA, devlink, sysfs, workqueue, MSI-X, PM, AER, RDMA core headers, and mlx4 internal modules (`fw.h`, `icm.h`, command wrappers, table allocators, resource tracker, sense, port, EQ/CQ/QP/SRQ/MR/UAR code). It exports symbols consumed by mlx4 Ethernet, mlx4 InfiniBand, virtualization, and auxiliary-device paths. It integrates with firmware through commands such as `QUERY_FW`, `MAP_FA`, `RUN_FW`, `QUERY_DEV_CAP`, `INIT_HCA`, `QUERY_HCA`, `SET_PORT`, `QUERY_ADAPTER`, `ALLOC_RES`, and `FREE_RES`. It integrates with userspace through module parameters, devlink params/reload/ports, sysfs port attributes, PCI device IDs, and ethtool-visible counter allocation used by upper drivers.

## Risks

The riskiest area is lifecycle unwinding: `mlx4_load_one()` and `mlx4_setup_hca()` have many partially initialized stages and mode-specific cleanup paths. Regressions commonly show as leaked ICM memory, stale MSI-X vectors, double cleanup of steering/counters, or a device left in command-event mode after a failed NOP. SR-IOV transitions are also fragile because PF reset, firmware caps, `pf_loading`, existing VFs, and slave probe deferral must align. Port type changes unregister and re-register upper devices, so they can race with userspace, link sensing, and reload unless locks are held consistently. Timestamp mapping and BlueFlame mapping depend on BAR offsets and firmware caps. Devlink driverinit values mutate module globals at reload time, so validation must catch invalid combinations before hardware reinit.

## Test Signals

Useful signals include successful probe/remove across PF, VF, and no-SR-IOV modes; devlink reload with changed `max_macs`, `enable_64b_cqe_eqe`, `enable_4k_uar`, and crash-dump settings; sysfs/devlink port type switching between IB/ETH/auto; suspend/resume and PCI AER reset recovery; MSI-X fallback after a failed NOP interrupt test; counter allocation/free under native and multifunction modes; low-memory/kdump profile boot; active VF removal warnings; and leak/error-path testing that forces failures at each table initialization stage.
