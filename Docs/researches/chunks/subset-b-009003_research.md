# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 21116-25526

## Scope

This chunk covers the tail of the vendored `nlohmann::json` single-header implementation used under WiredTiger tests. The range starts inside the iterator-range constructor for `basic_json`, then covers most public `basic_json` value lifecycle, inspection, conversion, element access, lookup, iterator, capacity, modifier, comparison, text/binary serialization, parse, JSON Pointer, JSON Patch, and Merge Patch APIs. It ends with user-defined literals, `std` specializations, optional global UDL exports, and macro cleanup for the amalgamated header.

The file is third-party code, not WiredTiger-native logic. Changes should normally come from updating the vendored nlohmann/json release rather than editing this range by hand.

## Purpose

The code in this chunk is the operational surface of `basic_json`: it defines how JSON values are copied, moved, serialized, parsed, inspected, converted to C++ types, accessed like arrays/objects, mutated, compared, patched, and translated to or from binary encodings. WiredTiger test code can include this header to build test JSON data, consume JSON test fixtures, compare generated JSON, or serialize diagnostics without depending on a system-installed nlohmann/json package.

The chunk also closes the header cleanly for consumers. It provides literals such as `"_json"`, nonmember support such as `std::hash<nlohmann::json>`, and then undefines the many feature-detection and portability macros introduced earlier in the amalgamated file.

## Important APIs, Types, and Data

- `basic_json(const basic_json&)`, `basic_json(basic_json&&)`, `operator=(basic_json)`, and `~basic_json()`: manage deep copy, move invalidation, copy/swap assignment, invariant checks, diagnostic position transfer, and destruction through the `data`/`json_value` storage layer.
- `dump(indent, indent_char, ensure_ascii, error_handler)`: serializes a value to `string_t` through `serializer` and `detail::output_adapter`.
- Type inspection helpers: `type()`, `is_null()`, `is_boolean()`, `is_number()`, `is_number_integer()`, `is_number_unsigned()`, `is_number_float()`, `is_object()`, `is_array()`, `is_string()`, `is_binary()`, `is_discarded()`, `is_primitive()`, `is_structured()`, and implicit `operator value_t()`.
- Value access: `get_ptr<T*>()`, `get<T>()`, `get_to(T&)`, `get_ref<T&>()`, implicit conversion `operator ValueType()`, and `get_binary()`. These route through SFINAE-selected `get_impl` overloads and `JSONSerializer<ValueType>::from_json`.
- Element access: `at(index)`, `at(key)`, `operator[](index)`, `operator[](key)`, `value(key, default)`, `value(json_pointer, default)`, `front()`, and `back()`.
- Erase and lookup: iterator/range/key/index `erase`, `find`, `count`, and `contains`, including transparent-key and JSON Pointer overloads where enabled.
- Iteration and capacity: `begin`, `end`, `cbegin`, `cend`, reverse iterators, `items()`, deprecated `iterator_wrapper`, `empty`, `size`, and `max_size`.
- Modifiers: `clear`, `push_back`, `operator+=`, `emplace_back`, `emplace`, array `insert`, object range `insert`, `update`, and `swap`.
- Comparisons: equality, inequality, ordering, and optional C++20 three-way comparison, with special handling for cross-number comparisons, NaN, and `discarded` values.
- Text parsing/streaming: `operator<<`, `operator>>`, `parse`, `accept`, and `sax_parse`, gated by `JSON_NO_IO` where appropriate.
- Binary support: `to_cbor`, `to_msgpack`, `to_ubjson`, `to_bjdata`, `to_bson`, and matching `from_*` functions using `binary_writer`, `binary_reader`, and SAX DOM parsers.
- JSON Pointer/Patch/Merge Patch: pointer `operator[]`, pointer `at`, `flatten`, `unflatten`, `patch_inplace`, `patch`, static `diff`, and `merge_patch`.
- Internal storage in this chunk: nested `struct data` owns `value_t m_type` and `json_value m_value`, destroys payloads in its destructor, and disables copying.
- Header tail: `to_string(const basic_json&)`, `operator ""_json`, `operator ""_json_pointer`, `std::hash`, `std::less<value_t>`, optional `std::swap` specialization before C++20, optional global UDL exports, and macro undefinition.

