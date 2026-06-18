# `sources/user-network-fs/mergerfs/vendored/CLI11/CLI11.hpp` lines 6824-12216

## Purpose

This chunk contains the central inline implementation and public surface for CLI11's command-line application model. It starts by finishing `Option` result reduction, validation, and string-to-result expansion, then defines the `CLI11_PARSE` convenience macro, `App` and `Option_group`, the command/subcommand parse engine, config-file read/write helpers, failure-message helpers, and the default help `Formatter`.

Within the vendored mergerfs tree this is third-party CLI parsing infrastructure. Local mergerfs code uses it indirectly by including `CLI11.hpp` and building `CLI::App` instances with options, flags, subcommands, config files, environment fallbacks, validators, and callbacks. The covered range is behavioral code, not merely declarations: it owns the parse state machine and the ordering rules that decide when callbacks, help/version exits, config files, environment variables, requirements, and extras are processed.

## Important APIs, Types, and Functions

The `Option` helpers at the start of the chunk are internal but shape nearly every option parse result:

- `Option::_reduce_results(results_t &out, const results_t &original)` applies `MultiOptionPolicy`. `TakeLast`, `Reverse`, and `TakeFirst` trim to the expected item count; `Join` joins original strings with the configured delimiter or newline; `Sum` numeric-sums string values; `Throw` enforces min/max counts. It also handles the special config empty-container sentinel `{}` plus `%%`.
- `Option::_validate(std::string &result, int index)` runs validators whose application index is either global `-1` or matches the input index. It returns the first error string, converting thrown `ValidationError` to text.
- `Option::_add_result(std::string &&result, std::vector<std::string> &res)` expands parsed strings into result elements. It recognizes escaped bracket vectors of the form `[[...]]` with duplicated characters, bracketed vector strings split by comma, and delimiter-separated values.

`detail::Classifier` is the parse-token category enum used by `App::_recognize` and `App::_parse_single`: `NONE`, `POSITIONAL_MARK`, `SHORT`, `LONG`, `WINDOWS_STYLE`, `SUBCOMMAND`, and `SUBCOMMAND_TERMINATOR`.

The extras and prefix enums drive unknown-argument behavior:

- `ExtrasMode` supports hard errors, immediate errors, ignore, capture, and two "assume following args" modes.
- `ConfigExtrasMode` / `config_extras_mode` decide whether unknown config keys error, ignore, ignore all not-configurable keys, or are captured into `missing_`.
- `PrefixCommandMode` controls command-wrapper behavior where an unrecognized token stops CLI11 parsing and leaves the rest for a downstream executable.

`CLI::App` is the core command/subcommand object. Its state includes:

- Basic identity and callback fields: `name_`, `description_`, `has_automatic_name_`, `required_`, `disabled_`, `pre_parse_callback_`, `parse_complete_callback_`, and `final_callback_`.
- Option storage and defaults: `option_defaults_`, `options_`, `help_ptr_`, `help_all_ptr_`, `version_ptr_`, and `config_ptr_`.
- Parse state: `missing_`, `parse_order_`, `parsed_subcommands_`, `parsed_`, and requirement/exclusion sets for options and subcommands.
- Subcommand behavior: `subcommands_`, `ignore_case_`, `ignore_underscore_`, `fallthrough_`, `subcommand_fallthrough_`, `allow_windows_style_options_`, `positionals_at_end_`, `configurable_`, `validate_positionals_`, `validate_optional_arguments_`, `silent_`, `allow_non_standard_options_`, and `allow_prefix_matching_`.
- Formatting and config dependencies: `formatter_` defaults to `Formatter`, and `config_formatter_` defaults to `ConfigTOML`.

Public `App` APIs in this range include callback setup, parser mode setters, option and flag creation, config option setup, subcommand creation/removal, option groups, requirements/exclusions, help and version generation, accessors, `parse(...)` overloads for argc/argv, strings, vectors, wide strings, and streams, and `exit(...)` for converting `ParseError` subclasses into output and exit codes.

The typed `add_option` templates convert CLI string results into user variables using `detail::lexical_conversion`, derive type names/counts from type traits, install default-string capture callbacks, and configure expected argument counts. Flag APIs route through `_add_flag_internal`, which strips default flag-value annotations from names when present, rejects positional flags, sets `MultiOptionPolicy::TakeLast`, expected count zero, and non-required status. Integral counting flags use `MultiOptionPolicy::Sum`.

