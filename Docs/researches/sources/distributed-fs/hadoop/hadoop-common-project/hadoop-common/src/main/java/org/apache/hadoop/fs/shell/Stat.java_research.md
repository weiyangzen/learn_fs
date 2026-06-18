# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/shell/Stat.java

Purpose: implements `-stat`, printing selected `FileStatus` fields according to a lightweight percent-format string.

Important APIs and types: `processOptions()`, `processPath()`, `timeFmt`, and default `format = "%y"`. Supports `%a`, `%A`, `%b`, `%F`, `%g`, `%n`, `%o`, `%r`, `%u`, `%x`, `%X`, `%y`, and `%Y`.

Control flow: parses optional `-R`, treats first argument containing `%` as the format, then requires at least one path. `processPath()` scans characters, expands recognized format sequences, drops a trailing `%`, and leaves unknown sequence letters without the `%`.

State and persistence: no mutation. Per-command state is format string and date formatter.

Dependencies and integration: extends `FsCommand`, consumes `PathData.stat`, and uses `SimpleDateFormat` for access/modification times.

Risks: formatting is not POSIX-complete; unknown escapes lose `%`, and trailing `%` is silently dropped. `SimpleDateFormat` uses default timezone despite help saying UTC dates. Format detection by `contains("%")` can misclassify path strings containing `%` as a format if placed first.

Test signals: cover all format tokens, recursive option, default format, unknown/trailing percent behavior, timezone expectations, path containing `%`, directories/files/symlinks, and multiple paths.
