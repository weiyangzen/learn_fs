# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_int.h

## Purpose
`qed_int.h` declares the interrupt, attention, IGU, CAU, status-block, and doorbell recovery interfaces used across the QED driver.

## Important APIs, Types, and Functions
- IGU PF/VF configuration bit macros define function, MSI/MSI-X, INTx, attention, single-ISR, and parent-PF fields.
- `enum igu_ctrl_cmd` and `struct igu_ctrl_reg` describe IGU command register encoding.
- `enum qed_coalescing_fsm` selects RX or TX CAU PI state machines.
- `struct qed_igu_block` describes one IGU mapping entry with validity/free/PF/default flags.
- `struct qed_igu_info` stores all IGU mapping entries, default SB id, usage counters, and PF/VF change allowance.
- Public APIs cover SB init/setup/release, SP DPC, SB counts, post-ISR-release cleanup, attention clear behavior, SB debug, doorbell recovery, IGU CAM reset/read/init, callback registration, CAU SB config, interrupt allocation/setup/free, interrupt enable/disable, timer resolution, and PGLUE attention handling.

## Control Flow
Device init code reads and optionally resets the IGU CAM, allocates interrupt state, initializes runtime IGU registers, sets up default and attention SBs, then enables interrupts in the selected mode. Protocols register slowpath callbacks and get firmware consumer pointers for their PI. Teardown disables interrupts, releases IRQ state, releases status blocks, and frees interrupt memory.

## State and Persistence
The header defines state shapes for IGU resource accounting and status-block ownership. Implementations mutate `p_hwfn->hw_info.p_igu_info`, `qed_sb_info`, CAU memory, IGU mapping memory, and interrupt flags.

## Dependencies and Integration Points
It includes QED core types and is used by device init, slowpath, protocol offloads, SR-IOV, debug, and storage paths. `qed_iscsi.c` uses `qed_get_igu_sb_id()` for queue SB mapping.

## Risks
- Incorrect use of `QED_SP_SB_ID` with release paths is explicitly rejected for PFs.
- IGU mapping memory size is derived from `NUM_OF_SBS(dev)`, so device-specific constants must match hardware.
- Timer resolution changes require initialized hardware and PF context.

## Test Signals
Compile coverage across PF/VF builds, successful SB allocation/release, callback registration and DPC dispatch, correct SB counts, and valid CAU/IGU debug reads are the main signals.
