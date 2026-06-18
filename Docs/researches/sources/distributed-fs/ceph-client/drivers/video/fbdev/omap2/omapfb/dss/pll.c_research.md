# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/pll.c

## Purpose
`pll.c` is the generic DSS PLL framework for fbdev OMAP DSS. It registers PLL objects, controls enable/disable and cached configuration, searches clock/divider combinations, waits for hardware state changes, and writes two supported PLL register programming formats.

## Important APIs, types, and functions
Public APIs are `dss_pll_register`, `dss_pll_unregister`, `dss_pll_find`, `dss_pll_enable`, `dss_pll_disable`, `dss_pll_set_config`, `dss_pll_hsdiv_calc`, `dss_pll_calc`, `dss_pll_wait_reset_done`, `dss_pll_write_config_type_a`, and `dss_pll_write_config_type_b`. State is held in `static struct dss_pll *dss_plls[4]`.

## Control Flow
Registration stores PLLs in the first free slot. Enable prepares the input clock, enables an optional regulator, then calls the PLL-specific enable op; errors unwind regulator and clock. Disable calls the PLL-specific disable op, disables regulator and clock, and clears cached clock info. Calculation helpers iterate legal `n`, `m`, and HSDIV ranges and stop when a callback accepts a candidate. Type A/B writers program PLL configuration registers, trigger GO, wait for GO clear and lock, and for type A enable HSDIV outputs and wait for acknowledgements.

## State and Persistence
Runtime state is the PLL registry and each PLL's cached `cinfo`. Hardware state persists in PLL control/configuration/status registers while powered. No persistent storage exists.

## Dependencies and Integration Points
It depends on common DSS structs in `dss.h`, clocks, optional regulators, jiffies/hrtimeout polling, and low-level MMIO. HDMI and DRA7 video PLL drivers build `struct dss_pll` instances and use these helpers.

## Risks
The registry has no locking and fixed capacity. Waits are polling/time-based. Type-specific register writers rely on correct `dss_pll_hw` bit metadata. Search helpers can be expensive across ranges but stop early by callback. Error returns differ (`-EIO` versus `-ETIMEDOUT`) across lock failures.

## Test Signals
Test registration capacity and unregister, enable failure unwinding, regulator/clock behavior, PLL search callbacks for edge frequencies, type A and B register programming against known configurations, timeout paths for GO/LOCK/HSDIV ack, and cached `cinfo` clearing on disable.
