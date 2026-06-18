# subset-b-004361 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_fw_defs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_fw_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_fw_file_hdr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_fw_file_hdr.h

## Purpose
Defines the table-of-contents format at the front of the bnx2x firmware binary. The driver uses this header to locate init operations, init data, storm interrupt tables, storm PRAM images, the `IRO` array, and the firmware version block inside a single requested firmware file.

## Important APIs, Types, and Functions
`struct bnx2x_fw_file_section` contains big-endian `len` and `offset` fields. `struct bnx2x_fw_file_hdr` is an ordered set of these sections: `init_ops`, `init_ops_offsets`, `init_data`, `tsem_int_table_data`, `tsem_pram_data`, `usem_int_table_data`, `usem_pram_data`, `csem_int_table_data`, `csem_pram_data`, `xsem_int_table_data`, `xsem_pram_data`, `iro_arr`, and `fw_version`.

## Control Flow and State
There is no executable logic. Runtime state comes from parsing this fixed layout after firmware load; each section offset becomes a pointer stored in the bnx2x device object and later consumed by init replay, PRAM loading, and offset calculations. The big-endian fields make byte-order conversion mandatory before using lengths or offsets on little-endian hosts.

## Dependencies and Integration Points
Depends on kernel fixed-width endian types such as `__be32`. It integrates with the firmware request/parsing path in `bnx2x_main.c`, with `bnx2x_init_ops.h` through `INIT_OPS(bp)`, `INIT_OPS_OFFSETS(bp)`, `INIT_DATA(bp)`, and `INIT_*_PRAM_DATA(bp)`, and with `bnx2x_fw_defs.h` through the firmware-provided `IRO` section.

## Risks and Test Signals
The structure is an on-disk ABI. Reordering fields, reading without endian conversion, or failing to validate `len`/`offset` bounds can point init code at corrupt data and cause device misprogramming. Test signals include firmware request success, section bounds validation, matching firmware version reporting, successful PRAM decompression/load for all four storms, and init-op replay without invalid opcodes or out-of-range data offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_fw_file_hdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_hsi.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_hsi.h

## Purpose
Defines the bnx2x host-side interface contract shared by the Linux driver, management firmware, and on-chip storm firmware. It covers NVRAM/shared-memory layout, driver-to-MFW mailbox protocol, DCBX/LLDP data, statistics buffers, DMAE commands, doorbells, status blocks, IGU acknowledgments, Ethernet contexts, ramrod payloads, descriptors, CQEs, event rings, congestion-management data, function update data, and per-storm queue/VF zones.

## Important APIs, Types, and Functions
The header is type- and constant-only. Major shared memory types include `struct shared_hw_cfg`, `struct port_hw_cfg`, `struct shared_feat_cfg`, `struct port_feat_cfg`, `struct shm_dev_info`, `struct drv_port_mb`, `struct drv_func_mb`, `struct mf_cfg`, `struct shmem_region`, and `struct shmem2_region`. These define board configuration, PHY/SFP pins, SR-IOV limits, link status, load/unload mailbox commands, driver pulses, DCC/DCBX/AFEX/EEE events, multi-function bandwidth and protocol configuration, FLR acknowledgments, OS driver state, and management debug data.

Firmware and packet-path structures include `struct dmae_command`, `struct doorbell_hdr`, `struct eth_tx_doorbell`, `struct hc_status_block_e1x`, `struct hc_status_block_e2`, `struct hc_sp_status_block`, `struct host_sp_status_block`, `struct igu_ack_register`, `union igu_consprod_reg`, `struct parsing_flags`, `struct eth_context`, `struct client_init_ramrod_data`, `struct client_update_ramrod_data`, `struct eth_classify_rules_ramrod_data`, `struct eth_filter_rules_ramrod_data`, `struct eth_multicast_rules_ramrod_data`, `struct eth_rss_update_ramrod_data`, `struct eth_rx_bd`, `union eth_rx_cqe`, `struct eth_rx_sge`, `struct eth_spe`, `union eth_tx_bd_types`, `struct mac_configuration_cmd`, `struct tpa_update_ramrod_data`, `struct cmng_init`, `struct cmng_init_input`, `struct event_ring_data`, `union event_ring_elem`, `struct function_start_data`, `struct function_update_data`, `struct stats_query_header`, and `struct stats_query_cmd_group`.

