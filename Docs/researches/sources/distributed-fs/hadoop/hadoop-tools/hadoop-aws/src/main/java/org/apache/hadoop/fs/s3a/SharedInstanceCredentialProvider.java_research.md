# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/SharedInstanceCredentialProvider.java

## Purpose
`SharedInstanceCredentialProvider` restores a documented public credential provider name by subclassing `IAMInstanceCredentialsProvider` for IAM instance/container credentials.

## Important APIs, Types, and Functions
The class declares no methods or fields; its behavior is inherited entirely from `IAMInstanceCredentialsProvider`.

## Control Flow and State
Construction and credential resolution follow the superclass. Authentication failures should surface as `NoAwsCredentialsException`, allowing retry handlers to treat them as non-recoverable.

## State and Persistence Behavior
All state is inherited from the IAM provider. This wrapper persists no additional data.

## Dependencies and Integration Points
Dependencies are `IAMInstanceCredentialsProvider` and `NoAwsCredentialsException`. The class name is a configuration-facing compatibility point for `fs.s3a.aws.credentials.provider` and documentation.

## Risks and Test Signals
Risks include accidental removal/renaming breaking configured deployments, superclass semantic changes altering this provider, and public evolving API expectations. Tests should verify class instantiation through configured provider lists and failure translation when instance/container credentials are unavailable.
