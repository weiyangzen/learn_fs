# sources/distributed-fs/eos/namespace/utils/StringConvertion.hh

## Purpose
Defines a small namespace utility for fast conversion of arbitrary values to strings. The filename preserves a historical misspelling, while the API offers a concise wrapper around `fmt`.

## Important APIs, types, and functions
`template <typename T> std::string stringify(const T& elem)` returns `fmt::to_string(elem)`. It is generic and header-only.

## Control flow
There is no branching. Callers instantiate the template for types supported by `fmt::to_string`.

## State and persistence
No state is kept and no persistence is involved. Output formatting follows the linked `fmt` version and available formatters.

## Dependencies and integration points
Includes `namespace/Namespace.hh` for namespace macros and `fmt/format.h`. It is a convenience adapter for namespace code that wants a uniform string conversion spelling.

## Risks and test signals
Risk is low, but template instantiation failures surface at compile time for unsupported types. Formatting may differ from `std::to_string` for some values. Tests should cover integer, floating-point, string-like, and custom formatter-supported types if callers rely on exact text.
