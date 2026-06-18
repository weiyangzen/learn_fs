# Research: sources/distributed-fs/ceph/src/rgw/driver/posix/zpp_bits.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006963`: lines 1-5628, `Docs/researches/chunks/subset-b-006963_research.md`
- `subset-b-006964`: lines 5629-5665, `Docs/researches/chunks/subset-b-006964_research.md`

## Chunk Research

### subset-b-006963: lines 1-5628

# sources/distributed-fs/ceph/src/rgw/driver/posix/zpp_bits.h lines 1-5628

## Scope

This chunk covers almost all of `zpp_bits.h` through the `u8string_view2b` alias. The file is a single-header C++20 serialization library vendored under the Ceph RGW POSIX driver tree. The covered range defines the public `zpp::bits` API, compile-time reflection helpers, binary input/output archives, varint support, RPC binding/client/server helpers, protobuf-like protocol support, constexpr byte conversion and hashing utilities, user-defined literals, and many sized string/vector/span aliases.

The chunk stops before the final UTF-8/UTF-16/UTF-32 string view aliases and closing include guard, so any merged per-file report should account for the remaining aliases after line 5628.

## Purpose

The header provides generic binary serialization/deserialization with a small error type, no external runtime dependency, and heavy use of C++20 concepts and `constexpr` machinery. RGW POSIX code can include it to encode/decode in-memory objects, containers, variants, optional values, pointers, and custom protocol-wrapped structs into byte buffers.

The same primitives are reused to build:

- normal little/native/swapped-endian binary archives;
- varint and zig-zag integer encodings;
- message-size-prefixed protocol dispatch;
- RPC request/response helpers keyed by serialized IDs;
- protobuf-compatible field/tag encoding for aggregate structs;
- compile-time conversion, SHA-1/SHA-256 hashing, and string literal utilities.

There is no direct POSIX filesystem code in this chunk. Its role in the source tree is as a reusable serialization substrate for the RGW POSIX driver code that surrounds it.

## Important APIs, Types, and Functions

### Core metadata and errors

- `kind` distinguishes input and output archive directions.
- `members<N>` and `protocol<Protocol, Members>` are type-level serialization descriptors. They let a type opt into aggregate-member serialization or a custom protocol implementation, optionally with an explicit member count.
- `serialization_id<Id>`, `serialize_id<Id, MaxSize>()`, `id<Id, MaxSize>`, and `id_v<Id, MaxSize>` turn compile-time values into stable serialized IDs, often used by variants and RPC bindings.
- `errc` wraps `std::errc`, supports `success()`/`failure()` checks, `or_throw()`, and optional coroutine interop if `zpp_throwing.h` is present.
- `value_or_errc<T>` is a small result container used by RPC and `apply()`. It can store either an `errc` or a return value, including references and void-like returns, and mirrors the same throwing/coroutine paths.

### Reflection and traits

The private `access` struct is the central friend-like utility:

- construction/destruction helpers (`make`, `placement_new`, `make_unique`, `destruct`);
- aggregate member counting up to `max_visit_members == 50`;
- `visit_members()` and `visit_members_types()` based on structured bindings;
- `has_serialize()`, `has_explicit_serialize()`, `has_protocol()`, and `get_protocol()`;
- byte-serializability and self-reference detection.

`traits` and `concepts` provide most dispatch predicates. Important ones include `container`, `associative_container`, `tuple`, `variant`, `optional`, `owning_pointer`, `bitset`, `by_protocol`, `byte_serializable`, `endian_independent_byte_serializable`, `serialize_as_bytes`, and `self_referencing`.

The `traits::variant` helper assigns each variant alternative a unique ID. IDs can come from a nested `serialize_id`, an ADL `serialize_id()`, or fallback to the alternative index as `std::byte`. Static assertions ensure all IDs are unique and of one common ID type.

### Byte views, sizing, and options

