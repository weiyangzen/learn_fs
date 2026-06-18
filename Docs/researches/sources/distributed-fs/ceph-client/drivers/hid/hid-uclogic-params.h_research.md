# sources/distributed-fs/ceph-client/drivers/hid/hid-uclogic-params.h

Purpose: declares the UC-Logic parameter model shared by the core driver and parameter discovery implementation.

Important APIs, types, and functions: defines quirk bits `UCLOGIC_MOUSE_FRAME_QUIRK` and `UCLOGIC_BATTERY_QUIRK`; enums for pen in-range behavior and frame type; `struct uclogic_params_pen_subreport` for subreport-to-report-ID rewriting; `struct uclogic_params_pen` for pen descriptor, report ID, subreports, in-range mode, fragmented high-resolution coordinate flags, and tilt correction; `struct uclogic_params_frame` for frame descriptor, report ID, input suffix, rotary encoder, Wacom-compatible device ID byte, touch controls, and bitmap dial transforms; `struct uclogic_raw_event_hook` for raw-event-triggered work; `struct uclogic_params` for whole-interface validity, common descriptor, pen, frame list, and hooks; and `struct uclogic_drvdata` for runtime core state.

Control flow: the header itself has no control flow, but its structures define the contract: parameter discovery fills declarative fields, the core concatenates descriptor parts and applies report-time transformations based on those fields.

State and persistence: describes ownership expectations for kmalloc descriptor pointers and event-hook lists. `uclogic_drvdata` persists for the HID device lifetime and includes transient timer, pen input pointer, rotary state, and quirks.

Dependencies and integration: includes USB, HID, and list headers. Exports `uclogic_params_init()`, `uclogic_params_get_desc()`, `uclogic_params_cleanup()`, and `uclogic_params_hid_dbg()` to `hid-uclogic-core.c`.

Risks: because fields are offset and report-ID sensitive, comments are part of the safety contract. Zero-filled structures are defined as noop, so future fields should preserve that invariant. Ownership mistakes around `desc_ptr` and `event_hooks` can cause leaks or use-after-free.

Test signals: exercised indirectly by UC-Logic KUnit suites and by all UC-Logic hardware paths. ABI is internal to this driver, not userspace.
