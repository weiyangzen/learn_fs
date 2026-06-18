# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_telemetry.h

Purpose: defines generic QAT telemetry hardware metadata, runtime telemetry state, constants, and lifecycle APIs.

Important types: `struct adf_tl_hw_data` describes layout sizes, counter arrays, conversion factors, counts, maximums, and command-queue multipliers. `struct adf_telemetry` stores device pointer, state, selected history depth, current history index, message count, DMA memory, history buffers, selected RP indexes, locks, delayed work, slice counts, and cmdq counts.

Control flow and state: state is per device at `accel_dev->telemetry`. `atomic_t state` doubles as enabled flag and requested aggregation window. `regs_hist_lock` protects history snapshots/readers; `wr_lock` serializes debugfs control writes.

Dependencies and integration: includes firmware admin slice-count struct and debugfs counter declarations. Functions become no-ops without `CONFIG_DEBUG_FS`.

Risks and test signals: no-op fallback means telemetry exists only in debugfs builds. Test build configurations, state transitions, lock ordering with debugfs, and proper freeing of DMA/history buffers.
