# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AAWSCredentialsProvider.java

## Purpose

Comprehensive unit suite for S3A AWS credentials provider configuration, instantiation, remapping, resolution, exception handling, reference counting, and concurrent lazy initialization.

## Important APIs, Types, and Functions

The suite exercises `createAWSCredentialProviderList()`, `buildAWSProviderList()`, `AWSCredentialProviderList.resolveCredentials()/share()/close()`, `CredentialProviderListFactory` mappings, profile credentials, IAM instance credentials, `AbstractSessionCredentialsProvider`, `S3AUtils.getTrimmedStringCollectionSplitByEquals()`, and `S3ATestUtils.authenticationContains()`.

## Control Flow

Early tests assert failures for wrong provider classes, abstract classes, missing classes, bad constructors, constructor exceptions, and invalid factory return types. Chain tests validate configured, default, profile, anonymous, simple, temporary, IAM, environment, and remapped providers. Provider-list tests validate credential resolution, no-auth retry behavior, close/ref-count semantics, IOE propagation, and non-SDK exception wrapping. Concurrency tests run four threads against slow and failing session providers, checking cached success or cached initialization error. String-splitting tests cover whitespace, duplicates, empty entries, and invalid `key=value` forms.

## State, Dependencies, and Integration Points

State includes Hadoop `Configuration`, temp profile files, credential provider lists with reference counts, cached session-provider credentials/errors, and thread pools. It integrates AWS SDK v2 credential providers, legacy provider-name remapping, S3A auth classes, public dataset URI helpers, Hadoop retry policy, and configuration parsing.

## Risks and Test Signals

Provider instantiation is reflection-heavy and sensitive to constructor/factory signatures. Concurrency tests are important for race conditions in lazy credentials. Strong signals include exact provider class order, exception text/classes, no retry on auth failures, ref-count transitions to closed state, and deterministic split-map validation.
