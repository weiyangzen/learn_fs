# sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.cc

## sources/distributed-fs/eos/unit_tests/mgm/http/rest-api/tape/RestApiTest.cc

Purpose: tests tape REST handler routing and URL parsing/building utilities.

Important APIs and types: `RestHandler`, `TapeRestHandler`, `TapeRestApiConfig`, `RestException`, `URLParser`, `common::HttpResponse`, and fixture `RestApiTest`.

Control flow: constructor tests reject programmer-supplied wrong base URLs. Handler tests call `handleRequest` with missing resource, missing version, unknown resource, and valid resource/version combinations, checking HTTP response status or exceptions. URL parser tests verify prefix matching, parameter extraction from route templates, and URL construction.

State and persistence: handler/config objects are in memory. No network server or persistent state is started.

Dependencies and integration: this is the routing layer between MGM HTTP requests and tape REST handlers. It validates that route structure and version/resource matching behave before business handlers execute.

Risks and test signals: URL shape is an API contract. Exact routing and status behavior can break clients if changed. These are unit-level tests and do not exercise full HTTP transport.
