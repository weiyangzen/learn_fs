## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreatedStageBulkRequestResponseModel.hh

Purpose: represents the response body returned after successful stage request creation.

Important APIs/types/functions: constructor stores a const request id; `getRequestId` returns it; inherits `Jsonifiable`.

Control flow: create-stage action wraps the created bulk request ID in this model and serializes it through `CreatedStageBulkRequestJsonifier`.

State and persistence: immutable in-memory request id; persisted request state lives in bulk-request storage.

Dependencies and integration points: includes `bulk::BulkRequest` for conceptual linkage and common JSON framework.

Risks and test signals: tests should verify `201 Created`, request ID serialization, and any `Location` headers built by the action/factory path.
