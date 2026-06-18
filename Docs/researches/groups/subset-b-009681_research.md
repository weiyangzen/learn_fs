# Research: subset-b-009681

Work item `subset-b-009681` covers three files under the vendored `{fmt}` copy in mergerfs:

- `sources/user-network-fs/mergerfs/vendored/fmt/compile.h`
- `sources/user-network-fs/mergerfs/vendored/fmt/core.h`
- `sources/user-network-fs/mergerfs/vendored/fmt/format-inl.h`

Read signal: all three listed files were read for this pass. `compile.h` is 588 lines, `core.h` is 5 lines, and `format-inl.h` is 1948 lines.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/compile.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/compile.h

## Purpose

`compile.h` implements fmt's experimental compile-time format-string compilation layer. It converts `FMT_COMPILE("...")` or, when enabled, the `"_cf"` literal into a small constexpr representation that can format directly without reparsing the format string at runtime. It sits above `format.h`: the generated representation still calls core fmt writing and `formatter<T, Char>` machinery for actual value formatting.

The file is intentionally feature-gated. The fast compile path is enabled only when the compiler supports `constexpr if` and return type deduction. C++20 non-type template parameters add the optional `"_cf"` literal. Otherwise `FMT_COMPILE` falls back to `FMT_STRING`, preserving compile-time format checking but not necessarily the direct compiled representation.

## Important APIs, Types, and Functions

- `fmt::compiled_string` is a marker base type. `is_compiled_string<S>` identifies FMT string wrapper types produced by `FMT_COMPILE`.
- `FMT_COMPILE(s)` wraps a string literal through `FMT_STRING_IMPL(s, fmt::compiled_string)` when the constexpr compile path is available; otherwise it maps to `FMT_STRING(s)`.
- `fmt::literals::operator""_cf` converts a `detail::fixed_string` to the same compiled-string wrapper when `FMT_USE_NONTYPE_TEMPLATE_ARGS` is true.
- `detail::type_list`, `detail::get<N>`, and `detail::get_type<N, type_list<...>>` are compile-time utilities for resolving a replacement field's argument type from a parameter pack.
- `detail::text<Char>`, `detail::code_unit<Char>`, `detail::field<Char, V, N>`, `detail::spec_field<Char, V, N>`, `detail::runtime_named_field<Char>`, and `detail::concat<L, R>` form the compiled format AST. Each type has a `format(out, args...)` method.
- `detail::compile_format_string<Args, POS, ID>(fmt)` recursively parses literals, escaped braces, positional fields, named fields, and specifier-bearing fields into that AST.
- `detail::parse_specs<T>` instantiates `formatter<T, Char>`, runs its `parse` method under `compile_parse_context`, and stores the parsed formatter inside `spec_field`.
- Public overloads of `fmt::format`, `fmt::format_to`, `fmt::format_to_n`, `fmt::formatted_size`, and `fmt::print` accept compiled-string inputs and dispatch either to the compiled AST or to normal runtime formatting when the compiler cannot statically resolve a field.
- `fmt::static_format_result<N>` and `FMT_STATIC_FORMAT` produce a compile-time, null-terminated result whose size is computed with `formatted_size(FMT_COMPILE(...), ...)`.

## Control Flow

`FMT_COMPILE` creates a type that carries the literal and inherits `compiled_string`. Public `format`/`format_to` overloads then call `detail::compile<T...>(S())`, which builds `basic_string_view` over the literal and invokes `compile_format_string<type_list<T...>, 0, 0>`.

The recursive parser walks the string at compile time. Literal spans become `text`; single literal code units can become `code_unit`; escaped `{{` and `}}` become text; replacement fields resolve either automatic indexes, explicit numeric indexes, compile-time named indexes, or runtime named fields. A field without format specs becomes `field`; a field with specs becomes `spec_field` after parsing the formatter. Each parsed head is joined with the remaining tail through `concat`.

Argument-index state is tracked through the integer template parameter `ID`; `manual_indexing_id == -1` marks explicit indexing. `static_assert`s reject switching from automatic to manual indexing or vice versa. Missing braces and unsupported compile-time forms are rejected with `format_error` or `static_assert`, while named fields with unknown type information and format specs return `unknown_format` so public overloads can fall back to normal runtime `fmt::format`.

