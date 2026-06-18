# Research Group subset-b-009397

This grouped report covers FlatBuffers support headers vendored under `sources/test-tools/syzkaller/executor/_include/flatbuffers`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flexbuffers.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/flexbuffers.h

## Purpose

`flexbuffers.h` implements the self-describing FlexBuffers binary format in a header-only form. It provides type tags, compact width selection, readers, writers, JSON-like rendering, in-place scalar/string mutation, map lookup, and structural verification for FlexBuffers buffers. In this syzkaller executor include tree it is vendored as FlatBuffers runtime support; the executor can compile generated or embedded FlatBuffers code without relying on a system FlatBuffers install.

## Important APIs, Types, and Functions

The core format enums are `BitWidth` and `Type`, with helpers such as `IsInline`, `IsTypedVector`, `IsFixedTypedVector`, `ToTypedVector`, `ToTypedVectorElementType`, `PackedType`, and `NullPackedType`. Scalar access is centralized through `ReadSizedScalar`, `ReadInt64`, `ReadUInt64`, `ReadDouble`, `Indirect`, `WidthU`, `WidthI`, and `WidthF`.

Read-side object wrappers are `Object`, `Sized`, `String`, `Blob`, `Vector`, `TypedVector`, `FixedTypedVector`, `Map`, and `Reference`. `Reference` is the main dynamic value handle and exposes predicates (`IsNull`, `IsInt`, `IsMap`, `IsAnyVector`), conversions (`AsInt64`, `AsUInt64`, `AsDouble`, `AsString`, `AsBlob`, `AsVector`, `AsTypedVector`, `AsFixedTypedVector`, `AsMap`, `As<T>`), formatting (`ToString`), and mutation (`MutateInt`, `MutateUInt`, `MutateBool`, `MutateFloat`, `MutateString`).

The writer is `Builder`, configured by `BuilderFlag`. It exposes scalar appenders, keyed appenders, `Key`, `String`, `Blob`, `StartVector`/`EndVector`, `StartMap`/`EndMap`, callback helpers `Vector`, `TypedVector`, `Map`, scalar-array vector helpers, `FixedTypedVector`, `LastValue`, `ReuseValue`, `ForceMinimumBitWidth`, and `Finish`. `Builder::Value` stores pending stack entries before serialization. `Verifier` and free `VerifyBuffer` validate a FlexBuffers buffer.

## Control Flow

Reading starts at `GetRoot(buffer, size)`, which parses backward from the final byte width and packed type, then returns a `Reference` pointing at root data. `Reference` conversions branch on `type_`; inline scalars read directly from `data_` using `parent_width_`, while indirect values compute `Indirect()` and read using `byte_width_`. `Vector::operator[]` reads a per-element packed type table after the vector body. `TypedVector` and `FixedTypedVector` synthesize references from the vector element type. `Map::operator[]` resolves the key vector, chooses a width-specific binary-search comparator, and returns the value at the matching index.

Writing is stack based. Scalar and blob/key/string calls push `Builder::Value` records, while string/key/blob bytes are written immediately to `buf_`. `StartVector` and `StartMap` capture a stack index. `EndVector` or `EndMap` calls `CreateVector`, removes consumed stack entries, and pushes the resulting vector/map value. `EndMap` first validates interleaved key/value stack entries, sorts key/value pairs by serialized key bytes, records duplicate-key detection, writes a typed key vector, then writes the map value vector with a prefixed key offset and key width. `Finish` requires exactly one pending root value, aligns and writes the root value, appends packed type and root byte width, and marks `finished_`.

Verification mirrors the wire layout. `Verifier::VerifyBuffer` reads the final root metadata and calls `VerifyRef`. `VerifyRef` checks byte width, type, offsets, alignment, and recursively validates containers through `VerifyVector`, `VerifyKeys`, and `VerifyKey`. The optional reuse tracker records already verified offsets and packed types to accelerate shared strings/keys and reject conflicting reused locations.

## State and Persistence Behavior

`Reference` and wrapper objects are non-owning views into caller-owned memory. Mutations write directly into that memory and only succeed when the new value fits the original encoded width, or when the replacement string length exactly matches the old string length. `Builder` owns `buf_`, pending `stack_`, key/string pools, duplicate-key state, finish state, sharing flags, and a forced minimum bit width used to make later mutation possible. `Clear` resets buffer, stack, pools, finish state, and forced width but keeps builder flags. No filesystem or process-global persistence is used, except static empty sentinel buffers returned for type-mismatch conversions.

## Dependencies and Integration Points

The header depends on FlatBuffers `base.h` and `util.h` for endian-safe scalar I/O, padding, numeric/string conversion, escaping, assertions, and type traits. It uses STL containers (`std::vector`, `std::set`, `std::map`, `std::string`) and algorithms (`std::sort`, `std::bsearch`). `idl.h` includes this file for parsing JSON-like data into FlexBuffers and for `IDLOptions::use_flexbuffers`. In the syzkaller executor tree, its main integration signal is successful compilation of vendored FlatBuffers-generated code and any executor code that manipulates dynamic FlatBuffers payloads.

## Risks and Edge Cases

