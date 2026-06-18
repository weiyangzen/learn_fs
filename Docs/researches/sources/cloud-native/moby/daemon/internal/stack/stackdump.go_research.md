<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump.go -->
# sources/cloud-native/moby/daemon/internal/stack/stackdump.go

Purpose: dumps all goroutine stacks to stderr or a timestamped file for diagnostics.

Important APIs and types: `Dump`, `DumpToFile`, `dump`, and constant `stacksLogNameTemplate`.

Control flow: `Dump` writes to stderr. `DumpToFile` opens a `goroutine-stacks-<timestamp>.log` file in the supplied directory or uses stderr for empty dir, then syncs/closes file and calls `dump`. `dump` repeatedly grows a buffer until `runtime.Stack` fits, then writes it.

State and persistence: writes diagnostic stack logs to disk when a directory is supplied.

Dependencies and integration: used by daemon diagnostics and signal handling paths.

Risks: file mode is 0666 subject to umask. Timestamp removes colons but can still collide if called multiple times in the same second. Dumping all goroutines may include sensitive stack data.

Test signals: `stackdump_test.go` confirms stderr path and file contains `goroutine`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/stack/stackdump.go -->
