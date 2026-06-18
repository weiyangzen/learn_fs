# subset-b-008399 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/encodings.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/encodings.h

Purpose: This header defines RapidJSON's encoding concept implementations and transcoding glue for Unicode and byte streams. It covers UTF-8, UTF-16 native, UTF-16LE/BE, UTF-32 native, UTF-32LE/BE, ASCII, runtime-selected `AutoUTF`, and `Transcoder` templates used by the reader, writer, encoded streams, schema regex, and pointer URI fragment handling.

Important APIs and types: Key types are `UTF8`, `UTF16`, `UTF16LE`, `UTF16BE`, `UTF32`, `UTF32LE`, `UTF32BE`, `ASCII`, `UTFType`, `AutoUTF`, and `Transcoder`. Each encoding exposes `Ch`, `supportUnicode`, `Encode`, `EncodeUnsafe`, `Decode`, `Validate`, `TakeBOM`, `Take`, `PutBOM`, and `Put`. UTF-8 uses `GetRange()` classification for DFA-style validation. `AutoUTF` dispatches through static function-pointer tables keyed by stream `GetType()`.

Control flow: Encode paths branch by codepoint range and emit one or more code units. Decode paths consume stream code units, validate continuation/surrogate/range rules, and return false on malformed input. Byte-order variants explicitly compose or decompose little- and big-endian byte sequences and skip BOMs when present. `Transcoder<Source, Target>` decodes a codepoint from the source and encodes it to the target, while the same-encoding specialization copies one code unit and delegates validation to the encoding.

State and persistence behavior: There is no persistent storage. State lives only in caller-provided streams and static lookup tables. Invalid encodings consume bytes/code units as they validate, so callers depend on parse-error propagation rather than rewind.

Dependencies and integration points: It depends on `rapidjson.h`, stream `Put`/`Take` concepts, and `PutUnsafe` from `stream.h`. Reader string parsing, writer output, encoded input/output streams, regex decoding, and pointer percent transcodes all rely on these exact semantics.

Risks: UTF decoding is boundary-sensitive: overlong UTF-8, surrogate halves, invalid continuations, BOM handling, and stream truncation can all corrupt parse behavior if changed. `ASCII::supportUnicode = 0` means non-ASCII data must be rejected or escaped by callers. `AutoUTF` assumes valid runtime `UTFType` indexes.

Test signals: Cover UTF-8 boundary codepoints, invalid UTF-8 classes, UTF-16 surrogate pairs and lone surrogates, UTF-32 values above `0x10FFFF`, BOM detection for every endian variant, same-encoding copy versus validate behavior, ASCII rejection above `0x7F`, and `AutoUTF` dispatch for each `UTFType`.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/encodings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/en.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/en.h

Purpose: This header provides RapidJSON's default English parse-error message mapper. It translates `ParseErrorCode` enum values from `error.h` into human-readable strings for diagnostics.

Important APIs and types: The single public API is `GetParseError_En(ParseErrorCode)`, returning `const RAPIDJSON_ERROR_CHARTYPE*`. It covers every parse error declared in `error.h`, including document, value, object, array, string, number, termination, and unspecific syntax errors. Messages are wrapped in `RAPIDJSON_ERROR_STRING()` so users can redefine error character handling.

Control flow: The function is an inline `switch` over `ParseErrorCode`. Known codes return fixed string literals; the default branch returns "Unknown error." This switch-based mapping is intentionally safer when enum values are extended because new cases remain visible in compiler diagnostics when warnings are enabled.

State and persistence behavior: There is no runtime state or persistence. Returned pointers refer to static string literals in the translation unit after macro expansion.

Dependencies and integration points: It includes `error.h` and is commonly used with `ParseResult::Code()`, `GenericReader::GetParseErrorCode()`, and `GenericDocument::GetParseError()`. Applications can copy this file to localize messages.

Risks: Message text is part of user-facing diagnostics, so changing strings can break tests that assert exact output. Locale customization depends on consistent `RAPIDJSON_ERROR_CHARTYPE` and `RAPIDJSON_ERROR_STRING` definitions across all included RapidJSON headers.

Test signals: Verify every `ParseErrorCode` maps to the expected English message, unknown numeric codes map to the fallback, and custom `RAPIDJSON_ERROR_CHARTYPE`/`RAPIDJSON_ERROR_STRING` builds compile.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/en.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/error.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/error.h

Purpose: This header defines RapidJSON parse error codes, the `ParseResult` value wrapper, and customization hooks for error-message character type and string literal conversion.

Important APIs and types: `ParseErrorCode` enumerates all reader/document parse failures, starting with `kParseErrorNone`. `ParseResult` stores a `ParseErrorCode` plus byte/code-unit offset and exposes `Code()`, `Offset()`, `operator bool`, `IsError()`, equality with codes or results, `Clear()`, and `Set()`. `GetParseErrorFunc` is a function pointer for locale-specific mappers such as `GetParseError_En`.

Control flow: Parsing code constructs or mutates `ParseResult` as it detects syntax or encoding failures. The boolean conversion returns success when `code_ == kParseErrorNone`; offsets are caller-supplied and meaningful only on error.

State and persistence behavior: `ParseResult` is a small in-memory value object. No filesystem or global state exists, but the macros `RAPIDJSON_ERROR_CHARTYPE` and `RAPIDJSON_ERROR_STRING` are compile-time ABI/configuration state that must remain consistent across translation units.

Dependencies and integration points: It includes `rapidjson.h` for namespace, size type, and diagnostic macros. Reader and document parse APIs return or expose these codes; `error/en.h` maps them to text.

Risks: Equality operators compare only `code_`, not `offset_`; tests or callers expecting offset-sensitive equality can be surprised. Adding, reordering, or renaming enum values affects diagnostics and localization tables. The macro customization surface can create mismatched string types if defined inconsistently.

