# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/KerberosUgiAuthenticator.java

## Purpose

`KerberosUgiAuthenticator` customizes Hadoop HTTP Kerberos authentication so SPNEGO fallback uses Hadoop `UserGroupInformation` instead of the base pseudo-authenticator username lookup.

## Important APIs, Types, And Functions

It extends `KerberosAuthenticator` and overrides `getFallBackAuthenticator`. The returned anonymous `PseudoAuthenticator` overrides `getUserName` to return `UserGroupInformation.getLoginUser().getUserName()`.

## Control Flow

When an authenticated URL tries Kerberos and the server does not use SPNEGO, the fallback pseudo authenticator supplies the UGI login user name. `IOException` while retrieving the login user is wrapped as `SecurityException`.

## State And Persistence

The class owns no state. It reads current process login-user state from UGI.

## Dependencies And Integration Points

It is used by `URLConnectionFactory.openConnection(url, true)` through `AuthenticatedURL`. It depends on Hadoop security authentication client classes and UGI.

## Risks

Incorrect fallback identity can cause insecure-cluster or proxy-user behavior differences. Wrapping `IOException` in unchecked `SecurityException` changes failure handling relative to callers expecting checked authentication errors.

## Test Signals

Tests should cover SPNEGO fallback in simple-auth mode, UGI login-user selection, and failure when UGI cannot provide a user.
