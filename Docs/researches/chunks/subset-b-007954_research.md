# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucJson.hh lines 6195-13847

## Scope

This chunk covers the middle of XRootD's vendored `nlohmann/json` 3.12.0 single-header implementation. The assigned range starts at the `adl_serializer` definition, then includes binary subtype support, JSON hashing, input adapters, the JSON lexer, SAX interfaces and DOM-building SAX handlers, binary readers for BSON/CBOR/MessagePack/UBJSON/BJData, the recursive-descent JSON text parser, and the beginning of iterator support.

This is not XRootD-specific application code. Its integration role is to provide the `nlohmann::json` API that XRootD includes through `XrdOucJson.hh`, with an escape hatch at the top of the file to use the system `nlohmann/json.hpp` instead when `USE_SYSTEM_NLOHMANN_JSON` is defined.

## Purpose

The code in this chunk is the parsing and traversal core for JSON values. It lets callers:

- customize conversion to and from user types through argument-dependent `to_json` and `from_json`;
- represent binary JSON values with optional numeric subtypes;
- hash JSON values for use in standard unordered containers;
- adapt many input sources into a uniform byte stream;
- tokenize JSON text, validate UTF-8, decode escapes, and classify numeric tokens;
- drive SAX consumers for validation-only parsing, DOM construction, or callback-filtered DOM construction;
- parse binary encodings into the same SAX event stream;
- expose iterator primitives used by `basic_json::iterator` and `const_iterator`.

For XRootD consumers, the practical effect is that configuration or protocol code using `nlohmann::json` can parse strings, streams, byte buffers, CBOR/MessagePack/UBJSON/BJData/BSON data, and then traverse or convert the resulting DOM with upstream-compatible behavior.

## Important APIs, Types, and Functions

- `nlohmann::adl_serializer<ValueType>` at lines 6197-6230 forwards conversion to free `::nlohmann::from_json` and `::nlohmann::to_json` overloads. This is the default customization hook used by `basic_json::get<T>()` and assignment/construction from arbitrary types.
- `byte_container_with_subtype<BinaryType>` at lines 6254-6336 extends a byte container with `subtype_type`, `set_subtype`, `subtype`, `has_subtype`, and `clear_subtype`. The sentinel for "no subtype" is returned as all-ones `uint64_t`, while `m_has_subtype` records whether that sentinel is meaningful.
- `detail::combine` and `detail::hash` at lines 6370-6474 implement recursive JSON hashing. The value type is included in the seed so `null`, `false`, signed zero-like numbers, unsigned values, strings, arrays, objects, and binary blobs do not collapse solely by payload.
- `detail::input_format_t` at line 6549 identifies supported input encodings: JSON, CBOR, MessagePack, UBJSON, BSON, and BJData.
- Input adapters at lines 6555-7056 normalize sources. They include `file_input_adapter`, `input_stream_adapter`, `iterator_input_adapter`, wide-string adapters, container/pointer/array overloads for `input_adapter`, and `span_input_adapter`.
- `detail::lexer_base` and `detail::lexer` begin at lines 7122 and 7198. They define token kinds, token names, source positions, string and number buffers, and scanner methods such as `scan_string`, `scan_comment`, `scan_number`, and `scan`.
- `json_sax<BasicJsonType>` at lines 8738-8859 is the abstract event interface: scalar events, `start_object`, `key`, `end_object`, `start_array`, `end_array`, and `parse_error`.
- `detail::json_sax_dom_parser` at lines 8881-9185 turns SAX events into a `BasicJsonType` DOM by maintaining a stack of object/array pointers.
- `detail::json_sax_dom_callback_parser` at lines 9187-9622 adds `parser_callback_t` filtering, with keep stacks for values and object keys and a discarded sentinel for skipped content.
- `detail::json_sax_acceptor` at lines 9624-9698 is a validation-only SAX target that returns true for valid events and false on parse errors.
- SAX trait utilities at lines 9733-9892 detect whether a user SAX type implements the required methods with compatible return types.
- `detail::binary_reader<BasicJsonType, InputAdapterType, SAX>` at lines 9910-12914 converts BSON, CBOR, MessagePack, UBJSON, and BJData byte streams to SAX events.
- `detail::parser<BasicJsonType, InputAdapterType>` at lines 12996-13469 parses JSON text tokens from the lexer and drives a SAX target.
- `detail::primitive_iterator_t`, `detail::internal_iterator`, and the start of `detail::iter_impl` at lines 13517-13847 provide the storage and constructor logic for iterating primitive, array, and object JSON values.

## Control Flow

Text JSON parsing starts by adapting the input with `detail::input_adapter`, constructing a `lexer`, and then constructing a `parser`. `parser::parse` selects either `json_sax_dom_parser` or `json_sax_dom_callback_parser` depending on whether a callback was supplied. `parser::accept` uses `json_sax_acceptor` for validation. `parser::sax_parse` drives a caller-provided SAX target.

