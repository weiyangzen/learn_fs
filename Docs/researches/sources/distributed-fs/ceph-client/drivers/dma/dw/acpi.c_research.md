## sources/distributed-fs/ceph-client/drivers/dma/dw/acpi.c

Purpose: ACPI DMA controller registration and channel filter for classic DW DMA devices.

Important APIs/types/functions: `dw_dma_acpi_controller_register()`, `dw_dma_acpi_controller_free()`, and internal `dw_dma_acpi_filter()`. Uses `acpi_dma_controller_register()`, `acpi_dma_simple_xlate()`, and `dw_dma_filter()`.

Control flow: registration checks for an ACPI companion, allocates `acpi_dma_filter_info`, sets a DMA_SLAVE capability mask and filter callback, and registers the controller. The filter translates `acpi_dma_spec` slave ID into a `dw_dma_slave` with memory/peripheral master IDs from driver match data, then delegates channel suitability to `dw_dma_filter()`.

State and persistence: devm-allocated filter info lives for device lifetime. No persistent state beyond ACPI registration.

Dependencies and integration: compiled under `CONFIG_ACPI`; used by both platform and PCI glue after successful core probe.

Risks and test signals: incorrect match data master IDs can bind clients to wrong bus masters; missing ACPI companion should be a no-op. Test ACPI DMA client lookup, removal cleanup, and systems without ACPI companions.
