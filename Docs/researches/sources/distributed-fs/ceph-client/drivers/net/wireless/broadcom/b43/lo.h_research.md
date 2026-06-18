# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/lo.h

This header declares G-PHY local oscillator calibration types and APIs. `struct b43_loctl` stores signed I/Q control values. `struct b43_lo_calib` stores a calibrated control pair keyed by baseband and RF attenuation plus a jiffies timestamp. `struct b43_txpower_lo_control` stores RF/BB attenuation lists, a 32-word DC lookup table cache, calibration list, measurement timestamps, TX bias/magnification, and power vector.

Public APIs are `b43_lo_g_adjust()`, `b43_lo_g_adjust_to()`, `b43_gphy_dc_lt_init()`, `b43_lo_g_maintenance_work()`, `b43_lo_g_cleanup()`, and `b43_lo_g_init()`. G-PHY code uses them to initialize hardware power-control tables, adjust LO after attenuation/power changes, run periodic maintenance, and free cached calibrations.

State is runtime-only and attached to the G-PHY object. Expiration constants define when calibration entries, power vectors, and TX-control measurements become stale. Dependencies include `phy_g.h` RF/baseband attenuation structures and b43 LO implementation/debugfs inspection. Risks are invalid I/Q ranges, timeout assumptions tied to periodic scheduling, and `B43_DC_LT_SIZE` matching hardware. Test signals include adjustment on power/channel changes, periodic refresh, and cleanup freeing all list entries.
