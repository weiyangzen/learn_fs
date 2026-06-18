# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/nic.h

Purpose: this EF10-family NIC header defines PHY type constants, EF10 statistic indexes, EF10 private NIC state, and exported NIC type instances.

Important types and APIs: the first enum lists legacy PHY type IDs used by diagnostics and MCDI PHY code. The large EF10 stats enum extends generic stats with port, RX/TX, FEC, CTPIO, and datapath counters. `struct efx_ef10_nic_data` stores EF10-specific runtime state: MCDI DMA buffer, warm boot count, VI and PIO allocation, write-combining mappings, MC stats buffers, firmware workaround flags, datapath capabilities, firmware IDs, PF/VF/vswitch state, vport MAC/VLANs, UDP tunnel ports, and licensed features. It declares `efx_ef10_tx_tso_desc()` and NIC type externs for Huntington and X4.

Control flow and integration: controller implementations allocate this private structure as `efx->nic_data` and use it during probe, reset recovery, datapath capability checks, stats, SR-IOV, UDP tunnel restore, and licensed feature checks such as PTP TX timestamps.

State and risks: many fields are recovery flags after MC reboot (`must_restore_piobufs`, `must_check_datapath_caps`, `must_probe_vswitching`, `udp_tunnels_dirty`). Incorrect handling can leave firmware resources stale after reset. Test signals include EF10 probe/reset, MC reboot recovery, stats, TSOv2, PIO/CTPIO, SR-IOV, UDP tunnel offload, and licensed timestamp feature behavior.
