# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/resources/webapps/kms/WEB-INF/web.xml

## Purpose
`web.xml` declares the KMS web application components for the servlet container.

## Important APIs, Types, and Functions
It registers `KMSWebApp` as a listener, Jersey `ServletContainer` as `webservices-driver` scanning `org.apache.hadoop.crypto.key.kms.server`, Hadoop `JMXJsonServlet`, servlet mappings for `/kms/*` and `/kms/jmx`, and filters `KMSAuthenticationFilter` and `KMSMDCFilter` on all paths.

## Control Flow
Container startup invokes `KMSWebApp.contextInitialized`, eagerly loads Jersey, and routes `/kms/*` REST calls through auth and MDC filters into Jersey resources. `/kms/jmx` exposes JMX JSON through the same filter mappings.

## State and Persistence
The descriptor is static deployment metadata. Runtime state is created by the listener and filters it declares.

## Dependencies and Integration Points
It ties together `KMSWebApp`, `KMS`, Jersey providers and exception mappers in the server package, the authentication filter, request context filter, and JMX servlet.

## Risks
Filter order is important: authentication is declared before MDC so request UGI is available. Package scanning must include all providers; moving classes out of the package would require descriptor changes. JMX exposure is protected only by the configured filter/admin behavior.

## Test Signals
Integration tests should verify REST and JMX mappings, listener startup, provider discovery, filter order, authentication enforcement, and that `/kms/*` paths match client expectations.
