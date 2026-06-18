# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.h

Purpose: declares the heartbeat debugfs add/remove interface.

Important API: `adf_heartbeat_dbgfs_add(struct adf_accel_dev *accel_dev)` and `adf_heartbeat_dbgfs_rm(struct adf_accel_dev *accel_dev)`.

Control flow and state: no behavior or state in the header. It establishes the integration contract between generic debugfs setup and heartbeat diagnostics.

Dependencies and integration: forward-declares `struct adf_accel_dev`; implemented by `adf_heartbeat_dbgfs.c`. Called from broader QAT debugfs lifecycle when a device starts/stops.

Risks and test signals: build or link catches signature drift. Runtime test should confirm heartbeat debugfs directory appears only when heartbeat state exists and is removed without stale dentries during shutdown/restart.
