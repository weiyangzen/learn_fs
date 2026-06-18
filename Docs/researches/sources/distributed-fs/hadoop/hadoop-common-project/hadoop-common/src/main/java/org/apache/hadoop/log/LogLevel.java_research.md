<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogLevel.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogLevel.java

## Purpose
`LogLevel` provides a runtime log-level inspection and mutation tool for Hadoop daemons, with both a command-line client and an HTTP servlet.

## Important APIs, Types, And Functions
- Constants define usage text and supported protocols `http`/`https`.
- `main` runs `CLI` through `ToolRunner`.
- `isValidProtocol(String)` accepts only exact lowercase `http` or `https`.
- `CLI` parses `-getlevel <host:port> <classname>`, `-setlevel <host:port> <classname> <level>`, and optional `-protocol`.
- `CLI.connect(URL)` uses `AuthenticatedURL` with `KerberosAuthenticator`; HTTPS configures `SSLFactory` and an `SSLSocketFactory`.
- `CLI.process(String)` connects and prints servlet output lines prefixed by `MARKER` after stripping HTML tags.
- `Servlet.doGet` checks administrator access, renders an HTML form, reads `log` and `level` parameters, and delegates log4j logger mutation.
- `Servlet.process(Logger, String, PrintWriter)` validates the requested level via `Level.toLevel`, sets it when valid, and prints the effective level.

## Control Flow
The CLI parses exactly one operation and at most one protocol, defaults protocol to HTTP, constructs the servlet URL, authenticates, reads the HTML response, and prints only marked output lines. The servlet enforces admin access first, initializes an HTML response, resolves the requested SLF4J logger, verifies whether it is backed by log4j via `GenericsUtil.isLog4jLogger`, optionally sets the log4j level, always reports the effective level for log4j loggers, and renders forms.

## State And Persistence
The CLI stores parsed arguments in memory. The servlet changes runtime log4j logger level in the daemon JVM; this is process-local mutable state and is not persisted across restart unless logging configuration is separately changed.

## Dependencies And Integration Points
Integrates with Hadoop `Tool`, `Configuration`, generic options, SPNEGO/Kerberos authentication, optional SSL client configuration, `HttpServer2` administrator authorization, servlet utilities, SLF4J/log4j bridging, and daemon web UIs mounted at `/logLevel`.

## Risks And Edge Cases
CLI query parameters are concatenated without URL encoding, so class names or levels with special characters could produce malformed requests. Protocol validation is case-sensitive. HTTPS `SSLFactory` is initialized but not explicitly destroyed. Servlet output includes submitted logger names in HTML; it relies on servlet utilities and controlled values for safety. Runtime level mutation is restricted to log4j-backed loggers; non-log4j loggers can be inspected only to the extent of the message saying mutation is unsupported. `Level.toLevel` maps unknown strings to DEBUG by default, so the code compares the normalized value to the original to reject invalid levels.

## Test Signals
Tests should cover CLI parsing errors, duplicate operations/protocols, default protocol, HTTP/HTTPS connection setup, marker/tag stripping, servlet admin denial, get-level and set-level flows, invalid levels, non-log4j logger behavior, and persistence expectations across daemon restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/log/LogLevel.java -->
