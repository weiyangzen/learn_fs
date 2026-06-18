# Research: subset-b-007035

This grouped report covers the EOS MGM REST tape API, its shared REST response/routing/model utilities, and the adjacent WebDAV HTTP handler/response implementation. Each file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/business/tape/ITapeRestApiBusiness.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/business/tape/ITapeRestApiBusiness.hh

Purpose: declares the abstract business interface behind the WLCG tape REST API. It separates HTTP/action/model handling from tape operations implemented through EOS bulk-request and prepare managers.

Important APIs/types/functions: `ITapeRestApiBusiness` exposes `createStageBulkRequest`, `cancelStageBulkRequest`, `getStageBulkRequest`, `deleteStageBulkRequest`, `getFileInfo`, and `releasePaths`. Inputs are request models (`CreateStageBulkRequestModel`, `PathsModel`) plus `common::VirtualIdentity`; outputs are bulk request objects or response models.

Control flow: this header has no implementation, but it defines the command surface consumed by tape REST actions. Stage creation returns a persisted `bulk::BulkRequest`; cancellation/deletion mutate existing stage requests; archive info and release are query/evict style operations.

State and persistence: persistence is delegated to implementations through `bulk::BulkRequest` and related bulk-request storage. The interface makes caller identity explicit for authorization and namespace checks.

Dependencies and integration points: depends on EOS MGM namespace macros, bulk-request types, query prepare response, tape request models, and `VirtualIdentity`. Implemented by `TapeRestApiBusiness` and injected into `TapeRestHandler` action objects.

Risks and test signals: every implementation should test identity-sensitive behavior, request-not-found behavior, partial cancellation semantics, and prepare-manager return-code mapping because the interface itself does not constrain error categories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/business/tape/ITapeRestApiBusiness.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/business/tape/TapeRestApiBusiness.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/business/tape/TapeRestApiBusiness.cc

Purpose: implements tape REST business operations by translating request models into EOS prepare/bulk-request calls. It is the main bridge from REST actions to MGM tape staging, cancellation, query, deletion, archive-info, and release/evict behavior.

Important APIs/types/functions: `createStageBulkRequest` builds `PrepareArgumentsWrapper("fake_id", Prep_STAGE, paths, opaqueInfos)` and expects `SFS_DATA`; `cancelStageBulkRequest` loads a stage bulk request, authorizes issuer/root access, verifies each requested path belongs to the request, and calls `Prep_CANCEL`; `getStageBulkRequest` loads a persisted `StageBulkRequest`, authorizes, queries current prepare status, and fills `GetStageBulkRequestResponseModel`; `deleteStageBulkRequest` cancels all paths then deletes the persistency entry; `getFileInfo` runs `Prep_QUERY`; `releasePaths` runs `Prep_EVICT`.

Control flow: all public methods add MGM stats and timing. Stage/create/release create prepare managers over `RealMgmFileSystemInterface(gOFS)`. Cancel and delete first retrieve bulk-request state through `BulkRequestBusiness`, then run prepare cancellation only after local validation. Query maps CTA/EOS prepare responses back to REST model file entries, preferring persisted bulk-request file errors, then CTA `error_text`, then missing request-id errors.

State and persistence: persisted stage requests are accessed through `BulkRequestBusiness` created with `ProcDirectoryDAOFactory(gOFS, *gOFS->mProcDirectoryBulkRequestTapeRestApiLocations)`. Delete mutates both the live prepare state and the proc-directory bulk-request persistency. No state is cached in the business object.

Dependencies and integration points: depends heavily on global `gOFS`, MGM stats, `BulkRequestPrepareManager`, `PrepareManager`, `BulkRequestBusiness`, `ProcDirectoryDAOFactory`, and XRootD `XrdOucErrInfo`. REST exceptions (`ObjectNotFoundException`, `ForbiddenException`, `TapeRestApiBusinessException`, `FileDoesNotBelongToBulkRequestException`) are translated later by response factories.

Risks and test signals: authorization is enforced for get/cancel/delete by `checkIssuerAuthorizedToAccessStageBulkRequest`, allowing root or the original issuer uid; tests should cover unauthorized uid returning forbidden, nonexistent IDs, path-not-in-request cancellation, empty cancellation subsets, prepare return-code failures, persistency exceptions, and CTA query error text. A remaining risk is uid-only authorization: gid, auth protocol, and identity realm are not considered. Another risk is that stage and release rely on `fake_id`; tests should confirm underlying prepare managers ignore or replace that ID safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/business/tape/TapeRestApiBusiness.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/business/tape/TapeRestApiBusiness.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/business/tape/TapeRestApiBusiness.hh

Purpose: declares the concrete `TapeRestApiBusiness` implementation of `ITapeRestApiBusiness` and its factory helpers for bulk-request and prepare manager creation.

Important APIs/types/functions: overrides all tape business methods. Protected helpers are `createBulkRequestPrepareManager`, `createPrepareManager`, `createBulkRequestBusiness`, and `checkIssuerAuthorizedToAccessStageBulkRequest`.

Control flow: the public interface is invoked by REST actions; the protected factories centralize construction of EOS bulk/prepare managers so tests can subclass or override if needed. Authorization logic is intentionally factored out for get/cancel/delete operations.

State and persistence: no member fields; all state is created per call. Persistence goes through the returned `BulkRequestBusiness` and `ProcDirectoryDAOFactory` in the `.cc` implementation.

Dependencies and integration points: includes bulk prepare managers, `StageBulkRequest`, and the tape business interface. It sits between `TapeActions` and lower MGM bulk-request subsystems.

Risks and test signals: because helpers are protected rather than injected interfaces, unit tests may need subclass overrides or integration fakes. Access-control tests should target `checkIssuerAuthorizedToAccessStageBulkRequest` indirectly through public methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/business/tape/TapeRestApiBusiness.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.cc

Purpose: implements in-memory configuration for the tape REST API, including access URL, site name, activation flags, tape-enabled flag, endpoint-to-URL overrides, host alias, xrootd HTTP port, and stage enablement.

Important APIs/types/functions: constructors default `mAccessURL` to `/api/` or accept a custom access URL. Setters/getters exist for site name, activated state, tape-enabled state, host alias, endpoint mapping, XrdHttp port, access URL, and stage-enabled state.

Control flow: setters mutate the relevant field; string/map fields take write locks and getters take read locks. Atomic bool/port fields are read/written directly. `getAccessURL` returns a const reference without locking because the access URL is immutable after construction.

State and persistence: configuration is purely process-local and not persisted here. Values are populated by `RestApiManager`/MGM configuration code elsewhere and consumed when handlers are instantiated.

Dependencies and integration points: uses `common::RWMutex` lock guards and atomics. `TapeRestHandler` consults this object for request acceptance, route construction, `.well-known` endpoint URLs, host alias, port, and site name.

