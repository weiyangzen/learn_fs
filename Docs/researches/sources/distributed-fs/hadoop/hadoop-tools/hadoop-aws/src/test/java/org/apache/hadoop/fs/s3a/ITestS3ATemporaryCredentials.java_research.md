# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ATemporaryCredentials.java

Purpose: Tests STS temporary credential acquisition, validation, session-token propagation into S3A and delegation tokens, expiry metadata, bad endpoint/region handling, and exception translation.

Important APIs/types/functions: `STSClientFactory`, `StsClient`, `TemporaryAWSCredentialsProvider`, `MarshalledCredentials`, `MarshalledCredentialBinding`, `SessionTokenIdentifier`, `requestSessionCredentials()`, `toAWSCredentials()`, `assertCredentialsEqual()`, `ASSUMED_ROLE_STS_ENDPOINT`, `ASSUMED_ROLE_STS_ENDPOINT_REGION`, `AWS_CREDENTIALS_PROVIDER`, and `SESSION_TOKEN`.

Control flow: setup requires session tests and configures delegation-token session binding. `testSTS()` shares parent credentials, requests STS credentials, writes them to a cloned config, verifies S3 access with temporary credentials, then corrupts the token and expects S3 access failure. Other tests validate blank/empty credential rejection, delegation-token origin and exact credential propagation, expiry within expected duration, invalid STS token failure, region/endpoint combinations via `expectedSessionRequestFailure()`, validation on load, empty credentials, and request exception translation.

State and persistence: `credentials` holds a shared credential provider list closed in teardown. Tests write small S3 files with temporary credentials and call live STS endpoints.

Dependencies and integration points: AWS STS, S3A credential provider binding, delegation-token session binding, retry invoker, marshalled credential validation, region/endpoint signing rules, and filesystem creation with cloned configs.

Risks: live STS/network/account permissions required; clock skew affects expiry assertions; expected exception types vary by endpoint/region behavior; corrupted token failure can occur at filesystem creation or file IO.

Test signals: broad credential-chain signal covering both successful temporary credential use and many failure/validation paths.
