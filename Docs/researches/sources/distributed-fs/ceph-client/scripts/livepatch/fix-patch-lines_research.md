# sources/distributed-fs/ceph-client/scripts/livepatch/fix-patch-lines

## Purpose
`fix-patch-lines` is an awk filter that inserts `#line` directives into C/header patch hunks so compiled patched code preserves original `__LINE__` values where possible.

## Important APIs, Types, and Functions
It tracks `in_hunk`, `skip`, old-file current line `cur`, hunk end `last`, and `need_line_directive`. It recognizes `--- ` file headers, `@@` hunk headers, changed lines, context lines, and `\ No newline at end of file`.

## Control Flow
For non-C/header files, it prints lines unchanged. For C/header hunks, it parses the old-file line range from the hunk header. After each group of added/removed lines, before the next context line, it emits `+#line <cur>` into the patch, then resumes copying and updating the old-line counter.

## State and Persistence
All state is streaming awk state; no files are written directly by the script.

## Dependencies and Integration Points
Used in livepatch tooling pipelines that transform unified diffs before compilation. Depends on awk with `match(..., array)` support.

## Risks and Edge Cases
Only `.c` and `.h` files are processed. Hunk header parsing must match standard unified diff format. The inserted directive is an added line in the patch and may interact with style checks or unusual preprocessor contexts.

## Test Signals
Feed patches with additions, removals, mixed hunks, non-C files, one-line hunks, and no-newline markers; verify generated patched source reports original line numbers.
