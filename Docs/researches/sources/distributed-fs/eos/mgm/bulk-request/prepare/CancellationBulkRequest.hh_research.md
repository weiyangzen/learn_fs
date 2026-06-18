## sources/distributed-fs/eos/mgm/bulk-request/prepare/CancellationBulkRequest.hh

Purpose: declares the cancellation request type used to cancel files in an existing stage bulk request. It derives from `BulkRequest` and returns `PREPARE_CANCEL`.

Important behavior: constructor takes the request ID, normally matching the stage request being canceled. It adds no extra state beyond base files.

Integration: created by `BulkRequestFactory` and `BulkRequestPrepareManager`, saved by business/DAO as mutations to stage proc directories. Risks include no explicit link type beyond reused ID and files, and comments still saying “prepared”. Tests should verify type dispatch and DAO cancellation xattr update behavior.
