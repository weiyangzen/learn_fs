# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfs_configuration_test.cc

## Purpose

This unit test validates the HDFS-specific configuration wrapper and config parser API.

## Important APIs, types, and functions

It tests `HdfsConfiguration::GetOptions()`, constants such as `kFsDefaultFsKey`, socket/retry/security keys, `ConfigurationLoader::LoadDefaultResources()`, and `ConfigParser::get_string_or()` / `ValidateResources()`.

## Control flow, state, and persistence

Tests load empty or generated XML and assert default or configured `Options` fields: default FS URI, RPC timeout, max retries, retry delay, connect timeout, and Kerberos authentication. Default resource tests create temporary `core-site.xml` and `hdfs-site.xml` combinations. Config parser tests verify successful resource validation and damaged XML error reporting.

## Dependencies and integration points

The file depends on `common/hdfs_configuration.h`, configuration helpers, temp utilities, gmock, and iostream. It connects generic configuration parsing to production `Options` consumed by `RpcEngine`, `FileSystem`, and builders.

## Risks and test signals

Risks are wrong key mapping, fallback defaults drifting, case or path sensitivity in default resource loading, and parser diagnostics changing. The damaged XML test asserts an exact exception string around character 74, which is useful for compatibility but fragile across parser changes.
