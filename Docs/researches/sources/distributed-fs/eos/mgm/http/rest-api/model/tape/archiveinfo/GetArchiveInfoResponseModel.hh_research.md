## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/archiveinfo/GetArchiveInfoResponseModel.hh

Purpose: wraps a `bulk::QueryPrepareResponse` for archive-info responses.

Important APIs/types/functions: constructor takes `std::shared_ptr<bulk::QueryPrepareResponse>`; `getQueryPrepareResponse` returns it. Inherits `common::Jsonifiable<GetArchiveInfoResponseModel>`.

Control flow: business `getFileInfo` returns query response; action wraps it in this model and assigns `GetArchiveInfoResponseJsonifier`.

State and persistence: holds shared ownership of query result only; no persistence.

Dependencies and integration points: depends on bulk-request response model and common JSON framework.

Risks and test signals: tests should cover null query response, empty responses vector, error text propagation, and JSON serialization of all fields.
