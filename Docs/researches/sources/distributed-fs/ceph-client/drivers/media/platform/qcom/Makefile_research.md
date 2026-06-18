# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Makefile

## sources/distributed-fs/ceph-client/drivers/media/platform/qcom/Makefile

Purpose: Top-level Qualcomm media platform build file that recurses into the CAMSS, Iris, and Venus driver directories.

Important APIs/types/functions: Uses `obj-y += camss/`, `iris/`, and `venus/` so child Makefiles control object selection based on Kconfig symbols.

Control flow/state: No runtime state. Build inclusion is unconditional at directory traversal level; actual module/built-in choices are made in child Makefiles.

Dependencies/integration: Consumed by Kbuild from `drivers/media/platform`. Must stay synchronized with the sibling Kconfig source entries.

Risks/test signals: Missing entries prevent entire driver families from building even when Kconfig enables them. Test with allmodconfig or targeted `CONFIG_VIDEO_QCOM_CAMSS=m` builds.
