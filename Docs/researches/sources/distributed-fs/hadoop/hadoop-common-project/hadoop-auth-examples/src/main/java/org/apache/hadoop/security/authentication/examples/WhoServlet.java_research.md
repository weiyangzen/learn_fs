# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/WhoServlet.java

Purpose: sample servlet that reports the authenticated remote user and principal placed on the request by Hadoop Auth.

Important APIs, types, and functions: `doGet()` sets `text/plain`, status 200, reads `req.getRemoteUser()` and `req.getUserPrincipal().getName()`, and writes a formatted line. `doPost()` delegates to `doGet()`.

Control flow: servlet endpoints are reached after the configured auth filter chain. The response reflects authentication state from the request wrapper installed by `AuthenticationFilter`.

State and persistence: stateless servlet; no persistent data.

Dependencies and integration points: depends on servlet APIs and is mapped to anonymous, simple, and kerberos example URL prefixes in `web.xml`.

Risks and test signals: exposes identity information for demonstration only. Test signals are endpoint responses showing null or authenticated user/principal values depending on the configured auth filter and token state.