`Option_group` subclasses `App` with an empty app name and group label. It lets callers move existing options and subcommands under a group while preserving ownership in the underlying `App_p` vectors. Groups whose names are empty or start with `+` remove inherited help flags and participate specially in option lookup/help expansion.

Helper APIs `TriggerOn`, `TriggerOff`, `deprecate_option`, and `retire_option` mutate app/option behavior. Trigger helpers install preparse callbacks that enable or disable other apps. Deprecation and retirement are implemented by adding validators that print warnings to `std::cout`; retirement replaces or creates an inert option with type/default text `"RETIRED"`.

`FailureMessage::simple` and `FailureMessage::help` are the default error formatting hooks. `simple` emits the error text plus a help flag suggestion; `help` emits an `ERROR:` header and full help output.

Config helpers implement both parsing and serialization:

- `detail::convert_arg_for_ini` quotes, escapes, or preserves strings based on whether they look like booleans, numbers, hex/octal/binary literals, printable text, binary data, or long multiline values.
- `detail::ini_join` joins vector results using config array delimiters.
- `detail::generate_parents`, `detail::checkParentSegments`, `detail::hasMLString`, and `detail::find_matching_config` maintain nested section parent paths and duplicate-key merging.
- `ConfigBase::from_config` parses INI/TOML-like streams into `ConfigItem` entries.
- `ConfigBase::to_config` serializes current app/option/subcommand state back to config text.

`Formatter` methods at the end generate default help text: descriptions, usage, positionals, option groups, subcommand groups, expanded subcommand help, option names/options/descriptions, and positional usage fragments.

## Control Flow

Top-level `parse` setup is consistent across overloads. The argc/argv overload records an automatic app name from `argv[0]` if needed, reverses command-line arguments into a vector, and calls `parse(vector)`. String parsing optionally extracts a program name, escapes quoted values after `=` or Windows-style `:`, splits shell-like text, removes quotes, reverses arguments, and calls `parse(vector)`.

`parse(vector)` and `parse(vector&&)` clear previous parse data if needed, temporarily mark `parsed_` so cleanup happens if validation/configuration throws, then run `_validate()`, `_configure()`, detach the root from any parent, reset `parsed_`, and enter `_parse`. `parse_from_stream` skips command-token parsing and feeds config items directly into `_parse_config`.

The command-token state machine is:

1. `_parse` increments parse counts for the current app and nameless groups, triggers preparse once, and loops while args remain.
2. `_parse_single` classifies the next token with `_recognize`, then dispatches to positional mark handling, subcommand parsing, option parsing, or positional parsing.
3. `_recognize` checks `--`, valid subcommands, long options, short options, numeric-looking short-token exceptions, Windows-style options, `++` subcommand terminators, and dotted subcommand notation.
4. `_parse_subcommand` resolves the subcommand, supports dotted notation, records non-silent parsed subcommands, recurses into the child app, and propagates parsed-subcommand state through intermediate parents.
5. `_parse_arg` splits long/short/Windows tokens, finds a local option, searches nameless subcommands, supports non-standard short names, supports dotted subcommand option notation, falls through to parents when enabled, captures unknown options into `missing_`, or consumes option values according to min/max/type-size rules.
6. `_parse_positional` assigns a positional to the first eligible positional option, optionally validating before assignment. If no local positional can consume it, it tries nameless subcommands, fallthrough parents, repeated subcommands, subcommand fallthrough, extras handling, and prefix-command capture.

Option value collection is sensitive to arity. `_parse_arg` handles flag-like zero-argument options through `get_flag_value`, `--long=value`, short rest values such as `-Trest`, required minimum positional values, optional values while the next token is `NONE`, `--` ending an unlimited list, flag defaults when optional values are omitted, partial tuple/type errors, and `trigger_on_parse` callbacks. It leaves unused short-token rest back on the arg stack as a new short option.

After token parsing, root `_parse` runs `_process`, then `_process_extras`. `_process` deliberately stages callbacks and help checks by `CallbackPriority`: `FirstPreHelp`, help at `First`, `First`, config/env processing, `PreRequirementsCheckPreHelp`, help at `PreRequirementsCheck`, requirements, `NormalPreHelp`, help at `Normal`, `Normal`, delayed config-file exception rethrow, `LastPreHelp`, help at `Last`, and `Last`. This gives help/version and callback priorities predictable precedence over config-file failures and requirement checks.

For subcommands with `parse_complete_callback_`, `_parse` runs a reduced process pipeline immediately at subcommand parse completion, including env processing and requirements, then calls `run_callback(false, true)` to suppress the final callback until the main callback pass.

