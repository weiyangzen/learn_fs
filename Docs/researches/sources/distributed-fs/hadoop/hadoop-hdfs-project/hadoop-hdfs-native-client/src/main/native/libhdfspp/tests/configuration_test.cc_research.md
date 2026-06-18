# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/configuration_test.cc

## Purpose

This unit test exercises the generic `Configuration` and `ConfigurationLoader` XML configuration behavior used by libhdfspp.

## Important APIs, types, and functions

Tests cover degenerate XML, basic key/value reads, compact property syntax, multiple resource overlays, final-property behavior, file reads, search path formatting, default resource loading, integer/double/bool conversions, and URI conversion. It uses helpers from `configuration_test.h`, `TestUtils::TempFile`, and `TestUtils::TempDir`.

## Control flow, state, and persistence

The tests build XML strings or temporary `core-site.xml` files, clear or set loader search paths, load configurations, overlay resources or values, and assert case-insensitive key handling. Temporary files and directories are created for file-based tests and cleaned by RAII utilities. No production state persists.

## Dependencies and integration points

The file depends on `common/configuration.h`, `common/configuration_loader.h`, `hdfspp/config_parser.h` indirectly through helpers, temp-file utilities, gtest/gmock, and standard streams. It validates behavior later consumed by `HdfsConfiguration`, `hdfsBuilder`, RPC options, and URI parsing.

## Risks and test signals

Important risks are invalid XML tolerance, final-property overwrite rules, case-insensitive overlays, numeric conversion fallback, and search path normalization. The tests are broad and form the main regression suite for configuration parsing, but they also encode exact error/fallback behavior that downstream code may depend on.
