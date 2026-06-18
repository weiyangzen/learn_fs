# sources/distributed-fs/ceph-client/drivers/reset/reset-tps380x.c

Purpose: reset-controller driver for TI TPS380x voltage supervisor reset GPIOs, currently supporting TPS3801 timing.

Important APIs/types/functions: `tps380x_reset` stores rcdev, reset GPIO, and reset delay. `tps380x_reset_assert()` drives the GPIO active, while `tps380x_reset_deassert()` releases it and sleeps for the maximum reset time. `tps380x_reset_of_xlate()` exposes a single zero-cell reset line.

Control flow: probe gets match timing data, requests `reset` GPIO as initially asserted, sets max delay, and registers one reset. Consumers assert/deassert through GPIO operations that may sleep.

State and persistence: only GPIO output state persists in hardware. Delay data is static per compatible.

Dependencies and integration: GPIO descriptors, OF match data, platform probing, reset-controller framework.

Risks and test signals: no `.reset` pulse op is provided, only assert/deassert. Always waits max delay rather than typ/min. Test GPIO polarity from DT, initial asserted output, deassert delay, missing GPIO, and zero-cell phandle translation.
