## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeModelBuilders.hh

Purpose: consolidates tape REST request model builders for path-list operations and stage creation.

Important APIs/types/functions: `PathsModelBuilder` accepts either `{"files":[{"path":"..."}]}` or `{"paths":["..."]}` and returns `PathsModel`. `CreateStageRequestModelBuilder` parses `files[].path` plus optional `targeted_metadata` and chooses endpoint-specific `activity` over `default.activity`, converting it to opaque info `activity=<value>`.

Control flow: builders parse JSON into `Json::Value`, validate expected arrays/objects/strings, append files to model containers, and throw `JsonValidationException` on the first invalid condition.

State and persistence: builders are mostly stateless except `CreateStageRequestModelBuilder::mRestApiEndpointId`, normally the site name from config.

Dependencies and integration points: used by `TapeRestHandler` route initialization for create stage, cancel stage, archiveinfo, and release actions. Depends on `FilesContainer` path normalization.

Risks and test signals: path validation is minimal in these builders and does not use `PathValidator`; empty strings may pass for some shapes if only string-ness is checked. `activity` is concatenated into opaque info without escaping, so tests should cover special characters and multiple metadata scopes.