- `string_literal<CharType, Size>` stores compile-time strings without the trailing null in `end()`.
- `bytes<Item>` is a trivially-copyable span wrapper for raw byte transfer; `as_bytes()` wraps a single object.
- `sized_item`, `sized_t`, `unsized_t`, `sized_item_ref`, `sized<SizeType>()`, and `unsized()` override the archive's default size-prefix type for one object or type alias.
- Options include `append`, `reserve`, `resize`, `alloc_limit<N>`, `enlarger<M, D>`, `exact_enlarger`, endian selectors, `no_fit_size`, `no_enlarge_overflow`, `enlarge_overflow`, `no_size`, fixed-size-prefix options (`size1b`, `size2b`, `size4b`, `size8b`, `size_native`), and `size_varint`.

### Varints

`varint<Type, Encoding>` stores a value with either normal or zig-zag encoding. Aliases include `vint32_t`, `vint64_t`, `vuint32_t`, `vuint64_t`, `vsint32_t`, `vsint64_t`, and `vsize_t`.

Serialization writes 7-bit continuation bytes into archive remaining space, using `varint_max_size`, `varint_size()`, and `decode_varint()`. Decoding has fast paths for single-byte values and unrolled paths for full-size buffers, with `std::errc::result_out_of_range` for incomplete buffers and `std::errc::value_too_large` for overlong encodings.

### Binary archives

`basic_out<ByteView, Options...>` and `out<ByteView, Options...>` serialize objects into byte views. They expose:

- `operator()(items...)` and internal `serialize_many()` / `serialize_one()`;
- `data()`, `remaining_data()`, `processed_data()`, `position()`, and `reset()`;
- optional resizing via `enlarge_for()` for resizable byte containers;
- endian-aware fundamental writes through reversed byte order when `endian::swapped` is selected;
- optimized byte-copy paths for byte-serializable arrays/containers;
- structured handling for tuples, optionals, variants, owning pointers, bitsets, associative containers, and protocol-backed types.

`in<ByteView, Options...>` mirrors the output archive for deserialization. It reads fundamentals, raw bytes, arrays, containers, associative containers, tuples, optionals, variants, owning pointers, bitsets, and protocol-backed objects while advancing `m_position`. It can resize destination containers when a size prefix is present, can bind const byte spans/string views directly to remaining archive data, and enforces `alloc_limit` before resizing.

Convenience constructors and helpers include `input()`, `output()`, `in_out()`, `data_in_out()`, `data_in()`, and `data_out()`.

### Compile-time bytes and IDs

- `to_bytes_one<Object, MaxSize>()`, `to_bytes<Objects...>()`, `join<Data...>()`, `slice<Left, Right>()`, and `from_bytes<Data, Type...>()` support constexpr object serialization/deserialization.
- `known_id<Id>(variant)` and `known_id(dynamic_id, variant)` wrap variants when the tag is already known externally, avoiding or supplying normal variant ID serialization.

### RPC helpers

`function_traits` extracts parameter and return tuple types from function pointers and member function pointers, including `noexcept` and const overloads.

`apply()` reads function parameters from an input archive and invokes a free function, functor, or member function. Void-returning functions produce `errc`; value-returning functions produce `value_or_errc<Return>`.

`bind<Function, Id, MaxSize>` and `bind_opaque<Function, Id, MaxSize>` describe RPC endpoints. `rpc<Bindings...>` validates unique binding IDs through a synthetic variant and exposes:

- `rpc_impl::client<In, Out>` for writing request IDs and parameters and reading typed responses;
- `rpc_impl::server<In, Out, Context>` for reading IDs, dispatching to matching bindings, and serializing responses;
- `client_server()` helpers that pair both sides on shared archives.

Opaque bindings receive archives or remaining input bytes directly and can control their own request/response body handling.

### Protobuf protocol layer

`pb<Options...>` implements a protobuf-like protocol adapter usable via `using serialize = protocol<pb{}>` or `pb_members<N>`.

Important support types:

- `pb_reserved` is a placeholder for reserved fields.
- `pb_map<From, To>` remaps aggregate member index `From` to protobuf field number `To`.
- `pb_field<Type, FieldNumber>` wraps fundamental or class fields with explicit field numbers.
- `pb_value()` unwraps `pb_field` values.
- `pb_protocol` and `pb_members` are ready-made protocol aliases.

The protocol computes field numbers from explicit `pb_field_number`, mapping options, or aggregate index plus one. It checks that field numbers are unique and that each field type is protobuf-serializable. Wire types are `varint`, `fixed_64`, `length_delimited`, and `fixed_32`.

