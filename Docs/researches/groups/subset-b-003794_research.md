# Research: subset-b-003794

Grouped code research for Linux HID-BPF programs under `sources/distributed-fs/ceph-client/drivers/hid/bpf/progs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Inspiroy-2-S.bpf.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Inspiroy-2-S.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas-Pro-19.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas-Pro-19.bpf.c

## Purpose
This program fixes Huion Kamvas Pro 19 and Kamvas Pro 27 pen-display descriptors and reports. It corrects the second stylus button usage from Secondary Tip Switch to Secondary Barrel Switch, creates an extra button usage for the third stylus button, and disambiguates the firmware's use of the Invert bit between eraser mode and the third button.

## Important APIs, Types, And Functions
The match table targets USB multitouch Win8 devices for PIDs `0x006B` and `0x006c`. `fixed_rdesc[]` is a full replacement descriptor for the pen, touch, feature, and newer firmware mouse/touchpad/vendor collections. `hid_fix_rdesc_huion_kamvas_pro_19()` handles descriptor replacement. `kamvas_pro_19_fix_3rd_button()` rewrites incoming report ID `0x0a` pen reports. `probe()` verifies descriptor sizes, confirms the original Secondary Tip Switch byte is still present at offset 17, and checks the HID device name against `HUION Huion Tablet_GT1902` or `HUION Huion Tablet_GT2701`, with `uhid test ` stripped for test devices.

## Control Flow
Descriptor fixup accepts old size 328 and newer firmware size 438. For size 438 it copies all of `fixed_rdesc`; for the older descriptor it copies only `PRE_240524_RDESC_FIXED_SIZE` bytes, preserving a descriptor length appropriate to the old firmware. Event fixup ignores non-pen reports, marks an out-of-range report by clearing `in_eraser_mode`, treats a subsequent Invert/Eraser state after out-of-range as real eraser mode, and otherwise copies the Invert bit into the inserted third-button bit position before clearing Invert.

## State And Persistence
Two booleans persist in BPF data: `prev_was_out_of_range` and `in_eraser_mode`. They encode proximity history so the event hook can decide whether an Invert bit means eraser entry or stylus button 3. There is no external persistence.

## Dependencies And Integration Points
The file depends on HID-BPF helpers and on stable Huion names and descriptor layouts. It integrates with the HID multitouch group, preserving touch report sections while modifying stylus semantics. The `hid_bpf_allocate_context()` call in `probe()` is used only to inspect the HID device name.

## Risks
Name matching and byte-offset checks prevent accidental binding, but they also make the quirk sensitive to firmware or kernel naming changes. The eraser/button heuristic assumes an out-of-proximity event precedes real eraser mode. If a future pen reports eraser/Invert differently, the third-button rewrite could suppress legitimate eraser state.

## Test Signals
Tests should include old and 240524+ firmware descriptor sizes, both GT1902 and GT2701 names, and a negative test where offset 17 is no longer Secondary Tip Switch. Runtime traces should verify button 2 maps to BTN_STYLUS2, button 3 maps through the inserted button usage, normal eraser transitions after out-of-range remain untouched, and simple third-button presses do not leave Invert set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas-Pro-19.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas13Gen3.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas13Gen3.bpf.c

## Purpose
This program supports the Huion Kamvas 13 Gen 3 by preferring vendor/raw mode, where wheel identity and wheel buttons are distinguishable. It replaces the vendor descriptor with a meaningful pen and custom tablet-pad descriptor, disables unused firmware-mode tablet and wheel nodes when a matching firmware property indicates raw mode, and rewrites vendor reports into standard input reports.

## Important APIs, Types, And Functions
The match uses `VID_HUION` `0x256c`, PID `0x2008`, and `HID_GROUP_ANY`. Descriptor lengths are 36 for vendor, 368 for tablet, and 108 for wheel. `fixed_rdesc_vendor[]` describes report ID 8 pen data and custom report ID 9 pad data. `hid_fix_rdesc_huion_kamvas13_gen3()` performs descriptor replacement/disablement. `hid_fix_event_huion_kamvas13_gen3()` handles vendor report subtypes: pen `0x08`, pen out `0x00`, buttons `0x0e`, and wheels `0x0f`.

## Control Flow
The descriptor hook checks `UDEV_PROP_HUION_FIRMWARE_ID` for prefix `HUION_M22c_`. If present, tablet and wheel descriptors are replaced with fixed-size vendor descriptors so silent duplicate firmware nodes do not produce input devices. The vendor descriptor is always expanded into fixed pen and pad collections. In the event hook, non-14-byte or non-report-ID-8 events are ignored. Pen reports have Y tilt inverted in place. Button and wheel reports are rewritten into the packed custom pad report: subtype `0x0f` maps `data[3]` to top or bottom wheel and `data[5]` from 1/2 to signed +1/-1; subtype `0x0e` updates `last_button_state` only on clean transitions, filtering ambiguous multi-button holds.

## State And Persistence
`last_button_state` persists the most recent accepted pad-button bitmap so wheel-only reports still include current button state and ambiguous non-release events can be ignored while a button is held. No BPF maps or external persistence are used.

## Dependencies And Integration Points
The file depends on HID-BPF helper macros and udev-hid-bpf firmware properties populated by raw-mode switching tools. It integrates with the input stack by presenting the vendor endpoint as a digitizer pen plus tablet function keys, including two relative axes: generic wheel and Consumer AC Pan for the bottom wheel.

## Risks
The implementation intentionally focuses on vendor mode and does not fully repair firmware-mode wheel ambiguity. The author notes uncertainty for pens with erasers; Invert and Eraser bit positions are not confirmed. Filtering simultaneous button holds is heuristic and may drop real multi-button combinations. Descriptor size or firmware prefix changes will bypass some fixes.

## Test Signals
Validation should cover vendor, tablet, and wheel descriptor sizes; firmware property present and absent; pen coordinate, pressure, and tilt reports; top and bottom wheel deltas; wheel-button buttons 6 and 7; ambiguous simultaneous button traces; and battery/feature report preservation through the fixed descriptor. A good runtime signal is custom report ID 9 with top wheel in byte 5 and bottom wheel in byte 6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas13Gen3.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas16Gen3.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas16Gen3.bpf.c

## Purpose
This is the Kamvas 16 Gen 3 sibling of the Kamvas 13 Gen 3 quirk. It enables practical vendor-mode operation by replacing the vendor descriptor with a fixed pen and tablet-pad descriptor, disabling unused firmware-mode nodes when raw-mode firmware is detected, and rewriting vendor reports into standard pen and pad reports. It also accounts for the Kamvas 16's 24-bit X-axis layout.

## Important APIs, Types, And Functions
The target device is USB Huion PID `0x2009`. Known descriptor sizes are vendor 36, tablet 328, and wheel 200; vendor report ID is 8 and vendor report length is 14. `fixed_rdesc_vendor[]` defines a 24-bit X axis, 16-bit Y, pressure, tilt, eight pad buttons, top wheel, and bottom wheel. `hid_fix_rdesc_huion_kamvas16_gen3()` handles descriptor replacement. `hid_fix_event_huion_kamvas16_gen3()` handles pen, buttons, and wheel report subtypes.

## Control Flow
The descriptor hook checks `UDEV_PROP_HUION_FIRMWARE_ID` for prefix `HUION_M22d_`. When present, descriptor sizes 328 and 200 are replaced by disabled descriptors; size 36 is always replaced by the fixed vendor descriptor. The event hook accepts only 14-byte vendor report ID 8. Pen reports invert Y tilt and rearrange bytes from the device layout into the descriptor layout by moving `data[8]` into the third byte of X and shifting subsequent Y/pressure bytes. Button and wheel subtype handling mirrors Kamvas13Gen3: clean button state is persisted, top/bottom wheel direction is converted from 1/2 to +1/-1, and a packed custom report ID 9 is returned.

## State And Persistence
`last_button_state` stores the current accepted pad-button bitmap. There are no maps, files, or cross-load persistence.

## Dependencies And Integration Points
Dependencies are HID-BPF core helpers, `hid_report_helpers.h`, and udev firmware properties. The fixed descriptor integrates the vendor endpoint with Linux as a digitizer pen plus tablet pad. The file explicitly references Kamvas13Gen3 behavior for detailed wheel/button caveats.

## Risks
The 24-bit X byte shuffle is layout-specific; a firmware change to report packing would corrupt coordinates. Eraser/Invert behavior remains unverified for pens with erasers. The simultaneous-button filter can reject legitimate overlapping button presses. The firmware-prefix gating may leave duplicate firmware nodes if userspace does not set the expected property.

## Test Signals
Descriptor tests should cover sizes 36, 328, and 200. Event tests should verify 24-bit X reconstruction against known maximum 69920, Y maximum 39340, pressure maximum 16383, Y tilt inversion, eight pad buttons including wheel buttons, and separate top/bottom wheel deltas. Negative tests should send non-ID-8 or non-14-byte reports and expect no rewrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__Kamvas16Gen3.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20-Bluetooth.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20-Bluetooth.bpf.c

## Purpose
This program fixes the Bluetooth Huion Keydial K20/Keydial Mini. Unlike the USB K20, it does not rely on switching into vendor mode; instead it rewrites the active Bluetooth keyboard, consumer-control, and mouse-wheel reports into one tablet-pad report and disables the silent puck node.

## Important APIs, Types, And Functions
The match is Bluetooth Huion PID `0x8251`. Descriptor lengths are 160 for the active pad node and 114 for the silent puck node. `k20_bt_fix_rdesc()` replaces the active descriptor with `fixed_rdesc_pad[]` and the puck descriptor with `disabled_rdesc_puck[]`. `k20_bt_fix_events()` rewrites report IDs 1, 2, and 5 into report ID 11. A packed local `pad_report` carries a stylus dummy bit, dummy X/Y bytes, a 32-bit button field, and an 8-bit wheel value.

## Control Flow
Descriptor fixup is length-selected: size 160 becomes a tablet function-key descriptor with 19 buttons and a wheel; size 114 becomes a fixed-size vendor-only disabled descriptor. Event fixup maps report ID 1 keyboard events to buttons by scanning HID key arrays and modifiers. Modifiers Control, Alt, and Shift become buttons 13, 14, and 15; normal key usages map through the 18-entry table. Report ID 2 maps Consumer Play/Pause to button 19 and updates `last_button_state`. Report ID 5 carries mouse wheel deltas and emits them while preserving the last button bitmap.

## State And Persistence
`last_button_state` is a persistent global holding the current 19-button bitmap across independent keyboard, consumer-control, and wheel reports. This is required because the physical wheel click and wheel movement arrive on different report IDs from key buttons.

## Dependencies And Integration Points
The program depends on HID-BPF helpers and `hid_report_helpers.h`. It integrates the Bluetooth remote with Linux tablet-pad handling by advertising Digitizers Tablet Function Keys plus button usages 1-10 and 0x31-0x3a for higher buttons.

## Risks
The keyboard mapping table assumes the default Bluetooth key assignments. Unknown key assignments or remapped firmware profiles will not be translated. The event hook reads 12 bytes even though source reports are shorter, relying on HID-BPF data access and the output struct size; unexpected report lengths should be tested. Wheel deltas are passed through as unsigned bytes, with 0xff representing -1.

## Test Signals
Descriptor tests should show the 160-byte node converted to report ID 11 and the 114-byte node disabled. Runtime tests should press each mapped key button, each modifier-derived button, Play/Pause wheel click, and wheel up/down, checking that button state persists correctly while wheel-only reports are emitted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20-Bluetooth.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20.bpf.c

## Purpose
This program fixes the USB Huion Keydial K20 across firmware and raw/vendor modes. Firmware mode sends buttons as keyboard shortcuts and exposes an unreliable wheel/puck node; tablet mode sends vendor reports. The program creates a tablet-pad descriptor, disables duplicate firmware nodes when raw-mode firmware is detected, and rewrites both vendor and keyboard reports into a single pad report.

## Important APIs, Types, And Functions
The match is USB Huion PID `0x0069`. Known descriptor lengths are pad 135, puck 108, and vendor 18. `k20_fix_rdesc()` rewrites or disables descriptors based on `UDEV_PROP_HUION_FIRMWARE_ID` prefix `HUION_T21h_`. `k20_fix_events()` converts vendor report ID 8 and firmware keyboard report ID 3. `HID_BPF_OPS(keydial_k20)` publishes both hooks, and `probe()` accepts only the three known descriptor sizes.

## Control Flow
If the firmware ID prefix matches, the pad and puck descriptors are disabled to avoid duplicate silent or redundant devices. If the prefix is absent, the pad descriptor is replaced with a tablet-pad descriptor that preserves original report lengths. The vendor descriptor is always replaced with a tablet-pad descriptor for raw mode. Event handling first rewrites vendor reports: `data[1] == 0xf1` is a wheel report and maps direction byte 2 to 0xff, otherwise bytes 4-6 become the 19-button bitmap stored in `last_button_state`. Firmware report ID 3 scans the keyboard report and modifier byte against a mapping table, creates the button bitmap, zeros consumed key slots, and emits the same pad report with wheel zero.

## State And Persistence
`last_button_state` persists raw-mode button state for wheel-only vendor reports. Firmware keyboard reports compute a local button bitmap per report. No durable persistence exists.

## Dependencies And Integration Points
The file depends on HID-BPF helpers, report helper macros, and udev-hid-bpf firmware properties from tools such as huion-switcher. It integrates with Linux tablet-pad handling by using Digitizers Tablet Function Keys and HID button usages that map to BTN_0-BTN_9 and BTN_A-family controls.

## Risks
Firmware-mode wheel and wheel-button data are documented as unreliable and intentionally not supported; users need raw/tablet mode for reliable wheel operation. Descriptor length gating may fail on new firmware. The keyboard mapping assumes default Huion shortcut assignments. Missing firmware properties can leave duplicate event nodes.

## Test Signals
Tests should cover descriptor sizes 18, 108, and 135, property-present and property-absent paths, raw-mode button and wheel reports, firmware keyboard shortcut translation for buttons 1-18, and rejection of unknown descriptor sizes. Runtime success is a single tablet-pad event stream with correct 19-button bitmap and wheel deltas in raw mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Huion__KeydialK20.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/IOGEAR__Kaliber-MMOmentum.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/IOGEAR__Kaliber-MMOmentum.bpf.c

## Purpose
This small descriptor quirk enables the extra buttons on the IOGEAR Kaliber Gaming MMOmentum Pro mouse. The original descriptor marks several button groups as constants, so Linux only exposes five of the twelve physical buttons.

## Important APIs, Types, And Functions
The match is USB VID `0x258A`, PID `0x0027`. `hid_fix_rdesc()` is the only runtime hook. It obtains descriptor data with `hid_bpf_get_data()` and edits offsets 84, 112, and 140. `HID_BPF_OPS(iogear_kaliber_momentum)` installs only `.hid_rdesc_fixup`. `probe()` binds only to descriptor size 213.

## Control Flow
The descriptor hook first checks `data[3] == 0x06` to limit changes to the keyboard interface. For each known offset, it changes an Input item from `0x81 0x03` (Constant, Variable, Absolute) to `0x81 0x02` (Data, Variable, Absolute). It returns 0 because it edits the descriptor in place without changing size.

## State And Persistence
There is no mutable state beyond the in-place descriptor bytes.

## Dependencies And Integration Points
The program depends on HID-BPF helpers and the fixed descriptor layout for the target mouse's keyboard interface. It integrates before normal HID parsing so the kernel exposes additional button inputs.

## Risks
The VID is shared by other vendors, so the descriptor-size and keyboard-interface checks are important but still layout-specific. If a firmware variant has the same size but different offset contents, the code safely checks `0x81 0x03` before editing, but may leave buttons unfixed.

## Test Signals
A descriptor dump should show offsets 84/112/140 changed from constant inputs to data inputs. Functional testing should confirm all twelve mouse buttons are visible and no unrelated interface with a different descriptor size binds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/IOGEAR__Kaliber-MMOmentum.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Logitech__SpaceNavigator.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Logitech__SpaceNavigator.bpf.c

## Purpose
This descriptor quirk fixes 3Dconnexion/Logitech SpaceNavigator units whose six axes are absolute but declared as relative. The kernel had a historical fix for some variants, but the offsets differ across devices, so this BPF program tries all known offsets for descriptor sizes seen in the field.

## Important APIs, Types, And Functions
The match is USB Logitech VID `0x046D`, PID `0xC626`, `HID_GROUP_ANY`. `hid_fix_rdesc()` edits Input item flags at offsets 32, 36, 49, and 53 when they are `0x81 0x06`. `probe()` accepts descriptor sizes 202, 217, and 228 and refuses to load if the descriptor already appears fixed.

## Control Flow
At descriptor-fixup time, each candidate offset is inspected independently. If an item is `Input(Data,Var,Rel)`, the second byte is changed to `0x02` for `Input(Data,Var,Abs)`. Probe first filters unknown descriptor sizes, then checks both known offset pairs; if either pair is already absolute, it returns `-EINVAL` to avoid double-fixing.

## State And Persistence
The program is stateless after descriptor mutation.

## Dependencies And Integration Points
It depends on HID-BPF helpers and known SpaceNavigator descriptor layouts. It integrates with the HID parser so the evdev axis semantics are absolute rather than relative for X/Y/Z and Rx/Ry/Rz collections.

## Risks
The 2009 model size is not known and future variants may need additional offsets. The current code is conservative because it only changes bytes that match `0x81 0x06`, but an unknown same-size layout could remain unfixed.

## Test Signals
Tests should cover descriptor sizes 202, 217, and 228, already-fixed descriptors, and each offset pair. Runtime verification should show stable absolute 6-axis values rather than accumulating relative deltas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Logitech__SpaceNavigator.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Makefile

## Purpose
This Makefile builds every `*.bpf.c` HID-BPF program in the directory into stripped `*.bpf.o` objects. It also bootstraps libbpf, bpftool, and `vmlinux.h` generation from BTF when needed.

## Important APIs, Types, And Targets
Important variables include `OUTPUT=.output`, `TOOLS_PATH=../../../../tools`, `LIBBPF_SRC`, `BPFTOOL_SRC`, `VMLINUX_BTF_PATHS`, `VMLINUX_BTF`, `VMLINUX_H`, and tool overrides `CLANG`, `LLC`, `LLVM_STRIP`, `BPFTOOL`. `SOURCES = $(wildcard *.bpf.c)` and `TARGETS = $(SOURCES:.bpf.c=.bpf.o)`. Main targets are `all`, `clean`, pattern target `%.bpf.o`, `vmlinux.h`, `$(BPFOBJ)`, `$(DEFAULT_BPFTOOL)`, and output-directory creation.

## Control Flow
`all` builds every object. The pattern rule compiles each BPF C source with `clang -g -O2 --target=bpf -Wall -Werror`, includes generated `vmlinux.h`, libbpf headers, and UAPI headers, enables Microsoft anonymous-tag extensions, then strips debug info with `llvm-strip -g`. `vmlinux.h` is generated by `bpftool btf dump` from the first existing BTF source unless `VMLINUX_H` is provided. libbpf and bpftool are built under `.output`, with a cross-compile branch that builds bpftool bootstrap without the local libbpf bootstrap output coupling.

## State And Persistence
Build products live in `.output`, generated `vmlinux.h`, `*.bpf.o`, libbpf install output, and bpftool bootstrap output. `clean` removes `.output` and built BPF objects but not necessarily external BTF sources.

## Dependencies And Integration Points
The file depends on a Linux kernel source tree with `tools/lib/bpf`, `tools/bpf/bpftool`, UAPI headers, and accessible kernel BTF via build output, `/sys/kernel/btf/vmlinux`, or `/boot/vmlinux-$(uname -r)`. It integrates these standalone HID-BPF programs with the kernel self-contained BPF build workflow.

## Risks
The `vmlinux.h` rule lists `| $(INCLUDE_DIR)`, but `INCLUDE_DIR` is not defined in this file; make treats an empty order-only prerequisite benignly, but the variable may indicate stale intent. Builds fail hard when no BTF source is found. `-Werror` makes warnings fatal across all device-specific programs. `SOURCES` wildcarding means any temporary `*.bpf.c` file in the directory becomes a build target.

## Test Signals
Run `make -n` to inspect commands, `make V=1` for full command output, `make clean all` with valid `VMLINUX_BTF`, and override `VMLINUX_H` to test the copy path. A good artifact signal is one stripped `.bpf.o` per `*.bpf.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Microsoft__Xbox-Elite-2.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Microsoft__Xbox-Elite-2.bpf.c

