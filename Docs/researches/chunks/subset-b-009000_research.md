# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 1-6198

Purpose: this chunk is the opening portion of the vendored single-header `nlohmann/json.hpp` 3.12.0 used by WiredTiger tests. It establishes the library version/ABI namespace, portability and compiler-feature macros, public serialization helper macros, forward declarations for `basic_json`, the core JSON type enum, metadata/type-trait machinery, exception classes, conversion overloads for C++/STL types, and the start of binary subtype support. It is infrastructure for the later `basic_json` class definition rather than WiredTiger-specific logic.

Important APIs, types, and functions:

- Version and ABI macros define `NLOHMANN_JSON_VERSION_MAJOR/MINOR/PATCH` as 3.12.0 and construct the inline namespace from version plus ABI-affecting feature flags: diagnostics, diagnostic byte positions, and legacy discarded-value comparison. `NLOHMANN_JSON_NAMESPACE_BEGIN/END` and `NLOHMANN_JSON_NAMESPACE` wrap all exported library symbols.
- `detail::void_t`, `detail::nonesuch`, `detail::detector`, `is_detected`, `detected_t`, `detected_or_t`, `is_detected_exact`, and `is_detected_convertible` provide C++11-compatible SFINAE detection used throughout serializer selection and container compatibility checks.
- The Hedley block defines `JSON_HEDLEY_*` feature probes and attributes for many compilers. It normalizes version checks, pragma support, diagnostic push/pop, cast wrappers, `deprecated`, `warn_unused_result`, `noreturn`, `unreachable`, branch prediction, `malloc`/`pure`/`const`, inline/visibility/nothrow/fallthrough annotations, static assertions, C/C++ linkage helpers, warning/message pragmas, and deprecated compatibility aliases.
- Internal macro-scope configuration detects supported compilers, C++ language level (`JSON_HAS_CPP_11/14/17/20/23`), filesystem availability, ranges, three-way comparison, static RTTI, inline variables, `[[no_unique_address]]`, exception support, user-overridden exception/assert macros, implicit conversions, enum serialization, and global UDL behavior.
- Public serialization macros include `NLOHMANN_JSON_SERIALIZE_ENUM`, `NLOHMANN_DEFINE_TYPE_INTRUSIVE`, `NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE`, their `_WITH_DEFAULT` and `_ONLY_SERIALIZE` variants, and derived-type variants added for 3.12.0. These expand to ADL-visible `to_json`/`from_json` functions using up to 64 listed data members.
- Forward declarations expose `template<class...> class basic_json`, `json_pointer`, `adl_serializer`, aliases `json` and `ordered_json`, and `ordered_map`.
- `detail::value_t` enumerates stored JSON types: `null`, `object`, `array`, `string`, `boolean`, signed/unsigned/float numbers, `binary`, and `discarded`. Its ordering operator implements the library's cross-type ordering with special handling for unordered/discarded cases when C++20 comparison is available.
- JSON Pointer helpers `replace_substring`, `escape`, and `unescape` implement RFC 6901 token escaping for `~` and `/`.
- `detail::position_t` carries parser token position state: total bytes/chars read, current-line character count, and line count. It converts to `size_t` for SAX compatibility.
- C++ future/backfill utilities include `uncvref_t`, `enable_if_t`, C++11 `integer_sequence`/`index_sequence` replacements, `priority_tag`, `static_const`, and `make_array`.
- Iterator and range traits include `iterator_types`, custom `iterator_traits`, `NLOHMANN_CAN_CALL_STD_FUNC_IMPL(begin/end)`, `is_range`, `iterator_t`, and `range_value_t`, avoiding brittle `std::iterator_traits` behavior on older compilers.
- Type traits determine JSON conversion viability: `is_basic_json`, `is_basic_json_context`, `is_json_ref`, `has_from_json`, `has_non_default_from_json`, `has_to_json`, `is_getable`, comparator/key traits, object/array/string constructibility and compatibility, `is_compatible_integer_type`, tuple constructibility, JSON iterator/pointer exclusion, ordered-map detection, integer range checks, C-string detection, and transparent-comparator detection.
- `detail::concat_length`, `concat_into`, and `concat` assemble exception strings efficiently through detected `append`, `+=`, iterator, or data/size APIs.
- Exception classes define the public error taxonomy: `detail::exception`, `parse_error`, `invalid_iterator`, `type_error`, `out_of_range`, and `other_error`. They carry stable integer IDs and formatted `what()` strings. With `JSON_DIAGNOSTICS`, errors include a JSON Pointer-like path by walking parent links; with `JSON_DIAGNOSTIC_POSITIONS`, errors can include byte spans.
- `identity_tag<T>` is a dispatch tag for return-by-value `from_json` overloads, especially non-default-constructible target types.
- `detail::std_fs` aliases either `std::filesystem` or `std::experimental::filesystem` when available.
- `from_json` overloads convert JSON to `nullptr_t`, optional values, booleans, strings, arithmetic types, enum underlying values, `std::forward_list`, `std::valarray`, C arrays up to 4 dimensions, `std::array`, constructible array containers, `binary_t`, constructible object/map-like containers, tuples/pairs, non-string-key `std::map`/`std::unordered_map` represented as arrays of pairs, and filesystem paths. The inline function object `nlohmann::from_json` forwards to ADL-visible overloads.
- `iteration_proxy_value` and `iteration_proxy` implement `items()` support, yielding key/value proxy objects for arrays, objects, and primitives. `std::tuple_size` and `std::tuple_element` specializations plus `get<0/1>` enable structured bindings; ranges builds mark the proxy as a borrowed range.
- `external_constructor<value_t>` specializations centralize mutation of an existing `basic_json` into boolean, string, binary, number, array, and object values. Each destroys the old `m_data.m_value`, sets `m_data.m_type`, installs the new value, updates parent pointers for structured values, and asserts invariants.
- `to_json` overloads convert optional values, booleans including `std::vector<bool>` references, strings, floating-point and integer types, enums, arrays/ranges, `binary_t`, `std::valarray`, objects/maps, non-string C arrays, pairs, `items()` proxy values, tuples, and filesystem paths into a `BasicJsonType`. The inline function object `nlohmann::to_json` forwards to ADL-visible overloads.
- `adl_serializer<ValueType>` delegates `from_json` and `to_json` to the global ADL customization points. This is the default serializer template parameter used by `basic_json`.
- The chunk ends at the beginning of `byte_container_with_subtype<BinaryType>`, declaring `container_type` and `subtype_type`. Its constructors and subtype state are outside this chunk.

