# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx.h

Purpose: top-level public internal header for the aic94xx driver, providing driver identity, debug macros, shared cache declarations, and cross-file libsas callback prototypes.

Important APIs/types/functions: defines `ASD_DRIVER_NAME`, `ASD_DRIVER_DESCRIPTION`, `asd_printk()`, `ENTER`/`EXIT`, `ASD_DPRINTK`, and `AIC94XX_SCB_TIMEOUT`. Declares `asd_dma_token_cache`, `asd_ascb_cache`, opaque `asd_ha_struct`/`asd_ascb`, SDS readers, device found/gone hooks, task execution, DMA mode setup, TMFs, nexus clear functions, and PHY control.

Control flow: no direct runtime flow. Macros compile into logging paths and timeouts used by SCB posting and error recovery.

State and persistence: exposes global slab caches created at module init and destroyed at module exit. All other state is held by structures declared in lower headers.

Dependencies and integration: includes Linux slab/ctype and `<scsi/libsas.h>`. It is included by all aic94xx implementation files to keep callbacks and driver naming consistent.

Risks and test signals: prototype drift across implementation files breaks module builds. Debug macro configuration materially changes logging volume. Integration tests should verify libsas callback registration, SCB timeout behavior, and debug/no-debug builds.
