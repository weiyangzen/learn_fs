# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice.h

## Purpose
`ice.h` is the central driver-private header for the ICE Linux Ethernet driver. For this subset, it supplies the shared PF/VSI data model that devlink, health, adapter sharing, and ARFS operate on.

## Important APIs, Types, And Functions
The file defines constants for queue descriptors, MSI-X minima, queue mapping, reset waiting, MTU/TSO limits, switch filter priorities, and Flow Director statistics. Iteration macros cover VSIs, Tx/Rx/XDP queues, allocated queues, q_vectors, and channel traffic classes.

Key types include `enum ice_feature`, `struct ice_channel`, `struct ice_txq_meta`, `struct ice_tc_cfg`, `struct ice_qs_cfg`, `struct ice_sw`, `enum ice_pf_state`, `enum ice_vsi_state`, `struct ice_vsi`, `struct ice_q_vector`, `enum ice_pf_flags`, `struct ice_eswitch`, `struct ice_adapter` pointer usage, `struct ice_pf_msix`, and the central `struct ice_pf`. `struct ice_pf` owns devlink regions, the PF devlink port, adapter reference, VSI array, queue bitmaps, locks, reset counters, hardware object, eswitch state, dynamic SF xarrays, DPLL/hwmon/health state, and RDMA core device info.

Inline helpers include `ice_irq_dynamic_ena()`, `ice_netdev_to_pf()`, XDP/XSK helpers, `ice_get_max_txq()`, `ice_get_max_rxq()`, `ice_get_main_vsi()`, `ice_get_ctrl_vsi()`, `ice_find_vsi()`, `ice_is_switchdev_running()`, `ice_is_adq_active()`, RDMA capability setters, and primary/dual NAC helpers.

## Control Flow
Most implementation files include `ice.h` to access PF/VSI state and common helpers. Devlink reload uses `ice_get_main_vsi()`, state flags, init/deinit prototypes, and ADQ checks. Port code uses PF dynamic-port xarrays and VSI state. Health stores `struct ice_health` inside `struct ice_pf`. ARFS stores filter tables and counters inside the PF VSI.

## State And Persistence
This file defines runtime state more than behavior. Persistent effects are represented indirectly through fields such as NVM PHY types, link default override, RDMA enable flags, eswitch mode, and hardware capabilities mirrored from firmware. Reset state bits and counters govern rebuild behavior. Locks define concurrency domains: queue allocation, switch/VSI allocation, TC changes, auxiliary device access, LAG, AQ wait lists, xarray-backed dynamic ports, and health reporter state.

## Dependencies And Integration Points
`ice.h` pulls in Linux netdevice, PCI, devlink, XDP, tc, bridge, tunnel, auxiliary bus, CPU rmap, and many ICE internal headers. It is the integration hub for devlink, health, ARFS, adapter sharing, scheduler, RDMA, SR-IOV, eswitch, PTP, DPLL, GNSS, and queue management.

## Risks And Test Signals
Because this header defines central layouts, changes have broad ABI and compile impact inside the driver. Risks include cacheline/layout churn, incorrect state bit ordering before `ICE_STATE_NOMINAL_CHECK_BITS`, lock misuse, stale PF/VSI pointer access during reset, and helper assumptions such as `pf->vsi[0]` being the main VSI. Test signals include full driver build, probe/remove, reset/reload, SR-IOV and switchdev scenarios, XDP/XSK queue setup, RDMA enable/disable, and ARFS/RFS acceleration operation.
