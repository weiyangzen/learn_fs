# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 13907-21115

## Scope

This chunk covers a large middle section of the vendored nlohmann JSON single-header library, version 3.12.0. It starts near the end of `detail::iter_impl`, then includes reverse iterators, the default/custom base-class adapter, the full `json_pointer` implementation, `json_ref`, output adapters, binary serializers for BSON/CBOR/MessagePack/UBJSON/BJData, decimal floating-point formatting, textual JSON serialization, `ordered_map`, and the beginning of `basic_json` through its early constructors and storage machinery.

This is library infrastructure rather than WiredTiger-specific logic. WiredTiger tests include it as a third-party dependency, so the important integration surface is the public nlohmann JSON API and the binary/text encoders used by tests or utilities that instantiate `nlohmann::json` from this header.

## Purpose

- Provide STL-style iterator behavior for JSON values, including random-access behavior for arrays and primitive pseudo-iteration, while rejecting invalid operations on object iterators.
- Implement JSON Pointer per RFC 6901, including token parsing, escaping, checked/unchecked lookup, creation during unflattening, containment tests, flatten/unflatten support, pointer composition, and comparison operators.
- Provide lightweight helper types used by `basic_json`: a default empty base class for optional custom base support, `json_ref` for initializer-list construction without unnecessary copies, and `ordered_map` for insertion-order-preserving object storage.
- Provide output adapter abstraction so serializers can write to strings, byte vectors, and output streams through a uniform `write_character` / `write_characters` protocol.
- Serialize JSON values to binary formats: BSON, CBOR, MessagePack, UBJSON, and BJData, including binary subtype handling and optimized homogeneous container encodings.
- Serialize JSON values to textual JSON with pretty-print support, ASCII escaping, UTF-8 validation/recovery policies, locale-independent float output, and binary values represented as JSON objects with `bytes` and `subtype`.
- Start defining `basic_json` itself: public aliases, exception aliases, object/array/string/number/binary type aliases, allocator-backed `json_value` storage, invariant checks, diagnostics parent tracking, metadata reporting, and initial construction APIs.

## Important APIs, Types, And Functions

- `detail::iter_impl` operators in this chunk implement increment/decrement, comparisons, offset arithmetic, indexing, `key()`, and `value()`. They switch on the owning `basic_json` value type and throw `invalid_iterator` for object offset/order operations or invalid primitive dereferences.
- `detail::json_reverse_iterator<Base>` wraps `std::reverse_iterator<Base>` and preserves JSON-specific `key()` and `value()` access by looking at `--base()`.
- `detail::json_default_base` and `detail::json_base_class<T>` ensure `basic_json` always has a base class, using an empty type when the `CustomBaseClass` template parameter is `void`.
- `nlohmann::json_pointer<RefStringType>` stores `reference_tokens` and exposes `to_string()`, conversion to string, stream output, `/=` and `/` composition, `parent_pointer()`, `pop_back()`, `back()`, `push_back()`, `empty()`, and comparison operators.
- `json_pointer::array_index<BasicJsonType>()` validates array token syntax, forbids leading zeroes, converts with `std::strtoull`, detects `ERANGE`, and checks the result against `BasicJsonType::size_type`.
- `json_pointer::get_unchecked()`, `get_checked()`, `contains()`, `get_and_create()`, `flatten()`, and `unflatten()` are private friend-facing algorithms used by `basic_json` pointer APIs and by flatten/unflatten features.
- `detail::json_ref<BasicJsonType>` is a move-only wrapper that either stores an owned JSON value or references an existing value. `moved_or_copied()` returns by move for owned values and by copy for references.
- `detail::output_adapter_protocol`, `output_vector_adapter`, `output_stream_adapter`, `output_string_adapter`, and `output_adapter` abstract serialization sinks behind `std::shared_ptr`.
- `detail::binary_writer<BasicJsonType, CharType>` exposes `write_bson()`, `write_cbor()`, `write_msgpack()`, and `write_ubjson()`. Private helpers calculate BSON sizes, write endian-correct numbers, choose compact float encodings, choose UBJSON/BJData numeric prefixes, and emit BJData ndarray objects when the `_ArrayType_`, `_ArraySize_`, and `_ArrayData_` shape is recognized.
- `detail::dtoa_impl` implements Grisu2-style float-to-decimal conversion using `diyfp`, cached powers, boundary computation, digit generation, rounding, exponent formatting, and fixed/exponential layout.
- `detail::to_chars()` wraps the DTOA implementation for finite IEEE float/double values and formats zero as `0.0`.
- `detail::serializer<BasicJsonType>` exposes `dump()` for textual JSON and contains `dump_escaped()`, `dump_integer()`, `dump_float()`, UTF-8 `decode()`, and locale cleanup for fallback `snprintf` float formatting.
- `nlohmann::ordered_map<Key, T, ...>` is a `std::vector<std::pair<const Key, T>>`-backed associative container with linear `emplace`, `operator[]`, `at`, `erase`, `count`, `find`, and `insert`, preserving insertion order and supporting transparent key lookup where available.
- The `basic_json` opening section declares friend internals, public type aliases, `meta()`, `create<T>()`, the `json_value` union and its `destroy()` method, diagnostic parent setters, parser callback aliases, and constructors for null, explicit type, compatible types, other `basic_json` instantiations, initializer lists, binary values, arrays, objects, repeated arrays, and iterator ranges.

