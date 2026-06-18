# sources/distributed-fs/eos/unit_tests/mgm/HttpTests.cc

## Purpose
Tests HTTP client distinguished-name normalization in the MGM HTTP server. It verifies that old slash-separated and newer comma-separated certificate DN formats converge to the canonical slash-separated form.

## Important APIs, types, and functions
The test includes `mgm/http/HttpServer.hh` under `IN_TEST_HARNESS` and calls `eos::mgm::HttpServer::ProcessClientDN()`.

## Control flow
It constructs an `HttpServer`, passes an already canonical DN, then passes a reversed comma-separated DN, and asserts both produce the same canonical string.

## State and persistence
No persistent state is involved. DN normalization affects request identity presentation and authorization/accounting inputs.

## Dependencies and integration points
Depends on Google Test and MGM HTTP server internals. It integrates with TLS/X.509 client identity handling.

## Risks and test signals
The test protects one common DN shape but not escaping, commas inside attribute values, whitespace, lowercase attribute names, multi-valued RDNs, or malformed DNs. Because identity strings feed authorization, parser hardening tests are important.
