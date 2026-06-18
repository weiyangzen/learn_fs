# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/audit/HttpReferrerAuditHeader.java

Purpose: builder and runtime generator for Hadoop audit data encoded as an HTTP Referer header, including static attributes, dynamic per-request attributes, global audit context, filtering, escaping, and parsing helpers.

Important APIs, types, and functions: `REFERRER_PATH_FORMAT`, `buildHttpReferrer()`, `set()`, getters, `escapeToPathElement()`, `maybeStripWrappedQuotes()`, `extractQueryParameters()`, static `builder()`, and builder methods for context ID, operation name, span ID, paths, attributes, evaluated suppliers, global context values, and filters.

Control flow: construction copies builder maps into thread-safe structures, adds operation/path/span query attributes, overlays global context values with `putIfAbsent()`, and eagerly builds an initial header for validation. `buildHttpReferrer()` copies attributes, evaluates suppliers in the current thread, filters keys, joins query pairs, and constructs a URI with origin host and audit path. URI syntax failures and supplier/runtime failures are logged at most once and return an empty header. Parsing strips wrapping quotes and uses Apache HTTP client URL utilities.

State and persistence: stores immutable identity fields plus concurrent maps for static attributes and evaluated suppliers. `set()` can mutate attributes after construction. The generated header is a string emitted to HTTP requests and external logs.

Dependencies and integration points: depends on `CommonAuditContext`, audit constants, Apache HTTP `URLEncodedUtils`, Guava `ImmutableSet`, commons-lang `StringUtils`, and `LogExactlyOnce`. Tests are noted in S3A audit test classes because S3 logs consume the header.

Risks and test signals: query strings are built as raw `key=value` pairs before `URI` encoding, so special characters, null supplier values, and duplicate keys need coverage. Tests should cover dynamic evaluation per thread, filtering, global context precedence, parse round trip, quote stripping, escape rules for `/` and `@`, malformed attributes returning empty header, and once-only warning behavior.
