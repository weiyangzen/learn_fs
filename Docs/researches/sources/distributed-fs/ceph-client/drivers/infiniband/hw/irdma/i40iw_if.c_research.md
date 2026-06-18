# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/i40iw_if.c

## Purpose
`i40iw_if.c` connects the IRDMA driver to the i40e auxiliary/client interface for Gen1 iWARP devices. It handles client probe/remove, open/close, L2 parameter changes, reset requests, device-info population, control/runtime hardware bring-up, and IB device registration.

## Important APIs, types, and functions
Important local functions are `i40iw_l2param_change`, `i40iw_close`, `i40iw_request_reset`, `i40iw_fill_device_info`, `i40iw_open`, `i40iw_probe`, and `i40iw_remove`. The file exports `struct auxiliary_driver i40iw_auxiliary_drv` for module registration.

## Control flow, state, and persistence
Probe registers an i40e RDMA client. The i40e client `open` callback allocates `irdma_device` and `irdma_pci_f`, fills Gen1 PF-only iWARP state, runs `irdma_ctrl_init_hw`, builds L2 parameters from i40e QoS data, runs `irdma_rt_init_hw`, and registers the IB device. Close marks reset if requested, clears status, emits an IB port event, and unregisters the IB device. Runtime state is held in `iwdev`, `rf`, i40e client data, and the registered ibdev lifetime.

## Dependencies and integration points
The file depends on `<linux/net/intel/i40e_client.h>`, Gen1 hardware constants, common `main.h` APIs, and RDMA core device lookup by netdev. It integrates with i40e-provided MSI-X vectors, netdev, QoS parameters, and reset operations.

## Risks and test signals
Risks include missing ibdev during close/L2 callbacks, error unwind leaks between control/runtime init, incorrect DCB VLAN mode detection, and reset ordering with i40e. Tests should cover open failure at each stage, close with and without reset, MTU change propagation, QoS mapping, and module probe/remove cycles.
