# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_lib.h Research

## Purpose
`ice_lib.h` declares the internal VSI library interface used across the ICE driver. It exposes creation, configuration, reset, queue, interrupt, RSS, TC, stats, bandwidth, default forwarding, VLAN, feature-bit, security, loopback, and L2 tag extraction helpers implemented in `ice_lib.c`.

## Important APIs, Types, And Functions
The header includes `ice.h` and `ice_vlan.h`, so its declarations are built around core driver objects such as `struct ice_pf`, `struct ice_vsi`, `struct ice_hw`, `struct ice_q_vector`, `struct ice_ring_container`, `struct ice_tx_ring`, `struct ice_rx_ring`, `struct ice_port_info`, `struct ice_vsi_cfg_params`, `struct ice_vsi_ctx`, `enum ice_vsi_type`, `enum ice_disq_rst_src`, and `enum ice_feature`.

It defines `ICE_VSI_FLAG_INIT` and `ICE_VSI_FLAG_NO_INIT` for create-versus-update/rebuild flows. It also defines the QRX context register index/bit offset used for `ice_vsi_update_l2tsel()` and declares `enum ice_l2tsel` with the two supported extraction modes: first VLAN tag into `L2TAG2_2ND` or first VLAN tag into `L2TAG1`.

The exported function groups are: VSI lifecycle (`ice_vsi_setup()`, `ice_vsi_alloc()`, `ice_vsi_cfg()`, `ice_vsi_rebuild()`, `ice_vsi_decfg()`, `ice_vsi_release()`, `ice_vsi_delete()`, `ice_vsi_free()`); open/close/pause/resume (`ice_vsi_close()`, `ice_ena_vsi()`, `ice_dis_vsi()`); queue and interrupt control (`ice_vsi_cfg_msix()`, ring start/stop helpers, IRQ/ring frees, ITR/INTRL writers, NAPI association); RSS/CRC/TC helpers; reset-state helpers; stats helpers; default-VSI/link/bandwidth helpers; VLAN-zero and VLAN-count helpers; feature support helpers; and security/local-loopback/L2TSEL update helpers.

## Control Flow
This header does not implement control flow, but it codifies the sequence expected by callers. New VSI callers prepare `struct ice_vsi_cfg_params`, set `ICE_VSI_FLAG_INIT`, and call `ice_vsi_setup()`. Reset callers reuse an existing VSI through `ice_vsi_rebuild()` with either init or no-init flags. Shutdown callers typically move through `ice_dis_vsi()` or `ice_vsi_close()` before `ice_vsi_release()`. TC/mqprio/DCB callers use `ice_vsi_cfg_tc()` while queues are quiesced, then refresh netdev TC state with `ice_vsi_cfg_netdev_tc()`.

## State, Persistence, And Dependencies
The header owns no storage beyond constants and the `enum ice_l2tsel` declaration. Its ABI is internal to the kernel driver build; persistence lives in the objects passed through the prototypes. Because it includes broad ICE core headers, any consumer sees the full core driver type graph and must obey locking/lifetime rules implemented in `ice_lib.c`, such as RTNL for NAPI queue association, reset-state checks around rebuild/release, and PF/VSI ownership of queue and stats arrays.

## Integration Points
The declarations are consumed by PF setup and reset code in `ice_main.c`, VF/SR-IOV support, DCB and mqprio paths, devlink reset wait paths, switchdev/eswitch security paths, LAG migration logic, virtchnl VLAN tag extraction paths, and ethtool/statistics code. The header acts as the stable local boundary between VSI lifecycle machinery and higher-level policy modules.

## Risks
Because this is a broad internal header, unrelated modules can depend directly on low-level lifecycle and hardware-update routines. Misordered calls are possible if a caller treats declarations as independent operations instead of phases in the VSI state machine. The `ice_vsi_update_l2tsel()` constants are hardware-layout details exposed in the public local header; future register-layout changes require coordinated updates. `ICE_VSI_FLAG_INIT` is a single bit with `NO_INIT` defined as zero, so default-zero parameter structs can accidentally request an update/rebuild flow if a setup wrapper forgets to set the init flag; `ice_vsi_setup()` defends against that with a warning.

## Test Signals
Compile coverage should include all modules that include `ice_lib.h`, especially after signature or enum changes. Runtime signals mirror `ice_lib.c`: PF/SF/VF/CTRL setup and release, reset rebuilds, DCB/mqprio TC updates, RSS programming, IRQ/NAPI association, default-VSI operations, bandwidth limit policy, VLAN-zero behavior, feature support gating by device ID/MAC type, security toggles, local loopback, and virtchnl-driven L2 tag extraction updates.