The format is compact and pointer-arithmetic heavy. Corrupt buffers can otherwise drive out-of-bounds reads, so callers should use `VerifyBuffer` before reading untrusted bytes. `GetRoot` itself assumes the supplied size is large enough; verification checks `size_ >= 3`. `Map::operator[]` depends on sorted, duplicate-free keys; `Builder` only records duplicate keys in `has_duplicate_keys_` instead of failing. Typed vectors require homogeneous types, fixed typed vectors support only lengths 2 through 4 and scalar element types, and deprecated string vectors are treated as key vectors, truncating embedded NUL strings. `ScalarVector` asserts if length width exceeds element width, which makes byte vectors larger than 255 unsuitable unless represented as blobs. Mutation APIs can silently return false when width constraints are not met. Verification has depth and vector-count limits, but disabling alignment checks or skipping reuse tracking changes both strictness and performance.

## Test Signals

Primary test signals are FlatBuffers upstream FlexBuffers tests for scalar width minimization, vectors/maps, duplicate keys, string/key sharing, mutation, and verifier failures. In this repository, useful signals are syzkaller executor and generated-code builds that include the vendored header, plus any fuzz inputs that feed malformed FlexBuffers through `Verifier`. Regression tests should include truncated root metadata, bad offsets, unterminated keys/strings, nested vectors beyond `max_depth`, duplicate map keys, and mutation of forced-width versus minimal-width scalars.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/flexbuffers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/grpc.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/grpc.h

## Purpose

`grpc.h` glues FlatBuffers buffers to C++ gRPC transport primitives. It wraps `grpc::Slice` in a typed FlatBuffers message, provides a `FlatBufferBuilder` variant backed by gRPC slice allocation, and specializes gRPC `SerializationTraits` so `flatbuffers::grpc::Message<T>` can be used as an RPC payload type.

## Important APIs, Types, and Functions

`flatbuffers::grpc::Message<T>` is a move-only typed wrapper around `grpc::Slice`. It exposes `data`, `mutable_data`, `size`, `Verify`, `GetRoot`, `GetMutableRoot`, and `BorrowSlice`. `SliceAllocator` implements FlatBuffers `Allocator` using a single refcounted `grpc::Slice`; it overrides `allocate`, `deallocate`, and `reallocate_downward`. `detail::SliceAllocatorMember` guarantees allocator construction before `FlatBufferBuilder`. `MessageBuilder` derives from `FlatBufferBuilder`, owns a `SliceAllocator`, can be constructed from an existing `FlatBufferBuilder`, and exposes `Swap`, `ReleaseRaw`, `GetMessage<T>`, and `ReleaseMessage<T>`.

The `grpc::SerializationTraits<flatbuffers::grpc::Message<T>>` specialization implements `Serialize` by packaging the borrowed slice into a `ByteBuffer`, and `Deserialize` by obtaining a single slice via `TrySingleSlice` or `DumpToSingleSlice`, clearing the source buffer, assigning the message, and optionally verifying it.

## Control Flow

For outgoing messages, callers build a buffer with `MessageBuilder`; allocation and growth operate on `grpc::Slice` memory. `GetMessage<T>` calculates the FlatBuffers payload subrange within the builder's downward-growing buffer, takes a subslice from the allocator-owned slice, and wraps it as `Message<T>`. `ReleaseMessage<T>` does the same and then resets the builder. gRPC serialization later borrows that slice and builds a one-slice `ByteBuffer`.

For incoming messages, `Deserialize` tries to obtain a single slice without copying. If that fails, it dumps the `ByteBuffer` to one slice. It clears the original `ByteBuffer`, stores the slice in a `Message<T>`, and unless `FLATBUFFERS_GRPC_DISABLE_AUTO_VERIFICATION` is defined, runs `Message<T>::Verify` before accepting the payload.

## State and Persistence Behavior

State is limited to refcounted slice ownership. `Message<T>` shares the underlying gRPC slice and is move-only to avoid ambiguous ownership. `SliceAllocator` assumes exactly one active allocation and asserts that allocation/deallocation pointers match its slice. `MessageBuilder::Swap` must swap builder state and then restore allocator identity because the allocator is an embedded member whose address must remain the builder's allocator pointer.

## Dependencies and Integration Points

This header depends on `flatbuffers/flatbuffers.h`, `grpcpp/support/byte_buffer.h`, and `grpcpp/support/slice.h`. It integrates with generated FlatBuffers root types through `Verifier::VerifyBuffer<T>`, `GetRoot<T>`, and `GetMutableRoot<T>`, and with gRPC through `SerializationTraits`. It is only usable where the C++ gRPC headers and ABI are available.

## Risks and Edge Cases

The allocator is specialized for one FlatBuffers buffer at a time; misuse outside `MessageBuilder` can trip assertions. Moving from a normal `FlatBufferBuilder` is documented to support only default-allocator builders, because the raw memory becomes owned by a `grpc::Slice` with a deallocator callback. `mutable_data` returns a non-const pointer type from `grpc::Slice::begin()` via const interface semantics, so mutation requires care and should happen only before sharing across threads. Auto-verification can be disabled by macro, which improves speed but allows invalid RPC payloads through.

