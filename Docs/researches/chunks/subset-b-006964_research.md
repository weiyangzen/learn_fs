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
