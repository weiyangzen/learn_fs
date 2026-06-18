# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestAwsClientConfig.java

## Purpose
`TestAwsClientConfig` unit-tests `AWSClientConfig`, especially duration/default handling and custom request header parsing for different AWS service clients.

## Important APIs, Types, and Functions
- Extends `AbstractHadoopTestBase`.
- `teardown()` resets `AWSClientConfig` minimum operation duration.
- `conf()` creates a configuration with no default/site XML loading.
- Tests call `createConnectionSettings()`, `createApiConnectionSettings()`, `createClientConfigBuilder()`, and `ConfigurationHelper.enforceMinimumDuration()`.
- Header tests target `CUSTOM_HEADERS_S3`, `CUSTOM_HEADERS_STS`, `AWS_SERVICE_IDENTIFIER_S3`, and `AWS_SERVICE_IDENTIFIER_STS`.

## Control Flow
Duration tests verify minimum enforcement, default connection settings from an empty config, minimum duration winning for selected network operations, zero-minimum fields retaining configured values, and API request timeout propagation/defaults. Header tests set S3 or STS custom header strings, build client override configurations for both services, and verify headers are applied only to the targeted service, with whitespace trimming and duplicate values preserved.

## State and Persistence Behavior
All state is in in-memory `Configuration` and static AWSClientConfig minimum-duration settings. No persistent files or network calls are used. Static duration state is reset after each test.

## Dependencies and Integration Points
The tests integrate Hadoop configuration parsing, S3A constants, AWS SDK client override configuration, and Hadoop `Lists` utility for expected multi-value headers.

## Risks and Edge Cases
`testCreateApiConnectionSettingsDefault()` uses a default-loading `Configuration` and asserts no core-site/default value sets `REQUEST_TIMEOUT`; local site configuration drift could fail it. Header parsing tests depend on comma/semicolon/equal syntax.

## Test Signals
Passing indicates client connection defaults, minimum durations, request timeout propagation, and service-scoped custom header parsing remain stable and isolated.
