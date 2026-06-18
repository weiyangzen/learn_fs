# sources/distributed-fs/ceph-client/net/mac80211/pm.c

Purpose: implements mac80211 suspend preparation and WoWLAN wakeup reporting.

Important APIs and functions: `__ieee80211_suspend()` is the main suspend path used by mac80211. `ieee80211_sched_scan_cancel()` stops scheduled scans unless WoWLAN any-trigger keeps them alive. `ieee80211_report_wowlan_wakeup()` exports driver wakeup reporting to cfg80211.

Control flow: suspend marks `local->suspending`, cancels scans, DFS CAC, ROC work, and virtual monitor, tears down BA sessions unless WoWLAN any-trigger is active, stops queues, synchronizes networking, flushes queues and workqueue, deletes timers, and then either delegates to `drv_suspend()` for WoWLAN or removes driver-created interfaces and stops the device. Resume is intentionally handled elsewhere through reconfiguration.

State and persistence: transient state includes `local->suspending`, `quiescing`, `suspended`, `wowlan`, queue stop reasons, BA block flags, dynamic power-save flags/timers, station auth/assoc progress, and driver interface presence. No durable state is written.

Dependencies and integration points: depends on scan, DFS, ROC purge, monitor removal, BA teardown, managed-mode quiesce, driver suspend/remove/stop operations, queue control, net synchronization, LED/mesh headers, and cfg80211 WoWLAN reporting.

Risks: memory barriers are used so timers and other paths observe suspending/quiescing state in order. Error returns from `drv_suspend()` must restore queue state and BA flags. WoWLAN power-save handling can otherwise leave firmware active after resume if TX woke it during suspend.

Test signals: suspend with no open interfaces, WoWLAN success/error/deferred-disconnect returns, active auth/assoc cleanup, BA session blocking and restoration on driver error, scheduled scan keep/cancel behavior, and queue/timer quiescence.
