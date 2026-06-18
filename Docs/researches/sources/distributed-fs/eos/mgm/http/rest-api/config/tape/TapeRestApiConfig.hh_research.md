## sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.hh

Purpose: defines `TapeRestApiConfig`, the shared configuration object used by REST manager and tape handlers.

Important APIs/types/functions: exposes setters/getters for site name, activation, tape-enabled, host alias, endpoint mapping, XrdHttp port, access URL, and stage-enabled. Internals include `mSiteName`, `mAccessURL`, `mHostAlias`, `mTapeRestApiEndpointUrlMap`, `mIsActivated`, `mTapeEnabled`, `mXrdHttpPort`, `mConfigMutex`, and `mStageEnabled`.

Control flow: the class is a mutable configuration holder; request handling calls are expected to read it frequently, while MGM config reload paths may update it.

State and persistence: state is resident in memory and shared by pointer from `RestApiManager`. String/map state is mutex-protected; activation booleans and port use atomics.

Dependencies and integration points: depends on `mgm/Namespace.hh`, `common/RWMutex.hh`, `<atomic>`, and STL string/map. It controls `TapeRestHandler::isRestRequest` gating and `.well-known` URL generation.

Risks and test signals: validate default disabled behavior, explicit activation, tape-enabled gating, missing host alias/site name messages, stage-enabled behavior in action code, and endpoint override handling. The port field should be initialized before use in URL builders.
