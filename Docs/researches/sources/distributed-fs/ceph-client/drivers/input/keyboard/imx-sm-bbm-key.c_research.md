## sources/distributed-fs/ceph-client/drivers/input/keyboard/imx-sm-bbm-key.c

Purpose: NXP i.MX System Manager SCMI BBM power-button input driver. It converts SCMI IMX BBM button notifications into a wake-capable Linux key, defaulting to `KEY_POWER`.

Important APIs/types/functions: `struct scmi_imx_bbm` stores the SCMI protocol handle, BBM ops, notifier block, keycode, cached `keystate`, suspend flag, delayed work, and input device. `scmi_imx_bbm_key_probe()` acquires `SCMI_PROTOCOL_IMX_BBM`; `scmi_imx_bbm_pwrkey_init()` allocates/registers input and notifier; `scmi_imx_bbm_key_notifier()` schedules polling; `scmi_imx_bbm_pwrkey_check_for_events()` calls `button_get()` and reports state changes.

Control flow: probe enables wakeup and registers the notifier. A BBM button event calls `pm_wakeup_event()`, optionally synthesizes a press after resume, and schedules debounce work. The delayed worker reads firmware state, reports changed press/release events, relaxes the wakeup source after transition handling, and keeps polling every 60 ms while pressed.

State/dependencies/integration: all state is volatile driver data. It integrates with the SCMI bus (`module_scmi_driver`), NXP BBM SCMI protocol ops, input core, delayed work, and system suspend wakeup accounting. Removal uses a devm action to cancel delayed work.

Risks and test signals: the notifier assumes non-button BBM events are unexpected and only logs them. Resume behavior forces a press if suspended, so tests should validate no duplicate press when firmware already reports pressed. Exercise debounce, long press polling, release wake-relax, notifier unregister, and wake from suspend.
