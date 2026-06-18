# sources/distributed-fs/ceph-client/drivers/hid/hid-cougar.c

Purpose: supports Cougar 500k/700k gaming keyboards whose programmable keys arrive on a separate vendor HID interface, translating those vendor reports into key events on the real keyboard input device.

Important APIs/types/functions: `cougar_mapping` maps vendor key codes to `KEY_F13..KEY_F17`, `KEY_SPACE` or `KEY_F18` for G6, and `KEY_SCREENLOCK`. Module parameter `g6_is_space` controls G6 mapping through custom param ops. `struct cougar_shared` stores shared per-physical-device state: kref, enabled flag, keyboard HID device, and input device pointer. `struct cougar` stores per-interface state and a pointer to shared state. `cougar_report_fixup()` clamps an excessive usage count to `HID_MAX_USAGES - 1`. `cougar_bind_shared_data()` links multiple HID interfaces from the same physical device using `hid_compare_device_paths()`. `cougar_raw_event()` decodes vendor reports and injects input events.

Control flow: probe parses the interface. If the top-level collection is the vendor usage, it starts HIDRAW only and opens the interface for raw events; otherwise it starts normal HID. Shared state is created or reused under a global mutex and released through devm action/kref. The keyboard interface records its registered input device and enables shared event injection. The vendor interface preinitializes the G6 mapping and opens HID. Raw events from the vendor interface are blocked from further processing and, when mapped, reported to the shared keyboard input device.

State/persistence: shared state persists until all interfaces for the physical device release their references. `enabled` prevents vendor-interface injection after keyboard removal. The G6 mapping is global and can be changed at runtime through the module parameter.

Dependencies/integration: depends on HID core, HIDRAW, input event injection, device physical path comparison, krefs, mutex-protected global list management, and Solid Year/Cougar USB IDs.

Risks: multi-interface ordering is delicate: the vendor interface may receive reports before the keyboard input pointer is available, returning `-EPERM`. `hid_compare_device_paths()` requires valid physical paths containing the separator. The raw report parser indexes fixed bytes without size checks in `cougar_raw_event()`, relying on device report shape. Shared-state list/kref logic must avoid leaks and stale input pointers.

Test signals: test both keyboard and vendor interfaces probing in either order, G1-G6 and lock key translation, `g6_is_space` runtime changes, unmapped-key warnings only on press, remove of either interface while the other remains, descriptor usage-count fixup, and no injected events after `enabled` is cleared.