Key enums define slow-path command IDs, event opcodes, RSS modes and hash types, connection types, COS modes, traffic types, tunnel types, VLAN modes, CQE types, IGU commands, status-block states, MF modes, and VF/PF channel states. The header also defines many bit masks for mailbox messages, link status, DCBX features, descriptor flags, CQE flags, classification rules, malicious VF errors, and firmware version flags.

## Control Flow and State
There is no direct control flow, but the structures describe several persistent state machines. Shared memory persists across driver/MFW interactions and records board configuration, mailbox requests, mailbox acknowledgments, function status, DCBX negotiation, EEE state, FLR state, and OS driver state. Fast-path state persists in DMA rings, status blocks, event rings, storm contexts, and internal RAM zones. Slow-path control uses ramrods: the driver fills a payload, posts an `eth_spe` or `protocol_common_spe`, firmware acts on it, and completion returns through CQEs or event-ring messages.

The file is heavily endian-aware. Many structs use `__le*` fields for firmware-visible little-endian data and conditional field order under `__BIG_ENDIAN` versus `__LITTLE_ENDIAN` where byte layout matters. This is part of the ABI rather than cosmetic C layout.

## Dependencies and Integration Points
Includes `bnx2x_fw_defs.h` for firmware offset constants and `bnx2x_mfw_req.h` for management firmware request structures. The definitions are consumed across `bnx2x_main.c`, `bnx2x_cmn.c`, `bnx2x_sp.c`, `bnx2x_vfpf.c`, `bnx2x_sriov.c`, link/PHY code, DCBX support, stats collection, ethtool paths, and firmware-loading/init code. The hardware-facing fields integrate with PCI BAR writes, DMA-coherent host buffers, SPQ posting, interrupt coalescing, and management firmware shared-memory reads/writes.

## Risks and Test Signals
This file is the central ABI surface. Risks include layout drift, endian mistakes, incorrect mask/shift values, assuming a field exists on all chip generations, using the wrong HSI version with VFs, mailbox sequence mismatch, writing unsupported DCBX/AFEX/EEE fields for older bootcode, descriptor/CQE size changes, and malicious-VF validation gaps. Test signals include all-endian build coverage, firmware load and version negotiation, link up/down mailbox events, driver pulse acknowledgments, PF/VF load/unload, VF fast-path HSI negotiation, slow-path ramrod completions for setup/update/RSS/filter/multicast/classification, interrupt moderation behavior, stats query correctness, DCBX/EEE negotiation, tunnel offload traffic, TPA/GRO traffic, and SR-IOV error injection for malicious VF events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_hsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_init.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_init.h

## Purpose
Defines initialization opcodes, init phases/modes/blocks, queue-manager helper logic, congestion-management initialization, ILT data structures, SRC entries, and block parity controls for bnx2x hardware bring-up and teardown.

## Important APIs, Types, and Functions
Init replay definitions include opcodes `OP_RD`, `OP_WR`, `OP_SW`, `OP_ZR`, `OP_ZP`, `OP_WR_64`, `OP_WB`, `OP_WB_ZR`, `OP_IF_MODE_OR`, and `OP_IF_MODE_AND`; phase constants `PHASE_COMMON`, `PHASE_PORT*`, `PHASE_PF*`; mode flags such as `MODE_ASIC`, `MODE_E2`, `MODE_E3`, `MODE_PORT4`, `MODE_MF_*`, `MODE_E3_B0`, and endian flags; and block IDs such as `BLOCK_PXP2`, `BLOCK_QM`, `BLOCK_TSEM`, `BLOCK_IGU`, and `BLOCK_MISC_AEU`. `union init_op` overlays the firmware init-op record formats.

