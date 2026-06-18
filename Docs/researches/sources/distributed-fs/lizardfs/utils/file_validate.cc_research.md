# sources/distributed-fs/lizardfs/utils/file_validate.cc

Purpose: command-line validator for files produced by `DataGenerator`.

Important APIs/functions: installs `SIGPIPE` ignore, reads `REPEAT_AFTER_MS` and `SEED`, then calls `DataGenerator::validateFile()` for each supplied path. Validation errors are caught per file and printed as `File <path>: <exception>`.

Control flow: no arguments prints usage and exits 1. Any validation failure sets aggregate return code 2, but later files are still checked. Repeat validation mode intentionally swallows an initial exception, sleeps, seeks back to start, and performs a decisive second validation.

State and persistence: read-only except for timing effects. It opens each file and closes it after validation.

Dependencies/integration: depends on `configuration.h`, `data_generator.h`, POSIX signal handling, and expected generated-file format. It is a test assertion binary for filesystem correctness.

Risks and test signals: first-pass errors are hidden when `REPEAT_AFTER_MS > 0`, so logs may not show transient corruption if the second pass succeeds. Test signals are clean files, corrupted header size, corrupted body byte, repeat-after cache behavior, multiple input aggregation, and SIGPIPE-safe use in pipelines.
