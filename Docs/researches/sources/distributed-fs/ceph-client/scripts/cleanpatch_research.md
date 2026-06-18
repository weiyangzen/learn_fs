# sources/distributed-fs/ceph-client/scripts/cleanpatch

## Purpose
`cleanpatch` rewrites unified patch files in place, cleaning only added lines while preserving context and removed lines, and adjusts hunk headers when trailing added blank lines are removed.

## Important APIs, Types, and Functions
It shares `clean_space_tabs()` and `strwidth()` logic with `cleanfile`. The parser tracks hunk headers matching `@@ -start,count +start,count @@`, `$minus_lines`, `$plus_lines`, and `@hunk_lines`. Width warnings are emitted for added text lines only.

## Control Flow and State
For each regular, non-binary file, the script alternates between outside-hunk passthrough and inside-hunk processing. Added lines are cleaned, removed/context lines decrement hunk counters, malformed structure sets an error and prevents rewriting. At hunk end it removes trailing added blank lines and rewrites the plus-line count. Persistence is in-place file replacement through seek, print, and truncate.

## Dependencies and Integration
It depends on Perl and unified diff syntax. It is used as a developer patch cleanup tool before submission.

## Risks and Test Signals
Only strict hunk headers with explicit counts are accepted. It does not preserve malformed patches and can destructively modify valid but unusual diffs. Test clean added lines, unchanged context, trailing added blank removal, malformed hunks, zero-length hunks, binary detection, and width warnings.
