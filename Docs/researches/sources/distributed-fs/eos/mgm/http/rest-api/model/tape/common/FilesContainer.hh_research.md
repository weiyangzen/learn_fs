## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/FilesContainer.hh

Purpose: stores paired path and opaque-info vectors for prepare/query calls.

Important APIs/types/functions: `addFile(path)`, `addFile(path, opaqueInfo)`, `getPaths`, and `getOpaqueInfos`. `addFile` normalizes duplicate slashes in the stored path via `URLParser::removeDuplicateSlashes`.

Control flow: request model builders append files; business logic reads the vectors into `PrepareArgumentsWrapper`.

State and persistence: in-memory vectors; ordering matters because opaque info vector corresponds by index to path vector.

Dependencies and integration points: used by `CreateStageBulkRequestModel` and `PathsModel`; depends on `URLParser`.

Risks and test signals: tests should ensure path/opaque vector sizes remain identical and that duplicate slash normalization does not alter URL schemes or intended double-slash semantics in EOS paths.
