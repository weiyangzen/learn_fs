# sources/compression/xz/src/scripts/xzless.in

## Purpose
Template for `xzless`, using `less` with `LESSOPEN` to view decompressed xz-compatible files.

## Important APIs, Types, And Functions
Variables:
- `xz='@xz@ --format=auto'`.
- `LESSMETACHARS` workaround for old less versions.
- `VER` parsed from `less -V`.
- `LESSOPEN` configured differently by less version.
- `SHOW_PREPROC_ERRORS` enabled for less >= 632.

## Control Flow
The script handles `--help` and `--version`, initializes `LESSMETACHARS` if absent, parses the major less version, selects `LESSOPEN` prefix form (`||-`, `|-`, or `|`) based on version capabilities, optionally enables `--show-preproc-errors`, exports variables, and execs `less`.

## State And Persistence
Exports environment variables for the executed `less` process only.

## Dependencies And Integration Points
Configured shell/xz/package placeholders. Depends on `less` behavior and xz autodetection. Installed with script aliases by Automake.

## Risks
Version parsing assumes `less -V` output format and numeric version. `exec less $SHOW_PREPROC_ERRORS "$@"` intentionally allows the optional flag to split but depends on it being empty or one option. Preserving `XZ_OPT` can affect resource limits.

## Test Signals
Run with less versions below 429, 429-450, 451+, and 632+ if available or mocked. Test empty compressed files, stdin, file arguments, `--help`, `--version`, and inherited `LESSMETACHARS`.
