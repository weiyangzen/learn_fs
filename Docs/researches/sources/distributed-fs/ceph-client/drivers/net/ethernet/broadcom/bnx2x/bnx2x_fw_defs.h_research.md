# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_fw_defs.h

## Purpose
Defines firmware-derived offsets and sizing constants for the Broadcom/QLogic bnx2x Everest firmware interface. The first half maps logical driver concepts to storm internal RAM offsets through the firmware-provided `IRO[]` table. The second half records Ethernet HSI limits and fixed firmware constants used by queue setup, status blocks, RSS, multicast filtering, slow path commands, congestion management, and storage offloads.

## Important APIs, Types, and Functions
This header has no functions or types. Its main API is macro families such as `CSTORM_*_OFFSET`, `TSTORM_*_OFFSET`, `USTORM_*_OFFSET`, and `XSTORM_*_OFFSET`, each computing an internal RAM address from `IRO[n].base`, `IRO[n].m1`, `IRO[n].m2`, `IRO[n].m3`, and sometimes `IRO[n].size`. Important consumers use offsets for storm assert lists, function enable bytes, VF-to-PF state, event-ring producer/data, slow-path status blocks, regular status blocks, sync blocks, SPQ producer/page base/data, RX producer zones, TPA data, multicast/RSS configuration, iSCSI/FCoE parameters, and congestion-management state.

The fixed constants define ring geometry and firmware limits: `ETH_FP_HSI_VERSION`, `X_ETH_LOCAL_RING_SIZE`, `NUM_OF_ETH_BDS_IN_PAGE`, `U_ETH_MAX_SGES_FOR_PACKET`, `U_ETH_BDS_PER_PAGE`, `U_ETH_CQE_PER_PAGE_MASK`, `T_ETH_INDIRECTION_TABLE_SIZE`, `T_ETH_RSS_KEY`, `ETH_MAX_RX_CLIENTS_*`, `MAX_STAT_COUNTER_ID_*`, MAC/VLAN credit limits, aggregation queue counts, multicast bin/engine counts, minimum CQE counts with and without TPA, `MC_PAGE_SIZE`, `HC_*` status-block sizing, `MAX_RAMRODS_PER_PORT`, timer resolutions, flow-control dimensions, `C_ERES_PER_PAGE`, `AFEX_LIST_TABLE_SIZE`, and FCoE task limits.

## Control Flow and State
There is no runtime control flow. The state model is declarative and firmware-version-sensitive: macros compute addresses into microcontroller memory using `IRO[]`, which is loaded from the firmware file. Callers then use BAR-relative register or memory writes to program the persistent firmware state for PFs, VFs, status blocks, event rings, offload queues, and storm-global variables.

## Dependencies and Integration Points
Depends on the generated `IRO` metadata and on struct sizes exposed by `bnx2x_hsi.h` through `STRUCT_SIZE(...)` and `PAGE_SIZE` calculations. It is included by `bnx2x_hsi.h` and indirectly by most driver code. Integration points include `bnx2x_main.c` setup/cleanup, `bnx2x_cmn.c` fast-path status-block setup, `bnx2x_sp.c` filter/RSS/classification programming, SR-IOV VF/PF channel code, and debug paths that read storm assert lists.

## Risks and Test Signals
The macros are firmware ABI. A stale `IRO` index, wrong multiplier, or wrong constant can write valid-looking data into the wrong storm memory location. Risk is highest around chip-generation differences, E1/E1H/E2/E3 sizing, PF/VF index arithmetic, and constants tied to descriptor size. Test signals include firmware load/version compatibility, successful function start/stop, SR-IOV VF setup, RSS indirection behavior, multicast filter programming, status-block interrupt delivery, event-ring completions, TPA/GRO traffic, and driver debug dumps showing sane storm assert/status structures.
