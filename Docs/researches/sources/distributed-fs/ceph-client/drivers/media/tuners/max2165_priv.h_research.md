# sources/distributed-fs/ceph-client/drivers/media/tuners/max2165_priv.h

Purpose: private register map and state for MAX2165. It defines register addresses for PLL divider, tracking filter, LNA, PLL config, shutdown/VCO/baseband/DC-offset, ROM table access, status, and autotune registers, plus `struct max2165_priv`.

The private state stores parent config/I2C, cached frequency/bandwidth, and calibration values read from the chip ROM: notch filter configs, balun references, and 7/8 MHz baseband filter configs. These fields are consumed by bandwidth and RF tuning paths.

Dependencies are the public config type included by the C file. Risks: register constants are untyped raw values, cached bandwidth must be kept in sync by implementation, and ROM-derived values need valid reads before tuning. Test signals: init path reading ROM table, set-bandwidth using both 7 and 8 MHz values, and failure injection for ROM/status register reads.
