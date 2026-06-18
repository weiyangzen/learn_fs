## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/client/HttpFSUtils.java

Purpose: `HttpFSUtils` provides private client utilities for constructing HttpFS operation URLs and parsing JSON responses.

Important APIs and types: constants define service prefix `/webhdfs`, version `/v1`, and empty byte array. `createURL(Path, Map)` and `createURL(Path, Map, Map<String,List<String>>)` build HTTP/HTTPS URLs. `jsonParse(HttpURLConnection)` validates JSON content type and parses response streams with JSON-simple.

Control flow: `createURL()` maps `webhdfs` to `http` and `swebhdfs` to `https`, appends `/webhdfs/v1` plus the path, then URL-encodes single-valued and multi-valued query parameters. Invalid schemes throw `IllegalArgumentException`. `jsonParse()` accepts absent content type, rejects non-compatible media types, and wraps JSON parse errors in `IOException`.

State and persistence: stateless utility methods; no persistence or cached state.

Dependencies and integration points: used by `HttpFSFileSystem` for every operation URL and JSON parse path. Integrates `Path`, `HttpURLConnection`, `URLEncoder`, JAX-RS `MediaType`, JSON-simple parser, and UTF-8 stream decoding.

Risks: query parameter order follows map iteration order, so callers should use deterministic maps if exact URL order matters. It uses historical `"UTF8"` encoding labels in some calls. Missing content type is permitted for compatibility, which can defer bad response detection to JSON parsing.

Test signals: expected behavior is visible through HttpFS/WebHDFS request tests and JSON parsing failures: correct scheme translation, service prefix insertion, multi-valued xattr params, content-type compatibility, and parse-error wrapping.