Output serialization writes protobuf tags and values, using varints for booleans/enums/varint wrappers, fixed-width little-endian values for integrals/floats, length-delimited fields for nested messages and packed primitive containers, repeated tags for non-primitive repeated elements, and key/value nested messages for associative containers.

Input deserialization creates a limited little-endian, varint-sized archive view over the remaining message bytes, clears repeated containers, loops over tags until the message view is exhausted, and dispatches matching field numbers to aggregate members. Unknown nonzero fields are ignored without skipping payload bytes in the visible code path, which is an important compatibility risk noted below.

### Big-endian numbers, hashes, literals, and aliases

`numbers::big_endian<Type>` stores numeric values in big-endian byte order and implements shifts, addition, bitwise operators, comparison, and `members<1>` serialization. It is used by constexpr SHA implementations.

`sha1<Object, Digest>()` and `sha256<Object, Digest>()` serialize an object at compile time, pad the message, process 512-bit chunks with big-endian words, and deserialize the resulting digest into the requested digest type.

String literal operators provide:

- `"_s"` for `string_literal`;
- `"_b"` for serialized bytes;
- `"_decode_hex"` for compile-time hex decoding with validation;
- `"_sha1"` / `"_sha256"` for digest arrays;
- `"_sha1_int"` / `"_sha256_int"` for integer-sized serialized digest IDs.

The covered alias block defines sized and unsized variants for `std::vector`, `std::span`, `std::string`, `std::string_view`, `std::wstring`, `std::wstring_view`, `std::u8string`, and part of `std::u8string_view`.

## Control Flow

Binary output flows through `out::operator()` into `basic_out::serialize_many()`, then compile-time overload selection in `serialize_one()`. Each item either uses explicit `type::serialize()` / ADL `serialize()`, direct fundamental byte copy, raw `bytes`, aggregate member visitation, or a specialized container/tuple/optional/variant/pointer/bitset/protocol branch. Errors stop the sequence immediately and propagate as `errc`.

Binary input follows the same `serialize_many()` structure but mutates destination objects. Size-prefixed containers first decode a `SizeType`; resizable containers are resized, byte views may be rebound to input memory, associative containers are cleared and rebuilt from temporary placement-new objects, and non-default-constructible optional/variant elements are constructed in local aligned storage before being moved into place.

Protocol-backed output reserves a size prefix when the default size type is not `void`, serializes the protocol body, computes message length, and patches the prefix. Varint size prefixes are special: the code initially reserves one byte, then shifts the message body forward with `memmove` if the final varint length needs more bytes.

RPC server flow is: read or receive request ID, recursively compare it with binding IDs, decode parameters for non-opaque bindings via `apply()`, call the target function or member function, and serialize a return value when present. If `zpp_throwing.h` is available and bindings return awaitables, coroutine-specific dispatch paths are compiled.

Protobuf output flow is: visit aggregate members in order, compute each field tag, skip empty fields/containers, write scalar values or length-delimited packed payloads, and serialize nested protocol objects through normal archive protocol handling. Protobuf input flow is: create a bounded inner archive, clear repeated members, read tag varints, locate a matching member by field number through recursive template dispatch, and decode that member based on wire/category.

## State and Persistence Behavior

The header itself defines no global mutable state, persistent storage, file I/O, locks, or threads. All runtime state is local to archive instances:

- `m_data` references or owns the caller-provided byte view/container depending on template deduction;
- `m_position` tracks consumed or produced bytes;
- resizable output archives may mutate backing container size and capacity;
- input archives may mutate destination objects, clear and repopulate containers, reset owning pointers, assign optional/variant alternatives, and bind span/string-view-like objects to input memory.

Serialization format state is embedded in options selected at archive construction or type wrappers: endian behavior, size-prefix type, allocation limit, enlarger policy, no-size mode, protocol selection, variant ID scheme, and protobuf field mapping.

The persistence contract is therefore the byte format generated by these templates. Any source type layout change, member-count change, field-number remap, endian option change, size-prefix change, or variant ID change changes the stored/wire representation.

