# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 13848-21067

## Scope

This chunk is a large middle section of XRootD's vendored, single-header copy of `nlohmann::json` version 3.12.0. It starts in the tail of `detail::iter_impl` and continues through reverse iteration, JSON Pointer support, output adapters, binary serialization, floating-point-to-text conversion, text serialization, `ordered_map`, and the beginning of `basic_json` storage and constructors.

The code is generic library infrastructure rather than XRootD-specific policy. Its observable role in this tree is to provide the JSON value type, JSON Pointer access, dump/binary serialization, ordered-object option, and internal storage model used by any XRootD code that includes `XrdOucJson.hh`.

## Purpose

The chunk implements the runtime mechanics that make `basic_json` behave like an STL-style container and a JSON serialization engine:

- iterator dereference, motion, comparison, indexing, object-key access, and reverse iteration;
- RFC 6901 JSON Pointer parsing, token escaping, pointer traversal, `flatten`, and `unflatten`;
- `json_ref`, the initializer-list helper that lets `basic_json` distinguish owned temporaries from referenced values;
- output abstraction over vectors, strings, and streams;
- binary output for BSON, CBOR, MessagePack, UBJSON, and BJData;
- shortest round-trippable decimal conversion for floating point values plus textual JSON dumping;
- `ordered_map`, a vector-backed object container preserving insertion order for `ordered_json`;
- `basic_json` aliases, allocator-backed union storage, parent-pointer diagnostics, and the first constructors.

This is a header-only implementation section. Most functions are templates or inline class members, so compile-time integration and macro configuration matter as much as normal link-time behavior.

## Important APIs, Types, And Functions

### Iterator Infrastructure

The opening lines finish `detail::iter_impl<BasicJsonType>`. `set_begin()` and `set_end()` dispatch on `m_object->m_data.m_type` and initialize the active member in `m_it`:

- objects use `object->begin()` / `object->end()`;
- arrays use `array->begin()` / `array->end()`;
- `null` has an empty primitive iterator range;
- primitive non-null values expose a single synthetic element.

The public operators implement the user-facing iterator API:

- `operator*()` and `operator->()` return object values, array elements, or the primitive JSON value when the primitive iterator is at begin; otherwise they throw `invalid_iterator.214`.
- `operator++`, `operator--`, `operator+=`, `operator-=`, arithmetic, distance, and `operator[]` advance either object/array iterators or the synthetic primitive iterator.
- object iterators reject random-access ordering and offsets with `invalid_iterator.208`, `.209`, or `.213`.
- `operator==` rejects comparisons across different containers with `invalid_iterator.212`, while value-initialized iterators compare equal.
- `key()` is valid only for object iterators; `value()` delegates to `operator*()`.

`json_reverse_iterator<Base>` wraps `std::reverse_iterator<Base>` but preserves JSON-specific `key()` and `value()` by decrementing the base iterator before reading. It is the backing type for `basic_json::reverse_iterator` and `const_reverse_iterator`.

### Base-Class Customization

`detail::json_default_base` and `json_base_class<T>` normalize the `CustomBaseClass` template parameter. `basic_json` always derives from some base class: an empty default when `CustomBaseClass == void`, otherwise the supplied type. This lets constructors and assignments avoid case splits for "no base class" versus "custom base class."

### JSON Pointer

`json_pointer<RefStringType>` stores `reference_tokens` as a `std::vector<string_t>`, where `string_t` is either the provided string type or the `StringType` from a `basic_json` template argument for backward compatibility.

Public pointer APIs include:

- constructor from pointer string, parsed by `split`;
- `to_string()` and deprecated string conversion;
- stream output when IO is enabled;
- `operator/=` and `operator/` for appending another pointer, an unescaped string token, or an array index;
- `parent_pointer()`, `pop_back()`, `back()`, `push_back()`, and `empty()`;
- equality, inequality, ordering, and optional C++20 three-way comparison.

Private traversal helpers are the important integration surface with `basic_json`:

