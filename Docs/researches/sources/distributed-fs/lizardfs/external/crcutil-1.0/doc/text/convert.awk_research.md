<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/doc/text/convert.awk -->
# sources/distributed-fs/lizardfs/external/crcutil-1.0/doc/text/convert.awk

## Purpose
This small AWK filter converts whitespace-separated input rows into a LaTeX-style table row format. It appears intended for documentation text generation, aligning the first column and emitting ampersand-separated fields followed by a LaTeX row terminator.

## Important variables and behavior
- `first_line` is initialized to `1` in `BEGIN`.
- On the first processed record, the script prints twenty leading spaces before any fields.
- For each field `i`, if it is the first field of a non-first line, it is printed in a fixed width of 20 characters without a leading ampersand.
- All other fields are printed as ` &` plus a six-character field width.
- Every input record ends with four spaces and `\\`, then `first_line` is set to `0`.

## Control flow
The script is purely streaming. AWK reads one input record at a time, loops `i = 1` through `NF`, emits formatted columns, prints the row terminator, and moves to the next input line. There are no pattern-specific branches beyond the `first_line` and first-field checks.

## State and persistence behavior
The only state is the in-memory `first_line` flag. There are no files opened by the script itself, no accumulated output, and no persistence across AWK invocations. Output goes to stdout.

## Dependencies and integration points
The script depends on a standard AWK implementation and on callers redirecting stdout to the desired documentation artifact. It integrates with crcutil's `doc/text` workflow, likely converting benchmark or tabular text data into LaTeX table rows for documentation.

## Risks and edge cases
Fields are split with AWK's default whitespace rules, so input values containing spaces cannot be preserved as a single table cell. Values wider than the fixed widths are not truncated, so alignment can drift. The script does not escape LaTeX-sensitive characters such as `_`, `%`, `&`, or `#`; callers must provide safe input or escape it earlier. Empty lines produce only the row terminator and spacing.

## Test signals
Run `awk -f convert.awk` on representative multi-row numeric/text input and verify the first row has an empty first-column pad while later rows place the first field in the 20-character slot. Include wide fields and LaTeX metacharacters in a manual test if the generated documentation will be compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/external/crcutil-1.0/doc/text/convert.awk -->
