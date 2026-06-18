# sources/user-network-fs/mergerfs/vendored/CLI11/CLI11.hpp lines 1-6823

## Scope

This chunk covers the front portion of the vendored CLI11 single-header library, version 2.6.2. It starts at the generated header metadata and standard/platform includes, then defines the `CLI` namespace support layer through most of `CLI::Option`. The range ends inside `Option::_validate_results`, before the rest of option reduction, parsing, `App`, config serialization, and formatter implementations that appear later in the header.

This is third-party command-line parsing infrastructure used by mergerfs rather than mergerfs-specific filesystem logic. The code is header-only unless `CLI11_COMPILE` is defined, in which case `CLI11_INLINE` changes linkage expectations.

## Purpose

The covered code provides the foundation for CLI11's public API:

- Compiler/platform feature detection for C++14/17/20/23/26, RTTI, `<filesystem>`, `<codecvt>`, Windows argument decoding, and inline/module linkage.
- UTF-8/wide-string conversion helpers for Windows and non-Windows builds.
- String parsing helpers for command lines, config tokens, quoted strings, binary-escaped strings, option-name splitting, and paragraph formatting.
- The CLI11 error hierarchy and typed exit codes.
- Template metaprogramming that classifies option target types, generates help type names, converts strings to typed values, and fills tuples/containers/wrappers.
- Config item abstractions and configurable TOML/INI parsing front matter.
- Validators and transformers used by options, including file/path checks, type/range checks, member-set validation, string-to-value mapping, unit conversion, IPv4 validation, and optional permission checks.
- Formatter interfaces and the beginning of option registration/state APIs.
- `OptionBase`, `OptionDefaults`, and most of `Option`, including names, expected counts, validators, needs/excludes, environment binding, defaults, result storage, callback execution, and the beginning of result validation.

## Important APIs And Types

Public and integration-facing items in this chunk include:

- Version macros: `CLI11_VERSION_MAJOR`, `CLI11_VERSION_MINOR`, `CLI11_VERSION_PATCH`, and `CLI11_VERSION`.
- Encoding helpers: `CLI::narrow`, `CLI::widen`, and, when filesystem is available, `CLI::to_path`.
- Windows command-line helper: `detail::compute_win32_argv`, which uses `CommandLineToArgvW(GetCommandLineW())` and converts wide argv values to UTF-8 strings.
- Generic string utilities in `CLI::detail`: `split`, `join`, `rjoin`, `trim` variants, `remove_quotes`, `fix_newlines`, `valid_name_string`, `find_member`, `split_up`, `process_quoted_string`, `binary_escape_string`, `extract_binary_string`, and `streamOutAsParagraph`.
- Error classes: `Error`, `ConstructionError`, `IncorrectConstruction`, `BadNameString`, `OptionAlreadyAdded`, `ParseError`, `Success`, `CallForHelp`, `CallForAllHelp`, `CallForVersion`, `RuntimeError`, `FileError`, `ConversionError`, `ValidationError`, `RequiredError`, `ArgumentMismatch`, `RequiresError`, `ExcludesError`, `ExtrasError`, `ConfigError`, `InvalidError`, `HorribleError`, and `OptionNotFound`.
- Type traits and conversion helpers: `enable_if_t`, `void_t`, `conditional_t`, `is_mutable_container`, `is_tuple_like`, `type_count`, `type_count_min`, `expected_count`, `classify_object`, `type_name`, `lexical_cast`, `lexical_assign`, `lexical_conversion`, `tuple_conversion`, and `sum_string_vector`.
- Option-name helpers: `split_short`, `split_long`, `split_windows_style`, `split_names`, `get_default_flag_values`, and `get_names`.
- Config APIs: `ConfigItem`, abstract `Config`, `ConfigBase`, alias `ConfigTOML`, and `ConfigINI`.
- Validator APIs: `Validator`, `CustomValidator`, built-in global validators such as `ExistingFile`, `ExistingDirectory`, `ExistingPath`, `NonexistentPath`, `EscapedString`, `Number`, `ValidIPV4`, `NonNegativeNumber`, `PositiveNumber`, and classes `FileOnDefaultPath`, `Range`, `Bound`, `IsMember`, `Transformer`, `CheckedTransformer`, `AsNumberWithUnit`, and `AsSizeValue`.
- Formatting interfaces: `AppFormatMode`, `FormatterBase`, `FormatterLambda`, and declaration-heavy `Formatter`.
- Option APIs: `results_t`, `callback_t`, `Option_p`, `Validator_p`, `MultiOptionPolicy`, `CallbackPriority`, `OptionBase<CRTP>`, `OptionDefaults`, and `Option`.

