# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icss_iep.c

## Purpose
`icss_iep.c` implements the TI ICSS/ICSSG Industrial Ethernet Peripheral timer driver. It exposes the IEP counter as a PTP hardware clock, supports firmware-provided clock operations, PPS/perout/external timestamp features, variant-specific register maps, exclusive client acquisition by DT phandle, and raw firmware timer initialization.

## Important APIs, Types, and Functions
Exported APIs include `icss_iep_get()`, `icss_iep_get_idx()`, `icss_iep_put()`, `icss_iep_init()`, `icss_iep_exit()`, `icss_iep_init_fw()`, `icss_iep_exit_fw()`, `icss_iep_get_count_low()`, `icss_iep_get_count_hi()`, and `icss_iep_get_ptp_clock_idx()`. PTP callbacks are `icss_iep_ptp_adjfine()`, `icss_iep_ptp_adjtime()`, `icss_iep_ptp_gettimeex()`, `icss_iep_ptp_settime()`, and `icss_iep_ptp_enable()`. Perout/PPS work is handled by compare register programming, `icss_iep_cap_cmp_irq()`, and `icss_iep_cap_cmp_work()`.

## Control Flow and State
Probe maps the IEP register resource, optionally requests the compare/capture IRQ, reads the clock rate, calculates default nanosecond increment, initializes a regmap using SoC-specific offsets and valid-register callbacks, copies base PTP info, initializes the PHC mutex, stores drvdata, and disables the counter. Client drivers acquire a single IEP through `icss_iep_get_idx()`, which rejects concurrent owners via `client_np`. `icss_iep_init()` programs default and compensation increments, optional slow compensation, shadow mode for cyclic operation, sets time to real time, derives supported PTP features from hardware flags/clockops/IRQ, and registers the PHC. `icss_iep_exit()` unregisters the PHC, disables the counter, and tears down PPS/perout state.

## Dependencies and Integration Points
The file depends on PTP clock kernel APIs, regmap with custom MMIO callbacks, platform/OF helpers, clocks, workqueues, and PRU Ethernet firmware clockops (`prueth_iep_clockops` declared in the header). ICSSG Ethernet drivers use this for PHC indices, firmware time sync, RX/TX timestamp conversion, and perout/PPS.

## Risks and Test Signals
`icss_iep_ptp_adjfine()` divides by `ppb`; a zero adjustment can produce a divide-by-zero path unless guarded elsewhere. PPS and perout are mutually exclusive and share compare 1/sync registers, so state transitions need lock coverage. Register writes mix `regmap` and direct `readl/writel` for timing, so variant offset tables must be exact. Test signals include PHC registration across AM335x/AM437x/AM57xx/AM654 variants, 32-bit versus 64-bit counter reads, adjfine positive/negative/zero, PPS/perout enable/disable and IRQ work, exclusive get/put behavior, firmware clockops delegation, and invalid slow clock rejection.
