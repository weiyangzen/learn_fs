# sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.hh

## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/JsonCPPTapeModelBuilderTest.hh

Purpose: declares the GoogleTest fixture for tape REST JSON model builder tests.

Important APIs and types: `JsonCPPTapeModelBuilderTest`, inherited `::testing::Test`, and static `std::string restApiEndpointID`.

Control flow: setup and teardown are empty. The static endpoint id is defined in the `.cc` file and reused by builder construction tests.

State and persistence: only fixture-local state plus the static endpoint-id string. No persistence or external services.

Dependencies and integration: includes `mgm/Namespace.hh` and gtest. It gives the `.cc` tests a shared place for endpoint identity constants.

Risks and test signals: minimal fixture. Any future shared setup should preserve isolation because JSON builder tests expect no cross-test state.