## Dependencies and Integration Points

The header depends only on C++ standard library headers plus optional local `zpp_throwing.h`. It requires C++20 features: concepts, `std::span`, `std::endian`, `std::bit_cast` or compiler builtin fallback, `std::is_constant_evaluated`, class NTTPs for `string_literal`, and extensive constexpr evaluation.

Integration points for callers:

- add a nested `using serialize = members<N>` or `protocol<pb{}>` to a type;
- provide ADL `serialize(archive, object)` or `try_serialize(object)`;
- provide nested/ADL `serialize_id` for variant alternatives;
- instantiate `zpp::bits::in` / `out` over vectors, spans, strings, arrays, or custom byte views;
- use `pb_field` / `pb_map` for protobuf field numbering;
- use `bind` / `bind_opaque` and `rpc` for request dispatch.

Within the Ceph tree, the path under `src/rgw/driver/posix` indicates this is expected to integrate with RGW POSIX driver code rather than Ceph's broader messenger or object-store encoders. Because the header is standalone and namespace-scoped, integration is mostly through includes and template instantiation in nearby POSIX driver source files.

## Risks and Edge Cases

- Aggregate reflection is limited to 50 members. Types with more members or ambiguous aggregate construction fail at compile time unless they provide explicit serialization metadata.
- The default aggregate auto-detection mode is controlled by `ZPP_BITS_AUTODETECT_MEMBERS_MODE`; changing it can alter compile-time detection and serialized layouts.
- Raw byte serialization is enabled only for trivially copyable types passing strict byte-serializability checks, but layout padding and native representation remain ABI-sensitive when not using explicit member serialization.
- Endian handling is option-driven. Native binary archives without `endian::swapped` can produce platform-dependent data for multi-byte fundamentals.
- Output container growth uses arithmetic on sizes and an `enlarger` multiplier/divisor. Overflow checks can be disabled with `no_enlarge_overflow`, making caller limits important.
- Input size prefixes can cause large allocations unless `alloc_limit` is set. Several branches check this limit before resizing, but callers should still bound untrusted data.
- Varint decode rejects truncated and overlarge values, but template paths are dense and duplicated under `ZPP_BITS_INLINE_DECODE_VARINT`, so regression tests need both modes if that macro is used.
- Non-null owning pointers are required on output; null pointer serialization returns `invalid_argument`. `optional_ptr` is provided when nullability must be serialized.
- Variant deserialization returns `bad_message` only when the computed index is greater than the alternative count. Because `std::variant_size` is a count, an index equal to the count appears suspicious and should be tested carefully.
- Protobuf unknown-field handling appears incomplete in this visible chunk: when no member matches a nonzero field number, `deserialize_field()` returns success without consuming the unknown field payload. For unknown fields with payload bytes, the outer loop may then interpret payload bytes as new tags, causing decode errors or misalignment. This is a compatibility risk for forward-compatible protobuf messages.
- Protobuf deserialization does not visibly validate wire type for every scalar branch before delegating to archive reads. Mismatched wire types may decode incorrectly instead of returning a protocol error.
- Several constexpr helpers call `.or_throw()`. With exceptions disabled, failures abort.
- `value_or_errc` manually manages a union and uses `std::memcpy` for the error arm in move construction; nontrivial evolution of its stored types would need care.

## Test Signals

Useful tests for this chunk should cover both compile-time and runtime behavior:

