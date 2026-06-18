# sources/distributed-fs/lizardfs/utils/file_overwrite.cc

Purpose: command-line wrapper around `DataGenerator::overwriteFile()` for rewriting existing files with deterministic content while preserving their current size.

Important APIs/functions: reads `SEED` and `BLOCK_SIZE` through shared utilities, constructs a `DataGenerator`, and overwrites each file named on the command line.

Control flow: requires at least one path. For each file it stats the file to get size, opens it write-only, and writes the deterministic header/body pattern for that size. Lower-level assertions abort on stat/open/write/close failures.

State and persistence: mutates files in place and leaves their length unchanged because `overwriteFile()` opens without `O_TRUNC` and writes exactly `st_size` bytes. Existing content is fully replaced for regular files of at least eight bytes.

Dependencies/integration: paired with `file_generate` and `file_validate` in filesystem tests that want data churn without changing metadata size.

Risks and test signals: regular-file semantics are assumed; sparse files, concurrent writers, or files smaller than the 8-byte header can trigger assertion failures or partial writes. Test signals are preserving file size, validating overwritten content with the same seed, and expected failure on missing or read-only files.
