# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/S3Handler.java

`S3Handler` is the servlet-v2 per-request coordinator. It parses bucket/object paths under `S3RequestServlet.S3_V2_SERVICE_PATH_PREFIX`, URL-decodes names, authenticates via `S3RestUtils.getUser`, rejects unsupported subresources, initializes filesystem/audit resources, creates multipart metadata storage, and instantiates the correct bucket or object task.

`processResponse` bridges JAX-RS `Response` objects to `HttpServletResponse`, copying status, headers, and entities. `InputStream` entities are streamed with a thread-local 8 KiB buffer; string entities get a content length and are written to the servlet output stream.

Persistent effects include creating `.alluxio_s3_api_metadata/uploads` and using the static expiring `BUCKET_PATH_CACHE`. Dependencies include servlet APIs, Alluxio `FileSystem`, configuration, `ProxyWebServer` context attributes, audit logging, task factories, and `S3ErrorResponse`.

Tests should cover URL parsing/decoding, auth failures, unsupported query rejection, metadata directory creation, task selection, response header replacement/addition, stream and string entities, and stream-read failures. Risks include `extractAMZHeaders` collecting all headers despite its name and recursive error emission after partial output.
