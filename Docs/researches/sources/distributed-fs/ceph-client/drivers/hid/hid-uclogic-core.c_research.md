# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-core.c

Purpose: main HID driver for UC-Logic, Huion, UGEE, XP-PEN, Trust, and related tablets whose descriptors or raw reports require correction. It orchestrates parameter discovery, descriptor replacement, input-device naming, raw-event normalization, in-range emulation, and cleanup.

Important APIs, types, and functions: `uclogic_probe()` sets `HID_QUIRK_MULTI_INPUT` and `HID_QUIRK_HIDINPUT_FORCE`, allocates `struct uclogic_drvdata`, initializes timer/rotary state, calls `uclogic_params_init()`, generates a replacement descriptor with `uclogic_params_get_desc()`, parses, and starts HID. `uclogic_report_fixup()` returns the generated descriptor. `uclogic_input_mapping()` remaps keypad frame buttons through `uclogic_extra_input_mapping[]` and can discard invalid pen usages. `uclogic_input_configured()` names input devices by report ID/application and clears `EV_MSC` for touch controls. `uclogic_raw_event()` dispatches input reports through event hooks, pen subreport remapping, pen tweaks, and frame tweaks.

Control flow: probe builds declarative parameters before HID parsing so report fixup can supply corrected descriptors. Runtime raw events first check hook patterns, then possibly convert pen subreports into synthetic report IDs, then mutate pen or frame report bytes in place. Resume re-runs parameter initialization only to re-enable hardware state, discarding the temporary parameters.

State and persistence: `uclogic_drvdata` holds parameters, generated descriptor memory, pen input pointer, in-range timer, rotary encoder previous state, and match-table quirks. The in-range timer synthesizes pen-up events for hardware without out-of-range reporting. No persistent storage exists.

Dependencies and integration: depends on HID core, input core, timers, usbhid, `hid-uclogic-params.h`, and `hid-ids.h`. The device table supplies model quirks for selected UGEE tablets.

Risks: report mutation is offset-sensitive and assumes sizes checked before access. Timer-driven pen-up needs `timer_delete_sync()` on remove. Event hooks schedule work from raw-event context and rely on parameter cleanup to cancel. Generated descriptor lifetime must outlive HID parsing and runtime use.

Test signals: includes `hid-uclogic-core-test.c` under `CONFIG_HID_KUNIT_TEST`. Hardware tests should cover multi-input naming, pen in-range emulation, frame dial/touch transforms, resume, and disconnect while hooks/timers are active.
