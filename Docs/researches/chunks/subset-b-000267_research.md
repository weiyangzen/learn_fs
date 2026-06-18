# sources/cloud-native/overlaybd/src/tools/CLI11.hpp lines 1-6694

## Scope And Purpose

This chunk is the first 6,694 lines of Overlaybd's vendored single-header copy of CLI11 2.2.0. It supplies almost all public setup-time and early parse-time machinery used by the Overlaybd command-line tools: portability macros, string/token helpers, error types, compile-time type deduction, lexical conversion, config item parsing interfaces, validators, help formatting interfaces, `Option`, `OptionDefaults`, and the first large portion of `App`.

The header is intentionally self-contained. It carries the CLI11 BSD-style license text, defines version macros, conditionally detects C++14/C++17/C++20 support, conditionally uses `std::filesystem`, and otherwise falls back to `stat`-based path checks. Overlaybd includes this file directly from tools such as `overlaybd-create.cpp`, `overlaybd-apply.cpp`, `overlaybd-commit.cpp`, `overlaybd-merge.cpp`, `overlaybd-zfile.cpp`, and `turboOCI-apply.cpp`.

For Overlaybd, the important purpose is pragmatic command-line binding: tools construct `CLI::App`, add options and flags that bind into local C++ variables, attach validators such as `CLI::ExistingFile` and `CLI::NonNegativeNumber`, set defaults, then call `CLI11_PARSE(app, argc, argv)`. This chunk owns the API surface that turns those declarations into parse state, type conversion, validation, help output, and parse errors.

## Important APIs, Types, And Functions

The portability and low-level helper layer defines `CLI11_VERSION*`, `CLI11_CPP14`, `CLI11_CPP17`, `CLI11_HAS_FILESYSTEM`, `CLI11_USE_STATIC_RTTI`, and `CLI11_DEPRECATED`. `CLI::detail` then provides string and option-name utilities including `split`, `join`, `rjoin`, `trim`, `remove_quotes`, `fix_newlines`, `valid_name_string`, `split_up`, `escape_detect`, `add_quotes_if_needed`, `split_short`, `split_long`, `split_windows_style`, `split_names`, and `get_names`.

The error hierarchy starts with `CLI::Error`, `ConstructionError`, and `ParseError`, then specializes errors such as `IncorrectConstruction`, `BadNameString`, `OptionAlreadyAdded`, `CallForHelp`, `CallForAllHelp`, `CallForVersion`, `FileError`, `ConversionError`, `ValidationError`, `RequiredError`, `ArgumentMismatch`, `RequiresError`, `ExcludesError`, `ExtrasError`, `ConfigError`, `InvalidError`, `HorribleError`, and `OptionNotFound`. `ExitCodes` gives stable integer codes for parser success, construction failures, parse failures, and base errors. `CLI11_PARSE` catches `CLI::ParseError` and returns `app.exit(e)`.

The type system layer is a major part of the chunk. It defines `enable_if_t`, `void_t`, `conditional_t`, type traits for booleans, pointers, containers, wrappers, tuple-like objects, streamability, complex numbers, and object categories. `type_count`, `type_count_min`, `subtype_count`, `expected_count`, `type_name`, `lexical_cast`, `lexical_assign`, and `lexical_conversion` infer how many command-line strings an option consumes and how to convert them into scalar, enum, bool, string, container, tuple, complex, wrapper, and stream-parsable target types.

Configuration support begins with `ConfigItem`, `Config`, `ConfigBase`, `ConfigTOML`, and `ConfigINI`. This chunk declares `ConfigBase::to_config()` and `ConfigBase::from_config()` and implements generic config-file entry points such as `Config::from_file()`, which opens an `ifstream` and throws `FileError::Missing` if the file is not readable. Config items carry parent sections, a name, inputs, and a dot-joined `fullname()`.

Validation support centers on `Validator`. A validator owns a description function, a string-mutating validation function, a name, an application index, and active/non-modifying flags. Validators can be combined with `operator&`, `operator|`, and `operator!`. Built-ins in this chunk include `ExistingFile`, `ExistingDirectory`, `ExistingPath`, `NonexistentPath`, `ValidIPV4`, `TypeValidator`, `Number`, `FileOnDefaultPath`, `Range`, `NonNegativeNumber`, `PositiveNumber`, `Bound`, `IsMember`, `Transformer`, `CheckedTransformer`, `AsNumberWithUnit`, and `AsSizeValue`.

