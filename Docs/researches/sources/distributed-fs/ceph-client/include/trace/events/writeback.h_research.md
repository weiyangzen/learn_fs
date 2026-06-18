# sources/distributed-fs/ceph-client/include/trace/events/writeback.h

Purpose: Defines extensive writeback tracing for dirty folios/inodes, writeback work scheduling/execution, cgroup writeback ownership, writeback-control state, dirty throttling, superblock requeueing, and single-inode writeback.

Important APIs/types/functions: Provides helper decoders for inode state and writeback reasons, templates such as `writeback_folio_template`, `writeback_dirty_inode_template`, `writeback_write_inode_template`, `writeback_work_class`, `wbc_class`, `writeback_single_inode_template`, and `writeback_inode_template`, and events including `writeback_dirty_folio`, `writeback_mark_inode_dirty`, `inode_switch_wbs*`, `track_foreign_dirty`, `flush_foreign`, `writeback_queue/exec/start/written/wait`, `writeback_pages_written`, `writeback_bdi_register`, `writeback_queue_io`, `global_dirty_state`, `bdi_dirty_ratelimit`, `balance_dirty_pages`, `writeback_sb_inodes_requeue`, and inode writeback/lazytime events.

Control flow: VFS/MM writeback paths emit events as dirty state is created, queued, throttled, written, and cleared. Assignments snapshot inode identifiers, bdi/wb names, cgroup ids, page counts, bandwidth limits, dirty thresholds, and reason flags.

State/persistence: It owns no writeback state; trace buffers persist sampled dirty/writeback state for analysis.

Dependencies/integration: Includes backing-device and writeback headers; cgroup-specific events depend on `CONFIG_CGROUP_WRITEBACK`.

Risks: This trace ABI is heavily used by performance tools. Field changes can break scripts, and high-frequency dirtying paths require minimal overhead.

Test signals: Run filesystem writeback, dirty throttling, and cgroup writeback tests with `writeback:*`; verify work lifecycle and dirty accounting fields.
