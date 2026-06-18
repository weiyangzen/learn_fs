# sources/distributed-fs/juicefs/pkg/object/tos.go

Purpose: implements Volcengine TOS object storage behind `tos`.

Important APIs and types: `tosClient` stores bucket, TOS V2 client, and `tierStorage`. It implements object CRUD, listing, restore, multipart upload/copy/list/abort/complete, and `newTOS`.

Control flow and state: `Create` treats bucket-exists errors as success. `Get` applies shared range/status checking, propagates request ID/storage class, and verifies checksum metadata on full reads. `Put` adds checksum metadata when the reader is seekable, applies tier storage class and tags, and records response attributes. `Head` maps 404 to `os.ErrNotExist` and formats restore status. `List` validates returned keys against prefix/start, includes common prefixes, and sorts mixed output. Multipart methods map JuiceFS parts to TOS part structures.

Persistence and integration: data persists in a TOS bucket. `newTOS` parses bucket and region from host segments, creates static credentials with optional token, configures SSL verification and CRC behavior from shared transport/query, and registers as `tos`.

Risks and test signals: multipart `CreateMultipartUpload` advertises 5 MiB minimum while `Limits` says 4 MiB. Endpoint parsing assumes three host segments. No TOS-specific tests are present.