## Test Signals

Useful tests build a generated FlatBuffer with `MessageBuilder`, serialize and deserialize through gRPC `ByteBuffer`, verify the received root, and exercise multi-slice incoming buffers that require `DumpToSingleSlice`. Negative tests should cover invalid payload verification, move construction/assignment, `ReleaseRaw`, and conversion from a default `FlatBufferBuilder`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/grpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/hash.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/hash.h

## Purpose

`hash.h` provides named FNV-1 and FNV-1a hash implementations used by FlatBuffers schema attributes such as `hash`. It supports 16-, 32-, and 64-bit outputs and exposes lookup tables so parser/generator code can resolve hash function names from schema metadata.

## Important APIs, Types, and Functions

`FnvTraits<T>` supplies the FNV prime and offset basis for `uint32_t` and `uint64_t`. `HashFnv1<T>` and `HashFnv1a<T>` iterate over NUL-terminated input strings and compute the selected FNV variant. `uint16_t` specializations fold the 32-bit hash by XORing high and low 16-bit halves. `NamedHashFunction<T>` pairs a schema-visible name with a function pointer. `kHashFunctions16`, `kHashFunctions32`, and `kHashFunctions64` list supported functions, and `FindHashFunction16`, `FindHashFunction32`, and `FindHashFunction64` linearly search those lists.

## Control Flow

Hashing starts from the type-specific offset basis and consumes bytes until the first NUL byte. FNV-1 multiplies then XORs each byte; FNV-1a XORs then multiplies. Lookup functions iterate over the static named table for the requested width and return the matching function pointer or `nullptr`.

## State and Persistence Behavior

The header is stateless aside from static const lookup arrays. It does not cache results and does not own input memory. Inputs are treated as C strings, so embedded NUL bytes terminate hashing.

## Dependencies and Integration Points

It depends on `<cstdint>`, `<cstring>`, and `flatbuffers/flatbuffers.h`. `idl.h` includes this header, and parser code can call the lookup functions when processing hash attributes in schemas.

## Risks and Edge Cases

The functions are non-cryptographic and should not be used for security decisions or collision-resistant identifiers. The 16-bit variants have very small output space and high collision probability. Passing `nullptr` or non-NUL-terminated data is unsafe. Unknown names return `nullptr`, so callers must check before invoking the returned pointer.

## Test Signals

Good tests compare FNV-1/FNV-1a outputs against known vectors for 32- and 64-bit variants, verify 16-bit folding, and confirm name lookup for all supported names plus failure for unknown names. Parser tests using `hash` schema attributes indirectly exercise this header.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/idl.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/idl.h

## Purpose

`idl.h` defines the in-memory schema model, parser interface, generator options, JSON/text conversion hooks, and gRPC generator declarations for FlatBuffers IDL. It is the shared declaration surface used by `flatc`, schema reflection serialization, JSON parsing, FlexBuffers parsing, and language-specific code generators.

## Important APIs, Types, and Functions

The file defines schema base types through `FLATBUFFERS_GEN_TYPES_*` macros and the `BaseType` enum. Helper functions classify and size types: `IsScalar`, `IsInteger`, `IsFloat`, `IsLong`, `IsBool`, `IsOneByte`, `IsVector`, `IsUnsigned`, `SizeOf`, `TypeName`, and `StringOf`.

The data model is built from `Type`, `Value`, `SymbolTable<T>`, `Namespace`, `Definition`, `FieldDef`, `StructDef`, `EnumVal`, `EnumDef`, `RPCCall`, `ServiceDef`, and `IncludedFile`. `Type` tracks scalar/vector/array/struct/enum shape and can serialize/deserialize reflection types. `FieldDef` records field attributes such as deprecation, key, shared string behavior, native inline, flexbuffer, 64-bit offset, presence, nested FlatBuffer, padding, and sibling union field. `StructDef` owns fields and layout metadata. `EnumDef` owns enum values, union flags, underlying type, sorting and lookup operations. `IDLOptions` contains generator and parser behavior for all supported languages, JSON output, binary schema emission, proto mode, optional scalars, object API, naming, TypeScript, Rust, Swift, C#, Python, and 64-bit/vector features.

`ParserState` tracks cursor, line, token, current attribute, and doc comments. `CheckedError` enforces explicit error checking. `Parser` is the main public parser and schema holder. Public methods include `Parse`, `ParseJson`, `BytesConsumed`, `SetRootType`, `MarkGenerated`, `GetIncludedFilesRecursive`, `Serialize`, `Deserialize`, `DeserializeType`, `ConformTo`, `ParseFlexBuffer`, struct lookups, `UnqualifiedName`, `Error`, `SupportsOptionalScalars`, and `GetIncludedFiles`. Utility declarations include `GenTextFromTable`, `GenText`, `GenTextFile`, and gRPC generator entry points.

## Control Flow

