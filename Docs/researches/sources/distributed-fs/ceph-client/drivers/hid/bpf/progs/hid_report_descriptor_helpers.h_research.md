# sources/distributed-fs/ceph-client/drivers/hid/bpf/progs/hid_report_descriptor_helpers.h

Purpose: This header defines compact, BPF-friendly data structures for parsed HID report descriptors. The structures let HID-BPF programs reason about reports, fields, collections, usages, logical ranges, and field flags without parsing raw descriptor bytes themselves.

Important APIs/types/functions: `HID_MAX_COLLECTIONS`, `HID_MAX_FIELDS`, and `HID_MAX_REPORTS` bound descriptor representation sizes. `enum hid_rdesc_field_type` distinguishes variable, array, and constant fields. `struct hid_rdesc_collection` stores usage page, usage ID, and collection type. `struct hid_rdesc_field` stores field type, collection count, bit start/end offsets, usage page, variable usage ID or array usage min/max, signed logical min/max, flag bits for relative/wrap/nonlinear/no-preferred/null/volatile/buffered/reserved, and an inline array of collections. `struct hid_rdesc_report` stores report ID, size in bits, field count, and field array. `struct hid_rdesc_descriptor` stores counts and arrays for input, output, and feature reports.

Control flow: There is no executable control flow in this file. It provides packed layout definitions consumed by helper functions and HID-BPF programs that receive or store parsed descriptor data.

State and persistence: The header has no global state. Instances of these structs may be produced by parser code elsewhere or embedded in maps/program data by HID-BPF users. Fields are packed to keep ABI layout stable and compact for BPF access.

Dependencies and integration points: It depends on integer types from `vmlinux.h` and compiler attributes. `hid_bpf_helpers.h` uses these definitions for `field_start_byte()`, `field_end_byte()`, `extract_bits()`, and descriptor iterator macros. Programs that inspect descriptor semantics rely on the max-count constants matching parser output and verifier loop bounds.

Risks: Fixed maximum counts can truncate complex descriptors if parser code does not report overflow clearly. Packed structs may create unaligned access concerns on some targets, so generated BPF access patterns need compiler/verifier coverage. The flag bit for `is_volatile` is documented as not populated and always zero, which callers must not treat as authoritative output/feature volatility. Any ABI drift between parser producers and these structures would break descriptor introspection.

Test signals: Compile-time size/layout checks, parser tests for descriptors with many reports/fields/collections, iterator tests that respect maximum counts, field bit-offset extraction tests, and big/little endian build coverage for consumers that read packed integer fields.
