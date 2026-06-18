# sources/distributed-fs/ceph-client/drivers/hid/hid-haptic.h

Declares shared HID haptic data structures and helper APIs for HID touchpad drivers, with no-op stubs when `CONFIG_HID_HAPTIC` is disabled.

`struct hid_haptic_effect` stores a report buffer, input device, work item, and control-list fields. `struct hid_haptic_device` stores input/HID pointers, auto/manual trigger reports and mutexes, workqueue, manual report length, pressure and force calibration fields, mode, default trigger, vendor metadata, waveform/duration maps, press/release ordinals, effect array, and stop effect. Constants define waveform none/stop ordinals and device/host modes.

Including drivers allocate or embed `struct hid_haptic_device`, pass it through mapping hooks during parsing, and call `hid_haptic_init()` after input setup. Disabled-config stubs compile callers while returning neutral behavior.

State is runtime-only and owned by the haptic implementation and associated HID/input lifetime. Dependencies are `<linux/hid.h>`, input/workqueue types, `IS_ENABLED(CONFIG_HID_HAPTIC)`, and exported symbols from `hid-haptic.c`.

Risks include declared helpers that are not visibly implemented in this source set, plus API asymmetry between enabled prototypes and disabled stubs. Test signals are build coverage in enabled/disabled configs, caller compilation, structure lifetime review, and unresolved-symbol checks.
