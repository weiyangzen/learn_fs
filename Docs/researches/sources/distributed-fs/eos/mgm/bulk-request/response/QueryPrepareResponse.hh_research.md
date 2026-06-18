## sources/distributed-fs/eos/mgm/bulk-request/response/QueryPrepareResponse.hh

Purpose: declares the structured response for `xrdfs query prepare`. `QueryPrepareFileResponse` stores per-file status, and `QueryPrepareResponse` stores the request ID and vector of file responses.

Important fields: path, existence, tape state, online state, requested state, request-ID presence, request time, and error text. A legacy `operator<<` emits JSON-like output; the primary JSON path is via `Jsonifiable` and `QueryPrepareResponseJson`.

State/integration: populated by `PrepareManager::doQueryPrepare()` and serialized by MGM query handling. Risks include manual stream serialization without escaping and public mutable fields. Tests should focus on JSON serializer output and query-manager population for error and state combinations.
