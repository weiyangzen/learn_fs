# File Research: sources/block-storage/thin-provisioning-tools/src/xml.rs

## Purpose
Provides shared XML attribute parsing and construction helpers used by thin metadata XML code and likely other XML readers/writers in the crate.

## Main Components
- `string_val()` unescapes an attribute value and returns it as `String`.
- `parse_val<T>()` parses raw attribute bytes as UTF-8 and then as `T`.
- `u64_val()`, `u32_val()`, and `bool_val()` specialize numeric/boolean parsing.
- `bad_attr()` returns a formatted error for unknown attributes.
- `check_attr()` unwraps required attributes or reports a missing-attribute error.
- `missing_attr()` formats the missing-attribute error.
- `mk_attr()` creates a `quick_xml::Attribute` from a byte key and displayable value.
- `mk_attr_()` formats a displayable value into owned bytes.

## Behavior
String values are XML-unescaped, while numeric and boolean values are parsed from raw attribute bytes. Writer helpers format values with `Display` and store them in owned byte buffers.

## Dependencies and Interactions
This file is the low-level companion to `thin/xml.rs`. It depends on `quick_xml` attribute and name types, `Cow`, `Display`, and `anyhow`.

## Research Notes
The error strings have minor formatting issues: unknown-attribute output joins `"attribute "` and `"in tag"` through an optional attribute-name fragment, and missing-attribute output omits the closing quote after the tag name. These are presentation issues, not parser behavior issues.
