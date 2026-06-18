# sources/distributed-fs/ceph-client/drivers/platform/chrome/chromeos_tbmc.c

Purpose: ACPI tablet-mode switch driver for ChromeOS convertibles exposing GOOG0006 and method `TBMC`.

Important APIs, types, and functions: `chromeos_tbmc_query_switch()` evaluates ACPI integer method `TBMC` and reports `SW_TABLET_MODE`. `chromeos_tbmc_notify()` handles ACPI notify event `0x80`. `chromeos_tbmc_open()` reports current state when the input device is opened. `chromeos_tbmc_resume()` refreshes state after resume.

Control flow: probe allocates an input device named `Tablet Mode Switch`, sets ACPI HID as phys path, registers `SW_TABLET_MODE`, enables device wakeup, and installs an ACPI notify handler. Notifications trigger wakeup accounting and state refresh. Remove unregisters the notify handler and disables wakeup.

State and persistence: tablet mode state is read from firmware on demand. The input subsystem stores last reported switch state. No writable state.

Dependencies and integration points: ACPI platform device `GOOG0006`, input subsystem, PM wakeup framework. Firmware event is described as EC host mode-change propagated through ACPI.

Risks and edge cases: only notify `0x80` is recognized; other events log errors. ACPI method failure returns `-ENODEV` but notifications remain installed. The raw integer from firmware is reported as switch state without normalization.

Test signals: verify initial/open/resume state reports, ACPI notify changes, wakeup behavior, and removal cleans up notify handler.
