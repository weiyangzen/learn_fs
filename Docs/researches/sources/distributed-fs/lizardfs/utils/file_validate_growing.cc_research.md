# sources/distributed-fs/lizardfs/utils/file_validate_growing.cc

Purpose: validates a prefix/current length of a file that is still growing, using the same deterministic `DataGenerator` format.

Important APIs/functions: parses `<size>` with `UtilsConfiguration::parseIntWithUnit()`, ignores `SIGPIPE`, constructs `DataGenerator(seed)`, and calls `validateGrowingFile(path, FILE_SIZE)`.

Control flow: requires exactly `<file name> <size>`. On validation exception it prints the file name and exception text and exits 2; usage errors exit 1.

State and persistence: read-only. It opens the file and validates bytes through the requested size without requiring the embedded total-size header to match the current stat size.

Dependencies/integration: supports tests that read files while writers are still extending them, especially cache/coherency scenarios.

Risks and test signals: the underlying validator is sensitive to zero/too-small sizes and concurrent truncation. Because the requested size is trusted, tests should exercise sizes before and after block boundaries, partial final 8-byte words, and racing growth while validation is in progress.
