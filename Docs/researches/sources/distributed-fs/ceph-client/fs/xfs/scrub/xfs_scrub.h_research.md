<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfs_scrub.h -->
## sources/distributed-fs/ceph-client/fs/xfs/scrub/xfs_scrub.h

Purpose: Provides the top-level ioctl entry declarations for XFS online metadata scrub, with stubs when scrub support is disabled.

Important APIs: When `CONFIG_XFS_ONLINE_SCRUB` is enabled, declares `xfs_ioc_scrub_metadata(struct file *, void __user *)` and `xfs_ioc_scrubv_metadata(struct file *, void __user *)`. When disabled, both names are preprocessor stubs returning `-ENOTTY`.

Control flow and integration: This is included by ioctl-facing XFS code so callers can invoke scrub operations without scattering configuration checks. It controls whether scrub ioctls are live or report unsupported operation.

State and persistence: No state is stored here; persistence behavior is entirely in the enabled scrub implementation elsewhere.

Dependencies: Depends on kernel `struct file`, user pointer annotation, and the XFS Kconfig option.

Risks: The macro stubs must match function signatures closely enough for callers. Tests must cover disabled builds because no runtime symbol exists in that configuration.

Test signals: Compile matrix with `CONFIG_XFS_ONLINE_SCRUB=y/n`; ioctl tests should expect `ENOTTY` when disabled and dispatch into scrub when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfs_scrub.h -->