## Purpose
This descriptor quirk fixes Bluetooth Xbox Elite Series 2 controller paddle reporting. The original descriptor places paddle usages in a consumer/assign-selection block that the kernel does not interpret properly, yielding `KEY_UNKNOWN`; the program replaces that block with a gamepad button collection for buttons 21-24.

## Important APIs, Types, And Functions
The match is Bluetooth Microsoft VID/PID for Xbox Elite 2. `OFFSET_ASSIGN_SELECTION` identifies the descriptor block to replace, and `ORIGINAL_RDESC_SIZE` gates probe. `rdesc_assign_selection[]` contains the expected original bytes and `fixed_rdesc_assign_selection[]` contains same-sized replacement bytes. `_Static_assert`s enforce equal replacement length and in-bounds offset. `hid_fix_rdesc()` verifies and copies the replacement; `probe()` repeats the size/content validation.

## Control Flow
Probe only accepts the known keyboard interface descriptor size and expected original block. Descriptor fixup then checks the same block with `__builtin_memcmp()` and copies the replacement into place. The hook returns 0 because descriptor length is unchanged.

## State And Persistence
The program is stateless aside from descriptor bytes modified during HID parsing.

## Dependencies And Integration Points
It depends on HID-BPF helpers and on the exact Bluetooth descriptor layout. It integrates by changing how the HID parser classifies the paddles, causing them to appear as gamepad buttons rather than unknown keyboard/consumer usages.

