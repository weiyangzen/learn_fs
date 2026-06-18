## sources/distributed-fs/ipfs-kubo/test/sharness/t0400-api-no-gateway.sh

Purpose: verifies the RPC API listener does not behave as a general IPFS gateway by default, preventing browser scripting vulnerabilities, while `--unrestricted-api` explicitly enables gateway behavior.

Important commands and control flow: imports a CAR fixture with `ipfs dag import`, sets a known fixture hash, launches a default daemon and expects `http://127.0.0.1:$API_PORT/ipfs/$HASH` to return 404. It restarts with `--unrestricted-api` and expects the same URL to return 200.

State and persistence: content is imported into the test repo; daemon flag determines API route exposure.

Dependencies and integration points: depends on CAR import, API listener, gateway route gating, `test_curl_resp_http_code`, and daemon lifecycle helpers.

Risks and test signals: catches accidental exposure of gateway routes on the API port and regressions in the explicit unrestricted mode.
