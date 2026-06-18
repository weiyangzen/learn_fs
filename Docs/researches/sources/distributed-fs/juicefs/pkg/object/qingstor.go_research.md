# sources/distributed-fs/juicefs/pkg/object/qingstor.go

Purpose: implements the QingStor object backend behind `qingstor` when `!noqingstor` is enabled.

Important APIs and types: `qingstor` wraps a QingStor bucket client plus `tierStorage`. It implements bucket creation, object metadata, range reads, writes with content length and MIME type, delete, copy, list, multipart upload/copy/complete/abort/list, and the unsupported `Restore`. `findLen` normalizes arbitrary readers into a reader plus length for APIs requiring content length.

Control flow and state: `Create` treats `bucket_already_exists` as success. `Head` converts QingStor 404 to `os.ErrNotExist`. `Get` uses shared `getRange` and `checkGetStatus`, populating `ResponseAttrs` request ID and storage class from the output. `Put` may buffer non-sized readers, sets `XQSStorageClass` from the active tier, and expects HTTP 201. List clamps to 1000, optionally includes common prefixes, and sorts mixed object/prefix output.

Persistence and integration: data is stored in a configured QingStor bucket. `newQingStor` parses public or private-cloud endpoint shapes into bucket, zone, host, protocol, and shared HTTP transport.

Risks and test signals: buffering in `findLen` can be memory-heavy for large non-seekable inputs. Restore is not supported. Endpoint parsing assumes specific host segment patterns. No QingStor-specific tests appear in this subset.