## Control Flow

Lifecycle operations are type-dispatch heavy. The copy constructor copies `m_data.m_type`, checks the source invariant, and switches over `value_t` to deep-copy object, array, string, binary, and scalar payloads. The move constructor moves the storage, then resets the source object to `null` with an empty value so the moved-from object remains destructible and valid. Assignment takes its argument by value, swaps storage and diagnostic positions, assigns the base class, then resets diagnostic parent pointers.

Serialization through `dump` creates a `serializer` around a string output adapter, selects pretty or compact mode based on `indent >= 0`, and delegates all formatting to `serializer::dump`. Stream output follows the same serializer path, using `ostream::width()` as the indentation request and then resetting width to `0`.

Value conversion is selected by template priority tags. The lowest-priority general overload default-constructs a target and calls `JSONSerializer<ValueType>::from_json(*this, ret)`. A higher-priority overload handles non-default-constructible types whose serializer returns the value directly. Further overloads copy or convert to another `basic_json` type, or return an internal pointer. `get()` exposes this selection while rejecting reference targets; references must go through `get_ref()`, which verifies the requested reference type through `get_ptr()`.

Element access separates checked and unchecked semantics. `at()` validates the current type and array bounds or object-key presence, throwing nlohmann exception types with stable error IDs. Non-const `operator[]` converts `null` to an array or object as needed, grows arrays with null values for out-of-range numeric indices, and inserts `nullptr` for missing object keys. Const `operator[]` asserts the key exists rather than inserting.

Mutation APIs generally validate the current JSON kind, sometimes converting `null` to the required container. `push_back` and `emplace_back` convert `null` to array; object-pair `push_back`, `emplace`, and `update` convert `null` to object. Array insertion validates that the insertion iterator belongs to the receiving array and rejects inserting a range from the same container. Object `update` can recursively merge existing object values when `merge_objects` is true.

Comparison uses a macro-generated switch that first compares same-type values, then handles mixed integer/unsigned/float numeric combinations, then treats NaN and `discarded` as unordered. If values are different nonnumeric types, ordering falls back to the `value_t` ordering. C++20 builds may use `operator<=>`; older builds define the six relational friend operators.

Parsing and SAX APIs build `detail::input_adapter` instances from generic input or iterator ranges. JSON text input uses `parser`; binary formats use `binary_reader`. DOM-producing binary parses create a `json_sax_dom_parser`, run SAX parse, and return either the populated result or a `discarded` JSON value when parsing fails without exceptions.

`patch_inplace` validates that the patch document is an array of objects, extracts `"op"` and `"path"` fields, maps the operation string to an internal enum, and applies RFC 6902 operations. `add` resolves the parent pointer and inserts/replaces/appends; `remove` erases from an object or array; `replace` assigns through checked pointer access; `move` reads from `"from"`, removes it, then adds it at the target; `copy` reads from `"from"` and adds; `test` compares the target value and throws if it does not match. `diff` recursively emits a JSON Patch array that transforms source into target. `merge_patch` follows RFC 7386 behavior: object patches recurse, null members erase keys, and non-object patches replace the whole value.

## State and Persistence

All state is local in-memory C++ object state. `basic_json::data` stores the active type tag and union-like `json_value` payload. Heap-allocated payloads for object, array, string, and binary values are owned by the JSON value and destroyed through `json_value::destroy(m_type)` when `data` is destructed. Diagnostic builds also maintain parent pointers and, if enabled, parse start/end positions.

The code performs no WiredTiger persistence and does not read or write database files, logs, metadata, checkpoints, or durable configuration. Persistence-like behavior is limited to serialization into caller-provided strings, streams, output adapters, or vectors, and deserialization from caller-provided inputs.

Mutating APIs can invalidate references, pointers, and iterators. The header documents this explicitly for internal pointers returned by `get_ptr()`/`get()`. Array growth, insertion, erase, and swap can relocate child values; diagnostic parent pointers are repaired with `set_parent` or `set_parents` after such operations.

## Dependencies and Integration Points

