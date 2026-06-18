<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-pmu.c

Purpose: This file implements the PMU backend for Apple Motion Sensor hardware found on late 2005 PowerBooks. It accesses sensor registers through PMU ADB requests.

Important APIs and state: `ams_pmu_cmd` stores the PMU command byte derived from the OF `reg` property. Backend callbacks are `ams_pmu_get_xyz()`, `ams_pmu_get_vendor()`, `ams_pmu_clear_irq()`, and exit `ams_pmu_exit()`. Register accessors `ams_pmu_set_register()` and `ams_pmu_get_register()` submit PMU requests and wait on completions.

Control flow: `ams_pmu_init()` fills the core callback contract, reads the command byte, disables and clears all interrupts, attaches the core sensor, programs default freefall/shock thresholds and debounce/control values, clears interrupts, marks device present, enables interrupts, and logs success. Exit detaches core resources, disables and clears interrupts, clears presence state, and logs unloading.

State and persistence: The PMU command byte and `ams_info` singleton state persist while loaded. Hardware thresholds are programmed at init and not persisted by the driver. Register access uses static `adb_request` objects in the get/set helpers, which assumes serialized task-context access through the core mutex.

Dependencies and integration: It depends on PMU request APIs, ADB request completions, Open Firmware properties, and AMS core callbacks.

Risks and test signals: The static request objects in register accessors are safe only if callers keep serialization; concurrent direct calls would corrupt state. PMU request failure returns silently with zero/default values. Test missing `reg` property, PMU request failure, interrupt enable/clear bits, attach failure cleanup, and exit with pending interrupt work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-pmu.c -->
