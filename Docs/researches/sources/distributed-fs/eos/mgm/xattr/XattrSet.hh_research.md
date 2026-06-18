## sources/distributed-fs/eos/mgm/xattr/XattrSet.hh

Purpose: Provides a small serializer/deserializer for storing a set of strings as a single space-separated extended attribute value.

Important APIs and types: `XattrSet::values` is the backing `std::set`; constructors optionally deserialize C strings; `deserialize` accepts C string or `std::string`; `serialize` joins set values with single spaces.

Control flow: deserialization scans from token start to space or NUL, inserts tokens with length greater than one, and continues until NUL. Serialization iterates the sorted set, appends a trailing space per value, then removes the final separator.

State and persistence: there is no external persistence beyond the xattr-compatible string. Using `std::set` sorts and deduplicates values, so original order and duplicate tokens are intentionally lost.

Dependencies and integration: only depends on MGM namespace macros and standard library containers. It is suited for simple xattrs whose values cannot contain spaces.

Risks: single-character tokens are dropped because the condition is `str-begin > 1`; if one-character values are valid, this is a bug. Empty or repeated spaces are ignored. Values containing spaces cannot round-trip.

Test signals: cover empty strings, repeated tokens, leading/trailing/multiple spaces, one-character tokens, sorted serialization, and round-trip behavior for expected xattr values.