Test signals: Cover success and error `ParseResult` construction, bool conversion, `Clear`/`Set`, equality ignoring offset, all enum values accepted by local message mappers, and customized error character builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/error/error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filereadstream.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filereadstream.h

Purpose: `FileReadStream` adapts a `std::FILE*` plus caller-owned buffer to RapidJSON's input stream concept for byte-oriented parsing.

Important APIs and types: The class exposes `typedef char Ch`, constructor `FileReadStream(std::FILE*, char*, size_t)`, `Peek()`, `Take()`, `Tell()`, and `Peek4()` for encoding detection. Output-stream functions are present only to satisfy concept shape and assert if called.

Control flow: Construction asserts a non-null file and a buffer of at least four bytes, then performs an initial `Read()`. `Take()` returns the current byte and advances through `Read()`. `Read()` increments inside the current buffer until exhausted, then uses `fread()` to refill. A short read appends a `'\0'` sentinel, advances `bufferLast_`, and marks EOF.

State and persistence behavior: Runtime state tracks `fp_`, `buffer_`, `bufferSize_`, `bufferLast_`, `current_`, `readCount_`, cumulative `count_`, and `eof_`. It reads from the file but does not own or close it. `Tell()` is derived from fully consumed chunks plus current buffer offset.

Dependencies and integration points: It includes `stream.h` and `<cstdio>`. Reader/document parsing can use it directly, and encoded input streams use `Peek4()` to detect BOM/UTF type.

Risks: The caller must keep the file and buffer alive. `fread()` errors are not distinguished from EOF. `Peek()` after EOF returns the sentinel. Buffer sizes below four violate assumptions needed by encoding detection.

Test signals: Parse from small and large buffers, verify `Tell()` across buffer refills, confirm EOF sentinel behavior, check `Peek4()` availability near buffer boundaries, and exercise short-read and empty-file parsing.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filereadstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filewritestream.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filewritestream.h

Purpose: `FileWriteStream` adapts a `std::FILE*` plus caller-owned buffer to RapidJSON's output stream concept for byte-oriented JSON writing.

Important APIs and types: The class exposes `typedef char Ch`, constructor `FileWriteStream(std::FILE*, char*, size_t)`, `Put(char)`, `PutN(char, size_t)`, and `Flush()`. A specialized free `PutN(FileWriteStream&, char, size_t)` delegates to the efficient member implementation.

Control flow: `Put()` flushes when the buffer is full and writes one byte into the buffer. `PutN()` fills the available buffer with `memset`, flushing as many complete chunks as necessary, then stores any remainder. `Flush()` writes buffered bytes with `fwrite()` and resets `current_` to the buffer start.

State and persistence behavior: The stream holds raw pointers to the file and buffer and tracks `bufferEnd_` and `current_`. It writes to the file but does not own or close it. Write failures are deliberately ignored except for avoiding unused-result warnings, so no sticky error state is exposed.

Dependencies and integration points: It includes `stream.h` and `<cstdio>`. `Writer`, `PrettyWriter`, and encoded output streams can use it as a sink. The generic `PutN` specialization is used by indentation and repeated-character output.

Risks: Callers must call `Flush()` or close/flush the underlying file after writer completion. Partial writes are silent, which can hide disk or pipe failures. Copying is disabled to avoid duplicate buffer ownership assumptions.

Test signals: Verify exact bytes for buffered writes, boundary flushes, `PutN()` across multiple buffer-size chunks, explicit final flush, behavior with very small buffers, and simulated partial `fwrite()` if a test harness can intercept it.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/filewritestream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/fwd.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/fwd.h

Purpose: This header centralizes forward declarations and default typedefs for RapidJSON's public types. It lets users and other headers refer to RapidJSON classes without pulling in full definitions.

Important APIs and types: It forward declares encodings, `Transcoder`, allocators, string streams, string buffers, file streams, memory streams, reader, writer, pretty writer, document/member/value types, pointer types, and schema types. Default typedefs include `StringStream`, `InsituStringStream`, `StringBuffer`, `MemoryBuffer`, `Reader`, `Value`, `Document`, `Pointer`, `SchemaDocument`, `IRemoteSchemaDocumentProvider`, and `SchemaValidator`.

Control flow: There is no executable flow. The header includes `rapidjson.h`, opens the configured namespace, declares templates/classes, and defines aliases wired to `UTF8<char>`, `CrtAllocator`, and `MemoryPoolAllocator<CrtAllocator>`.

State and persistence behavior: No state or persistence exists. The important behavior is compile-time dependency management and ABI consistency through shared typedef choices.

Dependencies and integration points: It is an integration surface across all RapidJSON modules. Code can include `fwd.h` in interfaces to avoid heavy dependencies on `document.h`, `reader.h`, `writer.h`, or `schema.h`.

Risks: Forward declarations must match the real template parameter lists exactly. The default typedefs couple callers to UTF-8 and default allocator choices. Any namespace customization must be visible consistently because these declarations live under `RAPIDJSON_NAMESPACE`.

Test signals: Compile-only tests should include `fwd.h` before and after full headers, instantiate all typedefs after including their definitions, and verify custom namespace builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/fwd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/biginteger.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/biginteger.h

Purpose: `internal::BigInteger` is a fixed-capacity unsigned big integer used by precise decimal-to-double conversion in `strtod.h`.

Important APIs and types: The class stores 64-bit `Type` digits in little-endian order with fixed `kCapacity`. It supports construction from `uint64_t` or decimal character spans, copy/assignment, addition by `uint64_t`, multiplication by `uint64_t` or `uint32_t`, left shift, equality, `MultiplyPow5`, `Difference`, `Compare`, `GetCount`, `GetDigit`, and `IsZero`.