Risks and test signals: `mXrdHttpPort` is atomic but not initialized in the header, so tests should verify config population before `.well-known` URL construction. Endpoint map copies are protected, but no validation is performed on version strings or URLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.hh

Purpose: defines `TapeRestApiConfig`, the shared configuration object used by REST manager and tape handlers.

Important APIs/types/functions: exposes setters/getters for site name, activation, tape-enabled, host alias, endpoint mapping, XrdHttp port, access URL, and stage-enabled. Internals include `mSiteName`, `mAccessURL`, `mHostAlias`, `mTapeRestApiEndpointUrlMap`, `mIsActivated`, `mTapeEnabled`, `mXrdHttpPort`, `mConfigMutex`, and `mStageEnabled`.

Control flow: the class is a mutable configuration holder; request handling calls are expected to read it frequently, while MGM config reload paths may update it.

State and persistence: state is resident in memory and shared by pointer from `RestApiManager`. String/map state is mutex-protected; activation booleans and port use atomics.

Dependencies and integration points: depends on `mgm/Namespace.hh`, `common/RWMutex.hh`, `<atomic>`, and STL string/map. It controls `TapeRestHandler::isRestRequest` gating and `.well-known` URL generation.

Risks and test signals: validate default disabled behavior, explicit activation, tape-enabled gating, missing host alias/site name messages, stage-enabled behavior in action code, and endpoint override handling. The port field should be initialized before use in URL builders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/exception/Exceptions.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/exception/Exceptions.hh

Purpose: provides the consolidated REST exception hierarchy and includes JSON validation plus tape-specific business exceptions.

Important APIs/types/functions: defines `NotFoundException`, `MethodNotAllowedException`, `ForbiddenException`, `NotImplementedException`, `ObjectNotFoundException`, `ActionNotFoundException`, `ControllerNotFoundException`, `TapeRestApiBusinessException`, and `FileDoesNotBelongToBulkRequestException`, all ultimately deriving from `RestException`.

Control flow: these exceptions are thrown by routing, handlers, model builders, and business logic. `ErrorHandling.hh` and `WellKnownHandler` catch selected types and translate them into HTTP responses.

State and persistence: no mutable state beyond the inherited exception message.

Dependencies and integration points: includes `RestException.hh` and `JsonValidationException.hh`; used by REST router, tape business, JSON builders, response factory, and well-known handler.

Risks and test signals: exception granularity determines HTTP mapping. `FileDoesNotBelongToBulkRequestException` derives directly from `RestException`, so centralized handling maps it to 500 unless action-level code maps it earlier; tests should confirm intended client status for malformed path subsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/exception/Exceptions.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/exception/JsonValidationException.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/exception/JsonValidationException.hh

Purpose: represents JSON parse or schema validation failures and optionally carries structured validation errors.

Important APIs/types/functions: constructors accept a simple message or `std::unique_ptr<ValidationErrors>`. `getValidationErrors() const` exposes a raw const pointer, while the non-const overload moves ownership out.

Control flow: JSON model builders throw this exception when request bodies are invalid. `RestResponseFactory::BadRequest(const JsonValidationException&)` inspects the first validation error when present.

State and persistence: owns an optional `ValidationErrors` vector through `unique_ptr`; moving errors out makes subsequent access null.

Dependencies and integration points: depends on `RestException` and `ValidationError.hh`. Integrated with response factory error body generation.

Risks and test signals: tests should cover malformed JSON, missing fields, structured validation errors, and repeated access after move. The overload that moves the errors can surprise callers if used before response generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/exception/JsonValidationException.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/exception/RestException.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/exception/RestException.hh

Purpose: defines the base exception type for REST API errors.

Important APIs/types/functions: `RestException` derives from `common::Exception` and forwards a message string to the base class.

Control flow: derived exceptions are thrown through routing, validation, and business layers and caught by centralized error handling.

State and persistence: only stores inherited exception message/state.

Dependencies and integration points: depends on EOS namespace macros and `common/exception/Exception.hh`; included by all REST exception headers.

Risks and test signals: because generic `RestException` maps to internal server error in `HandleWithErrors`, new client-caused exceptions should derive from a more specific class or receive explicit catch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/exception/RestException.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.cc

Purpose: implements the base REST handler entrypoint validation and request-prefix matching.

Important APIs/types/functions: constructor calls `verifyRestApiEntryPoint`; `isRestRequest` uses `URLParser::startsBy`; `getEntryPointURL` returns the configured base path. The allowed entrypoint regex is `^\/(\.?[a-z0-9-]+)+\/$`.

Control flow: every concrete REST handler is constructed with an entrypoint, validated immediately, then asked by the manager whether a URL should be handled.

State and persistence: stores only `mEntryPointURL`.

Dependencies and integration points: uses `URLParser`, `common::RegexWrapper`, logging, and REST exceptions. Base class for `TapeRestHandler` and `WellKnownHandler`.

Risks and test signals: test valid and invalid entrypoints, prefix matching with duplicate slashes or boundary-like paths, and error messages for malformed config. The regex admits `.well-known` style paths and lower-case alphanumeric/hyphen tokens only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.hh

Purpose: declares the abstract base class for REST HTTP handlers.

Important APIs/types/functions: pure virtual `handleRequest(HttpRequest*, const VirtualIdentity*)`; virtual `isRestRequest`; `getEntryPointURL`; protected `mEntryPointURL`; private entrypoint verifier.

Control flow: `RestApiManager` creates concrete handlers and calls `isRestRequest`/`handleRequest` depending on URL routing.

State and persistence: no persistent storage beyond entrypoint string.

Dependencies and integration points: depends on common HTTP request/response classes, `VirtualIdentity`, and XrdHttp handler types. Extended by tape and well-known handlers.

Risks and test signals: concrete handlers own raw `HttpResponse*` return semantics; tests should confirm response ownership expectations at the higher HTTP server layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.cc

Purpose: wires the tape REST API routes, versioning, `.well-known` metadata, configuration gating, master-only enforcement, and centralized error mapping.

Important APIs/types/functions: `apiVersionToStr` maps `V0Dot1` and `V1`; constructor initializes well-known info, default version routes, and endpoint overrides; `initialize` creates `TapeRestApiBusiness`; `initializeStageRoutes`, `initializeArchiveinfoRoutes`, and `initializeReleaseRoutes` create action objects and register router lambdas; `isRestRequest` checks config gates; `handleRequest` rejects non-master MGM and dispatches via `HandleWithErrors`; `getAccessURLBuilder` creates `https://host:port/...`; `getWellKnownInfos` exposes discovery data.

