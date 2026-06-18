# sources/storage-engines/wiredtiger/test/3rdparty/nlohmann/json.hpp lines 6199-13906

## Scope

This chunk covers a large middle section of the vendored nlohmann JSON single-header library used by WiredTiger tests. It starts at the end of `byte_container_with_subtype`, continues through JSON hashing, input adapters, the text JSON lexer, SAX handlers, SAX concept checks, binary-format readers for BSON/CBOR/MessagePack/UBJSON/BJData, the recursive-descent JSON parser, and the beginning of iterator support. The range ends inside `detail::iter_impl::operator->`, so iterator behavior after the binary value case is outside this chunk.

The file is a third-party dependency (`JSON for Modern C++`, version 3.12.0) under `test/3rdparty`. It should be treated as vendored library code rather than WiredTiger-owned storage-engine logic.

## Purpose

The code in this range provides the deserialization and traversal core for `nlohmann::basic_json`:

- binary values can carry optional subtypes through `byte_container_with_subtype`;
- `detail::hash` computes type-aware recursive hashes for JSON values;
- input adapters normalize `FILE*`, streams, containers, iterators, C strings, spans, and wide strings into a byte-oriented reader interface;
- `detail::lexer` tokenizes RFC 8259 JSON text, including UTF-8 validation, escape decoding, number parsing, comment skipping when enabled, BOM handling, and diagnostics;
- `json_sax` defines the event interface consumed by text and binary parsers;
- DOM SAX implementations build `basic_json` values, optionally applying user callbacks that can discard parsed subtrees;
- `binary_reader` maps BSON, CBOR, MessagePack, UBJSON, and BJData bytes into the same SAX event stream;
- `parser` implements non-recursive recursive-descent JSON syntax analysis over lexer tokens;
- `primitive_iterator_t`, `internal_iterator`, and the beginning of `iter_impl` provide uniform iteration over objects, arrays, and primitive JSON values.

Within WiredTiger, this header supports tests that need JSON parsing/serialization without linking an external JSON package. The chunk does not directly interact with WiredTiger persistence, cache, log, or storage-engine state.

## Important APIs, Types, and Functions

- `byte_container_with_subtype<BinaryType>` tail: constructors from byte containers with and without subtype, equality/inequality, `set_subtype`, `subtype`, `has_subtype`, and `clear_subtype`. The subtype state is separate from the inherited byte container and uses `-1` as the public sentinel when absent.
- `detail::combine` and `detail::hash(const BasicJsonType&)`: type-aware hash helpers. They include the JSON value type, object keys and values, array elements, primitive payloads, and binary subtype metadata.
- `enum class input_format_t`: identifies `json`, `cbor`, `msgpack`, `ubjson`, `bson`, and `bjdata`.
- Input adapters: `file_input_adapter`, `input_stream_adapter`, `iterator_input_adapter`, `wide_string_input_adapter`, `iterator_input_adapter_factory`, container and pointer overloads of `input_adapter`, and `span_input_adapter`.
- `lexer_base::token_type`: the token vocabulary used by the text parser, including literals, structural tokens, numeric token classes, `parse_error`, `end_of_input`, and diagnostic-only `literal_or_value`.
- `lexer<BasicJsonType, InputAdapterType>`: scans strings, comments, numbers, literals, whitespace, BOM, and single tokens. Public getters expose parsed numbers, string buffers, token text, error messages, and `position_t`.
- `json_sax<BasicJsonType>`: abstract event interface for null, boolean, signed/unsigned/float numbers, strings, binary values, object/array starts and ends, object keys, and parse errors.
- `json_sax_dom_parser`: SAX sink that constructs a full DOM in a referenced `BasicJsonType`, using `ref_stack` and `object_element` to track nesting and pending object keys.
- `json_sax_dom_callback_parser`: SAX sink that constructs a DOM while invoking `parser_callback_t` at object, array, key, and value events. It uses `keep_stack` and `key_keep_stack` to discard rejected subtrees or object members.
- `json_sax_acceptor`: SAX sink used by `accept`; it returns true for all valid events and false on parse error without storing a DOM.
- `is_sax` and `is_sax_static_asserts`: compile-time checks that a SAX type has the complete callback surface with exact `bool` return types.
- `enum class cbor_tag_handler_t`: controls CBOR tag behavior as `error`, `ignore`, or `store`.
- `binary_reader<BasicJsonType, InputAdapterType, SAX>`: deserializes BSON, CBOR, MessagePack, UBJSON, and BJData to SAX callbacks.
- `parse_event_t` and `parser_callback_t`: callback event taxonomy and function signature for text JSON parsing with filtering.
- `parser<BasicJsonType, InputAdapterType>`: public `parse`, `accept`, and `sax_parse` APIs over the lexer.
- `primitive_iterator_t`, `internal_iterator<BasicJsonType>`, and partial `iter_impl<BasicJsonType>`: storage and dereference logic for basic JSON iterators.

