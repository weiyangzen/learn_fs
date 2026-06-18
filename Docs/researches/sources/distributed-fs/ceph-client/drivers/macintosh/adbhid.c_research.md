<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adbhid.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/adbhid.c

Purpose: `adbhid.c` translates Apple Desktop Bus keyboards, mice, trackpads, trackballs, and miscellaneous buttons into Linux input devices. It also programs keyboard LEDs and performs device-specific handler/init sequences.

Important APIs, types, and state: `struct adbhid` stores the input device, ADB id/default/original/current handler IDs, mouse kind, keycode table, names, and flags for Fn/power/caps-lock translation. Global `adbhid[16]` indexes active ADB devices. The ADB notifier `adbhid_adb_notifier` reacts to pre-reset, powerdown, and post-reset events. Input handlers are `adbhid_keyboard_input()`, `adbhid_mouse_input()`, and `adbhid_buttons_input()`. `adbhid_kbd_event()` sends keyboard LED updates back to ADB hardware.

Control flow: Module init gates unsupported machines, marks LED request complete, probes ADB devices, then registers the ADB notifier. `adbhid_probe()` registers ADB handlers for mouse, keyboard, and misc devices, configures keyboard LEDs/handler IDs, identifies and initializes mouse variants through handler changes and register reads, registers or reregisters Linux input devices, and cleans up devices no longer present. Keyboard input validates register 0 packets and reports translated key events, including special caps-lock, Fn-delete, and power-key handling. Mouse input normalizes multiple ADB mouse protocols into BTN_LEFT/MIDDLE/RIGHT and REL_X/Y reports. Misc button input maps audio, eject, brightness, video, and keyboard illumination buttons.

State and persistence: Device state persists in `adbhid[]` until a reset cleanup removes absent devices. Keyboard LED requests are serialized with `leds_lock`, a single global `led_request`, per-device pending LED values, and a ring of pending devices. Caps-lock translation state survives suspend enough to ignore a spurious resume event.

Dependencies and integration: It depends on the ADB core registration/notification API, Linux input core, PMU/CUDA headers, optional PowerMac backlight helpers, and ADB request primitives for handler changes and register writes.

Risks and test signals: The protocol matrix is large and hardware-specific. LED request queuing uses static state and should be stress-tested with rapid LED changes. `adbhid_exit()` is empty, so practical unloading support is limited. Test keyboard type mappings, ISO key swap, caps-lock modes, Fn/delete and Fn/command power translations, all mouse handler fallbacks, reset/powerdown notifier behavior, and input device cleanup after bus topology changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adbhid.c -->
