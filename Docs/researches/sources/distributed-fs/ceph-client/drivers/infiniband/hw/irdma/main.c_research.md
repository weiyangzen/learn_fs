# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/main.c

## Purpose
`main.c` is the module entry/exit and Gen3 vport integration file. It registers network notifiers, exposes module metadata, handles Gen3 vport auxiliary probe/remove and MTU events, and registers/unregisters all generation auxiliary drivers.

## Important APIs, types, and functions
Important functions include `irdma_register_notifiers`, `irdma_unregister_notifiers`, `irdma_log_invalid_mtu`, `ig3rdma_idc_vport_event_handler`, `ig3rdma_vport_probe`, `ig3rdma_vport_remove`, `irdma_init_module`, and `irdma_exit_module`. It registers Gen1 `i40iw_auxiliary_drv`, Gen2 `icrdma_core_auxiliary_drv`, Gen3 core, and Gen3 vport drivers.

## Control flow, state, and persistence
Module init registers auxiliary drivers in order and unwinds earlier registrations if a later registration fails, then registers IP/netdevice notifiers. Gen3 vport probe retrieves the already-initialized core `rf`, allocates an `irdma_device`, fills vport/netdev/RoCE defaults, runs runtime initialization, registers the IB device, and stores drvdata. Vport remove unregisters the IB device. Module exit unregisters notifiers and all auxiliary drivers.

## Dependencies and integration points
The file depends on Linux auxiliary bus, IDPF vport IIDC APIs, network notifier callbacks implemented elsewhere, and common runtime init/IB registration paths. It links Gen3 core setup from `ig3rdma_if.c` to per-vport runtime devices.

## Risks and test signals
Risks include registration/unregistration ordering, missing cleanup when `ib_alloc_device` fails, core drvdata absence during vport probe, notifier callbacks after device removal, and MTU warning correctness. Tests should cover module init failure unwinds, vport probe/remove, MTU events, notifier registration lifecycle, and Gen3 core-before-vport ordering.
