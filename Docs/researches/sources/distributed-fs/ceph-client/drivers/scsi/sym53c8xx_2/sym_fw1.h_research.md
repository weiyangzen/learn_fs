<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw1.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw1.h

## Purpose
`sym_fw1.h` is the generic Symbios SCRIPTS firmware template used for older/non-load-store chips when `SYM_CONF_GENERIC_SUPPORT` is enabled. It defines the layout and initializer contents for script area A, script area B, and initialization script Z, encoding SCSI selection, command dispatch, data movement, message handling, reselection, completion, abort, negotiation, and snoop-test behavior.

## Important APIs, Types, And Functions
The main types are `struct SYM_FWA_SCR`, `struct SYM_FWB_SCR`, and `struct SYM_FWZ_SCR`. They are not normal callable APIs; their array fields are named script labels consumed by `sym_fw.h` and `sym_fw.c`. Script A contains hot-path labels such as `start`, `getjob_begin`, `select`, `wf_sel_done`, `send_ident`, `command`, `dispatch`, `init`, `clrack`, `datai_done`, `datao_done`, `msg_in`, `status`, `complete`, `done`, `save_dp`, `restore_dp`, `disconnect`, `idle`, `ungetjob`, `reselect`, `reselected`, `resel_tag`, `resel_dsa`, `resel_no_tag`, `data_in`, `data_out`, `pm0_data`, and `pm1_data`. Script B contains out-of-line paths such as `no_data`, `sel_for_abort`, `msg_bad`, `msg_weird`, `wdtr_resp`, `send_wdtr`, `sdtr_resp`, `send_sdtr`, `ppr_resp`, `send_ppr`, `data_ovrun`, `abort_resel`, `resel_bad_lun`, `bad_i_t_l`, `bad_i_t_l_q`, and data slots like `done_pos`, `startpos`, and `targtbl`. Script Z provides `snooptest` and `snoopend`.

## Control Flow
The SCRIPTS processor starts at `start`, checks whether the host requested manual recovery, reads the next job from the start queue, loads DSA, selects the target with ATN, sends identify/tag/negotiation messages, sends the command, and dispatches by SCSI phase. Data phases jump through generated SG move tables; status and command-complete message paths save status, copy the CCB header back, flush posted writes with dummy reads, enqueue the DSA in the done queue, and raise `SCR_INT_FLY`. Disconnect paths save host status and return to the scheduler. Reselection waits in `reselect`, decodes target/LUN/tag, reloads transfer registers and CCB headers, and jumps back to the saved restart point. Script B handles extended/messages, negotiation replies, overrun byte counting, abort/reset message sending, bad status, bad reselections, and WSR residual-byte handling. Script Z performs a read/write/read memory snoop test then interrupts.

## State And Persistence Behavior
The template contains static script opcodes and `SCR_DATA_ZERO` placeholders. Runtime setup fills `data_in`/`data_out`, zeroes data placeholders, patches queue/target addresses, and relocates `HADDR`, `RADDR`, and `PADDR` operands into per-adapter bus/MMIO addresses. It persists no state beyond the controller-executed script copy in DMA memory.

## Dependencies And Integration Points
It depends on script opcode macros from `sym_defs.h`, relocation macros from `sym_fw.h`, host data structures such as `struct sym_hcb`, `struct sym_ccb`, `struct sym_dsb`, `struct sym_ccbh`, `struct sym_tcbh`, and `struct sym_lcbh`, and interrupt/status constants handled by the C driver (`SIR_*`, `HS_*`, `HF_*`, `SS_REG`, `HS_REG`, `HF_REG`). It is included by `sym_fw.c` under macro-renamed symbol names.

## Risks
This is high-risk firmware data: array lengths in the structs must match initializer instruction counts, self-modifying script slots must remain aligned with comments and offset tables, and host C structures must keep the offsets assumed by `offsetof()` operands. Bugs can lose completions, corrupt queues, mishandle reselection tags, hang the SCSI bus, or misreport residuals. Conditional blocks for IARB and target-role support change lengths and must stay synchronized.

## Test Signals
Test compile-time structure initializers, firmware offset generation, script relocation, generic firmware selection on non-`FE_LDSTR` chips, normal command completion, disconnect/reselect with tagged and untagged commands, SAVE/RESTORE DATA POINTER, wide residual handling, data overrun/underrun, negotiation messages (WDTR/SDTR/PPR), abort/reset recovery, bad LUN/tag reselection, snoop test interrupt, and completion queue integrity under heavy tagged I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw1.h -->
