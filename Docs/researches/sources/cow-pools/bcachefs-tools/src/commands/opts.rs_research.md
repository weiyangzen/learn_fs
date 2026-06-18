# File Research: sources/cow-pools/bcachefs-tools/src/commands/opts.rs

## Purpose
Provides shared option-table utilities for command-line handling of bcachefs filesystem/device/format options exposed from the C option table.

## Main Interfaces
- Public helpers:
  - `opts_usage_str`
  - `bch_option_args`
  - `bch_opt_lookup_negated`
  - `bch_opt_lookup`
  - `bch_option_names`
  - `bch_options_from_matches`
- Crate helper:
  - `parse_opt_val`

## Behavior
- Iterates `bch2_opt_table` entries by flag filter while skipping hidden options.
- Generates formatted usage text with option type hints, string choices, and help text.
- Builds clap `Arg`s dynamically for matching bcachefs options.
- Handles boolean options with optional values and hidden negated forms such as `--nofoo`/`--no-foo`.
- Extracts selected option/value pairs from clap matches.
- Looks up option IDs by name through C `bch2_opt_lookup`.
- Parses option values with `bch2_opt_parse`, returning `None` when the option needs an open filesystem and must be deferred.

## Dependencies and Coupling
- Coupled directly to `bch_bindgen::opts::opt_table`, `c::bch2_opt_table`, and option flag/type enums.
- Uses `Printbuf` to capture C parse errors.
- Used by commands such as `image`, `migrate`, and `set_option`.

## Important Implementation Notes
- `leak` intentionally leaks dynamically generated strings to satisfy clap’s `'static` argument-name/alias requirements.
- `bch_opt_lookup_negated` accepts both `no_foo` and `nofoo` prefixes, then verifies the target option is boolean.
- `parse_opt_val` calls C parser with null filesystem context.

## Risks and Edge Cases
- Runtime-generated clap args depend on stable option table contents at startup.
- Leaked strings are process-lifetime allocations by design.
- Negated option naming can be ambiguous for option names naturally beginning with `no`.