Control flow: default version is `v1`. V1 exposes stage, archiveinfo, and release; v0.1 exposes archiveinfo/release but no stage if initialized. Actions are stored in `mActions` to keep router lambda targets alive. Requests are routed only after config-level acceptance and master check.

State and persistence: handler state is per-instantiation: config pointer, response factory, router, action vector, and well-known info. It does not persist tape state; business layer does.

Dependencies and integration points: integrates `TapeActions.hh`, `TapeRestApiBusiness`, JSON builders/jsonifiers, `Router`, `RestResponseFactory`, MGM master state, and `TapeRestApiConfig`.

Risks and test signals: route strings use both `controllerAccessURL` ending in `/` and additions like `"/" + URLPARAM_ID`, which can produce duplicate slashes; route matching and `FilesContainer` slash normalization should be tested. `mStageEnabled` is not checked in `isRestRequest`; confirm stage disabling is enforced in action code or add handler tests. Non-master returns 500 rather than redirect or 403; verify desired behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.hh

Purpose: declares the concrete REST handler for WLCG tape API requests.

Important APIs/types/functions: public constructor, `handleRequest`, `isRestRequest`, `getAccessURLBuilder`, and `getWellKnownInfos`. Private `ApiVersion`, `DEFAULT_API_VERSION`, route initialization helpers, well-known helpers, response factory, config pointer, router, action storage, and well-known info.

Control flow: the handler owns route initialization and delegates request execution to action objects via `Router`.

State and persistence: holds handler-local routing/action/discovery state; config is borrowed by pointer and must outlive the handler.

Dependencies and integration points: depends on `RestHandler`, tape business interface, `Router`, `Action`, `RestResponseFactory`, `TapeRestApiConfig`, `URLBuilder`, and `TapeWellKnownInfos`.

Risks and test signals: tests should verify object lifetime of action lambdas, default endpoint generation, config gating, and behavior when endpoint override mapping contains unsupported versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.cc

Purpose: implements the `/.well-known/wlcg-tape-rest-api` endpoint for tape REST API discovery.

Important APIs/types/functions: constructor stores `RestApiManager` and registers routes. `handleRequest` dispatches and maps not found/method/unknown exceptions. `initializeRoutes` registers a GET handler that creates a tape handler from the manager, extracts `TapeWellKnownInfos`, verifies tape API availability through `isRestRequest`, wraps it in `GetTapeWellKnownModel`, and returns JSON.

Control flow: request enters router; route lambda re-instantiates a `TapeRestHandler` using current config, checks whether tape REST API itself is enabled, and serializes well-known versions/URLs.

State and persistence: stores manager pointer, response factory, router, and unused action vector. No persistent state; discovery info is derived dynamically from config.

Dependencies and integration points: depends on manager, tape handler, tape well-known model/jsonifier, router, response factory, and REST exceptions.

Risks and test signals: lambda uses `static_cast<TapeRestHandler*>` after requesting a handler for tape access URL; this assumes manager mapping cannot change to another handler. Availability failure returns 500 with config error detail. Tests should cover disabled tape API, endpoint overrides, method not allowed, and invalid manager return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.hh

Purpose: declares the REST handler for `.well-known` discovery routes.

Important APIs/types/functions: constructor, `handleRequest`, private `initializeRoutes`, manager pointer, response factory, router, and action vector.

Control flow: extends `RestHandler` and routes discovery requests through `Router`.

State and persistence: no persistent storage; keeps a non-owning `RestApiManager` pointer.

Dependencies and integration points: includes `RestHandler`, `RestResponseFactory`, `Router`, `Action`, and `TapeRestHandler`; forward declares `RestApiManager`.

Risks and test signals: manager pointer lifetime is critical. The `mActions` vector is present but unused in this implementation, so tests should focus on router behavior rather than action lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/JsonModelBuilder.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/JsonModelBuilder.hh

Purpose: defines the generic interface for building typed request models from JSON strings.

Important APIs/types/functions: template `JsonModelBuilder<Model>` with pure virtual `std::unique_ptr<Model> buildFromJson(const std::string&)` and virtual destructor.

Control flow: REST actions own or receive model builders and call `buildFromJson` before invoking business logic.

State and persistence: stateless abstract interface.

Dependencies and integration points: base for `JsonCppModelBuilder` and tape-specific builders in `TapeModelBuilders.hh`.

Risks and test signals: implementations are responsible for all validation and exception consistency. Tests should exercise builder polymorphism through action code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/JsonModelBuilder.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/ValidationError.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/ValidationError.hh

Purpose: provides small structures for structured JSON validation errors.

Important APIs/types/functions: `ValidationError` stores `fieldName` and `reason`; `ValidationErrors` owns a vector of `unique_ptr<ValidationError>` and exposes `addError`, `getErrors`, and `hasAnyError`.

Control flow: validators/builders can accumulate errors and pass them into `JsonValidationException`.

State and persistence: in-memory ownership of error objects only.

Dependencies and integration points: used by `JsonValidationException` and `RestResponseFactory::BadRequest` for client error details.

Risks and test signals: only the first validation error is emitted by the current response factory. Tests should verify ordering, empty error lists, and move-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/ValidationError.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppModelBuilder.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppModelBuilder.hh

Purpose: adds JsonCPP parsing support to the generic model-builder interface.

Important APIs/types/functions: template `JsonCppModelBuilder<Model>` inherits `JsonModelBuilder<Model>`, leaves `buildFromJson` abstract, and provides protected `parseJson(json, Json::Value&)`.

Control flow: `parseJson` uses `Json::Reader::parse` and throws `JsonValidationException` with the original JSON string if parsing fails.

State and persistence: stateless helper.

Dependencies and integration points: includes JsonCPP, REST exceptions, and validation errors. Tape request builders inherit it.

Risks and test signals: parse errors include full request JSON in exception detail, which can leak sensitive metadata into logs/responses. Tests should cover malformed JSON and ensure callers map exceptions to 400 rather than 500.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppModelBuilder.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppValidator.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppValidator.hh

Purpose: defines reusable JsonCPP validators and a factory for basic JSON field validation.

Important APIs/types/functions: `ValidatorException`; abstract `JsonCppValidator::validate`; concrete `NonEmptyArrayValidator`, `StringValidator`, `ObjectValidator`; `JsonCppValidatorFactory` factory methods.

Control flow: validators throw `ValidatorException` on invalid shape. Factories allocate validators as `unique_ptr`.

State and persistence: validators are stateless.

Dependencies and integration points: intended for model builders and extended by tape-specific validator factory.

Risks and test signals: `getNotNullValidator` returns `StringValidator`, so it validates string-ness rather than general non-null. Tests should verify factory semantics before relying on it for object or scalar fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppValidator.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeJsonifiers.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeJsonifiers.hh

