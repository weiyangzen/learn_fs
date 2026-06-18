# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/IAMInstanceCredentialsProvider.java

## Purpose
`IAMInstanceCredentialsProvider` obtains credentials from AWS container metadata first and falls back to EC2 instance profile metadata. It is S3A's v2 replacement for legacy EC2/container provider wrappers.

## Important APIs and control flow
The constructor creates a `ContainerCredentialsProvider` with async refresh enabled. `resolveCredentials()` calls synchronized `getCredentials()` and converts `SdkClientException` into `NoAwsCredentialsException`, extracting embedded IO exceptions when available. `getCredentials()` first tries the current provider. On first failure from the container provider, it closes it, switches to `InstanceProfileCredentialsProvider` with async refresh and a five-minute stale time, and retries. Subsequent instance-profile failures are rethrown. `close()` closes the active HTTP credentials provider.

## State, dependencies, and integration
State is the mutable active `HttpCredentialsProvider` and boolean indicating whether it is still using container credentials. Dependencies include AWS SDK container/instance providers, S3A error translation, and auth exceptions. It is part of the standard credential provider chain.

## Risks and test signals
Fallback is one-way; a transient container metadata failure switches permanently to instance profile for that provider instance. Tests should cover container success, container failure then instance success, both failure with `NoAwsCredentialsException`, IO cause extraction, async refresh configuration, and close after fallback.