`Option` is the central stateful type in this range. It stores short names, long names, default flag values, one positional name, environment variable name, help strings, dynamic type/default string functions, type arity, expected count range, validators, dependency/exclusion links, parent `App *`, callback, raw results, reduced results, option parse state, and behavior flags such as `allow_extra_args_`, `flag_like_`, `inject_separator_`, `trigger_on_result_`, and `force_callback_`.

## Control Flow

Header setup is mostly preprocessor control flow. Feature macros select C++ feature levels, filesystem support, codecvt support, RTTI behavior, diagnostics pragmas, Windows headers, and whether path checks use `std::filesystem` or `stat`.

String conversion routes through `narrow_impl` and `widen_impl`. With codecvt available, it uses `std::wstring_convert`; otherwise it temporarily switches the process locale to a UTF-8-capable locale, uses `wcsrtombs`/`mbsrtowcs`, and restores the old locale with a scope guard. This fallback is process-global because C locale mutation is global.

Token parsing helpers are layered:

1. `split_names` splits comma-separated declarations.
2. `get_default_flag_values` extracts flag aliases with `{default}` or `!` false-style markers.
3. `get_names` validates and categorizes names into short, long, and positional forms, throwing `BadNameString` for malformed or reserved names.
4. `split_short`, `split_long`, and `split_windows_style` recognize runtime command-line tokens.
5. `split_up`, `close_sequence`, and quote/escape helpers preserve quoted/bracketed groups and unescape JSON-like sequences.

Type conversion control flow is compile-time selected with SFINAE. `classify_object` chooses a category, then `lexical_cast` overloads parse integers, unsigned integers, chars, bools, floating-point values, complex numbers, strings, wide strings, enums, wrappers, constructible numeric classes, and stream-readable fallback types. `lexical_conversion` then scales one-string conversion up to tuples, containers, vectors of tuple-like entries, complex values, and wrapper types. Container conversion uses `detail::is_separator` markers to split variable-sized elements.

Validator control flow is uniform: a validator owns a `std::function<std::string(std::string &)>` that returns an empty string on success or an error message on failure. `Validator::operator&` runs both functions and combines errors; `operator|` succeeds if either validator succeeds; `operator!` fails when the wrapped validator succeeds. Transforming validators mutate the input string, while `check()` marks validators non-modifying before attaching them to an option.

`Option` setup and execution flow in this chunk is:

1. The private constructor parses the option declaration into `snames_`, `lnames_`, and `pname_`.
2. `OptionBase::copy_to` copies default option settings into concrete options.
3. `expected()` and `type_size()` configure how many option occurrences and raw strings are expected.
4. `check()`, `transform()`, and `each()` append or prepend validators.
5. `needs()` and `excludes()` build dependency and mutual-exclusion sets; `excludes()` also inserts the reverse relationship.
6. `ignore_case()` and `ignore_underscore()` temporarily enable matching changes, scan parent app options for conflicts, and roll back on conflict.
7. `add_result()` appends raw parsed strings through `_add_result()` and resets state to `parsing`.
8. `run_callback()` validates raw results if needed, reduces them if needed, picks reduced or raw results, invokes the callback, clears forced default results when appropriate, and throws `ConversionError` if the callback reports failure.
9. `results<T>()` obtains reduced/validated results or default-derived results, stores them in `proc_results_` when needed to stabilize view-like outputs, and uses `detail::lexical_conversion<T, T>`.
10. `_validate_results()` begins validator application. In this chunk it handles multi-value options by computing an index modulo `type_size_max_`, resets indexes on separator entries for variable-sized chunks, and creates negative indexes for earlier values when `TakeLast` or `Reverse` policies mean only later values are relevant. The source range stops before the single-value loop body and before `_reduce_results()`.

## State And Persistence Behavior

Most state is in memory and owned by parser objects:

- `ConfigBase` stores parse/emit configuration such as comment character, array delimiters, quote characters, parent separator, maximum nesting layers, duplicate-field behavior, selected section, and section index.
- `Validator` stores a description function, operation function, name, application index, active flag, and non-modifying flag. Validators attached to options are `std::shared_ptr<Validator>`.
- `OptionBase` stores option defaults and behavior shared by `OptionDefaults` and `Option`.
- `Option` stores parse results in `results_`, caches reduced results in mutable `proc_results_`, and tracks lifecycle with `current_option_state_`.

There is no durable persistence in this chunk, but it does include I/O boundaries:

- `Config::from_file()` opens a config file through `std::ifstream`, using `std::filesystem::path` conversion when available.
- Path validators inspect the filesystem with `std::filesystem::status` or `stat`/`_stat64`.
- `get_environment_value()` reads process environment variables via `_dupenv_s` on MSVC or `std::getenv` elsewhere.
- `split_program_name()` probes candidate command prefixes with `check_path()` to infer a program name.

Static local state appears in `AsSizeValue::get_mapping`, which caches size-unit maps for base-1000 and base-1024 interpretations. Global constant validator objects are initialized at program startup or module load according to C++ static initialization rules.