Control flow: Decimal construction parses chunks up to 19 digits, repeatedly multiplying the current value by `10^chunkLength` using `MultiplyPow5(exp) <<= exp`, then adding the parsed chunk. Multiplication uses platform intrinsics or `unsigned __int128` when available, with a manual 32-bit split fallback. Difference orders operands, subtracts with borrow, and returns whether the original value was smaller than the RHS.

State and persistence behavior: State is the in-object digit array and count. There is no heap allocation or persistence. The capacity is sized for decimal conversion workloads rather than arbitrary unbounded arithmetic.

Dependencies and integration points: It depends on `rapidjson.h` and optional MSVC x64 intrinsics. `strtod.h` uses it to compare an approximated double against the exact scaled decimal within half an ULP.

Risks: Capacity assertions protect expected parse ranges but are not recoverable in release builds if assumptions are violated. Shift and multiplication code is architecture-sensitive. `Difference()` assumes unequal operands and writes only significant digits, so callers must initialize/interpret output carefully.

Test signals: Cover decimal parsing across chunk boundaries, multiplication by 0/1/large values, powers of five, left shifts by word and non-word bit counts, comparison ordering, exact differences, and fallback multiplication on non-x64 builds.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/biginteger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/diyfp.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/diyfp.h

Purpose: This header implements `internal::DiyFp`, the normalized 64-bit significand/exponent representation used by Grisu2 double-to-string and string-to-double conversion.

Important APIs and types: `DiyFp` exposes constructors from raw `(uint64_t, int)` and `double`, subtraction, multiplication, `Normalize()`, `NormalizeBoundary()`, `NormalizedBoundaries()`, `ToDouble()`, IEEE-754 constants, and public fields `f` and `e`. Free helpers `GetCachedPowerByIndex`, `GetCachedPower`, and `GetCachedPower10` return cached powers of ten as `DiyFp` plus decimal exponent metadata.

Control flow: The double constructor decodes exponent and significand bits, adding the hidden bit for normal values. Multiplication produces the high half of a 128-bit product with rounding. Normalization shifts the significand until the top bit is set. Boundary computation derives minus/plus rounding bounds for shortest decimal generation. Cached power selection uses a precomputed table from `10^-348` through `10^340`.

State and persistence behavior: There is no mutable global state. Static lookup tables hold cached powers. All conversion state is local value data.

Dependencies and integration points: It depends on `rapidjson.h` and optional compiler intrinsics. `dtoa.h` uses it for Grisu2; `strtod.h` uses cached powers and `ToDouble()` in approximation.

Risks: Bit-level IEEE-754 assumptions are central. Multiplication and normalization have compiler-specific branches. Cached-power table indexes must stay aligned with exponent arrays. NaN/Inf handling is not performed here and must be filtered by callers.

Test signals: Verify decoded components for normal, denormal, and boundary doubles; multiplication rounding; normalized boundaries for powers of two; cached power exponent/index selection; and round-trip support through dtoa/strtod tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/diyfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/dtoa.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/dtoa.h

Purpose: This header provides RapidJSON's internal double-to-ASCII conversion using the Grisu2 algorithm plus formatting prettification.

Important APIs and functions: Core functions are `GrisuRound`, `CountDecimalDigit32`, `DigitGen`, `Grisu2`, `WriteExponent`, `Prettify`, and `dtoa(double, char*, int maxDecimalPlaces = 324)`. It uses `DiyFp`, cached powers, `Double` from `ieee754.h`, and `GetDigitsLut()` from `itoa.h`.

Control flow: `dtoa()` handles signed zero specially, emits a leading minus for negative finite values, runs `Grisu2()` to generate shortest significant digits and decimal exponent, then `Prettify()` chooses fixed or scientific notation. `DigitGen()` emits integral digits first, then fractional digits while tracking the safe rounding interval; `GrisuRound()` adjusts the last digit if the generated value is closer after decrementing.

State and persistence behavior: No persistent state exists. The caller owns the output buffer and receives a returned end pointer. Formatting mutates the buffer in place using `memmove` and appended punctuation/exponent bytes.

Dependencies and integration points: `Writer::WriteDouble()` relies on this output. The code depends on finite input handling by callers or writer policy. Integer digit LUT and cached power tables are performance-critical dependencies.

Risks: Buffer sizing is caller responsibility. `maxDecimalPlaces` truncates fixed decimal forms and can intentionally produce rounded-down display. NaN/Inf are not formatted here. Edge cases around negative zero, exponent thresholds, halfway values, and mantissa overflow are regression-sensitive.

Test signals: Cover zero and negative zero, smallest/largest normal and denormal finite doubles, powers of ten, halfway rounding cases, fixed-versus-exponent threshold transitions, `maxDecimalPlaces` truncation, and JSON writer integration for non-finite handling policy.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/dtoa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/ieee754.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/ieee754.h

Purpose: `internal::Double` wraps IEEE-754 binary64 bit inspection and small helper operations used by RapidJSON number parsing and formatting.

Important APIs and types: Constructors accept `double` or raw `uint64_t`. Methods include `Value()`, `Uint64Value()`, `NextPositiveDouble()`, `Sign()`, `Significand()`, `Exponent()`, `IsNan()`, `IsInf()`, `IsNanOrInf()`, `IsNormal()`, `IsZero()`, `IntegerSignificand()`, `IntegerExponent()`, `ToBias()`, and static `EffectiveSignificandSize(int order)`.

Control flow: Methods mask and shift the raw `uint64_t` representation. Normal values include the hidden significand bit; denormal values use the denormal exponent path. `NextPositiveDouble()` increments the raw representation and asserts the value is non-negative.

State and persistence behavior: State is a union of `double` and `uint64_t` in the wrapper object. There is no external state or persistence.

Dependencies and integration points: It depends on `rapidjson.h` for constants and assertions. `dtoa.h` uses it for zero/sign detection, while `strtod.h` uses integer significands, exponents, ULP comparison, and next-double adjustment.

