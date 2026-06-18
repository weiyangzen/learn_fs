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