- `array_index<BasicJsonType>()` validates array index strings, rejects leading zeroes, non-numeric tokens, overflow, and values beyond `size_type`.
- `get_and_create()` builds missing object/array paths for `unflatten`; a null value becomes an array only for token `"0"`, otherwise an object.
- mutable `get_unchecked()` creates missing values for `operator[]`-style pointer access; null nodes become arrays for numeric tokens or `"-"` and objects otherwise.
- mutable and const `get_checked()` use `at()` and throw for unresolved paths or the special `"-"` array token.
- `contains()` walks without throwing for normal misses, validates token syntax, and rejects unresolved primitive paths.
- `flatten()` recursively emits a pointer-keyed object; empty arrays and objects flatten to `null`.
- `unflatten()` requires an object whose values are primitive, then assigns each value through `json_pointer(element.first).get_and_create(result)`.

The `split()` routine enforces RFC 6901 syntax: a non-empty pointer must start with `/`, and `~` escapes must be only `~0` or `~1`.

### Initializer References

`detail::json_ref<BasicJsonType>` supports initializer-list construction without unnecessary copies. It either owns a `BasicJsonType` or points at an existing const value. It is movable only, has deleted copy assignment/copy construction, and exposes:

- `moved_or_copied()` for constructors to consume owned temporaries or copy referenced values;
- `operator*()` and `operator->()` for type-deduction checks in initializer-list construction.

### Output Adapters

The output layer abstracts where serialized bytes/chars go:

- `output_adapter_protocol<CharType>` is a virtual interface with `write_character` and `write_characters`.
- `output_vector_adapter`, `output_stream_adapter`, and `output_string_adapter` write to `std::vector`, `std::basic_ostream`, and `std::basic_string`.
- `output_adapter` wraps concrete adapters in `std::shared_ptr<output_adapter_protocol<CharType>>`.

This layer is shared by text dumping and binary writers. It hides destination-specific append mechanics while keeping serialization code expressed as sequential writes.

### Binary Writer

`detail::binary_writer<BasicJsonType, CharType>` serializes `basic_json` to multiple binary encodings through an `output_adapter_t<CharType>`.

Public entry points:

- `write_bson()` accepts only top-level objects and throws `type_error.317` otherwise.
- `write_cbor()` recursively emits CBOR major types for null, bool, signed/unsigned integers, floats, strings, arrays, binary, objects, and binary subtypes/tags.
- `write_msgpack()` recursively emits MessagePack fix/int/str/bin/array/map/ext encodings with length-class selection.
- `write_ubjson()` emits UBJSON or BJData depending on flags, including optimized `$` type and `#` count prefixes.

Important private helpers:

- BSON sizing/writing: `calc_bson_entry_header_size`, `calc_bson_*_size`, `write_bson_*`, `write_bson_element`, and `write_bson_object`.
- format prefix selection: `get_cbor_float_prefix`, `get_msgpack_float_prefix`, `get_ubjson_float_prefix`, and `ubjson_prefix`.
- numeric UBJSON emission: `write_number_with_ubjson_prefix` overloads for unsigned, signed, and floating values, including BJData-only unsigned prefixes and high-precision fallback.
- `write_bjdata_ndarray()` detects JData-style objects with `_ArrayType_`, `_ArraySize_`, and `_ArrayData_`, validates total element count, and writes BJData optimized ndarray payloads.
- `write_number()` copies numeric bytes into an array, reverses based on system endianness versus target endianness, and writes raw bytes.
- `write_compact_float()` chooses single-precision output for finite values exactly representable as `float`, otherwise double.
- `to_char_type()` overloads safely convert `std::uint8_t` to signed or unsigned `CharType`.

### Float-To-Text Conversion

The `detail::dtoa_impl` namespace implements Grisu2 for shortest decimal output of finite IEEE single/double values:

- `reinterpret_bits` copies bit representations.
- `diyfp` models a significand and exponent with subtraction, multiplication, normalization, and normalization to a target exponent.
- `compute_boundaries()` finds the lower/upper rounding boundaries for positive finite values.
- `cached_power` and `get_cached_power_for_binary_exponent()` supply powers of ten for scaling.
- digit generation and rounding functions produce a shortest decimal digit buffer that round-trips.
- `append_exponent()` and `format_buffer()` turn the raw digit buffer and decimal exponent into JSON/`%g`-style text.
- `detail::to_chars()` handles sign, zero, finite assertions, Grisu2 invocation, and final formatting.

