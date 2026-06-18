# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/FsUsage.java

Purpose: implements filesystem usage commands `df`, `du`, and deprecated `dus`, with aligned table formatting.

Important APIs and types: outer `formatSize()`, `TableBuilder`, nested `Df`, `Du`, and `Dus`. `Df` reports `FsStatus`; `Du` reports `ContentSummary` length and space consumed.

Control flow: `Df` defaults to `/`, creates a six-column table, then for viewfs uses `ViewFileSystemUtil.getStatus()` to report mount-point target status and mounted-on path; non-viewfs hides the mounted-on column and reports `item.fs.getStatus()`. `Du` defaults to `.`, optionally shows headers, recurses one level for command-line directories unless summary mode is enabled, subtracts snapshot length/space under `-x`, and appends rows. `TableBuilder` computes column widths and prints aligned visible columns.

State and persistence: no filesystem mutation. Per-run state includes human-readable flag and collected table rows.

Dependencies and integration: uses `PathData`, `FsStatus`, `ContentSummary`, viewfs classes, and `StringUtils.TraditionalBinaryPrefix`.

Risks: table rows are accumulated before printing, so very large result sets can hold memory until completion. `Df` percentage divides used by size; zero-capacity filesystems need attention. Viewfs handling assumes mount target URI array has at least one element. `Du` content summaries may be expensive and only go one level deep unless inherited recursion changes.

Test signals: cover human-readable output, viewfs and non-viewfs columns, hidden column formatting, `du -s/-v/-x`, default paths, one-level directory recursion, and zero/edge capacity formatting.
