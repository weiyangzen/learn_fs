<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.h -->
# sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.h

## Purpose
Declares the lightweight util-linux JSON writer API and convenience macros.

## Important APIs and Types
Defines `UL_JSON_OBJECT`, `UL_JSON_ARRAY`, `UL_JSON_VALUE`, `struct ul_jsonwrt`, open/close/empty/flush functions, root/array/object/value macros, and typed value writers.

## Control Flow
The header has no runtime logic beyond macro aliases that specialize `ul_jsonwrt_open`, `ul_jsonwrt_close`, and `ul_jsonwrt_empty` by JSON element type.

## State and Persistence
The writer state consists of a target `FILE`, indentation integer, and `after_close` bit. Output persists to the stream chosen by the caller.

## Dependencies and Integration Points
Includes stdio and stdint. Used by command code that needs JSON without pulling in a heavier JSON library.

## Risks
The API is procedural and trusts callers to maintain valid nesting. Raw-value output is intentionally unsafe for untrusted strings.

## Test Signals
Compile tests plus CLI JSON parse tests from consumers such as admin status cover this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.h -->
