# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 21068-25716

## Purpose

This chunk is the closing portion of XRootD's bundled nlohmann JSON 3.12.0 single-header implementation. It completes `basic_json`'s public API surface: explicit array/object/binary construction, copy/move lifetime handling, type inspection, conversion/access helpers, element access and mutation, lookup/iteration/capacity utilities, comparison, text and binary serialization/deserialization, JSON Pointer, JSON Patch, JSON Merge Patch, user-defined literals, `std` integrations, and final macro cleanup.

Within XRootD this header provides a self-contained JSON dependency under `src/XrdOuc`, so callers can parse, build, inspect, serialize, diff, patch, and convert JSON values without linking a separate JSON library. The code is generic upstream library code rather than XRootD-specific business logic, but it is an integration point for any XRootD component using `nlohmann::json` through this vendored header.

## Important APIs, Types, and Functions

- `basic_json::binary(...)` explicitly constructs `value_t::binary` values from a `binary_t::container_type`, optionally with a subtype. Both copy and move overloads are present.
- `basic_json::array(...)` and `basic_json::object(...)` force initializer-list construction into array or object mode.
- `basic_json(size_type cnt, const basic_json& val)` constructs an array with repeated values; `basic_json(InputIT first, InputIT last)` constructs a value from compatible JSON iterators and validates primitive iterator ranges.
- Copy/move constructors, assignment, and destructor manage `m_data`, diagnostic positions, parent pointers, and invariant checks.
- Type inspection APIs include `dump`, `type`, `is_primitive`, `is_structured`, `is_null`, `is_boolean`, number/string/object/array/binary/discarded checks, and implicit `operator value_t`.
- Value access APIs include `get`, `get_to`, `get_ref`, `get_ptr`, `get_binary`, implicit `operator ValueType`, and serializer-driven `JSONSerializer<ValueType>::from_json` dispatch.
- Element access APIs include `at(index)`, `at(key)`, `operator[](index)`, `operator[](key)`, JSON Pointer overloads, and `value(key_or_pointer, default)`.
- Mutation APIs include `erase`, `clear`, `push_back`, `operator+=`, `emplace_back`, `emplace`, `insert`, `update`, and `swap`.
- Lookup and iteration APIs include `find`, `count`, `contains`, `begin/end/cbegin/cend`, reverse iterators, `items`, and deprecated `iterator_wrapper`.
- Serialization/deserialization includes stream operators, `parse`, `accept`, `sax_parse`, `type_name`, binary writers/readers for CBOR, MessagePack, UBJSON, BJData, and BSON.
- JSON Pointer functions expose unchecked/checked pointer access, `flatten`, and `unflatten`.
- JSON Patch and Merge Patch APIs include `patch_inplace`, `patch`, static `diff`, and `merge_patch`.
- Nonmember support adds `nlohmann::to_string`, `_json` and `_json_pointer` literals, `std::hash<nlohmann::json>`, `std::less<value_t>`, and pre-C++20 `std::swap` specialization.

## Control Flow

Construction and assignment set `m_data.m_type` first, populate the matching `json_value` union arm, then call `set_parents()` and `assert_invariant()` where needed. Iterator-range construction rejects incompatible iterators, enforces full primitive ranges, copies primitive payloads directly, and creates new container storage for arrays/objects.

Access paths are strongly type-gated. `at()` performs type checks and range/key checks, throwing library exceptions with specific error IDs. Non-const `operator[]` has mutating semantics: null values are implicitly converted into arrays or objects, array access resizes with null fillers when the index is beyond the current size, and object access inserts `null` for missing keys. Const `operator[]` assumes the key/index is valid for the active type.

Conversion dispatch uses SFINAE priority tags. Pointer requests delegate to `get_ptr`; default-constructible target types use `JSONSerializer::from_json(json, out)`, non-default-constructible targets use a returning `from_json(json)`, JSON types copy `*this`, and reference access validates pointer compatibility.

Container mutation validates iterator ownership and target type before modifying storage. Array insertion centralizes through `insert_iterator`, which computes a stable offset before insertion and refreshes parent links afterwards. Object `update` can either overwrite keys or recursively merge object-valued keys when `merge_objects` is true.

JSON Patch applies operations sequentially to `*this` in `patch_inplace`. It first requires the patch document to be an array of objects, extracts typed members (`op`, `path`, `value`, `from`) through a local validator, maps operation strings to an enum, and executes add/remove/replace/move/copy/test. Add handles root replacement, object insertion, array append via `-`, and bounded array insertion. Remove finds object keys or erases array indices. Move copies the source value, removes it, then adds it at the target. Test compares with `operator==` and throws on mismatch. `patch` is the copy-on-write wrapper around `patch_inplace`.

