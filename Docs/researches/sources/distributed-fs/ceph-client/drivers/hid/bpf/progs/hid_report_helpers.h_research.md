# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_report_helpers.h

## Purpose

`hid_report_helpers.h` is a generated helper header for composing HID report descriptors inside HID-BPF programs. It turns HID descriptor items into C macro fragments that expand to byte initializer lists, so device-specific `.bpf.c` files can define replacement or supplemental `static const __u8` report descriptors without writing raw hex for every item.

The file is intentionally header-only and generated. Its non-generated hand-authored surface is the descriptor-building macro vocabulary: integer-width checks, little-endian byte splitting, HID collection wrappers, main/global/local item macros, unit helpers, a vendor padding report helper, and generated usage page / usage macros.

## Important APIs, Types, and Macros

- `must_be(e, msg_)` is an expression-form compile-time assertion. It uses `_Static_assert` inside a `sizeof(struct {...})` expression multiplied by zero, so successful checks contribute `0` to a descriptor initializer while failed checks stop compilation.
- `i4`, `i8`, `i16`, and `i32` validate that literal descriptor values fit the intended HID item width. They cast to Linux fixed-width integer aliases such as `__u8`, `__u16`, and `__u32`; those types must be available from the including BPF source, normally via `vmlinux.h` / local HID-BPF headers.
- `LE16` and `LE32` emit little-endian byte sequences for multi-byte HID item payloads.
- `Collection`, `CollectionPhysical`, `CollectionApplication`, and `CollectionLogical` emit a collection start item, nested descriptor bytes passed via `__VA_ARGS__`, and the matching `End Collection` byte.
- `PushPop(...)` emits HID global `Push`, the supplied nested items, and `Pop`.
- `Const`, `Var`, `Arr`, `Abs`, `Rel`, `Null`, and `Buff` are bit flags intended for `Input`, `Output`, and `Feature` macros.
- `Input`, `Output`, `Feature`, plus `_i16` forms, emit HID main items. The plain versions restrict the flag payload to one byte.
- `ReportId`, `ReportSize`, `ReportCount`, logical/physical min/max macros, usage minimum/maximum macros, `UsagePage_i8`, `UsagePage_i16`, `Usage_i8`, `Usage_i16`, and `Usage_i32` map directly to HID global/local item encodings.
- Unit helpers define system/unit nibble values such as `SILinear`, `SIRotation`, `EnglishLinear`, `EnglishRotation`, `cm`, `rad`, `deg`, and `in`, then expose `Unit`, `Unit_i8`, `Unit_i16`, `Unit_i32`, and `UnitExponent`.
- `FixedSizeVendorReport(bytes_)` creates a vendor-specific input report with report ID `0xac`, 8-bit fields, and `ReportCount(bytes_ - 1)`. It is meant to ensure the rewritten descriptor still advertises at least the largest report size the kernel may receive from the device.
- The generated section defines 37 `UsagePage_*` macros and 2769 `Usage_*` macros, with 2864 `#define` entries total in the header. The usage macros encode HID Usage Tables names into the correct `Usage_i8` or `Usage_i16` form.

## Control Flow

There is no runtime control flow. All behavior happens during C preprocessing and compilation:

1. A device-specific BPF source includes `hid_report_helpers.h`.
2. That source writes a descriptor array as a sequence of macros, often with top-level `UsagePage_*`, `Usage_*`, and `CollectionApplication(...)` blocks.
3. The preprocessor expands these macros into byte initializer elements.
4. Compile-time assertions in `must_be` validate constant ranges for item payloads and vendor usage pages.
5. The resulting byte array is passed to HID-BPF helper calls from the including program, typically to replace or adjust a device report descriptor.

The most important structural control mechanism is variadic nesting: `Collection*` and `PushPop` macros wrap arbitrary descriptor fragments and append their closing bytes automatically. This reduces unmatched collection/pop errors in callers, but the header cannot validate HID semantic correctness such as report bit alignment or whether usages match report sizes.

## State and Persistence Behavior

This header owns no state and has no persistence layer. It defines only preprocessor constants and initializer-list fragments. Any persistent effect comes from the including HID-BPF object being loaded for a HID device by `udev-hid-bpf`; once loaded, the kernel sees the descriptor bytes produced by the macros as part of that BPF program's data.