## Dependencies And Integration Points

This header depends only on the C++ standard library and narrow platform APIs:

- Standard headers for algorithms, streams, containers, type traits, locale, conversion, exceptions, and file I/O.
- Optional `<filesystem>` for path validation and config path opening.
- Optional `<codecvt>` for UTF-8/wide conversion on pre-C++26-capable builds.
- POSIX `stat` through `<sys/stat.h>` and `<sys/types.h>` when filesystem is unavailable.
- Windows APIs and headers for native argv decoding and filesystem checks on Windows builds.

Within mergerfs, this vendored header is an integration dependency for command-line parsing. Code that includes it can build a `CLI::App` in later parts of the header, register options, attach validators, read configuration files, consult environment variables, and receive typed callback values. This chunk supplies the low-level pieces those later `App` APIs rely on.

Important internal integration points include:

- `App` is forward-declared and granted friendship by `OptionBase`/`Option`; later `App` code constructs options, owns `Option_p`, runs parsing, calls private validation/reduction helpers, and inspects option internals.
- `ConfigBase` is a friend of `Option` and later maps `ConfigItem` values into options.
- `Formatter` methods are declared here but implemented later; they call option getters such as `get_name`, `get_type_name`, `get_default_str`, and relationship getters.
- `Option`'s `ignore_case` and `ignore_underscore` methods assume the parent object exposes `options_` and `get_option_no_throw`, so they are tightly coupled to the later `App` definition.
- Validators use the same `lexical_cast` and `type_name` infrastructure as option callbacks, making help text, validation, and final conversion consistent.

## Risks And Maintenance Notes

- This is a vendored generated single header. Local edits can diverge from upstream CLI11 and are hard to review because declarations and implementations are interleaved across thousands of lines.
- The codecvt-disabled fallback mutates the process C locale around conversions. The scope guard restores it, but `setlocale` is process-global and can be problematic in multithreaded code.
- Many behaviors are selected by compiler and platform macros. A path validated with `std::filesystem` on one build may go through `stat` on another; Windows also has separate wide/narrow argument handling.
- Template dispatch is broad and subtle. New target types can accidentally classify as strings, wrappers, containers, tuples, or constructible numeric classes, changing how CLI values are split and converted.
- `lexical_cast` accepts numeric separators, base prefixes, boolean synonyms, complex suffixes, and stream fallback. These convenience paths should be covered when changing conversion rules because they affect all options and validators.
- `sum_string_vector` falls back from numeric addition to string concatenation if any element is not numeric/flag-like. This underpins `MultiOptionPolicy::Sum` later and can surprise callers expecting strict numeric behavior.
- Validators may mutate input unless attached through `check()`, which forces `non_modifying()`. Ordering matters because `transform()` inserts validators at the beginning, before later checks.
- `Option::default_val()` temporarily clears and restores `results_` and `current_option_state_` while validating or running callbacks for defaults. Exceptions must leave the old option state intact.
- `excludes()` creates symmetric links but `remove_excludes()` removes only from the current option's set in this chunk. Callers relying on symmetry need to understand later `App` cleanup behavior.
- The range ends mid-`Option::_validate_results`; final validation and reduction semantics are completed outside this chunk.

## Test Signals

Useful validation for this chunk is mostly compile-time plus focused behavioral tests:

- Compile a mergerfs target that includes `sources/user-network-fs/mergerfs/vendored/CLI11/CLI11.hpp` under the repository's normal compiler flags.
- Add or run CLI tests that exercise short, long, positional, default-flag, and Windows-style name splitting.
- Verify malformed declarations throw the expected construction errors: reserved names (`-`, `--`, `++`), one-dash long names when non-standard names are disabled, duplicate positional names, and invalid characters.
- Test string parsing with quoted strings, escaped quotes, `\u`/`\U` escapes, binary escaped strings, bracketed values, and delimiter-separated vectors.
- Test numeric conversion for decimal, hex, octal `0o`, binary `0b`, grouped numbers, unsigned overflow, booleans (`true`, `false`, `on`, `off`, `yes`, `no`, `+`, `-`), floating values, complex values, enums, tuples, and containers.
- Test validators: existing/non-existing file/path, `Range`, `Bound`, `IsMember` with ignore filters, `Transformer`, `CheckedTransformer`, `AsNumberWithUnit`, `AsSizeValue`, and `ValidIPV4`.
- Test option state transitions by adding results, calling `reduced_results()`, calling `results<T>()`, setting `default_val()`, forcing callbacks, and using `trigger_on_parse`.
- Test conflict detection for `ignore_case()` and `ignore_underscore()` against sibling options in a parent `App`.
- On Windows, verify `compute_win32_argv`, wide-string `parse` paths, and `to_path` preserve non-ASCII arguments and file paths.
