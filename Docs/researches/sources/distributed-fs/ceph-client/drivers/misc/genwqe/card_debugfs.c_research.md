# sources/distributed-fs/ceph-client/drivers/misc/genwqe/card_debugfs.c

## Purpose
`card_debugfs.c` exposes GenWQE diagnostic state through debugfs. It dumps current and previous FFDC registers, DDCB queue state, job timers, queue working time, and tunables used during recovery and timeout debugging.

## Important APIs, Types, and Functions
Public lifecycle functions are `genwqe_init_debugfs()` and `genqwe_exit_debugfs()`. Show helpers include `curr_dbg_uidn_show()`, `prev_dbg_uidn_show()`, `curr_regs_show()`, `prev_regs_show()`, `jtimer_show()`, `queue_working_time_show()`, `ddcb_info_show()`, and `info_show()`, wrapped with `DEFINE_SHOW_ATTRIBUTE`.

## Control Flow
Initialization creates a per-card directory, common files (`ddcb_info`, `info`, `err_inject`, `ddcb_software_timeout`, `kill_timeout`), and for privileged PFs adds current/previous register dumps, UID debug buffers, VF job-timeout controls, job timer views, queue working time, and recovery toggles. Current FFDC readers stop traps before reading hardware buffers, then restart traps. Exit removes the card debugfs tree recursively.

## State and Persistence
Debugfs files expose live `struct genwqe_dev` state and MMIO register snapshots. Writable debugfs nodes directly modify in-memory fields such as timeout, error injection, and recovery flags. No settings persist across driver reload.

## Dependencies and Integration Points
The file depends on debugfs, seq_file, FFDC helpers from `card_utils.c`, queue definitions from `card_ddcb.h`, and `genwqe_dev` state from `card_base.h`. It is created from `genwqe_device_create()` and removed during device teardown.

## Risks and Edge Cases
Debugfs has intentionally broad debug access, including writable error injection and timeout knobs. `curr_regs_show()` allocates a register array but does not free it after printing, which is a leak on reads. Hardware reads can be unreliable during reset or PCI error recovery; privileged filtering limits some exposure to PFs.

## Test Signals
Mount debugfs and verify all expected files for PF versus VF, queue dumps with active requests, FFDC reads before/after injected GFIR, and teardown without stale dentries. Memory-leak tooling should cover repeated register-dump reads.
