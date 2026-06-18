# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/firmware_exports.h

## Purpose

`firmware_exports.h` defines the firmware-facing constants used by the T3 driver and offload clients: work-request opcodes, management opcodes, maximum WR size/count, firmware queue/context ranges, reserved TID/token starts, and firmware version bitfield helpers. It is a shared hardware/firmware ABI description, not an implementation file.

## Important APIs, types, and functions

- Work-request opcodes: `FW_WROPCODE_FORWARD`, `FW_WROPCODE_BYPASS`, tunnel TX/RX, ULPTX data/memory/packet/invalidate, offload close/abort/TX data/ACK/get-TCB, RDMA operations, management, and SGE egress context read.
- Management opcode: `FW_MNGTOPCODE_PKTSCHED_SET`, used by `cxgb3_main.c` packet scheduler binding.
- WR sizing: `FW_WR_SIZE`, `FW_T3_WR_NUM`, `FW_N3_WR_NUM`, and selected `FW_WR_NUM`.
- Firmware context ranges: `FW_TUNNEL_NUM`, `FW_TUNNEL_SGEEC_START`, `FW_TUNNEL_TID_START`, `FW_CTRL_NUM`, `FW_CTRL_SGEEC_START`, `FW_CTRL_TID_START`, `FW_OFLD_NUM`, `FW_OFLD_SGEEC_START`, `FW_RI_NUM`, `FW_RI_SGEEC_START`, `FW_RI_TID_START`, `FW_RX_PKT_NUM`, `FW_RX_PKT_TID_START`, and `FW_WRC_NUM`.
- Version fields: `S_`, `M_`, `V_`, and `G_` macros for firmware type, major, minor, and micro components.

## Control flow

This header has no runtime control flow. Its constants are consumed when other files construct firmware work requests. For example, `cxgb3_main.c` uses `FW_WROPCODE_FORWARD` for SMT/L2T/RTE/TCB management CPLs and `FW_WROPCODE_MNGT` plus `FW_MNGTOPCODE_PKTSCHED_SET` for scheduler commands; `cxgb3_offload.c` uses offload abort and RDMA context constants; `l2t.c` uses `FW_WROPCODE_FORWARD` for L2 table writes.

## State and persistence behavior

The header defines static ABI values only. Those values become hardware/firmware state when written into SGE contexts, work-request headers, or version parsing logic. No mutable or persistent software state is declared here.

## Dependencies and integration points

It is included by `cxgb3_main.c`, `cxgb3_offload.c`, and `l2t.c`. It also aligns with firmware binaries requested by `cxgb3_main.c` and with CPL/work-request structures in `t3_cpl.h`. The queue and TID constants must match firmware expectations exactly because hardware completions and offload clients depend on these numeric ranges.

## Risks and edge cases

- Several macro names contain historical spelling mistakes such as `FW_WROPOCDE_ULPTX_DATA_SGL` and `FW_WROPOCDE_RSVD`; code must use the existing spellings or compatibility aliases would be needed.
- Changing any opcode or context start value is firmware ABI-breaking and can misroute completions or corrupt hardware context state.
- `FW_WR_NUM` varies under `N3`; builds must verify the intended firmware target.
- Version extraction macros assume packed 32-bit version fields with fixed bit widths; mismatched firmware encoding would produce misleading ethtool driver info and upgrade checks.

## Test signals

Validation is primarily integration-based: compile all users, inspect generated work requests for correct opcodes, run firmware version reporting through ethtool, verify packet scheduler management requests, RDMA control QP setup using `FW_RI_*`, and confirm offload queue/TID ranges match observed firmware behavior on T3/N3 variants.