Runtime helpers include `bnx2x_map_q_cos()` for queue-to-COS register remapping, `bnx2x_dcb_config_qm()` for mapping Ethernet/FCoE/iSCSI queues according to traffic class policy, and congestion-management builders `bnx2x_init_max()`, `bnx2x_init_min()`, `bnx2x_init_fw_wrr()`, `bnx2x_init_safc()`, and `bnx2x_init_cmng()`.

ILT and SRC types include `struct ilt_line`, `struct ilt_client_info`, `struct bnx2x_ilt`, and `struct src_ent`. Parity support is encoded by `bnx2x_blocks_parity_data`, `mcp_attn_ctl_regs`, and inline helpers `bnx2x_set_mcp_parity()`, `bnx2x_parity_reg_mask()`, `bnx2x_disable_blocks_parity()`, `bnx2x_clear_blocks_parity()`, and `bnx2x_enable_blocks_parity()`.

## Control Flow and State
Queue mapping is read-modify-write: `bnx2x_map_q_cos()` reads the current VOQ/COS mapping, updates per-VNIC queue mappings, clears the old COS bitmap, sets the new COS bitmap, and updates command-queue mapping on non-E3B0 chips. Congestion management computes a `struct cmng_init` shadow image from requested port/VNIC/COS rates; callers must write port and VNIC pieces to separate XSTORM offsets rather than memcpy the whole struct.

ILT state lives in software as allocated DMA pages and in hardware as page-table entries and client boundaries. Parity state lives in hardware mask/status registers plus MCP AEU enable bits. The parity helpers choose masks by chip generation, disable attentions before sensitive flows, clear logged parity status, and re-enable selected parity attentions.

## Dependencies and Integration Points
Depends on `struct bnx2x`, register macros such as `REG_RD` and `REG_WR`, chip predicates like `CHIP_IS_E1()`/`CHIP_IS_E3()`, `INIT_MODE_FLAGS(bp)`, register definitions from `bnx2x_reg.h`, HSI types from `bnx2x_hsi.h`, and utility macros like `BITS_TO_BYTES` and `ARRAY_SIZE`. It is included by main driver initialization code and by `bnx2x_init_ops.h`. Integration points include common/port/function init stages, DCB/PFC setup, CNIC offload setup, QM setup, PXP/ILT/SRC programming, and fatal-attention/parity recovery paths.

## Risks and Test Signals
Risks include firmware init-op layout mismatch, incorrect phase/block index arithmetic, queue/COS bitmaps diverging from VOQ registers, 4-port E3B0 COS offset mistakes, division by unexpected zero rates in congestion calculations, ILT client range errors, chip-generation parity masks hiding real errors or enabling unsupported bits, and parity clear sequences losing diagnostic information. Test signals include full probe/remove cycles on E1/E1H/E2/E3, DCB queue remapping tests, bandwidth/min-rate behavior, CNIC enabled/disabled boots, parity attention injection or debug logging, FLR/reset recovery, and register dumps for QM and XSTORM congestion-management regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_init_ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_init_ops.h

## Purpose
Implements static initialization helpers that are included into `bnx2x_main.c`. It replays firmware init operations, writes large firmware data blocks through the best available path, loads compressed PRAM/int-table blobs, programs the PXP arbiter, allocates and writes ILT entries, initializes QM pointer tables, and seeds the SRC T2 free list.

## Important APIs, Types, and Functions
Firmware replay helpers include `bnx2x_init_str_wr()`, `bnx2x_init_ind_wr()`, `bnx2x_write_big_buf()`, `bnx2x_init_fill()`, `bnx2x_write_big_buf_wb()`, `bnx2x_init_wr_64()`, `bnx2x_sel_blob()`, `bnx2x_init_wr_wb()`, `bnx2x_wr_64()`, `bnx2x_init_wr_zp()`, and the central `bnx2x_init_block()`. These depend on external helpers declared at the top: `bnx2x_gunzip()`, `bnx2x_reg_wr_ind()`, and `bnx2x_write_dmae_phys_len()`.

