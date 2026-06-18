# Research Group: subset-b-009682

This grouped report covers the requested vendored fmt headers under `sources/user-network-fs/mergerfs/vendored/fmt`. Each section is source-tree aligned and can be split into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/format.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/format.h

## Purpose
`format.h` is the main implementation surface for the vendored `{fmt}` formatting library used by mergerfs. It builds on `base.h` and supplies the public `fmt::format`, locale-aware formatting, `fmt::format_to`, `fmt::formatted_size`, `fmt::to_string`, `fmt::format_int`, `fmt::system_error`, pointer/enum helpers, named-argument literals, and most of the internal integer, floating-point, Unicode, buffer, and formatter dispatch machinery.

## Important APIs, Types, and Functions
Public-facing types include `basic_memory_buffer`, `memory_buffer`, `writer`, `string_buffer`, `format_error`, `generic_context`, `loc_value`, `format_facet`, `bytes`, `group_digits_view`, `nested_formatter`, and `format_int`. Public helpers include `fmt::format`, `fmt::vformat`, locale overloads of `format`/`vformat_to`/`format_to`/`formatted_size`, `fmt::ptr`, `fmt::underlying`, `fmt::group_digits`, `fmt::to_string`, `fmt::system_error`, `fmt::format_system_error`, and `fmt::report_system_error`. Formatter specializations cover strings, character arrays, pointers, `std::byte`, enum `format_as`, `bytes`, grouped digits, and platform integer/float variants.

Important internal types include `uint128_fallback`, `dragonbox::decimal_fp`, `basic_fp`, `bigint`, `digit_grouping`, `fallback_digit_grouping`, `dynamic_spec_getter`, `format_handler`, `default_arg_formatter`, and `arg_formatter`. Important internal functions include `reserve`, `to_pointer`, `format_decimal`, `format_base2e`, `utf8_decode`, `for_each_codepoint`, `display_width_of`, `write_padded`, `write_int`, `write_float`, `format_float`, `format_dragon`, `format_hexfloat`, `parse_align`, `write_escaped_string`, `write_escaped_char`, and dynamic width/precision handling.

## Control Flow
Runtime formatting flows from `fmt::format` to `vformat`, then into `detail::vformat_to` from `base.h` with a `format_handler`. The handler copies literal text, resolves positional or named argument ids, parses format specs, applies dynamic width and precision from arguments, then dispatches either custom formatters or built-in formatting visitors. Built-in integers are normalized into unsigned absolute values plus encoded sign/prefix metadata, then written in decimal, hex, octal, binary, or character presentation with optional padding and grouping. Floating-point formatting first handles sign, non-finite values, locale, and precision; fast IEEE values use Dragonbox for shortest output, while precision and hard cases can route through Dragon/FPP big-integer generation and then fixed or exponent rendering.

String and character formatting route through debug escaping when requested, including UTF-8 decoding for display width and escape boundaries. Output iterators are optimized by reserving contiguous backing storage when possible, otherwise temporary stack or memory buffers are copied into the supplied iterator. Locale-aware paths query thousands separators, grouping, decimal points, and optional locale facets, but fall back to unlocalized formatting when locale support or a facet is absent.

## State and Persistence Behavior
The header is mostly stateless template code. Mutable state is local to buffers, format contexts, parser contexts, formatter objects, and temporary conversion helpers. `basic_memory_buffer` owns inline storage plus optional heap storage and moves by either stealing heap storage or copying when allocator propagation rules require it. `format_int` stores digits in an object-local fixed buffer and writes a trailing NUL only when `c_str()` is called. Persistent external state is limited to locale facets attached to `std::locale` objects and error reporting through thrown exceptions or `report_system_error` output; there is no project-specific persistent storage.

## Dependencies and Integration Points
`format.h` depends directly on `base.h` for core parse contexts, argument storage, format specs, buffer primitives, and macros. Optional implementation dependencies include C headers, C++ string/runtime/error headers, compiler intrinsics, `std::bit_cast`, `std::string_view`, native 128-bit integers, `__float128`, locale support, and `format-inl.h` in header-only builds. Mergerfs integration is indirect: source that includes vendored fmt uses these APIs for formatted strings, logs, exceptions, and user-facing messages without depending on the system fmt package.

