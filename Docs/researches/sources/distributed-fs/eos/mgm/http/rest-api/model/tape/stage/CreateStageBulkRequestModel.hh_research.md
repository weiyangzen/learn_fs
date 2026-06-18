## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreateStageBulkRequestModel.hh

Purpose: represents a client request to create a stage bulk request.

Important APIs/types/functions: `addFile(path, opaqueInfos)` appends to internal `FilesContainer`; `getFiles` returns it.

Control flow: `CreateStageRequestModelBuilder` populates this model; `TapeRestApiBusiness::createStageBulkRequest` consumes it.

State and persistence: in-memory request model only; persistence is created later through bulk-request business.

Dependencies and integration points: depends on `FilesContainer` for path normalization and opaque metadata alignment.

Risks and test signals: validate that targeted metadata is preserved in opaque infos and that empty or duplicate files behave as expected in prepare manager calls.
