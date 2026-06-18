# sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_ice.h

Purpose: extends the common IIDC RDMA interface with ICE-specific queue-set, QoS, VSI filter, reset, and MSI-X vector allocation APIs.

Important APIs and types: constants define maximum user priorities and DSCP PFC mode. `struct iidc_rdma_qset_params` carries TEID, RDMA-provided queue-set handle, vport id, and traffic class. `struct iidc_rdma_qos_info` and `struct iidc_rdma_qos_params` expose per-TC context, relative bandwidth, priority type, virtual user priorities, UP-to-TC map, vport scheduling settings, TC count, PFC mode, and DSCP map. `struct iidc_rdma_priv_dev_info` provides PF id, vport id, netdev, QoS info, and MMIO base. ICE callbacks include `ice_add_rdma_qset()`, `ice_del_rdma_qset()`, `ice_rdma_request_reset()`, `ice_rdma_update_vsi_filter()`, `ice_alloc_rdma_qvector()`, and `ice_free_rdma_qvector()`.

Control flow: an RDMA driver receives ICE private device info, allocates vectors, adds qsets to traffic classes, enables VSI filtering, reacts to QoS changes from IIDC events, and removes qsets/vectors during teardown. Reset requests are sent back to ICE using function or device reset types from the common header.

State and persistence: runtime state includes qset TEIDs returned by ICE, MSI-X vector reservations, vport/QoS snapshots, filters, and MMIO access. No state is persistent outside hardware configuration and driver-owned objects.

Dependencies and integration points: depends on DCBNL TC constants, DSCP sizing from the common include stack, netdev, MSI-X, MMIO, and ICE LAN driver internals. It connects RDMA scheduling and filtering to ICE's LAN resource manager.

Risks and test signals: risks include stale TEID use after qset deletion, TC/UP/DSCP map mismatch, vector leaks, enabling filters on wrong VSI, reset request escalation, and QoS array bounds over `IEEE_8021QAZ_MAX_TCS` or DSCP_MAX. Test qset add/delete, vector allocate/free, MTU/TC/QoS changes, VSI filter enable/disable, reset requests, PFC/DSCP modes, and teardown after partial allocation failures.
