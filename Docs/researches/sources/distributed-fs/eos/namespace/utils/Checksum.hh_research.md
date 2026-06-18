# sources/distributed-fs/eos/namespace/utils/Checksum.hh

## Purpose
`Checksum.hh` provides inline namespace checksum formatting and hex parsing helpers for file metadata and protobuf metadata.

## Important APIs, Types, and Functions
`appendChecksumOnStringAsHexNoFmd()` formats a `Buffer` into hexadecimal according to a layout ID's nominal checksum length, optional separator, and optional override length. `appendChecksumOnStringAsHex()` adapts that logic to an `IFileMD`. `appendChecksumOnStringProtobuf()` adapts protobuf checksum bytes into a `Buffer`. `hexArrayToByteArray()` overloads parse hex strings into raw byte strings.

## Control Flow
Formatting determines the layout's checksum length through `LayoutId::GetChecksumLen()`, chooses either the nominal or override target length, then appends two lowercase hex characters per byte. If target length exceeds the nominal checksum length, zeros are emitted. Separators are inserted between bytes when requested. The function returns false only when the nominal checksum length is zero. Hex parsing requires even length, converts two characters at a time with `strtol(..., 16)`, and clears output on parse failure.

## State and Persistence Behavior
All helpers are stateless and operate on caller-provided output strings. They do not modify metadata.

## Dependencies and Integration Points
The helpers depend on layout encoding, protobuf `FileMdProto`, `Buffer`, and `IFileMD`. They are used by etag generation, printing, and tests that need stable checksum text.

## Risks and Edge Cases
Formatting pads missing checksum bytes with zeros to preserve compatibility, which can hide truncated checksum storage in display paths. `appendChecksumOnStringProtobuf()` copies protobuf bytes into a mutable buffer before formatting. Hex parsing pushes a byte before checking whether `strtol` consumed both characters, then clears on failure; this is safe for output but noteworthy. `strtol` accepts signs and whitespace if present in the two-character slice in standard C semantics, though full two-character consumption limits most invalid forms.

## Test Signals
`VariousTests.cc` covers MD5 and CRC32 formatting, separators, override length padding, null `IFileMD`, and hex parsing for invalid and mixed-case input.
