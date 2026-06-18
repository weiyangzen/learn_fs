# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.h

Purpose: declares the tiny internal interface between the PMU interrupt driver and the PMU input-event bridge.

Important APIs and types: defines event IDs `PMU_EVT_POWER` and `PMU_EVT_LID`, and declares `extern void via_pmu_event(int key, int down);`.

Control flow: none. `via-pmu.c` includes this header and calls `via_pmu_event()` when decoding environment interrupt packets; `via-pmu-event.c` implements it.

State and persistence: no state. Event numbers are internal to this driver pair.

Dependencies and integration: guarded by `__VIA_PMU_EVENT_H`; no external headers required.

Risks: adding event IDs requires updating both the producer decode logic and the consumer switch. If `CONFIG_ADB_PMU_EVENT` is not enabled, call sites must be guarded as they are in `via-pmu.c`.

Test signals: compile coverage with and without PMU event input support, and runtime verification that the two defined IDs map to `KEY_POWER` and `SW_LID`.
