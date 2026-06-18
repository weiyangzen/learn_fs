# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/debugfs.c

## Purpose
This file implements shared debugfs and diagnostics support for HiSilicon accelerator queue-manager (`hisi_qm`) devices. It exposes queue-manager registers, live status, device usage, command-driven queue/context dumps, per-device counters, and register-difference snapshots used by accelerator-specific drivers such as HPRE.

## Important APIs, Types, and Functions
The exported functions are `hisi_qm_regs_dump()`, `hisi_qm_regs_debugfs_init()`, `hisi_qm_regs_debugfs_uninit()`, `hisi_qm_acc_diff_regs_dump()`, `hisi_qm_show_last_dfx_regs()`, `hisi_qm_debug_init()`, and `hisi_qm_debug_regs_clear()`. Internal debugfs file operations include `qm_cmd_fops`, `qm_debug_fops`, `qm_regs_fops`, `qm_usage_fops`, `qm_diff_regs_fops`, `qm_state_fops`, and `qm_status_fops`.

Command dump support is table-driven through `struct qm_cmd_dump_item`, with commands for `sqc`, `cqc`, `eqc`, `aeqc`, `sq`, `cq`, `eq`, and `aeq`. Register-difference support uses `struct dfx_diff_registers` arrays, initialized by `dfx_regs_init()` and freed by `dfx_regs_uninit()`.

## Control Flow
`hisi_qm_debug_init()` creates the `qm` debugfs directory under an accelerator-provided root, adds PF-only state/current selector files, adds `regs`, `cmd`, `status`, device state/timeout controls, atomic counter files, optional `diff_regs`, optional `dev_usage`, and optional algorithm QoS debugfs. Reads of register files call `hisi_qm_regs_dump()` under `hisi_qm_get_dfx_access()` to avoid racing reset/suspend. Writes to selector files parse small numeric buffers and update current PF/VF or queue selection registers under per-file locks.

The command write path copies at most `QM_DBG_WRITE_LEN` bytes from userspace, strips a trailing newline, takes DFX access, rejects work while QM is stopped, parses the first token, and dispatches to dump functions. SQC/CQC dumps prefer mailbox hardware context reads and fall back to software cached contexts under `qps_lock`. SQ/CQ/EQ/AEQ dumps read queue memory directly after validating queue and element IDs. Sensitive DMA address fields are masked before printing SQC/CQC/SQE data.

Register snapshot initialization captures baseline QM and accelerator register regions for later diff output. Last-register support snapshots selected QM registers and can print changes during reset/error handling.

## State and Persistence Behavior
There is no disk persistence. Runtime state is stored in `qm->debug`, including debugfs dentries, current selected queue/function count, `qm_diff_regs`, `acc_diff_regs`, and `qm_last_words`. Atomic counters in `struct qm_dfx` are exposed through debugfs and can be reset by writing zero. Hardware state is affected by writes to current selector registers and read-clear enable registers.

## Dependencies and Integration Points
This file depends on the shared queue-manager definitions in `<linux/hisi_acc_qm.h>` and `qm_common.h`, Linux debugfs, seq_file, mailbox helpers such as `qm_set_and_get_xqc()`, reset/suspend gating through `hisi_qm_get_dfx_access()`, and accelerator-specific register ranges supplied to `hisi_qm_regs_debugfs_init()`. HPRE calls these exports for common register dumps and diff snapshots.

## Risks and Edge Cases
Debugfs write paths are privileged by permissions but still user-triggered; bounds and token validation are therefore important. Some dump paths read queue memory after validating against current `qm->qp_num` and queue depths, but queue lifetime depends on `qps_lock` coverage and DFX access. `qm_status_read()` indexes `qm_s[]` using `atomic_read(&qm->status.flags)` and assumes only expected status values. Register-difference baselines can become stale across reset unless refreshed by the accelerator lifecycle. Read-clear controls can alter hardware counters and should not be treated as passive observation.

## Test Signals
Test debugfs creation for PF and VF devices, command parser handling of valid commands, extra tokens, oversized writes, invalid queue IDs, and newline-terminated writes. Exercise reset/suspend paths where `hisi_qm_get_dfx_access()` returns errors or `-EAGAIN`. Validate that SQC/CQC/SQE dumps mask address fields, diff registers report only changed values, read-clear counter reset works, and `hisi_qm_debug_regs_clear()` clears current selectors and read-clear counters.
