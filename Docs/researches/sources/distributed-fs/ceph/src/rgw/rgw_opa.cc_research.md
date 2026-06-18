# sources/distributed-fs/ceph/src/rgw/rgw_opa.cc

## Purpose
`rgw_opa.cc` implements optional Open Policy Agent authorization for RGW requests. When enabled in `rgw_process.cc`, it serializes request context into JSON, POSTs it to the configured OPA endpoint, and allows the operation only when OPA returns a JSON `result: true`.

## Important APIs, Types, And Functions
`rgw_opa_authorize(RGWOp*& op, req_state* s)` is the single exported function. It reads `rgw_opa_url`, `rgw_opa_token`, and `rgw_opa_verify_ssl` from config, uses `RGWHTTPTransceiver`, and serializes request method, URIs, query params, AWS4 URI, object name, subuser, user info, and bucket info using `JSONFormatter`.

## Control Flow
The function validates that an OPA URL exists, builds a POST with `X-Auth-Token`, JSON content type, and `Expect: 100-continue`, sends the body with `req.process(op, s->yield)`, parses the returned bufferlist as JSON, decodes boolean `result`, and returns `0` for allow or `-EPERM` for deny. Transport errors and malformed JSON propagate as negative errors.

## State And Persistence
No local persistent state is modified. It sends potentially sensitive request and identity metadata to an external policy service. Authorization outcome is transient and bound to the current request.

## Dependencies And Integration Points
The function depends on `rgw_http_client.h`, `req_state`, `RGWOp` logging, Ceph config, JSON formatting/parsing, and the RGW coroutine yield path. It is called after op mask verification and before native `verify_permission()` in `rgw_process_authenticated()`.

## Risks And Test Signals
Risks include missing `rgw_opa_url`, OPA outage becoming request failure, schema drift between RGW and OPA policy, unchecked absence/type mismatch of `result`, sensitive data exposure, and SSL verification misconfiguration. Test signals should cover allow/deny responses, malformed JSON, missing URL, HTTP errors, SSL verify toggles, token header presence, and requests with/without user, bucket, object, and auth identity.
