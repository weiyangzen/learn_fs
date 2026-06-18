# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Inspiroy-2-S.bpf.c

## Purpose
This HID-BPF program fixes Huion Inspiroy 2 S USB tablet behavior across firmware mode and vendor/raw tablet mode. The device exposes separate vendor, pen, and pad HID descriptors; depending on mode, some nodes become silent and can create duplicate devices. The program rewrites descriptors so Linux sees usable pen and tablet-pad reports, disables duplicate firmware nodes when `HUION_FIRMWARE_ID` proves the tablet was switched by userspace, and normalizes vendor-mode reports into the fixed descriptors.

## Important APIs, Types, And Functions
The device match is declared with `HID_BPF_CONFIG(HID_DEVICE(BUS_USB, HID_GROUP_GENERIC, VID_HUION, PID_INSPIROY_2_S))`. The descriptor hook is `SEC(HID_BPF_RDESC_FIXUP) int BPF_PROG(hid_fix_rdesc, struct hid_bpf_ctx *hctx)`, using `hid_bpf_get_data()` and `__builtin_memcpy()` to replace descriptors. The event hook is `SEC(HID_BPF_DEVICE_EVENT) int BPF_PROG(inspiroy_2_fix_events, struct hid_bpf_ctx *hctx)`. `HID_BPF_OPS(inspiroy_2)` publishes both hooks, and `probe()` accepts only the three known descriptor lengths.

The file uses `hid_report_helpers.h` macros such as `UsagePage_Digitizers`, `ReportId`, `CollectionApplication`, and `FixedSizeVendorReport` to build replacement report descriptors. Key constants are `PAD_REPORT_DESCRIPTOR_LENGTH` 65, `PEN_REPORT_DESCRIPTOR_LENGTH` 93, `VENDOR_REPORT_DESCRIPTOR_LENGTH` 18, report IDs 3/10/8, and event lengths 8/10/12.

## Control Flow
`hid_fix_rdesc()` first checks the udev-provided `UDEV_PROP_HUION_FIRMWARE_ID` against prefix `HUION_T21j_`. For pad and pen descriptors, a matching firmware ID causes replacement with vendor-only disabled descriptors; otherwise the hook installs fixed pad or pen descriptors. The vendor descriptor is always replaced with a combined pen-plus-pad descriptor so raw mode can work even if the udev property is missing.

`inspiroy_2_fix_events()` reads up to 10 bytes. Firmware-mode pad report ID 3 keyboard shortcuts are mapped to a compact pad report: known key combinations become button numbers 1-6, Ctrl-minus/Ctrl-equals become wheel -1/+1, and the rewritten report is returned with length 6. Vendor-mode report ID 8 is split by bit tests in `data[1]`: pad subreports become report ID 3 with stored button state and relative wheel delta, while pen in-range subreports are mostly passed through with special handling to keep tip-down state stable when the secondary barrel/eraser button toggles.

## State And Persistence
Global BPF variables persist per loaded program: `last_button_state` remembers the last vendor-mode pad button bitmap for wheel-only reports; `last_tip_state`, `last_sec_barrel_state`, and `force_tip_down_count` preserve pen contact across transient firmware reports where changing the secondary barrel switch may briefly clear Tip Switch. There is no filesystem or map persistence.

## Dependencies And Integration Points
The program depends on Linux HID-BPF helper headers, vmlinux BTF types, the udev-hid-bpf property injection path, and userspace tools such as huion-switcher or DIGImend utilities that place the tablet in raw/vendor mode. It integrates at HID descriptor parse time and HID input-report time, before the normal HID/input stack creates evdev devices.

## Risks
The descriptor selection is length-based, so firmware revisions with changed descriptor sizes will be rejected or left unfixed. The firmware-ID prefix controls duplicate-node disabling; a missing or changed property can leave duplicate fixed nodes visible. The keyboard-shortcut-to-button mapping assumes a specific factory shortcut layout. The forced tip-down workaround is stateful and may hide unusual pen transitions if firmware behavior changes.

## Test Signals
Good signals are: probe accepts only descriptor sizes 18, 65, and 93; descriptor dumps show fixed pen physical units, removed bogus tilt/invert usages, and tablet-pad button/wheel usages; firmware-mode pad shortcuts emit buttons 1-6 and wheel deltas; raw-mode vendor reports emit a single pen report ID 8 and pad report ID 3; toggling the physical eraser/secondary barrel while tip is down does not create spurious tip-up events.