## Control Flow

Text JSON parsing flows through `input_adapter(...)` into `lexer`, then through `parser::sax_parse_internal`. The parser reads one token ahead with `get_token`, dispatches primitive tokens directly to SAX callbacks, and tracks nested arrays/objects with a `std::vector<bool>` where `true` means array and `false` means object. Objects require a string key, a name separator, then a value. Arrays accept values separated by commas. Once a value completes, the parser evaluates the current container state to decide whether to consume a comma, close a container, or report a syntax error.

`lexer::scan` first handles a UTF-8 BOM at the beginning of input, skips whitespace, optionally skips `//` and `/* */` comments, and then dispatches by the current byte. Strings are scanned until a closing quote while rejecting unescaped control characters, decoding JSON escapes, validating UTF-8 byte sequences, and composing Unicode surrogate pairs from `\uXXXX` escapes. Numbers are scanned by a label-based deterministic finite state machine derived from RFC 8259, then converted with `strtoull`, `strtoll`, or floating-point conversion. Locale-dependent decimal separators are normalized internally and restored to `.` when exposing the token string.

DOM construction is SAX driven. `json_sax_dom_parser::handle_value` stores the first value as the root, appends array elements to the current array, or assigns object values through the previously captured `object_element`. Object and array starts push the new container pointer on `ref_stack`, and end events pop it. Callback parsing follows the same structure but calls the user callback to decide whether to keep values, keys, objects, or arrays.

Binary parsing starts at `binary_reader::sax_parse`, which selects the format-specific parser and then, in strict mode, verifies there is no trailing data. BSON reads document and array element lists, dispatches BSON element type bytes, and supports doubles, strings, nested objects/arrays, binary, booleans, null, int32, int64, and uint64 while rejecting unsupported record types. CBOR dispatches major-type byte ranges for integers, byte strings, UTF-8 strings, arrays, maps, tags, booleans, null, and floats; indefinite-length strings, binaries, arrays, and maps loop until the break byte. MessagePack dispatches fixint/fixmap/fixarray/fixstr plus typed number, string, binary, extension, array, and map markers. UBJSON and BJData parse marker-prefixed scalar values, optimized containers with optional type and size metadata, no-op `N` bytes, high-precision numeric strings, BJData unsigned widths, half floats, binary optimized arrays, and BJData ND-array conversion into JData-style annotated objects.

Iterator flow in this chunk initializes `iter_impl` storage based on the owning JSON type. `set_begin` and `set_end` bind object and array iterators to their container boundaries; null begin is set equal to end; primitive values expose a single synthetic element. `operator*` returns object member values, array elements, or the owning primitive value when the primitive iterator is at begin, and throws `invalid_iterator` for null or past-end primitive positions. The range ends while `operator->` is handling the same object/array/primitive split.

## State and Persistence Behavior

All state in this chunk is in-memory parser, iterator, and value-construction state. There are no file writes, WiredTiger metadata updates, database checkpoints, transaction commits, or durable side effects.

Important transient state includes:

- input adapter cursor state, such as `FILE*`, `std::istream`/`streambuf`, or iterator pairs;
- wide-string adapter buffers that translate UTF-16/UTF-32 code units to UTF-8 bytes;
- lexer position counters, `current`, `next_unget`, `token_string`, `token_buffer`, parsed numeric fields, and locale decimal metadata;
- SAX DOM stacks (`ref_stack`, `keep_stack`, `key_keep_stack`) and pending `object_element` pointers;
- binary-reader `current`, `chars_read`, selected `input_format`, endianness flag, SAX pointer, and BJData lookup tables;
- parser `last_token`, callback, lexer, and exception policy;
- iterator owner pointer plus `internal_iterator` union-like storage for object, array, or primitive positions.

The input stream adapter deliberately clears most stream flags on destruction while preserving EOF state, because it reads through the stream buffer rather than normal formatted stream APIs. Binary containers persist subtype information inside `basic_json` binary values after parsing CBOR tags with `store`, MessagePack extension types, or BSON binary subtype bytes.

## Dependencies and Integration Points

