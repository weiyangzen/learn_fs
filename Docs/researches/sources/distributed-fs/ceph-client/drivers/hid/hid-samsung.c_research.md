# sources/distributed-fs/ceph-client/drivers/hid/hid-samsung.c

Purpose: supports several Samsung special HID devices, mainly the USB Samsung IrDA remote and Samsung wireless keyboard, keyboard/mouse, gamepad, action mouse, universal keyboard, and multi-HOGP keyboard devices. It corrects malformed descriptors and remaps nonstandard consumer/keyboard/button usages to Linux input codes.

Important APIs/types/functions: descriptor handling is split into `samsung_report_fixup()` and `samsung_irda_report_fixup()`. Input mapping helpers are `samsung_kbd_mouse_input_mapping`, `samsung_kbd_input_mapping`, `samsung_gamepad_input_mapping`, `samsung_actionmouse_input_mapping`, and `samsung_universal_kbd_input_mapping`; `samsung_input_mapping()` dispatches by product ID. `samsung_probe()` handles parse/start and special IrDA connection masks.

Control flow: report fixup only applies to the USB IrDA remote. Four descriptor variants are recognized by size and byte pattern: 184-byte vendor report reinterpretation, 203-byte report logical range fix, 135-byte logical range fix, and 171-byte logical range fix. Input mapping checks usage pages and product IDs, then maps selected consumer usages to media/browser/system keys, keyboard usages to corrected layout keys with repeat enabled, gamepad buttons to `BTN_*`, and vendor-ish Samsung hotkeys to `BTN_TRIGGER_HAPPY*` or explicit key codes. Probe parses the descriptor; for the 184-byte IrDA variant it disables hidinput and forces hiddev because userspace must reconstruct the vendor report.

State and persistence: no private per-device state is allocated. State consists of in-memory descriptor mutations and input mapping decisions made during HID input setup. The only persistent behavioral switch is `cmask` in probe for the IrDA 184-byte variant.

Dependencies/integration: depends on HID core, USB interface inspection for keyboard/mouse interface number, Linux input key namespaces, hiddev force connection for old IrDA userspace, and product IDs in `hid-ids.h`.

Risks: mappings encode device-specific usage values and may conflict if Samsung reuses product IDs with different descriptors. Some mappings use raw numeric key codes where no named key exists, increasing ABI-readability risk. IrDA fixups are byte-offset-specific; bad guards could corrupt descriptors, while overly narrow guards leave devices broken. The USB keyboard/mouse mapping reads the USB interface, so it is intentionally USB-only.

Test signals: descriptor dump for each IrDA size should show adjusted logical ranges or vendor report shape; wireless keyboard media/browser/hotkeys should produce expected Linux keys; gamepad buttons and consumer Back/Home/Menu should map correctly; action mouse usage `0x301` should map; Bluetooth universal and multi-HOGP keyboard brightness, Dex, screen capture, and hotkey usages should be visible.
