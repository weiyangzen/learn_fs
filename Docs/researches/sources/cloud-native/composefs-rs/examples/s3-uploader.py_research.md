# sources/cloud-native/composefs-rs/examples/s3-uploader.py

Purpose: uploads files from a directory to S3-compatible object storage, with MIME detection, optional zstd compression, symlink-target handling, and parallel processing.

Important APIs/types/functions: `MimeDB`, `MimeDB.getdb/content_type_for_data`, `ensure_file`, `find_not_type_d`, and `main`.

Control flow: opens the source directory as an fd, walks files with `os.fwalk`, sorts paths, creates a boto3 bucket resource, and maps files through a `ThreadPoolExecutor`. Each file is skipped if S3 `HEAD` succeeds, otherwise read with `O_NOFOLLOW`; symlinks are uploaded as their target text with content type `text/x-symlink-target`; payloads are compressed with zstd level 19 only if ratio exceeds 1.1.

State/persistence: remote S3 objects are persisted with `ContentEncoding` and `ContentType`; local state is read-only except environment variable `AWS_REQUEST_CHECKSUM_CALCULATION`.

Dependencies/integration: depends on boto3/botocore, libmagic Python bindings, zstd module, S3 endpoint credentials, and Unix fd-relative I/O.

Risks/test signals: no explicit tests in this subset. Race risk exists between HEAD skip and PUT; symlink handling encodes target with surrogateescape; path traversal is constrained by dirfd and `O_NOFOLLOW`.
