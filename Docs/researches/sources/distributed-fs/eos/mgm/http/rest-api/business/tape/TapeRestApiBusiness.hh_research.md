## sources/distributed-fs/eos/mgm/http/rest-api/business/tape/TapeRestApiBusiness.hh

Purpose: declares the concrete `TapeRestApiBusiness` implementation of `ITapeRestApiBusiness` and its factory helpers for bulk-request and prepare manager creation.

Important APIs/types/functions: overrides all tape business methods. Protected helpers are `createBulkRequestPrepareManager`, `createPrepareManager`, `createBulkRequestBusiness`, and `checkIssuerAuthorizedToAccessStageBulkRequest`.

Control flow: the public interface is invoked by REST actions; the protected factories centralize construction of EOS bulk/prepare managers so tests can subclass or override if needed. Authorization logic is intentionally factored out for get/cancel/delete operations.

State and persistence: no member fields; all state is created per call. Persistence goes through the returned `BulkRequestBusiness` and `ProcDirectoryDAOFactory` in the `.cc` implementation.

Dependencies and integration points: includes bulk prepare managers, `StageBulkRequest`, and the tape business interface. It sits between `TapeActions` and lower MGM bulk-request subsystems.

Risks and test signals: because helpers are protected rather than injected interfaces, unit tests may need subclass overrides or integration fakes. Access-control tests should target `checkIssuerAuthorizedToAccessStageBulkRequest` indirectly through public methods.
