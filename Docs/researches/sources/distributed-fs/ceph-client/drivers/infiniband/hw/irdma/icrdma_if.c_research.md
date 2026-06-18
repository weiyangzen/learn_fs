# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/icrdma_if.c

## Purpose
`icrdma_if.c` connects Gen2 IRDMA to the ice IIDC RDMA auxiliary interface. It handles QoS and MTU events, critical error reset requests, LAN qset registration, MSI-X vector allocation, device-info population, control/runtime initialization, IB registration, and remove cleanup.

## Important APIs, types, and functions
Important functions are `icrdma_prep_tc_change`, `icrdma_fill_qos_info`, `icrdma_iidc_event_handler`, `icrdma_lan_register_qset`, `icrdma_lan_unregister_qset`, `icrdma_request_reset`, `icrdma_init_interrupts`, `icrdma_deinit_interrupts`, `icrdma_fill_device_info`, `icrdma_probe`, and `icrdma_remove`. The exported object is `icrdma_core_auxiliary_drv`.

## Control flow, state, and persistence
Probe allocates `irdma_device` and `irdma_pci_f`, fills Gen2 PF state, allocates RDMA qvectors from ice, runs control initialization, derives L2 parameters from IIDC QoS, runs runtime initialization, registers the IB device, enables the VSI filter, and stores drvdata. Event handling updates MTU, suspends QPs before TC changes, rebuilds QoS after TC changes, and requests reset on critical PE/HMC/push errors. Remove disables the VSI filter, unregisters the IB device, frees qvectors, destroys AH locking, and frees `rf`.

## Dependencies and integration points
The file depends on `<linux/net/intel/iidc_rdma_ice.h>`, ice RDMA qvector/qset APIs, common `main.h`, work scheduler handling, and RDMA core registration. It bridges LAN traffic-class scheduling with IRDMA work scheduler nodes.

## Risks and test signals
Risks include timeout while waiting for QP suspend, qvector partial allocation cleanup, TC-change races, reset requests on recoverable critical events, and qset TEID lifetime. Tests should simulate MTU/TC/critical events, verify qset register/unregister calls, inject qvector allocation failures, and exercise iWARP versus RoCE protocol selection.
