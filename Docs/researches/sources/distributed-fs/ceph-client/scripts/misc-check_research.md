<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/misc-check -->
# sources/distributed-fs/ceph-client/scripts/misc-check

## Purpose

`misc-check` runs extra repository hygiene checks controlled by `KBUILD_EXTRA_WARN`. It catches tracked files ignored by git and mismatches between `EXPORT_SYMBOL()` use and direct inclusion of `<linux/export.h>`.

## Important APIs, Types, and Functions

`check_tracked_ignored_files()` reports tracked files that match ignore rules. `check_missing_include_linux_export_h()` finds C/header providers using export macros without including `<linux/export.h>`. `check_unnecessary_include_linux_export_h()` warns about `.c` files including the header without exporting symbols.

## Control Flow

The script exits on shell errors. If `KBUILD_EXTRA_WARN` contains `1`, it runs the git-ignore check. If it contains `2`, it runs both export-header checks. Git grep pipelines use `xargs -r` and write warnings to stderr.

## State and Persistence Behavior

It is read-only and emits warnings only. It uses `${srctree:-.}` to choose the source root.

## Dependencies and Integration Points

It depends on git, sed, xargs, grep-compatible regexes, and a git worktree. It integrates with Kbuild warning levels and source include-hygiene cleanup.

## Risks and Edge Cases

The checks require git metadata and intentionally exclude `tools/`. Regex detection can miss multiline or macro-wrapped exports and can warn on unusual generated files. It warns but does not fix ordering or include placement.

## Test Signals

Test with temporary tracked ignored files, source files with and without export macros, direct and indirect export-header use, and `KBUILD_EXTRA_WARN` combinations `0`, `1`, `2`, and `12`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/misc-check -->