Parsing is declared as a layered recursive descent pipeline. `Parse` or `ParseJson` starts a file/source, initializes parser state, and delegates to private helpers such as `Next`, `Expect`, `ParseNamespacing`, `ParseType`, `ParseField`, `ParseAnyValue`, `ParseTable`, `ParseVector`, `ParseArray`, `ParseNestedFlatbuffer`, `ParseMetaData`, `ParseHash`, `ParseDecl`, `ParseService`, proto-specific parsers, and include-aware `DoParse`. `CheckedError` forces each private parse step to be checked, reducing accidental ignored failures.

Schema definitions are accumulated in insertion-preserving `SymbolTable`s for types, structs, enums, and services. `Serialize` converts those definitions into binary reflection schema data in `builder_`; `Deserialize` performs the reverse from `reflection::Schema`. JSON parsing serializes values into `builder_`, while `ParseFlexBuffer` serializes dynamic JSON-like values into a supplied `flexbuffers::Builder`.

## State and Persistence Behavior

`Parser` owns namespaces, definition symbol tables, `FlatBufferBuilder builder_`, `flexbuffers::Builder flex_builder_`, root definition pointers, file identifiers/extensions, include maps, native include lists, known attribute registry, options, warning/error flags, advanced feature flags, current file name, source pointer, field stack, string cache, anonymous-name counter, and recursion depth counter. `SymbolTable` owns allocated definition pointers and deletes them in its destructor. `Parser` deletes namespace objects in its destructor. No direct filesystem persistence is implemented here, but private parser declarations and `Registry` users depend on loading schema files via utility functions in implementation files.

## Dependencies and Integration Points

This header depends on `base.h`, `flatbuffers.h`, `flexbuffers.h`, `hash.h`, and `reflection.h`, plus STL containers and callbacks. It is the integration hub between the schema parser, binary schema reflection (`reflection_generated.h`/`reflection.h`), text generation, FlexBuffers generation, proto compatibility parsing, and language/gRPC code generators. `registry.h` uses `Parser` and `IDLOptions` to convert arbitrary registered FlatBuffers between binary and text.

## Risks and Edge Cases

The parser has a large mutable state surface, so stale state across parses, namespace ownership, include resolution, and recursive parsing depth are critical. `FLATBUFFERS_MAX_PARSING_DEPTH` defaults to 64 to avoid stack overflow in nested schema/JSON/FlexBuffer parsing. Many feature gates (`SupportsAdvancedUnionFeatures`, arrays, optional scalars, default vectors/strings, 64-bit offsets, union underlying type) mean generator compatibility can fail if options and schema features diverge. `CheckedError` asserts if ignored, which is useful in debug builds but can be surprising when refactoring. `SymbolTable::Add` stores duplicate entries in `vec` even when `dict` already has a name and reports the duplicate via return value, so callers must enforce uniqueness.

## Test Signals

Strong signals are FlatBuffers parser tests for schemas, JSON parsing, includes, namespaces, unions, arrays, proto mode, attributes, optional scalars, 64-bit offsets, binary schema serialization/deserialization, and conformance checks. In this repo, build tests that compile vendored FlatBuffers headers and any syzkaller executor code using generated schemas catch API compatibility problems. Focused tests should verify parse-depth limits, unknown attributes, duplicate fields/enums, schema evolution failures, and `ParseFlexBuffer` output verification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/idl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/minireflect.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/minireflect.h

## Purpose

`minireflect.h` implements lightweight runtime reflection over generated `TypeTable` metadata. It supports iterating tables, structs, vectors, arrays, unions, scalar fields, enum names, and producing a compact JSON-like string without requiring a parsed schema or binary reflection schema.

## Important APIs, Types, and Functions

`IterationVisitor` is the callback interface. It has sequence callbacks, per-field callbacks, scalar callbacks, string and unknown callbacks, vector callbacks, and element callbacks. `InlineSize` computes inline storage size for an elementary type and optional type table. `LookupEnum` and `EnumName` translate enum values to names when mini-reflection names are available. `IterateObject`, `IterateValue`, and `IterateFlatBuffer` drive traversal. `ToStringVisitor` implements `IterationVisitor` and accumulates textual output. `FlatBufferToString` is the public formatting helper.

## Control Flow

`IterateFlatBuffer` obtains the root pointer with `GetRoot<uint8_t>` and calls `IterateObject`. `IterateObject` begins a sequence, walks `type_table->num_elems`, resolves each field's elementary type, repeat flag, type reference, name, and address. For tables it obtains field addresses through `Table::GetAddressOf`; for structs it computes offsets from the type table. Present fields call `visitor->Field`, then either iterate repeated values or call `IterateValue` once. Repeated table fields are FlatBuffers vectors; repeated struct fields are fixed arrays described by `array_sizes`.

`IterateValue` decodes scalar values with `ReadScalar`, resolves enum names where possible, dereferences string/table offsets, recursively visits nested tables/structs, and handles unions by reading the previous union type field or vector element from `prev_val`.

## State and Persistence Behavior

The traversal itself is stateless except for visitor-owned state. `ToStringVisitor` stores output string `s`, delimiter `d`, quote flag `q`, indentation string `in`, indentation level, and vector delimiter behavior. All reflected object pointers are non-owning views into an existing buffer.

## Dependencies and Integration Points