Formatting APIs include `AppFormatMode`, `FormatterBase`, `FormatterLambda`, and `Formatter`. The default formatter exposes overridable hooks such as `make_help`, `make_group`, `make_positionals`, `make_groups`, `make_subcommands`, `make_subcommand`, `make_expanded`, `make_footer`, `make_description`, `make_usage`, `make_option`, `make_option_name`, `make_option_opts`, `make_option_desc`, and `make_option_usage`. Implementations for many formatter methods are declared here but appear later in the single header outside this chunk.

`OptionBase`, `OptionDefaults`, and `Option` are the core option model. `OptionBase` owns shared option defaults such as group, required status, case/underscore matching, config enablement, delimiter, default capture, and `MultiOptionPolicy`. `Option` adds names, environment binding, descriptions, default text, type metadata, validators, dependency/exclusion sets, callback, parse results, processed results, and an internal state machine with `parsing`, `validated`, `reduced`, and `callback_run`.

`App` is the top-level command/subcommand object. In this chunk it owns app names and descriptions, options, help/version/config pointers, formatter/config formatter, subcommands, parse state, requirement counts, callbacks, and inheritance behavior for subcommands. Public APIs covered here include constructor/destructor, callback registration, names/aliases, enable/disable/silent flags, parser behavior toggles, formatter configuration, `add_option`, `add_option_no_stream`, `add_option_function`, `add_flag`, `add_flag_callback`, `add_flag_function`, `set_help_flag`, `set_help_all_flag`, `set_version_flag`, `set_config`, option removal, option groups, subcommand add/remove/lookup, requirement setters, `clear`, `parse` overloads, `parse_from_stream`, `exit`, `count`, `count_all`, `get_subcommands`, and `got_subcommand`.

## Control Flow

Command-line setup starts with construction of `CLI::App`, which installs `-h,--help` by default. Callers add options and flags. `App::add_option()` first constructs a temporary `Option` to check name collisions, creates the real owned `Option`, installs default capture behavior, copies `OptionDefaults`, captures defaults when requested, and returns a raw pointer for fluent configuration. `App::_add_flag_internal()` strips default flag modifiers like `{value}` or `!`, rejects positional flags, sets `TakeLast`, sets expected arity to zero, and clears required status.

Variable-bound options wrap a callback around `detail::lexical_conversion<AssignTo, ConvertTo>()`. The template path sets help type text, type-size range, expected count, and default callback behavior from the target type. Flags similarly wrap callbacks around `lexical_cast()` or an integer count, with integral multi-byte flags defaulting to `MultiOptionPolicy::Sum`, default string `"0"`, and forced callback behavior.

Parsing begins through `parse(argc, argv)`, `parse(string)`, `parse(vector&)`, `parse(vector&&)`, or `parse_from_stream()`. `parse(argc, argv)` sets the automatic program name from `argv[0]`, reverses the argument vector, and delegates. `parse(string)` optionally extracts a program name, rewrites escaped quotes after `=` and Windows-style `:`, tokenizes with `split_up()`, removes empty tokens, reverses the vector, and delegates. The vector overloads clear stale parse state, temporarily mark the app parsed so validation/configuration can run, call `_validate()` and `_configure()` implemented later in the header, reset `parent_` for top-level parsing, call `_parse()`, and finally `run_callback()`.

Option callback flow is staged. `Option::add_result()` stores raw strings and resets the option state to `parsing`. `Option::run_callback()` validates raw results, reduces them according to `MultiOptionPolicy`, marks the callback as run, and invokes the stored callback with either reduced or raw results. `Option::results<T>()` can re-run validation/reduction on demand when the callback has not already done so, then converts strings into the requested type.

Validation flow is ordered and may mutate values. `Option::check()` appends non-modifying validators, while `Option::transform()` inserts modifying validators at the front. `_validate_results()` applies validators either by type-position index or by occurrence index, with special handling for `TakeLast` so discarded leading results can receive negative indexes. `_validate()` catches `ValidationError` thrown by a validator and converts it into a message tied to the option name.

