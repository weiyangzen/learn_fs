<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.h

Purpose: declares debugfs integration points for controller and QI code while compiling to no-op stubs when debugfs or QI support is disabled.

Important APIs and control flow: exposes `caam_debugfs_init()`, `caam_debugfs_qi_congested()`, and `caam_debugfs_qi_init()` under the matching Kconfig conditions. The fallback inline functions accept the same arguments and do nothing.

State and persistence behavior: none in the header; it defines the conditional interface boundary.

Dependencies and integration points: forward-declares `struct dentry`, `struct caam_drv_private`, and `struct caam_perfmon`. Included by `ctrl.c` and `qi.c` so those files can call debugfs hooks without preprocessor clutter.

Risks and test signals: risks are signature drift between real and stub variants and missing coverage in non-debugfs builds. Test signals are clean builds with `CONFIG_DEBUG_FS` and `CONFIG_CRYPTO_DEV_FSL_CAAM_CRYPTO_API_QI` in all enabled/disabled combinations and no runtime dependency on debugfs availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.h -->
