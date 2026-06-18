# sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.hh

## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.hh

Purpose: declares shared fixture state for tape REST API tests.

Important APIs and types: `RestApiTest`, `TapeRestApiConfig`, `RestHandler`, static API URL/path/version/resource constants, and helper members used by the `.cc` test implementation.

Control flow: the fixture provides empty setup/teardown and shared constants so route tests are consistent.

State and persistence: static constants only. No persistent or network state.

Dependencies and integration: includes MGM namespace support, REST handler abstractions, and tape REST config. It binds the tests to the REST API version/resource naming contract.

Risks and test signals: changes to API version strings, resource names, or base paths must update both config and tests. The fixture centralizes those values to reduce drift.
