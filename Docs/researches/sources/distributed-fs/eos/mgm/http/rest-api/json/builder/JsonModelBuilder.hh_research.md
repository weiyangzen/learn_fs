## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/JsonModelBuilder.hh

Purpose: defines the generic interface for building typed request models from JSON strings.

Important APIs/types/functions: template `JsonModelBuilder<Model>` with pure virtual `std::unique_ptr<Model> buildFromJson(const std::string&)` and virtual destructor.

Control flow: REST actions own or receive model builders and call `buildFromJson` before invoking business logic.

State and persistence: stateless abstract interface.

Dependencies and integration points: base for `JsonCppModelBuilder` and tape-specific builders in `TapeModelBuilders.hh`.

Risks and test signals: implementations are responsible for all validation and exception consistency. Tests should exercise builder polymorphism through action code.
