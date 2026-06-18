# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/main.c

## Purpose
`main.c` is the primary mlx5 core PCI driver and device lifecycle implementation. It registers the PCI driver, probes/removes devices, initializes software and PCI resources, enables firmware/HCA functions, configures capabilities, loads and unloads runtime subsystems, handles devlink registration, PCI error recovery, suspend/resume, shutdown, and VF-to-PF core-device lookup.

## Important APIs, types, and functions
Major entry points include module init/exit `mlx5_init()`/`mlx5_cleanup()`, PCI callbacks `probe_one()`, `remove_one()`, `shutdown()`, `mlx5_suspend()`, `mlx5_resume()`, AER handlers, `mlx5_mdev_init()`/`mlx5_mdev_uninit()`, `mlx5_init_one()`/`mlx5_uninit_one()`, `mlx5_load_one()`/`mlx5_unload_one()`, light-probe variants, recovery helpers, and exported VF accessors. Capability code includes `mlx5_core_get_caps()`, `set_hca_cap()`, handlers for general, general2, atomic, ODP, RoCE, and port-selection caps, plus `mlx5_core_enable_hca()`/`mlx5_core_disable_hca()`.

## Control flow
Module init verifies parameters, registers debugfs, initializes mlx5e and SF driver support, then registers the PCI driver. Probe allocates devlink/core device state, assigns PF/VF type, initializes mdev software, enables PCI and maps BAR/ISEG, initializes shared devlink, then runs full device initialization. Full init sets up firmware command access, enables HCA, allocates startup pages, queries timeouts/capabilities, initializes once-only software objects, registers devlink parameters, loads runtime subsystems, marks the interface up, registers auxiliary devices, enables crash dump and hwmon, and saves PCI state.

Runtime load allocates BFREGs, starts event/pagealloc machinery, creates IRQ/EQ tables, loads clock/tracer/fw-reset/hyperv/resource-dump/FPGA/flow-steering/EC/LAG/SR-IOV/SF/devlink trap pieces in a strict order. Unload reverses that order. Uninit unregisters user-visible devices, unloads if up, unregisters devlink params, cleans once-only subsystems, tears down the HCA, unregisters devlink, then PCI close and mdev uninit happen in remove.

PCI error handling enters error state, unloads, disables PCI, waits for slot reset vitality, then reloads and marks health reporter healthy on resume. Shutdown tries firmware fast/force teardown before falling back to normal unload.

## State and persistence behavior
State spans `struct mlx5_core_dev`, devlink, PCI config, BAR mappings, firmware command state, health pollers, capability caches, notifier heads, debugfs, auxiliary devices, IRQ/EQ resources, flow steering, eswitch/SR-IOV/SF/LAG/FPGA/tracer resources, and interface state bits. Persistent hardware state includes PCI enable/master/PTM/atomic settings, HCA capabilities set in firmware, startup pages, and NV/firmware state affected by subordinate modules. Software state is carefully unwound through labeled error paths.

## Dependencies and integration points
The file integrates nearly every mlx5 subsystem: command, health, page allocation, events, IRQ/EQ, flow steering, eswitch, SR-IOV, SF, devlink, devcom, MPFS, VXLAN/Geneve, clock, FPGA, LAG, ECPF, fw reset, hwmon, crash dump, PCI VSC, and mlx5e. It depends heavily on Linux PCI, devlink, module, DMA, debugfs, workqueue, and AER APIs.

## Risks and edge cases
Lifecycle ordering is the dominant risk. A missing rollback in probe/load or wrong unload order can leak IRQs, flow tables, devlink params, health work, or PCI resources. Firmware wait loops must honor removal via `MLX5_BREAK_FW_WAIT`. Capability setting depends on current/max cap caches and devlink driver-init params. Light probe deliberately initializes only a subset and must transition cleanly to full reload. Shutdown fast teardown intentionally enters error state and frees IRQs without full software cleanup.

## Test signals
Test module load/unload, probe/remove on PF/VF/SF-capable hardware, interface load/unload/reload, devlink reload and parameter registration, light probe, PCI AER reset recovery, suspend/resume, shutdown/kexec, SR-IOV enable/disable, firmware init timeout paths, capability negotiation with RoCE on/off, fault injection at each labeled init/load step, and lockdep for devlink and interface-state locking.