- Round-trip primitive, enum, aggregate, tuple, optional, variant, owning pointer, bitset, array, vector, string, span, map, and set serialization through `out`/`in`.
- Fixed buffer overflow and resizable buffer growth, including `no_fit_size`, `reserve`, `resize`, `append`, `exact_enlarger`, overflow handling, and `alloc_limit`.
- Endian options on known byte sequences for 16/32/64-bit integers and floats.
- Varint normal and zig-zag encodings for boundary values, maximum-size values, truncated buffers, and overlong encodings.
- `sized<T>`, `unsized<T>`, `size1b`/`size2b`/`size4b`/`size8b`/`size_varint`, and native-size aliases on containers and strings.
- Aggregate member-count detection for empty, fixed-size array, tuple-like, explicit `members<N>`, explicit `protocol<...>`, and unsupported/member-count-too-large types.
- Variant ID uniqueness failures, explicit `serialize_id`, `known_id()` serialization, and bad ID deserialization.
- `pb` encoding compared with protobuf wire-format golden bytes for scalars, enums, nested messages, repeated packed primitives, repeated nested messages, maps, explicit `pb_field`, and `pb_map`.
- Protobuf unknown-field and mismatched-wire-type inputs, specifically to confirm or expose the no-skip behavior described above.
- RPC client/server request, request-body-only, void return, value return, `errc`, `value_or_errc`, member function context, and opaque binding paths.
- Compile-time `to_bytes`, `from_bytes`, `"_decode_hex"`, `"_sha1"`, `"_sha256"`, and integer digest literal tests against known vectors.
- Builds with and without `zpp_throwing.h`, with exceptions disabled, with GCC/Clang, and with `ZPP_BITS_INLINE_DECODE_VARINT` toggled.

### subset-b-006964: lines 5629-5665

# sources/distributed-fs/ceph/src/rgw/driver/posix/zpp_bits.h lines 5629-5665

## Scope And Purpose

This chunk is the final Unicode string alias block in the vendored `zpp::bits` serialization header used by the RGW POSIX driver. It exports ready-made `sized_t` wrappers for UTF-8, UTF-16, and UTF-32 string and string-view types, then closes the `zpp::bits` namespace and the include guard.

The aliases are convenience APIs rather than new algorithms. They let callers select the exact serialized length-prefix type for UTF containers without spelling out `sized_t<std::u8string_view, std::uint32_t>` or similar templates at each use site. This matters because `zpp::bits` encodes containers by optionally writing a size field before the element bytes or element sequence; choosing the alias fixes that wire-format size width.

## Important APIs And Types

- `u8string_view4b` and `u8string_view8b` wrap `std::u8string_view` with `std::uint32_t` or `std::uint64_t` length prefixes.
- `static_u8string_view` wraps `std::u8string_view` with `SizeType = void`, meaning no length prefix is emitted or consumed by the wrapper itself.
- `native_u8string_view` uses `std::u8string_view::size_type` as the serialized size type.
- `u16string1b`, `u16string2b`, `u16string4b`, and `u16string8b` wrap owning `std::u16string` with 1-, 2-, 4-, and 8-byte length prefixes.
- `static_u16string` and `native_u16string` provide no-prefix and native-size variants for `std::u16string`.
- `u16string_view1b`, `u16string_view2b`, `u16string_view4b`, and `u16string_view8b` do the same for `std::u16string_view`.
- `static_u16string_view` and `native_u16string_view` provide no-prefix and native-size variants for `std::u16string_view`.
- `u32string1b`, `u32string2b`, `u32string4b`, and `u32string8b` wrap `std::u32string`.
- `static_u32string` and `native_u32string` provide no-prefix and native-size variants for `std::u32string`.
- `u32string_view1b`, `u32string_view2b`, `u32string_view4b`, and `u32string_view8b` wrap `std::u32string_view`.
- `static_u32string_view` and `native_u32string_view` provide no-prefix and native-size variants for `std::u32string_view`.

All aliases depend on the earlier `sized_t<Type, SizeType>` alias, which maps to `sized_item<Type, SizeType>`. `unsized_t<Type>` is a `sized_t<Type, void>`. `sized_item` publicly inherits from the wrapped string or view type, forwards constructors and assignment, and provides a static `serialize()` hook that calls `archive.template serialize_one<SizeType>()` on the base object.

## Control Flow

When an alias object is serialized, overload resolution finds the `sized_item` serialization hook. For output archives, the hook casts the object to `const Type&` and calls `serialize_one<SizeType>()`. For input archives, it casts to mutable `Type&` and calls the same archive entry point.

The container serializer then decides whether to write or read a size field. For output, if `SizeType` is not `void` and the container shape is resizable or view-like, the archive writes `static_cast<SizeType>(container.size())` before serializing the contents. If `SizeType` is `void`, no length field is written and the caller must provide an externally bounded container or view contract.

