# sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.cc

## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.cc

Purpose: tests JSON-to-C++ model building for tape stage REST requests.

Important APIs and types: `CreateStageRequestModelBuilder`, `JsonValidationException`, `FILES_KEY_NAME`, `File`, endpoint id `restApiEndpointID`, and request fields such as path, activity, and endpoint.

Control flow: invalid JSON, empty JSON, wrong field names, non-array `files`, malformed file entries, and wrong element formats throw `JsonValidationException`. Valid formats build a model with expected files. Activity-related tests distinguish default endpoint behavior from explicitly supplied endpoint values.

State and persistence: builder state is local to each test. Parsed request objects are in memory only.

Dependencies and integration: includes tape REST model builders and JSON validation exception classes. It validates the REST API boundary before requests enter MGM/tape prepare logic.

Risks and test signals: strict validation protects downstream prepare code from malformed input. Tests focus on schema shape and selected fields, so deeper semantic validation may be elsewhere.