The generated descriptor arrays in callers are usually static constants embedded in BPF objects. They persist only for the lifetime of the loaded BPF program and the device association managed by the loader / udev rules.

## Dependencies

- The including source must provide Linux fixed-width aliases `__u8`, `__u16`, and `__u32`.
- The code assumes a C compiler with `_Static_assert`, variadic macros, and BPF-compatible compilation through clang.
- It relies on HID report descriptor item encodings from the HID specification.
- The surrounding build uses `clang --target=bpf`, libbpf headers, generated `vmlinux.h`, and bpftool as shown by the local `Makefile`.
- Runtime deployment is external to this header. The directory README describes loading compiled `.bpf.o` files through `udev-hid-bpf` and checking loaded programs with `bpftool`.

## Integration Points

This file is included by multiple HID-BPF programs in the same directory; an `rg` scan found 11 `.bpf.c` include users. Examples include Huion tablet/dial fixes, XPPen tablet/controller fixes, and the generic touchpad program.

The strongest integration point is descriptor replacement code in device-specific files. Those programs compose `fixed_rdesc` arrays with readable HID terms such as `UsagePage_GenericDesktop`, `UsagePage_Digitizers`, `Usage_GD_X`, `Usage_Dig_TipSwitch`, `ReportId(...)`, `ReportSize(...)`, `ReportCount(...)`, and `Input(Var|Abs)`. Several programs append `FixedSizeVendorReport(...)` to keep the new descriptor large enough for original device reports that are still delivered.

The header also sits beside related helper headers:

- `hid_bpf_helpers.h` / `hid_bpf.h` provide HID-BPF program and helper interfaces used by callers.
- `hid_usages.h` provides numeric usage constants for runtime inspection of parsed HID fields, while `hid_report_helpers.h` provides byte-emitting descriptor macros.
- `hid_report_descriptor_helpers.h` is a separate descriptor parsing/editing helper surface; this file is focused on descriptor composition.

## Risks and Edge Cases

- The file is generated and marked "DO NOT EDIT"; manual changes risk being overwritten or drifting from the HID usage source used by the generator.
- `Unit_i16` and `Unit_i32` use `i16` / `i32` directly rather than `LE16` / `LE32`, so they emit a single integer initializer instead of explicit bytes. That may be intentional for callers that rarely use these paths, but it is a descriptor-encoding risk if a caller expects byte-split multi-byte unit items.
- `i8` intentionally accepts signed 8-bit values and unsigned byte values up to `0xff`. This matches common HID descriptor practice, but can hide signedness mistakes when a logical field should be constrained more narrowly.
- `i32` reports the assertion message `"not a i32/u16"`, which appears to be a typo and could mislead debugging.
- `Collection*` automatically appends `0xc0`, but HID semantic validity still depends on the caller placing global/local/main items in legal order.
- `FixedSizeVendorReport(bytes_)` assumes `bytes_ >= 1`; otherwise `ReportCount((bytes_) - 1)` will fail or produce an invalid descriptor. The report ID `0xac` is fixed, so callers must avoid collisions with meaningful reports.
- Placing `FixedSizeVendorReport` outside an application collection can create an unwanted extra evdev node, as the header comments warn.
- Generated usage names may collide by abbreviation across pages. This file already has repeated prefixes such as `Usage_SC_*` for different pages; users must pair usages with the correct current `UsagePage_*` and read names carefully.

## Test Signals

- Compile all HID-BPF programs in this directory with `make`; `-Wall -Werror` makes range-check failures, invalid macro expansions, and many descriptor initializer mistakes hard failures.
- Add targeted compile tests when introducing a descriptor that uses less common paths such as `Unit_i16`, `Unit_i32`, `Usage_i32`, `Input_i16`, `Output_i16`, or `Feature_i16`.
- Use HID selftests for the device-specific BPF programs that consume this header, because they validate the composed descriptor in a kernel/HID context rather than only checking C compilation.
- For deployed objects, use the README signals: verify udev matching with `udevadm test` and confirm the program is loaded with `bpftool prog`.
- Runtime behavior should be checked against `hid-recorder`, `libinput debug-events`, `evtest`, or the relevant tablet/game/controller stack to confirm report IDs, report sizes, axes, buttons, batteries, and vendor padding reports are interpreted as intended.
