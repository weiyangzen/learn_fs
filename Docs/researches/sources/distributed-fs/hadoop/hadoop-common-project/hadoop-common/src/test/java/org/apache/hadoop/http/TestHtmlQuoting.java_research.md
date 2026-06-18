# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHtmlQuoting.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHtmlQuoting.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHtmlQuoting.java

Purpose: this unit test validates HTML escaping/unescaping utilities and request-parameter quoting used by `HttpServer2.QuotingInputFilter`.

Important APIs and types: tests `HtmlQuoting.needsQuoting()`, `quoteHtmlChars()`, `unquoteHtmlChars()`, and `HttpServer2.QuotingInputFilter.RequestQuoter`. Mockito supplies a mock `HttpServletRequest`.

Control flow: quoting tests cover all escapable characters (`<`, `>`, `&`, apostrophe, quote), empty strings, newline-only strings, and nulls. Round-trip tests quote then unquote representative strings and all ASCII characters below 127. Request quoting verifies single parameter and array parameter escaping plus null behavior.

State and persistence: no external state or persistence. State is local strings and mocked request return values.

Dependencies and integration points: integrates utility escaping with the request wrapper used by HTTP server filters to protect servlet consumers from raw HTML metacharacters.

Risks: expected escaping format is strict, so any change from named entities to numeric entities would require test updates even if semantically equivalent.

Test signals: confirms no NPE on missing params, arrays are quoted element-wise, non-quotable input remains stable through round trip, and dangerous HTML characters are escaped consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHtmlQuoting.java -->
