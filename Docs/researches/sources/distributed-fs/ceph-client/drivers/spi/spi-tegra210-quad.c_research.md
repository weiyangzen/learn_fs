# sources/distributed-fs/ceph-client/drivers/spi/spi-tegra210-quad.c

## Purpose
`spi-tegra210-quad.c` implements NVIDIA Tegra QSPI host support for Tegra210, Tegra186/194, Tegra234, and Tegra241 style controllers. It is a half-duplex QSPI driver with single/dual/quad bus widths, PIO and DMA transfer paths, optional external DMA or internal DMA-address registers, combined command/address/dummy/data sequence support on capable SoCs, TPM hardware flow support on newer SoCs, OF and ACPI matching, and runtime PM.

## Important APIs, Types, And Functions
`struct tegra_qspi` contains device/controller handles, spinlock, clock/MMIO/IRQ, DMA channels and coherent buffers, active transfer progress, register shadows, dummy-cycle state, completion objects, and SoC feature data. `struct tegra_qspi_soc_data` records combined-sequence capability, TPM support, external DMA availability, and chip-select count. `struct tegra_qspi_client_data` stores per-device tap delays.

Core SPI entry points are `tegra_qspi_probe()`, `tegra_qspi_remove()`, `tegra_qspi_setup()`, and `tegra_qspi_transfer_one_message()`. Transfer paths are split into `tegra_qspi_combined_seq_xfer()` and `tegra_qspi_non_combined_seq_xfer()`, selected by `tegra_qspi_validate_cmb_seq()`. Lower-level helpers configure individual transfers, start PIO or DMA, flush FIFOs, map/unmap DMA, stop failed PIO/DMA, handle timeout fallback, and process IRQ completion.

## Control Flow
Probe allocates a host, applies OF/ACPI match data, configures half-duplex mode bits and word sizes, maps registers, gets IRQ and optional clock, initializes DMA support, enables runtime PM autosuspend, resets hardware, writes default command state, requests a threaded IRQ, and registers the controller. Setup parses tap-delay device properties, configures inactive CS polarity in the default command register, and uses runtime PM around register access.

For each message, validation selects combined mode if the SoC supports it and the transfer list resembles command, address, optional dummy, and data phases with supported lengths. Combined mode enables the combined-sequence register path, optionally enables TPM wait-poll, programs command/address values and configs, then runs only the data transfer through the common transfer engine. Non-combined mode disables combined/TPM bits, folds a following dummy transfer into QSPI dummy-cycle programming when possible, then runs each transfer independently. Individual transfers compute packing, set mode and tap delays on the first transfer, program bus width and TX/RX direction, write dummy cycles, flush FIFOs, and choose DMA for large transfers when `use_dma` is true.

IRQ completion is threaded only. The IRQ thread checks whether timeout handling already cleared `curr_xfer`, snapshots FIFO error bits, masks/clears IRQs, then dispatches to CPU or DMA handlers. CPU handling drains/fills FIFO chunks. DMA handling waits for external DMA completions when channels exist or relies on hardware internal DMA address registers otherwise, copies/unpacks data, unmaps packed DMA mappings, and continues with another chunk if required. Timeout handling checks `QSPI_RDY`; if hardware completed despite a lost/delayed IRQ, it manually invokes the same completion path instead of failing the transfer.

## State And Persistence
Register shadows include default and active command registers, DMA control, CS timing registers, and dummy cycles. Active transfer state is protected by `lock` and explicitly cleared after each transfer path. DMA buffers are persistent device-lifetime resources. Runtime PM gates the QSPI clock except on ACPI systems where runtime PM clock operations are disabled. System resume restores command registers and resumes the SPI controller. No persistent storage is used.

## Dependencies And Integration Points
The driver depends on SPI core, OF and ACPI platform matching, clk, reset via `device_reset()`, runtime PM, DMAengine, DMA mapping, MMIO polling helpers, threaded IRQs, and generic device properties. Compatible strings include `nvidia,tegra210-qspi`, `nvidia,tegra186-qspi`, `nvidia,tegra194-qspi`, `nvidia,tegra234-qspi`, and `nvidia,tegra241-qspi`; ACPI IDs include `NVDA1213`, `NVDA1313`, `NVDA1413`, and `NVDA1513`.

## Risks
This is a high-complexity driver. Combined-sequence validation must match actual SPI NOR/TPM transfer shapes or the wrong path may be selected. DMA behavior differs sharply between SoCs with external DMA channels and SoCs using internal DMA address registers; IOMMU absence can force PIO. Packed DMA maps client buffers directly but unpacked mode uses coherent bounce buffers, so unmap timing and length rounding matter. Timeout recovery deliberately completes transfers when `QSPI_RDY` is set despite a missed IRQ; this avoids false failures but needs race testing. Some register-value macros use uppercase parameter names while expanding lowercase identifiers, which is suspicious even if those macros are unused or hidden by compiler coverage.

## Test Signals
Test non-combined and combined SPI memory-style command/address/dummy/data sequences, TPM hardware-flow mode on capable SoCs, single/dual/quad data widths, 8/16/32-bit packed transfers, FIFO and DMA thresholds, external-DMA and internal-DMA SoCs, IOMMU-disabled PIO fallback, ACPI and OF probe paths, timeout-with-ready recovery, real timeout cleanup, and suspend/resume. Useful diagnostics include FIFO error logs, QSPI register dumps, lost/delayed IRQ warnings, DMA timeout errors, and combined-sequence acceptance/rejection behavior.