## Risks
The fix is intentionally exact-match. Firmware changes to the descriptor block or size will reject the quirk. If Microsoft changes paddle usages but leaves the same size, the memcmp protects against writing over an unexpected layout.

## Test Signals
Tests should verify `probe()` rejects descriptors with changed size or changed assign-selection bytes, accepts the known descriptor, and exposes paddles as buttons 21-24 without `KEY_UNKNOWN` events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Microsoft__Xbox-Elite-2.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Mistel__MD770.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Mistel__MD770.bpf.c

## Purpose
This descriptor quirk fixes the second interface of the Mistel MD770 keyboard so NKRO reports beyond the first six simultaneous key presses are parsed correctly. The bad descriptor marks the large key bitmap as Array input; it should be Variable input.

## Important APIs, Types, And Functions
The match is USB Holtek VID `0x04D9`, PID `0x0339`, descriptor size 203. `hid_rdesc_fixup_mistel_md770()` edits descriptor byte 201 from `0x00` to `0x02` when present. `HID_BPF_OPS(mistel_md770)` publishes only the descriptor hook. `probe()` gates on exact descriptor size.

## Control Flow
Descriptor fixup reads the full descriptor and checks `data[201]`. If it is the erroneous Input flags byte `0x00`, it changes it to `0x02` so the preceding keyboard usages are parsed as `Data,Var,Abs`. It returns 0 because no length changes occur.

