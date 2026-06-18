## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/jsoncpp/JsonCppValidator.hh

Purpose: defines reusable JsonCPP validators and a factory for basic JSON field validation.

Important APIs/types/functions: `ValidatorException`; abstract `JsonCppValidator::validate`; concrete `NonEmptyArrayValidator`, `StringValidator`, `ObjectValidator`; `JsonCppValidatorFactory` factory methods.

Control flow: validators throw `ValidatorException` on invalid shape. Factories allocate validators as `unique_ptr`.

State and persistence: validators are stateless.

Dependencies and integration points: intended for model builders and extended by tape-specific validator factory.

Risks and test signals: `getNotNullValidator` returns `StringValidator`, so it validates string-ness rather than general non-null. Tests should verify factory semantics before relying on it for object or scalar fields.
