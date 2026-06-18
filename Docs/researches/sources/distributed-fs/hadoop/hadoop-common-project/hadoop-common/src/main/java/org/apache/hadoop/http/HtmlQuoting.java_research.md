<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HtmlQuoting.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HtmlQuoting.java

Purpose: HTML escaping and unescaping utility used by Hadoop servlets and request filters to reduce cross-site scripting exposure in generated text and reflected request parameters.

Important APIs, types, and functions: `needsQuoting(byte[], off, len)` and `needsQuoting(String)` detect active HTML characters. `quoteHtmlChars(OutputStream, byte[], off, len)` and `quoteHtmlChars(String)` replace `&`, `<`, `>`, apostrophe, and quote with entity strings. `quoteOutputStream()` wraps an output stream. `unquoteHtmlChars()` reverses the supported entity set and rejects malformed or unknown entities.

Control flow: string quoting converts to UTF-8 bytes, checks whether work is needed, then writes escaped bytes to a `ByteArrayOutputStream`. Unquoting scans from ampersand to semicolon and throws `IllegalArgumentException` on unexpected entities.

State and persistence: stateless except for cached UTF-8 entity byte arrays. No persistence.

Dependencies and integration points: used by `HttpServer2.QuotingInputFilter` and servlet code that reflects request data. Depends only on standard IO and charset APIs.

Risks and test signals: byte-oriented scanning is safe for ASCII trigger characters but does not perform full HTML sanitization. `unquoteHtmlChars()` intentionally rejects unknown entities, which can turn malformed input into request failures. Tests should cover nulls, all five escaped characters, UTF-8 non-ASCII passthrough, output-stream wrapping, bad entity rejection, and round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/HtmlQuoting.java -->