The header depends on `flatbuffers/flatbuffers.h` for `Table`, `Vector`, `String`, `TypeTable`, `ElementaryType`, `SequenceType`, and scalar helpers, and on `flatbuffers/util.h` for string escaping and numeric formatting. It integrates with generated code emitted with `--reflect-types` or `--reflect-names`; callers pass `FooTypeTable()` for the root type.

## Risks and Edge Cases

Mini-reflection trusts generated type tables and buffer shape. It does not replace verifier-based validation for untrusted input. Union handling depends on the preceding type field and uses `prev_val`, so malformed or unexpected ordering can produce `Unknown`. If type names were not generated, output falls back to numeric enum values and omits field names. `InlineSize` asserts for unsupported elementary types and depends on struct byte size stored in the type table. String output aims to resemble FlatBuffers JSON but is not a full schema-aware JSON generator.

## Test Signals

Tests should compare `FlatBufferToString` output for generated tables with scalar, enum, nested table, struct, vector, array, and union fields. Visitor tests should assert field/set indices and callbacks for absent fields. Buffer verifier tests remain necessary before mini-reflection is used on external data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/minireflect.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection.h

## Purpose

`reflection.h` provides higher-level helpers for binary schema reflection. It builds on generated reflection schema types to inspect, read, write, resize, copy, and verify arbitrary FlatBuffers using a `reflection::Schema` instead of generated C++ accessors.

## Important APIs, Types, and Functions

Getter helpers include `IsScalar`, `IsInteger`, `IsFloat`, `IsLong`, `GetTypeSize`, `GetTypeSizeInline`, `GetAnyRoot`, `GetAnySizePrefixedRoot`, `GetFieldDefaultI`, `GetFieldDefaultF`, `GetFieldI`, `GetFieldF`, `GetFieldS`, `GetFieldV`, `GetFieldAnyV`, `GetFieldT`, `GetFieldStruct`, `GetAnyValueI`, `GetAnyValueF`, `GetAnyValueS`, `GetAnyFieldI/F/S`, `GetAnyVectorElemI/F/S`, `GetAnyVectorElemPointer`, `GetAnyVectorElemAddressOf`, `GetAnyFieldAddressOf`, and `ForAllFields`.

Setter and mutation helpers include `SetField`, `SetAnyValueI/F/S`, `SetAnyFieldI/F/S`, `SetAnyVectorElemI/F/S`, `pointer_inside_vector`, `piv`, `UnionTypeFieldSuffix`, `GetUnionType`, `SetString`, `ResizeAnyVector`, `ResizeVector`, `AddFlatBuffer`, and `SetFieldT`. Copy and verification declarations are `CopyTable`, `Verify`, and `VerifySizePrefixed`.

## Control Flow

Read helpers use reflection metadata to map a `reflection::Field` to its vtable offset or struct offset, then dispatch by `reflection::BaseType`. Table reads first check whether a field is present and otherwise return the reflected default. Vector element helpers compute element addresses by multiplying index by the reflected inline element size. Pointer helpers decode FlatBuffers relative offsets for strings, tables, vectors, and generic vector elements.

Mutation helpers write directly into an existing mutable buffer. Scalar setters locate the field or vector element and dispatch through `SetAnyValue*`. `SetString` and `ResizeAnyVector` are declared for cases that require changing buffer size; they require the FlatBuffer to live inside a `std::vector<uint8_t>` so internal references can be adjusted after resizing. `AddFlatBuffer` appends newly built data to an existing vector and returns a pointer suitable for offset mutation.

## State and Persistence Behavior

Most helpers are stateless and operate on caller-owned tables, structs, vectors, and buffers. Resizing helpers mutate a `std::vector<uint8_t>` in place and can invalidate pointers, which is why `pointer_inside_vector` stores offsets relative to vector data rather than raw pointers. No global state is stored.

## Dependencies and Integration Points

The header includes `reflection_generated.h` and depends on FlatBuffers core runtime types (`Table`, `Struct`, `VectorOfAny`, `FlatBufferBuilder`, `Verifier`). It integrates with binary schemas emitted by `flatc --schema` or `Parser::Serialize` in `idl.h`. It is the schema-aware counterpart to generated accessors and mini-reflection.

## Risks and Edge Cases

Many APIs intentionally do little type checking and rely on correct reflection metadata. `GetAnyVectorElemPointer` warns that it performs no typechecking. `GetFieldStruct` cannot distinguish table versus struct without the schema in one overload. In-place mutation can corrupt buffers if the field type or offset is wrong, if a pointer is retained across vector resizing, or if a string/vector resize does not update all dependent offsets. `CopyTable` notes that DAGs are copied as trees, so shared table identities can be duplicated.

## Test Signals

Good coverage exercises reflection reads and writes for all scalar widths, strings, vectors, structs, tables, unions, defaults, optional fields, size-prefixed buffers, and 64-bit vector/offset fields. Verification tests should compare generated verifier results with reflection verifier results. Mutation tests should verify pointer invalidation behavior and round-trip copied tables.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection_generated.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection_generated.h

## Purpose

`reflection_generated.h` is the generated C++ binding for FlatBuffers' own binary schema format, produced from `reflection/reflection.fbs`. It defines the serialized schema tables used by `idl.h` and `reflection.h` to persist and inspect schema metadata.