Reduction flow depends on `MultiOptionPolicy`. `TakeLast` and `TakeFirst` trim to expected item count; `Join` concatenates with a delimiter; `Sum` numerically sums values or concatenates non-numeric strings; `Throw` enforces min/max arity with `ArgumentMismatch`. Empty-container markers use `"{}"` and separator `"%%"` so container conversion can distinguish an empty container from missing values.

Exit flow is centralized in `App::exit()`. Runtime errors return their code without output. Help, all-help, and version requests print to stdout and return success. Other parse errors go through `failure_message_`, defaulting to `FailureMessage::simple`, and return the error exit code.

## State And Persistence Behavior

The dominant state is in-memory parser state. `App` tracks `options_`, `subcommands_`, `missing_`, `parse_order_`, `parsed_subcommands_`, dependency/exclusion sets, parse counters, callback functions, help/config/version option pointers, and inherited parser settings. `clear()` resets parse counters and parsed data recursively but preserves option/subcommand definitions.

`Option` stores raw `results_`, reduced `proc_results_`, validators, default strings/functions, type-size and expected-count settings, dependencies/exclusions, and callback state. Results are intentionally invalidated whenever new data is added or a multi-option policy changes. `force_callback_` can synthesize a result from `default_str_` when no command-line value was provided.

The chunk does not write persistent state. It can read persistent state through `Config::from_file()` and `parse_from_stream()`, and it can inspect filesystem metadata through path validators. `ConfigBase::to_config()` is declared here and implemented later, but within this range config output is represented as strings, not written to files.

Several global `const` validator objects are defined in namespace `CLI`, including `ExistingFile`, `ExistingDirectory`, `ExistingPath`, `NonexistentPath`, `ValidIPV4`, `Number`, `NonNegativeNumber`, and `PositiveNumber`. `AsSizeValue` caches generated unit maps in function-local statics. These are process-local immutable or effectively immutable resources used by all tools that include the header.

Subcommands inherit many settings from parents at construction time: help flags, option defaults, failure-message formatter, extras policy, prefix mode, immediate callback behavior, name matching behavior, fallthrough, validation toggles, config behavior, Windows-style option support, group, footer, formatter, config formatter, and maximum subcommand requirement. Later parent mutations do not automatically rewrite already-created child state unless the relevant API explicitly touches it.

## Dependencies And Integration Points

This header depends only on the C++ standard library and optional filesystem support. It includes containers, streams, functional, type traits, memory, limits, file streams, and either `<filesystem>` or POSIX/Windows stat headers. Its filesystem detection deliberately disables `std::filesystem` on macOS targets before 10.15, WASI, and older libstdc++ combinations.

Overlaybd integration is direct and broad. `overlaybd-create.cpp`, `overlaybd-apply.cpp`, `overlaybd-commit.cpp`, `overlaybd-merge.cpp`, `overlaybd-zfile.cpp`, and `turboOCI-apply.cpp` include this header and use `CLI::App`, `add_option`, `add_flag`, `default_val`, `default_str`, `required`, `type_name`, `check(CLI::ExistingFile)`, `check(CLI::NonNegativeNumber)`, and `CLI11_PARSE`. Failures in this header therefore surface as process exit codes and user-facing command-line diagnostics for those tools.

The main integration contract is callback binding. `App::add_option()` and `App::add_flag()` keep references to user variables through lambdas. Those referenced variables must outlive parsing, which is true for the Overlaybd tools because variables are local in `main()` and parsed immediately.

Config integration is abstracted through `Config` and `ConfigBase`; `App::set_config()` creates an option that points at a config file and marks it non-configurable. The actual `_configure()` implementation is later in the header, so this chunk establishes the API and state but not the full config application loop.

Help integration is similarly split. This chunk declares the formatter interfaces and stores formatter pointers in `App`; the concrete formatting method bodies are later in the generated header. Calls such as `App::exit(CallForHelp)` and `set_help_flag()` connect parse results to formatter output.

## Risks And Edge Cases

