<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAltKerberosAuthenticationHandler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAltKerberosAuthenticationHandler.java

## Purpose
Tests alternate Kerberos handler behavior for browser-like user agents while reusing the standard Kerberos handler test suite for non-browser cases.

## Important APIs, types, and functions
Overrides `getNewAuthenticationHandler()` to instantiate an anonymous `AltKerberosAuthenticationHandler` whose `alternateAuthenticate()` returns a fixed token. `getExpectedType()` expects `alt-kerberos`. Tests configure `alt-kerberos.non-browser.user-agents` and assert browser/non-browser routing.

## Control flow
Browser-like user agents invoke alternate authentication and return token `A/B`. Non-browser user-agent configuration defers to inherited Kerberos tests for missing, invalid, valid, and invalid-Kerberos Authorization headers.

## State and persistence
Uses inherited MiniKDC/keytab handler state from `TestKerberosAuthenticationHandler`. No durable state is created by this subclass beyond test keytabs.

## Dependencies and integration points
Depends on `AltKerberosAuthenticationHandler`, inherited `TestKerberosAuthenticationHandler`, servlet mocks, Mockito, and JUnit timeouts.

## Risks and test signals
Signals include configurable non-browser user-agent matching and alternate token type preservation. Gaps include null User-Agent, mixed-case user-agent matching, overlapping browser/non-browser substrings, and real SPNEGO browser negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/test/java/org/apache/hadoop/security/authentication/server/TestAltKerberosAuthenticationHandler.java -->
