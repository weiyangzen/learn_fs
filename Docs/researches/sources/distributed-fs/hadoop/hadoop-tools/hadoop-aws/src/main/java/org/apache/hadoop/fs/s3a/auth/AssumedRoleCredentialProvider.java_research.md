# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AssumedRoleCredentialProvider.java

## Purpose
`AssumedRoleCredentialProvider` obtains AWS credentials by assuming a configured IAM role through STS, using a separate credential-provider chain for the STS call.

## Important APIs and control flow
The constructor requires `fs.s3a.assumed.role.arn`, builds the base credential list from `ASSUMED_ROLE_CREDENTIALS_PROVIDER` while forbidding itself, derives or reads a sanitized session name, reads duration, optional scope-down policy, external ID, STS endpoint, and region, builds an `StsClient`, creates `StsAssumeRoleCredentialsProvider`, creates an `Invoker`, and calls `resolveCredentials()` to fail fast. `resolveCredentials()` retries raw STS provider resolution and wraps unexpected IO in `CredentialInitializationException`. `close()` closes the STS provider, base credential list, and STS client. `sanitize()` replaces characters outside AWS role-session safe set with `-`.

## State, dependencies, and integration
State includes role ARN, session name/duration, base credential list, STS client/provider, and retry invoker. Dependencies include AWS SDK STS/auth, S3A constants, `CredentialProviderListFactory`, `STSClientFactory`, `S3ARetryPolicy`, and UGI. It integrates as a credential provider class selectable in S3A configuration.

## Risks and test signals
Misconfigured role ARN, endpoint/region, forbidden recursive provider chains, and STS throttling are key risks. Tests should cover missing ARN, provider-list construction, session-name sanitization, policy/external ID propagation, fail-fast behavior, retry logging, and close propagation.
