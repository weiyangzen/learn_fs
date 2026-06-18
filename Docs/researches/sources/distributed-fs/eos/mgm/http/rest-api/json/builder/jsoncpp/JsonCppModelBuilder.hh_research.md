## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppModelBuilder.hh

Purpose: adds JsonCPP parsing support to the generic model-builder interface.

Important APIs/types/functions: template `JsonCppModelBuilder<Model>` inherits `JsonModelBuilder<Model>`, leaves `buildFromJson` abstract, and provides protected `parseJson(json, Json::Value&)`.

Control flow: `parseJson` uses `Json::Reader::parse` and throws `JsonValidationException` with the original JSON string if parsing fails.

State and persistence: stateless helper.

Dependencies and integration points: includes JsonCPP, REST exceptions, and validation errors. Tape request builders inherit it.

Risks and test signals: parse errors include full request JSON in exception detail, which can leak sensitive metadata into logs/responses. Tests should cover malformed JSON and ensure callers map exceptions to 400 rather than 500.