- Earlier definitions in the same header: `value_t`, `json_value`, `serializer`, `parser`, `binary_reader`, `binary_writer`, `json_pointer`, iterators, `iteration_proxy`, `byte_container_with_subtype`, exception classes, input/output adapters, and detection traits.
- C++ standard library: containers, iterators, streams, allocator traits, type traits, `std::hash`, `std::less`, `std::partial_ordering` when available, and `std::isnan` for float comparison.
- User customization: conversions rely on `JSONSerializer<ValueType>::from_json`; projects can extend behavior through nlohmann's `from_json`/`to_json` conventions.
- Compile-time configuration macros: `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_NO_IO`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`, `JSON_USE_GLOBAL_UDLS`, and `JSON_TEST_KEEP_MACROS` materially alter exposed APIs or behavior.
- WiredTiger test integration: this vendored header allows tests under `sources/storage-engines/wiredtiger/test` to use a consistent nlohmann/json version independent of the host environment.
- Namespace integration: the code closes `NLOHMANN_JSON_NAMESPACE`, adds literals in `nlohmann::literals::json_literals`, and specializes selected `std` templates for nlohmann types.

## Risks and Maintenance Notes

- This is vendored third-party code. Local edits risk diverging from upstream nlohmann/json 3.12.0 and should be avoided unless the repository intentionally carries a patch.
- Template overload resolution is delicate. Changes to `get`, `value`, `operator[]`, transparent-key support, or scalar comparison overloads can introduce ambiguous calls or break existing consumer code across C++ standard versions.
- Non-const `operator[]` has side effects: it converts `null` values into containers, grows arrays, and inserts missing object keys. Tests that only intend lookup should use `at`, `find`, `contains`, or `value`.
- Const object `operator[]` asserts the key exists and does not provide runtime checked semantics in the same way as `at`. Misuse can fail assertions or produce undefined behavior depending on build settings.
- Mixed signed/unsigned numeric comparison casts unsigned values to `number_integer_t` in one branch. Very large unsigned values can be sensitive to implementation details and should be covered by upstream tests.
- NaN and `discarded` values are treated as unordered, with legacy behavior optionally controlled by `JSON_USE_LEGACY_DISCARDED_VALUE_COMPARISON`. Test expectations can change with that macro.
- `patch_inplace` mutates the target progressively. If a later patch operation fails, earlier operations remain applied; callers needing all-or-nothing behavior should use `patch()` on a copy.
- Binary deserialization returns `discarded` on parse failure when exceptions are disabled. Callers must check `is_discarded()` if they suppress exceptions.
- Macro cleanup at the end is important for header hygiene. Defining `JSON_TEST_KEEP_MACROS` intentionally leaves some macros visible for tests; otherwise consumers should not rely on those macro names after inclusion.

## Test Signals

Useful validation signals for this chunk include:

- Upstream nlohmann/json unit tests for `basic_json` copy/move/assignment, `dump`, `parse`, `accept`, SAX parsing, binary formats, JSON Pointer, JSON Patch, Merge Patch, iterators, and comparisons.
- WiredTiger test builds that include this vendored header under the repository's supported C++ standard modes.
- Compile-only coverage with and without key feature macros such as `JSON_NO_IO`, `JSON_DIAGNOSTICS`, `JSON_DIAGNOSTIC_POSITIONS`, `JSON_USE_GLOBAL_UDLS`, and C++20 three-way comparison support.
- Runtime tests for checked access and exception IDs: array bounds, missing object keys, wrong-type `at`, wrong-type `erase`, invalid insert iterators, malformed patches, failed patch tests, and parse failures with exceptions disabled.
- Round-trip tests for JSON text and binary encodings: `parse(dump(j))`, `from_cbor(to_cbor(j))`, `from_msgpack(to_msgpack(j))`, `from_ubjson(to_ubjson(j))`, `from_bjdata(to_bjdata(j))`, and `from_bson(to_bson(j))` for representative scalar, object, array, string, binary, and nested values.
- Sanitizer or debug builds that exercise array growth, insertion, erase, swap, move construction, and patch operations, since those paths stress ownership, iterator validity, and diagnostic parent repair.
