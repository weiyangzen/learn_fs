# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x.h

## Purpose
`bnx2x.h` is the central private header for the Broadcom/QLogic Everest `bnx2x` Ethernet driver. It defines the main driver state object, chip-family predicates, MMIO/shared-memory accessors, ring geometry, queue indexing, fast-path data structures, slow-path data structures, feature flags, multi-function mode helpers, and cross-file prototypes. Most implementation files in the driver include this header to share a single contract for device state and hardware programming.

## Important APIs, Types, and Data
- Version and config constants: `DRV_MODULE_VERSION`, `BNX2X_BC_VER`, `DRV_MODULE_NAME`, debug masks, and `enum bnx2x_int_mode`.
- MMIO/shared-memory helpers: `REG_RD/WR`, `REG_RD_IND/REG_WR_IND`, DMAE helper macros, `SHMEM_RD/WR`, `SHMEM2_RD/WR`, `MF_CFG_RD/WR`, and `DOORBELL_RELAXED`.
- Chip and function identity: `struct bnx2x_common` plus `CHIP_IS_E1/E1H/E2/E3`, `CHIP_REV_*`, `BP_PATH`, `BP_PORT`, `BP_FUNC`, `BP_VN`, and related firmware mailbox index macros.
- Fast-path rings and queues:
  - `struct sw_rx_bd`, `struct sw_tx_bd`, `struct sw_rx_page`, and `union db_prod` wrap host-side buffer metadata and doorbell producer state.
  - `struct bnx2x_fp_txdata` tracks one TX queue/COS ring, including descriptor ring DMA address, producer/consumer counters, CID, doorbell payload, and status-block consumer pointer.
  - `struct bnx2x_fastpath` tracks one RX/TX/NAPI context, status block shortcuts, RX BD/CQE/SGE rings, TPA/GRO state, queue identifiers, producers/consumers, and allocation pool.
- Aggregation and offload data: `struct bnx2x_agg_info`, `enum bnx2x_tpa_mode_t`, TPA/GRO sizing constants, SGE bit-vector macros, TX checksum/GSO `XMIT_*` flags, and ring transition macros such as `NEXT_TX_IDX`, `NEXT_RX_IDX`, and `NEXT_RCQ_IDX`.
- Slow path:
  - `struct bnx2x_slowpath` holds ramrod data buffers, DMAE commands, stats buffers, writeback data, and management firmware message payloads.
  - `struct bnx2x_sp_objs` groups MAC, VLAN, and queue slowpath objects.
  - `enum sp_rtnl_flag` and `enum bnx2x_iov_flag` define deferred service flags.
- Main persistent driver state: `struct bnx2x` contains fastpath arrays, netdev/pci handles, status blocks, slowpath rings, event rings, state flags, link state, multi-function config, CNIC/FCoE/iSCSI hooks, DMAE/statistics state, firmware image/init data, SR-IOV state, DCB/PTP state, VLAN registration, UDP tunnel ports, and firmware capability/version fields.
- Public prototypes export operations implemented across the driver: MAC/VLAN programming, function init, GPIO, DMAE, FLR cleanup, slowpath posting, coalescing, PHY/link helpers, PTP, NVRAM, and VLAN reconfiguration.

## Control Flow
The header does not implement the top-level control flow, but it defines the state machine and invariants used by the control flow:
- Driver lifecycle moves through `BNX2X_STATE_CLOSED`, opening phases, `BNX2X_STATE_OPEN`, closing phases, diagnostic, and error states.
- Queue loops (`for_each_eth_queue`, `for_each_rx_queue`, `for_each_tx_queue`, CNIC variants) encode which fastpath entries participate depending on FCoE/CNIC state and `NO_FCOE_FLAG`.
- Ring macros encode wraparound and next-page descriptor slots for TX, RX BD, RX CQE, and RX SGE rings.
- Chip predicates steer runtime branches for HC versus IGU interrupt blocks, E1x versus E2/E3 status block layouts, RSS/hash ownership, offload mode, and multi-function behavior.

## State and Persistence Behavior
`struct bnx2x` is the long-lived per-device state anchored from `netdev_priv()`. It persists while the PCI device is bound and stores:
- MMIO mappings, doorbell base, DMA-coherent slowpath/status/statistics/ring buffers, and firmware pointers.
- Runtime control state such as `state`, `flags`, `recovery_state`, `sp_state`, `sp_rtnl_state`, queue counts, interrupt mode flags, and link reporting cache.
- Management-firmware shared-memory metadata such as mailbox sequence, pulse sequence, multi-function config, driver capability flags, and OS driver state.
- Offload integrations for CNIC, FCoE, DCB, SR-IOV, PTP, RSS, VXLAN/Geneve, VLAN filters, MAC/VLAN credit pools, and statistics.
Hardware-persistent effects happen through macros that write registers, shared memory, doorbells, and firmware command areas; the header centralizes address calculation but leaves sequencing to implementation files.

## Dependencies and Integration Points
- Includes Linux PCI, netdevice, DMA, PTP, timestamping, and MDIO APIs.
- Includes generated/hardware-specific headers: `bnx2x_hsi.h`, `bnx2x_reg.h`, `bnx2x_fw_defs.h`, `bnx2x_mfw_req.h`, plus link, slowpath, DCB, stats, and VF/PF headers.
- Integrates with `../cnic_if.h` for storage offload clients.
- Provides the shared data contract consumed by `bnx2x_main.c`, `bnx2x_cmn.c`, `bnx2x_link.c`, `bnx2x_sp.c`, `bnx2x_stats.c`, `bnx2x_dcb.c`, `bnx2x_ethtool.c`, SR-IOV files, and self-tests.

## Risks
- The ring geometry macros are tightly coupled to hardware page sizes and descriptor formats. Incorrect counts or next-page handling can corrupt DMA rings.
- `struct bnx2x` is very large and cross-cutting; field changes can silently affect fast path cache locality, lifecycle cleanup, or config-gated builds.
- MMIO and shared-memory macros do no runtime bounds checking. Callers must enforce chip generation, function identity, and mailbox availability.
- Multi-function and storage-only helper predicates feed queue counts, bandwidth limits, link reporting, and feature restrictions; regressions can affect other PFs/VFs on the same device.
- Many state bits are shared between interrupt, NAPI, workqueue, rtnl, management firmware, and recovery paths, so ordering assumptions and locks are critical.

## Test Signals
- Compile coverage across `CONFIG_BNX2X`, `CONFIG_BNX2X_SRIOV`, `CONFIG_DCB`, PTP, and FCoE-related kernel options.
- Probe/open/close cycles on E1x, E2, and E3 devices validate chip predicates, status block layouts, queue counts, and ring geometry.
- RSS, multi-COS, FCoE/CNIC, SR-IOV, VLAN filtering, DCB, PTP, and UDP tunnel feature tests exercise the major state fields.
- Stress tests for MTU changes, feature toggles, reset/recovery, suspend/resume, and TX timeout show whether state transitions and cleanup remain coherent.
