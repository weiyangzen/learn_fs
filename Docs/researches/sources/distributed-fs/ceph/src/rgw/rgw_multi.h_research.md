## sources/distributed-fs/ceph/src/rgw/rgw_multi.h

Purpose: declares multipart completion XML object classes and upload id helpers.

Important APIs/types: constants `MULTIPART_UPLOAD_ID_PREFIX_LEGACY` and `MULTIPART_UPLOAD_ID_PREFIX`; `RGWMultiCompleteUpload` with `parts`; `RGWMultiPart` with `etag` and `num`; leaf node classes for `PartNumber` and `ETag`; `RGWMultiXMLParser`; `is_v2_upload_id()`.

Control flow: RGW operations feed request XML through `RGWMultiXMLParser`, then read `RGWMultiCompleteUpload::parts` to complete multipart uploads.

State and persistence: classes are temporary parser state. Persistent upload metadata is handled elsewhere through manifests and multipart metadata objects.

Dependencies/integration: includes XML support, object types, compression types, SAL fwd, and RADOS object manifest header.

Risks and test signals: parser classes accept multiple root names for compatibility. Header includes a RADOS-specific manifest dependency marked FIXME, so layering changes should be tested across non-RADOS builds.