Purpose: consolidates JSON serializers for tape REST API response models and errors.

Important APIs/types/functions: `ErrorModelJsonifier`, `CreatedStageBulkRequestJsonifier`, `GetStageBulkRequestJsonifier`, `GetArchiveInfoResponseJsonifier`, and `GetTapeWellKnownModelJsonifier`, all implementing `jsonify`.

Control flow: response models receive a jsonifier via `setJsonifier`; `RestApiResponse` calls `model->jsonify`. Serializers manually stream JSON object and array syntax.

State and persistence: serializers are stateless; they read model fields and stream output.

Dependencies and integration points: integrates error models, stage response models, archive info query responses, and well-known endpoint models with the common `Jsonifiable` response path.

Risks and test signals: string values are written directly without JSON escaping, including paths, errors, site URLs, CTA error text, and request IDs. Tests should include quotes, backslashes, control characters, and non-ASCII paths. Archive-info null response produces `{}`; verify clients tolerate that.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeJsonifiers.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeModelBuilders.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeModelBuilders.hh

Purpose: consolidates tape REST request model builders for path-list operations and stage creation.

Important APIs/types/functions: `PathsModelBuilder` accepts either `{"files":[{"path":"..."}]}` or `{"paths":["..."]}` and returns `PathsModel`. `CreateStageRequestModelBuilder` parses `files[].path` plus optional `targeted_metadata` and chooses endpoint-specific `activity` over `default.activity`, converting it to opaque info `activity=<value>`.

Control flow: builders parse JSON into `Json::Value`, validate expected arrays/objects/strings, append files to model containers, and throw `JsonValidationException` on the first invalid condition.

State and persistence: builders are mostly stateless except `CreateStageRequestModelBuilder::mRestApiEndpointId`, normally the site name from config.

Dependencies and integration points: used by `TapeRestHandler` route initialization for create stage, cancel stage, archiveinfo, and release actions. Depends on `FilesContainer` path normalization.

Risks and test signals: path validation is minimal in these builders and does not use `PathValidator`; empty strings may pass for some shapes if only string-ness is checked. `activity` is concatenated into opaque info without escaping, so tests should cover special characters and multiple metadata scopes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeModelBuilders.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeRestApiJsonifier.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeRestApiJsonifier.hh

Purpose: defines the tape-specific JSON serializer interface over the common EOS `Jsonifier`.

Important APIs/types/functions: template `TapeRestApiJsonifier<Obj>` inherits `common::Jsonifier<Obj>` and requires `void jsonify(const Obj*, std::stringstream&)`.

Control flow: concrete jsonifiers implement this interface and are attached to `Jsonifiable` models.

State and persistence: stateless interface.

Dependencies and integration points: used by tape JSON serializers and response models returned by `RestApiResponse`.

Risks and test signals: the interface does not enforce escaping or content type; tests should validate concrete serializers through HTTP response bodies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeRestApiJsonifier.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/model-builders/validators/TapeJsonCppValidator.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/model-builders/validators/TapeJsonCppValidator.hh

Purpose: defines tape-specific JsonCPP validation for path-like request values.

Important APIs/types/functions: `PathValidator::validate` requires a non-empty string and rejects values convertible to JsonCPP `intValue`; `TapeJsonCppValidatorFactory::getPathValidator` returns it.

Control flow: intended for model builders to validate file path fields before adding them to models.

State and persistence: stateless validator.

Dependencies and integration points: extends `JsonCppValidatorFactory`, includes common path/string utilities, and can be used by tape request model builders.

Risks and test signals: current consolidated builders do not appear to call this validator directly, so path validation coverage may be weaker than intended. Tests should include empty strings, numeric JSON values, numeric-looking strings, and malformed path forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/json/tape/model-builders/validators/TapeJsonCppValidator.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.cc

Purpose: implements the REST API manager that owns tape REST configuration and creates handlers based on request URL prefixes.

Important APIs/types/functions: constructor creates `TapeRestApiConfig`, registers a factory for its access URL and one for `/.well-known/`; `isRestRequest` asks the matching handler whether it accepts the URL; `getTapeRestApiConfig` returns the mutable config pointer; `getRestHandler` finds the first access URL whose prefix matches; `getWellKnownAccessURL` returns `/.well-known/`.

Control flow: no handler instances are cached; a new handler is created for each query/dispatch path. Prefix matching is performed through `URLParser::startsBy`.

State and persistence: owns config and a map of URL prefixes to handler factories. No persistent storage.

Dependencies and integration points: integrates `TapeRestHandler`, `WellKnownHandler`, `TapeRestApiConfig`, and `URLParser`.

Risks and test signals: `std::map` iteration order controls prefix selection; overlapping prefixes should be tested. Recreating handlers per request rebuilds routes and well-known info each time, so performance and config consistency should be monitored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.hh

Purpose: declares the top-level manager for REST APIs served by the MGM HTTP layer.

Important APIs/types/functions: `isRestRequest`, `getTapeRestApiConfig`, `getRestHandler`, and `getWellKnownAccessURL`; private `mTapeRestApiConfig`, `mMapAccessURLRestHandlerCreator`, and unused-looking `mWellKnownAccessURL`.

Control flow: external HTTP integration asks this manager to recognize REST requests and obtain the right handler.

State and persistence: owns tape config for process lifetime; handler instances are produced on demand.

Dependencies and integration points: depends on `RestHandler` and `TapeRestApiConfig`; concrete handlers are registered in the `.cc`.

Risks and test signals: `getTapeRestApiConfig` returns mutable raw pointer, so config mutation is unconstrained. Tests should cover lifecycle and thread-safety expectations for concurrent reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/archiveinfo/GetArchiveInfoResponseModel.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/archiveinfo/GetArchiveInfoResponseModel.hh

Purpose: wraps a `bulk::QueryPrepareResponse` for archive-info responses.

Important APIs/types/functions: constructor takes `std::shared_ptr<bulk::QueryPrepareResponse>`; `getQueryPrepareResponse` returns it. Inherits `common::Jsonifiable<GetArchiveInfoResponseModel>`.

Control flow: business `getFileInfo` returns query response; action wraps it in this model and assigns `GetArchiveInfoResponseJsonifier`.

State and persistence: holds shared ownership of query result only; no persistence.

Dependencies and integration points: depends on bulk-request response model and common JSON framework.

Risks and test signals: tests should cover null query response, empty responses vector, error text propagation, and JSON serialization of all fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/archiveinfo/GetArchiveInfoResponseModel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.cc

Purpose: implements the RFC 7807-like error model used by REST error responses.

Important APIs/types/functions: constructors set title/status/detail; setters for type/title/status/detail; getters return optional type/detail and scalar fields.