## Risks
This is a large vendored implementation with many compiler, standard-library, ABI, and platform feature branches. Risks include divergence from upstream fmt security/compatibility fixes, undefined-behavior sensitivity in low-level bit casts and compiler intrinsics, allocation failures in buffers, formatting differences across locale and floating-point modes, UTF-8 edge cases in debug display width and escaping, and code-size or compile-time growth from template instantiations. `FMT_HEADER_ONLY`, exception settings, RTTI settings, locale settings, and int/float feature macros materially change behavior. Because it is vendored, local edits should be minimized unless syncing an upstream fmt release.

## Test Signals
Strong signals are successful mergerfs compilation under the supported compilers and C++ standard mode, plus direct tests of integer bases, sign/padding/alignment, dynamic width and precision, locale grouping, pointer formatting, null string handling, UTF-8 debug escaping, NaN/Inf formatting, shortest and precision floating output, `format_int`, `to_string`, and `system_error` text. Regression tests should include header-only and non-header-only builds when applicable, sanitizers for low-level numeric code, and comparison with upstream fmt behavior for edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/os.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/os.h

## Purpose
`os.h` adds optional OS-facing functionality to fmt: C-string view wrappers, platform error helpers, RAII file descriptor and `FILE*` wrappers, pipes, page-size access, and a fast buffered output stream for files. It is an extension layer over `format.h`, not part of the core formatter parser.

## Important APIs, Types, and Functions
Public types include `basic_cstring_view`, `cstring_view`, `wcstring_view`, `buffered_file`, `file` when `FMT_USE_FCNTL` is enabled, `pipe`, `detail::buffer_size`, `detail::ostream_params`, and `ostream`. Public helpers include `system_category`, Windows-only `windows_error`/`vwindows_error`/`report_windows_error`, macOS-only `say`, `getpagesize`, `buffer_size`, and `output_file`. `file` exposes open flags (`RDONLY`, `WRONLY`, `RDWR`, `CREATE`, `APPEND`, `TRUNC`), `descriptor`, `close`, `size`, `read`, `write`, `dup`, `dup2`, `fdopen`, and Windows wide-path open support.

## Control Flow
Header setup detects whether `<fcntl.h>` and POSIX-like file APIs are usable, maps POSIX calls through `_`-prefixed Windows variants where necessary, and wraps system calls through `FMT_SYSTEM` for testability. `buffered_file` owns a `FILE*`, closes it in the destructor, supports move transfer, and formats by choosing buffered or regular `vprint` depending on argument locking traits. `file` owns an integer descriptor, closes in destructor, retries interrupted POSIX calls via `FMT_RETRY`, and can transfer ownership to `buffered_file` through `fdopen`. `ostream` owns a `file` and a `detail::buffer<char>`; `print` appends formatted bytes to the buffer, `flush` writes buffered bytes to the descriptor, and `close` flushes then closes.

## State and Persistence Behavior
The stateful objects in this header own OS resources. `buffered_file` persists an open `FILE*` until `close`, move assignment, or destruction. `file` persists a descriptor until `close`, move assignment, or destruction, using `-1` as the closed sentinel. `pipe` persists two descriptors. `ostream` persists buffered bytes in memory until flush, close, or destruction, then writes to the filesystem. These wrappers intentionally interact with durable external state: opening, truncating, appending, writing, duplicating, and closing files.

## Dependencies and Integration Points
The header depends on `format.h`, C runtime file APIs, POSIX file APIs when enabled, Windows CRT shims, `std::system_error`, optional `<xlocale.h>`, and optional Windows family detection. It integrates with fmt's `writer` abstraction by converting `ostream` to a `writer`, with fmt print APIs through `buffered_file::print` and `ostream::print`, and with mergerfs anywhere vendored fmt is used for file or error output.

## Risks
The primary risks are OS resource leaks or double-close behavior if ownership semantics are violated, platform gaps when `FMT_USE_FCNTL` is disabled, Windows invalid-parameter behavior on repeated close, short read/write handling, interrupted system calls outside Windows, and data loss if buffered `ostream` is not flushed before abnormal termination. `output_file` defaults to create/truncate, so accidental use can overwrite files. Because APIs throw `fmt::system_error` for failures, callers must not rely on silent failure.

## Test Signals
Useful tests include opening nonexistent files and checking system errors, RAII close on destruction, move-only transfer of descriptors and `FILE*`, read/write round trips, `dup`/`dup2`, pipe creation, `fdopen`, `output_file` flush and close behavior, custom buffer sizes, and platform-specific Windows wide-path and error-formatting paths. Build signals should cover both `FMT_USE_FCNTL=1` and a configuration where it is disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/ostream.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/ostream.h

