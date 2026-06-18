## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/TapeJsonifiers.hh

Purpose: consolidates JSON serializers for tape REST API response models and errors.

Important APIs/types/functions: `ErrorModelJsonifier`, `CreatedStageBulkRequestJsonifier`, `GetStageBulkRequestJsonifier`, `GetArchiveInfoResponseJsonifier`, and `GetTapeWellKnownModelJsonifier`, all implementing `jsonify`.

Control flow: response models receive a jsonifier via `setJsonifier`; `RestApiResponse` calls `model->jsonify`. Serializers manually stream JSON object and array syntax.

State and persistence: serializers are stateless; they read model fields and stream output.

Dependencies and integration points: integrates error models, stage response models, archive info query responses, and well-known endpoint models with the common `Jsonifiable` response path.

Risks and test signals: string values are written directly without JSON escaping, including paths, errors, site URLs, CTA error text, and request IDs. Tests should include quotes, backslashes, control characters, and non-ASCII paths. Archive-info null response produces `{}`; verify clients tolerate that.