## Control Flow

Iterator operations route through the owning value's `m_data.m_type`. Object iterators delegate to the object container iterator for movement and equality, but order comparisons and offsets throw because object iterators are not random-access in this API. Array iterators use the array container iterator. Primitive values use a `primitive_iterator_t` that represents begin/end over a single scalar value. Equality also accepts value-initialized iterators and treats two null-owned iterators as equal.

JSON Pointer construction calls `split()`, which enforces an empty string or leading slash, splits on slash boundaries, validates every `~` escape, unescapes tokens, and stores them. Lookup then walks tokens against the current JSON type. Checked lookup uses `at()` and throws on missing keys or out-of-range indexes. Unchecked mutable lookup creates arrays or objects when the current value is null, treats `-` as append position for arrays, and uses `operator[]`. Const unchecked lookup cannot use `-` and throws if resolution fails. `contains()` follows the same traversal without mutating and returns false for syntactically invalid array tokens, missing keys, out-of-range indexes, or primitive intermediates.

Flattening recursively descends arrays and objects, building escaped pointer strings as keys in an output object. Empty arrays and objects become `null` at their reference string. Unflattening requires an object whose values are primitive, then constructs a fresh result by assigning each primitive through `json_pointer(element.first).get_and_create(result)`.

Binary output flows through an output adapter. `write_cbor()` and `write_msgpack()` switch directly on JSON type and emit format markers, lengths, and payload bytes recursively for arrays/objects. `write_ubjson()` handles optional count and type prefixes; for homogeneous containers it can elide per-element type markers. In BJData mode it uses additional unsigned integer markers and can encode JData-style ndarray objects as typed arrays. `write_bson()` requires a top-level object, calculates embedded document sizes before emission, then writes length-prefixed little-endian BSON objects/arrays with typed entries.

Textual serialization is recursive. `serializer::dump()` writes objects and arrays with either compact separators or indentation/newline formatting, serializes strings through `dump_escaped()`, serializes binary values as `{"bytes":[...],"subtype":...}`, emits non-finite floats as `null`, and emits discarded values as the literal `<discarded>`. `dump_escaped()` runs a DFA UTF-8 decoder, writes JSON escapes for control characters, quotes, backslashes, and optionally non-ASCII code points, and applies the configured error policy: strict throws, ignore drops invalid sequences, replace writes U+FFFD.

The beginning of `basic_json` centralizes all allocation of heap-backed value types through `create<T>()`, which uses the configured allocator and a temporary `unique_ptr` deleter for exception safety. `json_value(value_t)` constructs the active union member for empty objects, arrays, strings, binary values, booleans, numbers, or null. `destroy(value_t)` first flattens nested arrays/objects into a heap-allocated vector stack so deeply nested values do not recursively destroy on the C++ call stack, then destroys and deallocates the active heap member.