The formatted output path is simple: `concat::format` calls `lhs.format` then `rhs.format`; `field::format` extracts the Nth argument with `get_arg_checked`, unwraps named arguments, and writes either string-view data directly or routes the value through `write`; `spec_field::format` creates a `basic_format_context` from `make_format_args` and calls the stored `formatter`.

## State and Persistence Behavior

The file has no external persistence and no global mutable state. The compiled representation is embodied in constexpr object types and in local formatter objects stored inside `spec_field`. Output state is carried by the caller-provided output iterator or by temporary buffers used by `format`, `format_to_n`, `formatted_size`, and `print`.

The only stateful decisions are compile-time parser state: current position, next automatic argument id, and the manually indexed sentinel. Runtime named-field lookup is transient and folds across the function arguments.

## Dependencies and Integration Points

`compile.h` includes `format.h` and uses fmt internals such as `basic_string_view`, `formatter`, `compile_parse_context`, `arg_ref`, `arg_id_kind`, `parse_arg_id`, `basic_format_context`, `make_format_args`, `write`, `copy`, `memory_buffer`, `counting_buffer`, `appender`, `fixed_buffer_traits`, and `iterator_buffer`. It also uses `<iterator>` for `std::back_inserter` unless building as a module.

The public API integrates with regular fmt overload sets via SFINAE on `is_compiled_string` and `is_compiled_format`, so callers can pass compiled wrappers to standard `fmt::format`-style functions. In mergerfs this vendored fmt layer is a dependency implementation detail rather than mergerfs-specific logic.

## Risks and Edge Cases

- This is experimental and compiler-feature dependent; behavior changes across C++ standard modes and vendor support are expected.
- Compile-time named arguments with specs require type information. Unknown named fields with `:` fall back to runtime formatting, while unknown named fields without specs use `runtime_named_field`.
- `get_type<N>` and `get<N>` produce compile-time failures if a field index exceeds the provided argument pack.
- The direct `"{}"` char-format fast path calls `fmt::to_string` on the first argument, with special unwrapping for named args; tests should cover that shortcut separately from the general AST path.
- `format_to_n` fixes the buffer character type to `char` in this file's overload, which is consistent with this vendored fmt version but is worth checking if wide-character compiled strings are used.
- Because `spec_field` stores a parsed `formatter<V, Char>`, formatter parse behavior must be constexpr-compatible for full compile-time compilation.

## Test Signals

Useful signals include compile-only tests for `FMT_COMPILE`, automatic and manual index rejection, escaped braces, named arguments, unknown named fallback, fields with custom format specs, `format_to`, `format_to_n`, `formatted_size`, `print`, and `FMT_STATIC_FORMAT`. Cross-compiler builds should exercise C++14/17/20 gates, `FMT_USE_NONTYPE_TEMPLATE_ARGS`, and compilers without `constexpr if` to ensure fallback to `FMT_STRING` still works.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/compile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/core.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/core.h

## Purpose

`core.h` is a compatibility shim in this vendored fmt version. It exists so code including `fmt/core.h` still compiles, but the file comments warn it may be removed in a future version. It recommends `fmt/base.h` for users that do not need `fmt::format` and `fmt/format.h` otherwise.

## Important APIs, Types, and Functions

This file defines no APIs, types, macros, or functions of its own. Its entire operational content is:

- Include `format.h`.

All visible fmt API exposed through this include comes from `format.h`.

## Control Flow

There is no runtime control flow. Preprocessor inclusion of `core.h` immediately includes the vendored `format.h`, so downstream translation units see the same declarations and inline definitions they would receive from `fmt/format.h`.

## State and Persistence Behavior

No state is created or persisted by this file. It relies entirely on the included fmt headers.

## Dependencies and Integration Points

The only direct dependency is the adjacent `format.h`. The integration point is source compatibility for projects that include `fmt/core.h`; in this repository, it keeps mergerfs or third-party vendored code from depending on an upstream fmt layout detail that has changed over time.

## Risks and Edge Cases