Because this is a vendored generated header, local edits are high blast radius and can diverge from upstream CLI11 2.2.0. Overlaybd uses only a subset of the API, but all included translation units compile the entire template-heavy header, so seemingly unused template changes can affect compile portability.

The compile-time conversion traits are powerful but fragile. Small type changes in tool variables can change expected arity, type names, default capture, and conversion behavior. Containers, tuples, wrappers, complex numbers, and map-like types receive special treatment. Conversion failures often appear at parse time as `ConversionError`, but some unsupported types fail at compile time through static assertions.

Validators can mutate input. `transform()` intentionally runs before checks and can rewrite strings, while `check()` forces non-modifying behavior by copying input before validation. Combining validators with `&`, `|`, and `!` preserves only some metadata, such as the left-side application index. Tests should not assume every validator is read-only.

Flag behavior has several subtle cases. Named default flag values, disabled flag overrides, false flags, integer summing, `default_val()`, `force_callback()`, and `run_callback_for_default()` interact through stored strings such as `"true"`, `"false"`, `"{}"`, and `"0"`. Overlaybd uses many boolean flags with explicit `default_val(false)`, so regressions here can invert or force options unexpectedly.

Path validators follow platform-dependent path classification. With `std::filesystem`, symlinks and special files are treated as `file`; with `stat`, anything that exists and is not a directory is treated as `file`. `ExistingFile` therefore does not strictly mean regular file on every platform.

`parse(argc, argv)` reserves `argc - 1` after casting to `std::size_t`; normal `main()` calls have `argc >= 1`, but a malformed caller passing zero would underflow the reserve size. This is a library edge case rather than an Overlaybd normal path.

`App::parse()` sets `parent_ = nullptr` after validation/configuration when parsing a top-level object. Reusing a subcommand object as a top-level parser or parsing an app more than once depends on this state transition and on `clear()` preserving definitions while resetting parse results.

The requested chunk ends before the private parse engine and formatter/config method bodies. Public methods in this range call `_validate()`, `_configure()`, `_parse()`, `_parse_stream()`, `_compare_subcommand_names()`, `_find_subcommand()`, `run_callback()`, `help()`, and other members whose implementations are outside lines 1-6694. Any final per-file analysis must reconcile this chunk with later chunks before drawing complete conclusions about parse dispatch.

## Test Signals

Overlaybd tool smoke tests should exercise the actual uses of this header: `--help`, missing required positional arguments, invalid `CLI::ExistingFile` paths, invalid `CLI::NonNegativeNumber` values, defaulted boolean flags, explicit true/false flag overrides, and normal successful parsing for each tool that includes `CLI11.hpp`.

Focused parser tests should cover scalar conversion, boolean synonyms, unsigned negative rejection/clamping behavior, enum underlying conversion, vector splitting with delimiters, empty container markers, tuple/container arity, and `MultiOptionPolicy` cases `Throw`, `TakeFirst`, `TakeLast`, `TakeAll`, `Join`, and `Sum`.

Validator tests should cover `ExistingFile`, `ExistingDirectory`, `ExistingPath`, `NonexistentPath`, `ValidIPV4`, `Range`, `Bound`, `IsMember`, `Transformer`, `CheckedTransformer`, `AsNumberWithUnit`, and `AsSizeValue`, including both success and error-message paths. Unit-size tests should include case-insensitive units, required units, overflow detection, and the `kb_is_1000` toggle.

Help and exit tests should confirm that `CLI11_PARSE` returns success for help/version requests, prints help/version to stdout, prints normal parse failures through the configured failure-message function, and preserves the expected `ExitCodes`.

Configuration tests should at minimum verify `Config::from_file()` missing-file behavior and `App::set_config()` option creation/default/required behavior. Complete config parse/write tests need later chunks because `ConfigBase::from_config()`, `to_config()`, and `_configure()` are implemented outside this requested range.

Portability signals include compiling the Overlaybd tools under the repository's supported C++ standard and compiler versions, with and without usable `std::filesystem` where feasible. This is important because the header has explicit branches for C++ standard detection, MSVC language macros, GCC/libstdc++ filesystem versions, macOS deployment targets, WASI, and Windows-style option parsing.
