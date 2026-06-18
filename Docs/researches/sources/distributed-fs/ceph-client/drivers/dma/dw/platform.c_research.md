## sources/distributed-fs/ceph-client/drivers/dma/dw/platform.c

Purpose: Platform bus glue for classic DesignWare AHB DMA controllers.

Important APIs/types/functions: `dw_probe()`, `dw_remove()`, `dw_shutdown()`, OF and ACPI match tables, late suspend/resume callbacks, and subsys init/module exit registration.

Control flow: probe obtains match data, duplicates it, allocates `dw_dma_chip`, gets IRQ and MMIO resource, coerces a 32-bit DMA mask, obtains platform data from match, platform data, or DT parser, enables optional `hclk`, enables runtime PM, invokes variant probe, stores driver data, and registers OF/ACPI DMA controllers. Remove unregisters lookup providers, calls variant remove, disables runtime PM, and disables clock. Shutdown runtime-resumes unconditionally before disabling the DMA core to stop active transfers, then disables clock.

State and persistence: per-device `dw_dma_chip_pdata` and `dw_dma_chip` are devm-managed. Clock/runtime-PM state and OF/ACPI registration live for binding lifetime only.

Dependencies and integration: integrates platform resources, clocks, runtime PM, OF, ACPI, shared core, and static match data for standard DW and xbar iDMA32 variants.

Risks and test signals: shutdown/power sequencing is sensitive because registers may be inaccessible if powered off; DT fallback can fail if required pdata is absent; clock errors abort probe. Test platform probe/remove, OF and ACPI DMA client lookup, runtime/system suspend/resume, shutdown with active transfers, and optional clock absence.