Risks: The implementation assumes IEEE-754 binary64 layout and compatible union type punning. `IsNormal()` treats zero as normal for hidden-bit decisions through `Significand() == 0`, matching this code's needs but not the strict mathematical definition. `NextPositiveDouble()` is only valid for positive finite ranges.

Test signals: Verify bit decoding for zero, negative zero, normal, denormal, infinity, and NaN; `IntegerExponent()` around denormal boundaries; `EffectiveSignificandSize()` for underflow and normal orders; and `ToBias()` ordering behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/ieee754.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/itoa.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/itoa.h

Purpose: This header implements fast integer-to-decimal conversion helpers for writer output and pointer index stringification.

Important APIs and functions: `GetDigitsLut()` returns a 200-byte lookup table for pairs `"00"` through `"99"`. `u32toa`, `i32toa`, `u64toa`, and `i64toa` write decimal digits into a caller-supplied buffer and return the end pointer.

Control flow: Unsigned conversions split values into groups of two, four, eight, or sixteen decimal digits to minimize divisions and branches. Signed conversions emit `'-'` and convert through two's-complement negation (`~u + 1`) to handle minimum signed values without overflow. No null terminator is appended by these functions.

State and persistence behavior: There is no mutable state. The LUT is a static const array. Output is written only into the caller's buffer.

Dependencies and integration points: It includes `rapidjson.h`. `writer.h` uses it for integer JSON numbers, `dtoa.h` uses the LUT for exponent writing, and `pointer.h` uses it to construct array-index token names in `Append(SizeType)`.

Risks: Caller buffer sizing is critical: 32-bit signed values need up to 11 chars and 64-bit signed values up to 20 plus sign. Functions do not append `'\0'`, so callers that need strings must do so themselves. Threshold branches must preserve leading-zero behavior inside grouped suffixes.

Test signals: Verify min/max signed and unsigned 32/64-bit values, every digit-count threshold, zero, negative minimum values, no unintended leading zeros, and pointer append stringification for `SizeType` width.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/itoa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/meta.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/meta.h

Purpose: This header provides lightweight compile-time type traits and SFINAE helpers for RapidJSON without requiring C++11 `<type_traits>` by default.

Important APIs and types: It defines `Void`, `BoolType`, `TrueType`, `FalseType`, `SelectIf`, `BoolExpr`, `NotExpr`, `AndExpr`, `OrExpr`, `AddConst`, `MaybeAddConst`, `RemoveConst`, `IsSame`, `IsConst`, `IsMoreConst`, `IsPointer`, `IsBaseOf`, `EnableIf`, and `DisableIf`. Macros `RAPIDJSON_ENABLEIF`, `RAPIDJSON_DISABLEIF`, `RAPIDJSON_ENABLEIF_RETURN`, and `RAPIDJSON_DISABLEIF_RETURN` wrap the internal SFINAE machinery.

Control flow: There is no runtime flow. Template specialization and enum `Value` constants drive overload selection, const-correct iterator conversions, pointer/value overload disambiguation, and optional use of `std::is_base_of` when `RAPIDJSON_HAS_CXX11_TYPETRAITS` is enabled.

State and persistence behavior: No runtime state or persistence. The file is pure compile-time infrastructure.

Dependencies and integration points: It includes `rapidjson.h` and optionally `<type_traits>`. `document.h`, `pointer.h`, and related DOM APIs use these traits to constrain constructors and overloads.

Risks: The custom `IsBaseOf` implementation is a simplified Boost-style trait and can behave differently from full standard traits for exotic incomplete/private cases. The macros are subtle; misuse can yield difficult template errors. `NULL` appears in SFINAE defaults, so macro contexts must stay compatible with C++03.

Test signals: Compile tests should verify overload selection for pointer versus value types, const-to-nonconst conversion rejection, base-class detection with and without `<type_traits>`, and custom namespace qualification in SFINAE macros.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/meta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/pow10.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/pow10.h

Purpose: This header supplies a fast lookup-table implementation for `10.0^n` used during decimal-to-double conversion.

Important APIs and functions: The single function is `internal::Pow10(int n)`, which asserts `0 <= n <= 308` and returns a `double` from a static table containing `1e0` through `1e308`.

Control flow: `Pow10()` performs only an assertion and direct array indexing. It avoids repeated multiplication or standard-library `pow()` calls for speed and predictable results.

State and persistence behavior: No mutable state or persistence. The static const table is read-only process data.

Dependencies and integration points: It depends on `rapidjson.h`. `strtod.h` uses it in `FastPath()` and normal-precision conversion when exponents fall in representable ranges.

Risks: The function only supports non-negative exponents up to the maximum finite decimal exponent for double. Callers must handle negative exponents by division and underflow ranges separately. Table correctness is fundamental to number parsing accuracy.

Test signals: Validate returned values for boundary exponents `0`, `1`, `22`, `308`, assert behavior for invalid exponents in debug builds, and cross-check representative values against standard conversion results in strtod tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/pow10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/regex.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/regex.h

Purpose: This header implements RapidJSON's internal ECMAScript-subset regular expression engine, primarily for JSON Schema `pattern` validation.

Important APIs and types: `GenericRegex<Encoding, Allocator>` parses a pattern into a Thompson NFA and exposes `IsValid()`, `Match(InputStream&)`, `Match(const Ch*)`, `Search(InputStream&)`, and `Search(const Ch*)`. `Regex` aliases UTF-8 default allocation. Internal state includes `State`, `Range`, `Frag`, parser operator stacks, range lists, and mutable search state sets.

