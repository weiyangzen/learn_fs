# sources/distributed-fs/ceph-client/tools/perf/util/demangle-ocaml.c

## Purpose

`demangle-ocaml.c` demangles OCaml native-code symbols emitted with the `caml` prefix into more readable module/function names.

## Important APIs, Types, and Functions

The exported API is `ocaml_demangle_sym(const char *sym)`. `ocaml_is_mangled()` recognizes names beginning with `caml` followed by an uppercase letter. The demangler rewrites `__` to `.`, decodes `$xx` hex escapes, and otherwise copies characters after the prefix.

## Control Flow

The function first rejects symbols that do not match the OCaml mangling shape. For matching symbols, it allocates an output buffer no larger than the input, skips the `caml` prefix, then scans until the end applying the two rewrite rules and null-terminating the result.

## State and Persistence Behavior

There is no global or persistent state. Returned strings are heap allocated and caller-owned.

## Dependencies and Integration Points

It depends on `util/string2.h` for hex decoding, Linux ctype helpers, and `demangle-ocaml.h`. It integrates with perf symbol display where language-specific demanglers are attempted.

## Risks and Edge Cases

The scanner checks `sym[i + 1]` and `sym[i + 2]` for escape patterns, so malformed trailing `_` or `$` near the string end relies on the NUL terminator being safe to inspect. The recognizer intentionally excludes lowercase-after-prefix symbols. Hex escapes can decode to non-printable bytes.

## Test Signals

Tests should cover valid module/function symbols, double-underscore module separators, `$xx` escapes, lowercase or missing-prefix rejection, trailing `$` and partial hex sequences, allocation failure behavior, and display fallback on `NULL`.