## Purpose
`ostream.h` provides integration between fmt and `std::ostream`. It allows values with an `operator<<` to be formatted through fmt, and it adds `fmt::print`/`fmt::println` overloads that write formatted data to a `std::ostream`.

## Important APIs, Types, and Functions
Important APIs include `basic_ostream_formatter`, the `ostream_formatter` alias, `detail::streamed_view`, `fmt::streamed`, `fmt::vprint(std::ostream&, string_view, format_args)`, `fmt::print(std::ostream&, format_string<T...>, T&&...)`, and `fmt::println(std::ostream&, format_string<T...>, T&&...)`. Internal helpers include `detail::write_buffer`, `detail::formatbuf` from `chrono.h`, and platform-specific file-buffer access helpers used to detect Windows console streams.

## Control Flow
`basic_ostream_formatter::format` creates a fmt memory buffer, wraps it in `detail::formatbuf`, constructs a temporary `std::basic_ostream`, imbues the classic locale, streams the value with `operator<<`, then formats the resulting buffer as a string view using any outer fmt string specs. `streamed(value)` creates a lightweight view that selects this formatter explicitly. `print(os, ...)` formats into a memory buffer, then writes to the stream with `write_buffer`; in UTF-8 Windows console cases, `vprint` tries to retrieve the underlying `FILE*`, flushes the stream, and delegates to `detail::write_console`.

## State and Persistence Behavior
This header stores no global state. Formatting via `basic_ostream_formatter` uses temporary buffers and streams. `print` and `println` mutate the target `std::ostream` by writing bytes and may flush it on Windows console paths. Stream exception settings are applied to the temporary stream used for `operator<<`, so insertion failures become stream exceptions there. No filesystem state is created unless the supplied stream is backed by a file.

## Dependencies and Integration Points
The header depends on `chrono.h` for `formatbuf`, `format.h` transitively, `<fstream>`, and platform-specific Windows/GLIBCXX stream buffer details when available. It integrates fmt with legacy types that only implement `operator<<`, with `std::thread::id` formatting from `std.h`, and with user code that wants fmt syntax but an existing C++ stream sink.

## Risks
The biggest risk is semantic mismatch between fmt formatting and stream insertion: streamed values use the classic locale and only then receive outer string formatting. Windows console optimization depends on RTTI and implementation-specific `std::filebuf` internals, so it may be inactive or fragile across standard libraries. `println` formats the message to a string and then prints `"{}\n"`, causing an extra allocation relative to direct buffer append. Stream insertion can throw or set failure states depending on the value's `operator<<`.

## Test Signals
Tests should verify `fmt::streamed` for custom `operator<<` types, width/alignment applied to the streamed result, direct `print` and `println` to `std::ostringstream`, large buffer writes beyond `std::streamsize` chunks, classic-locale behavior, and Windows console UTF-8 handling where available. Negative tests should cover stream insertion failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/ostream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/printf.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/printf.h

## Purpose
`printf.h` implements fmt's legacy `printf`-style formatting API. It parses `%` conversion syntax, maps printf flags, width, precision, length modifiers, and conversion specifiers onto fmt's `format_specs`, and exposes `sprintf`, `fprintf`, and `printf` wrappers.

## Important APIs, Types, and Functions
Public types include `basic_printf_context`, `printf_context`, `wprintf_context`, `printf_args`, `wprintf_args`, and `vprintf_args`. Public functions include `make_printf_args`, `vsprintf`, `sprintf`, `vfprintf`, `fprintf`, and `printf`. Internal helpers include `parse_flags`, `parse_header`, `parse_printf_presentation_type`, `vprintf`, `printf_width_handler`, `printf_precision_handler`, `arg_converter`, `char_converter`, `get_cstring`, `is_zero_int`, and `printf_arg_formatter`.

## Control Flow
`sprintf`, `fprintf`, and `printf` create `basic_printf_context` argument stores and call `detail::vprintf`. The parser scans literal text until `%`, treats `%%` as an escaped percent, parses optional positional indexes, flags, width, precision, length modifiers, and conversion type, then fetches the referenced argument. Dynamic `*` width and precision consume arguments. Length modifiers convert integral arguments to the target signed or unsigned width before formatting. The final conversion type is translated to a fmt presentation type, uppercase variants set the upper flag, and `printf_arg_formatter` delegates actual output to the core `detail::write` functions.

