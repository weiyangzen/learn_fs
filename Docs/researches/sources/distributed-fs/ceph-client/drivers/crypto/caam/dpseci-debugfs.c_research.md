<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.c

Purpose: adds debugfs visibility for DPAA2 DPSECI frame queues by reporting pending frame and byte counts for each Rx and Tx virtual FQID.

Important APIs and control flow: `dpseci_dbg_fqs_show()` prints a heading for the DPSECI device, iterates `priv->num_pairs`, queries each Rx queue FQID and Tx queue FQID with `dpaa2_io_query_fq_count()`, and emits pending frame/byte counts. `DEFINE_SHOW_ATTRIBUTE()` creates file operations. `dpaa2_dpseci_debugfs_init()` creates a debugfs directory named after the device and adds `fq_stats`; `dpaa2_dpseci_debugfs_exit()` recursively removes it.

State and persistence behavior: stores the debugfs root in `dpaa2_caam_priv->dfs_root`; all displayed counts are live DPAA2 IO queries, not cached state.

Dependencies and integration points: depends on DPAA2 CAAM private data from `caamalg_qi2.h`, `dpaa2_io_query_fq_count()`, debugfs, and seq_file. It complements the DPSECI Management Complex API in `dpseci.c`.

Risks and test signals: query failures are silently skipped, output can be stale immediately after printing, and access depends on debugfs lifetime matching DPSECI object removal. Test signals include `fq_stats` listing all queue pairs, nonzero pending counts during load, graceful behavior when queries fail, and clean removal without dangling debugfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.c -->