Control flow: `RestResponseFactory::makeError` constructs and jsonifies `ErrorModel` for HTTP error responses.

State and persistence: stores title, status, optional detail, and optional type in memory.

Dependencies and integration points: paired with `ErrorModelJsonifier` and response factory.

Risks and test signals: string fields are serialized manually by `ErrorModelJsonifier`; tests should include quotes/newlines in details and verify RFC 7807 content expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.hh

Purpose: declares the JSON-serializable error response model for REST API failures.

Important APIs/types/functions: `ErrorModel` inherits `common::Jsonifiable<ErrorModel>`; exposes constructors, setters, getters, and optional `type`/`detail`.

Control flow: response factory creates and returns these models for 400/403/404/405/500 etc.

State and persistence: in-memory error payload only.

Dependencies and integration points: used by `RestResponseFactory` and `ErrorModelJsonifier`.

Risks and test signals: default constructor can leave title/status unset until populated; tests should avoid serializing partially initialized models unless intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/FilesContainer.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/FilesContainer.hh

Purpose: stores paired path and opaque-info vectors for prepare/query calls.

Important APIs/types/functions: `addFile(path)`, `addFile(path, opaqueInfo)`, `getPaths`, and `getOpaqueInfos`. `addFile` normalizes duplicate slashes in the stored path via `URLParser::removeDuplicateSlashes`.

Control flow: request model builders append files; business logic reads the vectors into `PrepareArgumentsWrapper`.

State and persistence: in-memory vectors; ordering matters because opaque info vector corresponds by index to path vector.

Dependencies and integration points: used by `CreateStageBulkRequestModel` and `PathsModel`; depends on `URLParser`.

Risks and test signals: tests should ensure path/opaque vector sizes remain identical and that duplicate slash normalization does not alter URL schemes or intended double-slash semantics in EOS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/FilesContainer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreateStageBulkRequestModel.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreateStageBulkRequestModel.hh

Purpose: represents a client request to create a stage bulk request.

Important APIs/types/functions: `addFile(path, opaqueInfos)` appends to internal `FilesContainer`; `getFiles` returns it.

Control flow: `CreateStageRequestModelBuilder` populates this model; `TapeRestApiBusiness::createStageBulkRequest` consumes it.

State and persistence: in-memory request model only; persistence is created later through bulk-request business.

Dependencies and integration points: depends on `FilesContainer` for path normalization and opaque metadata alignment.

Risks and test signals: validate that targeted metadata is preserved in opaque infos and that empty or duplicate files behave as expected in prepare manager calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreateStageBulkRequestModel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreatedStageBulkRequestResponseModel.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreatedStageBulkRequestResponseModel.hh

Purpose: represents the response body returned after successful stage request creation.

Important APIs/types/functions: constructor stores a const request id; `getRequestId` returns it; inherits `Jsonifiable`.

Control flow: create-stage action wraps the created bulk request ID in this model and serializes it through `CreatedStageBulkRequestJsonifier`.

State and persistence: immutable in-memory request id; persisted request state lives in bulk-request storage.

Dependencies and integration points: includes `bulk::BulkRequest` for conceptual linkage and common JSON framework.

Risks and test signals: tests should verify `201 Created`, request ID serialization, and any `Location` headers built by the action/factory path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/CreatedStageBulkRequestResponseModel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/GetStageBulkRequestResponseModel.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/GetStageBulkRequestResponseModel.hh

Purpose: holds the status response for a previously submitted stage bulk request.

Important APIs/types/functions: nested `File` contains `mPath`, `mError`, and `mOnDisk`; model has `addFile`, `getFiles`, `getCreationTime`, `getId`, `setCreationTime`, and `setId`.

Control flow: `TapeRestApiBusiness::getStageBulkRequest` fills request metadata and one `File` entry per query response matching persisted request files.

State and persistence: in-memory response only; it reflects persisted bulk request plus live query-prepare state at response time.

Dependencies and integration points: jsonified by `GetStageBulkRequestJsonifier`; uses bulk request/query response types.

Risks and test signals: `mCreationTime` and `mOnDisk` are uninitialized until explicitly set. Tests should verify no default model is serialized and that query responses for unknown files are ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/GetStageBulkRequestResponseModel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/PathsModel.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/PathsModel.hh

Purpose: represents a list of paths for archiveinfo, release, and stage cancellation operations.

Important APIs/types/functions: `addFile(path)` and `getFiles`.

Control flow: `PathsModelBuilder` populates it from JSON; business methods consume its `FilesContainer`.

State and persistence: in-memory path list only.

Dependencies and integration points: uses `FilesContainer`, so paths are duplicate-slash-normalized.

Risks and test signals: tests should cover accepted JSON shapes, path normalization, empty lists, duplicate paths, and cancellation paths not in request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/tape/stage/PathsModel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/wellknown/tape/GetTapeWellKnownModel.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/model/wellknown/tape/GetTapeWellKnownModel.hh

Purpose: wraps `TapeWellKnownInfos` for JSON serialization by the well-known endpoint.

Important APIs/types/functions: constructor stores a const pointer; `getTapeWellKnownInfos` returns it; inherits `Jsonifiable`.

Control flow: `WellKnownHandler` creates this model after validating tape API availability and assigns `GetTapeWellKnownModelJsonifier`.

State and persistence: borrowed pointer only; caller must ensure `TapeWellKnownInfos` outlives serialization.

Dependencies and integration points: depends on tape well-known info classes and common JSON framework.

Risks and test signals: because it stores a raw pointer to handler-owned state, tests should ensure response serialization occurs before handler destruction and not asynchronously afterward.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/model/wellknown/tape/GetTapeWellKnownModel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/ErrorHandling.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/response/ErrorHandling.hh

Purpose: centralizes exception-to-HTTP-response mapping for REST handlers.

Important APIs/types/functions: template `HandleWithErrors(ResponseFactory&, Fn)` catches `NotFoundException`, `MethodNotAllowedException`, `ForbiddenException`, `NotImplementedException`, generic `RestException`, and unknown exceptions.

Control flow: handler passes a lambda that may throw; helper logs and returns response factory outputs. Specific exceptions map to 404, 405, 403, 501; generic REST and unknown map to 500.

State and persistence: stateless function template.

Dependencies and integration points: used by `TapeRestHandler::handleRequest`; depends on response factory methods and REST exception hierarchy.

Risks and test signals: `JsonValidationException` currently derives from `RestException` but is not caught before generic `RestException` here, so if action code does not catch it, invalid JSON becomes 500. Tests should verify action-level handling or add a catch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/ErrorHandling.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponse.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponse.hh

Purpose: converts JSON-serializable models into `PlainHttpResponse` objects with status codes and optional headers.

