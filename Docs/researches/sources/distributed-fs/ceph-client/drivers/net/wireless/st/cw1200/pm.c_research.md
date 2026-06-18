# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/pm.c

Purpose: mac80211 WoWLAN and runtime suspend/resume support for CW1200.

Important APIs and functions: Public functions are `cw1200_pm_init`, `cw1200_pm_deinit`, `cw1200_pm_stay_awake`, `cw1200_can_suspend`, `cw1200_wow_suspend`, and `cw1200_wow_resume`. Internal helpers preserve delayed-work timers and filter settings during suspend.

Control flow: Suspend rejects if the stay-awake timer is pending, TX queues are non-empty, config mutex cannot be acquired, channel switch/join/scan is active, or BH buffers do not drain quickly. It locks TX, installs UDP and ethertype filters, optionally switches station mode to legacy PS, snapshots delayed work, enables beacon skipping, suspends BH, stores suspend state, and enables bus IRQ wake. Resume disables IRQ wake, releases scan lock, resumes BH, restores PS/beacon wake settings, queues delayed work with saved timeouts, removes filters, unlocks TX/config, and frees suspend state.

State and persistence: `cw1200_pm_state` stores a stay-awake timer, spinlock, and suspend-state pointer. Suspend-state captures delayed-work remaining times, previous PS mode, and beacon-skipping state.

Dependencies and integration: Depends on WSM filter/PM/beacon MIBs, BH suspend/resume, scan/unjoin/link work, `hwbus_ops->power_mgmt`, and mac80211 WoWLAN callbacks registered in `main.c`.

Risks: Several suspend steps call WSM commands after locking and must unwind in correct order. `cw1200_wow_resume` assumes `suspend_state` is non-NULL. Race handling with incoming IRQs returns `-EAGAIN`. PM behavior is limited to any/disconnect WoWLAN.

Test signals: Suspend rejection during TX, scan, join, channel switch, and stay-awake timer. Successful suspend/resume while associated, IRQ wake event resume, beacon skipping restoration, filter restoration, and no leaked TX/config locks after failed suspend.
