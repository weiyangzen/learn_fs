# sources/distributed-fs/ipfs-kubo/core/corehttp/option_test.go

## Purpose
Tests the API version checking serve option behavior.

## Important APIs, Types, and Functions
Defines `testcasecheckversion`, its `body` helper, and `TestCheckVersionOption`.

## Control Flow and State
Each case builds a request with a `User-Agent`, wraps a child mux via `CheckVersionOption`, records whether the downstream handler ran, and compares response code/body. API version mismatches are rejected for normal API paths but bypassed for `/api/v0/version` and `/webui`.

## Dependencies and Integration Points
Depends on Kubo version constants and httptest. It validates a serve option implemented outside this subset but mounted in the same corehttp option chain.

## Risks and Test Signals
The test signals API compatibility enforcement regressions, especially false rejection of browser/WebUI/version requests. It does not cover all user-agent variants or interaction with CORS/auth middleware.
