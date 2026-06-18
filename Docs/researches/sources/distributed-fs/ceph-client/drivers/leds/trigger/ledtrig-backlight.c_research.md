<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-backlight.c

Purpose: The backlight trigger lets LEDs emulate display backlight blank/unblank state. External display/backlight code calls `ledtrig_backlight_blank()` to turn registered LEDs off or restore brightness.

Important APIs and state: `struct bl_trig_notifier` stores the LED pointer, saved brightness, previous blank state, invert setting, and list node. `ledtrig_backlight_blank(bool blank)` is exported. Sysfs exposes `inverted`. A global list of active trigger instances is protected by `ledtrig_backlight_list_mutex`.

Control flow: Activation allocates notifier state, records current brightness and `UNBLANK`, then links it into the global list. The exported blank callback locks the list and updates each LED only when state changes. Inverting sysfs immediately recomputes current LED brightness.

State and persistence: Per-LED saved brightness and old blank status live until deactivation. No hardware state is persisted outside the LED class brightness setting.

Dependencies and integration: It integrates with LED triggers and any backlight/display path that calls the exported blank function.

Risks and test signals: Correctness depends on callers consistently reporting blank state. Saved brightness can be stale if the LED brightness changes while blanked. Test activation/deactivation under concurrent blank events, invert toggling, and exported symbol use from display code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-backlight.c -->