This is used by text serialization for IEEE `float` and `double`-like `number_float_t` values.

### Text Serializer

`detail::error_handler_t` controls invalid UTF-8 behavior:

- `strict` throws;
- `replace` writes replacement characters;
- `ignore` skips invalid sequences.

`detail::serializer<BasicJsonType>` owns the output adapter, locale metadata, reusable numeric/string buffers, indentation state, and error-handler setting. Its primary API is `dump(val, pretty_print, ensure_ascii, indent_step, current_indent)`.

`dump()` dispatches by `value_t`:

- objects and arrays recurse with optional indentation and comma management;
- strings call `dump_escaped`;
- binary values are represented as JSON objects with `"bytes"` and `"subtype"`;
- booleans, null, discarded values, signed/unsigned integers, and floats use specialized emission paths.

`dump_escaped()` decodes UTF-8 using a DFA, escapes JSON control characters, optionally escapes non-ASCII as `\uXXXX`, emits surrogate pairs for non-BMP code points, and applies the selected invalid UTF-8 policy.

Numeric helpers include:

- `dump_integer()`, with a two-digit lookup table for fast integer-to-decimal conversion;
- `remove_sign()` to handle signed minimum values without undefined overflow;
- `dump_float()`, which emits non-finite values as JSON `null`, uses Grisu2 for IEEE single/double, and falls back to `snprintf("%.*g")` for other float types while normalizing locale decimal points and removing thousands separators.

### Ordered Map

`nlohmann::ordered_map<Key, T, IgnoredLess, Allocator>` is a vector-backed, map-like container preserving insertion order. It derives from `std::vector<std::pair<const Key, T>, Allocator>` and provides:

- `emplace`, `insert`, and `operator[]` that reuse existing keys instead of adding duplicates;
- `at`, `find`, and `count`;
- key and iterator erasure;
- transparent key lookup when C++14 support is enabled.

Because keys are `const` inside `std::pair<const Key, T>`, erase operations destroy and reconstruct vector elements in place to shift elements. This design is compact and preserves insertion order, but lookups and erases are linear.

### `basic_json` Beginning

The chunk starts the main `basic_json` class template. It declares friend access for `json_pointer`, parser, serializer, iterators, binary reader/writer, SAX DOM parsers, and exceptions. It defines core aliases:

- internal aliases for lexer, parser, iterator, reverse iterator, output adapter, binary reader/writer, and serializer;
- public aliases for `value_t`, `json_pointer`, `json_serializer`, `error_handler_t`, `cbor_tag_handler_t`, `bjdata_version_t`, `initializer_list_t`, `input_format_t`, `json_sax_t`;
- exception aliases: `exception`, `parse_error`, `invalid_iterator`, `type_error`, `out_of_range`, `other_error`;
- container aliases: `value_type`, references, `difference_type`, `size_type`, allocator, pointers, iterators.

`meta()` builds a JSON object reporting library name, version, URL, platform, compiler family/version, and C++ standard value.

Storage setup includes:

- type aliases for object, array, string, boolean, integer, unsigned, float, binary, and comparator types;
- allocator-backed `create<T>(Args&&...)`;
- `json_value`, a union holding pointers for object/array/string/binary and inline primitive values for booleans and numbers;
- `json_value(value_t)` default construction for each JSON type;
- typed constructors for strings, objects, arrays, and binary containers;
- `destroy(value_t)`, which first flattens nested arrays/objects into a heap stack before deallocating to avoid recursive destructor depth, then destroys/deallocates the active pointer member.

The `assert_invariant()` helper checks that structured/string/binary pointer members are non-null for their active type and, under `JSON_DIAGNOSTICS`, validates parent pointers. `set_parents()`, range `set_parents()`, and `set_parent()` maintain diagnostic parent links, with special handling for array capacity changes and vector-backed `ordered_json` objects.

The constructor section begins with:

- `basic_json(value_t)` for empty typed values;
- `basic_json(nullptr_t)` for null;
- a compatible-type forwarding constructor using `JSONSerializer<U>::to_json`;
- a cross-`basic_json` constructor that converts by active type and optionally copies diagnostic positions;
- the start of initializer-list construction, where a list of two-element arrays with string first elements is detected as an object.

## Control Flow

Iterator operations are all type-dispatch flows: inspect `m_object->m_data.m_type`, then operate on the matching internal iterator. Invalid combinations are rejected immediately. Primitive values use `primitive_iterator_t` to synthesize a one-element range, so generic algorithms can iterate over primitive JSON values consistently.

JSON Pointer construction first tokenizes the pointer string. Access flows then iterate token by token:

1. Validate or interpret the current token as an object key, array index, or the special `"-"` append marker where permitted.
2. Dispatch on the current JSON node type.
3. For unchecked mutable access, create objects or arrays from null nodes as needed.
4. For checked/const access, call `at()` and throw if the path cannot be resolved.
5. Return the final JSON reference, boolean containment result, or throw a typed exception.

Flattening is recursive over source structure and writes into a result object keyed by pointer strings. Unflattening reverses that by iterating the flattened object, parsing each key as a pointer, creating the path in a result JSON value, and assigning the primitive leaf.

Serialization control flow is also type-dispatch oriented:

- text serialization recurses through object/array members and writes tokens directly to the output adapter;
- binary serialization recurses through values while choosing size prefixes and numeric encodings based on each output format;
- float formatting routes finite IEEE values through Grisu2 and non-IEEE values through locale-normalized `snprintf`.

`basic_json` construction routes through serializer hooks or active-type switches, then repairs diagnostic parent pointers and asserts storage invariants before returning.

## State And Persistence Behavior

There is no file, network, or database persistence in this chunk. State is in-memory and owned by the JSON object or serializer/writer instance:

- `iter_impl` stores a pointer to the owning JSON object plus one active internal iterator.
- `json_pointer` stores parsed tokens; it does not cache resolved nodes.
- output adapters store references to the destination vector/string/stream, so destination lifetimes must outlive serialization.
- `binary_writer` and `serializer` hold shared output adapters and reusable buffers.
- `basic_json::json_value` owns heap-allocated object/array/string/binary payloads through the configured allocator and stores primitive values directly.
- diagnostic builds add parent-pointer state and position metadata outside the normal JSON data model.

The main persistence-like behavior is deterministic serialization. The same JSON value should produce stable text and binary encodings subject to object ordering, selected format flags, locale normalization, and macro configuration.

## Dependencies And Integration Points

Internal dependencies include earlier sections of the same header:

- `value_t`, exception classes, macro configuration, `JSON_THROW`, `JSON_ASSERT`, and Hedley annotations;
- type-trait helpers such as `enable_if_t`, `is_usable_as_key_type`, `is_basic_json`, and `is_compatible_type`;
- `byte_container_with_subtype`, parser types, SAX types, binary reader declarations, and input format enums;
- string helpers `concat`, `escape`, and `unescape`;
- endian helper `little_endianness()`.

Standard library dependencies include algorithms, arrays, vectors, maps, strings, streams, allocators, numeric limits, locale metadata, `snprintf`, `memcpy`/`memmove`, type traits, and iterator traits.

External integration for XRootD is by inclusion. Consumers that use `XrdOucJson.hh` rely on this chunk for:

- `nlohmann::json` and `nlohmann::ordered_json` object behavior;
- pointer-based access such as `j.at(json::json_pointer("/path"))` or patch/flatten operations implemented later in the header;
- `dump()` and binary serialization APIs exposed later by `basic_json`;
- initializer-list syntax such as `json{{"key", value}}`;
- custom serializers and custom base classes.

Because this is a vendored third-party header, local changes have broad ABI/API consequences for every translation unit that includes it.

## Risks And Edge Cases