## Important APIs, Types, and Functions

The header pins compatibility with a static assertion for FlatBuffers version `23.5.26`. It defines `reflection::BaseType` and name/value helpers, plus `reflection::AdvancedFeatures` flags. Generated table types are `Type`, `KeyValue`, `EnumVal`, `Enum`, `Field`, `Object`, `RPCCall`, `Service`, `SchemaFile`, and `Schema`, each with accessors, vtable offset constants, key comparison helpers where appropriate, and `Verify` methods.

For each table there is a builder type, a `Create*` function, and where string/vector convenience is useful a `Create*Direct` function. Root helpers include `GetSchema`, `GetSizePrefixedSchema`, `SchemaIdentifier`, `SchemaBufferHasIdentifier`, `SizePrefixedSchemaBufferHasIdentifier`, `VerifySchemaBuffer`, `VerifySizePrefixedSchemaBuffer`, `SchemaExtension`, `FinishSchemaBuffer`, and `FinishSizePrefixedSchemaBuffer`.

## Control Flow

Generated accessors read fields through `Table::GetField` or `GetPointer` with schema defaults. `Verify` methods call `VerifyTableStart`, verify required offsets, verify nested tables/vectors/strings, verify scalar alignment, and finish with `verifier.EndTable`. Builder types start a table in their constructors, expose `add_*` methods for each field, and `Finish` closes the table and marks required fields with `fbb_.Required`. Direct constructors create strings and sorted vectors of tables before delegating to normal create functions.

The root schema buffer is identified by file identifier `BFBS` and extension `bfbs`. `FinishSchemaBuffer` and `FinishSizePrefixedSchemaBuffer` write that identifier into the finished buffer; the corresponding verifier helpers require it.

## State and Persistence Behavior

All generated table objects are non-owning views into a FlatBuffer. Builder state is confined to a referenced `FlatBufferBuilder` and current table start offset. Persisted state is the binary schema content itself: objects, enums, file identifier, file extension, root table, services, advanced feature mask, and per-file include metadata.

## Dependencies and Integration Points

The header includes `flatbuffers/flatbuffers.h` and is included by `reflection.h`; `idl.h` serializes/deserializes parser definitions using these generated types. `Parser::Serialize` produces `reflection::Schema` buffers, and tools or runtime reflection consumers read them through this API.

## Risks and Edge Cases

Because this file is generated, manual edits would be overwritten and can break compatibility with `reflection.fbs`. The version assertion requires the included runtime to match the generator version; mismatches fail compilation. Required fields are enforced both by builder `Required` calls and verifier checks, but callers can still construct invalid buffers if they bypass generated builders. Sorted-vector helpers assume key comparison functions match the schema keys (`name`, `value`, or `filename`), so lookup behavior depends on using sorted creation when expected.

## Test Signals

Tests should verify binary schema buffers produced by the parser pass `VerifySchemaBuffer`, have identifier `BFBS`, and round-trip through `GetSchema`/`Parser::Deserialize`. Generated accessor tests should inspect objects, fields, enums, services, schema files, advanced features, optional/padding/offset64 field metadata, and size-prefixed variants.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/reflection_generated.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/registry.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/registry.h

## Purpose

`registry.h` defines `flatbuffers::Registry`, a convenience class for converting arbitrary FlatBuffers to text and text back to binary by looking up schemas from file identifiers. It is a small runtime schema registry built on top of the IDL parser and text generator.

## Important APIs, Types, and Functions

Public methods are `Register`, `FlatBufferToText`, `TextToFlatBuffer`, `SetOptions`, `AddIncludeDirectory`, and `GetLastError`. The private `LoadSchema` helper resolves a file identifier to a registered schema path, loads the schema file, configures a `Parser`, and parses the schema. Private state includes `lasterror_`, `opts_`, `include_paths_`, and `schemas_`, where each `Schema` stores a schema path.

## Control Flow

Callers register possible schemas by file identifier. `FlatBufferToText` first checks that the buffer is long enough to contain a root offset plus file identifier, extracts the identifier bytes, loads the matching schema into a local `Parser`, then calls `GenText`. `TextToFlatBuffer` loads a schema by caller-supplied identifier, parses the text through `Parser::Parse`, and returns the detached builder buffer. `LoadSchema` handles missing identifier, file loading failure, parse failure, parser option propagation, and include path forwarding.

## State and Persistence Behavior

The registry stores schema path mappings and include directories, but it does not cache loaded schema text or parsed parser instances. Each conversion creates and discards a new `Parser`. `lasterror_` stores the most recent human-readable failure. Returned `DetachedBuffer` owns generated binary output; parse failure returns an empty `DetachedBuffer`.

## Dependencies and Integration Points

The header includes `base.h` and `idl.h`. It uses `LoadFile`, `Parser`, `IDLOptions`, `GenText`, `DetachedBuffer`, and FlatBuffers file identifier constants. It is useful for tools that receive buffers from multiple schemas and want to defer schema selection until runtime.

## Risks and Edge Cases

