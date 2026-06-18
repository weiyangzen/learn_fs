# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authorize/AuthorizationException.java

## Purpose

`AuthorizationException` is the service/proxy authorization failure exception used in Hadoop security code. It extends `AccessControlException` while deliberately suppressing stack trace exposure for security-sensitive failures.

## Important APIs, Types, and Functions

It provides default, message, and cause constructors. It overrides `getStackTrace` and all `printStackTrace` variants to return or print only the exception text, not frame details.

## Control Flow

Callers throw it when ACL, principal, proxy-user, or host checks fail. The overridden printing methods short-circuit normal throwable stack trace rendering.

## State and Persistence Behavior

The class has no mutable instance state beyond inherited exception fields. The shared static empty `StackTraceElement[]` is returned from `getStackTrace`.

## Dependencies and Integration Points

It depends on Hadoop `AccessControlException` and is thrown by `DefaultImpersonationProvider`, `ProxyUsers`, `ServiceAuthorizationManager`, and `ImpersonationProvider` default hostname resolution.

## Risks and Edge Cases

Suppressed stack traces are intentional but reduce operational debugging context. The cause constructor can still preserve cause metadata, but printed output hides stack frames.

## Test Signals

Tests should assert thrown type/messages from authorization failures and confirm stack trace access/printing does not expose frames.