`diff` recursively builds an RFC6902-style patch. Equal values produce an empty patch; type changes produce root/path replacement; arrays recurse over common indices, emit removals before additions for trailing source elements, and append trailing target elements at `/-`; objects recurse over shared keys, remove missing source keys, and add target-only keys.

`merge_patch` follows RFC7396-style behavior: object patches force the target to an object, null-valued members erase keys, non-null members recurse through `operator[]`, and non-object patches replace the target entirely.

## State and Persistence Behavior

Persistent state is the `data m_data` member, which contains `value_t m_type` and `json_value m_value`. The nested `data` destructor destroys the active union member according to `m_type`. Copy construction deep-copies heap-backed objects, arrays, strings, and binary values; move construction transfers `m_data` and nulls out the moved-from value. Assignment uses copy-and-swap semantics.

When `JSON_DIAGNOSTICS` is enabled, values track `m_parent`; resizing, insertion, swapping, copying, moving, and updates refresh parent links. When `JSON_DIAGNOSTIC_POSITIONS` is enabled, parse position fields are copied/moved/swapped and exposed via `start_pos()` and `end_pos()`.

The code does not persist data to disk by itself. Persistence-facing behavior is serialization through `dump`, stream `operator<<`, binary `to_*` functions, and parsing/deserialization through `parse`, stream `operator>>`, `from_*`, and SAX APIs. Failed binary parses return `value_t::discarded` when exceptions are disabled; text parse behavior depends on `allow_exceptions`.

## Dependencies and Integration Points

This code depends on the earlier portions of the same header for `value_t`, `json_value`, allocators, `binary_t`, `serializer`, `parser`, `binary_writer`, `binary_reader`, `json_pointer`, iterator types, `iteration_proxy`, diagnostics helpers, exception classes, SFINAE traits, `input_adapter`, and `output_adapter`.

It integrates with the C++ standard library via containers, iterators, allocators, streams, `std::hash`, `std::less`, `std::swap`, type traits, partial ordering when C++20 comparison is available, and optional `char8_t` literal overloads. It is controlled by compile-time macros such as `JSON_NO_IO`, `JSON_HAS_CPP_14/17/20`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_GLOBAL_UDLS`, and `JSON_TEST_KEEP_MACROS`.

For XRootD code, practical integration points are any component that includes `XrdOucJson.hh` and uses `nlohmann::json` for configuration, protocol payloads, logging payloads, or structured metadata. The final macro cleanup also matters to integration: most JSON/Hedley macros are undefined at the end of the header to avoid leaking into XRootD translation units.

## Risks and Edge Cases

- `operator[]` is intentionally mutating for null/object/array values; callers that only intend lookup should prefer `at`, `find`, `contains`, or `value` to avoid implicit object/array creation or array expansion.
- Const object `operator[]` asserts key existence rather than returning a default; using it for unchecked lookup can fail under assertions or become undefined if assumptions are wrong.
- `get_ptr`, `get_ref`, and `get_binary` expose or return references to internal storage. Pointers/references become invalid after mutations that reallocate or change the active value.
- Numeric comparison casts mixed signed/unsigned values through `number_integer_t` in some cases, which is upstream behavior but can be surprising around large unsigned values. Floating NaN and discarded values are treated as unordered.
- JSON Patch is not transactional in `patch_inplace`; operations before a later failing operation remain applied. `patch` should be used when callers need the original value preserved on failure.
- `patch_inplace` assumes each patch element is an object before `get_value` uses `val.m_data.m_value.object`; the explicit object check protects that path, but refactoring order would be risky.
- Binary parse APIs return `discarded` on failure when configured not to throw, so callers must check `is_discarded()` before using the result.
- Stream operators and deprecated overloads are gated by `JSON_NO_IO`; builds disabling I/O lose those integration points.
- Macro cleanup is broad. Translation units relying on JSON macros after including this header must opt into `JSON_TEST_KEEP_MACROS` or include/order code carefully.

## Test Signals

Useful coverage for XRootD's vendored copy should include compile-only tests across the supported compiler modes and macro configurations used by the project, especially with and without `JSON_NO_IO`, diagnostics, and C++20 comparisons. Behavioral tests should exercise parsing/dumping round trips, `at` versus `operator[]` behavior, defaulted `value` lookups, iterator-range construction and invalid iterator errors, object updates with and without recursive merging, JSON Pointer flatten/unflatten, all JSON Patch operations including failure cases, Merge Patch key deletion/replacement, and binary format round trips for CBOR/MessagePack/UBJSON/BJData/BSON.

Regression signals include exception IDs/messages for type/range errors, preservation of parent diagnostics after resize/insert/swap/update, `discarded` results when binary parse failures are non-throwing, NaN/discarded comparison behavior, literal parsing for `_json` and `_json_pointer`, and successful inclusion of the header without leaking macros into downstream XRootD code.
