# Research: sources/cloud-native/overlaybd/src/tools/CLI11.hpp

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000267`: lines 1-6694, `Docs/researches/chunks/subset-b-000267_research.md`
- `subset-b-000268`: lines 6695-9190, `Docs/researches/chunks/subset-b-000268_research.md`

## Chunk Research

### subset-b-000267: lines 1-6694

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

### subset-b-000268: lines 6695-9190

# sources/cloud-native/overlaybd/src/tools/CLI11.hpp lines 6695-9190

## Scope And Purpose

This chunk covers the tail of the vendored CLI11 single-header implementation in `sources/cloud-native/overlaybd/src/tools/CLI11.hpp`. It starts inside `CLI::App`, covering subcommand/option dependency APIs, help/config getters, parser validation, parse execution, config/env/callback processing, argument classification and consumption, option-group support, deprecation/retirement helpers, failure-message helpers, and test accessors. It then implements the inline configuration serializer/parser and the default help formatter.

Within overlaybd this header is infrastructure for command-line tools rather than overlaybd storage logic. Its purpose is to let tools declare options, positional arguments, subcommands, option groups, validators, configuration files, environment-variable fallbacks, help/version behavior, and parse callbacks in one embedded dependency. The logic in this range is high-impact because it decides how process arguments and config files become application state, which errors are surfaced, and what text users see in help and diagnostics.

The chunk is mostly in-memory parsing and formatting code. Persistent behavior is limited to reading config streams/files through the configured `Config` object and serializing current app/option values back to a config string. Environment-variable reads are also handled here. No overlaybd files, block devices, images, or snapshots are touched by this header section.

## Important APIs, Types, And Functions

`CLI::App` is the central type. The chunk exposes relation APIs such as `excludes(Option *)`, `excludes(App *)`, `needs(Option *)`, `needs(App *)`, and their `remove_*` counterparts. These update `exclude_options_`, `exclude_subcommands_`, `need_options_`, and `need_subcommands_`. Subcommand exclusion is symmetric: adding `A.excludes(B)` also inserts `A` into `B.exclude_subcommands_`; removal mirrors that by asking the other app to remove the reverse relation.

Help and config APIs include `footer(std::string)`, `footer(std::function<std::string()>)`, `config_to_str()`, `help()`, and `version()`. `config_to_str()` delegates to `config_formatter_->to_config()`. `help()` delegates to the selected parsed subcommand if any, otherwise uses `formatter_->make_help()`. `version()` temporarily drives the version option callback by replacing its results with `"true"`, catching `CLI::CallForVersion`, and restoring the original option results afterward.

Getter APIs expose formatter/config objects, descriptions, options, named options, flags such as ignore-case/fallthrough/prefix/allow-extras/configurable/disabled/silent, requirement bounds, special option pointers, app parent/name/aliases/group, parse order, and remaining arguments. `get_option_no_throw()` recursively searches nameless subcommands, which means option groups participate in lookup. `get_option()` wraps that with `OptionNotFound`. `remaining()`, `remaining_for_passthrough()`, and `remaining_size()` expose unconsumed argument state from `missing_`, optionally recursing into parsed subcommands and nameless groups.

Protected parse machinery includes `_validate()`, `_configure()`, `run_callback()`, `_valid_subcommand()`, `_recognize()`, `_process_config_file()`, `_process_env()`, `_process_callbacks()`, `_process_help_flags()`, `_process_requirements()`, `_process()`, `_process_extras()`, `_parse()`, `_parse_stream()`, `_parse_config()`, `_parse_single_config()`, `_parse_single()`, `_parse_positional()`, `_find_subcommand()`, `_parse_subcommand()`, `_parse_arg()`, `_trigger_pre_parse()`, `_get_fallthrough_parent()`, `_compare_subcommand_names()`, and `_move_to_missing()`. These functions are the core parser pipeline.

`Option_group` extends `App` to represent nameless groups of options. Its constructor creates a nameless `App` with a group name. It exposes `add_option(Option *)` and variadic `add_options()` to move existing parent options into the group, and `add_subcommand(App *)` to move existing subcommands under the group.

Utility APIs `TriggerOn()` and `TriggerOff()` alter default startup state and install preparse callbacks so one app/subcommand enables or disables another when parsed. `deprecate_option()` and `retire_option()` attach validators that print warnings to `std::cout`; retirement replaces an existing option with a no-effect option carrying similar arity/type metadata.

`FailureMessage::simple()` and `FailureMessage::help()` are user-facing error formatters. The simple formatter prints the error text and suggests configured help flags. The help formatter prefixes an error header and appends full `app->help()`.

`detail::AppFriend` exposes selected protected parser methods to tests: `_parse_arg()`, `_parse_subcommand()`, and `_get_fallthrough_parent()`.

The inline config helpers in `CLI::detail` are `convert_arg_for_ini()`, `ini_join()`, `generate_parents()`, and `checkParentSegments()`. `ConfigBase::from_config()` parses INI/TOML-like streams into `ConfigItem` objects. `ConfigBase::to_config()` serializes current `App` option values and selected subcommands. The `Formatter` methods build default help output, including descriptions, usage, positionals, grouped options, subcommands, option names, option metadata, option descriptions, and positional usage names.

## Control Flow

Parsing starts by validating/configuring the app tree before this chunk's internals are called by public parse entry points earlier in the header. `_configure()` applies default startup modes, clears automatic names, disables fallthrough and prefix-command behavior for nameless groups to prevent infinite loops, fixes parent pointers, and recurses into subcommands. `_validate()` rejects ambiguous unlimited positionals and impossible required-option bounds, then recurses through subcommands.

The main `_parse(std::vector<std::string> &args)` path increments parse counters for the current app and nameless groups, fires the preparse callback once, and then consumes `args` from the back until `_parse_single()` stops. On the root app it runs `_process()`, checks extras, and rewrites `args` to passthrough order from `remaining_for_passthrough()`. On a subcommand with a parse-complete callback, it performs env/callback/help/requirement processing immediately and runs callbacks while suppressing the final callback. The rvalue `_parse(std::vector<std::string> &&)` variant is root-only and consumes all args before the same processing/extras pass. `_parse_stream()` parses config items from a stream, applies them, increments parsed state, and processes/extras-checks.

`_parse_single()` classifies the next token unless `positional_only` was set by `--` or `positionals_at_end_`. It handles `--` by switching to positional-only mode and optionally moving the marker into `missing_`; `++` terminates a subcommand; subcommand tokens call `_parse_subcommand()`; long/short/Windows-style options call `_parse_arg()`; everything else is attempted as positional data through `_parse_positional()`. Unknown classifier values throw `HorribleError`, which is intended as an unreachable internal failure.

`_recognize()` is the classifier. It checks `--`, valid subcommand names, long options, short options, Windows-style options when enabled, and the `++` subcommand terminator. Short numeric-looking tokens are treated as non-options unless a matching short option exists. Subcommand recognition walks up parents when current app limits are reached, allowing higher-level commands to receive subcommands after fallthrough.

`_parse_arg()` splits the token according to classifier, finds a matching option in local options, then in nameless groups, then through fallthrough parents. Missing options are either left for an option group to reject, delegated to fallthrough, or moved to `missing_`. For a found option it handles separators, trigger-on-parse reset, flag values, `--opt=value`, short-option rest values, minimum required values, optional values, `--` ending an unlimited list, default flag values for optional flags, partial type validation, trigger-on-parse callbacks, and pushing leftover short-option rest back into the argument list.

`_parse_positional()` first gives required trailing positionals priority when `positionals_at_end_` is active. It then fills local positional options that still need items or allow extra args, optionally validating each candidate. If not consumed locally, it tries nameless subcommands, fallthrough parents, repeated subcommands, and broader parent subcommand lookup. If nothing consumes the token, the value moves to `missing_`; in prefix-command mode all remaining tokens are moved to missing as passthrough payload. With `positionals_at_end_`, an unconsumed token is an immediate `ExtrasError`.

Subcommand parsing in `_parse_subcommand()` first preserves required positionals by treating the token as positional when required positionals remain. Otherwise it finds an unused enabled subcommand, pops its name, records it in `parsed_subcommands_` unless the subcommand is silent, parses it recursively, and records the subcommand through intermediate parents. If recognition said a subcommand exists but lookup fails at the root, it throws `HorribleError`.

After raw parsing, `_process()` applies config, env, callbacks, help, and requirements in a deliberate order. `_process_config_file()` reads configured config files from the config option, reverses the config file list so later provided files are processed first from the reversed iterator, checks path existence, parses config through `config_formatter_`, and applies `_parse_config()`. Config file errors are delayed enough that callbacks and help flags can take precedence. `_process_env()` fills options from environment variables only when the option was not supplied; it recurses into nameless subcommands and into subcommands without parse-complete callbacks. `_process_callbacks()` runs priority nameless groups with parse-complete callbacks first, runs option callbacks once, then recurses into subcommands without parse-complete callbacks. `_process_help_flags()` propagates help/help-all triggers down parsed subcommands and throws `CallForHelp` or `CallForAllHelp` only at the final selected subcommand.

`_process_requirements()` enforces app-level excludes/needs, required options, option-level needs/excludes, minimum selected subcommands, required-option min/max bounds including used nameless option groups, and required subcommands/groups. It skips disabled subcommands and avoids checking optional empty nameless groups when the parent min/max requirement is already satisfied. `_process_extras()` raises `ExtrasError` when `missing_` remains and neither extras nor prefix-command mode is enabled; it recurses only into subcommands that were parsed.

Config parsing has its own control flow. `ConfigBase::from_config()` reads trimmed lines, skips short/empty/comment lines, recognizes bracketed sections including TOML double brackets, emits synthetic `"++"` and `"--"` `ConfigItem`s for section opens/closes through `checkParentSegments()`, splits `name=value` lines by the configured delimiter, handles comments, handles arrays and multiline arrays, treats bare keys as boolean `"true"`, removes quotes, generates parent chains from sections and dotted names, filters by configured `configSection` and `configIndex`, and coalesces repeated same-name/same-parent items by appending inputs. `_parse_single_config()` descends through parent subcommands, treats `"++"` as entering a configurable subcommand and `"--"` as closing it, finds matching options by `--long`, `-short`, or raw name, captures or rejects extras depending on `config_extras_mode`, rejects non-configurable options unless all extras are ignored, and adds flag or value results.

Help formatting flows from `App::help()` into `Formatter::make_help()`. Normal help prints option group labels for nameless groups, description/requirement text, usage, positionals, option groups, subcommands, and footer. Sub-help mode calls `make_expanded()`, which prints a subcommand's display name, description, aliases for nameless alias groups, positionals, groups, and nested subcommands, then indents the body. `make_subcommands()` groups named subcommands by their group label in definition order and can either print compact one-line entries or expanded sub-help for all subcommands.

## State And Persistence Behavior

Most state in this chunk is mutable in-memory parse state on `App` and `Option` objects. The parser mutates `parsed_`, `pre_parse_called_`, `parsed_subcommands_`, `parse_order_`, `missing_`, option results, option callback-run state, subcommand disabled state, and parent pointers. `increment_parsed()` increments nameless groups together with their parent so option groups can participate in count/requirements.

Dependency and exclusion APIs mutate relation sets. Subcommand exclusions are stored symmetrically and removal maintains that symmetry. Needs are one-way. `clear_aliases()`, `description()`, and `footer()` mutate app metadata used later by help/config output.

Config processing persists no data by itself, but it reads from configured config files and streams via `config_formatter_`. `config_to_str()` and `ConfigBase::to_config()` serialize current option state to a string that a caller may write elsewhere. Serialization includes configurable options, grouped option comments/descriptions when requested, defaults when requested, nameless option groups inline, and named subcommands either as sections when selected/configurable or as prefix-qualified keys when not selected.

Environment processing reads process environment variables using `_dupenv_s()` on MSVC or `std::getenv()` elsewhere. It only adds an env result when the option has not already been supplied and the environment value is non-empty. This means command-line/config values take precedence over env values in this processing order.

Callbacks can mutate arbitrary user state. This chunk controls callback ordering: preparse once before consuming an app, parse-complete callbacks at configured boundaries, option callbacks before non-priority subcommand callbacks, and final app callbacks bottom-up through parsed subcommands and used option groups. Immediate callback mode can clear a named app between parses while preserving parse count and missing extras.

`retire_option()` mutates the app option set by removing an existing option and adding a replacement option with warning validation and matching arity characteristics. `Option_group::add_option()` moves the owning `unique_ptr` for an option from the parent into the group through `_move_option()`. `_move_option()` refuses to move help, help-all, or config options and rejects duplicate-equivalent options in the destination group.

No durable overlaybd state is affected. The main persistence-relevant risk for overlaybd tools is user-facing: incorrect parsing could change which CLI options, config options, env values, or subcommands are accepted before a tool reaches its actual overlaybd operations.

## Dependencies And Integration Points

This code depends on the rest of the CLI11 header for `Option`, `App`, `Config`, `ConfigBase`, `FormatterBase`, `Formatter`, `ConfigItem`, `Validator`, `Error` subclasses, `detail::Classifier`, string splitting/normalization helpers, path checking, lexical casting, and formatting helpers. It also depends on the C++ standard library for containers, smart pointers, streams, algorithms, callbacks, environment access, and `std::cout`.

Overlaybd integration is by inclusion. Tool source files can instantiate `CLI::App`, add options/subcommands, configure config files/env vars, and call parse methods. The state produced here is then read by tool-specific logic. Because this is a vendored header, upstream CLI11 behavior and local overlaybd expectations are coupled: changing this file changes every tool that compiles against it.

The config integration point is `config_formatter_`, usually a `Config`/`ConfigBase` implementation with configurable delimiters, quote chars, section filtering, parent separator, array syntax, and maximum layer depth. The code supports INI-like arrays, TOML-like double-bracket sections, dotted parent paths, bare boolean keys, and generated section enter/exit sentinels.

The help integration point is `formatter_`, a `FormatterBase` implementation. The default `Formatter` in this chunk uses `App` and `Option` getters to construct help text. Apps can replace the formatter elsewhere in the header; `Formatter::make_help()` also forwards sub-help formatting so subcommands can use overridden formatter behavior.

The parser integrates with process environment via option `envname_`, with filesystem path checks through `detail::check_path()` for config files, with exception-based control flow through CLI11 errors (`FileError`, `ConfigError`, `RequiredError`, `ExtrasError`, `ArgumentMismatch`, `CallForHelp`, `CallForAllHelp`, `CallForVersion`, `HorribleError`), and with tests through `detail::AppFriend`.

## Risks And Edge Cases

Subcommand exclusion error text says `"cannot self reference in needs"` even in `excludes(App *)`. That is minor but can mislead users or tests expecting an excludes-specific diagnostic.

`check_name()` applies `detail::to_lower(name_)` to the original member after underscore removal assigned `local_name`. When both ignore-underscore and ignore-case are enabled, the local name case-folding path appears to ignore the underscore-stripped intermediate and lowercases `name_` again. If `detail::to_lower()` does not also remove underscores, a name that should match under both options could fail. Alias handling applies transforms sequentially to the alias copy and does not share that issue.

`version()` mutates the version option results to run its callback and then restores them. This is careful but still observable if a callback inspects broader app state or has side effects beyond throwing `CallForVersion`. Tests should treat version callbacks as executable logic, not pure string access.

`_process_config_file()` catches only `FileError` around config processing. Other config parse or option callback exceptions propagate immediately. This ordering is intentional for file-not-found versus help/callback precedence, but it means malformed config content can suppress later help flag handling depending on where the error is thrown.

Environment processing ignores empty environment variables. For string options where empty is meaningful, users cannot set an empty value through the environment path in this implementation.

`_parse_arg()` consumes the minimum number of following tokens without first classifying them. That is normal CLI11 behavior for required option arguments, but it means a required argument can consume a token that looks like an option or subcommand. Optional argument collection is more conservative and only consumes classifier `NONE` tokens.

Unlimited or large-vector option handling adjusts `max_num` based on type size and expected minimum unless `allow_extra_args` is set. Edge cases around container options, partial tuple-like types, optional validation, and `--` termination need focused tests because off-by-one errors here can change parse boundaries.

`_parse_positional()` has several fallback paths: nameless groups, fallthrough parent, repeated local subcommands, broader parent subcommands, missing capture, and prefix-command passthrough. This is flexible but sensitive to `fallthrough_`, `positionals_at_end_`, required positional counts, and `require_subcommand_max_`. A small flag change can redirect the same token from positional value to subcommand to extras.

`_process_requirements()` returns early for an app that is excluded or missing a needed dependency when the app itself received no input. That avoids raising errors for inactive optional groups, but can hide configuration mistakes until a related option/subcommand is actually used.

`_trigger_pre_parse()` in immediate callback mode clears named app state after subsequent parses while preserving `parsed_` and `missing_`. This helps repeated subcommand parsing, but callbacks or external code retaining option result pointers must account for state reset.

`ConfigBase::from_config()` skips trimmed lines shorter than three characters, so very short bare keys or `a=`-style entries are ignored. This likely follows CLI11 assumptions but can surprise users expecting one-letter config keys.

Config comment stripping uses `item.find(commentChar)` without quote awareness. Values containing the comment character inside quotes can be truncated before quote removal. Similarly, multiline array accumulation appends trimmed lines without inserting separators or spaces, relying on the input syntax already containing separators.

`ConfigBase::to_config()` emits named subcommand sections only when the subcommand is configurable and was parsed. Unparsed configurable subcommands are serialized as prefix-qualified keys. This distinction can affect round-tripping of default config templates.

`Formatter::make_description()` has user-visible text nits: `"Exactly Noptions"` lacks a space and `"follow options"` is grammatically off. These do not affect parsing but can be asserted in help-output tests.

`Formatter::make_expanded()` does `tmp.substr(0, tmp.size() - 1)` after replacing blank lines. If the accumulated string were empty, this would underflow. In normal use the display name line makes it non-empty, but custom formatter interactions or unusual nameless state should keep that invariant in mind.

`deprecate_option()` and `retire_option()` print warnings to `std::cout` from validators. That can pollute stdout for tools whose stdout is machine-readable unless callers deliberately avoid deprecated/retired options or redirect diagnostics.

## Test Signals

Parser tests should cover long, short, combined short-rest, Windows-style, flag, required-value, optional-value, vector, tuple-like, unlimited, `--`, and prefix-command arguments. Assertions should include option results, `parse_order()`, `remaining()`, `remaining_for_passthrough()`, and exact exception types for extras and argument mismatches.

Subcommand tests should cover aliases, ignore-case, ignore-underscore, both ignore modes together, disabled subcommands, silent subcommands, repeated subcommands, `require_subcommand_min_` and max handling, fallthrough through nameless groups, `++` subcommand terminators, and parent recording through nested option groups.

Requirement tests should cover app-level `needs()` and `excludes()` for both options and subcommands, symmetry of subcommand excludes and `remove_excludes(App *)`, inactive optional option groups, required option groups, option-level needs/excludes, and min/max option counts including nameless groups counted as used options.

Config tests should parse sections, nested dotted sections, TOML double brackets, repeated sections with `configIndex`, `configSection` filtering, repeated keys, multiline arrays, default arrays, INI arrays, bare boolean keys, quoted parent/name segments, too-deep parent chains, `"++"`/`"--"` section sentinel behavior, captured config extras, ignored extras, and non-configurable option errors. Round-trip tests should compare `config_to_str()` output with reparsed app state for selected subcommands and defaults.

Environment tests should verify precedence: command-line/config-provided options are not overwritten by env vars, env vars populate missing options, empty env vars are ignored, and nameless groups/subcommands without parse-complete callbacks receive env processing.

Callback tests should validate preparse call count and remaining-arg value, parse-complete ordering, priority option-group callbacks, option callback run-once behavior, trigger-on-parse behavior, immediate callback state clearing, final callback bottom-up order, and suppression of final callbacks in parse-complete subcommand paths.

Help and failure-message tests should assert normal help, all-subcommand help, sub-help expansion, grouped options, positionals, hidden help pointers in sub mode, footer string plus callback footer ordering, version callback restoration, simple failure help-flag suggestions, and full failure help output.

Option-group tests should move existing options and subcommands into groups, reject moving help/config options, reject duplicate-equivalent moved options, verify parent pointers after moves/configure, and ensure grouped options still resolve through `get_option_no_throw()`.

Deprecation/retirement tests should capture stdout, verify warnings are emitted when deprecated or retired options are parsed, check replacement descriptions/default/type names, and confirm retired options consume the same arity shape without mutating the original removed option target.

For overlaybd command-line tools specifically, integration tests should run representative tool binaries with CLI args, config files, and env vars that map to real tool options, then verify the parsed values before any storage operation runs. This catches vendored CLI11 behavior changes at the boundary where overlaybd code consumes parser state.
