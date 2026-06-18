## sources/distributed-fs/ceph-client/drivers/dma/dw-edma/dw-hdma-v0-debugfs.h

Purpose: Debugfs interface wrapper for native HDMA v0.

Important APIs/types/functions: declares `dw_hdma_v0_debugfs_on()` when `CONFIG_DEBUG_FS` is enabled and provides an empty stub otherwise.

Control flow: HDMA core invokes this through its debugfs op without surrounding ifdefs.

State and persistence: no state.

Dependencies and integration: includes `linux/dma/edma.h`; connects `dw-hdma-v0-core.c` to optional `dw-hdma-v0-debugfs.c`.

Risks and test signals: build-mode consistency is the main concern. Test `CONFIG_DEBUG_FS=y` and `n` with `CONFIG_DW_EDMA` enabled.
