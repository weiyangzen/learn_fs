# sources/distributed-fs/ceph-client/include/linux/pmu.h

Purpose: declares the PowerMac PMU interface for ADB-request based communication with the microcontroller handling battery charging, RTC, backlight, restart/shutdown, and power status on older PowerBook systems.

Important APIs and types: functions include PMU discovery, request submission/queueing/poll/wait, suspend/resume, IR LED, RTC get/set, restart/shutdown/unlock, presence/model queries, and backlight sleep/init controls. `struct pmu_battery_info` exports battery flags, charge/max charge, amperage, voltage, and time remaining. Globals expose battery count, battery info array, power flags, and suspend state.

Control flow: platform code discovers the PMU, drivers enqueue ADB requests and wait or poll for completion, power-management code brackets long interrupt-disabled regions with `pmu_suspend()`/`pmu_resume()`, and battery/RTC/backlight users query exported state or invoke helper commands.

State and persistence: state is global PMU driver runtime state: queued requests, battery snapshots, AC-present flags, model/presence data, RTC values, and suspend flag. The RTC itself persists in hardware; the header only declares accessors.

Dependencies and integration points: integrates with ADB request handling, PowerPC platform PM, RTC core, backlight code, xmon polling, battery status, and UAPI PMU commands. Suspend/resume stubs are empty without `CONFIG_ADB_PMU`.

Risks and test signals: risks include request lifetime while asynchronous completion is pending, non-stackable suspend calls, stale global battery snapshots, architecture/config misuse, and RTC conversion errors. Test PMU discovery on supported hardware, request completion ordering, suspend/resume, RTC set/get, shutdown/restart commands, backlight behavior, and non-PMU build compilation.
