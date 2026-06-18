# sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.h Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.h

### Purpose
`mmci.h` is the private register, bitfield, variant, and host-state contract for the PrimeCell MMCI driver family. It defines the PL180/181 register map, ST/STM32/Qualcomm register extensions, interrupt masks, FIFO/DMA constants, the variant description used by `mmci.c`, callback operations overridden by companion variant files, and the full `struct mmci_host` runtime state.

### Important APIs, Types, And Functions
Important types are `enum mmci_busy_state`, `struct variant_data`, `struct mmci_host_ops`, and `struct mmci_host`. `variant_data` encodes clock register values, command response encoding, data-control quirks, FIFO sizes, DMA restrictions, busy-detection bits, IRQ layout, open-drain bits, STM32 IDMA geometry, SDIO IRQ support, and the per-variant `init()` callback. `mmci_host_ops` is the callback table for data validation/preparation, DMA setup/start/finalization/error, clock/power writes, data-control configuration, busy completion, and signal-voltage switching. Function prototypes expose core helpers to variant files: `mmci_write_clkreg()`, `mmci_write_pwrreg()`, `mmci_dmae_*()`, `qcom_variant_init()`, and `sdmmc_variant_init()`.

### Control Flow
This header has no executable control flow except the inline `mmci_dctrl_blksz()`, which encodes the current data block size as `(ffs(blksz) - 1) << 4` for classic data-control registers. At runtime, `mmci.c` selects a `variant_data` from AMBA match data, calls its `init()`, and then uses the resulting `mmci_host_ops` table for request-specific behavior. Companion files implement `qcom_variant_init()` and `sdmmc_variant_init()` only when their Kconfig options are enabled; otherwise static inline no-op stubs keep `mmci.c` buildable.

### State, Persistence, And Dependencies
`struct mmci_host` documents all persistent per-controller state: MMIO base/physical address, current request command/data, stop-abort command, clock and regulator handles, spinlock, cached clock/power/data-control registers, busy-detect state, mask1 cache, variant-private pointer, pinctrl open-drain state, hardware designer/revision, PIO scatterlist iterator and byte count, DMA progress/private data, next pre-request cookie, and delayed Ux500 busy work. The register constants define the persistent hardware state written by `mmci.c` and variant files, including power, clock, command, data timer/length/control, status/clear/masks, FIFO count/data, and STM32 IDMA descriptors.

### Integration Points
The header is consumed by `mmci.c`, `mmci_qcom_dml.c`, and `mmci_stm32_sdmmc.c`. It also bridges to external kernel subsystems through forward declarations and types from MMC, DMA engine, clock, reset, pinctrl, and platform data headers included by users. Conditional prototypes bind to `CONFIG_DMA_ENGINE`, `CONFIG_MMC_QCOM_DML`, and `CONFIG_MMC_STM32_SDMMC`, making the base driver compile across configurations while preserving variant hooks.

### Risks
Most fields are low-level hardware contracts, so bit drift is high impact. A wrong mask can corrupt clocking, response decoding, SDIO IRQ delivery, or busy-detect completion. `variant_data` contains many one-bit booleans with similar names; mixing `busy_detect`, `busy_timeout`, `datactrl_first`, `datacnt_useless`, or `dma_lli` changes core control flow. `mmci_dctrl_blksz()` assumes power-of-two block sizes and relies on prior validation for variants that cannot handle arbitrary sizes. Because `struct mmci_host_ops` instances are mutable in `mmci.c`, callback ownership must remain carefully scoped.

### Test Signals
Header validation is indirect: build all Kconfig combinations with and without DMA engine, Qualcomm DML, and STM32 SDMMC; boot probe each variant ID; verify register values written for bus width, DDR timing, SDIO mode, busy detection, IDMA, and DML. Static review should compare register offsets/bitfields against TRMs for PL180/181, Ux500, STM32 SDMMC, and Qualcomm SDCC.
