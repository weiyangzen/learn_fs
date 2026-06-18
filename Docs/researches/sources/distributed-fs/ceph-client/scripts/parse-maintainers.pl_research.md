<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/parse-maintainers.pl -->
# sources/distributed-fs/ceph-client/scripts/parse-maintainers.pl

## Purpose

`parse-maintainers.pl` extracts, sorts, and filters information from the kernel `MAINTAINERS` file. It supports category and pattern-oriented output for tooling that needs maintainership metadata.

## Important APIs, Types, and Functions

Options select input/output behavior. Functions include `usage()`, `by_category()`, `by_pattern()`, `trim()`, `alpha_output()`, and `file_input()`. The parser stores section/category lines and file pattern lines in arrays/hashes for sorted output.

## Control Flow

The script parses arguments, reads `MAINTAINERS` or stdin, tracks section headers and tagged lines, normalizes whitespace, then emits records sorted alphabetically by category or by pattern depending on mode.

## State and Persistence Behavior

State is in memory during one run. Output goes to stdout and no files are modified.

## Dependencies and Integration Points

It depends on Perl and the format conventions of the Linux `MAINTAINERS` file. It integrates with scripts and reports that need maintainer/file-pattern indexes.

## Risks and Edge Cases

The parser is tied to MAINTAINERS tag syntax. Multiline continuations, unusual section names, malformed entries, and new tag types can produce incomplete output. Sorting may lose original contextual ordering that reviewers expect.

## Test Signals

Test representative MAINTAINERS entries with multiple `M:`, `L:`, `F:`, `X:`, `N:`, malformed sections, empty sections, and category/pattern sorting modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/parse-maintainers.pl -->