## State And Persistence
There is no runtime state.

## Dependencies And Integration Points
The program depends on HID-BPF descriptor mutation before HID parsing. It integrates with the keyboard input path by making the second interface's bitmap usable for rollover keys.

## Risks
The fix is exact-size and offset based. A firmware variant with the same size but different layout could either be left unchanged due to the byte guard or require a new offset. There is no event hook, so any remaining malformed runtime reports are outside this quirk.

## Test Signals
A descriptor dump should show byte 201 changed to `0x02`. Functional testing should hold more than six keys and confirm the second interface emits valid key events instead of being ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Mistel__MD770.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Rapoo__M50-Plus-Silent.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Rapoo__M50-Plus-Silent.bpf.c

## Purpose
This descriptor quirk enables the two side buttons on the Rapoo M50 Plus Silent mouse. The original descriptor has five button bits but a Usage Maximum of only 3, so Linux cannot assign usages to buttons 4 and 5.

## Important APIs, Types, And Functions
The match is USB Rapoo VID `0x24AE`, PID `0x2015`, descriptor size 186. `hid_rdesc_fixup_rapoo_m50()` edits `data[17]` from `0x03` to `0x05`. `HID_BPF_OPS(rapoo_m50)` provides `.hid_rdesc_fixup`; `probe()` accepts only descriptor size 186.

