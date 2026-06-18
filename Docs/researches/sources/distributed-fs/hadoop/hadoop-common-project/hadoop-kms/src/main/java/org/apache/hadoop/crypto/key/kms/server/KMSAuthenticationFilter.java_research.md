# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSAuthenticationFilter.java

## Purpose
`KMSAuthenticationFilter.java` adapts Hadoop delegation-token authentication to KMS-specific configuration, proxy-user settings, metrics, and audit behavior.

## Important APIs, Types, and Functions
It extends `DelegationTokenAuthenticationFilter`. `CONFIG_PREFIX` is `hadoop.kms.authentication.`. `getKMSConfiguration` maps simple and kerberos auth types to delegation-token authentication handlers and sets the KMS delegation token kind. `getProxyuserConfiguration` strips `hadoop.kms.` from proxyuser properties. Inner `KMSResponse` captures status and error message.

## Control Flow
For initialization, the filter copies KMS authentication-prefixed config from `KMSWebApp.getConfiguration()`. During `doFilter`, it wraps the response, delegates to the parent filter, then increments invalid-call metrics for non-OK/non-CREATED/non-UNAUTHORIZED statuses. Unauthorized responses increment unauthenticated metrics and audit unauthenticated requests except for OPTIONS, which is part of SPNEGO negotiation.

## State and Persistence
The filter keeps no persistent state. Request-local response status and message are held in the wrapper. Authentication cookies/tokens are handled by the parent Hadoop auth framework.

## Dependencies and Integration Points
It integrates with `KMSWebApp` configuration, `KMSDelegationToken`, Hadoop authentication handlers, Jetty response status reason support, and `KMSAudit`. It is registered in `web.xml` before `KMSMDCFilter`.

## Risks
`getKMSConfiguration` assumes `AUTH_TYPE` is present; a missing property would produce a null dereference. `sendError` must account for Jetty behavior after 9.4.21 by using `setStatusWithReason`. Metrics classification depends on captured status codes; code paths that do not set status may be invisible.

## Test Signals
Tests should validate auth type rewriting, token kind setting, proxyuser config key transformation, unauthorized audit suppression for OPTIONS, HTML quoting in errors, and invalid/unauthenticated meter increments.
