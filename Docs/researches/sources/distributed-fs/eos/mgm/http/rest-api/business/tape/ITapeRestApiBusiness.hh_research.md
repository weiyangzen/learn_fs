## sources/distributed-fs/eos/mgm/http/rest-api/business/tape/ITapeRestApiBusiness.hh

Purpose: declares the abstract business interface behind the WLCG tape REST API. It separates HTTP/action/model handling from tape operations implemented through EOS bulk-request and prepare managers.

Important APIs/types/functions: `ITapeRestApiBusiness` exposes `createStageBulkRequest`, `cancelStageBulkRequest`, `getStageBulkRequest`, `deleteStageBulkRequest`, `getFileInfo`, and `releasePaths`. Inputs are request models (`CreateStageBulkRequestModel`, `PathsModel`) plus `common::VirtualIdentity`; outputs are bulk request objects or response models.

Control flow: this header has no implementation, but it defines the command surface consumed by tape REST actions. Stage creation returns a persisted `bulk::BulkRequest`; cancellation/deletion mutate existing stage requests; archive info and release are query/evict style operations.

State and persistence: persistence is delegated to implementations through `bulk::BulkRequest` and related bulk-request storage. The interface makes caller identity explicit for authorization and namespace checks.

Dependencies and integration points: depends on EOS MGM namespace macros, bulk-request types, query prepare response, tape request models, and `VirtualIdentity`. Implemented by `TapeRestApiBusiness` and injected into `TapeRestHandler` action objects.

Risks and test signals: every implementation should test identity-sensitive behavior, request-not-found behavior, partial cancellation semantics, and prepare-manager return-code mapping because the interface itself does not constrain error categories.
