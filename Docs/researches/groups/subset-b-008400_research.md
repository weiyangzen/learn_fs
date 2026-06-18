# subset-b-008400 Research

This grouped report covers the exact source files assigned to `subset-b-008400`. Each source file has its own marker-delimited section so the report can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/reader.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/reader.h

## Purpose

`reader.h` implements RapidJSON's SAX-style JSON parser. `GenericReader` reads JSON from a `Stream`, emits synchronous handler events, supports recursive and iterative parsing modes, and is the primary event source used by `Document`, `SchemaValidatingReader`, and callers that stream JSON without building a DOM.

## Important APIs and Types

The public parse surface is `GenericReader<SourceEncoding, TargetEncoding, StackAllocator>::Parse<parseFlags>(InputStream&, Handler&)`, plus error accessors `HasParseError`, `GetParseErrorCode`, and `GetErrorOffset`. `Reader` aliases UTF-8 source/target parsing. `ParseFlag` configures in-situ parsing, encoding validation, iterative parsing, stop-when-done behavior, full-precision numbers, comments, number-as-string mode, trailing commas, and NaN/Inf acceptance. `BaseReaderHandler` defines default no-op handler behavior, and the handler concept includes scalar events, `RawNumber`, strings/keys, and object/array boundaries.

## Control Flow

Normal `Parse` clears the previous `ParseResult`, installs an RAII stack clearer, skips whitespace/comments, rejects empty input, parses one root value, and optionally checks for root singularity. `ParseValue` dispatches by leading character to object, array, string, literal, or number parsers. Objects and arrays loop through members/elements, call handler begin/end events, count children, enforce commas/colons/brackets, and optionally accept trailing commas. Strings are decoded through `ParseStringToStream`, handling escapes, surrogate pairs, optional transcoding validation, and SIMD fast paths for unescaped byte scans. Numbers are parsed through `NumberStream`, selecting int, uint, int64, uint64, double, raw number, or NaN/Inf handler events based on flags and range.

Iterative parsing replaces recursive descent with a small predictive state machine. It tokenizes the next byte, uses a state/token transition table, pushes parent state and member/element counts on `internal::Stack`, and calls the same scalar/string/object/array handlers during transitions. `HandleError` maps parser states to specific `ParseErrorCode` values when the state machine reaches an invalid transition or EOF too early.

## State and Persistence

The reader persists no JSON data beyond the current parse. Per-instance state is an `internal::Stack` used for decoded non-in-situ strings, full-precision number buffers, and iterative parser frames, plus the last `ParseResult`. In-situ parsing writes decoded strings back into the mutable input stream. `ClearStackOnExit` clears transient stack memory after parse completion or exception-style early exits.

## Dependencies and Integration Points

The header depends on RapidJSON allocators, stream abstractions, encoded streams, transcoding/encoding primitives, `internal::Stack`, `internal::strtod`, and error definitions. It has optional SSE2/SSE4.2 acceleration for whitespace and unescaped string scanning. `SchemaValidatingReader` and DOM `Document` parsing rely on this reader's handler protocol, and `RAPIDJSON_PARSE_ERROR_NORETURN` is a customization point for projects that throw exceptions instead of storing parse results.

## Risks and Edge Cases

The parser assumes stream implementations correctly provide null-terminated or sentinel-backed input; SIMD paths read aligned 16-byte blocks after alignment checks and therefore are sensitive to invalid buffer contracts. In-situ parsing is destructive and returns non-copy string pointers into the input. Handler methods can terminate parsing by returning false, which becomes `kParseErrorTermination`. Full-precision numeric parsing is slower and uses temporary stack buffers. NaN/Inf, comments, and trailing commas are non-standard and only accepted when explicitly flagged. `kParseStopWhenDoneFlag` allows trailing data to remain unread after a valid root.

## Test Signals

Useful tests include strict JSON root singularity, empty and malformed object/array syntax, all parse flags, comment and trailing-comma acceptance/rejection, in-situ decoded string mutation, invalid escape and surrogate handling, encoding validation failures, integer boundary promotion to 64-bit or double, exponent overflow, full-precision round trips, NaN/Inf gating, handler termination, iterative-vs-recursive parity, and SIMD/non-SIMD builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/schema.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/schema.h

## Purpose

`schema.h` implements RapidJSON's JSON Schema support. It compiles a JSON schema document into immutable internal schema nodes and validates JSON SAX event streams against type, structural, string, numeric, combinator, reference, and dependency constraints.

