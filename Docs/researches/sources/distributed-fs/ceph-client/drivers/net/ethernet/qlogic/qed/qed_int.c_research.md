# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.c

## Purpose
`qed_int.c` implements QED interrupt and attention handling. It manages slowpath status blocks, attention status blocks, IGU CAM discovery/reset, CAU status-block configuration and coalescing, slowpath callback dispatch, hardware attention decoding, doorbell overflow recovery, interrupt enable/disable, and status-block debug reads.

## Important APIs, Types, and Functions
- `struct qed_pi_info` stores one slowpath producer-index callback and cookie.
- `struct qed_sb_sp_info` combines a slowpath status block with callback slots.
- `struct aeu_invert_reg_bit` and `aeu_descs` describe AEU attention bits, parity status, callbacks, and debug block ids.
- Specific attention callbacks include MCP CPU, PSWHST incorrect access, GRC timeout, PGLUE RBC, firmware assertion, and DORQ.
- `qed_int_sp_dpc()` is the tasklet for default slowpath SB interrupts and attentions.
- `qed_int_sb_init()`, `qed_int_sb_setup()`, and `qed_int_sb_release()` manage client status blocks.
- `qed_int_register_cb()` and `qed_int_unregister_cb()` manage slowpath callback slots.
- `qed_int_igu_read_cam()` and `qed_int_igu_reset_cam()` discover and reprogram IGU mapping memory.
- `qed_int_igu_enable()`, `qed_int_igu_enable_int()`, and `qed_int_igu_disable_int()` control interrupt generation.
- `qed_int_cau_conf_sb()`, `qed_init_cau_sb_entry()`, and `qed_int_set_timer_res()` configure CAU memory and coalescing.
- `qed_db_rec_handler()` and DORQ helpers recover from PF doorbell overflow/drop conditions.

## Control Flow
During allocation, the driver allocates the slowpath SB and attention SB as coherent memory, initializes IGU addresses, computes parity masks, and sets up the tasklet. Setup zeros SBs, programs CAU/attention SB addresses, and prepares the DPC. Enabling interrupts first enables AEU-to-IGU attentions, requests the slowpath IRQ when appropriate, then programs PF interrupt mode bits for INTA/MSI/MSI-X/POLL.

When the slowpath tasklet runs, it disables default SB interrupts, updates the SB index and attention index, checks for a valid DPC PTT, handles attention changes, dispatches registered producer-index callbacks, acknowledges attentions, and re-enables interrupts. Attention assertion masks sources in IGU, records known bits, handles MCP events, and writes IGU attention-set commands. Deassertion reads all AEU-after-invert registers, handles parity first, then walks enabled non-parity causes per attention group, calls callbacks, prints block debug attention data, escalates fatal errors through `qed_hw_err_notify()`, clears IGU deassertion, unmasks benign sources, and clears known state.

Doorbell overflow recovery flushes incomplete EDPM transactions when needed, clears sticky overflow, and replays registered doorbells through the DB recovery mechanism.

## State and Persistence
Driver state includes `p_hwfn->p_sp_sb`, `p_hwfn->p_sb_attn`, `p_hwfn->sp_dpc`, `b_int_requested`, `b_int_enabled`, IGU block usage counters, callback slots, attention parity masks, known attention bits, and doorbell recovery flags. Hardware state includes IGU PF configuration, attention masks/latches, IGU mapping memory, cleanup status, CAU SB/PI memory, AEU enable registers, DORQ sticky/drop registers, and status-block producer/consumer memory.

## Dependencies and Integration Points
The file depends on Linux tasklets, DMA coherent memory, QED hardware access, runtime init storage, management firmware event handling, slowpath IRQ allocation, SR-IOV/VF helpers, debug attention parsing, and doorbell recovery. It integrates with protocol modules through `qed_int_register_cb()`, with device init through IGU CAM and CAU runtime setup, and with error recovery through hardware error notifications.

## Risks
- Attention descriptor tables must match hardware bit layout; incorrect lengths or flags misdecode parity/interrupt causes.
- Some attention callbacks return fatal status and permanently mask future attentions for that source.
- Slowpath callback registration scans without an explicit lock in this file; callers must sequence registration against DPC execution.
- IGU CAM reset depends on MFW resource counts and SR-IOV VF counts matching available mapping entries.
- Doorbell recovery must flush partial EDPM correctly before replay; failure leaves overflow recovery returning `-EBUSY`.
- `qed_int_alloc()` does not free the slowpath SB if attention SB allocation fails, so caller cleanup must handle partial allocation.

## Test Signals
Signals include successful IGU CAM read/reset logs, correct number of PF/VF SBs, tasklet dispatch of SPQ/protocol callbacks, clean attention ack progression, absence of repeated parity/fatal attention storms, successful doorbell recovery after overflow injection, configurable interrupt coalescing reflected in CAU memory, and valid output from `qed_int_get_sb_dbg()`.