Identifiers are raw four-byte FlatBuffers identifiers and may not be printable; error messages deliberately avoid echoing unknown identifiers. `include_paths_` stores raw `const char *` pointers, so callers must ensure pointed strings outlive the registry. Because schemas are reparsed on every conversion, performance depends on schema size and filesystem access. There is a TODO to cache schema files or parsed schemas. Buffer-to-text fails early on truncated buffers shorter than `sizeof(uoffset_t) + kFileIdentifierLength`.

## Test Signals

Tests should register multiple schemas, convert known binary buffers to text, parse text back to binary, validate include directory behavior, and assert errors for truncated buffers, unknown identifiers, missing schema files, schema parse errors, and text parse errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/registry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/stl_emulation.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/stl_emulation.h

## Purpose

`stl_emulation.h` provides FlatBuffers compatibility aliases and fallbacks for standard-library features across older and newer C++ modes. It wraps type traits, `unique_ptr`, optional scalars, and span-like views so FlatBuffers generated code can use a stable `flatbuffers::` API even when `std::optional` or `std::span` are unavailable.

## Important APIs, Types, and Functions

Feature macros include `FLATBUFFERS_USE_STD_OPTIONAL`, `FLATBUFFERS_USE_STD_SPAN`, and `FLATBUFFERS_SPAN_MINIMAL`. Type-trait wrappers include `numeric_limits`, `is_scalar`, `is_same`, `is_floating_point`, `is_unsigned`, `is_enum`, `make_unsigned`, `conditional`, `integral_constant`, `bool_constant`, `true_type`, and `false_type`. `unique_ptr` is either an alias or a wrapper around `std::unique_ptr`.

For optional values, the header either aliases `std::optional`, `std::nullopt_t`, and `std::nullopt`, or defines a scalar-only `Optional<T>` with `nullopt_t`, constructors, assignment, `reset`, `swap`, bool conversion, `has_value`, dereference, `value`, and `value_or`. Equality operators cover optional/nullopt/value comparisons. For span, it either aliases `std::span` or defines `dynamic_extent`, `internal::SpanIterator`, `span<T, Extent>`, and `make_span` overloads.

## Control Flow

Preprocessor checks select the standard implementation when language and library support are detected. Otherwise, wrappers or fallback classes are compiled. The fallback `Optional<T>` stores a `T value_` and `bool has_value_`. The fallback `span` stores a pointer and count, enforces fixed extents by nulling/counting zero on incompatible construction, and optionally provides iterators and array/std::array constructors when not in minimal mode.

## State and Persistence Behavior

All state is value-local: optional values contain a scalar and presence flag; spans are non-owning views over external memory. `nullopt` is implemented as a static constant or constexpr holder depending on compiler support. No dynamic allocation or persistence is performed by this header itself.

## Dependencies and Integration Points

The header includes `flatbuffers/base.h` and standard headers for strings, vectors, memory, limits, type traits, optional/span/array when available. It is used broadly by FlatBuffers runtime and generated code to represent optional scalar fields and non-owning byte or element ranges.

## Risks and Edge Cases

The fallback `Optional<T>` is intentionally scalar-only and asserts at compile time for non-scalar types. Its equality for two empty optionals returns false in this version, unlike `std::optional`, so generic code should be careful when relying on optional-to-optional equality semantics. The fallback `span` is a limited and naive partial implementation; fixed-extent mismatches produce an empty span rather than throwing, and bounds checks are not performed by `operator[]`. Some overloads are excluded in minimal mode for old compiler support.

## Test Signals

Tests should compile generated code under C++11, C++17, and C++20 configurations, exercising both fallback and standard optional/span paths. Runtime checks should cover optional construction/reset/value_or, span construction from pointer arrays and `std::array`, fixed extent mismatch behavior, and generated optional scalar accessors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/stl_emulation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/string.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/string.h

## Purpose

`string.h` defines the FlatBuffers runtime `String` view type and null-safe string helper functions. A FlatBuffers string is stored as a `Vector<char>` with a trailing NUL in the buffer, and this header exposes C-string, `std::string`, and optional string-view access.

## Important APIs, Types, and Functions

`struct String : public Vector<char>` provides `c_str`, `str`, optional `string_view`, and `operator<` based on `StringLessThan`. Free helpers are `GetString`, `GetCstring`, and optional `GetStringView`, each returning an empty value when passed `nullptr`.

## Control Flow

`c_str` returns `Data()` reinterpreted as `const char *`. `str` constructs a `std::string` from `c_str()` and `size()`, preserving embedded NUL bytes because the length is explicit. `operator<` delegates to FlatBuffers string comparison over raw data and size. The helper functions check for null before calling the corresponding member.

## State and Persistence Behavior

`String` is a non-owning view over serialized FlatBuffers memory inherited from `Vector<char>`. It does not allocate except when `str()` constructs a new `std::string`. `GetCstring` returns a pointer into the buffer or a static empty string literal.

## Dependencies and Integration Points

The header includes `base.h` and `vector.h`. Generated accessors for FlatBuffers string fields return `const String *` and often rely on these helpers for conversion to host-language strings.

## Risks and Edge Cases

