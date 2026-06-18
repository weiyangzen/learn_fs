## sources/distributed-fs/eos/mgm/http/rest-api/model/wellknown/tape/GetTapeWellKnownModel.hh

Purpose: wraps `TapeWellKnownInfos` for JSON serialization by the well-known endpoint.

Important APIs/types/functions: constructor stores a const pointer; `getTapeWellKnownInfos` returns it; inherits `Jsonifiable`.

Control flow: `WellKnownHandler` creates this model after validating tape API availability and assigns `GetTapeWellKnownModelJsonifier`.

State and persistence: borrowed pointer only; caller must ensure `TapeWellKnownInfos` outlives serialization.

Dependencies and integration points: depends on tape well-known info classes and common JSON framework.

Risks and test signals: because it stores a raw pointer to handler-owned state, tests should ensure response serialization occurs before handler destruction and not asynchronously afterward.
