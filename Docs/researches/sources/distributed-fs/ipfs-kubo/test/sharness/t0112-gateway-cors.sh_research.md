## sources/distributed-fs/ipfs-kubo/test/sharness/t0112-gateway-cors.sh

Purpose: tests gateway CORS defaults and custom `Gateway.HTTPHeaders` behavior for GET and OPTIONS requests.

Important APIs and helpers: uses `ipfs config Gateway.HTTPHeaders`, `curl -X GET/OPTIONS`, `test_should_contain`, daemon launch/kill helpers, and fixture content served through the gateway.

Control flow and state: confirms the default `Gateway.HTTPHeaders` config is empty while implicit CORS headers are supplied by the gateway stack, performs GET and OPTIONS against gateway resources and subdomain redirects, then configures custom headers. It verifies configured `Access-Control-Allow-Headers` extends the implicit list and configured `Access-Control-Allow-Origin` replaces the implicit origin list.

Dependencies and integration points: covers gateway header injection, preflight handling, subdomain redirect CORS behavior, and config reload after daemon restart.

Risks and test signals: catches accidental removal of implicit browser CORS support, duplicate or overwritten custom headers, and OPTIONS behavior changes. Passing is based on expected CORS headers in captured HTTP responses.