`parser::sax_parse_internal` is an iterative recursive-descent state machine. It reads an initial token, emits a scalar, object-start, or array-start event, and pushes `false` for objects or `true` for arrays onto a state stack. After each value it evaluates the enclosing state: arrays accept commas and `]`; objects accept commas, string keys, colons, values, and `}`. Strict mode requires end-of-input after the top-level value. `ignore_trailing_commas` allows `,]` and `,}` in the state-evaluation branches.

Lexing is split by token class. `scan_string` validates RFC 8259 strings, handles standard escapes, decodes `\u` sequences including surrogate pairs, rejects unescaped control characters, and validates multibyte UTF-8 byte ranges. `scan_number` uses an explicit finite state machine with labels to enforce JSON number grammar, accumulates the token text, then classifies it as signed integer, unsigned integer, or floating point. `scan_comment` is available only when the parser is configured to ignore comments, and handles `//` and `/* ... */` comments.

DOM construction is event-driven. `json_sax_dom_parser::handle_value` assigns the root when the stack is empty, appends to the current array, or writes through `object_element` for the most recent key. Object and array starts push pointers onto `ref_stack`; matching ends set parent pointers and pop the stack. The callback parser uses the same shape, but first calls the callback at object/array starts, keys, values, and object/array ends, then removes or replaces discarded values as needed.

Binary parsing starts in `binary_reader::sax_parse`, which dispatches by `input_format_t`. BSON validates document sizes, reads NUL-terminated keys, and emits typed values for double, string, object, array, binary, boolean, null, integer, and integer64 records. CBOR dispatches on the initial major-type byte and supports unsigned/negative integers, byte strings, UTF-8 strings, arrays, maps, tags, booleans, null, and half/single/double precision floats. MessagePack similarly switches on prefix families for fixints, fixmap, fixarray, fixstr, bin/ext, float, integer, array, and map encodings. UBJSON/BJData parse marker-based values, optimized containers with optional size/type markers, high-precision numbers, and BJData ND-array metadata.

Iterator construction in this chunk is type-directed. `iter_impl(pointer object)` records the owning JSON pointer, initializes an object iterator for objects, an array iterator for arrays, and a `primitive_iterator_t` for all scalar, null, binary, and discarded values. The actual navigation operators continue after this chunk.

## State And Persistence Behavior

This chunk owns no XRootD persistent state. It is header-only library code whose runtime state is stack or object-local during parse/conversion/traversal.

Important transient state includes:

- input adapter cursor state, such as `FILE*`, `std::streambuf*`, iterator pairs, or wide-string UTF-8 buffers;
- lexer state: current character, unget flag, source position, raw token text, decoded token buffer, numeric values, decimal separator, and error message pointer;
- parser state: last token, SAX callback pointer, lexer instance, exception policy, and trailing-comma policy;
- DOM SAX state: root reference, `ref_stack`, current `object_element`, error flag, exception policy, and optional lexer pointer for diagnostic positions;
- callback parser state: `keep_stack`, `key_keep_stack`, and a reusable discarded JSON value;
- binary reader state: current byte, bytes-read count, selected format, endian flag, SAX pointer, and BJData lookup tables.

For persistence, the notable behavior is format compatibility rather than file storage. Binary readers interpret on-wire encodings and produce JSON DOM state. `get_number` swaps numeric byte order depending on host endianness and format: CBOR, MessagePack, and UBJSON use network order, while BSON and BJData are treated as little-endian. CBOR tags can be rejected, ignored, or stored as binary subtypes depending on `cbor_tag_handler_t`.

With `JSON_DIAGNOSTIC_POSITIONS`, DOM SAX parsers also record start and end offsets into JSON values. That state is embedded in parsed values and depends on lexer position accounting, token lengths, and the special object/array start/end handling in the SAX handlers.

## Dependencies And Integration Points

- The chunk depends on the earlier parts of the same header for ABI namespace macros, exception types, `value_t`, type traits, `char_traits`, `position_t`, string concatenation helpers, endian detection, and `BasicJsonType` internals.
- It depends on standard C and C++ headers including `<cstdio>`, `<cstring>`, `<istream>`, `<streambuf>`, `<iterator>`, `<memory>`, `<limits>`, `<cmath>`, `<array>`, `<vector>`, `<string>`, `<tuple>`, `<functional>`, and `<type_traits>`.
- `JSON_NO_IO` removes `FILE*` and `std::istream` adapter support. `USE_SYSTEM_NLOHMANN_JSON` bypasses this vendored body entirely at the top of `XrdOucJson.hh`.
- Public `basic_json` methods later in the file use these internals for `parse`, `accept`, `sax_parse`, `from_cbor`, `from_msgpack`, `from_ubjson`, `from_bjdata`, and `from_bson`.
- Standard library integration later in the full header uses `detail::hash` to specialize `std::hash<nlohmann::json>`.
- XRootD integration is broad and compile-time: any source including `XrdOucJson.hh` obtains this `nlohmann` namespace implementation unless the build chooses the system header. Therefore ABI macro settings and the vendored version must be consistent across translation units.

