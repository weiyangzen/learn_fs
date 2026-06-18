# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3native/S3xLoginHelper.java

Purpose: private evolving utility shared by Hadoop S3 filesystem implementations for URI construction, URI canonicalization, and path ownership checks after URI-embedded login extraction was removed.

Important APIs/types/functions: `buildFSURI(URI)` validates non-null URI, scheme, and host and returns `scheme://host` without user info, path, query, or fragment. `canonicalizeUri(URI, int)` injects a positive default port when the URI lacks one. `checkPath(Configuration, URI, Path, int)` mirrors `FileSystem.checkPath` semantics while comparing `URI.getHost()` instead of authority, so embedded auth is ignored. Nested `Login` is a simple immutable user/password tuple with `hasLogin()`, equality, hash, and accessors.

Control flow: `checkPath()` returns immediately for relative paths. For matching schemes, it compares canonicalized host names case-insensitively; if the path host is absent, it may substitute `FileSystem.getDefaultUri(conf)` when schemes match. Any mismatch throws `IllegalArgumentException` with sanitized URI strings.

State and persistence: no persistent state; `Login` only holds immutable strings. The helper is stateless and thread-safe.

Dependencies and integration: depends on Hadoop `Configuration`, `FileSystem`, and `Path`, plus Apache Commons `StringUtils`. It is packaged under legacy `s3native` so S3A/S3N-style code can share it.

Risks: `buildFSURI()` intentionally drops ports, paths, query, and fragments; callers needing port retention must use `canonicalizeUri()`. `checkPath()` relies on host comparison, so URI forms with unusual authority parsing may behave differently from generic filesystem checks. Error text still includes `pathUri` and `fsUri`, but `buildFSURI()` avoids secrets in authority.

Test signals: this file contains no local tests; coverage is indirect through S3A/S3N filesystem URI/path qualification tests.
