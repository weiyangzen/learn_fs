## sources/distributed-fs/ceph-client/drivers/dma/Kconfig

### Purpose
`drivers/dma/Kconfig` defines the top-level DMA engine feature menu, core support options, platform controller driver selections, and DMA client options such as async_tx and dmatest.

### Important APIs, Types, And Functions
Key symbols include `DMADEVICES`, `DMADEVICES_DEBUG`, `DMADEVICES_VDEBUG`, `DMA_ENGINE`, `DMA_VIRTUAL_CHANNELS`, `DMA_ACPI`, `DMA_OF`, many controller symbols such as `ALTERA_MSGDMA`, `AMBA_PL08X`, and `AMD_*` through sourced sub-Kconfigs, plus clients `ASYNC_TX_DMA`, `DMATEST`, and `DMA_ENGINE_RAID`.

### Control Flow, State, And Persistence
The menu is gated by `HAS_DMA`; inside `if DMADEVICES`, core helper symbols are selected by controller drivers. Each driver entry declares architecture, bus, I/O memory, MSI, reset, or framework dependencies and selects required common pieces. At the end, subdirectory Kconfigs are sourced and client features become selectable only when the DMA engine core exists.

### Dependencies, Integration Points, Risks, And Test Signals
This file controls which C files in `drivers/dma/Makefile` participate in builds and which framework code is available. Risks include mismatched select/depend relationships, enabling drivers for unsupported architectures, hidden dependency cycles, and stale help text for hardware capabilities. Test signals are allmodconfig/allyesconfig across major architectures, COMPILE_TEST coverage, `DMA_ACPI`/`DMA_OF` auto-selection, AMD subconfig visibility, and dmatest availability when `DMA_ENGINE` is selected.
