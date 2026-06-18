# sources/distributed-fs/lizardfs/utils/file_generate.cc

Purpose: command-line wrapper around `DataGenerator::createFile()` for creating one or more deterministic test files.

Important APIs/functions: reads `FILE_SIZE` and `SEED` through `UtilsConfiguration`, constructs `DataGenerator`, and calls `createFile(argv[i], FILE_SIZE)` for each path. Usage text also advertises `BLOCK_SIZE`, which is used indirectly by the generator.

Control flow: if no file paths are provided it prints usage and exits 1. Otherwise all requested files are generated sequentially; assertion failures in lower-level file operations terminate the process.

State and persistence: creates or truncates each target with mode 0644 and writes deterministic content. No rollback exists if a later file fails.

Dependencies/integration: depends on `configuration.h` and `data_generator.h`. It is useful in integration tests needing known data on mounted LizardFS volumes.

Risks and test signals: large default size is 100 MiB, so test environments must budget disk space. Test signals are multi-file generation, explicit `FILE_SIZE` units, seeded body verification, and failure on unwritable targets.