## Control Flow
At descriptor fixup, the hook reads the descriptor and changes the Usage Maximum byte at offset 17 if it still has the bad value 3. It does not alter report count, size, or descriptor length because the descriptor already reserves five button bits.

## State And Persistence
There is no runtime state.

## Dependencies And Integration Points
The file depends on HID-BPF helpers and a stable mouse descriptor. It integrates with the normal mouse input parser so side buttons become standard button usages.

## Risks
The code relies on exact descriptor size and offset. Future descriptors may need different offsets. If the usage maximum is already fixed, the byte guard leaves it unchanged.

## Test Signals
Descriptor dump should show Usage Maximum 5 for the button collection. Runtime testing should produce left, right, middle, back, and forward button events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Rapoo__M50-Plus-Silent.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/TUXEDO__Sirius-16-Gen1-and-Gen2.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/TUXEDO__Sirius-16-Gen1-and-Gen2.bpf.c

## Purpose
This event quirk suppresses an unwanted F13 key event on TUXEDO Sirius 16 Gen1/Gen2 devices using USB VID/PID `0x048D:0x8910`. It zeroes both array-encoded and bitmap-encoded appearances of HID usage `0x68`.

## Important APIs, Types, And Functions
The program declares only a device-event hook: `ignore_key_fix_event()`. It reads 37-byte report ID 1 reports, scans bytes 3 through 8 for usage `0x68`, and clears bit 0 of byte 22 for bitmap-encoded additional keys. `HID_BPF_OPS(ignore_button)` installs `.hid_device_event`.

