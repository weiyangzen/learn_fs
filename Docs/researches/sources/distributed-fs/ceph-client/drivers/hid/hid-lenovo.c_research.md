# sources/distributed-fs/ceph-client/drivers/hid/hid-lenovo.c

## Purpose

`hid-lenovo.c` is the HID special-driver for IBM/Lenovo keyboards, TrackPoint devices, ScrollPoint mice, tablet keyboards, the ThinkPad Pro Dock, and one Lenovo Yoga Slim 7x I2C keyboard. It fixes malformed descriptors, maps vendor usages to Linux input keys, exposes device-specific sysfs controls, drives mute/micmute/Fn-lock LEDs, and sends vendor reports that put TrackPoint keyboards into useful native modes.

## Important APIs, Types, And Functions

The central private state is `struct lenovo_drvdata`, which stores LED report buffers and mutexes, two `led_classdev` objects, Fn-lock work, TrackPoint tuning fields, Compact keyboard sensitivity and middle-click state, and the owning `hid_device`. Driver entry points are collected in `lenovo_driver`: `lenovo_report_fixup()`, `lenovo_input_mapping()`, `lenovo_raw_event()`, `lenovo_event()`, `lenovo_probe()`, `lenovo_remove()`, `lenovo_input_configured()`, and `lenovo_reset_resume()`. Device-specific setup is split across `lenovo_probe_tpkbd()`, `lenovo_probe_cptkbd()`, and `lenovo_probe_tp10ubkbd()`. Sysfs handlers implement `fn_lock`, Compact keyboard `sensitivity` and `middleclick_workaround`, plus ThinkPad USB keyboard TrackPoint knobs `press_to_select`, `dragging`, `release_to_select`, `select_right`, `sensitivity`, and `press_speed`.

## Control Flow

HID core matches `lenovo_devices`, calls report fixup before parsing, then `lenovo_probe()` parses and starts HID hardware. Product id dispatch decides whether extra setup is needed. The ThinkPad USB keyboard path first relies on `lenovo_input_mapping_tpkbd()` marking the TrackPoint subdevice by temporarily setting drvdata to `1`; `lenovo_probe_tpkbd()` then validates feature/output reports, creates TrackPoint sysfs attributes, allocates real drvdata, registers mute LEDs, and sends report 4 settings. Compact USB/Bluetooth and TrackPoint II keyboards allocate drvdata on the mouse/native interface, set defaults, send vendor commands with `lenovo_features_set_cptkbd()`, and create sysfs controls. Tablet/Ultrabook keyboard setup searches output reports for application `0xffa00001`, allocates drvdata, initializes Fn-lock work and LED mutex, programs default Fn-lock state, creates sysfs, and registers LEDs.

Input mapping rewrites vendor usages into standard key codes for Compact keyboards, TrackPoint II keyboards, X1/X12 tablets, ThinkPad 10 Ultrabook keyboards, and ScrollPoint horizontal wheel reports. `lenovo_raw_event()` rewrites the Compact USB Fn-F12 report and synthesizes X12 tablet hotkey input events from raw report id 3. `lenovo_event()` tracks Fn-Esc toggles and implements the Compact middle-button workaround: a middle-button down followed by wheel movement becomes scrolling, while a down/up with no wheel movement emits a real middle click. Removal unregisters sysfs and LEDs per product and stops HID hardware. USB reset resume re-sends Compact keyboard configuration for USB mouse interfaces.

## State And Persistence Behavior

All runtime state is per-HID-device drvdata and is lost on unplug. Hardware state is explicitly programmed through feature/output reports: TrackPoint selection/sensitivity settings, Compact keyboard native middle-button mode and Fn-lock/sensitivity, and TP10/X1/X12 LED/Fn-lock output report 9. `fn_lock`, sensitivity, and TrackPoint tuning values persist only in kernel memory while the device is bound; the driver re-applies Compact settings on reset resume but does not persist user settings across rebinds. LED state is cached in `led_state`; TP10-style LED output uses `led_report_mutex` because one shared 3-byte output buffer is reused. Fn-lock LED sync for TP10-style devices is deferred through `fn_lock_sync_work`.

## Dependencies And Integration Points

The file integrates with HID parsing/mapping, Linux input events, sysfs attribute groups, LED class triggers `audio-mute` and `audio-micmute`, workqueues, mutexes, USB/Bluetooth/I2C HID ids from `hid-ids.h`, and PM reset-resume through `pm_ptr()`. It intentionally binds only selected generic HID groups for tablet keyboards so other drivers such as `hid-multitouch` can handle touchpad/TrackPoint portions.

## Risks And Test Signals

Risks are concentrated around fixed descriptor offsets and product-specific report assumptions: bad firmware revisions could make report fixups corrupt descriptors, missing reports return `-ENODEV`, and raw-event casts require sufficiently sized reports. The Compact keyboard sysfs setters call `lenovo_features_set_cptkbd()` without rolling back partial vendor-command failures, so user-visible state can diverge from hardware. Test signals include successful HID probe for each id, expected evtest key codes for Fn hotkeys, no duplicate wheel/middle events, functional TrackPoint sysfs writes, LED class brightness changes, X12 raw hotkey synthesis, reset-resume reconfiguration, and clean unbind with no pending work or LED leaks.
