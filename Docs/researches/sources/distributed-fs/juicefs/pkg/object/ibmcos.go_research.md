# sources/distributed-fs/juicefs/pkg/object/ibmcos.go


Purpose: implements IBM Cloud Object Storage behind `!noibmcos`, registering `ibmcos`.

Important APIs and flow: `ibmcos` directly uses IBM's S3-compatible SDK. It supports create, limits, get, restore, put, copy, head, delete, list, multipart upload, upload part, abort, complete, and list uploads. `Put` ensures an `io.ReadSeeker`, guesses content type, applies storage class and encoded tags, and captures request ID. `List` decodes URL-encoded keys and common prefixes. Multipart copy is explicitly unsupported.

State and persistence: bucket objects, storage class, restore status, tags, and multipart uploads persist in IBM COS. Local state is bucket, S3 client, and tier config.

Dependencies and integration: uses `github.com/IBM/ibm-cos-sdk-go`, IAM static credentials, shared `Tier`, `decodeKey`, and `DefaultStorageClass`. `newIBMCOS` parses bucket and region from host labels and creates IAM credentials from API key and service instance ID arguments.

Risks: endpoint parsing assumes a specific IBM COS hostname layout. `newIBMCOS` ignores the URL parse error. Context is not used for `Create`/`Restore`. Non-seekable puts buffer the full object. List upload time parsing has a FIXME. Upload-part-copy is not supported even though other S3-like stores may support it.

Test signals: `TestIBMCOS` is environment-gated on `IBMCOS_ENDPOINT` and then runs shared storage tests.