## State and Persistence Behavior
All parser state is local to `vprintf`: current iterator, parse context, format specs, and output buffer. The context stores references to caller arguments, so argument lifetimes must outlive formatting. `vsprintf` returns an in-memory string. `vfprintf` writes the completed buffer to the supplied `FILE*` with `std::fwrite`; partial writes return `-1`. `printf` writes to `stdout`. There is no persistent state beyond the effects of writing to the provided C stream.

## Dependencies and Integration Points
The header depends on `format.h` for argument storage, buffers, format specs, type categories, and core write routines, plus `<algorithm>` and `<limits>`. It integrates C-style formatting callers with fmt's type-erased argument system and output buffering. It supports `char` and `wchar_t` contexts, though wide overloads are marked deprecated.

## Risks
This is compatibility formatting, not a byte-for-byte libc `printf` clone. Unsupported or mismatched specifiers report fmt errors, `%n` is not implemented, and some undefined libc cases are intentionally not reproduced. Null strings render as `"(null)"` while null pointers render as `"(nil)"`. Positional and sequential argument modes rely on parse-context checks. Precision handling for C strings scans up to the requested precision and assumes a valid pointer. Argument references must remain valid until formatting completes.

## Test Signals
Useful tests include flags (`-`, `+`, space, `#`, `0`), dynamic width and precision, positional arguments, length modifiers (`hh`, `h`, `l`, `ll`, `j`, `z`, `t`, `L`), integer bases, char/string/pointer conversions, null string and pointer rendering, wide-string deprecated paths, invalid format errors, escaped percent handling, and `fprintf` short-write failure behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/printf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/ranges.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/ranges.h

## Purpose
`ranges.h` adds formatting support for ranges, maps, sets, tuple-like types, container adaptors, and `fmt::join`. It detects begin/end and tuple protocols, chooses an appropriate presentation category, and composes element formatters with delimiters.

## Important APIs, Types, and Functions
Public APIs include `range_format`, `is_tuple_like`, `is_tuple_formattable`, `is_range`, `range_formatter`, `range_format_kind`, tuple/range/map/string formatter specializations, `join_view`, `tuple_join_view`, and `fmt::join` overloads for iterator pairs, ranges, tuples, and initializer lists. Internal helpers include `range_begin`, `range_end`, `is_map`, `is_set`, begin/end detection traits, tuple detection and index-sequence helpers, `for_each`, `for_each2`, `range_reference_type`, `uncvref_type`, `parse_empty_specs`, `format_tuple_element`, `is_container_adaptor_like`, and `detail::all`.

## Control Flow
Type selection is compile-time. Tuple-like non-range values format with parentheses by default and parse optional `n` to remove brackets and separators. Ranges are classified as disabled, map, set, sequence, string, or debug string. `range_formatter` parses range-level controls such as `n`, `s`, `?s`, and optional nested element specs after `:`, then iterates begin/end at runtime and formats each element with the underlying element formatter. Sets use braces, sequences use brackets, maps use braces and format key/value tuple elements separated by `": "`. `join` returns view objects whose formatters output elements separated by the requested separator without outer brackets.

## State and Persistence Behavior
Formatter objects store delimiter strings, bracket strings, debug-string flags, and underlying element formatter instances. Runtime formatting only reads the supplied range or tuple and writes to the format context. `join_view` stores iterators/sentinel and a separator view, so it depends on the referenced range and separator data remaining alive through formatting. No persistent external state is created.

## Dependencies and Integration Points
The header depends on `format.h`, tuple utilities, iterator utilities, initializer lists, type traits, and ADL `begin`/`end`. It integrates with fmt's general `formatter<T, Char>` selection, with standard containers through their member begin/end and map/set typedefs, with tuple-like standard and user types through `std::tuple_size`/`std::tuple_element`/`get`, and with container adaptors by accessing the protected `c` member through a derived helper.

## Risks
Compile-time detection can surprise user types that expose `key_type`, `mapped_type`, tuple protocol, or begin/end-like APIs unintentionally. `join` can dangle if called with a temporary range whose iterators do not survive until formatting. Container adaptor formatting relies on the conventional protected member `c`, which is standard for adaptors but still implementation-sensitive. Formatting very large or single-pass ranges consumes the range during formatting. Debug string paths copy character ranges into a buffer before escaping.

