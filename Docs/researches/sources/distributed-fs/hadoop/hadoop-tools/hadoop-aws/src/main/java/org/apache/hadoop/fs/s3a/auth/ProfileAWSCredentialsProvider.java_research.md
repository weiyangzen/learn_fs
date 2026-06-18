# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/ProfileAWSCredentialsProvider.java

## Purpose
`ProfileAWSCredentialsProvider` loads AWS credentials from an AWS shared credentials profile file using S3A configuration keys or AWS environment variables.

## Important APIs and control flow
`getCredentialsPath()` checks `fs.s3a.auth.profile.file`, then `AWS_SHARED_CREDENTIALS_FILE`, then defaults to `$HOME/.aws/credentials`. `getCredentialsName()` checks `fs.s3a.auth.profile.name`, then `AWS_PROFILE`, then `default`. The constructor builds a v2 `ProfileCredentialsProvider` with the selected profile file and name. `resolveCredentials()` delegates directly to that provider.

## State, dependencies, and integration
State is the wrapped `ProfileCredentialsProvider`; inherited state includes URI and configuration. Dependencies include AWS SDK profile credentials/profile file APIs, Apache Commons `SystemUtils`, and Hadoop annotations/configuration. It can be named in S3A credential-provider configuration.

## Risks and test signals
Profile files may be missing, malformed, or environment-dependent. Tests should cover configuration overriding environment, environment fallback, default path/name selection, profile resolution errors, and behavior on non-default filesystems/path formats.
