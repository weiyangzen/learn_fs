# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-rbtn.c

Purpose: Dell airplane-mode switch driver for ACPI `DELRBTN`/`DELLABCE`, exposing sliders as rfkill and toggles as input hotkeys, with notifier hooks for Dell laptop integration.

Important APIs/types/functions: ACPI methods `CRBT`, `GRBT`, `ARBT`; `struct rbtn_data`; rfkill/input setup; ACPI notify handler; exported `dell_rbtn_notifier_register()` and unregister.

Control flow/state/persistence: Probe acquires ACPI events, determines toggle vs slider, registers input or rfkill, and installs notify handler. Event `0x80` reports `KEY_RFKILL` or updates rfkill and notifiers. Suspend suppresses a possible spurious resume notification. `auto_remove_rfkill` lets notifier consumers avoid duplicate rfkill devices.

Dependencies/integration: ACPI, rfkill, input, platform driver, PM sleep, and `dell-laptop.c`.

Risks/test signals: Resume filtering and auto-remove behavior are subtle. Test slider/toggle devices, notifier registration, rfkill hard state, suspend/resume, and modular/built-in combinations.