Control flow:

- Compile-time control flow dominates the first half of the chunk. Preprocessor checks decide ABI namespace spelling, available standard/library features, exception behavior, and compiler attributes before any `basic_json` code is compiled.
- Conversion selection is mostly SFINAE-driven. Traits check whether a target type looks like an object, array, string, arithmetic type, tuple, path, or user-serializable type; overload resolution then chooses the narrowest matching `from_json`/`to_json` path.
- Runtime conversion functions first validate the source JSON type with predicates such as `is_null`, `is_array`, `is_object`, `is_string`, `is_binary`, or `is_boolean`. Failures throw `type_error::create(302, ...)` through `JSON_THROW`, or abort when exceptions are disabled.
- Array/container conversion usually constructs a temporary container, transforms each JSON element with `get<T>()`, then move-assigns the result. Priority tags prefer exact `array_t`, then fixed `std::array`, then containers with `reserve`, then generic insertable containers.
- Object conversion reads the underlying `object_t` pointer and transforms each key/value pair into the target mapped type through `get<mapped_type>()`.
- Exception diagnostic path construction walks from a leaf JSON node to parents, records array indexes or object keys, escapes path tokens with the JSON Pointer helpers, and prepends that path to the error message.
- `external_constructor` is the key state transition layer for `to_json`: destroy old storage, set type tag, allocate/copy/move the new storage, restore parent links for arrays/objects, and assert invariants.

State and persistence behavior:

- This header has no direct filesystem or database persistence. It is vendored test dependency code compiled into consumers.
- Persistent runtime state belongs to `basic_json` instances, primarily `m_data.m_type`, `m_data.m_value`, optional parent pointers under diagnostics, and optional byte-position metadata under diagnostic-position builds. This chunk manipulates those fields in `external_constructor` and exception diagnostics but does not define the full storage type.
- Macro state is significant. Defining `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_IMPLICIT_CONVERSIONS`, `JSON_DISABLE_ENUM_SERIALIZATION`, `JSON_NOEXCEPTION`, `JSON_THROW_USER`, or namespace/version macros before including the header changes ABI, overloads, exception behavior, or generated functions.
- `iteration_proxy_value` stores iterator position, array index, cached stringified array index, and an empty string for primitive key reporting. This is transient iteration state only.
- Conversion functions mutate caller-provided target containers and scalars. Some clear or replace targets (`forward_list`, `valarray`, maps), while tuple/array identity-tag overloads return new values.

Dependencies:

