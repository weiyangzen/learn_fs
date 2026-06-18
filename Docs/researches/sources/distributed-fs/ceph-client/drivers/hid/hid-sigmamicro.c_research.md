# sources/distributed-fs/ceph-client/drivers/hid/hid-sigmamicro.c

Purpose: fixes a SiGma Micro keyboard descriptor whose report ID 4 describes keyboard bits incorrectly. The driver recognizes a complete known descriptor and changes one input item to variable semantics.

Important APIs/types/functions: `sm_0059_rdesc` is the expected descriptor template. `sm_report_fixup()` compares the live descriptor against the template and patches byte 99. `sm_driver` registers only the report-fixup callback for `USB_DEVICE_ID_SIGMA_MICRO_KEYBOARD2`.

Control flow: HID core invokes `sm_report_fixup()` before parsing. If size and full descriptor contents match `sm_0059_rdesc`, the driver logs a fixup and sets `rdesc[99] = 0x02`, changing the modifier report input from array to variable. If not, it returns the descriptor untouched. No custom probe, input mapping, or runtime callbacks exist.

State and persistence: no per-device allocation or persistent state. The descriptor patch is in-memory and per device instance.

Dependencies/integration: depends on HID descriptor parsing and `hid-ids.h` SiGma Micro IDs. The complete descriptor table doubles as both documentation and a strict guard.

Risks: full-descriptor matching avoids false positives but may miss devices with harmless descriptor differences. The byte index is meaningful only for the exact template. There is no runtime validation beyond whether HID input behaves correctly after parsing.

Test signals: affected keyboards should emit independent key bit events for report ID 4; descriptor mismatch variants should still bind without modification; no extra input devices or sysfs artifacts should appear.
