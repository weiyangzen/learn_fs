<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.h

Purpose: declares DPAA2 DPSECI debugfs helpers and provides stubs when debugfs is disabled.

Important APIs and control flow: exposes `dpaa2_dpseci_debugfs_init()` and `dpaa2_dpseci_debugfs_exit()` for `struct dpaa2_caam_priv`; fallback inline functions no-op under non-debugfs builds.

State and persistence behavior: none in the header. It fixes the conditional interface for DPSECI debugfs lifecycle.

Dependencies and integration points: includes `caamalg_qi2.h` for `dpaa2_caam_priv` and `linux/dcache.h` for debugfs dentry types. Used by DPAA2 CAAM code that owns DPSECI devices.

Risks and test signals: risks are coupling a debugfs header to a large DPAA2 CAAM private header and signature mismatch between stubs and implementation. Test signals are clean builds with debugfs enabled/disabled and correct init/exit pairing during DPSECI probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.h -->
