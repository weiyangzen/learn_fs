# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-iproc.c

## Purpose

`sdhci-iproc.c` is the SDHCI platform driver for Broadcom iProc, Cygnus, BCM2835/BCM2711, BCM7211A0, and related ACPI-described controllers. It supplies capability overrides, SoC-specific quirks, 32-bit-only register access with shadowing for affected Arasan integrations, clock handling, and generic SDHCI registration.

## Important APIs, Types, And Functions

- `struct sdhci_iproc_data` stores the SDHCI platform data, optional synthetic capabilities, MMC caps, and whether capabilities are missing from hardware.
- `struct sdhci_iproc_host` stores selected data plus shadow command/block registers and shadow-valid flags.
- `sdhci_iproc_readl/readw/readb()` and `sdhci_iproc_writel/writew/writeb()` implement 32-bit-only access and shadowing of block size/count plus transfer mode until command issue.
- `sdhci_iproc_get_max_clock()` uses the platform clock when present or a stored clock rate otherwise.
- `sdhci_iproc_bcm2711_get_min_clock()` raises the minimum clock to 200 kHz to avoid a BCM2711 low-bus-clock hang.
- Static `sdhci_iproc_data` instances encode quirks/caps for Cygnus, generic iProc, BCM2835, BCM2711, BCM7211A0, and ACPI variants.

## Control Flow

Probe obtains match data from OF or ACPI, creates an SDHCI platform host with the corresponding pdata and private state, parses MMC and SDHCI properties, applies extra MMC caps, enables the device clock for OF-described devices, injects synthetic capabilities with `__sdhci_read_caps()` when hardware lacks usable caps, and calls `sdhci_add_host()`. Shutdown delegates to `sdhci_pltfm_suspend()`; remove and PM use generic platform helpers.

For 32-bit-only controllers, 16-bit writes to `BLOCK_SIZE`, `BLOCK_COUNT`, and `TRANSFER_MODE` are cached. When `COMMAND` is written, the driver emits a combined block register write followed by combined transfer/command write, avoiding unsafe back-to-back same-register writes and respecting clock-domain timing delays at low card clocks.

## State And Persistence Behavior

Private state persists selected SoC data and shadowed command/block register values until the next command write. There is no nonvolatile state. Clock pointers and synthetic caps are held in generic host/platform state.

## Dependencies And Integration Points

The driver integrates OF and ACPI matching, SDHCI platform helpers, generic SDHCI PM, Linux clocks, MMC/SDHCI property parsing, and Broadcom/Raspberry Pi/Arasan hardware quirks. It supports ACPI IDs under `CONFIG_ACPI`.

## Risks And Edge Cases

- Shadowed write ordering is critical for affected Arasan cores; bypassing the custom accessors can reintroduce lost register writes.
- Low-clock delays in `sdhci_iproc_writel()` are tied to `host->clock`; incorrect clock state can under-delay writes.
- Synthetic capability data must match hardware.
- BCM2711 minimum clock is a hang workaround; changing it can affect no-card polling stability.
- ACPI variants may rely on firmware-provided caps rather than DT synthetic caps.

## Test Signals

Test OF and ACPI matching, all SoC data variants, 32-bit accessor shadowing under command issue, no-card polling at low clocks on BCM2711, synthetic caps visibility, SDR/DDR modes allowed by caps, multiblock reads with ACMD12/ACMD23 quirks, suspend/resume, shutdown, and build coverage with and without ACPI.
