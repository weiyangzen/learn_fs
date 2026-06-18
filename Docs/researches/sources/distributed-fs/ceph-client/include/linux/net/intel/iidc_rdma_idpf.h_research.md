# sources/distributed-fs/ceph-client/include/linux/net/intel/iidc_rdma_idpf.h

Purpose: extends the common IIDC RDMA model for IDPF-managed vports, mapped memory regions, function type reporting, vport control, reset requests, and synchronous virtchnl messaging.

Important APIs and types: `struct iidc_rdma_vport_dev_info` connects a vport auxiliary device to the core auxiliary device, netdev, and vport id. `struct iidc_rdma_vport_auxiliary_dev` and `struct iidc_rdma_vport_auxiliary_drv` wrap auxiliary bus objects and vport event handling. `enum iidc_function_type` distinguishes PF and VF. `struct iidc_rdma_lan_mapped_mem_region` describes MMIO region address, size, and start offset. `struct iidc_rdma_priv_dev_info` exposes reserved MSI-X entries/count, function type, number of mapped memory regions, and the region array. Functions include `idpf_idc_vport_dev_ctrl()`, `idpf_idc_request_reset()`, and `idpf_idc_rdma_vc_send_sync()`.

Control flow: IDPF creates core and vport auxiliary devices; an RDMA vport driver binds, uses private info for MSI-X and mapped memory, controls vport up/down state, sends synchronous virtchnl messages, and receives vport events through its auxiliary driver handler. Reset requests are routed through IDPF's IDC hooks.

State and persistence: state is runtime auxiliary-device linkage, vport id, reserved interrupts, mapped LAN memory windows, and virtchnl exchange buffers. No durable state is owned here.

Dependencies and integration points: depends on auxiliary bus, netdev/MSI-X types from the common include stack, endian types, and IDPF IDC/virtchnl implementation. It integrates RDMA auxiliary drivers with IDPF's split core/vport device model.

Risks and test signals: risks include vport/core auxiliary lifetime races, incorrect `num_memory_regions` endian handling, mapped region bounds mistakes, synchronous virtchnl buffer length errors, reserved MSI-X leaks, and PF/VF behavior divergence. Test vport auxiliary probe/remove, up/down control, reset request behavior, virtchnl send/receive length handling, mapped memory enumeration, and PF/VF configurations.
