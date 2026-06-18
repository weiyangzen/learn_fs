# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-led.c

Purpose: registers a LED class device for the PMU-controlled front LED on supported KeyLargo-based PowerBook, iBook, and PowerMac G5 systems.

Important APIs and functions: `pmu_led_set()` accepts `LED_OFF` or `LED_FULL`, coalesces desired state in `requested_change`, and sends PMU command `0xee` when no previous blink request is active. `pmu_req_done()` sends a deferred last requested change after asynchronous PMU completion. `via_pmu_led_init()` filters supported models and registers `pmu-led::front`.

Control flow: late init checks PMU model and root OF `model`, initializes the lock and request state, and registers the LED. Brightness changes update `requested_change` under `pmu_blink_lock`; if the previous request is complete and the system is not suspended, a PMU request is issued. Completion callback drains one deferred state.

State and persistence: `pmu_blink_req` is a reusable global `adb_request`; `requested_change` stores no-change/off/on; `pmu_blink_lock` serializes access. LED state is not persisted by the driver.

Dependencies and integration: depends on LED class framework, PMU request API, `pmu_sys_suspended` from `via-pmu.c`, OF model strings, and optional disk-activity trigger.

Risks: only full/off brightness is supported; intermediate brightness is ignored. Request coalescing keeps only the most recent pending state. The callback can issue another PMU request while holding the LED lock, so PMU callback behavior must remain compatible.

Test signals: LED device registration on allowed models only, disk trigger default when configured, full/off PMU command emission, coalesced rapid brightness changes, no command while suspended, and deferred update after request completion.
