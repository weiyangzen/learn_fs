# sources/distributed-fs/ceph/src/rgw/picojson/picojson.h

## Purpose
This is a vendored single-header JSON parser/serializer. RGW's JWT code enables `PICOJSON_USE_INT64` before including it so numeric date claims can remain integer values. The header provides a lightweight JSON value tree, serialization, stream operators, and recursive-descent parsing.

## Important APIs, types, and functions
- `picojson::value` stores one of null, bool, double, string, array, object, and optionally int64.
- `picojson::array` and `picojson::object` alias `std::vector<value>` and `std::map<std::string, value>`.
- `value::is<T>()`, `get<T>()`, `set<T>()`, `contains()`, `evaluate_as_boolean()`, `to_str()`, and `serialize()` are the main value APIs.
- Parser helpers include `input<Iter>`, `_parse_string()`, `_parse_codepoint()`, `_parse_array()`, `_parse_object()`, `_parse_number()`, and `_parse()`.
- Parse contexts include `default_parse_context`, `null_parse_context`, and `deny_parse_context`.
- Top-level `parse()` overloads parse from iterators, strings, and streams; stream operators use `get_last_error()`/`set_last_error()`.

## Control flow
`parse()` wraps input iterators in `input`, skips whitespace, dispatches by the next character, recursively parses arrays/objects, decodes strings including unicode surrogate pairs, parses numbers with `strtoimax` first when int64 support is enabled, and falls back to `strtod`. Serialization dispatches by type, escapes string control characters, optionally pretty-prints indentation, and emits locale-normalized numeric text.

## State and persistence behavior
`value` owns heap-allocated strings, arrays, and objects through a manual union plus `clear()`, copy/swap assignment, and optional move operations. There is no durable persistence. Missing array/object lookups return references to static null values, and the stream error API uses a static string.

## Dependencies and integration points
The header depends only on the C/C++ standard library and optional locale support. It is included by `jwt-cpp/jwt.h` and can be configured by macros such as `PICOJSON_USE_INT64`, `PICOJSON_USE_RVALUE_REFERENCE`, `PICOJSON_USE_LOCALE`, `PICOJSON_NOEXCEPT`, and `PICOJSON_ASSERT`.

## Risks and edge cases
- Manual union storage and static null references require care: non-const missing `get()` returns a static mutable null value.
- Deeply nested JSON can recurse until stack exhaustion.
- `parse(value&, const std::string&)` does not require full consumption of trailing non-whitespace unless callers inspect the returned iterator through the lower-level overload.
- Locale-aware parsing/printing can be surprising in multi-threaded programs that mutate process locale.
- Duplicate object keys overwrite earlier values through `o[key]`.
- Number parsing with int64 enabled changes type behavior; `is<double>()` can be true for int64 and `get<double>()` converts the value to number type.

## Test signals
Tests should cover valid/invalid JSON, full-consumption expectations, unicode escapes and surrogate errors, control-character escaping, int64 boundaries, floating special-value rejection, duplicate keys, deep nesting limits, stream failbit behavior, pretty serialization, and JWT claim parsing for objects, arrays, strings, and integer dates.
