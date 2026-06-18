# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSAuthenticationFilter.java

## Purpose
`TestKMSAuthenticationFilter.java` verifies that KMS authentication filter configuration rewrites simple authentication into the delegation-token-aware pseudo handler and sets the KMS delegation token kind.

## Important APIs, Types, and Functions
- `testConfiguration()` sets `hadoop.kms.authentication.type=simple`, calls `new KMSAuthenticationFilter().getKMSConfiguration(conf)`, and inspects returned `Properties`.
- It asserts `KMSAuthenticationFilter.AUTH_TYPE` equals `PseudoDelegationTokenAuthenticationHandler`.
- It asserts `DelegationTokenAuthenticationHandler.TOKEN_KIND` equals `KMSDelegationToken.TOKEN_KIND_STR`.

## Control Flow and State
The test is stateless beyond a local `Configuration` and returned `Properties`. It validates property translation rather than servlet filter execution.

## Dependencies and Integration Points
It links the KMS filter to Hadoop security token web authentication classes and the `KMSDelegationToken` token kind. This property contract is consumed when KMS initializes HTTP authentication.

## Risks and Edge Cases
The test only covers simple mode. Kerberos property conversion and error handling are left to broader KMS integration tests.

## Test Signals
The file gives a narrow regression signal that simple KMS auth still enables delegation token support rather than plain pseudo authentication.
