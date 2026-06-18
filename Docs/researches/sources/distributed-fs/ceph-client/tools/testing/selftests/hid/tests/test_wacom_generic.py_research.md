# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/test_wacom_generic.py

Purpose: this pytest module tests the Wacom driver's generic HID code path, meaning Wacom-like devices decoded from descriptors rather than explicit device-table handling. It covers pen naming, physical units/ranges, pointer-vs-direct properties, side switches, heartbeat reports, pad/touch-ring reports, and multitouch confidence handling.

Important APIs, types, and functions: `KERNEL_MODULE` requests the `wacom` module. `ProximityState.fill()` maps out/proximity/range into `inrange` and `wacomsense` report bits. `Buttons` and `ToolID` are `attrs` value objects that fill report fields for side switches and serial/tool IDs. `PhysRange.contains()` validates descriptor unit/range metadata. `BaseTablet` extends `base.UHIDTestDevice` and implements `create_report()`, `event()`, heartbeat and pad report creation, Wacom-specific evdev node matching, and feature-report offset generation. `OpaqueTablet`, `OpaqueCTLTablet`, and `PTHX60_Pen` are descriptor-backed device models. Test classes layer reusable assertions through `BaseTest.TestTablet`, `PenTabletTest`, `TouchTabletTest`, and `DirectTabletTest`.

Control flow: each test constructs a synthetic UHID device, sends reports through `call_input_event()`, then compares evdev output using `sync_and_assert_events()`. Descriptor physical validation iterates parsed input/feature/output reports and checks required usages against unit/range expectations. `TestPTHX60_Pen` parametrizes real PTH descriptor variants, xfails known physical-range errata, checks heartbeat reports for no events, and verifies pad ring/key events. `TestDTH2452Tablet` extends multitouch helpers and replays timelines for contact ID 0, confidence false, confidence loss, and confidence gain.

State and persistence: `BaseTablet` stores current `buttons`, `toolid`, `proximity`, pad ring/key state, and feature offset. Multitouch assertions inspect evdev slot state, but no data persists beyond the test process and kernel input state.

Dependencies and integration points: depends on `descriptors_wacom`, `hidtools.hut.HUT`, `hidtools.hid.HidUnit`, pytest, attrs, libevdev, the local UHID base, and `test_multitouch`. It integrates directly with the kernel Wacom driver and evdev node naming conventions.

Risks: inline descriptors are large and brittle; exact evdev names/properties may change with driver naming updates; physical range expectations intentionally xfail on known errata for PTH devices; confidence timelines assume stable slot allocation semantics. Because helper state is sticky, omitted fields in a report mean unchanged state rather than cleared state.

Test signals: expected signals include evdev key/ABS/MSC events, no spurious heartbeat sync, correct `INPUT_PROP_POINTER`/`INPUT_PROP_DIRECT`, valid descriptor unit metadata, expected pad `ABS_WHEEL` rotation, and correct multitouch tracking IDs/slot release when confidence changes.
