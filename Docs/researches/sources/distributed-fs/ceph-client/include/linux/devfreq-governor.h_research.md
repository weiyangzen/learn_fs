# sources/distributed-fs/ceph-client/include/linux/devfreq-governor.h

Purpose: Provides the internal devfreq governor interface used by devfreq policy modules and the devfreq core.

Important APIs, types, and functions: Defines `DEVFREQ_NAME_LEN`, `to_devfreq()`, governor event codes, min/max frequency sentinels, governor feature flags, governor attribute flags, and `struct devfreq_governor`. Functions start/stop/suspend/resume monitoring, update polling intervals, add/remove/devm-add governors, update status/target frequency, query frequency range, and inline `devfreq_update_stats()`.

Control flow: A governor registers with name, flags, attributes, `get_target_freq()`, and `event_handler()`. The core calls event handlers under `devfreq->lock` for lifecycle and PM events, uses monitoring work unless the governor is IRQ-driven, and asks the governor for target frequencies before applying profile callbacks.

State and persistence: Registered governors live on a core list. Per-device governor data is stored in `struct devfreq`, while profile status snapshots are refreshed through `devfreq_update_stats()`. No persistent state is defined here.

Dependencies and integration points: Depends on `linux/devfreq.h`, device core, OPP/QoS integration exposed by devfreq, and sysfs attributes selected by governor flags.

Risks and test signals: Risks include event handlers assuming unlocked state, immutable governors being switched, IRQ-driven governors accidentally scheduled, invalid polling updates, and missing `get_dev_status()`. Test governor register/remove, lifecycle events, polling interval sysfs, suspend/resume, OPP changes, and lockdep around `devfreq->lock`.