Config parse flow starts with `ConfigBase::from_config`, which scans lines, ignores short/comment/multiline-comment blocks, opens and closes sections with synthetic `++` and `--` items, handles multiline quoted values, arrays, whitespace/comma splitting, quoted string unescaping, parent-path extraction, duplicate merging with `%%` separators, maximum-layer filtering, and optional config-section filtering. `App::_parse_config` feeds each `ConfigItem` through `_parse_single_config`, erroring on unknown keys only in `ConfigExtrasMode::Error`.

`_parse_single_config` descends through `item.parents`, handles `++` section-open by incrementing parsed/configurable subcommands and recording them in the parent, handles `--` section-close with parse-complete callbacks, resolves configurable options by long, short, positional, or predicate search, captures unknown config extras when enabled, converts flag-like config items through `_add_flag_like_result`, and otherwise adds inputs then runs the option callback.

Help flow starts in `App::exit` or `_process_help_flags`. A help flag throws `CallForHelp`, all-help throws `CallForAllHelp`, and version throws `CallForVersion`. `exit` routes those to `help()`, all-help `help("", AppFormatMode::All)`, or `e.what()`. `App::help` delegates to the last selected subcommand so nested help describes the active leaf command; otherwise it calls the configured formatter.

## State and Persistence Behavior

Most state is process-local parse state inside `App` and `Option` objects. `clear()` resets `parsed_`, `pre_parse_called_`, `missing_`, `parsed_subcommands_`, `parse_order_`, every option, and all subcommands. `_configure()` reapplies startup enable/disable defaults, clears automatically generated names for child apps, disables fallthrough/prefix mode on nameless groups to avoid loops, and restores parent pointers before each parse.

`App` owns options and subcommands by `std::shared_ptr` (`Option_p` and `App_p`) but exposes raw pointers for user-facing APIs. Removal routines clean dependency links before erasing owning pointers. `_move_option` transfers ownership from a parent app to a subcommand/option group, rejecting help and config options.

Persistent external state is limited to explicit config-file and environment interactions. `_process_config_file` checks path type and reads config files through the configured `Config` object. `_process_env` reads environment variables for options that were not set by command line/config. `ConfigBase::to_config` produces a string representation but does not write files itself. `ensure_utf8` on Windows stores normalized argument strings and a parallel `char *` view inside the `App`; on non-Windows it returns the original pointer unchanged.

Callback helpers and deprecation/retirement warnings write to `std::cout`, while parse exit formatting writes to caller-provided `out`/`err` streams. No network, database, or long-lived cache behavior exists in this chunk.

## Dependencies

This code depends heavily on the earlier parts of the same header:

- `Option`, `OptionDefaults`, `FormatterBase`, `Formatter`, `FormatterLambda`, `Config`, `ConfigBase`, `ConfigTOML`, `ConfigItem`, `Validator`, `results_t`, `callback_t`, `MultiOptionPolicy`, `CallbackPriority`, and `AppFormatMode`.
- Error types such as `ParseError`, `ValidationError`, `ArgumentMismatch`, `ConversionError`, `RequiredError`, `RequiresError`, `ExcludesError`, `ExtrasError`, `ConfigError`, `FileError`, `IncorrectConstruction`, `OptionAlreadyAdded`, `OptionNotFound`, `CallForHelp`, `CallForAllHelp`, `CallForVersion`, `RuntimeError`, `InvalidError`, and `HorribleError`.
- `detail` utilities for string splitting, quoting, lexical conversion, flag values, path checks, environment reads, Windows narrowing/normalization, name validation, joins, paragraph formatting, binary escaping, and expected-count/type-count traits.

Standard-library dependencies include strings, vectors, sets, shared pointers, function objects, streams/stringstreams, algorithms, locale/ctype checks, exceptions, and iostreams. `_WIN32` gates Windows UTF-8 argv normalization and the default for Windows-style `/option` parsing.

## Integration Points

The primary integration contract is the public `CLI::App` API used by mergerfs command setup code. Callers create an `App`, add typed options/flags/subcommands, set config/env/help/version behavior, call `parse`, and then read bound variables or execute callbacks.

Config integration is two-way. Apps can set a config option with `set_config`; during processing, config file names may come from CLI arguments, default values, or an environment variable on the config option. Config items are parsed into the same option result/callback pipeline as command-line values. `config_to_str` serializes current values using `ConfigBase::to_config`, including configurable subcommands and option groups.

