# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 1-6194

## Purpose

This chunk is the opening slice of XRootD's local `XrdOucJson.hh` wrapper for nlohmann/json. If `USE_SYSTEM_NLOHMANN_JSON` is defined, the header delegates to `<nlohmann/json.hpp>`; otherwise it embeds the beginning of the single-header nlohmann/json 3.12.0 amalgamation. The covered range does not yet contain the full `basic_json` class body, parser, serializer, or public aliases at the end of the amalgamation. It establishes the ABI namespace, compiler-feature compatibility layer, type traits, exception classes, and the first `from_json` / `to_json` conversion helpers used later by the public JSON type.

For XRootD, this file is a vendored dependency boundary: code can include one XRootD-owned header and either use the system nlohmann/json package or a fixed bundled implementation with the same API surface. This reduces build-time dependency requirements while preserving a switch for distributions that prefer system libraries.

## Important APIs, Types, And Macros

- `USE_SYSTEM_NLOHMANN_JSON`: build switch at the top of the file. When enabled, all bundled code in this chunk is bypassed and the system nlohmann/json header defines the API.
- `NLOHMANN_JSON_VERSION_MAJOR/MINOR/PATCH`: pins the vendored implementation to `3.12.0` and warns if another nlohmann/json version was already included.
- `NLOHMANN_JSON_NAMESPACE`, `NLOHMANN_JSON_NAMESPACE_BEGIN`, and `NLOHMANN_JSON_NAMESPACE_END`: construct the inline ABI namespace under `nlohmann`, incorporating version and ABI tags for diagnostics, diagnostic byte positions, and legacy discarded-value comparison.
- `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, and `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`: compile-time ABI-affecting feature flags. Changing them changes namespace tagging and therefore type/link compatibility.
- `detail::nonesuch`, `detail::detector`, `is_detected`, `detected_t`, `detected_or_t`, `is_detected_exact`, and `is_detected_convertible`: C++11-compatible detection idiom used throughout the rest of the header to enable or suppress overloads by available methods and nested types.
- Hedley-derived `JSON_HEDLEY_*` macros: compiler and feature probes for GCC, Clang, MSVC, Intel, ARM, TI, IBM, SunPro, IAR, etc. They normalize attributes, pragmas, casts, fallthrough annotations, branch prediction, no-return, visibility, deprecation, `nodiscard`, constexpr, inline behavior, diagnostic push/pop, and unsupported compiler checks.
- `JSON_HAS_CPP_11/14/17/20/23/26`, `JSON_HAS_FILESYSTEM`, `JSON_HAS_EXPERIMENTAL_FILESYSTEM`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_HAS_RANGES`, and `JSON_HAS_STATIC_RTTI`: local feature macros that conditionally expose optional, filesystem, ranges, and comparison support.
- `JSON_THROW`, `JSON_TRY`, `JSON_CATCH`, `JSON_INTERNAL_CATCH`, and `JSON_ASSERT`: exception and assertion indirection points. With exceptions disabled or `JSON_NOEXCEPTION`, throwing aborts unless the user overrides these macros.
- `NLOHMANN_JSON_SERIALIZE_ENUM`: public macro that generates `to_json` and `from_json` overloads for enum mapping tables.
- `NLOHMANN_DEFINE_TYPE_*` and `NLOHMANN_DEFINE_DERIVED_TYPE_*`: macro families that generate intrusive or non-intrusive object field serialization hooks for user-defined types.
- `detail::value_t`: internal JSON type enum with entries for null, object, array, string, boolean, signed integer, unsigned integer, floating point, binary, and discarded values.
- `detail::replace_substring`, `detail::escape`, and `detail::unescape`: RFC 6901 JSON Pointer token escaping helpers.
- `detail::position_t`: line/column/byte counter structure used by parse errors and SAX-style position reporting.
- `detail::enable_if_t`, `index_sequence`, `make_index_sequence`, `priority_tag`, `static_const`, and `make_array`: C++11/C++14 compatibility utilities used to keep the library usable across older toolchains.
- `json_fwd.hpp` declarations: forward-declare `adl_serializer`, `basic_json`, `json_pointer`, `ordered_map`, and aliases `json` / `ordered_json`.
- `detail::exception`, `parse_error`, `invalid_iterator`, `type_error`, `out_of_range`, and `other_error`: nlohmann/json exception hierarchy with stable numeric `id` fields and formatted `what()` messages.
- `detail::from_json` overload set and `detail::to_json` overload set: conversion functions for primitives, strings, arrays, objects, tuples, pairs, C arrays, optional values, filesystem paths, valarrays, maps with non-string keys, and enum values.
- `detail::from_json_fn` / `detail::to_json_fn` and inline `nlohmann::from_json` / `nlohmann::to_json` function objects: ADL-friendly dispatch objects used by `adl_serializer` and `basic_json::get`.
- `detail::iteration_proxy_value` and `detail::iteration_proxy`: helper backing `items()` iteration, including structured binding support via `std::tuple_size` and `std::tuple_element` specializations.
- `detail::external_constructor<value_t::...>` specializations: low-level constructors that mutate `basic_json` storage for booleans, strings, binary values, numbers, arrays, and objects.

