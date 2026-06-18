# sources/distributed-fs/juicefs/pkg/object/qiniu.go

Purpose: implements a Qiniu backend that combines Qiniu native APIs with an embedded S3-compatible client for selected operations.

Important APIs and types: `qiniu` embeds `s3client` and holds a Qiniu `BucketManager`, credentials, config, and marker. It implements `String`, disabled tier init, limited `Limits`, native `Head`, `Put`, `Copy`, `Delete`, `List`, and a custom private-domain `download`; normal `Get` can delegate to S3 unless the key begins with `/` and `QINIU_DOMAIN` is set. Multipart upload is explicitly unsupported.

Control flow and state: `newQiniu` parses the bucket from the host and infers region from endpoint naming, builds an AWS S3 client for Qiniu's S3 endpoint, then configures Qiniu zone/upload hosts. Native `Put` calculates length with `findLen` and uses form upload. `List` filters entries and prefixes by `startAfter`, sorts when delimiter is used, and clears continuation if a page yields no visible objects.

Persistence and integration: data persists in one Qiniu bucket. The backend registers as `qiniu` and depends on both `!noqiniu` and `!nos3` build tags.

Risks and test signals: endpoint/region inference is string-based and brittle. Multipart and tier semantics are mostly disabled. Private-domain download requires `QINIU_DOMAIN`, and request attributes are not propagated on native paths. No Qiniu-specific tests are present.