Important APIs/types/functions: template constructors with code/model/headers; `getHttpResponse`; static `createResponse`; `void` specialization returns empty response body.

Control flow: for non-null models, creates `PlainHttpResponse`, sets header `application/type: json`, calls `mModel->jsonify`, sets body and response code. For `void`, only sets response code.

State and persistence: stores shared model, return code, and mutable header map until response creation. Allocates raw `HttpResponse*` for caller ownership.

Dependencies and integration points: used by `RestResponseFactory` for success and error responses.

Risks and test signals: header key appears to be `application/type` rather than `Content-Type`; tests should confirm clients receive expected JSON content type. Raw pointer allocation requires HTTP server ownership discipline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponse.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponseFactory.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponseFactory.hh

Purpose: compatibility header that redirects deprecated `RestApiResponseFactory.hh` includes to `RestResponseFactory.hh`.

Important APIs/types/functions: only include guard and include of `RestResponseFactory.hh`.

Control flow: no runtime behavior.

State and persistence: no state.

Dependencies and integration points: preserves older include paths during consolidation.

Risks and test signals: build tests should ensure legacy includes still compile and do not define conflicting factory names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponseFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.cc

Purpose: implements consolidated REST response factory error helpers.

Important APIs/types/functions: `makeError` creates `ErrorModel`, attaches `ErrorModelJsonifier`, and returns `RestApiResponse<ErrorModel>`. Public helpers implement `BadRequest`, `BadRequest(JsonValidationException)`, `NotFound`, `MethodNotAllowed`, `Forbidden`, `NotImplemented`, and `InternalError`.

Control flow: each helper maps a semantic error to an HTTP response code and title. Validation bad request prefers first structured validation error, otherwise exception text.

State and persistence: factory is stateless; responses own models by shared pointer.

Dependencies and integration points: used by REST handlers and `HandleWithErrors`; depends on tape jsonifiers for error serialization.

Risks and test signals: error detail is serialized without JSON escaping by `ErrorModelJsonifier`. `BadRequest(JsonValidationException)` only reports one validation error. Tests should verify exact status codes and JSON body shape.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.hh

Purpose: declares the consolidated factory for REST success and error responses.

Important APIs/types/functions: `createResponse`, `Ok`, `OkEmpty`, `Created`, `BadRequest`, `NotFound`, `MethodNotAllowed`, `Forbidden`, `NotImplemented`, `InternalError`, and private `makeError`.

Control flow: handlers/actions call factory methods after business/model work; error helpers are also used by centralized exception mapping.

State and persistence: stateless factory.

Dependencies and integration points: depends on `RestApiResponse`, `JsonValidationException`, and `ErrorModel`.

Risks and test signals: confirm `OkEmpty` returns status OK and no body, `Created` preserves custom headers, and response code enum-to-status integer conversion in error model is correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/router/Router.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/router/Router.hh

Purpose: provides a small exact-pattern router for REST API handlers.

Important APIs/types/functions: `Route` stores pattern, method, and handler callback. `Router::add` appends routes. `Router::dispatch` parses request URL/method, finds matching pattern via `URLParser::matches`, checks method, and invokes callback.

Control flow: dispatch scans in registration order. If any pattern matches but method differs, throws `MethodNotAllowedException`; if no pattern matches, throws `ActionNotFoundException`.

State and persistence: stores route vector for the handler lifetime.

Dependencies and integration points: used by `TapeRestHandler` and `WellKnownHandler`; depends on common HTTP request/response, `URLParser`, and REST exceptions.

Risks and test signals: route params are not extracted by dispatch; action code likely reparses if needed. Method-not-allowed behavior depends on pattern match before method. Tests should include duplicate routes, overlapping patterns, parameter placeholders, and unknown methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/router/Router.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.cc

Purpose: implements a fluent URL builder used for tape REST `.well-known` endpoint URLs.

Important APIs/types/functions: `getInstance`, `setHttpsProtocol`, `setHostname`, `setPort`, `add`, `build`, and `addSlashIfNecessary`.

Control flow: builder enforces call order through staged interfaces: protocol, hostname, port, then additional path pieces. `add` appends a slash only when the current URL does not end with `/` and next item does not start with `/`.

State and persistence: stores a mutable `mURL` string in the builder instance.

Dependencies and integration points: used by `TapeRestHandler::getAccessURLBuilder` and `.well-known` endpoint generation.

Risks and test signals: `addSlashIfNecessary` calls `mURL.back()` and assumes URL is non-empty; staged use satisfies this, but direct misuse after construction would be unsafe. Tests should cover leading/trailing slash combinations and port zero/unset config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.hh

Purpose: declares the staged fluent URL builder interfaces.

Important APIs/types/functions: interfaces `URLBuilderProtocol`, `URLBuilderHostname`, `URLBuilderPort`; concrete `URLBuilder` implements them and exposes `build`, `add`, and static `getInstance`.

Control flow: private constructor plus staged return types guide callers through protocol -> hostname -> port -> path additions.

State and persistence: mutable URL string inside builder.

Dependencies and integration points: consumed by tape handler discovery URL generation.

Risks and test signals: inheritance is private for `URLBuilderHostname` and `URLBuilderPort`, relying on member function return types; compile tests should cover intended chained calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLBuilder.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.cc

Purpose: implements token-based URL prefix, pattern matching, parameter extraction, and duplicate-slash removal.

Important APIs/types/functions: constructor tokenizes on `/`; `startsBy`; `matches`; `matchesAndExtractParameters`; `removeDuplicateSlashes`. Parameter placeholders match regex `^\{[a-z]*\}$`.

Control flow: `startsBy` compares token prefixes. `matchesAndExtractParameters` requires equal token counts and treats placeholder tokens as captures. Captured map keys include the braces, e.g. `{requestid}`.

State and persistence: stores token vector for one parsed URL.

Dependencies and integration points: used by `RestHandler`, `RestApiManager`, `Router`, actions, and `FilesContainer`.

Risks and test signals: token counts are stored in `uint8_t`, so very long URLs can truncate sizes. Placeholder regex accepts empty `{}` and only lowercase letters. Tests should cover trailing slashes, duplicate slashes, encoded slashes, and parameter key expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.hh

Purpose: declares URL parsing utilities for REST route recognition and path normalization.

Important APIs/types/functions: constructor, `startsBy`, `matches`, `matchesAndExtractParameters`, static `removeDuplicateSlashes`, and private token vector.

Control flow: callers instantiate parser per URL and compare it against access URLs or route patterns.

State and persistence: stores parsed URL tokens only.

Dependencies and integration points: central utility for REST manager/router and tape model path storage.

Risks and test signals: ensure callers understand `matchesAndExtractParameters` key names include placeholder braces and that matching is token-based, not URL-decoding-aware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/utils/URLParser.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.cc