## Control Flow

The first control-flow decision is purely preprocessor-driven. `USE_SYSTEM_NLOHMANN_JSON` includes the system header and skips the bundled implementation. Otherwise, the file enters the nlohmann/json include guard and starts expanding embedded logical headers in the same order as the upstream amalgamation.

Within the bundled path, the setup flow is:

1. Define version and ABI namespace macros, including ABI tag components selected by diagnostics-related flags.
2. Include standard-library headers required by early conversion, exception, and meta-programming code.
3. Define the detection idiom and Hedley portability macros.
4. Validate compiler support unless `JSON_SKIP_UNSUPPORTED_COMPILER_CHECK` is defined.
5. Detect C++ language/library features and configure exception/assertion indirection.
6. Define serialization helper macros for enum and user-defined type mappings.
7. Define `value_t`, JSON Pointer string escaping, token position state, and C++ compatibility helpers.
8. Forward-declare the public JSON templates and aliases.
9. Define type traits that choose later overloads for arrays, objects, strings, maps, iterators, JSON pointers, transparent object keys, enum conversions, integer range checks, and user-provided ADL serializers.
10. Define exception classes and conversion helpers.

Runtime control flow in this chunk appears mostly in conversion helpers:

- `from_json` verifies the stored JSON type with predicates such as `is_null()`, `is_string()`, `is_array()`, `is_object()`, `is_binary()`, and `is_boolean()`. Type mismatches throw `detail::type_error::create(302, ...)`.
- Numeric extraction uses `get_arithmetic_value`, switching on `value_t` and reading the correct stored numeric pointer. General arithmetic conversions also accept boolean input, while the explicit numeric template parameters do not.
- Array extraction uses overload priority. Native `array_t` copies directly; `std::array` and C arrays use indexed `at()` access; containers with `reserve()` allocate once then insert transformed elements; other insertable containers fall back to inserter-based population.
- Object extraction checks that the JSON value is an object, iterates the internal `object_t`, converts each mapped value, and inserts into the requested object-like container. Maps/unordered maps with non-string keys are represented as arrays of two-element arrays.
- Tuple and pair extraction treats JSON arrays as positional tuples, using `index_sequence` to call `at(N).get<T>()`.
- `to_json` selects a constructor path through SFINAE. Primitive values call the matching `external_constructor`, compatible ranges become arrays, compatible object types become objects, tuples and pairs become arrays, optional empty values become null, and filesystem paths become UTF-8 strings when filesystem support is enabled.
- `external_constructor` specializations always destroy the old `basic_json` union member before assigning the new type, then reset parent pointers for arrays/objects when diagnostics need parent tracking.

## State And Persistence Behavior

This chunk does not persist application data and does not perform I/O. Its state is compile-time configuration and in-memory JSON object mutation.

The relevant persistent contract is ABI and source compatibility. The inline namespace is versioned as `json_abi..._v3_12_0` unless disabled by macros. Diagnostics-related flags are part of the namespace tag, so object files compiled with different settings can refer to different nlohmann/json types. The `USE_SYSTEM_NLOHMANN_JSON` path is another compatibility boundary: the actual implementation and bug behavior can differ from the vendored 3.12.0 copy if the system package is a different release.

The runtime state touched in this range is `basic_json`'s internal `m_data.m_type` and `m_data.m_value`, though the full class is defined later. `external_constructor` functions explicitly destroy the existing value before replacing it, preserving memory ownership for heap-backed strings, arrays, objects, and binary values. Array/object construction calls `set_parents()` or `set_parent()` so diagnostic paths can be reconstructed when `JSON_DIAGNOSTICS` is enabled.

Exceptions store formatted messages inside a `std::runtime_error` member. `parse_error` additionally persists a byte position. With `JSON_DIAGNOSTIC_POSITIONS`, exception formatting can include start/end byte ranges from the leaf JSON element.