## Important APIs and Types

The main public types are `GenericSchemaDocument<ValueT, Allocator>`, `SchemaDocument`, `GenericSchemaValidator<SchemaDocumentType, OutputHandler, StateAllocator>`, `SchemaValidator`, `IGenericRemoteSchemaDocumentProvider`, and `SchemaValidatingReader`. Internally, `internal::Schema` represents one compiled schema node, `SchemaValidationContext` stores per-node validation state, `Hasher` computes order-sensitive array and order-insensitive object hashes for `enum` and `uniqueItems`, and `ISchemaStateFactory` lets schemas create nested validators, hashers, and state allocations.

## Control Flow

`GenericSchemaDocument` recursively walks the source schema, creates `internal::Schema` nodes keyed by JSON Pointer, and resolves `$ref` entries. Local references are deferred in `schemaRef_` until the initial graph is built; remote references are resolved immediately through an optional `IRemoteSchemaDocumentProvider`. Each `Schema` constructor inspects recognized keywords and prepares type bitmasks, enum hashes, all/any/one/not validator slots, properties, pattern properties, required flags, dependencies, additional property/item rules, tuple/list item schemas, string length/pattern rules, and numeric bounds.

`GenericSchemaValidator` is itself a SAX handler. For each incoming value it pushes the applicable schema context, calls the current schema's keyword-specific method, forwards events to parallel validators for `allOf`, `anyOf`, `oneOf`, `not`, schema dependencies, and pattern properties, then passes valid events to the output handler. Object keys append JSON Pointer tokens, select property/pattern/additional-property schemas, and track required/dependency existence. Array values select list, tuple, or additional item schemas and append numeric pointer tokens. `EndValue` checks enum/combinator/not outcomes, updates `uniqueItems` hashes in the parent array, pops schema context, and trims the document pointer stack.

## State and Persistence

`GenericSchemaDocument` owns compiled schema nodes in `schemaMap_`, unresolved reference records in `schemaRef_`, and an allocator if one was not supplied. It is immutable after construction. `GenericSchemaValidator` stores mutable validation state in `schemaStack_`, document pointer text in `documentStack_`, a `valid_` flag, optional allocator ownership, and nested validator/hash state allocated through the state factory. No state is persisted outside memory.

## Dependencies and Integration Points

The header depends on `document.h`, `pointer.h`, numeric math, RapidJSON allocators/stacks, and either RapidJSON's internal regex engine, `std::regex`, or no regex depending on compile-time macros. It integrates directly with `reader.h` through SAX handler methods and with downstream handlers through validator event forwarding. Verbose mode optionally uses `stringbuffer.h` for diagnostic pointer output.

## Risks and Edge Cases

Regex support is compile-time dependent; invalid patterns become null and therefore silently disable matching for that pattern. Property lookup is linear over gathered property names, which can be costly for very large object schemas. `multipleOf` for doubles checks an exact floating remainder and can be sensitive to representation error. `uniqueItems` uses hash codes, so correctness depends on hash collision improbability rather than structural comparison. `$ref` handling supports JSON Pointer fragments and provider-backed remote documents, but unresolved or invalid references degrade to typeless behavior through default schema pointers. The implementation targets an older JSON Schema dialect and ignores unknown keywords.

## Test Signals

Tests should validate every supported keyword family: type, enum, allOf/anyOf/oneOf/not, object properties, required, property and schema dependencies, patternProperties, additionalProperties, min/maxProperties, list and tuple items, additionalItems, uniqueItems, min/maxItems, min/maxLength with multibyte code points, pattern matching with available regex backend, minimum/maximum exclusivity, integer/number distinctions, multipleOf, local and remote `$ref`, invalid-schema tolerance, invalid schema/document pointer reporting, validator reset/reuse, and `SchemaValidatingReader` parse-error plus schema-error combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/schema.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stream.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stream.h

## Purpose

`stream.h` defines RapidJSON's stream concept and provides the basic string-backed streams used by the reader and writer. It is the small abstraction layer that lets parsing and writing operate over memory buffers, encoded streams, file streams, and custom user streams with the same API.

## Important APIs and Types

