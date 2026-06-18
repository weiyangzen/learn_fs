## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/fs/http/server/CheckUploadContentTypeFilter.java

Purpose: this servlet filter enforces `application/octet-stream` content type for HttpFS data upload requests.

Important APIs and types: it implements `javax.servlet.Filter`, uses `HttpServletRequest`, `HttpServletResponse`, `FilterChain`, `HttpFSFileSystem.Operation`, `HttpFSFileSystem.OP_PARAM`, `HttpFSFileSystem.UPLOAD_CONTENT_TYPE`, `HttpFSParametersProvider.DataParam.NAME`, and `StringUtils.toUpperCase()`.

Control flow: a static set marks upload operations `APPEND` and `CREATE`. `doFilter()` allows all requests by default, then for PUT/POST requests with an upload operation and `data=true`, compares request content type case-insensitively to `application/octet-stream`. Valid requests continue down the chain; invalid upload requests receive HTTP 400 with a specific message. `init()` and `destroy()` are no-ops.

State and persistence: persistent state is only the static upload-operation set. Runtime state is per-request method/op/data/content-type evaluation. No durable state is touched.

Dependencies and integration points: installed in the HttpFS server servlet chain to guard the second phase of create/append uploads that the client opens after redirect.

Risks: enforcement depends on the `op` and `data` parameters being present and correctly named. Requests with missing `data=true` bypass content-type checking, matching the distinction between control and upload phases.

Test signals: expected signal is server rejection of create/append data requests without the exact upload content type, while non-upload PUT/POST and control-phase requests pass through.
