# sources/distributed-fs/ceph-client/drivers/watchdog/xilinx_wwdt.c

## Purpose
`xilinx_wwdt.c` implements the Xilinx Versal window watchdog driver. It programs closed and open watchdog windows from the input clock and exposes the device through the watchdog core.

## Important APIs, types, and functions
`struct xwwdt_device` stores MMIO base, spinlock, `watchdog_device`, clock frequency, close-window percentage, and computed closed/open tick counts. Ops are `xilinx_wwdt_start` and `xilinx_wwdt_keepalive`. Probe maps registers, enables the clock, computes timeout limits, initializes watchdog core fields, and registers. Module parameters are `wwdt_timeout` and `closed_window_percent`.

## Control flow
Probe validates a >=1 MHz source clock, computes `max_hw_heartbeat_ms` from the combined 32-bit windows, validates/chooses the closed-window percentage, initializes timeout, converts milliseconds to ticks, and adjusts closed/open windows for hardware maximums. Start enables master write, clears enable, writes first and second window registers, then enables the watchdog. Ping enables master write and sets the software restart bit in ESR.

## State and persistence
Runtime state is per-platform device. Hardware window registers persist until reset or reprogramming. `nowayout` is forced on through `watchdog_set_nowayout(..., 1)`.

## Dependencies and integration points
It depends on platform MMIO resources, clocks, OF compatible `xlnx,versal-wwdt`, math64 helpers, spinlocks, and watchdog core min/max heartbeat handling.

## Risks and test signals
Risks include clock-rate assumptions, tick multiplication overflow before 64-bit division boundaries, closed-window percentages that violate hardware limits, forced nowayout surprise, no stop op, and pinging during the closed window. Test signals include multiple clock rates, timeout above and below hardware maximum, invalid close percentages, watchdog core min heartbeat enforcement, OF probe, and register write/read smoke tests.
