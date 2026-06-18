# sources/distributed-fs/ceph-client/drivers/char/hw_random/mxc-rnga.c

## Purpose
This driver supports Freescale i.MX RNGA hardware. It wakes and starts the generator, checks oscillator health, exposes FIFO-level readiness through legacy hwrng callbacks, and reads one word from the output FIFO.

## Important APIs, Types, and Functions
- `struct mxc_rng` stores device, hwrng, MMIO base, and clock.
- `mxc_rnga_init()` clears sleep, checks `RNGA_STATUS_OSC_DEAD`, and sets `RNGA_CONTROL_GO`.
- `mxc_rnga_data_present()` polls FIFO level in `RNGA_STATUS`.
- `mxc_rnga_data_read()` reads `RNGA_OUTPUT_FIFO`, checks error interrupt, and clears errors.
- `mxc_rnga_probe()` gets the clock, maps MMIO, and manually registers hwrng.

## Control Flow
Probe allocates state, enables the RNG clock, maps registers, and registers. Core init starts the generator after oscillator check. The core uses `data_present` before `data_read`; reads consume a FIFO word and suppress it if an error interrupt is detected. Cleanup clears the GO bit. Remove unregisters the hwrng.

## State and Persistence Behavior
Hardware control state persists while selected. Clock is devm-enabled for device lifetime. There is no software buffer. Manual registration requires remove-time unregister.

## Dependencies and Integration Points
It depends on OF compatibles `fsl,imx21-rnga` and `fsl,imx31-rnga`, platform MMIO, a clock, and hwrng core.

## Risks
`mxc_rnga_probe()` never calls `platform_set_drvdata()`, so `mxc_rnga_remove()` retrieves `NULL` and cannot safely unregister on remove. Error interrupts cause `data_read()` to return zero after already reading the FIFO word. The driver uses raw MMIO accessors.

## Test Signals
Test oscillator-dead init failure, FIFO empty/present polling, error interrupt clearing, remove path driver-data bug, clock/MMIO failures, and manual hwrng unregister.
