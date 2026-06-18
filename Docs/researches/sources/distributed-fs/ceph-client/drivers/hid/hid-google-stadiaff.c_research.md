# sources/distributed-fs/ceph-client/drivers/hid/hid-google-stadiaff.c

Adds rumble support for Google Stadia controllers over USB and Bluetooth. It registers a memless force-feedback device and sends strong/weak magnitudes through output report ID 5.

`struct stadiaff_device` stores HID/report pointers, a spinlock, removal flag, cached magnitudes, and a work item. `stadiaff_init()` validates output report ID `STADIA_FF_REPORT_ID`, allocates state, sets `FF_RUMBLE`, creates memless FF, and initializes work. `stadiaff_play()` records magnitudes and schedules work. `stadiaff_work()` writes report field values and calls `hid_hw_request()`. Remove sets `removed`, cancels work, and stops HID.

Playback is asynchronous so HID requests are not sent from the spinlocked callback. State is volatile and device-managed; the latest magnitudes persist only until sent or overwritten. Dependencies include HID core, input FF memless support, workqueues, spinlocks, and Google Stadia IDs from `hid-ids.h`.

Risks include assuming the validated report layout remains stable and not surfacing `hid_hw_request()` failures to userspace. Test signals include USB/Bluetooth matching, `FF_RUMBLE` exposure, value delivery to the output report, rapid playback changes, removal during active rumble, and missing report ID behavior.
