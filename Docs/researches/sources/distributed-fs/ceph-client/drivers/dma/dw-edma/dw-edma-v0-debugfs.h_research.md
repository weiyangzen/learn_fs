## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-edma-v0-debugfs.h

Purpose: Debugfs interface wrapper for eDMA v0.

Important APIs/types/functions: declares `dw_edma_v0_debugfs_on()` under `CONFIG_DEBUG_FS` and provides an empty inline stub otherwise.

Control flow: register back end calls this unconditionally through its debugfs op; the header makes that call compile away when debugfs is disabled.

State and persistence: no state in the header.

Dependencies and integration: includes `linux/dma/edma.h`; consumed by `dw-edma-v0-core.c` and implemented by `dw-edma-v0-debugfs.c`.

Risks and test signals: main risk is build consistency across debugfs-enabled and disabled configs. Test both build modes and verify no missing symbol when `CONFIG_DEBUG_FS=n`.
