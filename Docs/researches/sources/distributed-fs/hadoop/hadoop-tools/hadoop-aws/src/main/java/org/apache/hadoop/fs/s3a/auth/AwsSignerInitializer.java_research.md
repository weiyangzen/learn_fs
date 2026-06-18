# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AwsSignerInitializer.java

## Purpose
`AwsSignerInitializer` is an extension interface for custom AWS signer implementations that need per-store registration and unregistration hooks.

## Important APIs and control flow
`registerStore()` and `unregisterStore()` receive bucket name, store configuration, delegation-token provider, and store UGI. Implementations can maintain external signer state keyed by store identity.

## State, dependencies, and integration
The interface has no state. It depends on Hadoop `Configuration`, S3A filesystem concepts, delegation-token provider, and UGI. `CustomSdkSigner.Initializer` is a simple test implementation.

## Risks and test signals
Implementations must avoid leaking per-store state and must handle unregister even after partial initialization. Tests should verify custom signer initialization hooks are called with the expected bucket/config/user and that unregister runs on filesystem close.
