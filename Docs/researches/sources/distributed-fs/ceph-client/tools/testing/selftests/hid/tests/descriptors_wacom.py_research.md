# sources/distributed-fs/ceph-client/tools/testing/selftests/hid/tests/descriptors_wacom.py

## Purpose
`descriptors_wacom.py` is a data module containing raw HID report descriptors for Wacom tablet models and firmware variants. The descriptors are used by Wacom-oriented HID tests to emulate real devices with realistic pen, pad, touch, feature, and vendor report layouts.

## Important APIs, types, and functions
The module defines large byte-list constants: `wacom_pth660_v145`, `wacom_pth660_v150`, `wacom_pth860_v145`, `wacom_pth860_v150`, and `wacom_pth460_v105`. The v150 variants are shallow copies of the v145 descriptors with one report-count byte changed for report ID 20. There are no functions or classes.

## Control flow
There is no runtime control flow except list construction at import time and the two copy-plus-mutate operations. Descriptor comments document HID item meaning, report IDs, usage pages, units, report counts, and known errata such as missing physical maxima.

## State and persistence
The descriptor lists are module globals. Because v150 variants are copied before mutation, they do not alter their v145 source lists. Consumers should treat these lists as read-only; accidental mutation would affect later tests within the same Python process.

## Dependencies and integration points
The file has no imports. It integrates by being imported into Wacom tests, where the byte lists feed hidtools report descriptor parsing and UHID device creation.

## Risks and test signals
Risks include descriptor byte drift from actual hardware, accidental mutation of globals, and very large hand-maintained arrays where offset edits are brittle. Test signals appear indirectly: Wacom tests should create the right evdev devices, expose expected capabilities, and exercise feature/report handling for each model variant.