Purpose: implements a simple value object describing one tape REST API endpoint/version pair for discovery responses.

Important APIs/types/functions: constructor stores URI and version; `getUri` and `getVersion` return copies.

Control flow: `TapeWellKnownInfos::addEndpoint` creates these objects; jsonifier reads them for `.well-known` output.

State and persistence: in-memory URI/version strings only.

Dependencies and integration points: used exclusively by `TapeWellKnownInfos` and well-known JSON serialization.

Risks and test signals: no validation or escaping is done here; tests should validate endpoint override values before JSON output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.hh

Purpose: declares the endpoint/version value object for tape REST API discovery.

Important APIs/types/functions: `TapeRestApiEndpoint(uri, version)`, `getUri`, `getVersion`, private `mUri` and `mVersion`.

Control flow: endpoints are accumulated in `TapeWellKnownInfos` and serialized in discovery responses.

State and persistence: in-memory value object.

Dependencies and integration points: used by `TapeWellKnownInfos`.

Risks and test signals: getters return copies, which is simple but unnecessary for hot paths; no behavioral risk beyond validation at construction sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.cc -->
## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.cc

Purpose: implements the container of tape REST API discovery metadata.

Important APIs/types/functions: constructor stores site name; `addEndpoint` appends a `TapeRestApiEndpoint`; `getEndpoints` returns const vector reference; `getSiteName` returns copy.

Control flow: `TapeRestHandler` constructs this object and adds default/override endpoints during initialization. `WellKnownHandler` serializes it.

State and persistence: in-memory site name and vector of endpoint objects.

Dependencies and integration points: used by tape handler and well-known response model/jsonifier.

Risks and test signals: endpoint order follows insertion order. Tests should verify default endpoint is added only when no override exists for the default version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.hh -->
## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.hh

Purpose: declares the discovery metadata container for the tape REST API.

Important APIs/types/functions: `Endpoints` alias, constructor, `addEndpoint`, `getEndpoints`, `getSiteName`, `mSiteName`, and `mEndpoints`.

Control flow: filled during handler construction, then read by `.well-known` model/jsonifier.

State and persistence: in-memory metadata only.

Dependencies and integration points: owns `TapeRestApiEndpoint` objects.

Risks and test signals: raw pointer consumers of this object must respect handler lifetime. Site name is stored but current jsonifier serializes only versions/URLs, so tests should confirm whether site metadata is expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/LockResponse.cc -->
## sources/distributed-fs/eos/mgm/http/webdav/LockResponse.cc

Purpose: builds a dummy WebDAV LOCK response with lock discovery information.

Important APIs/types/functions: `LockResponse::BuildResponse` parses namespaces, validates root XML, clones request lock properties into `<activelock>`, then appends fixed timeout, depth, locktoken, response headers, and XML body.

Control flow: request XML is parsed by base `WebDAVResponse`; build creates declaration, `<prop xmlns="DAV:">`, `<lockdiscovery>`, `<activelock>`, clones all child properties from the lockinfo root, and returns `this`.

State and persistence: no real lock is persisted. It returns a constant opaque lock token `00000000-0000-0000-0000-000000000000` and fixed `Second-604800` timeout/depth infinity.

Dependencies and integration points: instantiated by `WebDAVHandler` on `LOCK`; uses RapidXML helpers from `WebDAVResponse`.

Risks and test signals: because locking is not enforced, clients may believe a lock exists while EOS does not maintain lock state. Tests should cover malformed XML, empty root, cloned owner/scope/type fields, headers, and unlock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/LockResponse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/LockResponse.hh -->
## sources/distributed-fs/eos/mgm/http/webdav/LockResponse.hh

Purpose: declares the WebDAV LOCK response builder.

Important APIs/types/functions: constructor takes request and `VirtualIdentity*`, stores identity, and calls base `WebDAVResponse`; `BuildResponse` overrides response construction.

Control flow: used by `WebDAVHandler` for LOCK methods.

State and persistence: stores client identity pointer but implementation does not use it for real lock state.

Dependencies and integration points: inherits `WebDAVResponse`; includes RapidXML, mapping, namespace, and identity dependencies.

Risks and test signals: identity pointer lifetime should match request handling. Since lock responses are dummy, compatibility tests with WebDAV clients are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/LockResponse.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.cc -->
## sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.cc

Purpose: implements WebDAV PROPFIND XML responses for file/directory properties, directory listings, quotas, etags, and OwnCloud extension fields.

Important APIs/types/functions: global URI encode/decode helpers; `PropFindResponse::EncodeURI`; `BuildResponse`; `ParseRequestPropertyTypes`; `BuildResponseNode`. Properties include content length/type, modified/creation dates, resource type, display name, etag, quotas, OwnCloud id/size/permissions, checked-in/out, and allprop marker.

Control flow: `BuildResponse` parses namespaces and requested property types, optionally enforces OwnCloud sync-allow attribute for `oc:id`, builds a multistatus document, stats the request path after namespace mapping, and branches by `Depth`: `0` or file returns one node; `1` opens the directory and appends child nodes excluding version/atomic/hidden entries; `1,noroot`, `infinity`, and empty depth return not implemented. `BuildResponseNode` stats each path, hides hardlinks, URI-encodes hrefs, creates found and not-found propstat blocks, fills requested properties, and maps stat/access failures to response code.

State and persistence: reads EOS namespace state through `gOFS->_stat`, `XrdMgmOfsDirectory`, `Quota::GetIndividualQuota`, and `gOFS->acc_access`. Does not mutate filesystem state.

Dependencies and integration points: instantiated by `WebDAVHandler`; uses `NamespaceMap`, `XrdMgmOfsDirectory`, `Quota`, `Timing`, `Path`, `OwnCloud`, and RapidXML.

Risks and test signals: URI encode buffers are stack-sized to `3 * strlen`; OK for byte expansion but global encode tables use static initialization without synchronization. XML values rely on RapidXML value setting; confirm escaping behavior during print. Tests should cover depth variants, missing/inaccessible paths, hardlink hiding, quota properties, OwnCloud sync-block attribute, hidden prefixes, symlink stat failures, and path namespace mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.hh -->
## sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.hh

Purpose: declares PROPFIND response parsing and property generation support.

Important APIs/types/functions: `EOS_WEBDAV_HIDE_IN_PROPFIND_PREFIX`; extern encode tables and `dav_uri_decode`; `PropertyTypes` bitmask enum; constructor initializes encode tables; `BuildResponse`, `ParseRequestPropertyTypes`, `BuildResponseNode`, `MapRequestPropertyType`, and `EncodeURI`.

Control flow: `MapRequestPropertyType` converts DAV/OwnCloud property names to bit flags consumed by `BuildResponseNode`.