- Standard library dependencies in this chunk include algorithms, arrays, containers, iterators, memory, strings, tuples, type traits, limits, exceptions, optional when C++17 is enabled, filesystem when available, ranges when available, and comparison when C++20 three-way comparison is available.
- The header depends heavily on compiler predefined macros and feature-test macros. Hedley support spans GCC, Clang, MSVC, Intel, ARM, IBM XL, TI, Cray, IAR, TinyCC, SunPro, Emscripten, and other compiler families.
- Internal dependencies include later `basic_json` APIs and fields: `is_*` predicates, `type_name`, `get_ptr`, `get<T>()`, `at`, `begin/end/rbegin/rend`, `size`, `m_data`, `set_parent(s)`, `assert_invariant`, `create`, parent links, and byte-position accessors. Those definitions are outside or later than this chunk.
- Public integration relies on ADL. User code supplies `to_json`/`from_json` functions in associated namespaces, or uses the `NLOHMANN_DEFINE_*` macros to generate them.
- WiredTiger integration is indirect: test code can include this vendored header without an external package dependency, and any compile flags/macros from WiredTiger's test build affect the generated JSON ABI and behavior.

Integration points:

- The chunk is part of an amalgamated header; comments show original component boundaries such as `adl_serializer.hpp`, `detail/abi_macros.hpp`, `detail/conversions/from_json.hpp`, `detail/exceptions.hpp`, `detail/meta/type_traits.hpp`, and `detail/conversions/to_json.hpp`.
- `NLOHMANN_BASIC_JSON_TPL_DECLARATION` and `NLOHMANN_BASIC_JSON_TPL` are used later to specialize and refer to the configurable `basic_json` template without repeating its long template parameter list.
- `adl_serializer` and the inline `to_json`/`from_json` function objects are the main public customization surface consumed by `basic_json` constructors, assignment, and `get<T>()`.
- `value_t` is the shared type tag used by storage, comparison, iterators, exceptions, parsing, and conversion. Later code depends on the exact enum values and ordering behavior.
- Exception classes are the stable public exception API exposed as nested aliases by `basic_json` later in the file.
- `iteration_proxy` integrates with `basic_json::items()` and C++ structured bindings.
- Filesystem overloads make JSON string conversion interoperate with `std::filesystem::path` when the compiler/runtime combination is accepted by the feature checks.

Risks and edge cases:

- This is third-party vendored code; local edits risk diverging from upstream nlohmann/json behavior and ABI. Version-mixing is partially detected by preprocessor warnings only.
- ABI namespace changes with diagnostics and version macros. Mixing translation units built with different macro settings can produce distinct types or linker surprises.
- `JSON_NOEXCEPTION` turns throws into `std::abort()`, so type errors and parse errors become process termination in exception-disabled builds.
- Numeric conversions use `static_cast` after type validation. Some paths intentionally allow narrowing or signedness-sensitive behavior; `is_compatible_integer_type` limits certain constructor overloads but `from_json` arithmetic extraction can still cast.
- Object and array compatibility traits are intricate and can select surprising overloads for custom containers, especially types that are both range-like and string-like or map-like.
- `std::map`/`std::unordered_map` with non-string keys deserialize from arrays of key/value arrays, not JSON objects; callers expecting object syntax need string-constructible keys.
- `from_json` for fixed C arrays indexes with `at()` but does not first check exact array size in this chunk; short JSON arrays throw through `at`, while extra JSON elements are ignored.
- Exception diagnostics require parent pointers to be maintained accurately. `external_constructor` calls `set_parent(s)` for structured values, but any later code that mutates without maintaining parents can degrade diagnostic paths.
- The Hedley and feature-detection matrix is broad. Unsupported or unusual compiler/library combinations may take fallback paths that compile but lose attributes, diagnostics, filesystem support, or performance hints.
- The assigned range ends mid-`byte_container_with_subtype`, so binary subtype construction/comparison/state behavior is only partially visible here.

Test signals:

- Compile-time coverage is the primary signal: including this header under WiredTiger's supported C++ standard and compiler matrix should pass unsupported-compiler checks, feature detection, and overload resolution.
- Serialization macro tests should cover generated intrusive/non-intrusive, defaulted, serialize-only, enum, and derived-type conversions.
- Conversion tests should exercise primitive type mismatches and confirm `type_error` id 302, numeric casts, enum serialization toggling, optional null/non-null behavior, STL container round trips, tuple/pair round trips, non-string-key map array-pair encoding, filesystem path conversion when enabled, and `items()` structured bindings.
- Diagnostic builds should verify JSON Pointer path escaping (`~` to `~0`, `/` to `~1`) and optional byte-position text in exceptions.
- Exception-disabled builds should be tested separately because error paths abort instead of throwing.
- For WiredTiger specifically, the useful guard is that tests including the vendored header compile without requiring a system nlohmann/json install and without macro conflicts from the broader test build.
