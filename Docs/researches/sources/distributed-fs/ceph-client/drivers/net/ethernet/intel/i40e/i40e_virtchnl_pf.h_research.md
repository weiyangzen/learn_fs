# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_virtchnl_pf.h

Purpose: this header defines the PF-side VF data model and exported SR-IOV/virtchnl interfaces for the i40e driver. It is the contract used by `i40e_virtchnl_pf.c` and other PF modules that need to reset VFs, process mailbox messages, publish VF netdevice operations, or notify VFs of link/reset changes.

Important APIs/types: it declares `enum i40e_vf_states`, `enum i40e_vf_capabilities`, `enum i40e_queue_ctrl`, `struct i40evf_channel`, `struct i40e_mdd_vf_events`, and `struct i40e_vf`. `struct i40e_vf` holds the PF pointer, VF id, virtchnl API version, driver capability mask, default MAC, port VLAN, trust/spoof/link/rate settings, VSI ids, queue counts, malicious-driver-detection counters, state/capability bitmaps, ADq channel state, cloud filter list, and RDMA queue-vector list. Function declarations expose SR-IOV allocation/free/configure, mailbox processing, VFLR processing, VF reset, link/reset notifications, netlink VF administration hooks, MSI restore, and stats collection.

Control flow and state: this header centralizes the state bits that gate virtchnl handling: `INIT`, `ACTIVE`, `RDMAENA`, `DISABLED`, promiscuous bits, `PRE_ENABLE`, `RESETTING`, and `RESOURCES_LOADED`. The constants for VLAN ids, queue-type mapping, VLAN priority masks, promisc flags, and reset wait counts are used by validation and hardware programming in the C file.

Dependencies and integration: it includes Linux virtchnl and netdevice headers plus `i40e_type.h`. It integrates PF code with PCI SR-IOV, netdev VF callbacks, link notification paths, and i40e hardware type definitions.

Risks and test signals: correctness depends on bit numbers staying aligned with code that uses `test_bit`/`set_bit`, and on cached VF fields being complete enough to rebuild VFs after reset. Tests should cover compile-time API consumers, VF reset state transitions, ADq channel array bounds, port VLAN priority extraction, and netdev VF handler availability under `CONFIG_PCI_IOV`.