PXP arbitration is driven by `struct arb_line`, large static tables `read_arb_data`, `write_arb_data`, `read_arb_addr`, `write_arb_addr`, and `bnx2x_init_pxp_arb()`. ILT functions include `bnx2x_ilt_line_mem_op()`, `bnx2x_ilt_client_mem_op()`, `bnx2x_ilt_mem_op_cnic()`, `bnx2x_ilt_mem_op()`, `bnx2x_ilt_line_wr()`, `bnx2x_ilt_line_init_op()`, `bnx2x_ilt_boundry_init_op()`, `bnx2x_ilt_client_init_op_ilt()`, `bnx2x_ilt_client_init_op()`, `bnx2x_ilt_client_id_init_op()`, `bnx2x_ilt_init_op_cnic()`, `bnx2x_ilt_init_op()`, `bnx2x_ilt_init_client_psz()`, and `bnx2x_ilt_init_page_size()`. QM and SRC helpers are `bnx2x_qm_init_cid_count()`, `bnx2x_qm_set_ptr_table()`, `bnx2x_qm_init_ptr_table()`, and `bnx2x_src_init_t2()`.

## Control Flow and State
`bnx2x_init_block()` obtains the start/end op indices for a block and phase from `INIT_OPS_OFFSETS(bp)[BLOCK_OPS_IDX(...)]`, iterates each `union init_op`, decodes `op->raw.op` and `op->raw.offset`, and dispatches reads, writes, string writes, DMAE widebus writes, zero fills, compressed blob writes, 64-bit pattern writes, and conditional skips based on `INIT_MODE_FLAGS(bp)`. `OP_IF_MODE_AND` skips when any required mode flag is missing; `OP_IF_MODE_OR` skips when none of the requested flags are present.

Large writes select between DMAE, indirect writes, and direct string writes based on `bp->dmae_ready`, chip generation, and widebus requirements. `bnx2x_init_wr_zp()` selects the relevant T/C/U/X storm PRAM or interrupt-table blob by address range, gunzips it into `GUNZIP_BUF(bp)`, converts dwords to little-endian, then writes the expanded result. PXP arbitration clamps PCI read/write orders, special-cases FPGA and chip generations, then programs many PXP2 bandwidth/MPS/tag-limit registers.

ILT memory state is allocated per client into DMA pages and mirrored into hardware as 64-bit page addresses with a valid bit. SET/INIT writes page entries and boundaries; CLEAR writes null mappings. QM state is initialized only for sufficiently large CID counts and sets per-queue base and pointer-table registers. SRC state is a host T2 linked list plus hardware first/last/count registers.

## Dependencies and Integration Points
Requires macros normally provided by `bnx2x_main.c`/`bnx2x.h`: `BP_ILT`, `BP_FUNC`, `BP_PORT`, `BNX2X_ILT_ZALLOC`, `BNX2X_ILT_FREE`, `GUNZIP_BUF`, `GUNZIP_PHYS`, `GUNZIP_OUTLEN`, `FW_BUF_SIZE`, `INIT_OPS`, `INIT_OPS_OFFSETS`, `INIT_DATA`, `INIT_*_PRAM_DATA`, `INIT_*_INT_TABLE_DATA`, `CNIC_SUPPORT`, `CONFIGURE_NIC_MODE`, register IO helpers, DMAE helpers, and chip predicates. Main initialization calls these helpers during common, port, function, and CNIC-specific bring-up and cleanup.

## Risks and Test Signals
Risks include init-op section corruption, invalid compressed blob selection, gunzip failure silently leaving firmware memory unwritten, endian conversion mistakes in decompressed dwords, DMAE readiness races, E1 widebus/ZLR workaround regressions, PXP arbitration table mistakes tied to PCI MPS/MRRS, ILT allocation leaks or partial allocation cleanup failures, wrong ILT boundary registers on E1 versus later chips, null ILT pointers under optional CNIC modes, and QM/SRC count off-by-one errors. Test signals include firmware init replay logs, successful common/port/function init on every supported chip generation, PRAM version visibility, DMAE and non-DMAE fallback boots, FPGA boots if supported, CNIC on/off probe cycles, memory allocation failure injection for ILT, PCI MPS/MRRS variation, traffic after RSS/filter/classification setup, and clean remove/reset without stale ILT/SRC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_init_ops.h -->
