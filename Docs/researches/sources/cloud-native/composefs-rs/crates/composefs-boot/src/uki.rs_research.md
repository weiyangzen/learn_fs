# sources/cloud-native/composefs-rs/crates/composefs-boot/src/uki.rs

## Purpose
This module parses the PE/EFI container structure used by Unified Kernel Images and extracts embedded text sections such as `.osrel` and `.cmdline`. It provides boot-label and command-line helpers for Type 2 BLS/UKI workflows.

## Important APIs, types, and functions
`DosStub`, `CoffFileHeader`, `PeHeader`, and `SectionHeader` are zerocopy representations of the PE structures needed for section lookup. `UkiError` distinguishes I/O failures, invalid PE data, missing sections, invalid UTF-8, and missing os-release name data.

`get_section(image, section_name)` parses an in-memory byte slice and returns a raw borrowed section. `get_section_buffered(reader, section_name)` performs the same lookup on a `Read + Seek` stream and returns owned bytes. `get_text_section` and `get_text_section_buffered` add UTF-8 validation. `get_boot_label` and `get_boot_label_buffered` extract `.osrel` and feed it to `OsReleaseInfo`. `get_cmdline` and `get_cmdline_buffered` extract `.cmdline`.

## Control flow
Section extraction constructs an 8-byte padded section-name key, reads the DOS stub to find the PE header offset, verifies the `PE\0\0` magic, skips the optional header, reads the declared section headers, and compares section names. In-memory parsing returns `None` for structurally invalid PE data and `Some(Err(MissingSection))` for valid PE files without the requested section. The public text helpers map invalid structure to `PortableExecutableError`.

## State and persistence behavior
The module does not persist data. Slice-based functions borrow from the input image. Buffered functions seek and read from the supplied stream, changing its cursor position. All parsed metadata is transient.

## Dependencies and integration points
It uses `zerocopy` little-endian wrappers for safe binary parsing and `thiserror` for public error reporting. `write_boot.rs` uses `get_cmdline` to validate that UKI `.cmdline` includes the expected composefs root hash. `get_boot_label` integrates with `os_release.rs` for display names. `bootloader.rs` discovers UKI files but leaves PE section parsing to this module.

## Risks
`section_name.len() > 8` will panic due to fixed PE section-name storage. Section extraction uses `virtual_size` rather than `size_of_raw_data`, which may be incorrect for malformed or unusual PE files. The in-memory API collapses several parse failures into `PortableExecutableError`, while buffered parsing reports some zerocopy failures as I/O errors. The code does not validate machine type, optional header contents, signatures, or UKI-specific required section sets beyond the requested section.

## Test signals
Tests synthesize PE-like byte arrays and cover successful boot-label extraction, buffered/slice parity, invalid PE data, missing `.osrel`, bad section offsets, raw and text extraction for `.osrel` and `.cmdline`, missing arbitrary sections, and invalid UTF-8. There is no test with a real UKI fixture.