Control flow: Construction decodes the source pattern into codepoints, parses operators, groups, character classes, anchors, and quantifiers, then patches fragments into an NFA ending at a match state. Quantifiers clone fragments as needed for bounded repetitions. Search maintains current and next state lists, expands split states through `AddState()`, tests codepoints and ranges, and honors `^`/`$` anchoring.

State and persistence behavior: The compiled regex persists in memory as stack-backed `states_` and `ranges_`; `stateSet_`, `state0_`, and `state1_` are mutable search buffers. No filesystem persistence exists. Match/search methods are logically const but mutate internal buffers, so shared concurrent use is risky.

Dependencies and integration points: It depends on `allocators.h`, `stream.h`, and `internal::Stack`. Schema validation uses it for string pattern checks. Encoding decoding defines what a pattern character means.

Risks: Unsupported escapes fail parsing. Bounded repetition can clone many states and consume memory. `stateSet_` is allocated from the states allocator and manually freed. Mutable search buffers make thread safety non-obvious. Anchoring behavior differs between `Match()` and `Search()`.

Test signals: Cover literals, alternation, concatenation, groups, `?`, `*`, `+`, `{n}`, `{n,}`, `{n,m}`, anchors, dot, class ranges, negated classes, escaped metacharacters, invalid patterns, Unicode patterns, schema integration, and concurrent-use expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/regex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/stack.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/stack.h

Purpose: `internal::Stack` is RapidJSON's type-unsafe growable byte stack used for parser stacks, writer nesting levels, memory buffers, regex states, and temporary construction storage.

Important APIs and types: The template `Stack<Allocator>` exposes constructor, destructor, optional C++11 move operations, `Swap`, `Clear`, `ShrinkToFit`, `Reserve<T>`, `Push<T>`, `PushUnsafe<T>`, `Pop<T>`, `Top<T>`, `End<T>`, `Bottom<T>`, `HasAllocator`, `GetAllocator`, `Empty`, `GetSize`, and `GetCapacity`.

Control flow: Memory allocation is lazy. The first expansion creates an owned allocator if none was supplied and allocates `initialCapacity_`. Later expansions grow capacity by 1.5x or to the exact needed size. `Resize()` uses allocator `Realloc` and restores the top pointer from the saved size. `ShrinkToFit()` frees memory completely when empty.

State and persistence behavior: State is allocator pointers plus raw `char*` base/top/end. It owns memory allocated through the allocator and may own the allocator itself. No persistence exists, but many higher-level objects rely on stack memory lifetime.

Dependencies and integration points: It includes `allocators.h` and `swap.h`. It underpins `MemoryBuffer`, `Writer` level state, `Reader` parse state, regex compilation/search, and pointer/document internals.

Risks: It is type-unsafe and does not run destructors for stored objects. Alignment depends on allocator behavior and caller usage. `PushUnsafe()` requires a prior successful reserve. Copying is disabled; move support depends on feature macros.

Test signals: Cover lazy allocation, growth, typed push/pop/top/bottom, reserve plus unsafe push, clear versus shrink, allocator ownership, swap, move construction/assignment when enabled, and integration with memory buffers and writer nesting.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strfunc.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strfunc.h

Purpose: This header provides small string helpers that work across RapidJSON encoding character types.

Important APIs and functions: `StrLen(const Ch*)` counts code units in a null-terminated string and returns `SizeType`. `CountStringCodePoint<Encoding>()` decodes a fixed-length encoded string and returns the number of Unicode codepoints through an output parameter.

Control flow: `StrLen()` advances until the zero terminator. `CountStringCodePoint()` wraps the input in `GenericStringStream<Encoding>`, decodes until the stream reaches the provided end pointer, increments a count for each valid codepoint, and returns false if decoding fails.

State and persistence behavior: No persistent state. The functions only read caller-provided memory and, for codepoint counting, update `outCount`.

Dependencies and integration points: It includes `stream.h` for `GenericStringStream` and depends on encoding `Decode()` methods. Pretty writer convenience overloads use `StrLen`; schema/string validation and length-related logic can use codepoint counting.

Risks: `StrLen()` counts code units, not Unicode characters, which matters for UTF-8 and UTF-16. `CountStringCodePoint()` assumes the supplied length points to complete encoded data; truncated sequences return false after consuming through the temporary stream.

Test signals: Cover narrow and wide strings, embedded null behavior through length-aware paths, UTF-8 multibyte counts, invalid encoding rejection, and distinction between code-unit length and codepoint count.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strfunc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strtod.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strtod.h

Purpose: This header implements RapidJSON's internal decimal-to-double conversion, combining fast paths, DiyFp approximation, and BigInteger correction for full precision.

Important APIs and functions: Key functions are `FastPath`, `StrtodNormalPrecision`, `Min3`, `CheckWithinHalfULP`, `StrtodFast`, `StrtodDiyFp`, `StrtodBigInteger`, and `StrtodFullPrecision`. Inputs are parsed decimal digits, their length, decimal position, and exponent from the reader's number parser.

Control flow: Normal precision multiplies or divides by powers of ten with underflow splitting. Full precision first tries the exact fast path for small exponents/significands, trims leading and trailing zeros, limits extremely long digit sequences, checks underflow, then uses `DiyFp` cached powers to approximate. If the approximation is not provably outside the uncertain half-ULP band, `BigInteger` compares the exact scaled decimal against the candidate double and adjusts to the next positive double if needed.

State and persistence behavior: No persistent state. Temporary `BigInteger`, `DiyFp`, and `Double` values hold conversion state on the stack.

Dependencies and integration points: It depends on `ieee754.h`, `biginteger.h`, `diyfp.h`, and `pow10.h`. Reader number parsing feeds it and then stores results in DOM values or SAX events.

Risks: Decimal-position/exponent arithmetic is subtle, especially after zero trimming. The 780-digit cap and underflow check affect extreme inputs. Rounding-to-even and half-ULP comparison are correctness-critical. Negative values are handled by callers, so this code assumes non-negative significands in full precision.