Help integration is formatter-pluggable. `App::formatter` accepts a `FormatterBase`, and `formatter_fn` wraps a callback in `FormatterLambda`. The default formatter queries `App` and `Option` getters, so changing option metadata affects usage/help output without changing formatter code.

Subcommand integration is hierarchical. Parent settings marked inheritable are copied in the child constructor, including option defaults, failure message, extras modes, prefix mode, immediate callback mode, case/underscore matching, fallthrough, validators for positionals/optional arguments, configurability, Windows-style options, group, usage/footer, formatter/config formatter, max subcommands, and prefix matching.

Testing integration is explicit through `detail::AppFriend`, which exposes protected parse helpers and fallthrough-parent lookup for tests while keeping those methods hidden from the normal public API.

## Risks and Edge Cases

- Pointer lifetime is easy to misuse. User-facing APIs return raw `Option *` and `App *` backed by vectors of `shared_ptr`; `remove_option`, `remove_subcommand`, and `_move_option` can invalidate previously saved raw pointers.
- Many behaviors depend on reversed argument vectors. External callers using `parse(std::vector<std::string> &args)` must pass a reversed vector as documented; otherwise parse order and leftovers are wrong.
- Dotted subcommand notation mutates the argument stack and has rollback paths. Bugs here can misroute options between parent and child apps, especially with short-option rest splitting.
- `ignore_case`, `ignore_underscore`, aliases, option groups, non-standard options, and prefix matching all widen match equivalence. The code performs conflict checks, but these settings can still create ambiguous UX, especially across nameless option groups and fallthrough parents.
- Config parsing is permissive and feature-rich: multiline strings, arrays, duplicate fields, section nesting, `++`/`--` synthetic items, `%%` separators, and quote rules all interact. Small changes to escaping or duplicate merging can change callbacks and option counts.
- The `{}` plus `%%` sentinel is a special empty-container escape used in option reduction/config output. Treating it as ordinary user data can make empty vectors and literal `"{}"` indistinguishable unless the guard paths stay intact.
- `deprecate_option` and `retire_option` warnings print directly to `std::cout` from validators. Applications that expect all diagnostics on `stderr` or caller-provided streams may get surprising output.
- Config-file `FileError` is intentionally delayed so callbacks/help/requirements can win. Tests that assert exact exception ordering need to account for this staged rethrow.
- `App::version()` temporarily clears and re-adds results on the version option to force the version callback, so custom callbacks with side effects could observe a synthetic state.
- `TriggerOn` and `TriggerOff` replace the target app's startup mode and the trigger app's preparse callback. A later `preparse_callback` assignment can overwrite trigger behavior because only one callback is stored.
- `ConfigBase::from_config` silently skips entries deeper than `maximumLayers` and short lines under three characters. That is intentional, but malformed or minimal config keys can disappear rather than error.

## Test Signals

Useful test coverage for this chunk should exercise behavior rather than only compiling the header:

- Parse a simple `App` with typed options, flags, counting flags, default flag values, repeated options under every `MultiOptionPolicy`, delimiter-split values, and validators with application indexes.
- Verify option arity errors: too few, too many, partial tuple/type, optional values stopping before required positionals, unlimited vector termination with `--`, and `positionals_at_end` extras errors.
- Cover subcommands with aliases, case/underscore-insensitive matching, prefix matching, silent subcommands, repeated subcommands, `require_subcommand`, named and nameless option groups, fallthrough, and subcommand fallthrough.
- Assert callback priority ordering with help/version/config/env/requirements. Include delayed config-file failure where a help flag or higher-priority callback wins.
- Test `parse_complete_callback_` and `immediate_callback_` on nested subcommands, including the clear-and-reparse behavior in `_trigger_pre_parse`.
- Exercise config files with nested sections, configurable subcommands, `++` and `--` section markers, unknown keys under every `ConfigExtrasMode`, duplicate fields, arrays, multiline quoted strings, literal `"{}"`, empty containers, and environment-sourced config file names.
- Round-trip `config_to_str` for normal options, flag aliases/default flag values, `Join`, `Sum`, `Reverse`, default values, required placeholders, option descriptions, option groups, configurable subcommands, and key names requiring quotes.
- Check help output for usage, positionals, grouped options, hidden help flags in subcommand mode, all-help expanded subcommands, aliases on display names, required labels, env/needs/excludes annotations, custom usage/footer callbacks, and paragraph formatting.
- Verify `remove_option`, `remove_subcommand`, `remove_needs`, `remove_excludes`, and `Option_group::add_option/add_subcommand` clean links and preserve ownership without leaving dangling dependency relationships.
