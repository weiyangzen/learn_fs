## sources/distributed-fs/ceph-client/drivers/platform/x86/fujitsu-tablet.c

Purpose: supports older Fujitsu tablet PC hardware exposing ACPI IDs `FUJ02BD` or `FUJ02BF`. It uses ACPI resources to obtain an I/O port range and IRQ, then reports tablet buttons plus dock/tablet-mode switches through the input subsystem.

Important APIs/types/functions: global `fujitsu` holds input device, DMI-selected `struct fujitsu_config`, previous keymask, IRQ, and I/O range. Low-level helpers `fujitsu_ack()`, `fujitsu_status()`, and `fujitsu_read_register()` access controller ports. `fujitsu_send_state()` reads register `0xdd` and reports `SW_DOCK` and `SW_TABLET_MODE` with DMI quirks. `fujitsu_interrupt()` checks interrupt status, sends switch state, reads keymask registers `0xde/0xdf`, computes changed bits, emits MSC scan and key events, then acknowledges. DMI callbacks select keymaps and invert/force switch quirks.

Control flow: module init applies DMI keymap/quirk selection and registers the ACPI platform driver. Probe walks `_CRS` resources for IRQ and I/O, sets ACPI name/class, registers input, reserves I/O region, resets controller, and requests shared IRQ. Remove frees IRQ, releases I/O region, and unregisters input. Resume resets controller and resends state.

State and persistence: runtime state is global and single-device. `prev_keymask` tracks pressed buttons. Hardware state is read from I/O registers and acknowledged; no persistent firmware settings are changed.

Dependencies and integration: ACPI resource walking, raw port I/O, IRQ handling, DMI matching, input key/switch events, platform driver PM.

Risks: raw I/O and shared IRQ require exact resource parsing. The default catch-all DMI entry may apply generic Lifebook mapping to unknown systems. Switch-state quirks are model-sensitive. Test signals include resource parse failures, request-region conflicts, shared IRQ behavior, key press/release transitions, dock/tablet switch inversion, resume reset, and unknown hardware with fallback keymap.
