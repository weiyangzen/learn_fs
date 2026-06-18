# sources/distributed-fs/ceph-client/include/linux/net/intel/i40e_client.h

Purpose: defines the client interface between the Intel i40e LAN driver and auxiliary clients such as iWARP/RDMA consumers.

Important APIs and types: version macros and `struct i40e_client_version` identify the interface. `struct i40e_qv_info` and flexible `struct i40e_qvlist_info` describe MSI-X vector to CEQ/AEQ/ITR mappings. QoS types `i40e_prio_qos_params`, `i40e_qos_params`, and `i40e_params` expose priority-to-traffic-class and MTU information. `struct i40e_info` describes a LAN device to clients: MAC, netdev, PCI device, auxiliary device, MMIO base, function id/type, PF private pointer, qvector list, mutable L2 params, operations, MSI-X entries, ITR index, and firmware version. `struct i40e_ops` lets clients set qvector lists, send virtchnl messages, request PF/core resets, and update VSI context flags. `struct i40e_client_ops` lets the LAN driver open/close clients, notify L2 param changes, deliver virtchnl messages, signal VF resets/enables, and query VF offload capability. `struct i40e_client_instance` and `struct i40e_client` track registered clients, state, refcount, flags, type, and ops.

Control flow: an i40e client registers with the LAN driver, which creates client instances for ready LAN devices and calls `open()`. The client requests queue/vector setup, sends or receives virtchnl traffic, receives MTU/QoS/VF/reset notifications, and calls reset/update hooks as needed. On netdev removal, reset, or client unregister, `close()` is invoked and `i40e_client_device_unregister()` tears down the association.

State and persistence: state is runtime coordination state: client lists, per-instance open state, refcounts, qvector allocations, MSI-X entries, L2 parameters, and firmware version snapshots. There is no persistent state; hardware configuration effects are mediated by i40e.

Dependencies and integration points: depends on auxiliary bus, netdev, PCI/MSI-X, MMIO, virtchnl messaging, and i40e PF internals. It bridges Ethernet PF ownership with RDMA/PE-engine style clients.

Risks and test signals: risks include interface version mismatch, qvector flexible-array sizing errors, stale `netdev` or `pcidev` during reset, failing to close on unregister, virtchnl message length validation, VF id misuse, and inconsistent QoS/MTU notifications. Test client register/unregister, PF reset and core reset, MTU change callbacks, VF enable/reset/capability paths, qvector setup with invalid indices, and concurrent netdev removal.
