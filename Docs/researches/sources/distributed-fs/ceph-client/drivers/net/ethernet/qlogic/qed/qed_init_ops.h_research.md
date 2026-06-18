# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_init_ops.h

## Purpose
`qed_init_ops.h` declares the firmware init interpreter and runtime register staging interface used during QED hardware bring-up.

## Important APIs, Types, and Functions
- `qed_init_iro_array()` installs the generated IRO array pointer in `struct qed_dev`.
- `qed_init_run()` runs a selected firmware init phase and mode set through a PTT.
- `qed_init_alloc()` and `qed_init_free()` manage `struct qed_rt_data` arrays.
- `qed_init_store_rt_reg()` and `qed_init_store_rt_agg()` stage scalar and aggregate runtime values.
- `STORE_RT_REG`, `OVERWRITE_RT_REG`, and `STORE_RT_REG_AGG` are the convenience macros used by other modules.
- `qed_gtt_init()` initializes PXP/GTT global windows.

## Control Flow
Callers allocate runtime arrays, store runtime values with the macros, run firmware init phases, and free runtime arrays during teardown. Aggregates are passed by address and stored as u32 words.

## State and Persistence
The declarations affect `p_hwfn->rt_data` and hardware GTT/init state through implementations in `qed_init_ops.c`. The header itself has no state.

## Dependencies and Integration Points
It includes QED core types and is included by firmware helper, interrupt, device, and context code that must stage runtime register values before init-script execution.

## Risks
- `STORE_RT_REG_AGG` casts aggregate storage to `u32 *`; callers must pass naturally sized firmware/register structs with correct endianness.
- `OVERWRITE_RT_REG` is identical to `STORE_RT_REG`, so there is no separate overwrite policy beyond replacing the staged value.

## Test Signals
Compile-time users should match the expected signatures. Runtime signals are successful device init and correct staged values flushed by `qed_init_run()`.
