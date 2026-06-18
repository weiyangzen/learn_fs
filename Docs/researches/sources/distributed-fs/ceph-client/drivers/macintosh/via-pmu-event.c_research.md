# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.c

Purpose: exposes selected PMU environment events as Linux input events. It currently reports power-button and lid-switch state for KeyLargo-based PMU models.

Important APIs and functions: `via_pmu_event_init()` allocates and registers an `input_dev` named `PMU` with `EV_KEY`, `EV_SW`, `KEY_POWER`, and `SW_LID` capabilities. `via_pmu_event()` is the callable bridge from the PMU interrupt handler; it maps `PMU_EVT_POWER` and `PMU_EVT_LID` to input reports and syncs the device.

Control flow: late init exits unless `pmu_get_model()` reports `PMU_KEYLARGO_BASED`. After registration, `via-pmu.c` calls `via_pmu_event()` from PMU environment interrupt handling when it sees the expected packet length.

State and persistence: one global `pmu_input_dev` pointer. No event queue beyond the input subsystem.

Dependencies and integration: depends on PMU model detection, `linux/input.h`, and constants from `via-pmu-event.h`. Integrated by direct call from `via-pmu.c`.

Risks: no module exit/unregister path is present because it is built as late init platform support. Event support is limited to models known to report these bits. Calls before input device registration are ignored.

Test signals: input device appears on KeyLargo PMU systems, power button emits `KEY_POWER`, lid changes emit `SW_LID`, unsupported PMU models return `-ENODEV`, and malformed/unrecognized event IDs are ignored.
