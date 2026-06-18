<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.h

Purpose: compile-time gate for firmware-runtime debugfs registration.

Important APIs/types: declares `iwl_fwrt_dbgfs_register(struct iwl_fw_runtime *fwrt, struct dentry *dbgfs_dir)` when `CONFIG_IWLWIFI_DEBUGFS` is enabled and provides an empty inline stub otherwise.

Control flow: callers can unconditionally call `iwl_fwrt_dbgfs_register()` from runtime initialization. The preprocessor selects either real registration in `debugfs.c` or a no-op, avoiding runtime branches in non-debugfs builds.

State and persistence: the real implementation initializes timestamp delayed work and creates debugfs entries; the stub mutates nothing.

Dependencies/integration: includes `runtime.h` for `struct iwl_fw_runtime` and integrates with `init.c`. It is a small but important build-configuration boundary.

Risks/test signals: primary risk is build skew between debugfs and non-debugfs configurations. Test with `CONFIG_IWLWIFI_DEBUGFS=y` and unset, ensuring runtime initialization links in both cases and no debugfs-only symbols leak into the stub build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/debugfs.h -->
