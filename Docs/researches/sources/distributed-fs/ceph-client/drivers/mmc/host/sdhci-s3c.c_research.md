# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-s3c.c

## Purpose
This file is Samsung S3C/Exynos SDHCI glue. It handles multi-source bus clock selection, Samsung-specific control register programming, platform/OF card-detect and bus-width data, quirks for known controller limitations, and runtime/system PM for `s3c-sdhci` and Exynos-compatible devices.

## Important APIs, Types, And Functions
`struct sdhci_s3c` stores the host, platform device, platform data, current clock source, external CD IRQ, IO clock, up to four bus clocks, cached rates, and a no-divider flag. `struct sdhci_s3c_drv_data` selects quirks, no-divider mode, and ops for variants. `sdhci_s3c_set_clock()` chooses the best fixed source and configures Samsung control registers; `sdhci_cmu_set_clock()` additionally asks the clock framework to set the selected source rate for CMU/no-divider variants. `sdhci_s3c_parse_dt()` derives bus width and card-detect type from OF.

## Control Flow
Probe requires platform data or OF, obtains IRQ, allocates a host with private `sdhci_s3c`, copies/parses platform data, gets and enables the `hsmmc` IO clock, discovers `mmc_busclk.0..3`, maps MMIO, optionally configures board GPIOs, installs default or variant ops, applies a long set of quirks, maps card-detect policy into broken-CD/non-removable caps, applies width/caps/PM caps, enables runtime PM, parses generic MMC OF properties, and registers the host. Under `CONFIG_PM`, it may disable the IO clock after probe for non-internal card detect.

Clock setting evaluates all available source clocks, selects the smallest delta from the requested rate, enables the new source, disables the previous source, writes base-clock selection and Samsung control registers, then invokes generic SDHCI clock programming. Exynos CMU mode uses `clk_round_rate()` for min/max and `clk_set_rate()` before enabling the card clock.

## State And Persistence
The driver persists `cur_clk`, cached `clk_rates`, card-detect type, bus-width/caps, and runtime PM state. Hardware state includes `CONTROL2`, `CONTROL3`, `CONTROL4`, selected base clock, drive strength, feedback-clock flags, and SDHCI clock control. Suspend/runtime suspend mark retune when needed and disable active bus/IO clocks; resume reenables them and calls SDHCI resume helpers.

## Dependencies And Integration Points
It depends on Samsung platform data, OF compatibles `samsung,s3c6410-sdhci` and `samsung,exynos4210-sdhci`, clock framework, PM runtime, SDHCI core, and MMC OF parsing. It registers both a platform ID table and OF table.

## Risks
The best-clock calculation assumes fixed divisors unless `no_divider` is set; wrong variant data can select bad rates. Error paths after `sdhci_alloc_host()` return without explicit host free in some early failures, relying on managed allocations only for later resources. Multiple quirks disable DMA or alter busy behavior, so performance-sensitive changes need hardware validation. Runtime PM clock gating depends on `cur_clk` being valid.

## Test Signals
Verify S3C6410 and Exynos clock rates, source switching, card-detect modes, bus widths up to 8-bit, runtime autosuspend/resume, system suspend/resume retuning, and absence of internal-clock-stable failures in CMU mode.
