# Research: sources/distributed-fs/alluxio/underfs/gcs/src/main/java/alluxio/underfs/gcs/GCSOutputStream.java

Purpose: GCS output stream that stages data to a local temp file and uploads the full object on close. It implements `ContentHashable` using the uploaded object's MD5 hash.

Important APIs and control flow: constructor validates bucket, records key/client, creates a UUID temp file under configured temp dirs, and wraps the local stream with MD5 digesting when available. `write` and `flush` target the local stream. `close` is idempotent through `AtomicBoolean`, closes the local stream, builds a `GSObject` with file, content length, binary content type, and optional MD5, uploads through `putObject`, records base64 MD5, and deletes the temp file in `finally`.

State, dependencies, integration, risks, tests: state includes temp file, digest, local output stream, closed flag, and content hash. Dependencies include JetS3t GCS client, `Mimetypes`, Alluxio temp-dir utilities, and Java security digest APIs. Risks include local disk exhaustion, failed temp deletion, no multipart streaming upload, and no key validation beyond bucket validation.
