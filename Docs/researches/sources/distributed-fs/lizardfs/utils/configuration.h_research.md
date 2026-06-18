# sources/distributed-fs/lizardfs/utils/configuration.h

Purpose: small utility configuration facade used by test binaries. `UtilsConfiguration` extends `devtools/configuration.h` and centralizes environment-driven values for generated file tests.

Important APIs/types: `blockSize()` reads `BLOCK_SIZE` with unit support and defaults to 64 KiB. `fileSize()` reads `FILE_SIZE` with unit support and defaults to 100 MiB. `repeatAfter_ms()` reads `REPEAT_AFTER_MS` and defaults to zero. `seed()` reads `SEED` and defaults to zero. The class publicly re-exports `Configuration::parseIntWithUnit` and `Configuration::parseInt` for command-line utilities.

Control flow: all methods are static wrappers over `getIntWithUnitOr()` or `getIntOr()`. There is no object state and no initialization order beyond the included configuration helper.

State and persistence: values are process-local reads from environment variables or explicit strings. Nothing is persisted.

Dependencies/integration: used by `data_generator.h` clients: `file_generate.cc`, `file_overwrite.cc`, `file_validate.cc`, and `file_validate_growing.cc`. It depends on the broader LizardFS devtools configuration parser, signal/system headers only indirectly, and standard C++ streams.

Risks and test signals: risks are inherited from environment parsing: invalid units, oversized values, or zero/small sizes that violate `DataGenerator` assumptions. Test signals are default behavior with no environment, unit parsing for sizes, `REPEAT_AFTER_MS` cache validation delay, and seeded deterministic generation.
