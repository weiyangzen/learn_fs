# sources/distributed-fs/juicefs/pkg/object/webdav.go

Purpose: implements WebDAV-backed object storage, mapping object keys to remote WebDAV paths.

Important APIs and types: `webdav` embeds `DefaultObjectStorage` and holds endpoint URL plus a `gowebdav.Client`. It implements `String`, no-op `Create`, `Head`, `Get`, `Put`, `Delete`, `Copy`, delimiter-only `List`, and `newWebDAV`. `webDAVFile` appends directory suffixes in sorted listing.

Control flow and state: `Head` maps WebDAV not-found to `os.ErrNotExist`. `Get` uses full or ranged stream reads. `Put` creates directories for suffix `/` keys or streams file content. `Delete` refuses non-empty directories and ignores missing paths. `List` supports only `/` delimiter, reads one directory, normalizes directory names with trailing slash, sorts, filters by prefix/marker, and uses `generateListResult`.

Persistence and integration: data persists on the WebDAV server. The shared HTTP transport is installed on the client; credentials come from user/password args.

Risks and test signals: no context cancellation is passed to WebDAV calls. `Put` does not create parent directories for files. Delete of non-empty directories returns an error. No WebDAV-specific tests are included.
