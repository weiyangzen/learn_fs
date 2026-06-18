# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-esdhc.h

## Purpose

`sdhci-esdhc.h` is the shared register and quirk definition header for Freescale/NXP eSDHC-style platform drivers. It centralizes default SDHCI quirks and non-standard eSDHC register offsets/bits used by the i.MX and ColdFire drivers.

## Important APIs, Types, And Functions

- `ESDHC_DEFAULT_QUIRKS` combines common SDHCI quirks: forced 2048 block size, 32-bit DMA address, no busy IRQ, data timeout uses SDCLK, PIO delay, and no HISPD bit.
- Defines eSDHC register offsets for host control, present state, protocol control, system control, system control 2, capabilities 1, tuning block registers, SD clock/timing control, DLL config/status, and DMA system control.
- Defines bit fields for bus width, voltage select, clock enables/dividers, tuning block control, HS400 mode/window, loopback clock, DLL enable/reset/lock, DMA peripheral clock, FIFO flush, and DMA snoop.

## Control Flow

This header has no runtime control flow. Including drivers use these macros in their accessor, clock, reset, tuning, and DMA paths.

## State And Persistence Behavior

No state is defined. The macros describe hardware state manipulated by consumers.

## Dependencies And Integration Points

The header depends on SDHCI quirk constants from `sdhci.h` through its consumers. It is included by `sdhci-esdhc-imx.c` and `sdhci-esdhc-mcf.c` to keep register naming consistent across related eSDHC drivers.

## Risks And Edge Cases

- Shared macros are used by multiple SoC families with different endian and register-layout requirements; changing a bit definition can affect both i.MX and ColdFire behavior.
- `ESDHC_DEFAULT_QUIRKS` encodes policy as well as hardware limitations.
- Several registers are non-standard relative to SDHCI; accidental use of generic SDHCI offsets in consumers can bypass these definitions.

## Test Signals

Validation is indirect through users: i.MX and ColdFire builds, register programming in clock/reset/tuning paths, bus-width transitions, DLL/HS400 support, timeout behavior, and DMA-system-control paths.