Constructors in this chunk either set `m_data` directly, delegate to serializer hooks, or inspect inputs to decide the JSON type. Initializer-list construction checks whether every element is a two-element array with a string key and, if so, creates an object; otherwise it creates an array unless the caller explicitly requested object construction, in which case incompatible input throws `type_error.301`.

## State And Persistence Behavior

The code has no external persistence of its own. It mutates in-memory JSON values and writes serialized bytes or characters to caller-provided sinks. Persistence is indirect: callers may store the emitted BSON, CBOR, MessagePack, UBJSON/BJData, or textual JSON elsewhere.

Important in-memory state includes:

- `json_pointer::reference_tokens`, a vector of unescaped path tokens.
- `output_adapter` shared pointers that reference caller-owned vectors, strings, or streams; the adapters do not own the underlying sink object.
- `binary_writer::oa` and `serializer::o`, which hold output adapters and must remain non-null.
- `serializer` buffers: `number_buffer` for integers/floats, `string_buffer` for escaped strings, and `indent_string` that grows as pretty-print depth increases.
- `serializer` locale snapshot fields `thousands_sep` and `decimal_point`, used only for fallback floating output cleanup.
- `ordered_map` state in its vector base; object insertion order is the vector order.
- `basic_json::m_data`, whose `m_type` selects the active member of the `json_value` union. Object, array, string, and binary values are heap allocated through the configured allocator; primitive values live directly in the union.
- Optional diagnostic parent pointers under `JSON_DIAGNOSTICS`, updated by `set_parents()`, `set_parent()`, and range parent helpers when structured values are created or inserted.

The `basic_json::meta()` function creates a JSON object reporting library name/version, platform, compiler, and C++ language version at compile time. It is runtime data but not persistent unless a caller serializes it.

## Dependencies And Integration Points

- This chunk is part of the amalgamated nlohmann header and depends heavily on earlier definitions in the same file: `value_t`, exceptions, macros, type traits, string escaping/concatenation helpers, `binary_reader`, parser types, `json_sax`, and the `NLOHMANN_BASIC_JSON_TPL` template macros.
- Standard library dependencies include algorithms, arrays, maps, vectors, strings, iterators, memory/allocators, streams, locales, numeric limits, C string functions, `errno`, `strtoull`, math functions, and type traits.
- The iterator, pointer, serializer, binary writer, parser, and SAX classes are all friends of `basic_json`, so they integrate by directly reading or mutating `m_data` internals instead of using only public APIs.
- `json_pointer` is a public alias inside `basic_json` and supports both direct user-facing pointer operations and internal flatten/unflatten implementation.
- `output_adapter` is the bridge used by public dump and binary serialization APIs to write to strings, byte containers, and streams.
- `ordered_map` is available as an alternative `ObjectType` template argument for `ordered_json`, trading lookup cost for insertion-order retention.
- Binary writer behavior is paired with binary reader behavior defined elsewhere in the header; tests must verify format round trips across both halves.
- In this repository, integration is through vendored third-party use in WiredTiger tests. Any local code including this header receives nlohmann 3.12.0 behavior, exception IDs, formatting choices, and binary format compatibility from this implementation.

## Risks And Edge Cases