## Risks And Edge Cases

- This is a vendored third-party header. Local edits risk diverging from upstream `nlohmann/json` behavior and can be hard to reconcile with builds that define `USE_SYSTEM_NLOHMANN_JSON`.
- `adl_serializer` intentionally forwards to free functions with ADL. User-defined conversions can become ambiguous or surprising if multiple `to_json`/`from_json` overloads are visible.
- `byte_container_with_subtype::subtype()` returns all-ones when no subtype is present; callers must check `has_subtype()` instead of treating that value as a real subtype.
- `detail::hash` recurses through all arrays and objects. It is deterministic for a given object ordering but can be expensive for large JSON trees and inherits collision behavior from `std::hash` for strings and numbers.
- `input_stream_adapter` reads through `streambuf` directly and adjusts only EOF state. Code that expects normal `istream` formatted-extraction state transitions may be surprised after parsing.
- Iterator and pointer input adapters depend on lifetime of the underlying data. Passing temporary buffers through low-level adapter paths can produce dangling reads if wrappers are misused.
- String lexing is strict about UTF-8 and control characters. Inputs with comments, unescaped control bytes, malformed surrogate pairs, overlong UTF-8, or invalid continuation bytes will produce parse errors unless the relevant nonstandard parser option is enabled for comments.
- Number scanning uses locale-aware C conversion after replacing or tracking the decimal point, and returns parse errors or falls back between signed, unsigned, and float classifications at numeric limits. Boundary values around `int64_t`, `uint64_t`, NaN, infinity, and decimal/exponent forms are high-value test cases.
- Callback parsing mutates the partially built DOM while callback decisions are made. Incorrect assumptions about callback depth, discarded sentinels, or object key filtering can lead to missing values that are intentional rather than parser corruption.
- `json_sax_dom_parser` and callback parser reach into `BasicJsonType::m_data` internals for performance. That tight coupling means custom `BasicJsonType` specializations must preserve the expected internals.
- Binary format readers trust declared lengths enough to loop and append until EOF or memory pressure. Length fields near `SIZE_MAX`, deeply nested containers, and indefinite-length encodings are important denial-of-service surfaces.
- BJData ND-array support multiplies dimensions and includes explicit overflow checks. Regressions here could wrap array sizes, emit malformed JData annotations, or allow recursive ND arrays, which the current code rejects.
- Binary object formats require string keys. CBOR maps and MessagePack maps are parsed through string-key helpers in this implementation; non-string map keys are not accepted as object keys.
- `get_to` advances `chars_read` specially on short primitive reads to report the failing location. Error positions in binary readers can shift if this accounting is changed.
- The beginning of `iter_impl` asserts that iterators are initialized with a non-null JSON pointer and chooses storage based on the value type at construction. Mutating a JSON value while iterators are live remains subject to the library's usual invalidation rules.

## Test Signals

Useful signals for this chunk are mostly upstream `nlohmann/json` conformance tests or XRootD tests that exercise JSON configuration parsing:

- ADL conversion tests should cover in-place `from_json(j, T&)`, value-returning `from_json(j, identity_tag<T>)`, and `to_json(j, T)` overload resolution.
- Binary JSON tests should cover subtype set/clear/equality, CBOR tag handling modes, and `std::hash` behavior for binary values with and without subtypes.
- Input adapter tests should parse from `std::string`, C strings, byte vectors, iterators, arrays, `FILE*`, `std::istream`, and UTF-16/UTF-32 sources when enabled.
- JSON text parser tests should cover empty input, strict trailing data rejection, allowed/forbidden trailing commas, optional comments, every scalar token, nested arrays/objects, missing separators, and meaningful parse-error positions.
- UTF-8 and escape tests should include all control characters, valid and invalid `\u` escapes, valid surrogate pairs, isolated high/low surrogates, overlong byte forms, truncated multibyte sequences, and maximum code point `U+10FFFF`.
- Numeric tests should include `-0`, signed and unsigned 64-bit boundaries, overflow to floating point, malformed exponent/decimal forms, locale decimal separators, nonfinite float rejection where applicable, and raw token retention for `number_float`.
- SAX tests should verify callback filtering at keys, values, object starts/ends, and array starts/ends, plus validation-only `accept` behavior with `allow_exceptions` both true and false.
- Binary reader tests should cover BSON document length validation, CBOR indefinite strings/binaries/arrays/maps, MessagePack fix and extended forms, UBJSON optimized arrays/objects, BJData unsigned markers, high-precision numbers, ND-array conversion to `_ArrayType_`, `_ArraySize_`, and `_ArrayData_`, and EOF in the middle of primitive reads.
- Iterator tests for the visible portion should verify begin/end setup for primitive, array, and object values once the later iterator methods are included.
- Build tests should compile with and without `JSON_NO_IO`, with `USE_SYSTEM_NLOHMANN_JSON`, and across compilers with different endian and byteswap support to ensure this vendored header and the system-header path remain behaviorally compatible enough for XRootD.
