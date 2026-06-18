# sources/distributed-fs/ceph-client/drivers/hid/hid-gfrm.c

Supports Google Fiber TV Box Bluetooth remote controls. It adds GFRM100-specific key mappings, synthesizes missing search-key reports, and enables software autorepeat.

Driver data distinguishes `GFRM100` and `GFRM200`. `gfrm_input_mapping()` remaps selected GFRM100 consumer usages to `KEY_INFO` and `KEY_OK`. `gfrm_raw_event()` intercepts report ID `0xf7`, converts search-key down/up states into Consumer Search reports with `hid_report_raw_event()`, and ignores audio payload reports. `gfrm_input_configured()` enables autorepeat. `gfrm_probe()` registers the missing GFRM100 report before `hid_hw_start()`.

State is limited to the model value stored in HID driver data. There is no persistent storage. Dependencies are Bluetooth HID matching, HID input mapping/raw-event hooks, input key codes, and HID report registration.

Risks include hard-coded GFRM100 report format, consuming original reports by returning `-1`, and intentional dropping of audio data. Test signals include GFRM100/GFRM200 pairing, info/OK mapping, search down/up with intervening audio data, repeat timings, and report-registration failure handling.