State and persistence: stores requested property bitmask and client identity pointer. Static encode table initialization is shared process state.

Dependencies and integration points: inherits `WebDAVResponse`; used by `WebDAVHandler`.

Risks and test signals: constructor's `initialized` flag is never set to true after initializing tables, so tables are rebuilt every construction; harmless but not intended. `ALLPROP_MARKER = 0xf000` overlaps extension bits and can make bit tests subtle; tests should cover allprop response differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropFindResponse.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.cc -->
## sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.cc

Purpose: builds a dummy WebDAV PROPPATCH multistatus response acknowledging requested property set/remove operations.

Important APIs/types/functions: `PropPatchResponse::BuildResponse` parses namespaces, validates root `<propertyupdate>`, builds `<d:multistatus>`, copies custom namespace declarations, then emits `HTTP/1.1 200 OK` propstat entries for each property under DAV `set/prop` and `remove/prop`.

Control flow: no property persistence is performed. It echoes property names in response nodes and always marks them successful when present.

State and persistence: does not mutate EOS attributes or any property store.

Dependencies and integration points: instantiated by `WebDAVHandler` for PROPPATCH; uses `WebDAVResponse` namespace and XML helpers.

Risks and test signals: clients may believe properties were saved although response is fake. The `<d:href>` node is created but no value is set. Tests should cover set/remove XML, custom namespaces, malformed XML, and client compatibility expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.hh -->
## sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.hh

Purpose: declares the WebDAV PROPPATCH response builder.

Important APIs/types/functions: constructor stores `VirtualIdentity*`; `BuildResponse` creates the XML response.

Control flow: used by `WebDAVHandler` for PROPPATCH requests.

State and persistence: identity pointer is stored, but implementation does not persist properties.

Dependencies and integration points: inherits `WebDAVResponse`; includes RapidXML and mapping dependencies.

Risks and test signals: if future implementation persists properties, tests must add permission checks and atomicity semantics required by WebDAV PROPPATCH.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.cc -->
## sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.cc

Purpose: dispatches WebDAV extension methods and implements MKCOL, MOVE, and COPY mutations against EOS MGM.

Important APIs/types/functions: `Matches` recognizes PROPFIND, PROPPATCH, MKCOL, COPY, MOVE, LOCK, UNLOCK. `HandleRequest` optionally routes to another MGM, records stats, creates response builders, and calls `BuildResponse`. `MkCol` calls `gOFS->mkdir`. `Move` parses/decodes Destination, applies OwnCloud remapping, calls `gOFS->rename`, and handles overwrite by deleting destination through `/proc/user`. `Copy` calls `/proc/user` `mgm.cmd=file&mgm.subcmd=copy`, with optional forced overwrite.

Control flow: all WebDAV requests add EOS app metadata, check federation/routing with `gOFS->ShouldRoute`, then switch by parsed method. Error mapping distinguishes `SFS_ERROR`, `SFS_REDIRECT`, `SFS_STALL`, and errno values such as `EEXIST`, `ENOENT`, `EPERM`, `ENOSPC`. Successful MKCOL returns 201 with `OC-FileId`; successful MOVE/COPY generally return 201 or 204 for overwrite.

State and persistence: MKCOL creates directories; MOVE renames/removes existing destinations; COPY creates files through proc command. PROPFIND/PROPPATCH/LOCK/UNLOCK behavior is delegated to response objects, some of which are dummy.

Dependencies and integration points: integrates `HttpServer`, `PropFindResponse`, `PropPatchResponse`, `LockResponse`, `gOFS`, MGM stats, `OwnCloud`, `ProcCommand`, `XrdSecEntity`, and common HTTP responses.

Risks and test signals: several error branches call `HttpServer::HttpError(..., response->BAD_REQUEST)` while `response` is null; enum access through null pointer compiles but is unsafe style and should be reviewed. Destination header handling uses 1024-byte decode buffers and skips decoding longer destinations. Copy command concatenates URL parameters without obvious escaping. Tests should cover routing redirects, missing body/path/destination, overwrite true/false, remote.php remapping, long/encoded destinations, permission errors, stalls, redirects, and proc-command injection-sensitive characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.hh -->
## sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.hh

Purpose: declares the WebDAV protocol handler for EOS HTTP.

Important APIs/types/functions: private method enum, constructor taking `VirtualIdentity*`, static `Matches`, `HandleRequest`, `MkCol`, `Move`, `Copy`, and inline `ParseMethodString`.

Control flow: HTTP server can test `Matches` and then delegate WebDAV requests to `HandleRequest`.

State and persistence: inherits identity and response storage from `ProtocolHandler`; mutation methods persist through MGM operations in `.cc`.

Dependencies and integration points: depends on common `ProtocolHandler`, mapping, namespace macros, and HTTP request/response types.

Risks and test signals: method parsing is exact and case-sensitive. Tests should cover unsupported WebDAV methods and interaction with other protocol handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.cc -->
## sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.cc

Purpose: implements shared XML request parsing and RapidXML response-building helpers for WebDAV response classes.

Important APIs/types/functions: constructor copies/parses request body or supplies default allprop PROPFIND XML for empty body; `ParseNamespaces`; `GetNode`; `AllocateNode`; `AllocateAttribute`; `CloneNode`; `AllocateString`; `SetValue`.

Control flow: constructor parses XML into `mXMLRequestDocument` and logs parse errors without throwing. Namespace parsing records DAV and custom namespaces from root-level attributes. `GetNode` searches direct children matching known DAV/custom namespace prefixes.

State and persistence: owns request XML copy, parsed request document, response document, and namespace maps for one response object.

Dependencies and integration points: base for `PropFindResponse`, `PropPatchResponse`, and `LockResponse`; depends on RapidXML and common logging.

Risks and test signals: parse errors leave an empty/partial document and derived builders must detect missing root. Namespace parsing only scans top-level sibling nodes, not nested declarations. Tests should cover invalid XML, empty body, namespace prefixes, custom namespaces, and memory-pool lifetime after printing/clearing response document.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.hh -->
## sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.hh

Purpose: declares the abstract base class for WebDAV XML responses.

Important APIs/types/functions: inherits `eos::common::HttpResponse`; defines `NamespaceMap`, XML document members, namespace maps, constructor, pure virtual `BuildResponse`, and XML helper methods.

Control flow: derived response builders use base helpers to parse request XML and assemble response XML.

State and persistence: per-response XML documents and namespace maps only.

Dependencies and integration points: used by all WebDAV response types and returned through the common HTTP response interface.

Risks and test signals: because the class itself is an `HttpResponse`, derived `BuildResponse` often returns `this`; ownership expectations should be verified to prevent leaks or double deletes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/http/webdav/WebDAVResponse.hh -->
