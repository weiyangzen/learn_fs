## sources/distributed-fs/ceph-client/drivers/dma/dw/internal.h

Purpose: Private shared header for classic DesignWare AHB DMA core, variants, and bus glue.

Important APIs/types/functions: declares `do_dma_probe/remove()`, core enable/disable helpers, variant probes/removes, `dw_dma_filter()`, ACPI/OF registration helpers, `struct dw_dma_chip_pdata`, and built-in platform-data instances for standard DW, iDMA32, and xbar iDMA32.

Control flow: bus glue selects a `dw_dma_chip_pdata` from OF/ACPI/PCI match data, fills `struct dw_dma_chip`, then calls the selected `probe()` callback. Variant probe installs callbacks and delegates to core probe.

State and persistence: static platform data encodes channel count, allocation order, priority, block size, masters, data width, multiblock support, and quirks. Runtime state itself is outside this header.

Dependencies and integration: includes public `linux/dma/dw.h` and private `regs.h`. Provides CONFIG_ACPI and CONFIG_OF stubs so callers can be unconditional.

Risks and test signals: static pdata mistakes affect entire hardware families. Test that each match path selects the intended pdata, that OF/ACPI stubs compile out cleanly, and that variant probe/remove linkage remains valid.