Test signals: Cover fast-path exact integers, disguised fast paths, long decimals, leading/trailing zeros, subnormal underflow, overflow handled by reader, halfway round-to-even cases, next-double adjustment, and consistency against standard `strtod` on representative inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strtod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/swap.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/swap.h

Purpose: This header defines a minimal `internal::Swap()` helper to avoid depending on `<algorithm>` for primitive swaps.

Important APIs and functions: `template <typename T> inline void Swap(T& a, T& b) RAPIDJSON_NOEXCEPT` copies `a` into a temporary, assigns `b` to `a`, then assigns the temporary to `b`.

Control flow: There is only the three-assignment swap sequence. It is intended for primitive or pointer-like types used by RapidJSON internals.

State and persistence behavior: No state beyond the two references being swapped. No persistence.

Dependencies and integration points: It includes `rapidjson.h` for namespace and `RAPIDJSON_NOEXCEPT`. `Stack::Swap()` and regex search state swapping use it.

Risks: The comment explicitly says primitive C++ types only. Using it for complex types can be slower or semantically wrong if move-aware or exception-aware swapping is needed. It does not use ADL or specialized swaps.

Test signals: Simple compile/runtime checks for primitive values and pointers, plus integration tests for `Stack::Swap()` preserving allocator and buffer state.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/swap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/istreamwrapper.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/istreamwrapper.h

Purpose: `BasicIStreamWrapper` adapts `std::basic_istream`-derived objects to RapidJSON's input stream concept.

Important APIs and types: `BasicIStreamWrapper<StreamType>` exposes `Ch`, constructor from a stream reference, `Peek()`, `Take()`, `Tell()`, and `Peek4()` for byte-stream encoding detection. Typedefs `IStreamWrapper` and `WIStreamWrapper` cover `std::istream` and `std::wistream`.

Control flow: `Peek()` delegates to `stream_.peek()` and returns `'\0'` on EOF. `Take()` calls `stream_.get()`, increments an internal count only on successful reads, and returns `'\0'` on EOF. `Tell()` returns this count instead of `tellg()` because `tellg()` can fail. `Peek4()` temporarily reads up to four bytes, stores them in a mutable buffer, clears EOF state if needed, puts bytes back in reverse order, and returns null if fewer than four are available.

State and persistence behavior: The wrapper holds a reference to the stream, a read count, and a mutable four-character peek buffer. It does not own or close the stream.

Dependencies and integration points: It includes `stream.h` and `<iosfwd>`. It lets document/reader parsing operate on C++ streams without copying into memory first.

Risks: `Peek4()` asserts one-byte `Ch`, so it is not for wide streams. Putback may fail on unusual stream buffers. The count can diverge from external stream repositioning because the wrapper assumes sequential reads.

Test signals: Parse from string streams and file streams, verify `Tell()` after reads and EOF, exercise `Peek4()` success/failure and putback preservation, wide-stream basic parsing, and behavior with externally manipulated streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/istreamwrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/memorybuffer.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/memorybuffer.h

Purpose: `GenericMemoryBuffer` is an in-memory byte output stream, mainly used with encoded output streams or callers that need raw generated bytes rather than a null-terminated string buffer.

Important APIs and types: The template `GenericMemoryBuffer<Allocator>` exposes `Ch = char`, constructor with optional allocator and capacity, `Put`, `Flush`, `Clear`, `ShrinkToFit`, `Push`, `Pop`, `GetBuffer`, `GetSize`, `kDefaultCapacity`, and public mutable `internal::Stack<Allocator> stack_`. `MemoryBuffer` is the default typedef, and `PutN(MemoryBuffer&, char, size_t)` is specialized with `memset`.

Control flow: `Put()` pushes one byte on the stack. `Push()` and `Pop()` expose bulk stack operations. `Flush()` is a no-op because data is already in memory. `ShrinkToFit()` delegates to the underlying stack.

State and persistence behavior: The buffer owns stack memory through the selected allocator, unless an external allocator is supplied. It is not null-terminated and has no persistence.

Dependencies and integration points: It includes `stream.h` and `internal/stack.h`. Encoded output streams and users needing binary buffers integrate with this stream concept.

Risks: `GetBuffer()` may be null when empty and is invalidated by later stack growth. Callers must use `GetSize()` because no terminator is appended. Exposing `stack_` enables optimized `PutN` but also leaks internals.

Test signals: Cover writes, bulk `PutN`, `Push`/`Pop`, clear and shrink behavior, custom allocator use, empty buffer access, and encoded output integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/memorybuffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/memorystream.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/memorystream.h

Purpose: `MemoryStream` adapts a caller-provided byte buffer and explicit size to RapidJSON's input stream concept.

Important APIs and types: The struct exposes `Ch = char`, constructor `MemoryStream(const Ch* src, size_t size)`, `Peek()`, `Take()`, `Tell()`, `Peek4()`, and public fields `src_`, `begin_`, `end_`, and `size_`. Output stream methods assert if called.

Control flow: `Peek()` returns the current byte or `'\0'` at end. `Take()` returns the current byte and advances unless already at end, where it returns `'\0'`. `Tell()` is pointer subtraction from the beginning. `Peek4()` returns the current pointer only when at least four bytes remain.

State and persistence behavior: The stream does not own the buffer. State is the current pointer and bounds. It reads from memory only and persists nothing.

Dependencies and integration points: It includes `stream.h`. It is useful for `EncodedInputStream` and `AutoUTFInputStream` because it supports `Peek4()` while unlike `StringStream` it does not require null termination or an encoding.

Risks: Caller must keep the source buffer alive. `'\0'` can be a valid byte inside the buffer but also marks end for stream concept consumers, so byte-level wrappers must honor size and parser expectations. Public fields can be mutated by callers.

