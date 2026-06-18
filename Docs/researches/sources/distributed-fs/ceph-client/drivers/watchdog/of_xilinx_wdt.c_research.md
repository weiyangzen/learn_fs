# sources/distributed-fs/ceph-client/drivers/watchdog/of_xilinx_wdt.c

## Purpose
`of_xilinx_wdt.c` drives Xilinx AXI/XPS timebase watchdog devices described by devicetree. It starts/stops the two-stage enable sequence, services the timer, and calculates timeout from DT interval and clock frequency.

## Important APIs, types, and functions
`struct xwdt_device` contains MMIO base, interval, spinlock, watchdog device, and optional clock. Operations are `xilinx_wdt_start`, `xilinx_wdt_stop`, `xilinx_wdt_keepalive`, `xwdt_selftest`, `xwdt_probe`, and suspend/resume handlers.

## Control flow
Probe maps MMIO, reads `xlnx,wdt-interval` and `xlnx,wdt-enable-once`, obtains an optional prepared clock or fallback `clock-frequency`, computes timeout as twice the first overflow interval, runs a timebase self-test with the clock enabled, then registers the watchdog. Start enables the clock, clears previous status bits, sets enable bit 1 in CSR0, then enable bit 2 in CSR1. Stop clears both enable bits and disables the clock. Keepalive writes status bits to reset state.

## State and persistence
Hardware CSR bits store enabled and reset-status state. `enable_once` maps to watchdog nowayout. The clock is prepared by devm and enabled only during self-test or active watchdog operation.

## Dependencies and integration points
It depends on OF compatibles `xlnx,xps-timebase-wdt-1.00.a` and `1.01.a`, optional clock framework, DT properties, MMIO access, spinlock serialization, and watchdog core.

## Risks and test signals
Risks include timeout calculation overflow/zero from `1 << wdt_interval`, optional clock paths where `clk_enable(NULL)` behavior must remain valid, self-test false failures, and no set-timeout support because timeout is hardware/DT fixed. Test signals include DT with/without clock, missing properties, enable-once nowayout, self-test behavior, suspend/resume active watchdog, and start/stop register sequencing.