- Standard library dependencies include iterators, streams, `FILE*`, strings, vectors, arrays, type traits, memory, numeric conversion, locale, `snprintf`, `memcpy`, `ldexp`, `isfinite`, hashing, and optional C++23 `std::byteswap`.
- Library-internal dependencies include `value_t`, `parse_error`, `out_of_range`, `invalid_iterator`, `exception`, `position_t`, `char_traits`, `iterator_traits`, detection/type-trait helpers, `concat`, `conditional_static_cast`, `value_in_range_of`, `make_array`, ABI/macro wrappers, and `JSON_ASSERT`/`JSON_THROW`.
- `basic_json` integration is heavy: the code uses `BasicJsonType` aliases for numbers, strings, binary containers, object/array storage, parser callbacks, exception types, allocator behavior through containers, max-size checks, parent-link maintenance, and optional diagnostic positions.
- Text and binary parsers share the SAX contract. Any custom SAX consumer used with `sax_parse` must satisfy the exact `is_sax_static_asserts` surface, including binary values and parse-error handling.
- Binary formats integrate with public APIs such as `from_cbor`, `from_msgpack`, `from_ubjson`, `from_bjdata`, and `from_bson` elsewhere in the header. This chunk supplies the core reader they call.
- Iterators integrate with `basic_json::begin`, `end`, `items`, object key/value iteration, array traversal, and primitive single-value iteration.
- WiredTiger integration is indirect: test code can include this vendored header and rely on consistent JSON behavior without involving WiredTiger build artifacts beyond include paths and compiler settings.

## Risks and Maintenance Notes

- This is vendored third-party code. Local edits risk diverging from upstream nlohmann behavior and should generally be avoided unless the vendored dependency is intentionally patched.
- Large untrusted inputs can consume memory while building strings, binaries, arrays, objects, or DOM trees. The code avoids pre-reserving huge string/binary sizes in some paths, but it still appends/read-loops until declared lengths, EOF, or allocation failure.
- Parser recursion is mostly avoided in text JSON by using an explicit state stack, but binary CBOR, MessagePack, BSON, and UBJSON parsing uses recursive calls for nested values and containers. Deep binary nesting can therefore stress call depth.
- Several binary length conversions rely on `conditional_static_cast`, `value_in_range_of`, and explicit overflow checks. Maintenance around new integer widths or BJData extensions must preserve those guards.
- CBOR tag handling is security-relevant. With `error`, tags are rejected; with `ignore`, tag metadata is skipped; with `store`, supported tag lengths become binary subtypes and the next item is expected to be binary. Callers must choose behavior deliberately.
- BSON support is intentionally partial. Unsupported element type bytes report parse error 114. Tests relying on broader BSON types would fail until additional cases are implemented.
- UTF handling is strict for JSON text strings, but wide-string adapters perform UTF-16/UTF-32 to UTF-8 conversion with limited validation of malformed surrogate usage before the lexer sees bytes. Wide string binary parsing is explicitly rejected.
- Locale handling in numeric scanning is subtle: conversion uses the active C locale decimal point internally while public token strings are normalized back to `.`. Locale-dependent regressions are easy around float parsing.
- `input_adapter(CharT b)` for null-terminated byte pointers uses `strlen`, so embedded NUL bytes truncate text input unless callers pass an explicit range/span.
- `span_input_adapter::get()` returns an rvalue reference to its stored adapter. Misuse after move would be invalid, but the class exists specifically to support `{ptr, len}` adapter construction patterns.
- `json_sax_dom_parser::key` uses `operator[]`, so duplicate object keys overwrite prior values according to `basic_json` object semantics.
- Callback parsing can discard data and then sets a discarded top-level result to null. Tests for callback behavior need to distinguish parse failure from intentional discard.
- Iterator safety relies on assertions for initialized iterators and throws for invalid dereference paths. Behavior with disabled assertions and uninitialized iterators remains undefined per the local comments.

## Test Signals

Useful validation for this chunk includes:

- JSON text parser tests for literals, empty input, trailing input under strict mode, arrays/objects, duplicate keys, callback discard behavior, and `accept` versus `parse`.
- String tests for escapes, Unicode surrogate pairs, malformed `\u` sequences, unescaped control characters, valid and invalid UTF-8, BOM handling, and optional comment skipping.
- Numeric tests for signed, unsigned, floating, exponent, overflow-to-float fallback, non-finite float rejection in text parsing, and locale decimal-point behavior.
- Input adapter tests for `FILE*`, `istream`, lvalue/rvalue streams, iterator ranges, containers, C strings, arrays, spans, null pointer rejection, wide UTF-16/UTF-32 strings, and binary rejection on wide input.
- SAX tests using custom SAX classes to verify compile-time interface checks and event ordering for primitives, objects, arrays, keys, binary values, and parse errors.
- Binary-format round trips and malformed-input tests for BSON, CBOR, MessagePack, UBJSON, and BJData, including strict EOF behavior, unexpected EOF diagnostics, unsupported BSON types, CBOR indefinite containers, CBOR tag modes, MessagePack extension subtype storage, UBJSON optimized containers, BJData unsigned markers, binary optimized arrays, ND-array conversion, and high-precision numbers.
- Endianness-sensitive tests for numeric decoding on little- and big-endian hosts or through targeted byte-swap unit tests.
- Hash tests showing different values for different JSON types with similar payloads, object key/value contribution, array ordering, binary byte contents, and binary subtype presence.
- Iterator tests for begin/end on null, primitives, arrays, and objects; dereference and arrow behavior; const/non-const conversion; and invalid dereference exceptions.