## Dependencies

The covered range depends only on the C++ standard library and optional compiler/library features. It includes or conditionally references algorithms, arrays, maps, unordered maps, forward lists, valarrays, vectors, tuples, strings, memory, iterators, type traits, exceptions, limits, cstddef/cstdint, filesystem or experimental filesystem, optional, compare, ranges, and string view.

The code also embeds third-party Hedley compatibility macros and a small Abseil-derived C++11 `integer_sequence` replacement. These are header-local compatibility dependencies rather than linked libraries.

If `USE_SYSTEM_NLOHMANN_JSON` is active, the dependency moves to the system-provided nlohmann/json installation. That can affect available APIs, namespace versioning, warnings, defects, and transitive standard-library requirements.

## Integration Points

- XRootD source code includes this header as the project-local JSON API. Downstream users see nlohmann/json names, not XRootD-specific wrapper types.
- Build systems and packagers can choose bundled versus system nlohmann/json by defining or omitting `USE_SYSTEM_NLOHMANN_JSON`.
- User code can provide ADL `to_json` / `from_json` overloads or specialize `adl_serializer`; the traits in this chunk are what discover those hooks.
- User code can opt into enum/object serialization macros defined here, which generate overloads in the surrounding namespace.
- Later parts of the same header depend on `value_t`, exception types, type traits, `external_constructor`, and conversion functions when implementing `basic_json` constructors, `get`, parser errors, iterators, JSON Pointer, serialization, and binary formats.
- Filesystem integration is conditional. When detected, `std::filesystem::path` or `std::experimental::filesystem::path` converts to/from UTF-8 JSON strings.
- `items()` integration is partly defined here through `iteration_proxy`, including support for structured bindings like `for (auto& [key, value] : j.items())`.

## Risks And Maintenance Notes

- Vendored/system divergence is the central risk. The bundled code is 3.12.0, but `USE_SYSTEM_NLOHMANN_JSON` can select another version with different overload resolution, diagnostics, bug fixes, or ABI namespace tags.
- ABI-affecting macros must be consistent across all translation units. Mixing `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`, or namespace-version settings can create incompatible JSON types.
- `JSON_NOEXCEPTION` changes failure behavior from throwing typed exceptions to `std::abort()` unless user macros replace `JSON_THROW`. XRootD code that expects parse/type errors to be recoverable must ensure exceptions are enabled or overridden appropriately.
- Numeric conversions in `from_json` use `static_cast` after selecting numeric storage. Some narrowing, sign, and floating/integer conversions are permitted by design and may not report overflow.
- Object/array conversion is heavily SFINAE-driven. New custom containers can be classified unexpectedly if they expose `begin`/`end`, `mapped_type`, `key_type`, `value_type`, transparent comparators, or string-like constructors.
- `std::map` and `std::unordered_map` with non-string keys serialize as arrays of pairs, not JSON objects. Consumers expecting object syntax can break when key types change from string-like to non-string-like.
- The exception diagnostic path walks parent pointers and object/array contents. Parent tracking must stay correct after any future edits to constructors or mutation paths.
- The header specializes `std::tuple_size` and `std::tuple_element` for `iteration_proxy_value`, which is allowed for user-defined types but sensitive to namespace and include-order issues.
- Compiler compatibility macros are broad and old-toolchain-oriented. Local edits to this region are risky because small macro changes can affect every downstream overload, warning state, or language-feature branch.

## Test Signals

Useful signals for this chunk are compile- and behavior-oriented:

- Build XRootD both with the bundled header and with `USE_SYSTEM_NLOHMANN_JSON` against the supported system nlohmann/json package.
- Compile translation units that include `XrdOucJson.hh` under the project's minimum and common modern C++ standards to exercise `JSON_HAS_CPP_*` branches.
- Exercise JSON parsing/getting paths that throw `parse_error`, `type_error`, and `out_of_range`, confirming exception IDs and messages remain compatible with callers.
- Round-trip primitive values, strings, binary values, vectors, maps, unordered maps, pairs, tuples, `std::array`, C arrays, enums, optional values, and filesystem paths where enabled.
- Verify `items()` iteration and structured bindings over arrays, objects, and primitive values.
- Run builds with diagnostics toggles if XRootD supports them, because those flags affect both exception content and ABI namespace selection.
- Watch for compiler warnings around this header after toolchain upgrades; the Hedley and diagnostic suppression blocks are intended to keep header-only use quiet across many compilers.