Test signals: Cover empty buffers, buffers containing null bytes, exact end behavior, `Tell()` after reads, `Peek4()` at offsets with three/four bytes remaining, and parsing non-null-terminated JSON data.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/memorystream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/inttypes.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/inttypes.h

Purpose: This compatibility header supplies C99-style `inttypes.h` definitions for older Microsoft Visual C++ compilers that lack complete support.

Important APIs and types: It includes local `stdint.h`, defines `imaxdiv_t`, `PRI*` and `SCN*` format macros for signed/unsigned exact, least, fast, max, and pointer-width integers, and maps `imaxabs`, `imaxdiv`, `strtoimax`, `strtoumax`, `wcstoimax`, and `wcstoumax` to MSVC CRT equivalents. For MSVC 2013 and newer it delegates to system `<inttypes.h>`.

Control flow: Preprocessor guards reject non-MSVC compilers. `_MSC_VER >= 1800` uses the platform header. Older branches define macros conditionally based on C++ format macro rules. The inline `imaxdiv()` computes quotient and remainder and adjusts for negative numerators with positive remainders.

State and persistence behavior: No runtime state except local variables in `imaxdiv()`. The header affects compile-time macro namespace.

Dependencies and integration points: `rapidjson.h` includes this on old MSVC when RapidJSON supplies 64-bit integer support. It pairs with `msinttypes/stdint.h`.

Risks: Format macros are compiler/CRT-specific and easy to break across MSVC versions or architectures. The header intentionally errors outside MSVC. Macro collisions with Boost or system headers are mitigated but still possible.

Test signals: Compile on representative old MSVC versions, verify format/scanning macros for 32/64-bit and pointer widths, test `imaxdiv()` sign behavior, and ensure MSVC 2013+ delegates cleanly.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/inttypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/stdint.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/stdint.h

Purpose: This compatibility header supplies C99-style fixed-width integer types, limits, and constants for Microsoft Visual C++ compilers.

Important APIs and types: It defines exact-width, least-width, fast-width, pointer-width, and max-width integer typedefs such as `int8_t`, `uint64_t`, `intptr_t`, and `uintmax_t`; limit macros such as `INT32_MAX`, `UINT64_MAX`, `SIZE_MAX`; and constant macros such as `INT64_C` and `UINTMAX_C`. For MSVC 2010+ it includes system `<stdint.h>` but overrides integer constant macros to avoid warnings.

Control flow: Preprocessor guards reject non-MSVC compilers. Compiler-version branches either delegate to system support or define types manually. Architecture branches distinguish `_WIN64` pointer and size limits from 32-bit builds.

State and persistence behavior: There is no runtime state. The header mutates the compile-time macro/type namespace.

Dependencies and integration points: `rapidjson.h` includes it for `_MSC_VER < 1800` when RapidJSON needs global `int64_t`/`uint64_t`. `msinttypes/inttypes.h` depends on it.

Risks: This is legacy toolchain compatibility code. Incorrect `_MSC_VER`, `_WIN64`, or `_M_ARM` handling can break builds. The file deliberately wraps `<wchar.h>` linkage for older environments, which is fragile. Macro definitions can collide with other portability headers.

Test signals: Compile with supported MSVC versions and architectures, verify sizes and signedness of typedefs, constants for min/max values, `_W64` pointer types on 32-bit, and coexistence with Boost/system integer headers.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/msinttypes/stdint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/ostreamwrapper.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/ostreamwrapper.h

Purpose: `BasicOStreamWrapper` adapts `std::basic_ostream`-derived objects to RapidJSON's output stream concept.

Important APIs and types: `BasicOStreamWrapper<StreamType>` exposes `Ch`, constructor from a stream reference, `Put(Ch)`, and `Flush()`. Typedefs `OStreamWrapper` and `WOStreamWrapper` cover `std::ostream` and `std::wostream`. Input/in-situ methods assert if called.

Control flow: `Put()` forwards one character to `stream_.put(c)`. `Flush()` calls `stream_.flush()`. No buffering is added by the wrapper; buffering remains the responsibility of the underlying stream buffer.

State and persistence behavior: The wrapper stores only a reference to the stream. It does not own, close, or track error state. Persistence is whatever the wrapped stream performs.

Dependencies and integration points: It includes `stream.h` and `<iosfwd>`. `Writer` and `PrettyWriter` can serialize JSON directly to standard streams through this adapter.

Risks: Stream errors are not surfaced through the wrapper API. The not-implemented methods return `char` rather than `Ch`, but they assert and are not intended for use. Copying is disabled because the stream reference is non-owning.

Test signals: Write compact and pretty JSON to `std::ostringstream`, wide output to `std::wostringstream`, explicit flush behavior, and underlying stream failure handling expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/ostreamwrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/pointer.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/pointer.h

Purpose: This header implements RFC 6901 JSON Pointer support for RapidJSON DOM values, including parsing, stringification, querying, creation, mutation, defaulting, swapping, erasing, and convenience free functions.

Important APIs and types: Public types include `PointerParseErrorCode`, `GenericPointer<ValueType, Allocator>`, nested `Token`, typedef `Pointer`, and helpers such as `CreateValueByPointer`, `GetValueByPointer`, `GetValueByPointerWithDefault`, `SetValueByPointer`, `SwapValueByPointer`, and `EraseValueByPointer`. `Token` stores name, code-unit length, and parsed array index or `kPointerInvalidIndex`.

Control flow: Parsing detects plain or URI-fragment form, splits on `/`, unescapes `~0` and `~1`, percent-decodes URI fragments, validates required percent encoding, and detects numeric array indexes without leading zeros or overflow. `Get()` walks objects by member name and arrays by numeric index. `Create()` walks or builds the path, converting parents to object or array as implied by tokens, growing arrays with nulls, and treating `"-"` as append. `Set`, `GetWithDefault`, and `Swap` are layered on `Create`; `Erase` walks to the parent and removes a member or array element.

