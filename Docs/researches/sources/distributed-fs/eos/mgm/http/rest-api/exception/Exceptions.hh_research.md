## sources/distributed-fs/eos/mgm/http/rest-api/exception/Exceptions.hh

Purpose: provides the consolidated REST exception hierarchy and includes JSON validation plus tape-specific business exceptions.

Important APIs/types/functions: defines `NotFoundException`, `MethodNotAllowedException`, `ForbiddenException`, `NotImplementedException`, `ObjectNotFoundException`, `ActionNotFoundException`, `ControllerNotFoundException`, `TapeRestApiBusinessException`, and `FileDoesNotBelongToBulkRequestException`, all ultimately deriving from `RestException`.

Control flow: these exceptions are thrown by routing, handlers, model builders, and business logic. `ErrorHandling.hh` and `WellKnownHandler` catch selected types and translate them into HTTP responses.

State and persistence: no mutable state beyond the inherited exception message.

Dependencies and integration points: includes `RestException.hh` and `JsonValidationException.hh`; used by REST router, tape business, JSON builders, response factory, and well-known handler.

Risks and test signals: exception granularity determines HTTP mapping. `FileDoesNotBelongToBulkRequestException` derives directly from `RestException`, so centralized handling maps it to 500 unless action-level code maps it earlier; tests should confirm intended client status for malformed path subsets.
