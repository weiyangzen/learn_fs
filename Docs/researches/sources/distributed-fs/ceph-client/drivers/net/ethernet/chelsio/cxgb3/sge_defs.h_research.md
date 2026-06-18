# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/sge_defs.h

## Purpose

`sge_defs.h` is an automatically generated register-field helper header for Chelsio T3 SGE context and response descriptor words. It provides shift, mask, value-construction, flag, and getter macros used when programming egress contexts, response queues, free lists, completion queues, and response descriptor control fields. It has no executable code, but it is part of the hardware ABI between `sge.c`, `t3_hw.c`, and the T3 SGE register block.

## Important APIs and Fields

- Egress context macros: `V_EC_CREDITS`, `V_EC_GTS`, `V_EC_INDEX`, `V_EC_SIZE`, `V_EC_BASE_LO`, `V_EC_BASE_HI`, `V_EC_RESPQ`, `V_EC_TYPE`, `V_EC_GEN`, `V_EC_UP_TOKEN`, and `F_EC_VALID` are used by `t3_sge_init_ecntxt()` and `t3_sge_enable_ecntxt()`.
- Response queue context macros: `V_RQ_MSI_VEC`, `F_RQ_INTR_EN`, `V_RQ_GEN`, `V_CQ_SIZE`, `V_CQ_INDEX`, `V_CQ_BASE_HI`, and related `CQ_*` fields define response/completion queue context layout.
- Free-list context macros: `V_FL_BASE_HI`, `V_FL_INDEX_LO`, `V_FL_INDEX_HI`, `V_FL_SIZE`, `V_FL_GEN`, `V_FL_ENTRY_SIZE_LO`, `V_FL_ENTRY_SIZE_HI`, `V_FL_CONG_THRES`, and `F_FL_GTS` configure Rx buffer rings.
- Descriptor generation macros: `F_FLD_GEN1`, `F_FLD_GEN2`, `F_RSPD_GEN1`, and `F_RSPD_GEN2` are central to ring ownership in `sge.c`.
- Response descriptor macros: `G_RSPD_TXQ*_CR`, `F_RSPD_TXQ*_GTS`, `F_RSPD_EOP`, `F_RSPD_SOP`, `F_RSPD_ASYNC_NOTIF`, `F_RSPD_FL0_GTS`, `F_RSPD_FL1_GTS`, `F_RSPD_IMM_DATA_VALID`, `F_RSPD_OFFLOAD`, `G_RSPD_LEN`, and `F_RSPD_FLQ` decode completions and packet location.

## Control Flow and Usage

The macros are expanded at call sites; there is no direct control flow. `t3_hw.c` writes SGE context data registers using these macros before issuing a context command. `sge.c` writes Rx descriptors with free-list generation fields, checks response descriptor generation with `F_RSPD_GEN2`, extracts Tx completion credits from response flags, and tests response flags to decide whether a descriptor carries immediate data, an async notification, an Ethernet/offload packet, or only credits/control information.

## State and Persistence Behavior

The header defines the bit layout of state stored in hardware contexts and descriptors. The state persists in DMA-coherent rings and SGE internal context memory while the adapter is active, but the header itself has no runtime state. Any change to these constants would alter how the driver interprets or programs hardware state and must match the T3 hardware specification exactly.

## Dependencies and Integration Points

`sge_defs.h` is included by `sge.c` and `t3_hw.c`. It complements `regs.h`, which supplies register addresses and broader register fields, and `firmware_exports.h`, which supplies context type and TID ranges. It also interacts indirectly with `adapter.h` queue structures whose fields hold context IDs, queue sizes, and descriptor pointers.

## Risks and Edge Cases

- The file is marked generated; manual edits are likely to be lost and could desynchronize from hardware documentation.
- Shift/mask errors here have broad impact: queue context programming can target the wrong response queue, corrupt base addresses, advertise invalid queue sizes, or make generation-bit checks fail.
- Address fields are split across low/high words. Callers must shift base addresses correctly before applying these macros.
- Response control flag names are close together and easy to confuse; `TXQ1` maps to offload and `TXQ2` maps to control in `sge.c`.

## Test Signals

Because this is a macro ABI header, test signals are integration-level: qset initialization succeeds, SGE context commands do not fail with invalid parameters, Rx/Tx rings make progress, generation bits wrap cleanly, completion credits are decoded correctly, MSI-X vector assignment works, and response descriptor flags result in the expected packet/control paths.