For input, a non-void `SizeType` is read first. Owning strings can be resized to that length before data is read. View aliases are rebound to spans of the archive buffer when the implementation can safely point at existing input bytes, or are range-checked against the supplied destination view. For `SizeType = void`, dynamic byte-like views may consume the remaining archive bytes; other fixed or pre-sized containers are read according to their existing extent.

The actual element transfer may be byte-wise or element-wise depending on `concepts::serialize_as_bytes`. For UTF-16 and UTF-32 strings, endian-aware archive options and the byte-serializability traits are important because multi-byte code units are only portable when the archive mode handles endian conversion consistently.

## State And Persistence Behavior

This chunk declares only type aliases and does not allocate memory or persist state by itself. Its persistence impact is the wire format chosen by the alias:

- `1b`, `2b`, `4b`, and `8b` aliases persist a length prefix of the named integer width before the string payload.
- `static_*` aliases persist only payload bytes or elements under an external length contract.
- `native_*` aliases persist a platform `size_type`, which can vary in width across ABIs and should be avoided for stable cross-platform data.

On decode, owning `std::u16string` and `std::u32string` aliases may allocate according to the encoded length, subject to the archive allocation limit option. View aliases do not own decoded bytes; they point into input storage or an existing caller-provided buffer, so the backing archive data must outlive the view.

## Dependencies And Integration Points

These aliases depend on C++20 Unicode string types from the standard library: `std::u8string`, `std::u8string_view`, `std::u16string`, `std::u16string_view`, `std::u32string`, and `std::u32string_view`. The header includes the needed standard facilities earlier and places the aliases in `namespace zpp::bits`.

The aliases integrate with:

- `sized_item` and `sized_item_ref`, which are the local wrappers for overriding archive size-prefix behavior.
- `basic_out` and `in` archive classes, whose `default_size_type` can also be changed globally with options such as `size1b`, `size2b`, `size4b`, `size8b`, `size_native`, or `no_size`.
- Container detection through `concepts::container`, since the wrapped standard string and string-view types expose `value_type`, `size()`, `begin()`, and `end()`.
- Byte serialization and endian handling through `concepts::serialize_as_bytes` and the archive endian options.
- RGW POSIX driver code that includes this vendored header for compact binary serialization, even though this specific alias block currently has no separate RGW caller references outside the header.

## Risks And Edge Cases

- Narrow size aliases can truncate silently on output because the container size is cast to `SizeType`; a string longer than 255, 65535, or 2^32-1 code units can produce an invalid or shortened length prefix if callers choose too small an alias.
- `static_*` aliases require an external framing contract. Decoding unsized dynamic views can consume all remaining input bytes, which is correct only when the field is the final payload or otherwise externally bounded.
- `native_*` aliases are not a stable interchange format across 32-bit and 64-bit builds.
- String-view aliases carry lifetime risk after input: decoded views may reference the archive buffer, so moving or destroying the buffer invalidates them.
- UTF-16 and UTF-32 payloads are sequences of code units, not validated Unicode scalar values. Serialization preserves bytes/code units and does not normalize, validate surrogate pairs, or transcode.
- Endianness matters for `char16_t` and `char32_t` content. Cross-machine persistence should use an endian-aware archive mode or a byte-oriented UTF-8 format.
- Allocation limits are the main guard against malicious length prefixes for owning strings; tests should exercise oversized encoded lengths.

## Test Signals

Useful tests for this chunk should verify wire-format compatibility rather than independent logic:

- Round-trip each `u8`, `u16`, and `u32` owning string alias with representative ASCII, non-ASCII, empty, and embedded-null data.
- Assert exact encoded size-prefix widths for `1b`, `2b`, `4b`, and `8b` aliases.
- Check overflow behavior when a container length exceeds the selected prefix width, especially for `1b` and `2b`.
- Decode into `*_string_view*` aliases and assert the view data matches while also documenting the required backing-buffer lifetime.
- Exercise `static_*` aliases only inside an externally framed message or as the final field, and test that later fields are not accidentally consumed.
- Run endian-aware cross-archive tests for UTF-16 and UTF-32 data on swapped-endian mode to catch code-unit byte-order regressions.
- Include allocation-limit failure cases for owning UTF-16 and UTF-32 strings with large encoded length prefixes.
