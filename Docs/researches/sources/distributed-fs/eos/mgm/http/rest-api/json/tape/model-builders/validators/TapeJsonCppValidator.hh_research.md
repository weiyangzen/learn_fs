## sources/distributed-fs/eos/mgm/http/rest-api/json/tape/model-builders/validators/TapeJsonCppValidator.hh

Purpose: defines tape-specific JsonCPP validation for path-like request values.

Important APIs/types/functions: `PathValidator::validate` requires a non-empty string and rejects values convertible to JsonCPP `intValue`; `TapeJsonCppValidatorFactory::getPathValidator` returns it.

Control flow: intended for model builders to validate file path fields before adding them to models.

State and persistence: stateless validator.

Dependencies and integration points: extends `JsonCppValidatorFactory`, includes common path/string utilities, and can be used by tape request model builders.

Risks and test signals: current consolidated builders do not appear to call this validator directly, so path validation coverage may be weaker than intended. Tests should include empty strings, numeric JSON values, numeric-looking strings, and malformed path forms.
