# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_usages.h

## Purpose

`hid_usages.h` is a generated, BPF-program-facing HID usage catalog. It gives HID-BPF programs stable C preprocessor names for HID usage pages and page-local usage IDs without pulling in the larger kernel HID parser headers. The file is data-only: it contains no executable code, no structs, and no inline helpers. Its value is the generated mapping between readable names such as `HidUsagePage_Digitizers` or `HidUsage_Dig_PadType` and the numeric values defined by the HID Usage Tables.

The header currently covers common HID pages used by input, sensors, lighting, barcode/scales, power, braille, monitor, camera, arcade, FIDO, haptics, and related device classes. A local consumer visible in this tree is `drivers/hid/bpf/progs/Generic__touchpad.bpf.c`, which includes this header and checks parsed report fields by comparing `field->usage_page` and `field->usage_id` against the generated constants.

## Important APIs, Types, and Definitions

- `#pragma once` is the only include guard.
- `HidUsagePage_*` macros define top-level HID usage pages. Examples include Generic Desktop `0x01`, Keyboard/Keypad `0x07`, Digitizers `0x0d`, Sensors `0x20`, Lighting and Illumination `0x59`, Power `0x84`, and FIDO Alliance `0xf1d0`.
- `HidUsage_GD_*`, `HidUsage_KK_*`, `HidUsage_LED_*`, `HidUsage_Con_*`, `HidUsage_Dig_*`, `HidUsage_Sen_*`, and many other prefix groups define page-local usage IDs.
- The prefix namespace is generated for readability, not for runtime dispatch. A BPF program must still pair a usage ID with the correct usage page because numeric usage IDs are only unique within their page.
- No kernel APIs are called directly. The public contract is the macro names and their numeric values.

## Control Flow

There is no runtime control flow in this file. Build control flow is limited to textual inclusion by HID-BPF programs. At compile time the C preprocessor substitutes the constants into BPF C source, and the BPF compiler emits immediate constants used in verifier-checked comparisons or assignments.

The typical consumer flow is: include `hid_usages.h`, read fields exposed by the HID-BPF context or HID-BPF helper structures, compare `usage_page` and `usage_id` to the generated macros, and modify report-descriptor or event behavior based on those matches. Because the file is generated, source changes should normally come from regenerating the usage table rather than hand editing one macro.

## State and Persistence Behavior

The header has no mutable state and no persistence behavior. Its persistence is source-level: the macro set becomes part of each compiled BPF object that includes it. If the generated constants drift from the HID Usage Tables, the compiled BPF programs will continue using the stale values until rebuilt.

## Dependencies and Integration Points

- The SPDX and generated-file comments identify it as a Linux kernel source artifact and warn against manual edits.
- It integrates with HID-BPF programs under `drivers/hid/bpf/progs/`, especially descriptor fixup or event-rewrite programs that need symbolic HID usage names.
- The constants mirror external HID Usage Table semantics, so the generator and upstream HID table version are an implicit dependency even though no generator script is referenced inside the header.
- It intentionally avoids kernel-only data structures so it can be consumed by restricted BPF C compilation.

## Risks and Edge Cases

- The file is generated and should not be manually edited. Local changes are likely to be lost and may also leave the generator output inconsistent.
- Macro names live in the global preprocessor namespace. Prefixes reduce collisions, but broad inclusion can still conflict with other generated or vendor headers if they choose the same names.
- Several prefixes are compact abbreviations, and some page initials are reused conceptually across the HID specification. Consumers must compare both page and usage rather than assuming a usage macro alone is globally meaningful.
- The file has no version macro or provenance pointer to the exact HID Usage Tables revision used for generation. Reviewers need external process evidence to know whether new HID usages are current.
- Generated spelling is part of the API for BPF source. Fixing a typo-like macro name can break existing BPF programs unless compatibility aliases are provided.

## Test Signals

- BPF build tests should compile all programs under `drivers/hid/bpf/progs/` after regeneration.
- A small compile-only test should include this header in BPF C and compare representative page and usage constants, including `HidUsagePage_Digitizers` and `HidUsage_Dig_PadType`.
- Regeneration tests should diff generated output against the checked-in file and flag manual drift.
- Verifier/load tests for HID-BPF programs should confirm constants are accepted as immediate comparisons and do not require unsupported relocations.
- HID behavior tests should exercise at least one consumer path, such as the generic touchpad descriptor logic, to show the symbolic constants still match parsed usage pages and IDs.
