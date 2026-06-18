# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/dphy.c

Purpose: controls the DesignWare MIPI D-PHY block used by the RP1 CSI-2 receiver.

Important APIs/types/functions: low-level MMIO helpers, test-interface bit setters, `dphy_transaction()`, `dphy_set_hsfreqrange()`, `dphy_init()`, `dphy_start()`, `dphy_stop()`, and `dphy_probe()`. The HS frequency table maps Mbps limits to databook HSFREQRANGE codes.

Control flow: `dphy_start()` writes active lane count, resets/shuts down the PHY, toggles the test interface clear/clock/data lines, programs HSFREQRANGE from `dphy_rate`, releases shutdown/reset, then releases host reset. `dphy_stop()` reduces active lanes to one and asserts reset. `dphy_probe()` reads and logs the hardware version.

State and persistence: consumes mutable `dphy_data` fields `dphy_rate`, `active_lanes`, and `max_lanes` set by the CFE/CSI-2 path. No persistent state is stored.

Dependencies and integration: called from `csi2_open_rx()`, `csi2_close_rx()`, and `csi2_init()`. Relies on CFE stream setup to calculate link frequency and active lane count before starting.

Risks: out-of-range rates only log an error and still choose a table entry, which may be unsafe for bad sensor/link-frequency data. Timing sleeps and reset ordering are hardware-sensitive. Active lanes must be nonzero before `dphy_start()` because it writes `active_lanes - 1`.

Test signals: hardware stream bring-up across lane counts and link frequencies, suspend/resume cycles, invalid link frequency handling, and CSI-2 packet stability after repeated start/stop.