- Because this shim includes `format.h`, it may pull in a larger API and implementation surface than newer upstream `fmt/core.h` users expect.
- The comment states the file may be removed in future versions, so local code should prefer the recommended includes when updating fmt.
- Include-order behavior is delegated to `format.h`; this file does not have its own include guard, so protection depends on `format.h` guards and normal compiler include handling.

## Test Signals

The useful test is build coverage: translation units that include `fmt/core.h` should compile and link exactly as if they included `fmt/format.h`. Any vendored fmt upgrade should include an include-compatibility check for `fmt/core.h`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/format-inl.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/format-inl.h

## Purpose

`format-inl.h` contains non-header-only implementation details for the vendored fmt formatting library. It supplies out-of-line or conditionally inline definitions for assertion failure, locale-aware formatting helpers, system-error formatting, Dragonbox floating-point decimal conversion, bigint formatting support, UTF-8 to UTF-16 conversion, runtime `vformat`, FILE/console printing, and Unicode printable-code-point lookup.

This file is implementation infrastructure for `format.h`; it is not mergerfs-specific. Its correctness directly affects all formatting, printing, diagnostics, and floating-point rendering performed through the vendored fmt copy.

## Important APIs, Types, and Functions

- `assert_fail(file, line, message)` reports failed fmt assertions to `stderr` and aborts unless `FMT_CUSTOM_ASSERT_FAIL` overrides it.
- `locale_ref::get<Locale>()`, fallback `detail::locale`, `detail::numpunct`, `thousands_sep_impl`, `decimal_point_impl`, and `write_loc` provide locale support when `FMT_USE_LOCALE` is enabled and predictable comma/period defaults otherwise.
- `format_error_code`, `format_system_error`, `report_system_error`, `do_report_error`, `vsystem_error`, and `report_error` are the error-reporting and exception construction utilities.
- `detail::dragonbox` contains the fast binary floating-point to shortest decimal conversion implementation. Key pieces are `cache_accessor<float>`, `cache_accessor<double>`, `get_cached_power`, `remove_trailing_zeros`, `shorter_interval_case`, and `to_decimal<T>`.
- `formatter<detail::bigint>` prints fmt's internal bigint in hexadecimal bigit order and appends a power marker when the bigint exponent is positive.
- `detail::utf8_to_utf16::utf8_to_utf16` converts UTF-8 to a null-terminated UTF-16/wchar buffer for Windows console output.
- `vformat`, `detail::vformat_to`, `vprint_buffered`, `vprint`, `vprintln`, and `detail::print` are runtime formatting and output entry points.
- `file_base`, `glibc_file`, `apple_file`, `fallback_file`, `file_print_buffer`, `get_file`, `has_flockfile`, and wrapper functions around `flockfile`/`funlockfile`/`getc_unlocked` implement optimized FILE-buffer integration when libc internals are available.
- `write_console` and `vprint_mojibake` handle Windows console and legacy encoding cases.
- `detail::is_printable(uint32_t)` uses generated tables to decide whether Unicode code points should be treated as printable.

## Control Flow

The top of the file sets platform includes and `FMT_FUNC`, then defines assertion and locale utilities. Error formatting paths first try high-level standard library messages (`std::system_error`) and fall back to bounded inline-buffer messages such as `"error N"` if allocation or formatting fails. `do_report_error` writes to `stderr` without throwing.

Floating-point formatting flows through `detail::dragonbox::to_decimal<T>`. It bit-casts the float/double, extracts exponent and significand fields, handles zero/subnormal/normal cases, computes a cached power of ten, and derives the shortest decimal significand/exponent pair. Normal powers with zero significand can use `shorter_interval_case`; other values execute the regular path: compute scaled interval endpoints, try the larger decimal divisor, compare endpoint inclusion and parity, remove trailing zeros, and fall back to the small-divisor path when necessary. `cache_accessor<double>` either uses the full cached-power table or reconstructs cache entries from a compressed table plus powers of five, depending on `FMT_USE_FULL_CACHE_DRAGONBOX`.

Runtime string formatting enters `vformat`, allocates a `memory_buffer`, calls `detail::vformat_to`, then converts the buffer to `std::string`. `detail::vformat_to` optimizes the exact `"{}"` case by visiting argument zero directly; otherwise it calls `parse_format_string` with a `format_handler` constructed from parse context, output appender, arguments, and locale.

