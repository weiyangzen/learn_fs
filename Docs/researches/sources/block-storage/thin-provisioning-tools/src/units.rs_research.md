# File Research: sources/block-storage/thin-provisioning-tools/src/units.rs

## Purpose
Defines storage unit parsing, display, byte conversion, and pretty-print sizing utilities used by command-line options and output.

## Main Components
- `Units` enum covers bytes, 512-byte sectors, decimal SI units through exabytes, and binary IEC units through exbibytes.
- `Units::size_bytes()` maps each unit to its byte multiplier.
- `Units::to_string_short()` returns display suffixes such as `b`, `s`, `KiB`, `MB`, and `EiB`.
- `Units::to_letter()` returns legacy one-letter suffixes, using lowercase for binary prefixes and uppercase for decimal prefixes.
- `FromStr for Units` accepts long names, short names, and legacy letters.
- `Display for Units` emits long unit names.
- `to_units()` converts byte counts to an `f64` in the requested unit.
- `StorageSize` pairs a multiple with a unit and validates against `u64` byte overflow.
- `FromStr for StorageSize` parses leading digits plus optional unit, defaulting unitless values to sectors.
- `to_pretty_print_size()` chooses a rounded binary unit/multiple intended to keep values at or below 8192 where possible.
- Embedded tests cover parsing, overflow rejection, round-tripping, and pretty-print edge cases.

## Behavior
`StorageSize::new()` prevents overflow by checking `multiple <= u64::MAX / unit.size_bytes()`. `size_bytes()` can therefore multiply directly. Unitless strings represent sectors, preserving block-device convention.

Pretty-printing uses binary units only. It chooses an initial unit from the highest set bit, shifts to get a multiple, and rounds into the next unit when the multiple exceeds 8192. It may return a rounded value whose exact byte equivalent exceeds `u64::MAX`, so it returns `(u64, Units)` rather than `StorageSize`.

## Compatibility Details
The parser intentionally distinguishes decimal uppercase legacy letters (`K`, `M`, `G`, etc.) from binary lowercase letters (`k`, `m`, `g`, etc.). It also accepts IEC spellings like `KiB`.

## Research Notes
There are small display inconsistencies in the file: `to_string_short()` returns `"Tib"` for `Tebibyte`, while parser support uses `"TiB"`; `Display for Units` returns `"terabyte"` for `Kibibyte`'s `Tebibyte` variant. Tests do not cover those display strings.