## Test Signals
Tests should cover vectors/lists/arrays, maps, sets, tuples, pairs, nested ranges, custom ADL ranges, non-const-only and const-only ranges, character ranges with `s` and `?s`, no-delimiter `n`, nested element specs through `:`, `fmt::join` over iterator pairs/ranges/tuples/initializer lists, queue/stack/priority_queue adaptor output, and dangling-prone usage rejected by review or covered by lifetime tests where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/ranges.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/std.h -->
# sources/user-network-fs/mergerfs/vendored/fmt/std.h

## Purpose
`std.h` provides fmt formatter specializations and helpers for many standard-library types. It extends core formatting to filesystem paths, bitsets, thread ids, optional, expected, source locations, variants, error codes, type info, exceptions, bit-reference proxies, atomics, complex numbers, smart pointers, and reference wrappers.

## Important APIs, Types, and Functions
Public helpers include `fmt::ptr` overloads for `std::unique_ptr` and `std::shared_ptr`, and the filesystem compatibility `fmt::path` wrapper when filesystem support is available. Formatter specializations cover `std::filesystem::path`, `std::bitset<N>`, `std::thread::id`, `std::optional<T>`, `std::expected<T,E>`, `std::source_location`, `std::monostate`, `std::variant`, `std::error_code`, `std::type_info`, `std::exception` subclasses, bit-reference-like proxy types, `std::atomic<T>`, `std::atomic_flag`, `std::complex<T>`, and `std::reference_wrapper<T>`. Internal helpers include path conversion/escaping, variant/expected alternative escaping, demangling and ABI-name normalization, bit-reference detection, and `format_as` guards for reference wrappers.

## Control Flow
Feature macros gate optional standard-library support based on headers and `__cpp_lib_*` values. Filesystem paths parse alignment, width, debug `?`, and generic `g` options, then either write native/generic path strings or escaped debug path strings with UTF-16 to UTF-8 conversion where needed. Optional and expected format as `optional(...)`, `none`, `expected(...)`, or `unexpected(...)`. Variants visit the active alternative and format it with debug escaping where applicable, catching `bad_variant_access`. Error codes parse width/debug/string options and output either `category:value` or `message`. Complex numbers parse numeric specs, format `(real+imagi)` when the real part is nonzero and `imagi` otherwise, with outer width applied after composing into a temporary buffer.

## State and Persistence Behavior
Formatter instances store parsed specs and small flags such as debug mode, path type, and exception typename mode. Formatting is read-only with respect to input objects except atomics, which perform `load()`, and `atomic_flag`, which performs `test()` when available. Temporary memory buffers are used for escaped paths, error-code strings, complex numbers with width, and demangled names. No external persistent state is modified.

## Dependencies and Integration Points
The header depends on `format.h` and `ostream.h`, plus many conditional standard headers: atomic, bitset, complex, exception, functional, memory, thread, typeinfo, filesystem, variant, optional, source_location, expected, and version. ABI demangling uses `<cxxabi.h>` when available and RTTI when enabled. It integrates with `ranges.h` indirectly by avoiding `format_as` traps and using nested/string formatters, and with ostream formatting for `std::thread::id`.

## Risks
Behavior varies significantly with compiler, standard-library, RTTI, and feature-test macros. Filesystem formatting has platform encoding risk, especially Windows wide native paths and invalid UTF-16 replacement. Demangled type names are ABI- and standard-library-specific despite normalization. Exception formatting with `t` only includes type names when RTTI is enabled. Atomic formatting observes a momentary value only. Variant and expected formatting require all alternatives to be formattable, and alternative string/char values are debug-escaped. `std::complex` uses numeric specs for components, so invalid specs surface through underlying numeric formatting.

## Test Signals
Tests should cover each feature macro path available in the build: filesystem native/generic/debug output, bitset padding, thread id ostream formatting, optional engaged/empty, expected value/error, source location layout, variant alternatives and valueless handling, error_code default/string/debug forms, exception `what()` and optional type name, bit-reference proxies such as `vector<bool>::reference`, atomic and atomic_flag formatting, complex real/imaginary/non-finite values, smart-pointer `ptr`, and reference_wrapper forwarding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/fmt/std.h -->
