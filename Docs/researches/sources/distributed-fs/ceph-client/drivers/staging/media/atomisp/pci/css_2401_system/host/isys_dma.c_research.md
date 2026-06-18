# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma.c

Purpose: provides CSS 2401 ISYS DMA capability data and a helper to configure maximum burst size.

Important APIs/types/functions: `N_ISYS2401_DMA_CHANNEL_PROCS` exposes the channel count per DMA ID. `isys2401_dma_set_max_burst_size()` writes the DDR connection max burst register with `max_burst_size - 1`.

Control flow: the setter asserts a valid DMA ID and burst size in 1..255, then stores to the DMA device-info register for the DDR connection.

State and persistence: writes persist in the ISYS DMA hardware register until reset/reconfiguration. The channel-count array is read-only module state.

Dependencies and integration: depends on `system_local.h`, `isys_dma_global.h`, `isys_dma_private.h`, DMA register macros, and device access.

Risks and test signals: burst size validation is assertion-only, so production behavior depends on assertion configuration. Tests should verify register index calculation, boundary burst values, and DMA ID bounds.
