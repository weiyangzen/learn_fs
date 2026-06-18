# sources/distributed-fs/ceph-client/drivers/clk/clk-twl6040.c

Purpose: platform CCF driver exposing the TWL6040 McPDM functional clock `pdmclk`. It powers the audio IC while prepared and reports the TWL6040 system-clock rate.

Important APIs/types/functions: `struct twl6040_pdmclk` stores parent MFD pointer, device pointer, `clk_hw`, and a software enabled flag. Clock ops are `twl6040_pdmclk_is_prepared`, `twl6040_pdmclk_prepare`, `twl6040_pdmclk_unprepare`, and `twl6040_pdmclk_recalc_rate`. Erratum support is in `twl6040_pdmclk_reset_one_clock()` and `twl6040_pdmclk_quirk_reset_clocks()`.

Control flow: probe obtains the parent `struct twl6040` from the parent device's driver data, allocates state, registers the `pdmclk` hardware clock, stores drvdata, and adds a simple OF provider. prepare powers the TWL6040, resets HPPLL and LPPLL to work around Phoenix Audio IC erratum #6, marks enabled, and powers down again if reset fails. unprepare powers off and clears enabled on success. recalc_rate delegates to `twl6040_get_sysclk()`.

State and persistence: hardware power state and PLL reset bits live in the TWL6040 MFD. Software tracks prepared state with `enabled`; `CLK_GET_RATE_NOCACHE` forces rate reads rather than cached CCF rates.

Dependencies and integration: depends on TWL6040 MFD APIs, platform-device binding `twl6040-pdmclk`, CCF, and OF simple provider. Audio/McPDM consumers request this clock from the TWL6040 child device.

Risks: `enabled` is not protected by a lock, relying on CCF prepare serialization. unprepare ignores power-off failure except for leaving `enabled` set. The erratum workaround always resets both PLLs during prepare, which may affect other TWL6040 users if sequencing assumptions change. Missing parent drvdata would lead to invalid MFD access.

Test signals: probe with TWL6040 MFD parent, prepare power-on plus HPPLL/LPPLL reset sequence, failure rollback, unprepare power-off, rate reporting for different sysclk selections, and OF clock lookup. No direct tests are present.
