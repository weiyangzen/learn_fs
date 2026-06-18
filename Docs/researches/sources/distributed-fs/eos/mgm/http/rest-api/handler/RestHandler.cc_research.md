## sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.cc

Purpose: implements the base REST handler entrypoint validation and request-prefix matching.

Important APIs/types/functions: constructor calls `verifyRestApiEntryPoint`; `isRestRequest` uses `URLParser::startsBy`; `getEntryPointURL` returns the configured base path. The allowed entrypoint regex is `^\/(\.?[a-z0-9-]+)+\/$`.

Control flow: every concrete REST handler is constructed with an entrypoint, validated immediately, then asked by the manager whether a URL should be handled.

State and persistence: stores only `mEntryPointURL`.

Dependencies and integration points: uses `URLParser`, `common::RegexWrapper`, logging, and REST exceptions. Base class for `TapeRestHandler` and `WellKnownHandler`.

Risks and test signals: test valid and invalid entrypoints, prefix matching with duplicate slashes or boundary-like paths, and error messages for malformed config. The regex admits `.well-known` style paths and lower-case alphanumeric/hyphen tokens only.