State and persistence behavior: A parsed pointer owns an allocator optionally, one contiguous allocation for tokens plus name buffer, parse error offset/code, and token count. User-supplied token construction avoids allocation and leaves token lifetime external. DOM mutation persists in the caller's `GenericValue`/`GenericDocument`, not in the pointer.

Dependencies and integration points: It includes `document.h` and `internal/itoa.h`, and uses encodings/transcoders for URI fragments. It is a high-level DOM integration point.

Risks: `Create()` can change parent types and discard existing values when the path implies a different shape. URI fragment handling is strict about percent encoding. Equality returns false for invalid pointers regardless of token equality. User-supplied tokens must outlive the pointer. Array growth can allocate large null-filled arrays for large indexes.

Test signals: Cover RFC examples, empty pointer root access, invalid escapes and percent encodings, URI fragment stringification, numeric index detection and overflow, leading-zero object keys, `"-"` append, `Create()` type conversion, `Get()` unresolved-token index, default insertion, erase root failure, object/array erasure, copy/assignment ownership, and helper free functions.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/pointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/prettywriter.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/prettywriter.h

Purpose: `PrettyWriter` extends `Writer` with indentation, newlines, spaces, and optional single-line arrays while preserving the SAX handler interface.

Important APIs and types: `PrettyFormatOptions` defines `kFormatDefault` and `kFormatSingleLineArray`. `PrettyWriter<OutputStream, SourceEncoding, TargetEncoding, StackAllocator, writeFlags>` inherits `Writer` and implements handler methods `Null`, `Bool`, integer/uint/double numbers, `RawNumber`, `String`, `StartObject`, `Key`, `EndObject`, `StartArray`, `EndArray`, and `RawValue`. Configuration methods are `SetIndent()` and `SetFormatOptions()`.

Control flow: Each value method calls `PrettyPrefix(type)` before delegating to base write methods. `PrettyPrefix()` inspects the top level stack: arrays get commas and either spaces or newline+indent; objects alternate between key positions and value positions, emitting commas/newlines between members and colon-space between key and value. End methods pop level state, optionally write closing indentation, and flush when the root completes.

State and persistence behavior: State is inherited writer state plus `indentChar_`, `indentCharCount_`, and `formatOptions_`. The underlying output stream receives bytes/chars; no filesystem persistence is owned by the writer.

Dependencies and integration points: It includes `writer.h`, relies on base `Level` stack and write primitives, uses `internal::StrLen` for convenience overloads, and `PutN` for indentation.

Risks: Object member sequencing is enforced by assertions only; invalid SAX event order can produce invalid output in release builds. `RawValue()` may not be re-indented internally. The second constructor does not initialize `formatOptions_` in this copy, so using it before `SetFormatOptions()` risks indeterminate formatting behavior.

Test signals: Cover object/array pretty output, empty containers, nested indentation, tabs/newline indent chars, single-line arrays, root-only flush, invalid event assertions in debug, raw value insertion, and constructor behavior without an immediate output stream.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/prettywriter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/rapidjson.h -->
# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/rapidjson.h

Purpose: This is RapidJSON's central configuration and common-definition header. It establishes version macros, namespace customization, platform detection, integer/size types, assertion/static assertion utilities, compiler diagnostic macros, C++11 feature flags, allocation customization hooks, and the JSON `Type` enum.

Important APIs and macros: Public configuration includes `RAPIDJSON_MAJOR_VERSION`, `RAPIDJSON_MINOR_VERSION`, `RAPIDJSON_PATCH_VERSION`, `RAPIDJSON_VERSION_STRING`, `RAPIDJSON_NAMESPACE`, `RAPIDJSON_HAS_STDSTRING`, `RAPIDJSON_NO_INT64DEFINE`, `RAPIDJSON_FORCEINLINE`, `RAPIDJSON_ENDIAN`, `RAPIDJSON_64BIT`, `RAPIDJSON_ALIGN`, `RAPIDJSON_UINT64_C2`, `RAPIDJSON_48BITPOINTER_OPTIMIZATION`, `RAPIDJSON_SIMD`, `RAPIDJSON_NO_SIZETYPEDEFINE`, `RAPIDJSON_ASSERT`, `RAPIDJSON_STATIC_ASSERT`, `RAPIDJSON_LIKELY`, `RAPIDJSON_UNLIKELY`, `RAPIDJSON_NOEXCEPT`, `RAPIDJSON_NEW`, and `RAPIDJSON_DELETE`. It defines `SizeType` by default and enum `Type` values for all JSON kinds.

Control flow: Most behavior is preprocessor selection. It detects endian via compiler/libc/architecture macros, selects 64-bit alignment, enables lower-48-bit pointer packing on x86-64, defines SIMD availability when requested, imports C99 integer headers or MSVC compatibility headers, and maps compiler-specific diagnostic and feature macros.

State and persistence behavior: No runtime state. Compile-time macro state controls ABI, object layout, enabled overloads, and assertions across all RapidJSON headers.

Dependencies and integration points: Every RapidJSON header depends on this file directly or indirectly. FoundationDB's vendored copy inherits these compile-time decisions wherever RapidJSON is included.

Risks: Inconsistent macro definitions across translation units can create ODR and ABI problems. Endianness detection has hard errors for unknown platforms. The 48-bit pointer optimization assumes x86-64 virtual address layout. Default `SizeType` is 32-bit even on 64-bit systems unless overridden.

Test signals: Compile with custom namespace, custom `SizeType`, std::string enabled/disabled, old MSVC integer support, endian overrides, assertions/static assertions, 32-bit and 64-bit builds, pointer optimization toggles, and writer/document behavior under custom allocation macros.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/rapidjson.h -->
