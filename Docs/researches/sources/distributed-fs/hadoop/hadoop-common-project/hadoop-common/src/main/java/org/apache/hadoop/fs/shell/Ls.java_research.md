# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Ls.java

Purpose: implements `-ls` and deprecated `-lsr`, listing files/directories with formatting, sorting, recursion, path-only output, printable-name filtering, and optional erasure coding policy.

Important APIs and types: `processOptions()`, visible-for-testing flag getters, `processPathArgument()`, `isSorted()`, `getListingGroupSize()`, `processPaths()`, `processPath()`, `adjustColumnWidths()`, and `initialiseOrderComparator()`.

Control flow: options set recursion, directory-as-file behavior, human-readable sizes, non-printable filtering, sort order, atime display, and EC policy display. Default path is `.`. Command-line directories are implicitly recursed once unless `-d` is specified. `processPaths()` prints item counts for nonrecursive directory listings, sorts as needed, updates column widths, and delegates item output. `processPath()` prints either only path or a formatted line with type, permissions, ACL marker, replication, owner, group, optional EC policy, size, date, and path.

State and persistence: no mutation. Formatting widths and comparator are instance state and grow across processed groups.

Dependencies and integration: uses `PathData`, `FileStatus`, `ContentSummary` for EC policy, `PrintableString`, `StringUtils.TraditionalBinaryPrefix`, and inherited recursive listing from `FsCommand`/`Command`.

Risks: EC policy display calls `getContentSummary()` for each path and rejects filesystems that return null on the initial argument. Width state can persist across groups in one command run. Recursive listing uses group size 100 unless path-only; sorting falls back to non-iterator paths when explicit sorting or summary printing is needed. `-S` is ignored when `-t` is also set due precedence.

Test signals: cover default output, `-C`, `-d`, `-R`, `-h`, `-q`, `-t`, `-S`, `-r`, `-u`, `-e`, lsr replacement, ACL marker, EC unsupported path, recursive grouping, and comparator precedence.