The stream concept requires `Ch`, `Peek`, `Take`, `Tell`, `PutBegin`, `Put`, `Flush`, and `PutEnd`, though read-only and write-only streams only implement the subset they need. `StreamTraits<Stream>::copyOptimization` lets the reader make local stream copies for cheap-copy streams. Utility functions `PutReserve`, `PutUnsafe`, and `PutN` support generic and specialized output paths. `GenericStringStream<Encoding>` is a read-only string stream, `StringStream` is its UTF-8 alias, `GenericInsituStringStream<Encoding>` is a read-write in-situ parsing stream, and `InsituStringStream` is its UTF-8 alias.

## Control Flow

`GenericStringStream` advances a `src_` pointer on `Take`, returns `*src_` on `Peek`, and computes offsets relative to `head_`. Its write methods assert because it is read-only. `GenericInsituStringStream` reads from `src_`, writes through `dst_` after `PutBegin`, and uses `PutEnd` to report bytes written; `Push` and `Pop` let parsers reserve or roll back decoded output. `PutN` reserves capacity when possible and emits repeated characters with `PutUnsafe`.

## State and Persistence

String streams only hold raw pointers into caller-owned memory. They do not allocate or own buffers. In-situ streams mutate the supplied input buffer during parsing and maintain separate read and write cursors. `StreamTraits` marks both string stream variants as safe for local copy optimization.

## Dependencies and Integration Points

The header includes `rapidjson.h` and `encodings.h`. `reader.h` depends on these streams for normal and in-situ parsing, `writer.h` and `stringbuffer.h` consume the stream utility functions, and users can specialize `StreamTraits` plus `PutReserve`/`PutUnsafe` for custom streams.

## Risks and Edge Cases

`GenericStringStream` assumes the input has a readable terminator; it performs no bounds checks. Calling write methods on read-only streams or `Put` before `PutBegin` on in-situ streams is an assertion failure, not a recoverable runtime error. Because streams borrow external storage, lifetime and mutability are the caller's responsibility.

## Test Signals

Tests should cover `Peek`/`Take`/`Tell` offsets, local copy optimization behavior in reader paths, in-situ `PutBegin`/`Put`/`PutEnd` mutation, `Push`/`Pop` cursor changes, `PutN` output with specialized streams, and custom stream trait specialization.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stringbuffer.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stringbuffer.h

## Purpose

`stringbuffer.h` implements RapidJSON's in-memory output stream. `GenericStringBuffer` is the usual sink for `Writer`, schema diagnostics, and any API that needs generated JSON or pointer text as a contiguous string.

## Important APIs and Types

`GenericStringBuffer<Encoding, Allocator>` exposes stream-compatible `Put`, `PutUnsafe`, and `Flush`, buffer management methods `Clear`, `ShrinkToFit`, `Reserve`, `Push`, `PushUnsafe`, and `Pop`, plus `GetString` and `GetSize`. `StringBuffer` aliases UTF-8 with `CrtAllocator`. The header specializes `PutReserve`, `PutUnsafe`, and `PutN<StringBuffer>` so writer hot paths can reserve stack space and use `memset` for repeated UTF-8 chars.

## Control Flow

Writes push characters into an `internal::Stack`. `GetString` temporarily pushes a null terminator, immediately pops it, and returns the stack bottom pointer, giving callers a null-terminated view without changing logical size. `ShrinkToFit` uses the same temporary terminator trick before compacting. Move construction and assignment transfer the underlying stack when C++11 rvalue references are available.

## State and Persistence

The buffer owns an `internal::Stack<Allocator>` and optionally uses a caller-supplied allocator. Data remains in memory until `Clear`, destruction, or stack reallocation. Returned `GetString` pointers are invalidated by later mutations or reallocations. Copy construction and assignment are intentionally disabled.

## Dependencies and Integration Points

The header depends on `stream.h` and `internal/stack.h`. `writer.h` includes it for the common `Writer<StringBuffer>` specialization, and schema verbose diagnostics can stringify pointers through `GenericStringBuffer`.

## Risks and Edge Cases

`GetString` on an empty buffer depends on stack bottom behavior after the temporary push/pop. `GetSize` reports bytes in the internal stack, not character count for wide encodings. `PutUnsafe` and `PushUnsafe` require prior reservation and can overrun if used incorrectly by custom code. Pointer stability is only guaranteed until the next mutating operation.

## Test Signals

Tests should cover writing and reading null-terminated output, clearing and reusing buffers, reserve/push/pop behavior, shrink-to-fit preserving content, move semantics where enabled, writer integration, and `PutN` specialization for repeated UTF-8 characters.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/stringbuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/writer.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/writer.h

## Purpose