- Iterator comparisons throw when containers differ. Code that compares iterators from different JSON values is not merely false; it is an exception path.
- Object iterators reject order comparisons, offsets, and `operator[]`, while array and primitive iterators support them. Generic iterator code can accidentally trip `invalid_iterator` exceptions when run over objects.
- Primitive iterator offset semantics are unusual because a scalar acts like a one-element range; invalid primitive offsets throw `invalid_iterator.214`.
- `json_pointer::array_index()` rejects leading zeroes and non-numeric tokens and throws out-of-range errors for overflow or incomplete parsing. This strictness can surprise callers expecting permissive array index parsing.
- Mutable unchecked JSON Pointer lookup can transform null values into arrays or objects, and `"-"` appends to arrays. This is intentional but can cause hidden mutation during pointer access.
- `contains()` performs its own array-token validation before calling `array_index()`, returning false for many invalid tokens rather than throwing, while overflow inside `array_index()` may still throw.
- Flattening represents empty arrays and objects as `null`, so flatten/unflatten cannot preserve the distinction between an empty structured value and a null leaf without the documented convention.
- BSON serialization rejects top-level non-objects and keys containing embedded NUL bytes. Size fields are cast to `std::int32_t`; extremely large documents or strings are only guarded by practical memory limits and assertions in this chunk.
- CBOR and MessagePack length branches assume sizes fit supported width cases; impossible or platform-limited larger cases are often marked as coverage-excluded rather than actively handled.
- MessagePack extension subtype is written as `int8_t`, so large binary subtype values are truncated to one signed byte for ext encodings.
- UBJSON/BJData optimized container encoding relies on homogeneous prefixes. BJData ndarray encoding trusts the `_ArraySize_` values as unsigned numbers and typed array data elements as the expected numeric kinds.
- `binary_writer::write_number()` depends on `little_endianness()` from elsewhere and type punning via `memcpy`; endian handling is central to cross-platform binary compatibility.
- Textual `dump_escaped()` strict mode throws on invalid UTF-8, while replace/ignore continue. Consumers must select an error policy consistent with whether strings may contain arbitrary bytes.
- `dump_float()` emits JSON `null` for NaN and infinity, which is standards-compliant JSON but lossy for applications that expect non-finite values to round-trip.
- The fallback float path uses C locale data and then removes thousands separators and rewrites decimal points. Locale edge cases are explicitly handled but remain a portability-sensitive area.
- `ordered_map` uses linear lookup for all key operations. It preserves insertion order but can be expensive for large objects.
- `ordered_map::erase()` manually destroys and reconstructs `pair<const Key, T>` elements in place because keys are const. This is subtle allocator/lifetime code and can be sensitive to nontrivial key/value types.
- `basic_json::json_value` manually manages a tagged union. Correctness depends on `m_type` always matching the active union member and on all type-changing code calling invariant/parent maintenance.
- Deep destruction is intentionally iterative for arrays/objects; changes that reintroduce recursive destruction could make deeply nested JSON values stack-sensitive.
- Diagnostics parent pointers are conditional. Code paths must remain correct both with and without `JSON_DIAGNOSTICS`, and ordered-map vector reallocation can invalidate child addresses, requiring full parent resets.

## Test Signals

- Iterator tests should cover array, object, primitive, null, binary, discarded, const, non-const, reverse, default-constructed, and cross-container comparison paths, including expected exception IDs for invalid operations.
- JSON Pointer tests should cover escaping/unescaping, invalid `~` sequences, missing leading slash, parent/back/pop on root, pointer composition, numeric tokens with leading zeroes, `"-"` behavior, overflow indexes, checked versus unchecked lookup, const lookup, containment, flatten, and unflatten.
- Serialization round-trip tests should cover BSON, CBOR, MessagePack, UBJSON, and BJData for every JSON type, nested arrays/objects, binary values with and without subtypes, large lengths around boundary markers, signed/unsigned integer limits, floats, NaN/infinity behavior, and endian-sensitive numeric outputs.
- BJData-specific tests should include draft2 versus draft3 binary markers, optimized type/count containers, homogeneous and heterogeneous arrays/objects, and valid/invalid JData ndarray objects.
- Text dump tests should cover compact and pretty output, indentation growth, `ensure_ascii`, all JSON string escapes, valid multi-byte UTF-8, invalid UTF-8 under strict/ignore/replace, binary textual representation, locale-sensitive fallback float formatting, negative zero, integer-like floats requiring `.0`, and non-finite floats becoming `null`.
- DTOA tests should verify shortest-round-tripping output for representative float/double values, exponent formatting boundaries, fixed versus scientific notation thresholds, subnormal values, and signed zero.
- `ordered_map` tests should cover insertion-order preservation, duplicate-key insertion behavior, transparent lookup, `operator[]`, `at()` exception behavior, erase by key and iterator range, and iterator validity expectations after vector-backed modifications.
- `basic_json` construction tests should cover explicit type construction, null construction, compatible-type serialization, cross-`basic_json` conversion, initializer-list object versus array deduction, forced object errors, binary factory overloads with subtypes, repeated-value arrays, iterator-range construction, allocator behavior, and diagnostics parent invariants when enabled.