## Control Flow
If the incoming report is shorter than 37 bytes, inaccessible, or not report ID 1, the hook returns without changes. Otherwise it clears any F13 usage found in the six-key array area and clears the bit corresponding to F13 in the extended bitmap area. The report length is unchanged.

## State And Persistence
The program is stateless.

## Dependencies And Integration Points
It depends on the target keyboard report layout and HID-BPF event mutation. It integrates after reports are received but before normal input delivery, preventing the unwanted key from reaching userspace.

## Risks
There is no `probe()` descriptor-size guard in the file, so safety relies on VID/PID and runtime report length/report ID checks. If a later firmware changes the F13 bit offset, the array path may still work but the bitmap path may miss or clear the wrong bit.

## Test Signals
Feed report ID 1 with `0x68` in bytes 3-8 and with byte 22 bit 0 set; both should be cleared. Reports with other IDs or length under 37 should be untouched. Functional testing should confirm the spurious F13 key no longer appears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/TUXEDO__Sirius-16-Gen1-and-Gen2.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Thrustmaster__TCA-Yoke-Boeing.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Thrustmaster__TCA-Yoke-Boeing.bpf.c

## Purpose
This descriptor quirk fixes the Thrustmaster TCA Yoke Boeing joystick descriptor so non-existing axes do not appear in Linux. Two vendor input fields are incorrectly marked as data inputs; the program marks them as constants.

## Important APIs, Types, And Functions
The match is USB Thrustmaster PID `PID_TCA_YOKE_BOEING`. `hid_fix_rdesc_tca_yoke()` expects descriptor length 148, reads the descriptor, checks Generic Desktop Joystick at the beginning, and edits Input flag bytes after offsets 90 and 103. `probe()` rejects devices whose offset 91 is no longer the original `0x02`, which means the kernel or firmware may already be fixed.

## Control Flow
Descriptor fixup returns early if size is not 148, data is unavailable, or the descriptor does not start with Usage Page Generic Desktop / Usage Joystick. If both relevant items are Input items, it changes bytes 91 and 104 to `0x03` (`Constant, Variable, Absolute`). It returns 0 because the descriptor length is unchanged.

## State And Persistence
There is no state.

## Dependencies And Integration Points
It depends on HID-BPF helpers and the exact joystick descriptor layout. It integrates with the joystick input stack by preventing phantom axes from being created.

## Risks
The `probe()` check only tests one of the changed bytes, while fixup changes two. Firmware variants with partial changes may need additional handling. Offset-based descriptor edits are sensitive to layout changes, but the start-of-descriptor and input-item checks reduce accidental writes.