`writer.h` implements RapidJSON's SAX-style JSON generator. `Writer` receives handler events or direct method calls and writes syntactically correct compact JSON to an output stream while tracking object/array nesting.

## Important APIs and Types

`Writer<OutputStream, SourceEncoding, TargetEncoding, StackAllocator, writeFlags>` implements the handler methods `Null`, `Bool`, integer and double overloads, `RawNumber`, `String`, `StartObject`, `Key`, `EndObject`, `StartArray`, and `EndArray`. It also exposes `Reset`, `IsComplete`, `GetMaxDecimalPlaces`, `SetMaxDecimalPlaces`, string/key convenience overloads, and `RawValue`. `WriteFlag` controls encoding validation and NaN/Inf emission. Internal `Level` records whether a nested level is an array and how many values have been emitted.

## Control Flow

Each public value method calls `Prefix` to emit required separators and enforce object key position assertions, writes the value, then calls `EndValue` to flush when the root value is complete. Objects and arrays push a `Level` after writing `{` or `[`, and pop it before writing `}` or `]`. Scalars use internal integer/double conversion helpers. Strings reserve worst-case escaped capacity, write a quote, stream through source characters, emit required escapes or Unicode surrogate pairs, optionally validate encoding, then write the closing quote. `RawValue` injects caller-provided JSON without validation beyond assertions.

## State and Persistence

The writer keeps a pointer to the current output stream, a stack of nesting `Level` objects, `maxDecimalPlaces_`, and `hasRoot_`. `Reset` replaces the stream, clears nesting, and permits reuse for another JSON document. Persistent output is owned by the supplied stream, commonly `StringBuffer`; the writer itself stores only generation state.

## Dependencies and Integration Points

The header depends on `stream.h`, `stringbuffer.h`, `internal::Stack`, string length helpers, integer/double conversion helpers, and optional SSE2/SSE4.2 intrinsics. It is the canonical output handler for `Reader::Parse` and `Document::Accept`, and it has full specializations for `Writer<StringBuffer>` to write numbers and SIMD-scanned string chunks directly into the buffer.

## Risks and Edge Cases

Structural correctness is enforced mostly with assertions, so release builds can generate invalid JSON if calls are made out of sequence. `RawValue` trusts the caller to provide well-formed JSON. NaN and Infinity are rejected unless the write flags allow them, and those outputs are not standard JSON. `SetMaxDecimalPlaces` truncates some double renderings and can affect round-trip precision. The `Writer<StringBuffer>::WriteDouble` specialization checks `kWriteDefaultFlags` for NaN/Inf rather than the template `writeFlags`, which is worth regression testing if non-default flags are used with the specialization.

## Test Signals

Tests should cover scalar rendering, nested object/array separator placement, object key assertions, reset and complete-state behavior, string escaping and Unicode transcoding, invalid encoding with validation enabled, raw values, decimal-place truncation, NaN/Inf gating, `StringBuffer` specializations, SIMD and non-SIMD string paths, and reader-to-writer round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/writer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/CMakeLists.txt -->
# sources/storage-engines/foundationdb/contrib/rapidxml/CMakeLists.txt

## Purpose

This CMake file declares RapidXML as a header-only interface library for the FoundationDB source tree. It gives consumers a target they can link against to inherit the RapidXML include directory.

## Important APIs and Types

The build API is the `rapidxml` CMake target created with `add_library(rapidxml INTERFACE)`. `target_include_directories(rapidxml INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/include")` publishes the local `include` directory to target consumers.

## Control Flow

Configuration simply registers the interface target and attaches include usage requirements. No source files are compiled and no install/export rules are defined here.

## State and Persistence

There is no runtime state. Build-system state is limited to the CMake target and its include path property during configure/generate.

## Dependencies and Integration Points

Any FoundationDB target that links to `rapidxml` receives the RapidXML headers on its include path. The file assumes the vendored RapidXML headers live under `contrib/rapidxml/include` relative to this CMake file.

## Risks and Edge Cases

Because the target is header-only, consumers rely on transitive include propagation and compiler settings from their own targets. The file does not guard against duplicate target names, does not define version metadata, and does not expose system include semantics. A moved or missing `include` directory would only surface when a dependent target compiles.

## Test Signals

Build validation should configure the FoundationDB tree, link at least one consumer against `rapidxml`, and compile a translation unit that includes a RapidXML header through the target's propagated include directory.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidxml/CMakeLists.txt -->
