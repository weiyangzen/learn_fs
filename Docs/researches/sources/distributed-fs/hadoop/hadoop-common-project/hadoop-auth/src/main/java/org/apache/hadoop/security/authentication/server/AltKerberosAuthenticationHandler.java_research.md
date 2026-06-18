# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/server/AltKerberosAuthenticationHandler.java

Purpose: abstract server-side handler that uses Kerberos for non-browser clients and delegates browser authentication to a subclass-defined alternate mechanism.

Important APIs, types, and functions: type constant is `alt-kerberos`. Config property `alt-kerberos.non-browser.user-agents` defaults to `java,curl,wget,perl`. Overrides `getType()`, `init()`, and `authenticate()`. Provides `isBrowser(String userAgent)` and abstract `alternateAuthenticate()`.

Control flow: initialization loads the comma-separated non-browser user-agent fragments. On authenticate, requests with browser-like user agents are sent to `alternateAuthenticate()`; non-browser clients use `KerberosAuthenticationHandler.authenticate()`.

State and persistence: stores lower-cased non-browser user-agent patterns in memory. Kerberos state is managed by the superclass.

Dependencies and integration points: extends `KerberosAuthenticationHandler` and is the base for `JWTRedirectAuthenticationHandler`. Covered by `TestAltKerberosAuthenticationHandler`.

Risks and test signals: user-agent classification is heuristic and spoofable. Null user-agent is treated as non-browser and gets Kerberos. Test signals include default and custom non-browser lists, browser alternate flow, and Kerberos fallback for CLI agents.
