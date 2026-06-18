# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestCrossOriginFilter.java

Purpose: tests Hadoop's `CrossOriginFilter` CORS handling, including same-origin passthrough, wildcard origins, header encoding against response splitting, wildcard and regex origin matching, disallowed request suppression, successful response headers, and reinitialization after destroy.

Important APIs and types: `CrossOriginFilter`, servlet `FilterConfig`, `FilterChain`, `HttpServletRequest`, `HttpServletResponse`, CORS header constants, Mockito, and `MockitoUtil.verifyZeroInteractions`.

Control flow: tests construct a map-backed `FilterConfigTest`, initialize a filter, and either call `areOriginsAllowed` directly or run `doFilter` with mocked requests/responses. Same-origin and disallowed origin/method/header tests verify no response headers are set while the chain proceeds. Pattern tests cover `*.example.com`, regex entries, complex protocol/port regex, mixed regex and wildcard lists, and origin-list strings where any origin may match. `testEncodeHeaders` confirms newline response-splitting content is truncated/sanitized while valid single or list origins survive. Successful CORS test verifies `Access-Control-Allow-Origin`, credentials, methods, and headers are set. Restart test initializes with one config, destroys, clears config, reinitializes with new values, and verifies new headers/origins.

State and persistence: filter instances are in-memory; no files. Restart test checks that destroy clears state enough for reuse.

Dependencies and integration points: integrates servlet filter lifecycle, Hadoop HTTP security config keys, CORS request/response headers, regex/wildcard matching, and response header encoding.

Risks: no negative regex malformed-pattern test. Disallowed requests are allowed through the chain without CORS headers, so tests do not assert browser-level behavior. Header comparison uses exact string ordering from config.

Test signals: strong signal for CORS origin matching semantics, header sanitation, allowed/disallowed branch behavior, and lifecycle reconfiguration.
