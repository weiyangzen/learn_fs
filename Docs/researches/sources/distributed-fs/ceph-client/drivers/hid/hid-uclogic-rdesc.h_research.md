# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-rdesc.h

Purpose: declares UC-Logic fixed descriptor arrays, descriptor template arrays, original descriptor size constants, report IDs, placeholder IDs, and the template application API.

Important APIs, types, and functions: defines original descriptor sizes such as `UCLOGIC_RDESC_WPXXXXU_ORIG_SIZE`, `UCLOGIC_RDESC_WP5540U_V2_ORIG_SIZE`, and TWHL850/TWHA60 interface sizes. Declares fixed descriptor arrays and sizes for legacy tablets, placeholder heads and macros `UCLOGIC_RDESC_PEN_PH()` and `UCLOGIC_RDESC_FRAME_PH_BTN`, enum `uclogic_rdesc_ph_id`, v1/v2 report IDs, frame/touch/dial device ID offsets, UGEE v2 probe data, battery report ID, Ugee G5 frame constants, XP-PEN Artist descriptors, and `uclogic_rdesc_template_apply()`.

Control flow: none. The header defines constants and extern contracts that parameter discovery uses to select descriptor replacements and raw-event transforms.

State and persistence: no runtime state. It documents immutable descriptor symbols and caller-owned kmalloc results from template application.

Dependencies and integration: included by params, rdesc implementation, and rdesc KUnit tests. It includes `linux/usb.h` for fixed-width USB/HID types used in declarations.

Risks: constants couple tightly to report-byte offsets in `hid-uclogic-core.c` and model logic in `hid-uclogic-params.c`. Changing report IDs or offsets without updating raw-event handling will cause misrouted input. Original descriptor size guards must match real hardware descriptors.

Test signals: used by KUnit tests for template substitution and by compile-time linkage of all descriptor symbols. Real hardware remains the main validation for descriptor semantic correctness.