`c_str` assumes the underlying FlatBuffers string has the standard trailing NUL; corrupted buffers should be verified before use. `GetCstring(nullptr)` returns an empty literal that must not be mutated. `string_view` support depends on `FLATBUFFERS_HAS_STRING_VIEW`. Ordering depends on `StringLessThan`, not locale-aware comparison.

## Test Signals

Tests should cover null helpers, embedded NUL preservation in `str`, string-view length, comparison ordering, and verifier rejection of malformed strings before `c_str` is used.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/struct.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/struct.h

## Purpose

`struct.h` defines the FlatBuffers runtime `Struct` view type. FlatBuffers structs are fixed-layout inline records without vtables, optional fields, or forward/backward-compatible field evolution, and this class exposes low-level reads from that inline data.

## Important APIs, Types, and Functions

`class Struct` provides `GetField<T>(uoffset_t)`, `GetStruct<T>(uoffset_t)`, and const/mutable `GetAddressOf(uoffset_t)`. Constructors, copy constructor, and assignment operator are private, because instances are obtained only by reinterpret-casting existing buffer memory.

## Control Flow

`GetField` reads a scalar at a fixed byte offset using `ReadScalar<T>`. `GetStruct` returns a nested struct pointer/reference type by reinterpret-casting the address at the offset. `GetAddressOf` returns a raw pointer to the requested byte offset for reflection or mutation helpers.

## State and Persistence Behavior

`Struct` is a non-owning view over serialized FlatBuffers memory. It contains a one-byte placeholder array to model flexible inline storage but is never constructed as a normal C++ object.

## Dependencies and Integration Points

The header includes `flatbuffers/base.h` for scalar types and endian-safe reads. It is used by generated accessors, `table.h` struct-field access, and reflection helpers for schema-driven struct access and mutation.

## Risks and Edge Cases

There is no bounds checking or vtable safety in `Struct`; offsets must come from generated code or trusted reflection metadata, and buffers should be verified before access. Struct schema evolution is inherently limited because every field is always present at fixed offsets. Misaligned or wrong-type reads can produce undefined behavior at the logical level even though scalar I/O is endian-safe.

## Test Signals

Tests should verify generated struct accessors, nested struct reads, reflection `GetFieldStruct`, and verifier coverage for struct alignment and inline size. Negative tests should use malformed buffers with invalid parent table offsets rather than constructing `Struct` directly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/table.h -->
# sources/test-tools/syzkaller/executor/_include/flatbuffers/table.h

## Purpose

`table.h` defines the FlatBuffers runtime `Table` view type. Tables are variable-layout objects with vtables, optional fields, defaults, pointer fields, struct fields, mutation helpers, and field verification helpers.

## Important APIs, Types, and Functions

`Table` exposes `GetVTable`, `GetOptionalFieldOffset`, `GetField`, `GetPointer`, `GetPointer64`, `GetStruct`, `GetOptional`, `SetField`, `SetPointer`, `GetAddressOf`, `CheckField`, `VerifyTableStart`, `VerifyField`, `VerifyFieldRequired`, `VerifyOffset`, `VerifyOffsetRequired`, `VerifyOffset64`, and `VerifyOffset64Required`. There is a specialization of `GetOptional<uint8_t, bool>` to avoid bool conversion warnings.

## Control Flow

`GetVTable` subtracts the signed vtable offset stored at the table start. `GetOptionalFieldOffset` reads the vtable size and returns a field offset only when the requested vtable slot exists; otherwise it reports field absence. Scalar getters return either the serialized scalar or the caller-supplied default. Pointer getters add the field offset, read a relative offset, and return the target pointer. Struct getters return the inline address. Setters update existing fields in place and only accept absent fields when setting the exact default for the default-aware scalar overload.

Verification starts with `VerifyTableStart`, then generated code calls `VerifyField`/`VerifyOffset` for optional fields or required variants for required fields. Offset64 helpers use `uoffset64_t` for 64-bit addressing fields.

## State and Persistence Behavior

`Table` is a non-owning mutable or immutable view over existing serialized memory. In-place setters mutate the underlying buffer but cannot add fields that are absent from the vtable. The class itself has private constructors and a one-byte placeholder array, so it is obtained only from FlatBuffers root/pointer accessors.

## Dependencies and Integration Points

The header includes `base.h` and `verifier.h`. It is central to generated table accessors, generated verifiers, `reflection_generated.h` table classes, and schema-driven reflection helpers in `reflection.h`.

## Risks and Edge Cases

Reading a corrupt table without verifier checks can produce invalid pointers or out-of-bounds reads. `GetPointer` and `SetPointer` assume the field uses the expected offset width; using 32-bit helpers on 64-bit offset fields is wrong. In-place mutation cannot materialize absent optional fields except by accepting an unchanged default. `GetAddressOf` returns null for absent fields, and callers must check before raw mutation.

## Test Signals

Generated accessor tests for optional/default fields, required fields, strings/vectors/tables, structs, 64-bit offsets, and mutation APIs exercise this header. Verifier tests should include truncated vtables, fields outside object bounds, missing required fields, bad offsets, and offset64-specific cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/executor/_include/flatbuffers/table.h -->
