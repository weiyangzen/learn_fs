# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc-mcf.c

## Purpose

`sdhci-esdhc-mcf.c` is the Freescale ColdFire eSDHC platform driver. It adapts a big-endian ColdFire eSDHC controller to the SDHCI core, handles register-offset/endian differences, clock divisor calculation, limited bus-width/card-detect platform data, DMA endian swapping, and ColdFire-specific quirks.

## Important APIs, Types, And Functions

- `struct pltfm_mcf_data` stores three clocks, shadow transfer mode (`aside`), and current bus-width bits.
- `esdhc_mcf_writeb_be()`, `esdhc_mcf_writew_be()`, `esdhc_mcf_writel_be()`, `esdhc_mcf_readb_be()`, `esdhc_mcf_readw_be()`, and `esdhc_mcf_readl_be()` adapt SDHCI byte/word/long accesses.
- `esdhc_mcf_pltfm_set_clock()` calculates divisors from ColdFire PLL registers and applies eSDHC clock-control bits.
- `esdhc_mcf_reset()` restores bus width and interrupt enables after reset.
- `esdhc_mcf_request_done()` swaps 32-bit words after DMA reads; `esdhc_mcf_copy_to_bounce_buffer()` swaps writes copied to the bounce buffer.
- `esdhc_mcf_plat_init()` interprets `mcf_esdhc_platform_data` for card-detect and max bus width.

## Control Flow

Probe allocates a platform SDHCI host with ColdFire private data, disables SDMA boundary, enables Auto CMD12, obtains `ipg`, `ahb`, and `per` clocks, enables them in order, initializes card-detect and bus-width policy from platform data, calls `sdhci_setup_host()`, requires the bounce buffer, and registers with `__sdhci_add_host()`. Remove unregisters the host and disables all clocks.

During requests, generic SDHCI code calls the custom accessors. Transfer mode writes are shadowed and combined with command writes; STOP commands are marked as abort. DMA error bit 28 is remapped to SDHCI ADMA error. Read-completion and write-bounce callbacks compensate for missing hardware DMA-endian selection.

## State And Persistence Behavior

Private state persists clock handles, a pending transfer-mode shadow, and current bus width. Bus width is restored after resets. No persistent storage exists.

## Dependencies And Integration Points

The file depends on platform data from `<linux/platform_data/mmc-esdhc-mcf.h>`, ColdFire PLL register macros, `sdhci-pltfm`, shared eSDHC register definitions in `sdhci-esdhc.h`, Linux clocks, MMC core, scatterlist mapping iterators, and SDHCI bounce-buffer support.

## Risks And Edge Cases

- The pdata initializer uses an undesignated value immediately after `.quirks`; in C this initializes the next field (`quirks2`) with `SDHCI_QUIRK2_HOST_NO_CMD23`, but it is easy to misread and fragile for struct layout changes.
- Clock divisor calculation relies on ColdFire PLL register layout and requested/actual clocks can diverge.
- DMA read/write endian swapping depends on bounce-buffer and scatterlist lengths.
- Platform data is mandatory; probe fails without it.

## Test Signals

Build ColdFire config coverage, probe with valid/invalid platform data, all three clocks enabled and unwound on failure, 1-bit and 4-bit bus modes, controller/permanent/no card-detect modes, DMA reads and writes with endian validation, CMD12/Auto CMD12 behavior on large cards, timeout handling, reset bus-width restoration, and remove clock cleanup.
