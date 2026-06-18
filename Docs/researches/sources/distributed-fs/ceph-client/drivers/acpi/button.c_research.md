# sources/distributed-fs/ceph-client/drivers/acpi/button.c

## Purpose
Implements the ACPI power button, sleep button, and lid switch driver. It converts fixed ACPI button events and ACPI device notifications into Linux input events, exposes legacy lid state through procfs, handles wakeup signaling, and works around platforms with unreliable lid state reporting.

## Important APIs, Types, And Functions
`struct acpi_button` holds the ACPI companion, platform device, button type, input device, physical path string, press count, lid state tracking, suspend flag, and lid initialization flag. The driver matches lid, sleep, sleep fixed, power, and power fixed ACPI HIDs.

Lid state helpers are `acpi_lid_evaluate_state()` for `_LID`, `acpi_lid_notify_state()` for SW_LID input events and firmware workaround logic, `acpi_lid_update_state()`, and `acpi_lid_initialize_state()`. Exported `acpi_lid_open()` lets graphics and platform drivers query the current lid state.

Notification handlers are `acpi_lid_notify()` for lid status events, `acpi_button_notify()` for power/sleep key events, and `acpi_button_event()` for fixed ACPI events. Procfs helpers create `/proc/acpi/button/lid/<BID>/state`. Module parameters are `lid_report_interval` and `lid_init_state`.

## Control Flow
Module init chooses `lid_init_state` from the explicit module parameter, DMI quirks, or default method-based initialization. It returns success without registering the platform driver when ACPI is disabled so modules linked against `acpi_lid_open()` can still load.

Probe identifies the button type from HID, rejects lid devices disabled by quirks, allocates state and an input device, creates legacy procfs state for lids, sets input capabilities (`KEY_POWER`, `KEY_WAKEUP`, `KEY_SLEEP`, or `SW_LID`), registers the input device, enables wakeup, then installs either a fixed event handler or an ACPI notify handler. Lid input open and resume initialize the switch state. Remove unregisters the corresponding ACPI event handler, waits for ACPI events to drain, disables wakeup, removes procfs, unregisters input, and frees state.

Button notifications generate PM wakeup events. While suspended, or for explicit wake notifications, they do not emit key presses. Normal power/sleep notifications synthesize key press/release pairs and generate ACPI netlink events. Lid notifications ignore events until initialization completes, evaluate `_LID`, optionally wake the system on open, and update SW_LID with workaround logic for platforms that miss open events or report bad initial state.

## State And Persistence
Global state includes `lid_device`, `lid_init_state`, `acpi_button_dir`, and `acpi_lid_dir`. Per-button state tracks `last_state`, `last_time`, `pushed`, `suspended`, and `lid_state_initialized`. Procfs nodes and input devices persist while the driver is bound. There is no on-disk state.

## Dependencies And Integration Points
Depends on ACPI fixed events and device notifications, platform-device ACPI matching, the input subsystem, procfs, DMI, PM wakeup helpers, and ACPI netlink event generation. `acpi_lid_open()` is an exported integration point for display drivers and platform code that need lid state.

## Risks
Lid firmware is historically unreliable. The complement-event logic avoids lost close events but can create surprising event sequences if applied to a reliable machine, so DMI and module-parameter behavior matter. The code assumes at most one meaningful lid procfs directory and reports an error on multiple lids. Fixed event and notify handler removal must match the handler type installed at probe. Input events are suppressed during suspend to avoid duplicate wake and key events.

## Test Signals
Signals include correct `/dev/input` events for power/sleep/lid, correct `/proc/acpi/button/lid/*/state`, wake events on button/lid activity, no key press on wake-only notifications, correct behavior after suspend/resume, and DMI quirk behavior on listed machines. Regression testing should include fixed-button devices, normal notify devices, disabled lid quirk systems, and unreliable `_LID` transitions.
