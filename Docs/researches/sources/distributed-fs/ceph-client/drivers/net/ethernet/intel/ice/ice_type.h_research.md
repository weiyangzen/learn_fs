# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_type.h

Purpose: defines core hardware-facing types, constants, capabilities, persistent state containers, and enums used throughout the ice driver. It is the central model of device, function, port, scheduler, DCB, PTP, NVM, switch, mailbox, and forwarding state.

Important APIs and types: top-level `struct ice_hw` holds MMIO base, backpointer, port info, MAC type, PCI IDs, scheduler topology, VSI contexts, bus/flash/capability data, control queues, firmware/API versions, package metadata, tunnel/DVM/filter/RSS state, mailbox snapshot, PTP hardware, and CGU metadata. `struct ice_port_info` owns link, MAC, PHY, flow control, scheduler tree, QoS, and per-port locks. Capability structs include `ice_hw_common_caps`, `ice_hw_func_caps`, and `ice_hw_dev_caps`. Other major types cover link status, PHY info, Flow Director profiles, TSPLL and clock source enums, NVM/OROM/netlist banks, TX scheduler nodes, DCBX config, switch recipe state, mailbox malicious-VF detection, and stats.

Control flow role: this header does not implement algorithms, but nearly every driver subsystem branches on these enums and fields. Examples include MAC-type dispatch for TSPLL, VSI-type dispatch in datapath and TC, DCB mode selection for queue priority, reset source handling, switch forwarding action selection, and capability checks for queues, MSI-X, RSS, PTP, RDMA, SR-IOV, NVM updates, and DVM.

State and persistence: many structures mirror persistent device or firmware state: flash bank locations and versions, active package metadata, scheduler tree TEIDs and bandwidth profiles, link/PHY requested modes, DCB desired/local/remote configs, PTP function ownership, switch recipe counts, Flow Director profiles/filter counts, RSS lists, mailbox snapshots, and hardware statistics. Some fields are protected by mutexes such as scheduler, tunnel, filter profile, Flow Director, and RSS locks.

Dependencies and integration: includes generated hardware definitions, device IDs, OS abstraction, control queue, LAN descriptor definitions, flex/parser types, protocol types, sideband queue commands, VLAN mode, fwlog, wait queues, and DSCP definitions. It is consumed by almost all C files in the driver.

Risks: because this is a shared contract header, field changes have broad ABI-like impact inside the driver. Bit definitions must match firmware/hardware registers. Lock ownership is documented by field grouping rather than enforced by types. Capability or enum mismatches can lead to unsupported hardware paths, wrong queue counts, incorrect TSPLL programming, or invalid switch actions.

Test signals: broad compile coverage, probe on multiple MAC types, firmware/API compatibility checks, NVM bank/version reads, DCB/DSCP configuration, scheduler and devlink-rate operations, SR-IOV/VF mailbox stress, Flow Director/RSS/filter programming, PTP/TSPLL initialization, reset flows, and ethtool stats validation.
