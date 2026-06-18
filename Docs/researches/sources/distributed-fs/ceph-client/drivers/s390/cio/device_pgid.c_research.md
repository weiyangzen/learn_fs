# sources/distributed-fs/ceph-client/drivers/s390/cio/device_pgid.c

Purpose: performs CCW path verification and path-group management using NOOP, SENSE PGID, SET PGID, DISBAND, and steal-lock channel programs.

Important APIs/types/functions: `ccw_device_verify_start()` starts the verification workflow, while `ccw_device_disband_start()` tears down path groups for offline. Internal flows are split across `verify_start()`, `nop_do()`/`nop_callback()`, `snid_do()`/`snid_callback()`/`snid_done()`, `spid_do()`/`spid_callback()`, `pgid_wipeout_start()`, and `verify_done()`. `ccw_device_stlck()` performs an unconditional reserve/release sequence for forced lock stealing.

Control flow: verification initializes `sch->vpm`, `sch->lpm`, PGID buffers, and path masks. Without path grouping it runs NOOP one path at a time and records paths that work, time out, or reject access. With path grouping it senses PGIDs, analyzes mismatch/reservation/reset state, fills target PGID data, then issues SET PGID establish/resign commands until `pgid_todo_mask` is empty. Unsupported multipath/pathgroup modes cause fallback and restart.

State and persistence behavior: state is in `pgid_valid_mask`, `pgid_todo_mask`, `pgid_reset_mask`, `path_noirq_mask`, `path_notoper_mask`, `flags.pgid_unknown`, `flags.pgroup`, `flags.mpath`, and `sch->vpm/config.mp`. PGID hardware grouping persists until disbanded or reset by hardware; driver state is in memory.

Dependencies and integration points: depends on internal `ccw_request`, `struct pgid` from CSS, CIO config commit, global CSS PGID, FSM callbacks `ccw_device_verify_done()` and `ccw_device_disband_done()`, and CCW commands `NOOP`, `SENSE_PGID`, `SET_PGID`, `STLCK`, and `RELEASE`.

Risks and test signals: path group state can become partially unknown after timeouts, requiring wipeout. Reserved-by-other paths return `-EUSERS`, mismatched PGIDs disable grouping, and multipath configuration must match `sch->config.mp`. Tests should inject per-path timeout/access/unsupported results, all-reserved paths, mismatched PGIDs, reset PGIDs, disband failures, forced lock stealing, and correct `vpm`/`lpm` outcomes.