## Test Signals
Descriptor tests should show bytes 91 and 104 changed from data input to constant input for the original descriptor. Runtime joystick enumeration should no longer include the non-existing axes while hat, buttons, and real axes remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Thrustmaster__TCA-Yoke-Boeing.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Trust__Philips-SPK6327.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Trust__Philips-SPK6327.bpf.c

## Purpose
This descriptor quirk fixes a Trust/Philips SPK6327 keyboard whose modifier keys are declared as Array input instead of Variable input, causing modifiers such as Ctrl, Alt, and Super to behave like Left Shift.

## Important APIs, Types, And Functions
The match is USB VID `0x145F`, PID `0x024B`. `hid_fix_rdesc()` reads the descriptor and changes byte 101 from `0x00` to `0x02`. `HID_BPF_OPS(trust_spk6327)` installs descriptor fixup only. `probe()` applies the program to interface 1 by accepting descriptor size 169 and rejecting interface 0 size 62.

## Control Flow
The hook obtains up to 4096 descriptor bytes. If available and the modifier Input flags byte at offset 101 is `0x00`, it changes it to `0x02`. The descriptor length is unchanged. Probe is a simple descriptor-size gate.

## State And Persistence
There is no mutable runtime state.

## Dependencies And Integration Points
The file depends on HID-BPF descriptor mutation and the target keyboard's fixed interface layout. It integrates before HID parsing so modifier usages become independent variable bits.

## Risks
The offset is specific to the 169-byte interface. If another firmware changes descriptor size or offset, the quirk will reject or fail to fix. The byte guard prevents rewriting a descriptor already fixed by firmware or kernel changes.

## Test Signals
Descriptor dump should show the modifier Input item flags changed to `0x02`. Functional tests should press LCtrl, LAlt, Super, and Shift independently and confirm they report distinct modifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Trust__Philips-SPK6327.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/WALTOP__Batteryless-Tablet.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/WALTOP__Batteryless-Tablet.bpf.c

## Purpose
This program fixes a WALTOP batteryless tablet by replacing its descriptor, correcting an ambiguous secondary barrel button report, and reshaping pressure values. The descriptor replacement adds Secondary Barrel Switch, corrects pen coordinate/tilt semantics, and keeps mouse, keyboard, and consumer-control collections.

## Important APIs, Types, And Functions
The match is USB WALTOP VID `0x172F`, PID `0x0505`, descriptor size 335. `fixed_rdesc[]` is a full replacement descriptor. `bitwidth32()`, `floor_log2_32()`, and `scaled_log2()` implement a fixed-point approximation for pressure scaling. `hid_fix_rdesc()` copies the replacement descriptor and returns its size. `waltop_fix_events()` handles pen report ID 16. `HID_BPF_OPS(waltop_batteryless)` installs both hooks.

## Control Flow
Probe accepts only descriptor size 335. Descriptor fixup always copies `fixed_rdesc`. Event fixup ignores non-pen reports. For pen reports, if the tablet sends Tip Switch and Barrel Switch together while neither was previously held, the code clears both and sets `SECONDARY_BARREL_SWITCH`, interpreting that transition as the physical secondary button. It then stores the current button byte. Pressure is read little-endian from bytes 6-7; values up to 102 are multiplied by 12, while higher values pass through `scaled_log2()` to map the exponential sensor curve into the advertised 0-2047 logical range.

## State And Persistence
`last_button_state` persists the prior pen button byte to distinguish a new ambiguous secondary-button press from ongoing tip or barrel holds. There is no external persistence.

## Dependencies And Integration Points
The file depends on HID-BPF helpers and stable report ID 16 layout. It integrates with the digitizer input path by presenting corrected pen buttons, axes, tilt, pressure, plus existing mouse/keyboard/media collections.

## Risks
The secondary-button heuristic assumes the only unambiguous simultaneous tip+barrel transition is the secondary button. If users press tip and barrel at exactly the same time from idle, it could be remapped. The pressure scaling is an approximation tuned to observed values 12 and 102. Full descriptor replacement is broad and sensitive to changes in the original descriptor.

## Test Signals
Tests should compare descriptor size and key pen usages, press tip/barrel/secondary barrel in isolation and combinations, verify pressure curve values around 0, 100, 102, and 2047, and confirm non-pen reports remain unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/WALTOP__Batteryless-Tablet.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Wacom__ArtPen.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Wacom__ArtPen.bpf.c

## Purpose
This event quirk smooths pressure reports for the Wacom Art Pen on supported Wacom tablets. The stylus reports pressure in chunky every-other-event steps; the program interpolates odd frames by averaging current and previous pressure while delaying pressure by one event.