Printing selects between buffered and direct paths. `vprint` checks whether the detected `FILE` wrapper is buffered and whether `flockfile` support exists. If not, it formats into a `memory_buffer` and writes with `fwrite_all`. If yes, `file_print_buffer` locks the FILE, points fmt's buffer at the libc write buffer, advances it as data is produced, and unlocks/flushed as needed. On Windows non-`FMT_USE_WRITE_CONSOLE` builds, `detail::print` detects TTY output, converts UTF-8 to UTF-16, and calls `WriteConsoleW`; otherwise it writes bytes.

Unicode printability is a table lookup: `is_printable(uint32_t)` selects generated singleton and range tables for BMP and supplementary planes, then rejects a handful of explicit high-plane ranges and bounds at `0x110000`.

## State and Persistence Behavior

The file has no repository or disk persistence. It does maintain process-local static constants: Dragonbox cached power tables, small power tables, and generated Unicode printability tables. Locale state is read through `locale_ref`; fallback locale behavior is stateless.

I/O state is transient but important: `file_print_buffer` temporarily locks a `FILE*`, writes directly into its internal buffer when supported, advances libc write pointers, and may flush line-buffered streams. `fwrite_all` and `file_base::get/unget` interact with `errno` and C stream error state. Windows console output temporarily materializes a UTF-16 buffer.

## Dependencies and Integration Points

`format-inl.h` includes `format.h` and standard headers for algorithms, errno, limits, math, exceptions, and optional locale support. It depends heavily on fmt internals declared elsewhere: buffers, appenders, parse contexts, `format_handler`, `loc_writer`, `format_facet`, integer traits, `basic_fp`, `float_info`, `uint128_fallback`, `bigint`, UTF code-point iteration, and value visitors.

Platform integration points include glibc `FILE` internals (`_IO_read_ptr`, `_IO_write_ptr`, `_flags`), Apple libc internals (`_p`, `_r`, `_w`, `_bf`), MSVC `_lock_file`/`_unlock_file` and `_fgetc_nolock`, POSIX-style `flockfile`, Windows `_isatty`, `_fileno`, `_get_osfhandle`, and `WriteConsoleW`. Build macros such as `FMT_USE_LOCALE`, `FMT_USE_FULL_CACHE_DRAGONBOX`, `FMT_USE_FALLBACK_FILE`, `FMT_USE_WRITE_CONSOLE`, `FMT_MODULE`, `_WIN32`, and `FMT_CUSTOM_ASSERT_FAIL` materially change compiled behavior.

## Risks and Edge Cases

- Dragonbox arithmetic is precision-critical. Incorrect cached powers, shifts, endpoint inclusion, parity checks, or trailing-zero removal will produce wrong float/double text, often only for narrow boundary values.
- The compressed double cache path is more complex than the full table path and should be tested separately.
- FILE-buffer optimization relies on libc private struct layouts. The SFINAE probes and `FMT_USE_FALLBACK_FILE` reduce portability risk, but libc changes can break assumptions.
- `file_print_buffer` writes directly to stream buffers while holding locks; exception safety and flush-on-newline behavior are important for partially formatted output.
- `format_error_code` intentionally avoids dynamic allocation by fitting into `inline_buffer_size`; long messages can be dropped before appending `"error N"`.
- Windows console output assumes input text is UTF-8 and throws on invalid UTF-8 during conversion; byte-oriented fallback writes legacy encoded output.
- Generated Unicode printable tables are opaque and must stay in sync with the fmt version's Unicode policy.
- `assert_fail` aborts the process after writing to `stderr`, which is appropriate for internal assertions but severe if an assertion is reachable from malformed user input.

## Test Signals

High-value tests include fmt's upstream floating-point formatting corpus, boundary floats/doubles around powers of ten, subnormals, signed zero, infinities/NaN through the surrounding formatter path, locale grouping/decimal behavior, `std::system_error` fallback behavior under allocation failure if testable, `vformat("{}")` fast path, ordinary parsed format strings, `vprint` to buffered and unbuffered files, Windows console UTF-8 output, invalid UTF-8 handling, line-buffered flush behavior, and Unicode escaping/printability cases around table boundaries such as BMP singletons and the explicit high-plane ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/format-inl.h -->
