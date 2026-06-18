## sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_fw_counters.h

Purpose: Declares the public debugfs lifecycle hooks for firmware counter reporting.

Important APIs/types: Forward-declares `struct adf_accel_dev` and exports `adf_fw_counters_dbgfs_add()` and `adf_fw_counters_dbgfs_rm()`. No data structures are exposed, keeping counter storage private to the implementation.

Control flow/state: This header does not own state. Consumers call add during debugfs/device setup and rm during teardown.

Dependencies/integration: Integrated by QAT common driver code that manages per-device debugfs files. It deliberately avoids including heavy QAT headers.

Risks and test signals: Build coverage should verify callers include this header when debugfs counters are enabled and that add/remove calls are balanced in device probe/remove or start/stop paths.
