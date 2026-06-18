<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerException.java

## Purpose
Defines the checked exception thrown when signed text is missing a signature or fails signature verification.

## Important APIs, types, and functions
`SignerException(String msg)` stores a failure message. `serialVersionUID` is fixed at zero.

## Control flow
No internal control flow beyond exception construction.

## State and persistence
Carries only the inherited exception message/cause state. No persistence occurs.

## Dependencies and integration points
Thrown by `Signer.verifyAndExtract()` and propagated to authentication-token parsing paths.

## Risks and test signals
The class has no cause-taking constructor, so callers cannot preserve underlying crypto/provider exceptions as causes. Tests should assert expected messages for missing and invalid signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/SignerException.java -->