- Iterator comparisons are only defined for the same container. The implementation throws when `m_object` differs; callers that compare iterators from different JSON values will fail at runtime.
- Primitive JSON values expose a synthetic one-element iterator. Generic code that assumes only arrays/objects are iterable can accidentally process primitives.
- Object iterators do not support ordering, offsets, or `operator[]`; ordered/random-access algorithms must not be applied to object iterators.
- JSON Pointer array indexes reject leading zeroes and malformed numeric tokens. Inputs such as `/01`, `/a`, or `/-` are accepted or rejected differently depending on checked, unchecked, const, or append contexts.
- `get_unchecked()` mutates null nodes into arrays or objects based on token shape. This is convenient for `operator[]` but can surprise callers expecting read-only path probing.
- `flatten()` maps empty arrays/objects to `null`, so structural emptiness is not preserved through flatten/unflatten in the same way as non-empty containers.
- BSON requires a top-level object and rejects NUL bytes in keys. Large strings, arrays, or document sizes are cast into 32-bit BSON sizes, so extremely large inputs rely on upstream bounds and platform behavior.
- Binary writers have many format-specific integer size thresholds. Boundary mistakes around 23/24, 127/128, 255/256, 65535/65536, and signed minima would change wire encodings.
- `write_number()` depends on correct endian detection and on `CharType` byte-size/triviality assumptions. Signed `char` handling uses reinterpretation/memcpy to preserve byte values above 127.
- BJData ndarray handling trusts the three-key object schema, then directly reads numeric union members from `_ArraySize_` and `_ArrayData_`; malformed values can trigger assertions or invalid output if not rejected earlier.
- Text serialization emits non-finite floating-point values as `null`, which is valid JSON but loses NaN/Inf identity.
- Invalid UTF-8 behavior depends on the configured `error_handler_t`; strict mode throws, replace mode injects U+FFFD, and ignore mode can silently drop bytes.
- `ordered_map` lookup/insert/erase are linear and erase reconstructs elements manually because keys are const. Iterator invalidation follows vector semantics and can be more aggressive than map users expect.
- `basic_json::destroy()` intentionally avoids recursive destruction for nested arrays/objects. Bugs in this flattening destruction path can leak, double-destroy, or disturb diagnostic parent assumptions.
- Diagnostic parent pointers need repair after vector reallocation or ordered-map movement. The `set_parent` capacity checks and ordered-map branch are critical for useful exception diagnostics.
- Since this code is header-only and heavily macro-gated, behavior can change with `JSON_NO_IO`, `JSON_DIAGNOSTICS`, `JSON_HAS_CPP_14`, `JSON_HAS_THREE_WAY_COMPARISON`, `JSON_HAS_CPP_26`, and compiler-specific macros.

## Test Signals

Useful test coverage for this chunk should include:

- iterator begin/end, dereference, `key()`, `value()`, arithmetic, invalid object offsets, cross-container comparison errors, and primitive/null iteration;
- reverse iteration over arrays and objects, including object key/value access;
- JSON Pointer parse failures for missing leading slash and bad `~` escapes;
- pointer traversal for checked, unchecked, const, `contains`, append `"-"`, array-index overflow, leading-zero rejection, and null-to-container creation;
- `flatten()`/`unflatten()` round trips for nested objects/arrays, escaped keys containing `/` and `~`, empty arrays/objects, primitive leaves, and invalid flattened values;
- initializer-list construction distinguishing arrays from object-like two-element string-key arrays;
- text `dump()` for compact and pretty output, binary-as-object representation, `ensure_ascii`, invalid UTF-8 under all handlers, control characters, surrogate-pair output, integer minima, unsigned maxima, finite floats, NaN, and infinities;
- CBOR, MessagePack, UBJSON, BJData, and BSON golden-byte tests around every length and integer threshold;
- BSON top-level non-object rejection and NUL-key rejection;
- endian-sensitive binary numeric output on little- and big-endian targets or with explicit byte-order fixtures;
- `ordered_json` insertion order, duplicate-key behavior, lookup, erase, iterator invalidation expectations, and heterogeneous lookup where enabled;
- construction/destruction of very deeply nested arrays/objects to validate non-recursive destruction;
- diagnostic builds that assert parent links after insertion, erase, vector capacity growth, and ordered-map object mutation.

For XRootD integration, regressions are likely to appear as compile failures in translation units including `XrdOucJson.hh`, runtime JSON parse/dump mismatches, changed binary serialization bytes, or exception behavior changes in configuration paths that use JSON Pointer or object iteration.
