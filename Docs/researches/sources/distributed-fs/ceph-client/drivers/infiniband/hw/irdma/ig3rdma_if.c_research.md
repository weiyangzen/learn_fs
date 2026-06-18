# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/ig3rdma_if.c

## Purpose
`ig3rdma_if.c` manages the Gen3 IDPF core auxiliary device. It initializes virtual-channel support, maps RDMA MMIO regions, configures the shared `irdma_pci_f`, starts the common control hardware path, and enables or disables vport device creation through IDPF.

## Important APIs, types, and functions
Important functions are `ig3rdma_idc_core_event_handler`, `ig3rdma_vchnl_send_sync`, `ig3rdma_vchnl_init`, `ig3rdma_request_reset`, `ig3rdma_cfg_regions`, `ig3rdma_decfg_rf`, `ig3rdma_cfg_rf`, `ig3rdma_core_probe`, and `ig3rdma_core_remove`. The exported driver object is `ig3rdma_core_auxiliary_drv`.

## Control flow, state, and persistence
Core probe allocates `irdma_pci_f`, initializes virtual-channel state and workqueue, maps the PF or VF RDMA window plus additional memory regions, sets protocol and reset operations, runs `irdma_ctrl_init_hw`, saves drvdata, and asks IDPF to enable vport devices. Remove disables vport devices, deinitializes control hardware, unmaps/free regions and locks, destroys workqueues, and frees `rf`. Reset warning events mark `rf->reset` and clear virtual-channel availability.

## Dependencies and integration points
The file depends on `<linux/net/intel/iidc_rdma_idpf.h>`, IDPF virtual-channel and reset APIs, common IRDMA control initialization, Gen3 hardware region definitions, and `main.c` vport probe for runtime device creation.

## Risks and test signals
Risks include virtual-channel timeout leaving control paths blocked, MMIO leaks on partial setup failure, core/vport lifetime ordering, and function type misclassification. Tests should cover PF/VF region setup, virtual-channel timeout and recovery, core probe failure injection, vport enable/disable sequencing, and reset-warning event handling.
