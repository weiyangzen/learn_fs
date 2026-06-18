# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.h

Purpose: Power-management interface and state structure for CW1200.

Important APIs and types: Defines `struct cw1200_pm_state` with suspend-state pointer, stay-awake timer, optional platform device pointer, and lock. Declares PM init/deinit, WoW suspend/resume, suspend eligibility, and stay-awake helpers when `CONFIG_PM` is enabled; provides no-op/negative inline fallbacks otherwise.

Control flow: Main registration initializes PM state, mac80211 callbacks call WoW functions, and queue/scan/BH code uses `cw1200_pm_stay_awake` to defer sleep.

State and persistence: In-memory per-device PM state only.

Dependencies and integration: Included by `cw1200.h`, `main.c`, queue, scan, BH, and STA code. Conditional compilation tracks `CONFIG_PM`.

Risks: Non-PM builds make `cw1200_can_suspend` return 0, so bus suspend code must be compiled consistently. The `pm_dev` field is present but not used in this subset.

Test signals: Compile with and without `CONFIG_PM`; verify callers link and PM callbacks are only registered when expected.