## Important APIs, Types, And Functions
The match is Wacom Intuos Pro 2 M PID `0x0357`, but the file is structured to support more devices through `struct wacom_params devices[]`. `wacom_params` records product ID, descriptor length, report ID, report length, and byte offsets for tip switch, pressure, and tool type. `probe()` uses `hid_bpf_allocate_context()` to inspect the actual product ID and copies matching parameters into global `params`. `artpen_pressure_interpolate()` mutates reports. Helper accessors `get_u16()` and `get_u8()` cast byte offsets.

## Control Flow
Probe rejects unsupported product/descriptor pairs and initializes `params` for matching devices. The event hook reads a 64-byte report chunk, validates report ID and offset bounds, checks tool type `0x0804` for Art Pen, and ignores other tools. If tip is up, it resets `prev_pressure` to 0 and starts the next contact on an odd frame. If tip is down and `odd` is true, it replaces pressure with the average of current pressure and `prev_pressure`; then it stores pressure and toggles `odd`.

## State And Persistence
`params` stores per-device offsets selected at probe time. `odd` tracks alternating frames, and `prev_pressure` stores the previous pressure sample. These are BPF globals, persistent while loaded.

## Dependencies And Integration Points
The program depends on HID-BPF event mutation and Wacom report layouts. It integrates after report receipt and before input delivery, leaving descriptor parsing unchanged. It depends on tool type bytes being present and little-endian-compatible with direct `__u16 *` access.

## Risks
The direct offset casts assume alignment and endianness as used by BPF/HID report data. The smoothing intentionally changes latency and may not suit all users. Only listed device descriptors are supported, so additional Wacom tablets using the Art Pen need new `devices[]` entries.

## Test Signals
Tests should use report ID 16, tool type `0x0804`, pressure offset 8, and tip offset 1 for descriptor length 949. A sample sequence 0,100,100,200,200 should become approximately 0,50,100,150,200 while non-ArtPen tool types and tip-up reports are unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/Wacom__ArtPen.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__ACK05.bpf.c -->
# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__ACK05.bpf.c

## Purpose
This program fixes the XPPen/Hanvon Ugee ACK05 shortcut remote. The device normally emits programmable buttons as ambiguous keyboard shortcuts; the program switches it into raw mode, disables normal keyboard/stylus descriptors, appends a fixed vendor descriptor describing pad and battery reports, and rewrites raw vendor reports into tablet-pad and battery events.

## Important APIs, Types, And Functions
The match is USB UGEE VID `0x28BD`, PID `0x0202`; it applies both direct and dongle connections. The file enables async support with `HID_BPF_ASYNC_MAX_CTX 1` and `hid_bpf_async.h`. Known descriptor sizes are wired pad 102, dongle pad 177, stylus 109, and vendor 36. `ack05_fix_rdesc()` appends `fixed_rdesc_vendor[]` to the vendor descriptor or disables non-vendor descriptors. `switch_to_raw_mode()` sends a 32-byte output report through `hid_bpf_hw_output_report()`. `ack05_fix_events()` handles reconnect, raw pad, and raw battery reports. `probe()` initializes async support and immediately switches to raw mode for the vendor descriptor.

## Control Flow
Descriptor fixup appends the fixed pad/battery descriptor after the vendor descriptor to preserve output reports required for raw-mode commands. Non-vendor descriptors are renamed as disabled and replaced with a fixed-size vendor report. Probe accepts all four known descriptor sizes; for the vendor descriptor it allocates a HID context, calls `HID_BPF_ASYNC_INIT()`, sends the raw-mode magic report, and releases the context. Event fixup ignores non-vendor report ID 2. A reconnect signature `f8 02 01` schedules a delayed raw-mode switch. Raw pad report `0xf0` is promoted into report ID `0xf0`, converts wheel direction value 2 to `0xff`, and returns length 8. Raw battery report `0xf2` is promoted and returned with length 5.

## State And Persistence
`last_button_state` is declared but not used by the current event path. Async context state is managed by `hid_bpf_async.h` for delayed calls. The device's raw-mode state is external hardware state triggered by output reports.

## Dependencies And Integration Points
The program depends on HID-BPF async infrastructure, hardware output reports, HID report helper macros, and the ACK05 raw protocol. It integrates with the kernel by making the remote look like a tablet function-key device and by exposing battery state without allowing the kernel to query battery state directly.

## Risks
The raw-mode magic packet is protocol-specific and may fail silently on firmware changes. The fixed descriptor is appended rather than replacing the vendor descriptor, so descriptor-size budget and parser behavior matter. Reconnect handling relies on a specific signature. Button mapping in raw mode includes an extra usage for BTN_A/BTN_SOUTH; keyboard-mode ambiguities are avoided by disabling those descriptors, not solved there.

## Test Signals
Tests should verify the vendor descriptor grows by the fixed descriptor size, other descriptors are disabled and renamed, probe sends the raw-mode report, reconnect schedules the delayed call, raw pad reports become 8-byte report `0xf0`, wheel counter-clockwise becomes `0xff`, and battery reports become 5-byte report `0xf2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/XPPen__ACK05.bpf.c -->
